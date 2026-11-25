"""Rules shared by the command line and HTTP preview."""

import csv
import io
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

MAX_BYTES = 512 * 1024
MAX_RECORDS = 5_000
ORDER_FIELDS = ("order_id", "line_id", "source_sku", "quantity")
CATALOG_FIELDS = ("source_sku", "item_code")
QUANTITY_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
# Python's Unicode \w includes alphanumerics and underscore.
IDENTIFIER = re.compile(r"[^\W_][\w./-]{0,63}")


class FileProblem(ValueError):
    def __init__(self, code: str, message: str, record: int | None = None):
        super().__init__(message)
        self.code = code
        self.record = record


@dataclass(frozen=True, slots=True)
class Issue:
    record: int
    field: str
    code: str


@dataclass(frozen=True, slots=True)
class Line:
    line_id: str
    item_code: str
    quantity: int


@dataclass
class Order:
    order_id: str
    status: Literal["ready", "held"]
    lines: list[Line]
    issues: list[Issue]


@dataclass
class Preview:
    records: int
    ready_orders: int
    held_orders: int
    orders: list[Order]


def read_limited(path: Path) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    check_size(len(data))
    return data


def check_size(size: int) -> None:
    if size > MAX_BYTES:
        raise FileProblem("file_too_large", "Each CSV may contain at most 524288 bytes.")


def records(data: bytes, fields: tuple[str, ...]) -> Iterator[tuple[int, dict[str, str]]]:
    check_size(len(data))
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise FileProblem("invalid_encoding", "Save the CSV as UTF-8.") from None

    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    record = 1
    try:
        header = next(reader, [])
        if len(header) != len(fields) or set(header) != set(fields):
            raise FileProblem("invalid_header", "Expected columns: " + ", ".join(fields), 1)
        count = 0
        record = 2
        for values in reader:
            count += 1
            if count > MAX_RECORDS:
                raise FileProblem("too_many_records", "Each CSV may contain at most 5000 data records.", record)
            if len(values) != len(header):
                raise FileProblem("invalid_width", "Record has the wrong number of columns.", record)
            yield record, dict(zip(header, values, strict=True))
            record += 1
        if count == 0:
            raise FileProblem("empty_file", "At least one data record is required.")
    except csv.Error:
        raise FileProblem("invalid_csv", "Invalid CSV quoting or field size.", record) from None


def valid_id(value: str) -> bool:
    return IDENTIFIER.fullmatch(value) is not None


def _quantity(value: str) -> int | None:
    if not 1 <= len(value) <= 6:
        return None
    digits = value if value.isascii() else value.translate(QUANTITY_DIGITS)
    if digits.isascii() and digits.isdecimal():
        return int(digits) or None
    return None


def load_catalog(data: bytes) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for number, row in records(data, CATALOG_FIELDS):
        source, target = row["source_sku"], row["item_code"]
        if not valid_id(source) or not valid_id(target):
            raise FileProblem("invalid_catalog_id", "A catalog identifier is invalid.", number)
        if source in mapping:
            raise FileProblem("duplicate_mapping", "A source SKU must occur exactly once.", number)
        mapping[source] = target
    return mapping


@dataclass(slots=True)
class _OrderState:
    lines: list[Line] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    seen_lines: set[str] = field(default_factory=set)


def preview(data: bytes, catalog: Mapping[str, str]) -> Preview:
    groups: dict[str, _OrderState] = {}
    count = 0
    for number, row in records(data, ORDER_FIELDS):
        count += 1
        order_id, line_id, sku = row["order_id"], row["line_id"], row["source_sku"]
        if not valid_id(order_id):
            raise FileProblem("invalid_order_id", "Cannot assign this record to a valid order.", number)
        if order_id not in groups:
            groups[order_id] = _OrderState()
        group = groups[order_id]
        issues = []
        if not valid_id(line_id):
            issues.append(Issue(number, "line_id", "invalid_line_id"))
        elif line_id in group.seen_lines:
            issues.append(Issue(number, "line_id", "duplicate_line"))
        else:
            group.seen_lines.add(line_id)
        if not valid_id(sku):
            issues.append(Issue(number, "source_sku", "invalid_sku"))
        elif sku not in catalog:
            issues.append(Issue(number, "source_sku", "unknown_sku"))
        quantity = _quantity(row["quantity"])
        if quantity is None:
            issues.append(Issue(number, "quantity", "invalid_quantity"))
        if issues:
            group.lines.clear()
            group.issues.extend(issues)
        elif not group.issues:
            group.lines.append(Line(line_id, catalog[sku], quantity))

    orders = [
        Order(key, "held" if group.issues else "ready", group.lines, group.issues)
        for key, group in groups.items()
    ]
    held = sum(order.status == "held" for order in orders)
    return Preview(count, len(orders) - held, held, orders)
