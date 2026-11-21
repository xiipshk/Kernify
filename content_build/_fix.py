import sys

path = "content_build/lessons/css/1_9.py"
src = open(path, encoding="utf-8").read()

bad = '        code(\n            """\n            <meta name="viewport" content="width=device-width, initial-scale=1">\n            """\n        ),'
good = '        html(\n            """\n            <meta name="viewport" content="width=device-width, initial-scale=1">\n            """\n        ),'

assert bad in src, "не найдено"
src = src.replace(bad, good)

# добавить импорт html в блок импорта
src = src.replace("    heading,\n", "    heading,\n    html,\n", 1)

open(path, "w", encoding="utf-8").write(src)
print("ok")
