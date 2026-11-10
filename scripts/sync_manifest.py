"""Keep the self-contained runtime command equal to the reviewed collector source."""
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
collector = (root / "collector.py").read_text(encoding="utf-8")
manifest = {
    "apiVersion": "specbound.example/v1alpha1",
    "kind": "EvidenceProviderPack",
    "metadata": {"id": "org.specbound.example-provider", "version": "1.1.0", "title": "Synthetic fixture provider", "description": "Synthetic examples only; not infrastructure evidence."},
    "runtime": {
        "kind": "approved-container",
        "image": "python:3.12-slim@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54",
        "entrypoint": ["python", "-c", collector],
        "input": "contracts/collect-request.json",
        "output": "contracts/observation.json",
    },
    "capabilities": [{"id": "demo.fixture", "version": "v1", "outputSchema": "schemas/fixture.json"}],
    "permissions": {},
    "tests": ["tests/request.json"],
}
result = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
path = root / "provider.yaml"
if args.check:
    if not path.exists() or path.read_text(encoding="utf-8") != result:
        raise SystemExit("provider.yaml is out of date; run python scripts/sync_manifest.py")
else:
    path.write_text(result, encoding="utf-8", newline="\n")
