"""
Astraa WSGI entrypoint.

Used by Gunicorn/WSGI production runtimes.
"""

from api import app

__all__ = ["app"]
