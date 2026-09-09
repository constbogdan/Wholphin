"""Verify public APK identity only. Never accepts or opens a keystore/private key."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def fingerprint(value):
    normalized = str(value or "").replace(":", "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized):
        raise ValueError("Expected public certificate SHA-256 must be configured first")
    return normalized


def validate_outputs(config, provenance, signature, badging):
    expected = fingerprint(config.get("expectedCertificateSha256"))
    if config.get("schemaVersion") != 1 or config.get("applicationId") != "io.github.constbogdan.mosaic":
        raise ValueError("Invalid Mosaic signing policy")
    signers = re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)$", signature, re.M)
    if len(signers) != 1 or fingerprint(signers[0]) != expected:
        raise ValueError("APK certificate does not match the approved single Mosaic signer")
    package = re.search(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging, re.M)
    if not package or "application-debuggable" in badging:
        raise ValueError("Expected a non-debuggable Release APK")
    if provenance.get("publication") is not True or provenance.get("dirty") is not False:
        raise ValueError("Expected clean publishable source provenance")
    code = provenance.get("versionCode")
    if type(code) is not int or not 1 <= code <= 2100000000 or provenance.get("versionName") != f"1.0.{code}":
        raise ValueError("Invalid downstream version identity")
    for field in ("sourceSha", "sourceTree", "epoch", "upstreamBaseline"):
        if not re.fullmatch(r"[0-9a-f]{40}", provenance.get(field, "")):
            raise ValueError("Missing exact source provenance")
    if not re.fullmatch(r"[0-9a-f]{64}", provenance.get("apkSha256", "")):
        raise ValueError("Missing validated unsigned APK hash")
    if package.groups() != (config["applicationId"], str(code), provenance["versionName"]):
        raise ValueError("APK package/version differs from validated source")
    return expected


def tool(args):
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if result.returncode:
        raise ValueError("Public APK verification tool failed; no acceptance record produced")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("mosaic-signing.json"))
    parser.add_argument("--apksigner", required=True)
    parser.add_argument("--aapt", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text())
        fingerprint(config.get("expectedCertificateSha256"))
        provenance = json.loads(args.provenance.read_text())
        signature = tool([args.apksigner, "verify", "--verbose", "--print-certs", str(args.apk)])
        badging = tool([args.aapt, "dump", "badging", str(args.apk)])
        expected = validate_outputs(config, provenance, signature, badging)
        record = {"schemaVersion": 1, "applicationId": config["applicationId"],
                  "certificateSha256": expected, "source": provenance,
                  "signedApkSha256": hashlib.sha256(args.apk.read_bytes()).hexdigest()}
        # Never overwrite an accepted record, even if a rerun claims the same version.
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(record, output, indent=2, sort_keys=True)
            output.write("\n")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
