"""Measure in-process validation of 5,000 synthetic lines. Run as a module."""

import platform
import statistics
import time

from ordercheck.intake import preview


def main() -> None:
    data = ("order_id,line_id,source_sku,quantity\n" +
            "".join(f"O{i // 5},{i % 5},X,2\n" for i in range(5000))).encode()
    catalog = {"X": "ITEM-01"}
    times = []
    for run in range(11):
        start = time.perf_counter()
        result = preview(data, catalog)
        elapsed = 1000 * (time.perf_counter() - start)
        assert (result.records, result.ready_orders, result.held_orders) == (5000, 1000, 0)
        if run:
            times.append(elapsed)
    print(f"{platform.python_implementation()} {platform.python_version()} | 5,000 lines | {len(data)} bytes")
    print(f"10 warm runs (ms): min {min(times):.2f}, median {statistics.median(times):.2f}, max {max(times):.2f}")


if __name__ == "__main__":
    main()
