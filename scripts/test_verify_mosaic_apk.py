import unittest
from unittest.mock import patch
import subprocess
import json
from pathlib import Path

from verify_mosaic_apk import fingerprint, tool, validate_outputs


class SigningVerificationTests(unittest.TestCase):
    def setUp(self):
        self.config = {"schemaVersion": 1, "applicationId": "io.github.constbogdan.mosaic",
                       "expectedCertificateSha256": "ab" * 32}
        self.provenance = dict(publication=True, dirty=False, versionCode=1, versionName="1.0.1",
                               sourceSha="a" * 40, sourceTree="b" * 40, epoch="c" * 40, upstreamBaseline="d" * 40,
                               apkSha256="e" * 64)
        self.signature = "Signer #1 certificate SHA-256 digest: " + "ab" * 32
        self.badging = "package: name='io.github.constbogdan.mosaic' versionCode='1' versionName='1.0.1'"

    def check(self):
        return validate_outputs(self.config, self.provenance, self.signature, self.badging)

    def test_matching_public_identity(self):
        self.assertEqual(self.check(), "ab" * 32)
        self.assertEqual(fingerprint(":".join(["AB"] * 32)), "ab" * 32)

    def test_repository_policy_pins_established_public_certificate(self):
        self.config = json.loads(Path(__file__).with_name("mosaic-signing.json").read_text())
        approved = fingerprint("63:75:61:83:D6:E7:7B:2A:5E:7C:D6:9B:40:95:32:EE:0B:3C:47:10:E1:3A:10:22:8D:FB:58:18:6F:55:6B:84")
        self.assertEqual(self.config["expectedCertificateSha256"], approved)
        self.signature = "Signer #1 certificate SHA-256 digest: " + approved
        self.assertEqual(self.check(), approved)
        for digest in ("ab" * 32, approved[:-1] + "5", ""):
            self.signature = "Signer #1 certificate SHA-256 digest: " + digest
            with self.assertRaises(ValueError):
                self.check()

    def test_unconfigured_or_wrong_certificate(self):
        for value in (None, "", "00" * 32):
            self.config["expectedCertificateSha256"] = value
            with self.assertRaises(ValueError):
                self.check()

    def test_multiple_signers_rejected(self):
        self.signature += "\nSigner #2 certificate SHA-256 digest: " + "ab" * 32
        with self.assertRaises(ValueError):
            self.check()

    def test_wrong_package_version_or_debug_rejected(self):
        original = self.badging
        for value in (original.replace("mosaic'", "mosaic.debug'"), original.replace("versionCode='1'", "versionCode='2'"),
                      original + "\napplication-debuggable"):
            self.badging = value
            with self.assertRaises(ValueError):
                self.check()

    def test_untrusted_or_incomplete_provenance(self):
        for field, value in (("dirty", True), ("publication", False), ("sourceSha", "short"), ("versionCode", 0),
                             ("apkSha256", "")):
            original = self.provenance[field]
            self.provenance[field] = value
            with self.assertRaises(ValueError):
                self.check()
            self.provenance[field] = original

    def test_failed_sdk_verification_cannot_accept_printed_fingerprint(self):
        result = subprocess.CompletedProcess([], 1, self.signature, "verification failed")
        with patch("verify_mosaic_apk.subprocess.run", return_value=result):
            with self.assertRaises(ValueError):
                tool(["apksigner", "verify", "fixture.apk"])


if __name__ == "__main__":
    unittest.main()
