"""Block 0.1 smoke test: every package imports cleanly."""

import importlib

PACKAGES = ["schemas", "ingestion", "battery", "generator", "grading", "derive"]


def test_packages_import():
    for name in PACKAGES:
        mod = importlib.import_module(name)
        assert mod is not None
