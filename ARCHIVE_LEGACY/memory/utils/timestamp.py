"""
Timestamp Utility
-----------------
Provides consistent timestamps for memory records.
"""

from datetime import datetime


def now_timestamp():
    return datetime.utcnow().isoformat() + "Z"
