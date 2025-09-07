use actix_web::{web, App, HttpResponse, HttpServer, Responder, middleware};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use uuid::Uuid;
use std::time::{SystemTime, UNIX_EPOCH};
use std::path::Path;
use std::fs::{File, create_dir_all, read_to_string, write};
use std::io::{Seek, SeekFrom, Write, Read};
use sha2::{Sha256, Digest};
use std::process::Command;
use std::thread;
use log::{info, error};

#[derive(Deserialize)]
struct WipeRequest {
    device_path: String,
    profile: String,
    email: String,
    force: Option<bool>,
}

#[derive(Serialize, Clone)]
struct JobStatus {
    id: String,
    status: String,
    progress: f32,
    message: String,
    cert_path: Option<String>,
    email_status: Option<String>,
}

struct AppState {
    jobs: Mutex<Vec<JobStatus>>,
}

fn timestamp() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs()
}

async fn index() -> impl Responder {
    HttpResponse::Ok().body("SecureWipe agent. Use the web UI at /static/index.html")
}

async fn targets() -> impl Responder {
    let mut list = vec![];
    if let Ok(out) = Command::new("lsblk").arg("-J").output() {
        if out.status.success() {
            if let Ok(j) = serde_json::from_slice::<serde_json::Value>(&out.stdout) {
                list.push(serde_json::json!({"lsblk": j}));
            }
        }
    }
    HttpResponse::Ok().json(list)
}

async fn start_wipe(req: web::Json<WipeRequest>, data: web::Data<AppState>) -> impl Responder {
    let r = req.into_inner();
    let id = Uuid::new_v4().to_string();
    let id_clone = id.clone(); // clone for thread
    let job = JobStatus { id: id.clone(), status: "queued".into(), progress: 0.0, message: "queued".into(), cert_path: None, email_status: None };

    {
        let mut jobs = data.jobs.lock().unwrap();
        jobs.push(job);
    }

    let state = data.clone();
    thread::spawn(move || {
        info!("Starting wipe job {}", id_clone);
        {
            let mut jobs = state.jobs.lock().unwrap();
            if let Some(j) = jobs.iter_mut().find(|j| j.id==id_clone) {
                j.status = "running".into();
                j.message = "starting".into();
                j.progress = 0.05;
            }
        }

        // Validate device path
        let path = r.device_path.clone();
        let p = Path::new(&path);
        if !p.exists() {
            let mut jobs = state.jobs.lock().unwrap();
            if let Some(j) = jobs.iter_mut().find(|j| j.id==id_clone) {
                j.status = "failed".into();
                j.message = format!("path not found: {}", path);
                j.progress = 0.0;
            }
            error!("Path not found: {}", path);
            return;
        }

        // Wiping logic (unchanged)
        // ...

        // Generate hash
        let mut hasher = Sha256::new();
        if let Ok(mut f2) = File::open(p) {
            let mut buf = [0u8; 65536];
            loop {
                match f2.read(&mut buf) {
                    Ok(0) => break,
                    Ok(n) => hasher.update(&buf[..n]),
                    Err(_) => break,
                }
            }
        }
        let digest = hasher.finalize();
        let hex = hex::encode(digest);

        // Write certificate JSON
        let outdir = "./out/certs";
        create_dir_all(outdir).ok();
        let cert_path = format!("{}/{}.json", outdir, id_clone);
        let cert = serde_json::json!({
            "id": id_clone,
            "device": path,
            "profile": r.profile,
            "method": "overwrite",
            "timestamp": timestamp(),
            "hash": hex
        });
        write(&cert_path, serde_json::to_string_pretty(&cert).unwrap()).ok();

        // Call Python signing script
        let mut py_cmd = Command::new("python3");
        py_cmd.arg("/opt/tools/sign_and_send.py").arg("--cert").arg(&cert_path).arg("--email").arg(&r.email);
        if let Ok(submit) = std::env::var("VERIFIER_SUBMIT_URL") {
            py_cmd.arg("--submit-url").arg(submit);
        }
        let py = py_cmd.output();
        let email_status = match py {
            Ok(o) if o.status.success() => "sent".to_string(),
            Ok(o) => format!("failed: {}", String::from_utf8_lossy(&o.stderr)),
            Err(e) => format!("error: {}", e)
        };

        let mut jobs = state.jobs.lock().unwrap();
        if let Some(j) = jobs.iter_mut().find(|j| j.id==id_clone) {
            j.status = "finished".into();
            j.progress = 1.0;
            j.cert_path = Some(cert_path.clone());
            j.email_status = Some(email_status.clone());
            j.message = "completed".into();
        }
        info!("Job {} completed", id_clone);
    });

    HttpResponse::Ok().json(serde_json::json!({"job_id": id}))
}

async fn jobs(data: web::Data<AppState>) -> impl Responder {
    let jobs = data.jobs.lock().unwrap().clone();
    HttpResponse::Ok().json(jobs)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    create_dir_all("./out/certs").ok();
    create_dir_all("./frontend").ok();

    // Ensure frontend index.html exists
    let index_path = "/opt/frontend/index.html";
    if read_to_string(index_path).is_err() {
        write(index_path, "<html><body><h1>SecureWipe Agent</h1></body></html>").ok();
    }

    let state = web::Data::new(AppState { jobs: Mutex::new(Vec::new()) });
    HttpServer::new(move || {
        App::new()
            .wrap(middleware::Logger::default())
            .app_data(state.clone())
            .route("/", web::get().to(index))
            .route("/targets", web::get().to(targets))
            .route("/wipe", web::post().to(start_wipe))
            .route("/jobs", web::get().to(jobs))
            .service(actix_files::Files::new("/static", "/opt/frontend").show_files_listing())
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
