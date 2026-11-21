"""Диагностика: что реально лежит в базе по языку."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from learning.models import Lesson  # noqa: E402


def main() -> None:
    # Отключаем мягкое удаление на уровне менеджера, чтобы видеть всё.
    qs = Lesson.objects.all()
    if hasattr(qs, "deleted"):
        print("используется общий менеджер")
    rows = []
    for x in qs.select_related("topic__program__language").order_by("pk"):
        rows.append(
            (
                x.pk,
                x.topic.program.language.slug,
                x.topic.program.order,
                x.topic.order,
                x.order,
                x.name,
                len(x.content or []),
                x.is_deleted,
                x.status,
            )
        )
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
