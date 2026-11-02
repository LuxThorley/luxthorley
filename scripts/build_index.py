#!/usr/bin/env python3
"""Rebuild the catalogue section of README.md.

Usage:  python3 scripts/build_index.py          # rewrite README.md
        python3 scripts/build_index.py --check  # exit 1 if README.md is out of date

Standard library only. Walks the whole repository (skipping .git), reads the
optional metadata in catalogue.json, and regenerates everything between
<!-- CATALOGUE:START --> and <!-- CATALOGUE:END --> in README.md. Text outside
the markers is never touched. Files with no catalogue entry are still indexed:
the title comes from the PDF's own metadata (tiny built-in parser) or the
filename, and the category from the folder (folder_categories in catalogue.json,
otherwise the top-level folder name).
"""
import json
import os
import re
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
CATALOGUE = os.path.join(ROOT, "catalogue.json")
START, END = "<!-- CATALOGUE:START -->", "<!-- CATALOGUE:END -->"
OWNER_REPO = os.environ.get("GITHUB_REPOSITORY", "LuxThorley/luxthorley")
BRANCH = os.environ.get("CATALOGUE_BRANCH", "main")
BLOB = f"https://github.com/{OWNER_REPO}/blob/{BRANCH}/"
RAW = f"https://github.com/{OWNER_REPO}/raw/{BRANCH}/"

TYPES = {
    ".pdf": "PDF", ".xlsx": "Excel", ".xls": "Excel", ".csv": "CSV", ".json": "JSON",
    ".md": "Markdown", ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".js": "JavaScript",
    ".py": "Python", ".yml": "YAML", ".yaml": "YAML", ".png": "Image", ".jpg": "Image",
    ".jpeg": "Image", ".gif": "Image", ".webp": "Image", ".svg": "Image", ".docx": "Word",
    ".pptx": "PowerPoint", ".txt": "Text", ".zip": "Archive", ".mp3": "Audio", ".mp4": "Video",
}


def load_catalogue():
    if os.path.exists(CATALOGUE):
        with open(CATALOGUE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def walk():
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in (".git", "__pycache__", "node_modules"))
        for name in files:
            rel = os.path.relpath(os.path.join(d, name), ROOT).replace(os.sep, "/")
            out.append(rel)
    return sorted(out)


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0


PDFDOC = {0x80: "\u2022", 0x81: "\u2020", 0x82: "\u2021", 0x83: "\u2026", 0x84: "\u2014",
          0x85: "\u2013", 0x86: "\u0192", 0x87: "\u2044", 0x88: "\u2039", 0x89: "\u203a",
          0x8a: "\u2212", 0x8b: "\u2030", 0x8c: "\u201e", 0x8d: "\u201c", 0x8e: "\u201d",
          0x8f: "\u2018", 0x90: "\u2019", 0x91: "\u201a", 0x92: "\u2122"}


def _decode_pdf_string(raw):
    if raw.startswith("<"):
        try:
            b = bytes.fromhex(re.sub(r"[^0-9A-Fa-f]", "", raw[1:-1]))
        except ValueError:
            return ""
    else:
        s = raw[1:-1]
        s = re.sub(r"\\([nrtbf()\\])", lambda m: {"n": "\n", "r": "", "t": " ", "b": "", "f": ""}.get(m.group(1), m.group(1)), s)
        s = re.sub(r"\\([0-7]{1,3})", lambda m: chr(int(m.group(1), 8)), s)
        b = s.encode("latin-1", "replace")
    if b.startswith(b"\xfe\xff"):
        return b[2:].decode("utf-16-be", "replace").strip("\x00")
    if b.startswith(b"\xff\xfe"):
        return b[2:].decode("utf-16-le", "replace").strip("\x00")
    try:
        return b.decode("utf-8").strip("\x00")
    except UnicodeDecodeError:
        # PDFDocEncoding: latin-1 plus typographic characters in 0x80-0x9F
        return "".join(PDFDOC.get(c, chr(c)) for c in b).strip("\x00")


def pdf_title(path):
    """Best-effort /Title and page count from a PDF, stdlib only."""
    title, pages = "", None
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            head = f.read(2_000_000)
            f.seek(max(0, size - 2_000_000))
            tail = f.read()
        data = head + tail
        text = data.decode("latin-1")
        m = re.search(r"/Title\s*(\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>)", text)
        if m:
            title = _decode_pdf_string(m.group(1)).strip()
        counts = [int(x) for x in re.findall(r"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", text)]
        counts += [int(x) for x in re.findall(r"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", text)]
        if counts:
            pages = max(counts)
    except OSError:
        pass
    junk = ("untitled", "microsoft word", "convert jpg", ".jpg", "anonymous", "pdfdrive")
    if title and (len(title) < 3 or any(j in title.lower() for j in junk)):
        title = ""
    return title, pages


def humanise(name):
    stem = os.path.splitext(name)[0]
    stem = re.sub(r"[_\-]+", " ", stem).strip()
    return stem[:1].upper() + stem[1:] if stem else name


