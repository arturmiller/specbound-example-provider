import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = Path(os.environ["SPECBOUND_ROOT"]).resolve()
sys.path.insert(0, str(PLATFORM / "services" / "api"))
sys.path.insert(0, str(PLATFORM / "services" / "worker"))

import docker  # noqa: E402
from app.git_source import GitSnapshot  # noqa: E402
from app.provider_pack import load_provider_pack  # noqa: E402
from collector_runner import ApprovedCollector, run_collector  # noqa: E402


class FixtureProviderTest(unittest.TestCase):
    def test_manifest_contains_exact_reviewed_collector(self):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_manifest.py"), "--check"], check=True)

    def test_rejects_credential_and_other_capability(self):
        original = json.loads((ROOT / "tests" / "request.json").read_text(encoding="utf-8"))
        for field, value in [("credentialsRef", "credential:fixture"), ("capabilities", ["other.capability/v1"])]:
            request = {**original, field: value}
            result = subprocess.run([sys.executable, str(ROOT / "collector.py")], env={**os.environ, "SPECBOUND_REQUEST": json.dumps(request)}, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")

    def test_git_pack_runs_in_real_specbound_collector(self):
        source = os.environ.get("PROVIDER_REPO_URL", str(ROOT))
        ref = os.environ.get("PROVIDER_REF")
        if not ref:
            self.assertEqual(source, str(ROOT), "PROVIDER_REF is required with PROVIDER_REPO_URL")
            ref = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        with tempfile.TemporaryDirectory() as temp:
            clone = Path(temp) / "provider"
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", "--", source, str(clone)], check=True)
            subprocess.run(["git", "-C", str(clone), "checkout", "--quiet", "--detach", ref], check=True)
            commit = subprocess.check_output(["git", "-C", str(clone), "rev-parse", "HEAD"], text=True).strip()
            tracked = subprocess.check_output(["git", "-C", str(clone), "ls-files", "-z"]).decode("utf-8").split("\0")
            files = {name: (clone / name).read_bytes() for name in tracked if name}
            provider = load_provider_pack(GitSnapshot(commit, files))
            request = json.loads(files["tests/request.json"])
            runtime = provider["manifest"]["runtime"]
            self.assertEqual(runtime["entrypoint"][2], files["collector.py"].decode("utf-8"))
            client = docker.from_env()
            self.assertTrue(client.ping())
            result = run_collector(client, provider, request, ApprovedCollector(runtime["image"], tuple(runtime["entrypoint"])))
            self.assertEqual((result.status, result.reason), ("OBSERVED", "ok"))
            self.assertEqual(len(result.observations), 1)
            observed = result.observations[0]
            self.assertEqual(observed["subjectId"], request["subject"]["id"])
            self.assertEqual(observed["scope"], request["scope"])
            self.assertEqual(observed["capability"], "demo.fixture/v1")
            self.assertEqual(observed["value"], {"synthetic": True, "message": "example-only"})
            self.assertEqual(observed["provenance"]["sourceRef"], "fixture:synthetic-example")


if __name__ == "__main__":
    unittest.main()
