from flask import Flask, request, render_template, jsonify, send_from_directory
import os, json, time, uuid
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)
OUT = os.environ.get("VERIFIER_OUT", "./out/receipts")
os.makedirs(OUT, exist_ok=True)

def load_pubkey():
    if os.environ.get("PUBKEY_CONTENT"):
        key_pem = os.environ["PUBKEY_CONTENT"].encode()
        return serialization.load_pem_public_key(key_pem, backend=default_backend())
    p = os.path.expanduser("~/.securewipe/public.pem")
    if os.path.exists(p):
        return serialization.load_pem_public_key(open(p,'rb').read(), backend=default_backend())
    return None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", result=None)

@app.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.get_json()
    if not data or "signature" not in data:
        return jsonify({"valid": False, "reason": "no signature"}), 400
    sig = bytes.fromhex(data["signature"]["hex"])
    payload = dict(data); del payload["signature"]
    payload_bytes = json.dumps(payload, separators=(",",":"), sort_keys=True).encode()
    pub = load_pubkey()
    if not pub:
        return jsonify({"valid": False, "reason": "no public key configured"}), 500
    try:
        pub.verify(sig, payload_bytes, padding.PKCS1v15(), hashes.SHA256())
        return jsonify({"valid": True})
    except Exception as e:
        return jsonify({"valid": False, "reason": str(e)}), 400

@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.get_json()
    ok = False
    try:
        sig = bytes.fromhex(data["signature"]["hex"])
        payload = dict(data); del payload["signature"]
        payload_bytes = json.dumps(payload, separators=(",",":"), sort_keys=True).encode()
        pub = load_pubkey()
        if not pub:
            return jsonify({"ok": False, "reason": "no public key configured"}), 500
        pub.verify(sig, payload_bytes, padding.PKCS1v15(), hashes.SHA256())
        ok = True
    except Exception as e:
        return jsonify({"ok": False, "reason": "verification failed: "+str(e)}), 400
    if ok:
        rid = str(uuid.uuid4())
        outp = os.path.join(OUT, rid + ".json")
        with open(outp, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify({"ok": True, "receipt_id": rid})
    return jsonify({"ok": False}), 400

@app.route("/ui/upload", methods=["GET","POST"])
def upload_ui():
    result = None
    if request.method=="POST":
        f = request.files.get("certificate")
        if not f:
            result = "No file uploaded"
        else:
            try:
                data = json.load(f)
                resp = app.test_client().post("/api/verify", json=data)
                if resp.status_code==200 and resp.json.get("valid"):
                    result = "Signature valid"
                else:
                    result = "Invalid: "+str(resp.json)
            except Exception as e:
                result = "Error: "+str(e)
    return render_template("index.html", result=result)

@app.route("/receipts/<path:fn>", methods=["GET"])
def receipts(fn):
    return send_from_directory(OUT, fn, as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
