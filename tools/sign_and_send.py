#!/usr/bin/env python3
"""sign_and_send.py
Signs certificate JSON using RSA private key, creates PDF, optionally emails and submits to verifier.
ENV: PRIVATE_KEY_CONTENT, SMTP_* variables
"""
import argparse, json, os, sys, time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from reportlab.pdfgen import canvas

def load_private_key(args):
    key_pem = None
    if os.environ.get("PRIVATE_KEY_CONTENT"):
        key_pem = os.environ["PRIVATE_KEY_CONTENT"].encode()
    elif args.private_key and os.path.exists(args.private_key):
        key_pem = open(args.private_key,'rb').read()
    else:
        p = os.path.expanduser("~/.securewipe/private.pem")
        if os.path.exists(p):
            key_pem = open(p,'rb').read()
    if not key_pem:
        print("No private key found (set PRIVATE_KEY_CONTENT or --private-key)", file=sys.stderr)
        sys.exit(2)
    return serialization.load_pem_private_key(key_pem, password=None, backend=default_backend())

def sign_payload(private_key, payload_bytes):
    sig = private_key.sign(payload_bytes, padding.PKCS1v15(), hashes.SHA256())
    return sig

def make_pdf(cert_signed, out_pdf):
    c = canvas.Canvas(out_pdf)
    c.setFont("Helvetica", 12)
    c.drawString(40,800,"SecureWipe Certificate")
    c.setFont("Helvetica",10)
    c.drawString(40,780,"ID: " + cert_signed.get("id",""))
    c.drawString(40,760,"Device: " + cert_signed.get("device",""))
    c.drawString(40,740,"Profile: " + cert_signed.get("profile",""))
    c.drawString(40,720,"Method: " + cert_signed.get("method",""))
    c.drawString(40,700,"Timestamp: " + str(cert_signed.get("timestamp","")))
    c.drawString(40,680,"Hash (SHA256): " + cert_signed.get("hash","")[:64])
    c.showPage()
    c.save()

def send_email(smtp_cfg, to_email, attachments):
    import smtplib
    from email.message import EmailMessage
    host = smtp_cfg.get("host")
    port = int(smtp_cfg.get("port", 587))
    user = smtp_cfg.get("user")
    pwd = smtp_cfg.get("pass")
    sender = smtp_cfg.get("from")

    msg = EmailMessage()
    msg["Subject"] = f"SecureWipe Certificate {os.path.basename(attachments[0])}"
    msg["From"] = sender or user
    msg["To"] = to_email
    msg.set_content("Attached: SecureWipe signed certificate (JSON) and PDF.")

    for path in attachments:
        with open(path,'rb') as f:
            data = f.read()
            if path.lower().endswith(".pdf"):
                maintype, subtype = "application","pdf"
            else:
                maintype, subtype = "application","json"
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))

    attempts = 3
    last_err = None
    for i in range(attempts):
        try:
            if port == 465:
                s = smtplib.SMTP_SSL(host, port, timeout=10)
                s.login(user, pwd)
            else:
                s = smtplib.SMTP(host, port, timeout=10)
                s.starttls()
                s.login(user, pwd)
            s.send_message(msg)
            s.quit()
            return True, "sent"
        except Exception as e:
            last_err = str(e)
            time.sleep(2 ** i)
    return False, f"failed after {attempts}: {last_err}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert", required=True)
    parser.add_argument("--email", required=False)
    parser.add_argument("--private-key", required=False)
    parser.add_argument("--submit-url", required=False)
    args = parser.parse_args()

    cert_path = args.cert
    if not os.path.exists(cert_path):
        print("Certificate not found:", cert_path, file=sys.stderr)
        sys.exit(2)

    cert = json.load(open(cert_path))

    private_key = load_private_key(args)
    payload_bytes = json.dumps(cert, separators=(",",":"), sort_keys=True).encode()

    signature = sign_payload(private_key, payload_bytes)
    sig_hex = signature.hex()

    cert_signed = dict(cert)
    cert_signed["signature"] = {"alg":"RSASSA-PKCS1v15","hex": sig_hex}

    out_json = cert_path.replace(".json","-signed.json")
    with open(out_json, "w") as f:
        json.dump(cert_signed, f, indent=2)

    out_pdf = out_json.replace(".json", ".pdf")
    try:
        make_pdf(cert_signed, out_pdf)
    except Exception as e:
        print("PDF generation failed:", e, file=sys.stderr)

    email_status = None
    smtp_cfg = {}
    if os.environ.get("SMTP_HOST"):
        smtp_cfg["host"] = os.environ.get("SMTP_HOST")
        smtp_cfg["port"] = os.environ.get("SMTP_PORT","587")
        smtp_cfg["user"] = os.environ.get("SMTP_USER")
        smtp_cfg["pass"] = os.environ.get("SMTP_PASS")
        smtp_cfg["from"] = os.environ.get("SMTP_FROM", smtp_cfg["user"])
    else:
        p = os.path.expanduser("~/.securewipe/smtp.json")
        if os.path.exists(p):
            smtp_cfg = json.load(open(p))

    if args.email and smtp_cfg:
        ok, status = send_email(smtp_cfg, args.email, [out_json, out_pdf])
        email_status = status
        if not ok:
            print("Email failed:", status, file=sys.stderr)
    else:
        if args.email:
            print("No SMTP config found; created files:", out_json, out_pdf)

    if args.submit_url:
        try:
            import requests
            resp = requests.post(args.submit_url, json=cert_signed, timeout=15)
            print("Submitted to verifier:", resp.status_code, resp.text)
        except Exception as e:
            print("Submit failed:", e, file=sys.stderr)

    print("Signed cert:", out_json)
    if email_status:
        print("Email status:", email_status)

if __name__ == "__main__":
    main()
