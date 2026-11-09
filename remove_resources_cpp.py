#!/usr/bin/env python3
"""Remove resource sections from cpp lesson fixtures 23-33.

Removes:
1. Content block heading "Полезные ресурсы:" / "Ресурсы" + following list block
2. Top-level "resources" array field (if non-empty)
"""

import json
import re
from pathlib import Path

FIXTURES_DIR = Path(
    r"C:\Users\maksy\OneDrive\Рабочий стол\логи клауде\проект\fixtures\lessons\cpp"
)

RESOURCE_HEADING_PATTERNS = [
    "полезные ресурсы",
    "ресурсы",
]


def remove_resource_content_blocks(blocks):
    """Remove heading+list resource blocks from content_blocks."""
    new_blocks = []
    i = 0
    while i < len(blocks):
        block = blocks[i]
        # Check if this is a resource heading block
        if (
            block.get("type") == "heading"
            and isinstance(block.get("content"), str)
            and any(p in block["content"].lower() for p in RESOURCE_HEADING_PATTERNS)
        ):
            # Skip this heading and the following list block if it exists
            i += 1
            if i < len(blocks) and blocks[i].get("type") == "list":
                i += 1
            continue
        new_blocks.append(block)
        i += 1
    return new_blocks


def process_file(path):
    """Process a single fixture file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False

    # 1. Remove resource content blocks
    original_blocks = data.get("content_blocks", [])
    new_blocks = remove_resource_content_blocks(original_blocks)
    if len(new_blocks) != len(original_blocks):
        data["content_blocks"] = new_blocks
        changed = True

    # 2. Remove top-level "resources" field if non-empty
    resources = data.get("resources")
    if resources and isinstance(resources, list) and len(resources) > 0:
        del data["resources"]
        changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  MODIFIED: {path.name}")
    else:
        print(f"  unchanged: {path.name}")

    return changed


def main():
    total_changed = 0
    for lesson_num in range(23, 34):
        path = FIXTURES_DIR / f"{lesson_num:02d}.json"
        if not path.exists():
            print(f"  MISSING: {path.name}")
            continue
        if process_file(path):
            total_changed += 1

    print(f"\nTotal files modified: {total_changed}")


if __name__ == "__main__":
    main()
