"""MerlinDB - Parse and export Microsoft Access Database files used by GeniSys software."""

from .api import (
    MerlinDB,
    get_database_info,
    list_tables,
    load_database,
    quick_export,
)
from .merlindb import *  # noqa: F403

__all__ = [
    "MerlinDB",
    "load_database",
    "quick_export",
    "list_tables",
    "get_database_info",
]
