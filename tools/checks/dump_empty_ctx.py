# -*- coding: utf-8 -*-
"""Печатает компактный контекст для всех пустых code-блоков."""

import json
import glob

OUT = '/private/var/folders/xw/9cpnw6912l3d0zdpcntn158w0000gn/T/opencode/empty_ctx.txt'

lines = []
for src in ['python', 'cpp', 'javascript', 'rust', 'css', 'csharp']:
    for f in sorted(glob.glob(f'fixtures/lessons/{src}/*.json')):
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        blocks = d.get('content_blocks', [])
        empt = [i for i, b in enumerate(blocks)
                if b.get('type') == 'code' and not str(b.get('content', '') or '').strip()]
        if not empt:
            continue
        lines.append('=' * 100)
        lines.append(f'### {f} | {d.get("title")}')
        for i in empt:
            prev = []
            for j in range(i - 1, -1, -1):
                b = blocks[j]
                if b.get('type') in ('heading', 'text'):
                    prev.append((j, b.get('type'),
                                 str(b.get('content') or b.get('items') or '')[:230]))
                    if len(prev) >= 2:
                        break
            nxt = ''
            for j in range(i + 1, len(blocks)):
                if blocks[j].get('type') in ('heading', 'text'):
                    nxt = (f"[{j}] {blocks[j].get('type')}: "
                           f"{str(blocks[j].get('content') or blocks[j].get('items') or '')[:160]}")
                    break
            lines.append(f"--- [{i}] lang={blocks[i].get('language')}")
            for p in reversed(prev):
                lines.append(f'    prev[{p[0]}] {p[1]}: {p[2]}')
            lines.append(f'    next: {nxt}')

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print(f'written {OUT}: {len(lines)} lines')
