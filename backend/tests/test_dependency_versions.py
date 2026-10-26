"""Regression guard for dependency security pins.

The versions below are the fixed versions named in the CVE notes
(GHSA/PYSEC entries) for the dependent packages. If a future change moves
any of these pins away from the fixed version, this test fails.
"""

import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REQUIREMENTS = BACKEND_DIR / "requirements.txt"
FRONTEND_LOCK = BACKEND_DIR.parent / "frontend" / "package-lock.json"

# Fixed versions required by the advisory notes (package name -> version).
EXPECTED_PYTHON_PINS = {
    "anyio": "4.14.2",
    "h11": "0.16.0",
    "SQLAlchemy": "0.7.0b4",
    "fastapi": "0.65.2",
    "starlette": "0.25.0",
    "uvicorn": "0.11.7",
}

EXPECTED_ZOD_VERSION = "4.6.6"


def _requirements_pins():
    pins = {}
    for line in REQUIREMENTS.read_text(encoding="utf-16").splitlines():
        line = line.strip()
        if not line or "==" not in line:
            continue
        name, _, version = line.partition("==")
        pins[name.strip()] = version.strip()
    return pins


def test_cve_fixed_versions_are_pinned():
    # Python dependencies (backend/requirements.txt).
    pins = _requirements_pins()
    for name, expected in EXPECTED_PYTHON_PINS.items():
        assert name in pins, f"{name} is missing from requirements.txt"
        assert pins[name] == expected, (
            f"{name} is pinned to {pins[name]!r}, expected {expected!r}"
        )

    # JavaScript dependency (frontend/package-lock.json).
    lock = json.loads(FRONTEND_LOCK.read_text(encoding="utf-8"))
    zod = lock["packages"]["node_modules/zod"]
    assert zod["version"] == EXPECTED_ZOD_VERSION, (
        f"zod is at {zod['version']!r}, expected {EXPECTED_ZOD_VERSION!r}"
    )
