import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_FILE = Path(__file__).parent / "chunks.json"
MAX_CHARS = 800
OVERLAP = 120


def split_front_matter(text):
    meta = {}
    if text.startswith("---"):
        _, header, body = text.split("---", 2)
        for line in header.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        text = body
    return meta, text.strip()


def split_sections(text):
    """Yield (heading, body) pairs, split on markdown headings."""
    heading = "Introduction"
    lines = []
    for line in text.splitlines():
        if re.match(r"^#{1,3}\s", line):
            if "".join(lines).strip():
                yield heading, "\n".join(lines).strip()
            heading = line.lstrip("#").strip()
            lines = []
        else:
            lines.append(line)
    if "".join(lines).strip():
        yield heading, "\n".join(lines).strip()


def pack(body):
    """Pack paragraphs into pieces of at most MAX_CHARS, with overlap."""
    if len(body) <= MAX_CHARS:
        return [body]
    pieces, current = [], ""
    for para in re.split(r"\n\s*\n", body):
        if current and len(current) + len(para) + 2 > MAX_CHARS:
            pieces.append(current)
            tail = current[-OVERLAP:]
            tail = tail[tail.find(" ") + 1:]  # start on a word boundary
            current = tail + "\n\n" + para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        pieces.append(current)
    return pieces


def chunk_file(path):
    meta, text = split_front_matter(path.read_text(encoding="utf-8-sig"))
    chunks = []
    for heading, body in split_sections(text):
        for piece in pack(body):
            chunks.append(
                {
                    "id": f"{path.stem}#{len(chunks):02d}",
                    "source": path.name,
                    "section": heading,
                    "access": meta.get("access", "internal"),
                    "updated": meta.get("updated", ""),
                    "text": f"{heading}\n{piece}",
                }
            )
    return chunks


def main():
    files = sorted(DATA_DIR.glob("*.md"))
    all_chunks = []
    for path in files:
        all_chunks.extend(chunk_file(path))
    OUT_FILE.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    print(f"{len(all_chunks)} chunks from {len(files)} files")
    for c in all_chunks:
        print(c["id"], "|", c["section"], "|", c["access"], "|", len(c["text"]), "chars")


if __name__ == "__main__":
    main()