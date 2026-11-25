"""Exercise the CLI/API agreement over loopback with a temporary process and token."""

import json
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    catalog = root / "examples/catalog.csv"
    token = secrets.token_urlsafe(32)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "ordercheck.api:create_app", "--factory", "--host", "127.0.0.1",
         "--port", str(port), "--no-proxy-headers", "--limit-concurrency", "8",
         "--no-access-log", "--log-level", "warning"],
        env=os.environ | {"ORDERCHECK_TOKEN": token, "ORDERCHECK_CATALOG": str(catalog)}, cwd=root,
    )
    client = build_opener(ProxyHandler({}))
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            if server.poll() is not None:
                raise RuntimeError("Service exited before readiness.")
            try:
                with client.open(base + "/healthz", timeout=1) as ready:
                    assert json.load(ready) == {"status": "ok"}
                break
            except URLError:
                time.sleep(0.1)
        else:
            raise RuntimeError("Readiness timed out.")

        data = (root / "examples/orders.csv").read_bytes()
        headers = {"Content-Type": "text/csv"}
        try:
            client.open(Request(base + "/v1/order-previews", data=data, headers=headers), timeout=3)
        except HTTPError as exc:
            assert exc.code == 401
            exc.close()
        else:
            raise AssertionError("Missing token accepted.")
        headers["Authorization"] = f"Bearer {token}"
        for name, exit_code, counts in (("orders.csv", 2, (1, 1)), ("orders-corrected.csv", 0, (2, 0))):
            data = (root / "examples" / name).read_bytes()
            cli = subprocess.run([sys.executable, "-m", "ordercheck", str(root / "examples" / name),
                                  "--catalog", str(catalog)], cwd=root, capture_output=True, timeout=10)
            assert cli.returncode == exit_code, (name, cli.returncode)
            expected = json.loads(cli.stdout)
            assert (expected["ready_orders"], expected["held_orders"]) == counts
            with client.open(Request(base + "/v1/order-previews", data=data, headers=headers), timeout=3) as result:
                assert json.load(result) == expected
            print(f"{name}: {expected['ready_orders']} ready, {expected['held_orders']} held")
        print("Loopback health, authorization and both previews passed.")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()


if __name__ == "__main__":
    main()
