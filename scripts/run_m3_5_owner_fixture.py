"""Create two reviewable M3.5 branch campaigns in the development database."""

import json

from fastapi.testclient import TestClient

from app.api import app
from app.config import get_settings
from tests.test_m3_lantern_scenario import _run_branching_lantern


def main() -> None:
    database_name = get_settings().database_url.rsplit("/", 1)[-1].split("?", 1)[0]
    if not database_name.startswith("gandalfdnd_dev"):
        raise RuntimeError(
            "Refusing to create the M3.5 owner fixture outside a gandalfdnd_dev database"
        )
    with TestClient(app) as client:
        bridge_world, bridge_ids = _run_branching_lantern(client, "signal_bridge")
        tunnel_world, tunnel_ids = _run_branching_lantern(client, "flooded_tunnel")
    print(
        json.dumps(
            {
                "fixture": "m3.5-branching-lantern-v1",
                "database": database_name,
                "external_provider_calls": 0,
                "signal_bridge": {**bridge_ids, "world": bridge_world},
                "flooded_tunnel": {**tunnel_ids, "world": tunnel_world},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
