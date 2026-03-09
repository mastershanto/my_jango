from __future__ import annotations

import os

import django


_BOOTSTRAPPED = False


def bootstrap_django() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    _BOOTSTRAPPED = True
