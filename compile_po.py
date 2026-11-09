"""Compile django.po to django.mo compatible with Python 3.11's gettext."""
import struct
import re


def unescape_po_string(s):
    """Unescape a PO file string value."""
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
                result.append(nxt)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def parse_po(filepath):
    """Parse a .po file and return list of (msgid, msgstr) tuples."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        if line.startswith('msgid '):
            msgid_parts = []
            m = re.match(r'msgid "(.*)"$', line)
            if m:
                msgid_parts.append(m.group(1))
            i += 1
            while i < len(lines):
                cont_line = lines[i].rstrip('\n')
                if cont_line.startswith('"') and cont_line.endswith('"'):
                    msgid_parts.append(cont_line[1:-1])
                    i += 1
                else:
                    break
            msgid = unescape_po_string(''.join(msgid_parts))

            msgstr_parts = []
            if i < len(lines) and lines[i].rstrip('\n').startswith('msgstr '):
                m = re.match(r'msgstr "(.*)"$', lines[i].rstrip('\n'))
                if m:
                    msgstr_parts.append(m.group(1))
                i += 1
                while i < len(lines):
                    cont_line = lines[i].rstrip('\n')
                    if cont_line.startswith('"') and cont_line.endswith('"'):
                        msgstr_parts.append(cont_line[1:-1])
                        i += 1
                    else:
                        break
            msgstr = unescape_po_string(''.join(msgstr_parts))

            entries.append((msgid, msgstr))
        else:
            i += 1

    return entries


def write_mo(filepath, entries):
    """Write entries to a GNU gettext .mo file (Python 3.11 compatible)."""
    # Include ALL entries including empty msgid (header with charset metadata)
    # Python's gettext reads charset from the header entry

    num_strings = len(entries)

    # Build string data.
    # Length (mlen/tlen) counts only the encoded content, NOT the null terminator.
    # Python's gettext detects the header entry by mlen == 0 (empty msgid).
    # The null terminator is still written as part of the data bytes.
    orig_encoded = []
    trans_encoded = []
    orig_lengths = []
    trans_lengths = []
    for msgid, msgstr in entries:
        oe = msgid.encode('utf-8')
        te = msgstr.encode('utf-8')
        orig_encoded.append(oe)
        trans_encoded.append(te)
        orig_lengths.append(len(oe))
        trans_lengths.append(len(te))

    # String data section starts after header + both index tables
    string_data_start = 20 + num_strings * 8 + num_strings * 8

    # Offsets are absolute file positions pointing into the string data area.
    # Each string's data includes its null terminator.
    orig_offsets = []
    trans_offsets = []
    pos = string_data_start
    for oe in orig_encoded:
        orig_offsets.append(pos)
        pos += len(oe) + 1  # +1 for null terminator
    trans_data_start = pos
    for te in trans_encoded:
        trans_offsets.append(pos)
        pos += len(te) + 1  # +1 for null terminator

    orig_index_data = b''
    for i in range(num_strings):
        orig_index_data += struct.pack('<II', orig_lengths[i], orig_offsets[i])

    trans_index_data = b''
    for i in range(num_strings):
        trans_index_data += struct.pack('<II', trans_lengths[i], trans_offsets[i])

    # Header: 5 integers (Python 3.11 gettext reads 5, not 7)
    # Magic: 0x950412de for Python 3.11 LE_MAGIC
    header = struct.pack('<IIIII',
        0x950412de,  # magic (Python 3.11 LE_MAGIC)
        0,            # version
        num_strings,
        20,           # offset to original index table (right after 5-int header)
        20 + num_strings * 8,  # offset to translated index table
    )

    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(orig_index_data)
        f.write(trans_index_data)
        for oe in orig_encoded:
            f.write(oe + b'\x00')
        for te in trans_encoded:
            f.write(te + b'\x00')


if __name__ == '__main__':
    po_path = 'locale/ru/LC_MESSAGES/django.po'
    mo_path = 'locale/ru/LC_MESSAGES/django.mo'

    entries = parse_po(po_path)
    print(f"Parsed {len(entries)} entries from {po_path}")
    write_mo(mo_path, entries)
    print(f"Written {mo_path}")