#!/usr/bin/env python3
import argparse, json, os, sys
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def load_pubkey(args):
    if os.environ.get("PUBKEY_CONTENT"):
        key_pem = os.environ["PUBKEY_CONTENT"].encode()
        return serialization.load_pem_public_key(key_pem, backend=default_backend())
    if args.pubkey and os.path.exists(args.pubkey):
        return serialization.load_pem_public_key(open(args.pubkey,'rb').read(), backend=default_backend())
    p = os.path.expanduser("~/.securewipe/public.pem")
    if os.path.exists(p):
        return serialization.load_pem_public_key(open(p,'rb').read(), backend=default_backend())
    print("No public key found", file=sys.stderr); sys.exit(2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cert", required=True)
    parser.add_argument("--pubkey", required=False)
    args = parser.parse_args()
    cert = json.load(open(args.cert))
    if "signature" not in cert or "hex" not in cert["signature"]:
        print("No signature in certificate"); sys.exit(2)
    sig = bytes.fromhex(cert["signature"]["hex"])
    payload = dict(cert); del payload["signature"]
    payload_bytes = json.dumps(payload, separators=(",",":"), sort_keys=True).encode()
    pub = load_pubkey(args)
    try:
        pub.verify(sig, payload_bytes, padding.PKCS1v15(), hashes.SHA256())
        print("Signature valid")
        print(json.dumps(payload, indent=2))
    except Exception as e:
        print("Verification failed:", e); sys.exit(3)

if __name__ == "__main__":
    main()
