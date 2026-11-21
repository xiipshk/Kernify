#!/usr/bin/env python
"""Crawl every accessible Django page and report 500s, TemplateSyntaxError, and exceptions.

Usage:
    python crawl_pages.py
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver
from django.template.exceptions import TemplateSyntaxError
from django.contrib.auth import get_user_model

User = get_user_model()


def collect_paths(patterns, prefix=""):
    """Walk the URL resolver tree, returning paths that need no path parameters."""
    found = []
    for p in patterns:
        route = getattr(p.pattern, "route", None)
        if route is None:
            route = getattr(p.pattern, "_route", None)
        if route is None:
            continue  # regex-based path we cannot build a URL for
        path = prefix + route
        if isinstance(p, URLResolver):
            found.extend(collect_paths(p.url_patterns, path))
        elif isinstance(p, URLPattern):
            if not getattr(p.pattern, "converters", {}):
                found.append(path)
    return found


def main():
    resolver = get_resolver()
    raw = collect_paths(resolver.url_patterns)
    # Normalize to leading-slash paths, de-duplicate, sort.
    paths = sorted({("/" + p.lstrip("/")) if p else "/" for p in raw})

    # --- Create a test user (email is USERNAME_FIELD) -----------------------
    email = "crawl_test@example.com"
    password = "CrawlTestPass123!"
    if not User.objects.filter(email=email).exists():
        User.objects.create_user(
            email=email,
            username="crawl_test",
            first_name="Crawl",
            last_name="Test",
            password=password,
        )
    else:
        u = User.objects.get(email=email)
        u.set_password(password)
        u.save()

    results = []

    def crawl(client, authenticated):
        for path in paths:
            try:
                resp = client.get(path)
                status = resp.status_code
                error = None
            except TemplateSyntaxError as exc:
                status = None
                error = f"TemplateSyntaxError: {exc}"
            except Exception as exc:  # noqa: BLE001 - report any runtime error
                status = None
                error = f"{type(exc).__name__}: {exc}"
            results.append(
                {
                    "path": path,
                    "authenticated": authenticated,
                    "status": status,
                    "error": error,
                }
            )

    print(f"URLs to crawl: {len(paths)}")
    print("=" * 70)

    # Unauthenticated (localhost is in ALLOWED_HOSTS; 'testserver' is not)
    crawl(Client(HTTP_HOST="localhost"), False)

    # Authenticated
    auth_client = Client(HTTP_HOST="localhost")
    auth_client.login(username=email, password=password)
    crawl(auth_client, True)

    # --- Report -------------------------------------------------------------
    errors = [r for r in results if r["error"] or r["status"] == 500]

    for r in results:
        mark = ""
        if r["error"]:
            mark = "  <<< ERROR"
        elif r["status"] == 500:
            mark = "  <<< 500"
        tag = "AUTH " if r["authenticated"] else "     "
        print(f"{tag}{r['status']}  {r['path']}{mark}")

    print("=" * 70)
    print(f"Requests made : {len(results)}  ({len(paths)} paths x 2 auth states)")
    print(f"Errors        : {len(errors)}  (500 / TemplateSyntaxError / exceptions)")
    print()

    if errors:
        print("=== ERROR DETAILS ===")
        for r in errors:
            tag = "AUTH " if r["authenticated"] else "     "
            print(f"{tag}{r['path']}")
            print(f"   {r['error'] if r['error'] else 'HTTP 500'}")
            print()
    else:
        print("No errors found.")


if __name__ == "__main__":
    main()
