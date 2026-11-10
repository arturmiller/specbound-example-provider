# Specbound Example Provider

A minimal, **synthetic** evidence-provider pack for [Specbound](https://github.com/arturmiller/specbound). It emits a fixed demonstration value; it does not inspect infrastructure, prove a security property, need credentials, or contact a cloud API. Never use this fixture as production evidence.

The pack declares `demo.fixture/v1`, request and response schemas, an observation-value schema, a request fixture, and an explicitly pinned Python runtime. The collector reads `SPECBOUND_REQUEST` and emits one JSON response on stdout. Specbound's runner has no network, mounts, or credentials; the manifest embeds the source as the Python command so the declared command and the reviewed source can be compared without fetching code at runtime. Regenerate the manifest with `python scripts/sync_manifest.py` after changing the collector.

## Verify locally

Python 3.12+, Git, Docker and a local Specbound checkout are required. Install `services/worker/requirements.txt` from that checkout in a virtual environment (on Windows also install `pywin32` for Docker's named pipe), pull the exact digest from `provider.yaml`, and set `SPECBOUND_ROOT` to the checkout path. Then run:

```sh
python scripts/sync_manifest.py --check
python -m unittest discover -s tests -p 'test_*.py' -v
```

The integration test clones this Git repository into a temporary directory, loads the exact committed pack via Specbound's validator, and runs the collector through the real restricted Docker runner. It asserts the observation's scope, subject, capability, synthetic value and provenance. It requires the pinned image to already be present; no image is automatically approved or pulled by the runner. To verify a published repository/tag, set `PROVIDER_REPO_URL` and `PROVIDER_REF` to the Git URL and tag or commit before running the tests.

Manifest validation and this fixture are not an image approval, a production collector, a cloud integration, or a guarantee that a deployed system is compliant.
