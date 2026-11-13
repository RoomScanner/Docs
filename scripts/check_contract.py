#!/usr/bin/env python3
"""Check that API contract documents follow the RoomScanner contract format.

Usage: python3 scripts/check_contract.py [files...]
With no arguments, checks every .md file in api-contract/ except README.md.
The format is described in api-contract/_TEMPLATE.md.
"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTRACT_DIR = ROOT / "api-contract"

CONTRACT_SECTIONS = [
    "Background", "Design Decisions", "Identity Model", "Endpoint Summary",
    "Enums", "Endpoints", "Core Schemas", "Open Points", "Changelog",
]
COMMON_SECTIONS = [
    "Common Headers", "Common Error Response", "Status Codes",
    "Pagination and Sorting", "Kafka Message Envelope", "Socket Events",
]
META_KEYS = ["Version", "Owner", "Consumers", "Last updated"]

FIELD_HEADER = ["Field", "Type", "Required", "Description"]
PARAM_HEADER = ["Parameter", "Type", "Required", "Description"]
ENDPOINT_META_HEADER = ["Protocol", "Provided by", "Consumed by", "Requirement IDs"]
TABLE_HEADERS = {
    "Identity Model": ["Identifier", "Type", "Description", "Usage"],
    "Endpoint Summary": ["#", "Method", "Path", "Protocol", "Description"],
    "Open Points": ["ID", "Topic", "Status"],
    "Changelog": ["Version", "Date", "Change"],
}

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
ENDPOINT_RE = re.compile(r"^(\d+)\. (GET|POST|PUT|PATCH|DELETE|KAFKA|SOCKET) (\S+)$")
REST_PATH_RE = re.compile(r"^/api/v1/[A-Za-z0-9/{}_-]+$")
KAFKA_TOPIC_RE = re.compile(r"^roomscanner\.(pp|cp|pms)\.[a-z0-9-]+\.(request|reply|event)$")
SOCKET_EVENT_RE = re.compile(r"^[a-z0-9]+(?:[.:-][a-z0-9]+)*$")
RESPONSE_H4_RE = re.compile(r"^([1-5]\d\d) [A-Za-z ]+ Response$")
ALLOWED_H4 = {
    "Path Parameters", "Query Parameters", "Request Body", "Response Codes",
    "Request Message", "Reply Message", "Event Message", "Failure and Retry",
    "Validation Rules", "Examples", "Notes",
}
PRIMITIVES = r"(?:string|integer|number|boolean|object)"
PASCAL_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------- parsing

def parse(text):
    """Split markdown into blocks: heading, table, code, text."""
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        ln = i + 1
        fence = re.match(r"^```(\w*)\s*$", line)
        if fence:
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            blocks.append({"kind": "code", "lang": fence.group(1), "text": "\n".join(lines[i + 1:j]), "ln": ln})
            i = j + 1
            continue
        heading = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if heading:
            blocks.append({"kind": "h", "level": len(heading.group(1)), "text": heading.group(2), "ln": ln})
            i += 1
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            header = rows[0]
            body = [r for r in rows[1:] if not all(re.fullmatch(r":?-{3,}:?", c) for c in r if c)]
            blocks.append({"kind": "table", "header": header, "rows": body, "ln": ln})
            continue
        if line.strip():
            blocks.append({"kind": "text", "text": line, "ln": ln})
        i += 1
    return blocks


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells, cur, esc = [], "", False
    for ch in s:
        if ch == "|" and not esc:
            cells.append(cur.strip())
            cur = ""
            continue
        esc = ch == "\\"
        cur += ch
    cells.append(cur.strip())
    return cells


def sections(blocks, level):
    """Group blocks under headings of the given level -> list of (heading, children)."""
    out, cur = [], None
    for b in blocks:
        if b["kind"] == "h" and b["level"] <= level:
            if b["level"] == level:
                cur = (b, [])
                out.append(cur)
            else:
                cur = None
            continue
        if cur is not None:
            cur[1].append(b)
    return out


def strip_code(s):
    return s.replace("`", "").strip()


# ---------------------------------------------------------------- checker

class Checker:
    def __init__(self, path):
        self.path = path
        self.rel = os.path.relpath(path, ROOT)
        self.errors = []

    def err(self, ln, msg):
        self.errors.append((ln, msg))

    # -- shared helpers

    def first(self, children, kind):
        return next((b for b in children if b["kind"] == kind), None)

    def check_table(self, table, header, where, ln):
        if table is None:
            self.err(ln, f"{where}: missing table with columns | {' | '.join(header)} |")
            return False
        if table["header"] != header:
            self.err(table["ln"], f"{where}: table columns must be | {' | '.join(header)} |, found | {' | '.join(table['header'])} |")
            return False
        for r in table["rows"]:
            if len(r) != len(header):
                self.err(table["ln"], f"{where}: row has {len(r)} cells, expected {len(header)}: {' | '.join(r)}")
        return True

    def check_json(self, code, where, ln):
        if code is None or code["lang"] != "json":
            self.err(ln, f"{where}: missing ```json example block")
            return None
        try:
            return json.loads(code["text"])
        except json.JSONDecodeError as e:
            self.err(code["ln"] + e.lineno, f"{where}: example is not valid JSON ({e.msg})")
            return None

    def check_type(self, t, ln, where):
        t = strip_code(t)
        base = re.sub(r" or null$", "", t)
        ok = (
            re.fullmatch(PRIMITIVES + r"(?: \([^)]+\))?", base)
            or re.fullmatch(r"string enum \(([A-Z][A-Za-z0-9]*)\)", base)
            or re.fullmatch(r"string enum: [A-Za-z0-9_, -]+", base)
            or re.fullmatch(r"object \(([A-Z][A-Za-z0-9]*)\)", base)
            or re.fullmatch(r"array<[^>]+>", base)
            or (PASCAL_RE.match(base) and base in self.known_names)
        )
        if not ok:
            self.err(ln, f"{where}: unknown type '{t}'. Use string, integer, number, boolean, object, array<T>, "
                         "string enum (EnumName), object (SchemaName), or a Core Schema name; add ' or null' if nullable")
        for ref in re.findall(r"\(([A-Z][A-Za-z0-9]*)\)|array<(?:string enum )?([A-Z][A-Za-z0-9]*)>", base):
            name = ref[0] or ref[1]
            if name and name not in self.known_names:
                self.err(ln, f"{where}: type refers to '{name}', which is not defined under Enums or Core Schemas")

    def check_fields(self, table, example, where, ln):
        if not self.check_table(table, FIELD_HEADER, where, ln):
            return
        names = set()
        for r in table["rows"]:
            if len(r) != 4:
                continue
            name, typ, req, desc = r
            name = strip_code(name)
            names.add(name)
            self.check_type(typ, table["ln"], f"{where}, field '{name}'")
            if not (req in ("Yes", "No") or req.startswith("Required when")):
                self.err(table["ln"], f"{where}, field '{name}': Required must be Yes, No or 'Required when ...'")
            if not desc:
                self.err(table["ln"], f"{where}, field '{name}': description is empty")
        if isinstance(example, dict):
            for key in example:
                if key not in names:
                    self.err(table["ln"], f"{where}: example has field '{key}' that is missing from the field table")
            for r in table["rows"]:
                if len(r) == 4:
                    name = strip_code(r[0])
                    if "." not in name and "[" not in name and r[2] == "Yes" and name not in example:
                        self.err(table["ln"], f"{where}: required field '{name}' is missing from the JSON example")

    def json_and_fields(self, children, where, ln):
        code = self.first(children, "code")
        example = self.check_json(code, where, ln)
        self.check_fields(self.first(children, "table"), example, where, ln)

    # -- document checks

    def run(self):
        text = pathlib.Path(self.path).read_text(encoding="utf-8")
        blocks = parse(text)
        if self.path.name == "common.md":
            self.check_h2(blocks, COMMON_SECTIONS)
        else:
            self.check_contract(blocks)
        return self.errors

    def check_h2(self, blocks, expected):
        found = [b for b in blocks if b["kind"] == "h" and b["level"] == 2]
        names = [b["text"] for b in found]
        if names != expected:
            self.err(found[0]["ln"] if found else 1,
                     "sections (## headings) must be exactly, in order: " + ", ".join(expected)
                     + ". Found: " + (", ".join(names) or "none"))
            return False
        return True

    def check_contract(self, blocks):
        if not blocks or blocks[0]["kind"] != "h" or blocks[0]["level"] != 1:
            self.err(1, "document must start with a '# <Name> API Contract' title")
        # metadata table before first ##
        pre = []
        for b in blocks[1:]:
            if b["kind"] == "h":
                break
            pre.append(b)
        meta = self.first(pre, "table")
        if meta is None:
            self.err(2, "missing metadata table under the title (" + ", ".join(META_KEYS) + ")")
        else:
            keys = [strip_code(r[0]).strip("*") for r in [meta["header"]] + meta["rows"] if r]
            for k in META_KEYS:
                if k not in keys:
                    self.err(meta["ln"], f"metadata table is missing the '{k}' row")

        if not self.check_h2(blocks, CONTRACT_SECTIONS):
            return
        sec = {h["text"]: (h, ch) for h, ch in sections(blocks, 2)}

        # names usable as types
        self.known_names = set()
        for name in ("Enums", "Core Schemas"):
            for h, _ in sections(sec[name][1], 3):
                self.known_names.add(h["text"])
        self.known_names.add("ErrorResponse")  # defined in common.md

        for name, header in TABLE_HEADERS.items():
            h, ch = sec[name]
            self.check_table(self.first(ch, "table"), header, name, h["ln"])

        # Changelog dates
        h, ch = sec["Changelog"]
        t = self.first(ch, "table")
        if t and t["header"] == TABLE_HEADERS["Changelog"]:
            if not t["rows"]:
                self.err(t["ln"], "Changelog needs at least one row")
            for r in t["rows"]:
                if len(r) == 3 and not DATE_RE.match(r[1]):
                    self.err(t["ln"], f"Changelog date '{r[1]}' must be YYYY-MM-DD")

        # Enums
        for h, ch in sections(sec["Enums"][1], 3):
            if not PASCAL_RE.match(h["text"]):
                self.err(h["ln"], f"enum name '{h['text']}' must be PascalCase")
            self.check_table(self.first(ch, "table"), ["Value", "Description"], f"enum {h['text']}", h["ln"])

        # Core schemas
        for h, ch in sections(sec["Core Schemas"][1], 3):
            if not PASCAL_RE.match(h["text"]):
                self.err(h["ln"], f"schema name '{h['text']}' must be PascalCase")
            self.json_and_fields(ch, f"schema {h['text']}", h["ln"])

        endpoints = self.check_endpoints(sec["Endpoints"])
        self.check_summary(sec["Endpoint Summary"], endpoints)

    def check_summary(self, sec, endpoints):
        h, ch = sec
        t = self.first(ch, "table")
        if not t or t["header"] != TABLE_HEADERS["Endpoint Summary"]:
            return
        rows = [(r[0], r[1], strip_code(r[2])) for r in t["rows"] if len(r) == 5]
        want = [(str(n), m, p) for n, m, p in endpoints]
        for row in rows:
            if row not in want:
                self.err(t["ln"], f"Endpoint Summary row '{' '.join(row)}' has no matching '### {row[0]}. {row[1]} {row[2]}' section")
        for e in want:
            if e not in rows:
                self.err(t["ln"], f"endpoint '{e[0]}. {e[1]} {e[2]}' is missing from the Endpoint Summary table")

    def check_endpoints(self, sec):
        found = []
        for expected_n, (h, ch) in enumerate(sections(sec[1], 3), start=1):
            m = ENDPOINT_RE.match(h["text"])
            if not m:
                self.err(h["ln"], f"endpoint heading '{h['text']}' must look like '### 1. GET /api/v1/...', "
                                  "'### 2. KAFKA roomscanner.pp.search.request' or '### 3. SOCKET event-name'")
                continue
            n, method, target = int(m.group(1)), m.group(2), m.group(3)
            found.append((n, method, target))
            where = f"endpoint {n}"
            if n != expected_n:
                self.err(h["ln"], f"{where}: endpoints must be numbered 1, 2, 3... in order (expected {expected_n})")
            if method in HTTP_METHODS and not REST_PATH_RE.match(target):
                self.err(h["ln"], f"{where}: REST path must start with /api/v1/ and use {{param}} for path parameters")
            if method == "KAFKA" and not KAFKA_TOPIC_RE.match(target):
                self.err(h["ln"], f"{where}: Kafka topic must look like roomscanner.<pp|cp|pms>.<feature>.<request|reply|event>")
            if method == "SOCKET" and not SOCKET_EVENT_RE.match(target):
                self.err(h["ln"], f"{where}: socket event name must be lowercase, e.g. event-suggestions")

            pre = []
            for b in ch:
                if b["kind"] == "h":
                    break
                pre.append(b)
            if not any(b["kind"] == "text" for b in pre):
                self.err(h["ln"], f"{where}: add a short description under the heading")
            meta = self.first(pre, "table")
            if self.check_table(meta, ENDPOINT_META_HEADER, where, h["ln"]):
                if len(meta["rows"]) != 1:
                    self.err(meta["ln"], f"{where}: metadata table needs exactly one row")
                else:
                    proto, prov, cons, reqs = (meta["rows"][0] + ["", "", "", ""])[:4]
                    want = "REST" if method in HTTP_METHODS else method.capitalize()
                    if proto != want:
                        self.err(meta["ln"], f"{where}: Protocol must be '{want}' for a {method} endpoint")
                    for label, val in (("Provided by", prov), ("Consumed by", cons)):
                        if val not in ("PP", "CP", "PMS", "PP, CP", "Partner squad"):
                            self.err(meta["ln"], f"{where}: {label} must be PP, CP, PMS, 'PP, CP' or 'Partner squad'")
                    if not re.search(r"[A-Z]+-[A-Z]+-[SMU]\d\d|[A-Z]+-[SMU]\d\d", reqs):
                        self.err(meta["ln"], f"{where}: list at least one requirement ID, e.g. PP-SEARCH-S01")

            subs = {s["text"]: (s, c) for s, c in sections(ch, 4)}
            for name, (s, _) in subs.items():
                if name not in ALLOWED_H4 and not RESPONSE_H4_RE.match(name):
                    self.err(s["ln"], f"{where}: unknown subsection '#### {name}'. Allowed: "
                                      + ", ".join(sorted(ALLOWED_H4)) + ", '<code> <Reason> Response'")

            if method in HTTP_METHODS:
                self.check_rest(where, h, method, target, subs)
            elif method == "KAFKA":
                self.check_kafka(where, h, subs)
            else:
                if "Event Message" not in subs:
                    self.err(h["ln"], f"{where}: socket endpoints need '#### Event Message'")
                else:
                    s, c = subs["Event Message"]
                    self.json_and_fields(c, f"{where} event message", s["ln"])
        return found

    def check_rest(self, where, h, method, path, subs):
        params = re.findall(r"{(\w+)}", path)
        if params:
            if "Path Parameters" not in subs:
                self.err(h["ln"], f"{where}: path has {{{params[0]}}}; add '#### Path Parameters'")
            else:
                s, c = subs["Path Parameters"]
                t = self.first(c, "table")
                if self.check_table(t, PARAM_HEADER, f"{where} path parameters", s["ln"]):
                    listed = {strip_code(r[0]) for r in t["rows"] if r}
                    for p in params:
                        if p not in listed:
                            self.err(t["ln"], f"{where}: path parameter '{p}' is not documented")
        if "Query Parameters" in subs:
            s, c = subs["Query Parameters"]
            self.check_table(self.first(c, "table"), PARAM_HEADER, f"{where} query parameters", s["ln"])

        if method in ("POST", "PUT", "PATCH"):
            if "Request Body" not in subs:
                self.err(h["ln"], f"{where}: {method} endpoints need '#### Request Body' with a JSON example and field table")
            else:
                s, c = subs["Request Body"]
                self.json_and_fields(c, f"{where} request body", s["ln"])
        elif "Request Body" in subs:
            self.err(subs["Request Body"][0]["ln"], f"{where}: {method} endpoints must not have a request body; use Query Parameters")

        if "Response Codes" not in subs:
            self.err(h["ln"], f"{where}: add '#### Response Codes'")
            return
        s, c = subs["Response Codes"]
        t = self.first(c, "table")
        if not self.check_table(t, ["Code", "Meaning"], f"{where} response codes", s["ln"]):
            return
        codes = [r[0] for r in t["rows"] if r]
        for code in codes:
            if not re.fullmatch(r"[1-5]\d\d", code):
                self.err(t["ln"], f"{where}: response code '{code}' is not a 3-digit HTTP status")
        if not any(c.startswith("2") for c in codes):
            self.err(t["ln"], f"{where}: list the success (2xx) response code")
        responses = {RESPONSE_H4_RE.match(n).group(1): v for n, v in subs.items() if RESPONSE_H4_RE.match(n)}
        for code in codes:
            if code.startswith("2") and code != "204" and code not in responses:
                self.err(t["ln"], f"{where}: add '#### {code} <Reason> Response' with a JSON example and field table")
        for code, (rs, rc) in responses.items():
            if code not in codes:
                self.err(rs["ln"], f"{where}: '{rs['text']}' is not listed in Response Codes")
            if code.startswith("2"):
                self.json_and_fields(rc, f"{where} {code} response", rs["ln"])

    def check_kafka(self, where, h, subs):
        if "Event Message" in subs:
            s, c = subs["Event Message"]
            self.json_and_fields(c, f"{where} event message", s["ln"])
            self.check_topic_line(where, s, c, "event")
        else:
            for name, kind in (("Request Message", "request"), ("Reply Message", "reply")):
                if name not in subs:
                    self.err(h["ln"], f"{where}: Kafka request/reply endpoints need '#### Request Message' and '#### Reply Message' "
                                      "(or '#### Event Message' for one-way events)")
                    continue
                s, c = subs[name]
                self.json_and_fields(c, f"{where} {name.lower()}", s["ln"])
                self.check_topic_line(where, s, c, kind)
        if "Failure and Retry" not in subs:
            self.err(h["ln"], f"{where}: Kafka endpoints need '#### Failure and Retry' (timeout, resend, duplicate handling)")

    def check_topic_line(self, where, s, c, kind):
        for b in c:
            if b["kind"] == "text":
                m = re.match(r"^Topic: `([^`]+)`", b["text"])
                if m:
                    if not KAFKA_TOPIC_RE.match(m.group(1)) or not m.group(1).endswith("." + kind):
                        self.err(b["ln"], f"{where}: topic '{m.group(1)}' must look like roomscanner.<pp|cp|pms>.<feature>.{kind}")
                    return
        self.err(s["ln"], f"{where}: add a 'Topic: `roomscanner.<pp|cp|pms>.<feature>.{kind}`' line under '{s['text']}'")


def main(argv):
    if argv:
        files = [pathlib.Path(a).resolve() for a in argv if a.endswith(".md")]
    else:
        files = sorted(p for p in CONTRACT_DIR.glob("*.md") if p.name != "README.md")
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    total = 0
    for f in files:
        errs = Checker(f).run()
        rel = os.path.relpath(f, ROOT)
        for ln, msg in errs:
            total += 1
            print(f"::error file={rel},line={ln}::{msg}" if in_ci else f"{rel}:{ln}: {msg}")
        if not errs:
            print(f"ok  {rel}")
    if total:
        print(f"\n{total} problem(s). See api-contract/_TEMPLATE.md for the required format.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
