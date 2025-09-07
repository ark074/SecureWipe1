#!/usr/bin/env python3
from cryptography.hazmat.primitives.asymmetric import rsa, serialization
from cryptography.hazmat.backends import default_backend
import argparse, os
parser = argparse.ArgumentParser()
parser.add_argument("--out-dir", default=".")
args = parser.parse_args()
priv = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
priv_pem = priv.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())
pub_pem = priv.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
open(os.path.join(args.out_dir,"private.pem"),"wb").write(priv_pem)
open(os.path.join(args.out_dir,"public.pem"),"wb").write(pub_pem)
print("Wrote private.pem and public.pem in", args.out_dir)
