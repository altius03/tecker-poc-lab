from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local self-signed device certificate for PoC mTLS testing.")
    parser.add_argument("--customer-id", required=True)
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--out-dir", default="certs")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    key_path = out_dir / "device.key"
    cert_path = out_dir / "device.crt"
    subject = f"/CN={args.device_id}/O={args.customer_id}/OU=edr-agent-parser"

    command = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        str(key_path),
        "-out",
        str(cert_path),
        "-days",
        str(args.days),
        "-subj",
        subject,
    ]
    completed = subprocess.run(command, text=True)
    if completed.returncode != 0:
        print("openssl command failed. Install OpenSSL or create cert/key manually.")
        return completed.returncode

    print(f"cert={cert_path}")
    print(f"key={key_path}")
    print("Do not commit certs/device.key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
