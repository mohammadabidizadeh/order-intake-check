"""Generate the API contract without real credentials or application state."""

import json
import os
import secrets
from pathlib import Path

from ordercheck.api import create_app


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    os.environ["ORDERCHECK_TOKEN"] = secrets.token_urlsafe(32)
    os.environ["ORDERCHECK_CATALOG"] = str(root / "examples/catalog.csv")
    document = json.dumps(create_app().openapi(), indent=2, ensure_ascii=False)
    (root / "docs/openapi.json").write_text(document + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
