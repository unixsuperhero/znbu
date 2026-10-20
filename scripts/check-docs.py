#!/usr/bin/env python3
"""Check the source map and canonical Markdown without making network requests."""

import argparse
import hashlib
import html
import json
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


OPEN_PLANS = {"open", "partial", "verification-pending"}
MARKDOWN = {".md", ".markdown"}


def without_fences(text):
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            lines.append("\n")
        elif match:
            fence = match[1]
            lines.append("\n")
        else:
            lines.append(line)
    return re.sub(r"<!--[\s\S]*?-->", "", "".join(lines))


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.anchors = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is not None:
                if name == "id" or (tag == "a" and name == "name"):
                    self.anchors.add(value)
                if name == "href" or (tag == "img" and name == "src"):
                    self.links.append(value)


def inline_target(text, start):
    text = text[start:].lstrip()
    if text.startswith("<"):
        end = text.find(">")
        return text[1:end] if end >= 0 else None
    target = []
    depth = 0
    escaped = False
    for char in text:
        if escaped:
            target.extend(("\\", char))
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == ")" and not depth:
            return "".join(target)
        if char.isspace() and not depth:
            return "".join(target)
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        target.append(char)
    return None


def links(text):
    text = re.sub(r"(`+)([\s\S]*?)\1", "", without_fences(text))
    definitions = {}
    definition = re.compile(r"(?m)^ {0,3}\[([^\]\n]+)\]:[ \t]*(?:<([^>\n]*)>|(\S+)).*$")
    for match in definition.finditer(text):
        definitions[" ".join(match[1].split()).casefold()] = match[2] if match[2] is not None else match[3]
    text = definition.sub("", text)
    found = list(Elements(text).links)
    for match in re.finditer(r"!?\[((?:[^\[\]\n]|\[[^\]\n]*\])*)\](?:[ \t]*\[([^\]\n]*)\])?", text):
        if match[2] is None and text[match.end():].startswith("("):
            target = inline_target(text, match.end() + 1)
            if target is not None:
                found.append(target)
        else:
            label = match[2] or match[1]
            target = definitions.get(" ".join(label.split()).casefold())
            if target is not None:
                found.append(target)
    return found


