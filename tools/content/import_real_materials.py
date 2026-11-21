#!/usr/bin/env python3
"""
Import real educational materials from Kernify-lesson folder into JSON fixtures.
Parses .txt and .md files and populates lesson JSON with real content.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Mapping: language folder -> language slug
LANG_FOLDER_MAP = {
    "обучение JavaScript": "javascript",
    "обучение питон": "python",
    "обучение C++": "cpp",
    "обучение C#": "csharp",
    "обучение CSS": "css",
    "обучение Rust": "rust",
}

# Lesson order mapping from filename to lesson_order
def extract_lesson_order(filename: str) -> int:
    """Extract lesson order from filename like '01_Введение.txt' -> 1"""
    match = re.match(r'^(\d+)[_\s]', filename)
    if match:
        return int(match.group(1))
    return 999

def parse_lesson_file(filepath: Path) -> Dict:
    """Parse a lesson .txt/.md file into structured content blocks."""
    content = filepath.read_text(encoding='utf-8')
    
    # Split by markdown headers (# ## ###)
    sections = re.split(r'\n(?=#{1,3}\s)', content)
    
    blocks = []
    current_title = None
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Detect header level
        header_match = re.match(r'^(#{1,3})\s+(.+)', section)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            body = section[header_match.end():].strip()
            
            blocks.append({
                "type": "heading",
                "level": level,
                "content": title
            })
            
            if body:
                # Process body content
                blocks.extend(parse_body(body))
        else:
            # Content without header
            blocks.extend(parse_body(section))
    
    return {"blocks": blocks}

def parse_body(text: str) -> List[Dict]:
    """Parse body text into content blocks (text, code, list, table)."""
    blocks = []
    
    # Split by code fences first
    parts = re.split(r'(```[\w]*\n.*?\n```)', text, flags=re.DOTALL)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Code block
        if part.startswith('```'):
            lang_match = re.match(r'```(\w*)\n(.*?)\n```', part, re.DOTALL)
            if lang_match:
                lang = lang_match.group(1) or 'text'
                code = lang_match.group(2).strip()
                blocks.append({
                    "type": "code",
                    "language": lang,
                    "content": code
                })
            continue
        
        # Table
        if '|' in part and re.search(r'\|.*\|', part):
            lines = part.split('\n')
            if len(lines) >= 3 and '|---' in lines[1]:
                blocks.append({
                    "type": "table",
                    "content": part
                })
                continue
        
        # Lists
        list_items = re.findall(r'^[\s]*[-*+]\s+(.+)$', part, re.MULTILINE)
        if list_items and len(list_items) > 1:
            # Check if ordered
            ordered = bool(re.match(r'^\s*\d+\.', part.strip()))
            blocks.append({
                "type": "list",
                "items": list_items,
                "ordered": ordered
            })
            # Also include any text before/after list
            remaining = re.sub(r'^[\s]*[-*+]\s+.+$', '', part, flags=re.MULTILINE).strip()
            if remaining:
                blocks.append({"type": "text", "content": remaining})
            continue
        
        # Regular text
        if part:
            blocks.append({"type": "text", "content": part})
    
    return blocks

def process_language_folder(lang_folder: Path, lang_slug: str):
    """Process all lesson files in a language folder."""
    lesson_files = sorted(lang_folder.glob('*.txt')) + sorted(lang_folder.glob('*.md'))
    
    results = []
    for lf in lesson_files:
        order = extract_lesson_order(lf.name)
        if order == 999:
            continue
            
        parsed = parse_lesson_file(lf)
        parsed['order'] = order
        parsed['filename'] = lf.name
        # Extract clean title from filename
        title = lf.stem
        # Remove leading order number (e.g., "01_Введение" -> "Введение")
        title = re.sub(r'^\d+[_\s]*', '', title)
        # Replace underscores with spaces
        title = title.replace('_', ' ')
        parsed['title'] = title.strip()
        results.append(parsed)
    
    return results

def update_fixture(lang_slug: str, lesson_order: int, parsed_content: Dict):
    """Update a single lesson JSON fixture with real content."""
    # Fixtures use zero-padded numbers: 01.json, 02.json, etc.
    fixture_path = Path(f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/{lang_slug}/{lesson_order:02d}.json")
    
    if not fixture_path.exists():
        print(f"  ⚠️ Fixture not found: {fixture_path}")
        return False
    
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixture = json.load(f)
    
    # Update content_blocks with parsed content
    if 'blocks' in parsed_content:
        fixture['content_blocks'] = parsed_content['blocks']
    
    # Update title if we have a better one
    if parsed_content.get('title'):
        fixture['title'] = f"Урок {fixture.get('lesson_order', 0):02d}: {parsed_content['title']}"
    
    with open(fixture_path, 'w', encoding='utf-8') as f:
        json.dump(fixture, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    base_path = Path("/Users/xiip.shk/работа/Kernify-lesson")
    
    total_updated = 0
    
    for folder_name, lang_slug in LANG_FOLDER_MAP.items():
        lang_folder = base_path / folder_name
        if not lang_folder.exists():
            print(f"⚠️ Folder not found: {lang_folder}")
            continue
        
        print(f"\n📚 Processing {folder_name} ({lang_slug})...")
        lessons = process_language_folder(lang_folder, lang_slug)
        
        for lesson in lessons:
            order = lesson['order']
            success = update_fixture(lang_slug, order, lesson)
            if success:
                total_updated += 1
                print(f"  ✅ Урок {order}: {lesson['title'][:50]}")
            else:
                print(f"  ❌ Урок {order}: {lesson['title'][:50]}")
    
    print(f"\n🎉 Updated {total_updated} lessons total!")

if __name__ == "__main__":
    main()