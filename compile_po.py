#!/usr/bin/env python3
"""Compile django.po to django.mo using pure Python (no msgfmt needed)."""
import struct
from pathlib import Path

LOCALE_DIR = Path("locale/ru/LC_MESSAGES")
PO_FILE = LOCALE_DIR / "django.po"
MO_FILE = LOCALE_DIR / "django.mo"


def unescape_po_string(s):
    """Convert .po escape sequences to actual characters (\\n, \\t, \\r, \\", \\\\)."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == 'n':
                result.append('\n')
            elif nxt == 't':
                result.append('\t')
            elif nxt == 'r':
                result.append('\r')
            elif nxt == '"':
                result.append('"')
            elif nxt == '\\':
                result.append('\\')
            else:
                result.append(s[i])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def compile_mo(po_path, mo_path):
    messages = []
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    current_msgid = None
    current_msgstr = None
    collecting_msgid = False
    collecting_msgstr = False

    for line in content.split('\n'):
        stripped = line.rstrip('\r\n')
        if stripped.startswith('msgid '):
            if current_msgid is not None:
                messages.append((current_msgid, current_msgstr or ""))
            val = stripped[6:]
            if val.startswith('"') and val.endswith('"'):
                current_msgid = unescape_po_string(val[1:-1])
            else:
                current_msgid = unescape_po_string(val)
            collecting_msgid = True
            collecting_msgstr = False
        elif stripped.startswith('msgstr '):
            val = stripped[7:]
            if val.startswith('"') and val.endswith('"'):
                current_msgstr = unescape_po_string(val[1:-1])
            else:
                current_msgstr = unescape_po_string(val)
            collecting_msgstr = True
            collecting_msgid = False
        elif stripped.startswith('"') and collecting_msgid:
            val = stripped[1:-1] if stripped.endswith('"') else stripped[1:]
            current_msgid += unescape_po_string(val)
        elif stripped.startswith('"') and collecting_msgstr:
            val = stripped[1:-1] if stripped.endswith('"') else stripped[1:]
            current_msgstr += unescape_po_string(val)

    if current_msgid is not None:
        messages.append((current_msgid, current_msgstr or ""))

    messages = [(m, s) for m, s in messages if m is not None]
    messages.sort(key=lambda x: (x[0] != "", x[0]))  # header (empty msgid) first

    mo_data = bytearray()
    mo_data.extend(struct.pack('<I', 0x950412de))  # magic (little endian)
    mo_data.extend(struct.pack('<I', 0))  # version
    mo_data.extend(struct.pack('<I', len(messages)))  # num messages

    msgid_table_offset = 28
    msgstr_table_offset = msgid_table_offset + len(messages) * 8

    mo_data.extend(struct.pack('<I', msgid_table_offset))
    mo_data.extend(struct.pack('<I', msgstr_table_offset))
    mo_data.extend(struct.pack('<I', 0))  # hash table size
    mo_data.extend(struct.pack('<I', 0))  # hash table offset

    current_str_offset = msgstr_table_offset + len(messages) * 8

    msgid_table = bytearray()
    msgstr_table = bytearray()
    strings_data = bytearray()

    for msgid, msgstr in messages:
        msgid_bytes = msgid.encode('utf-8')
        msgstr_bytes = msgstr.encode('utf-8')

        msgid_table.extend(struct.pack('<I', len(msgid_bytes)))
        msgid_table.extend(struct.pack('<I', current_str_offset))
        strings_data.extend(msgid_bytes)
        current_str_offset += len(msgid_bytes)

        msgstr_table.extend(struct.pack('<I', len(msgstr_bytes)))
        msgstr_table.extend(struct.pack('<I', current_str_offset))
        strings_data.extend(msgstr_bytes)
        current_str_offset += len(msgstr_bytes)

    mo_data.extend(msgid_table)
    mo_data.extend(msgstr_table)
    mo_data.extend(strings_data)
    mo_data.extend(b'\x00')  # trailing byte: Python gettext requires tend < buflen

    mo_path.write_bytes(mo_data)
    print(f"Written {mo_path} with {len(messages)} messages")


compile_mo(PO_FILE, MO_FILE)