def anchors(text):
    text = without_fences(text)
    found = Elements(text).anchors
    generated = set()
    previous = ""
    for line in text.splitlines():
        heading = re.match(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", line)
        title = heading[1] if heading else None
        if title is None and previous.strip() and re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", line):
            title = previous.strip()
        if title is not None:
            title = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", title)
            title = re.sub(r"!?\[([^\]]+)\](?:\[[^\]]*\])?", r"\1", title)
            title = re.sub(r"(_{1,3})(.*?)\1", r"\2", title)
            title = html.unescape(re.sub(r"<[^>]+>", "", title))
            base = re.sub(r"[^\w\-\s]", "", title.lower()).strip()
            base = re.sub(r"\s", "-", base)
            slug = base
            suffix = 0
            while slug in generated:
                suffix += 1
                slug = f"{base}-{suffix}"
            generated.add(slug)
            found.add(slug)
        previous = "" if heading else line
    return found


def local_reference(value):
    value = html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]^_`{|}~ ])", r"\1", value))
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    return unquote(parsed.path), unquote(parsed.fragment)


def repo_path(root, value):
    if not value or value.startswith(("/", "~")):
        raise ValueError(f"expected a repository-relative path: {value!r}")
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"path leaves repository: {value}")
    return path


def load_manifest(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("source-map.json must have version 1")
    fields = {
        "sources": ("id", "original", "preserved", "sha256", "role", "destinations"),
        "plans": ("path", "status"),
        "items": ("id", "status", "path", "evidence"),
    }
    for table, required in fields.items():
        if not isinstance(data.get(table), list):
            raise ValueError(f"{table} must be an array")
        for number, row in enumerate(data[table], 1):
            if not isinstance(row, dict):
                raise ValueError(f"{table}[{number}] must be an object")
            for field in required:
                value = row.get(field)
                if field in {"destinations", "evidence"}:
                    valid = isinstance(value, list) and all(isinstance(v, str) and v for v in value)
                else:
                    valid = isinstance(value, str) and bool(value)
                if not valid:
                    raise ValueError(f"invalid {table}[{number}].{field}")
            for field in {"todo", "outline"} & row.keys():
                if not isinstance(row[field], str) or not row[field]:
                    raise ValueError(f"invalid {table}[{number}].{field}")
    return data


def check(root, data):
    errors, historical, pending = [], set(), []
    text_cache, anchor_cache = {}, {}

    def text(path):
        if path not in text_cache:
            text_cache[path] = path.read_text(encoding="utf-8")
        return text_cache[path]

    def check_target(path, fragment):
        if not path.exists():
            return f"missing path {path.relative_to(root)}"
        if fragment:
            if not path.is_file() or path.suffix.lower() not in MARKDOWN | {".html", ".htm", ".txt"}:
                return f"cannot resolve anchor #{fragment} in {path.relative_to(root)}"
            if path not in anchor_cache:
                anchor_cache[path] = anchors(text(path))
            if fragment not in anchor_cache[path]:
                return f"missing anchor {path.relative_to(root)}#{fragment}"
        return None

    def manifest_target(value, label):
        reference = local_reference(value)
        if reference is None:
            errors.append(f"{label}: expected a local repository path, got {value}")
            return None
        try:
            path = repo_path(root, reference[0])
        except ValueError as error:
            errors.append(f"{label}: {error}")
            return None
        problem = check_target(path, reference[1])
        if problem:
            errors.append(f"{label}: {problem}")
        return path

    source_ids, originals, preserved = set(), {}, set()
    for source in data["sources"]:
        label = f"source {source['id']}"
        if source["id"] in source_ids:
            errors.append(f"duplicate source ID {source['id']}")
        source_ids.add(source["id"])
        if not source["original"].startswith("~/"):
            errors.append(f"{label}: original must use a ~/ label")
        if source["original"] in originals:
            errors.append(f"duplicate original {source['original']}")
        originals[source["original"]] = source
        try:
            path = repo_path(root, source["preserved"])
        except ValueError as error:
            errors.append(f"{label}: {error}")
            continue
        preserved.add(path)
        if not path.is_file():
            errors.append(f"{label}: missing preserved file {source['preserved']}")
        elif not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            errors.append(f"{label}: invalid SHA-256")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            errors.append(f"{label}: SHA-256 mismatch for {source['preserved']}")
        if source.get("previousSnapshot"):
            previous = repo_path(root, source["previousSnapshot"])
            preserved.add(previous)
            if not previous.is_file():
                errors.append(f"{label}: missing previous snapshot")
            elif hashlib.sha256(previous.read_bytes()).hexdigest() != source.get("previousSha256"):
                errors.append(f"{label}: previous snapshot SHA-256 mismatch")
        if not source["destinations"]:
            pending.append(source["id"])
            errors.append(f"{label}: missing canonical destination")
        for destination in source["destinations"]:
            manifest_target(destination, label)

    canonical = sorted({p.resolve() for p in (root / "docs").rglob("*")
                        if p.is_file() and p.suffix.lower() in MARKDOWN
                        and not ({"sources", "prompts", "generated", "data", ".git"} & set(p.relative_to(root / "docs").parts))
                        and p.resolve() not in preserved})
    if (root / "README.md").is_file():
        canonical.append(root / "README.md")
    if (root / "docs/sources/README.md").is_file():
        canonical.append(root / "docs/sources/README.md")
    inbound = {}
    for path in canonical:
        for value in links(text(path)):
            reference = local_reference(value)
            if reference is None:
                continue
            target_name, fragment = reference
            try:
                if target_name.startswith("/"):
                    target = repo_path(root, target_name.lstrip("/"))
                elif target_name:
                    relative = (path.parent / target_name).relative_to(root)
                    target = repo_path(root, str(relative))
                else:
                    target = path
            except ValueError as error:
                errors.append(f"{path.relative_to(root)}: {value}: {error}")
                continue
            inbound.setdefault(target, set()).add(path)
            problem = check_target(target, fragment)
            if problem:
                errors.append(f"{path.relative_to(root)}: {value}: {problem}")

    for source in data["sources"]:
        path = root / source["preserved"]
        if not path.is_file() or path.suffix.lower() not in MARKDOWN | {".txt"}:
            continue
        for value in links(text(path)):
            reference = local_reference(value)
            if reference is None:
                continue
            target_name, fragment = reference
            if target_name.startswith("~/"):
                original = posixpath.normpath(target_name)
            elif not target_name:
                original = source["original"]
            elif target_name.startswith("/"):
                original = target_name
            else:
                original = posixpath.normpath(posixpath.join(posixpath.dirname(source["original"]), target_name))
            target_source = originals.get(original)
            if target_source is None:
                if not fragment and target_name.endswith("/") and any(name.startswith(original + "/") for name in originals):
                    continue
                historical.add(f"{source['original']}: {value}: original target not preserved ({original})")
            else:
                target = root / target_source["preserved"]
                problem = check_target(target, fragment)
                if problem:
                    historical.add(f"{source['original']}: {value}: {problem}")

    def in_section(path, section):
        return path is not None and path.is_relative_to(root / "docs" / section)

    for plan in data["plans"]:
        label = f"plan {plan['path']}"
        path = manifest_target(plan["path"], label)
        if path is not None and not path.is_file():
            errors.append(f"{label}: plan must point to a file")
        todo = manifest_target(plan["todo"], label) if plan.get("todo") else None
        outline = manifest_target(plan["outline"], label) if plan.get("outline") else None
        if todo is not None and not in_section(todo, "todo") and todo != root / "docs/todo.md":
            errors.append(f"{label}: todo must point to a todo document")
        if outline is not None and not in_section(outline, "outline") and outline != root / "docs/outline.md":
            errors.append(f"{label}: outline must point to an outline document")
        if plan["status"] in OPEN_PLANS:
            linked = {p for p in inbound.get(path, set()) if in_section(p, "todo") or p == root / "docs/todo.md"}
            if not linked or (todo is not None and todo not in linked):
                errors.append(f"{label}: unfinished plan needs a Markdown link FROM its todo document")

    item_ids = set()
    for item in data["items"]:
        label = f"item {item['id']}"
        if item["id"] in item_ids:
            errors.append(f"duplicate item ID {item['id']}")
        item_ids.add(item["id"])
        path = manifest_target(item["path"], label)
        if path is not None and path not in canonical:
            errors.append(f"{label}: path must point to a canonical Markdown document")
        closed = {"implemented", "superseded", "historical", "source-reported-completed"}
        section = "outline" if item["status"] in closed else "todo"
        if not in_section(path, section):
            errors.append(f"{label}: status {item['status']} must live under docs/{section}/")

    original_items = set()
    for source in data["sources"]:
        if source["role"] == "historical-backlog":
            path = repo_path(root, source["preserved"])
            if path.is_file() and path.suffix.lower() in MARKDOWN:
                original_items.update(re.findall(r"^### (B-\d+)\b", text(path), re.MULTILINE))
    for item_id in sorted(original_items - item_ids):
        errors.append(f"original backlog item {item_id} has no canonical disposition")

    for message in errors:
        print(f"ERROR {message}")
    for message in sorted(historical):
        print(f"HISTORICAL {message}")
    if pending:
        print(f"PENDING {len(pending)} source mappings have no canonical destinations: {', '.join(pending)}")
    print(f"Checked {len(data['sources'])} preserved sources, {len(canonical)} canonical Markdown files, {len(data['plans'])} plans, {len(data['items'])} items.")
    print(f"{len(errors)} errors; {len(historical)} unresolved historical references (non-failing); {len(pending)} pending source mappings.")
    print("External URLs were skipped. No network requests were made.")
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (default: script's parent repository)")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    try:
        return check(root, load_manifest(root / "docs/source-map.json"))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
