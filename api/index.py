"""Vercel ASGI entrypoint for the public synthetic ClaimBack demo."""
import os

os.environ.setdefault("CLAIMBACK_DB", "/tmp/claimback.db")
os.environ.setdefault("CLAIMBACK_MODE", "demo")

from claimback.api import app  # noqa: E402,F401