def category_for(rel, meta, cat):
    if meta.get("category"):
        return meta["category"]
    best = ""
    for prefix in cat.get("folder_categories", {}):
        if (rel == prefix or rel.startswith(prefix.rstrip("/") + "/")) and len(prefix) > len(best):
            best = prefix
    if best:
        return cat["folder_categories"][best]
    top = rel.split("/")[0] if "/" in rel else ""
    return "folder:" + top if top else "uncatalogued"


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def anchor(title):
    a = re.sub(r"[^\w\- ]", "", title.lower(), flags=re.UNICODE).strip().replace(" ", "-")
    return a


def build():
    cat = load_catalogue()
    files_meta = cat.get("files", {})
    exclude = set(cat.get("exclude", ["README.md"]))
    pages_cfg = cat.get("pages", {})
    cats = {c["id"]: c for c in cat.get("categories", [])}
    order = [c["id"] for c in cat.get("categories", [])]

    entries = []
    for rel in walk():
        if rel in exclude:
            continue
        meta = dict(files_meta.get(rel, {}))
        full = os.path.join(ROOT, rel)
        ext = os.path.splitext(rel)[1].lower()
        title, pages = meta.get("title", ""), meta.get("pages")
        if ext == ".pdf" and (not title or not pages):
            t, p = pdf_title(full)
            title = title or t
            pages = pages or p
        title = title or humanise(os.path.basename(rel))
        c = category_for(rel, meta, cat)
        if c not in cats:
            label = "Uncatalogued (root)" if c == "uncatalogued" else "Folder: " + c.split(":", 1)[1]
            cats[c] = {"id": c, "title": label, "description": "Indexed automatically; add details in catalogue.json."}
        if c not in order:
            order.append(c)
        pages_url = ""
        pf = pages_cfg.get("folder")
        if pf and rel.startswith(pf.rstrip("/") + "/"):
            sub = rel[len(pf.rstrip("/")) + 1:]
            if sub == "index.html":
                sub = ""
            pages_url = pages_cfg.get("url", "").rstrip("/") + "/" + quote(sub)
        entries.append({
            "path": rel, "title": title, "author": meta.get("author", ""),
            "date": str(meta.get("date", "")), "type": TYPES.get(ext, ext.lstrip(".").upper() or "File"),
            "size": os.path.getsize(full), "pages": pages, "category": c,
            "description": meta.get("description", ""), "licence": meta.get("licence", ""),
            "pages_url": pages_url, "catalogued": rel in files_meta,
        })

    by_cat = {c: [] for c in order}
    for e in entries:
        by_cat[e["category"]].append(e)
    for c in by_cat:
        by_cat[c].sort(key=lambda e: (e["date"] or "9999", e["title"].lower(), e["path"]))

    total_size = sum(e["size"] for e in entries)
    n_pdf = sum(1 for e in entries if e["type"] == "PDF")
    L = [START, "", "<!-- This section is generated by scripts/build_index.py. Edit catalogue.json, not this block. -->", ""]
    L.append(f"**{len(entries)} files** · **{n_pdf} PDFs** · {human_size(total_size)} in total · "
             f"{sum(1 for c in order if by_cat[c])} sections")
    L += ["", "### Contents", ""]
    for c in order:
        if by_cat[c]:
            t = cats[c]["title"]
            L.append(f"- [{t}](#{anchor(t)}) ({len(by_cat[c])})")
    for c in order:
        items = by_cat[c]
        if not items:
            continue
        t = cats[c]["title"]
        L += ["", f"### {t}", ""]
        if cats[c].get("description"):
            L += [f"_{esc(cats[c]['description'])}_", ""]
        L.append("| Title | Author | Date | Type | Size | Links |")
        L.append("|---|---|---|---|---|---|")
        for e in items:
            q = quote(e["path"])
            links = [f"[view]({q})", f"[download]({RAW}{q})"]
            if e["pages_url"]:
                links.append(f"[live]({e['pages_url']})")
            title = f"**{esc(e['title'])}**"
            extra = [x for x in (e["description"], e["licence"] and "Licence: " + e["licence"]) if x]
            if extra:
                title += "<br><sub>" + esc(" · ".join(extra)) + "</sub>"
            title += f"<br><sub>`{esc(e['path'])}`</sub>"
            typ = e["type"] + (f", {e['pages']} pp" if e["pages"] else "")
            L.append(f"| {title} | {esc(e['author'])} | {esc(e['date'])} | {typ} | {human_size(e['size'])} | {' · '.join(links)} |")
    L += ["", END]
    return "\n".join(L)


def main():
    block = build()
    with open(README, encoding="utf-8") as f:
        old = f.read()
    if START in old and END in old:
        pre = old.split(START, 1)[0]
        post = old.split(END, 1)[1]
        new = pre + block + post
    else:
        new = old.rstrip("\n") + "\n\n## Catalogue\n\n" + block + "\n"
    if "--check" in sys.argv:
        if new != old:
            print("README.md catalogue is out of date; run python3 scripts/build_index.py")
            sys.exit(1)
        print("README.md catalogue is up to date")
        return
    if new != old:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
