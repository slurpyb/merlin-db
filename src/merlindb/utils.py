"""Deprecated utilities - functionality moved to parser.py"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from merlindb.exporters import CSVExporter, DataExporter, JSONExporter, YAMLExporter
from merlindb.parser import get_available_tables, get_mdb, get_table_data


# This file is kept for backward compatibility but functionality has been moved to parser.py
def export_tables(
    db_path: str,
    output_path: str,
    format_name: str = "json",
    mode: str = "raw",  # Keep for backward compatibility, but ignored
    tables: list[str] | None = None,
    single_file: bool = True,
) -> dict[str, Any]:
    """Export database tables to files.

    Args:
        db_path: Path to the MDB database file
        output_path: Path for output file(s)
        format_name: Export format ('json', 'yaml', 'csv')
        mode: Mode (ignored, kept for backward compatibility)
        tables: List of table patterns to export or None for all tables
        single_file: If True, export to single file. If False, create separate files.

    Returns:
        Dictionary with export results and metadata

    Raises:
        ValueError: If export fails
    """
    try:
        # Get database and available tables
        db, available_tables = get_database_info(db_path)

        # Select which tables to export
        selected_tables = select_tables(available_tables, tables)

        # Get exporter for the specified format
        exporter = get_exporter(db, format_name)

        # Prepare output path
        output_base = Path(output_path)
        output_files = []

        if single_file:
            # Export all selected tables to a single file
            exporter.export_multiple_tables(selected_tables, output_base, single_file=True)
            output_files = [str(output_base)]
        else:
            # Export each table to separate files
            exporter.export_multiple_tables(selected_tables, output_base, single_file=False)

            # Build list of output files
            extension = exporter.get_file_extension()
            for table in selected_tables:
                table_file = output_base.parent / f"{output_base.stem}_{table}{extension}"
                output_files.append(str(table_file))

        return {
            "format": format_name,
            "tables_exported": len(selected_tables),
            "table_names": selected_tables,
            "output_files": output_files,
        }

    except Exception as e:
        raise ValueError(f"Export failed: {e}") from e


def get_database_info(db_path: str) -> tuple[Any, list[str]]:
    """Get database instance and available tables.

    Args:
        db_path: Path to the MDB database file

    Returns:
        Tuple of (database instance, list of table names)

    Raises:
        ValueError: If database cannot be loaded
    """
    db = get_mdb(db_path)
    if not db:
        raise ValueError(f"Failed to load database from {db_path}")

    tables = get_available_tables(db)
    return db, tables


def get_exporter(db: Any, format_name: str) -> DataExporter:
    """Get an exporter instance for the specified format.

    Args:
        db: Database instance
        format_name: Export format ('json', 'yaml', 'csv')

    Returns:
        DataExporter instance for the specified format

    Raises:
        ValueError: If format is not supported
    """

    # Create a simple provider-like object for backward compatibility with exporters
    class SimpleDataProvider:
        def __init__(self, database):
            self.db = database

        def get_available_tables(self) -> list[str]:
            return get_available_tables(self.db)

        def get_table_data(self, table_name: str) -> dict[str, Any]:
            return get_table_data(self.db, table_name)

        def get_mode_name(self) -> str:
            return "raw"

    provider = SimpleDataProvider(db)

    exporters = {
        "json": JSONExporter,
        "yaml": YAMLExporter,
        "csv": CSVExporter,
    }

    format_lower = format_name.lower()
    if format_lower not in exporters:
        available = ", ".join(exporters.keys())
        raise ValueError(f"Unsupported format '{format_name}'. Available formats: {available}")

    return exporters[format_lower](provider)


def select_tables(
    available_tables: list[str], table_patterns: list[str] | None = None
) -> list[str]:
    """Select tables based on patterns or return all tables.

    Args:
        available_tables: List of all available table names
        table_patterns: List of table name patterns (supports wildcards) or None for all tables

    Returns:
        List of selected table names

    Raises:
        ValueError: If no tables match the patterns
    """
    if not table_patterns:
        # Return all tables if no patterns specified
        return available_tables

    selected_tables = set()

    for pattern in table_patterns:
        # Support exact match and wildcard patterns
        matches = fnmatch.filter(available_tables, pattern)
        selected_tables.update(matches)

        # Also try exact match (case-insensitive)
        for table in available_tables:
            if table.lower() == pattern.lower():
                selected_tables.add(table)

    selected_list = sorted(selected_tables)

    if not selected_list:
        available_str = ", ".join(available_tables)
        patterns_str = ", ".join(table_patterns)
        raise ValueError(
            f"No tables found matching patterns: {patterns_str}. Available tables: {available_str}"
        )

    return selected_list
