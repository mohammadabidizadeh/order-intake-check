"""Offline operator entry point. Exit 2 means at least one order needs review."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .intake import FileProblem, load_catalog, preview, read_limited


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview an order CSV against a catalog mapping.")
    parser.add_argument("orders", type=Path)
    parser.add_argument("--catalog", type=Path, required=True)
    args = parser.parse_args()
    try:
        catalog = load_catalog(read_limited(args.catalog))
        result = preview(read_limited(args.orders), catalog)
    except FileProblem as exc:
        print(json.dumps({"code": exc.code, "message": str(exc), "record": exc.record}), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"code": "unreadable_file", "message": "Could not read the order or catalog file.",
                          "record": None}), file=sys.stderr)
        return 1
    print(json.dumps(asdict(result), indent=2))
    return 2 if result.held_orders else 0


if __name__ == "__main__":
    raise SystemExit(main())
