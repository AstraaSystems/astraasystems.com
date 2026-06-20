"""
Astraa WSGI Entry Point

Production WSGI servers such as Gunicorn or uWSGI can import this module.

Example:
    gunicorn wsgi:app

Local/internal QA can still run:
    python3 api.py
"""

from api import app

application = app
