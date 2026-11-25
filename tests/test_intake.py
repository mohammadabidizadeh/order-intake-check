import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ordercheck.intake import FileProblem, MAX_BYTES, MAX_RECORDS, load_catalog, preview, valid_id

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
HEADER = "order_id,line_id,source_sku,quantity\n"


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog((EXAMPLES / "catalog.csv").read_bytes())

    def test_demo_is_order_atomic_even_when_interleaved(self):
        result = preview((EXAMPLES / "orders.csv").read_bytes(), self.catalog)
        self.assertEqual((result.records, result.ready_orders, result.held_orders), (4, 1, 1))
        valid, held = result.orders
        self.assertEqual([line.line_id for line in valid.lines], ["01", "02"])
        self.assertEqual([line.item_code for line in valid.lines], ["BOX-01", "PART-127"])
        self.assertEqual(held.lines, [])
        self.assertEqual((held.issues[0].record, held.issues[0].code), (5, "unknown_sku"))

    def test_corrected_fixture_is_repeatable(self):
        data = (EXAMPLES / "orders-corrected.csv").read_bytes()
        self.assertEqual(preview(data, self.catalog), preview(data, self.catalog))
        self.assertEqual(preview(data, self.catalog).ready_orders, 2)

    def test_quantities_and_significant_ids(self):
        data = (HEADER + "۰۰۱,01,00127,۰۲\n001,01,00127,٣").encode("utf-8-sig")
        result = preview(data, self.catalog)
        self.assertEqual([order.order_id for order in result.orders], ["۰۰۱", "001"])
        self.assertEqual([order.lines[0].quantity for order in result.orders], [2, 3])

    def test_duplicate_line_holds_only_its_own_order(self):
        data = (HEADER + "A,1,S-001,1\nB,1,S-001,1\nA,1,S-002,2").encode()
        first, second = preview(data, self.catalog).orders
        self.assertEqual((first.lines, first.issues[0].code), ([], "duplicate_line"))
        self.assertEqual(second.status, "ready")

    def test_repeated_sku_allowed_for_distinct_lines(self):
        data = (HEADER + "A,1,S-001,1\nA,2,S-001,1").encode()
        self.assertEqual(len(preview(data, self.catalog).orders[0].lines), 2)

    def test_quantity_range(self):
        for value in ("", "0", "۰", "-1", "1.1", "1e2", " 2", "1000000", "²", "１"):
            with self.subTest(value=value):
                order = preview((HEADER + f"A,1,S-001,{value}").encode(), self.catalog).orders[0]
                self.assertEqual(order.issues[0].code, "invalid_quantity")
        result = preview((HEADER + "A,1,S-001,999999").encode(), self.catalog)
        self.assertEqual(result.orders[0].lines[0].quantity, 999999)

    def test_multiple_issues_reported_without_echo(self):
        order = preview((HEADER + "A,,=formula,0").encode(), self.catalog).orders[0]
        self.assertEqual([i.code for i in order.issues], ["invalid_line_id", "invalid_sku", "invalid_quantity"])
        self.assertEqual(order.lines, [])

    def test_case_and_leading_zeroes_in_skus(self):
        for value in ("127", "s-001"):
            self.assertEqual(preview((HEADER + f"A,1,{value},1").encode(), self.catalog).held_orders, 1)

    def test_identifiers_preserve_unicode_and_length_boundaries(self):
        for value in ("X", "A" * 64, "کد/۲.۳-۴_۵", "²"):
            with self.subTest(value=value):
                self.assertTrue(valid_id(value))
        for value in ("", "A" * 65, "_ref", "A B", "A\n", "A\u200cB", "A\u0301"):
            with self.subTest(value=value):
                self.assertFalse(valid_id(value))

    def test_reordered_quoted_columns_and_crlf(self):
        result = preview(b'quantity,source_sku,order_id,line_id\r\n"2","S-001","A","01"\r\n', self.catalog)
        self.assertEqual(result.orders[0].lines[0].line_id, "01")

    def test_structural_failures_reject_file(self):
        cases = [
            (HEADER.encode(), "empty_file", None),
            (b"order_id,line_id,source_sku,source_sku\n", "invalid_header", 1),
            ((HEADER + ",1,S-001,1").encode(), "invalid_order_id", 2),
            ((HEADER + "A,1,S-001,1\nB,1").encode(), "invalid_width", 3),
            ((HEADER + '"unterminated').encode(), "invalid_csv", 2),
            (b'\xff\xfe', "invalid_encoding", None),
            (b"a" * (MAX_BYTES + 1), "file_too_large", None),
        ]
        for data, code, record in cases:
            with self.subTest(code=code), self.assertRaises(FileProblem) as failure:
                preview(data, self.catalog)
            self.assertEqual((failure.exception.code, failure.exception.record), (code, record))

    def test_record_budget(self):
        rows = "".join(f"A,{i},S-001,1\n" for i in range(MAX_RECORDS))
        self.assertEqual(preview((HEADER + rows).encode(), self.catalog).records, MAX_RECORDS)
        with self.assertRaises(FileProblem) as failure:
            preview((HEADER + rows + "B,1,S-001,1").encode(), self.catalog)
        self.assertEqual(failure.exception.code, "too_many_records")

    def test_logical_record_after_multiline_field(self):
        data = (HEADER + 'A,1,"S-\n001",2\r\nB,1,S-001,1\r\nA,1,S-002,1').encode()
        held, ready = preview(data, self.catalog).orders
        self.assertEqual([(i.record, i.code) for i in held.issues],
                         [(2, "invalid_sku"), (4, "duplicate_line")])
        self.assertEqual(held.lines, [])
        self.assertEqual(ready.status, "ready")

    def test_exact_byte_limit_and_catalog_record_limit(self):
        # Fill the budget with correctly shaped rows. Duplicate lines hold this order.
        row = b"A" * 64 + b"," + b"L" * 64 + b",S-001,1\n"
        count, remainder = divmod(MAX_BYTES - len(HEADER), len(row))
        data = HEADER.encode() + row * (count - 1) + row.rstrip(b"\n") + b"0" * remainder + b"\n"
        self.assertEqual(len(data), MAX_BYTES)
        self.assertEqual(preview(data, self.catalog).held_orders, 1)
        with self.assertRaises(FileProblem) as failure:
            preview(data + b"\n", self.catalog)
        self.assertEqual(failure.exception.code, "file_too_large")
        mapping = b"source_sku,item_code\n" + b"".join(
            f"S{i},ITEM\n".encode() for i in range(MAX_RECORDS)
        )
        self.assertEqual(len(load_catalog(mapping)), MAX_RECORDS)
        with self.assertRaises(FileProblem) as failure:
            load_catalog(mapping + b"EXTRA,ITEM\n")
        self.assertEqual((failure.exception.code, failure.exception.record),
                         ("too_many_records", MAX_RECORDS + 2))

    def test_late_file_error_emits_no_partial_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            orders = Path(directory) / "orders.csv"
            orders.write_bytes((HEADER + "A,1,S-001,2\nB,2").encode())
            run = subprocess.run([sys.executable, "-m", "ordercheck", str(orders),
                                  "--catalog", str(EXAMPLES / "catalog.csv")], capture_output=True)
        self.assertEqual((run.returncode, run.stdout), (1, b""))
        self.assertEqual(json.loads(run.stderr)["record"], 3)
        self.assertEqual(json.loads(run.stderr)["code"], "invalid_width")

    def test_catalog_refuses_ambiguous_or_invalid_entries(self):
        for rows, code in [("A,B\nA,C", "duplicate_mapping"), ("A,", "invalid_catalog_id")]:
            with self.subTest(code=code), self.assertRaises(FileProblem) as failure:
                load_catalog(("source_sku,item_code\n" + rows).encode())
            self.assertEqual(failure.exception.code, code)

    def test_cli_exit_codes_and_json(self):
        for filename, expected in [("orders.csv", 2), ("orders-corrected.csv", 0), ("missing.csv", 1)]:
            with self.subTest(filename=filename):
                run = subprocess.run([sys.executable, "-m", "ordercheck", str(EXAMPLES / filename),
                                      "--catalog", str(EXAMPLES / "catalog.csv")], capture_output=True, check=False)
                self.assertEqual(run.returncode, expected)
                if expected != 1:
                    self.assertIn("orders", json.loads(run.stdout))
                else:
                    self.assertEqual(json.loads(run.stderr)["code"], "unreadable_file")
                    self.assertNotIn(b"missing.csv", run.stderr)
                    self.assertFalse(run.stdout)
