"""Emit one explicitly synthetic observation for the requested subject and scope."""

import datetime
import json
import os

request = json.loads(os.environ["SPECBOUND_REQUEST"])
if request["capabilities"] != ["demo.fixture/v1"] or request["credentialsRef"] is not None:
    raise ValueError("Only the credential-free demo.fixture/v1 capability is supported")

response = {
    "schemaVersion": 1,
    "observations": [{
        "subjectId": request["subject"]["id"],
        "capability": "demo.fixture/v1",
        "scope": request["scope"],
        "observedAt": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"sourceRef": "fixture:synthetic-example"},
        "value": {"synthetic": True, "message": "example-only"},
    }],
}
print(json.dumps(response, separators=(",", ":")))
