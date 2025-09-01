from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from merlindb.exporters import CSVExporter, DataExporter, JSONExporter, XLSXExporter, YAMLExporter
from merlindb.providers import (
    DataProvider,
    DeviceDataProvider,
    DynaliteDataProvider,
    RawDataProvider,
)
from merlindb.utils import get_mdb


def get_provider(db_path: str, mode: str) -> DataProvider:
    """Get a data provider instance for the specified mode.

    Args:
        db_path: Path to the MDB database file
        mode: Browsing mode ('raw', 'dynalite', 'device')

    Returns:
        DataProvider instance for the specified mode

    Raises:
        ValueError: If mode is not supported or database cannot be loaded
    """
    db = get_mdb(db_path)
    if not db:
        raise ValueError(f"Failed to load database from {db_path}")

    providers = {
        "raw": RawDataProvider,
        "dynalite": DynaliteDataProvider,
        "device": DeviceDataProvider,
    }

    mode_lower = mode.lower()
    if mode_lower not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unsupported mode '{mode}'. Available modes: {available}")

    return providers[mode_lower](db)


def get_exporter(provider: DataProvider, format_name: str) -> DataExporter:
    """Get an exporter instance for the specified format.

    Args:
        provider: DataProvider instance to use as data source
        format_name: Export format ('json', 'yaml', 'csv', 'xlsx')

    Returns:
        DataExporter instance for the specified format

    Raises:
        ValueError: If format is not supported
    """
    exporters = {
        "json": JSONExporter,
        "yaml": YAMLExporter,
        "csv": CSVExporter,
        "xlsx": XLSXExporter,
    }

    format_lower = format_name.lower()
    if format_lower not in exporters:
        available = ", ".join(exporters.keys())
        raise ValueError(f"Unsupported format '{format_name}'. Available formats: {available}")

    return exporters[format_lower](provider)


def select_tables(provider: DataProvider, table_patterns: list[str] | None = None) -> list[str]:
    """Select tables based on patterns or return all tables.

    Args:
        provider: DataProvider instance to get table list from
        table_patterns: List of table name patterns (supports wildcards) or None for all tables

    Returns:
        List of selected table names

    Raises:
        ValueError: If no tables match the patterns
    """
    available_tables = provider.get_available_tables()

    if not table_patterns:
        # Return all tables if no patterns specified
        return available_tables

    selected_tables = set()

    for pattern in table_patterns:
        # Support exact match and wildcard patterns
        matches = fnmatch.filter(available_tables, pattern)
        if matches:
            selected_tables.update(matches)
        elif pattern in available_tables:
            # Direct match
            selected_tables.add(pattern)

    selected_list = sorted(selected_tables)

    if not selected_list:
        available_str = ", ".join(available_tables)
        patterns_str = ", ".join(table_patterns)
        raise ValueError(
            f"No tables match patterns: {patterns_str}. Available tables: {available_str}"
        )

    return selected_list


def dump_tables(
    db_path: str,
    output_path: str,
    format_name: str,
    mode: str = "raw",
    tables: list[str] | None = None,
    single_file: bool = True,
) -> dict[str, Any]:
    """Dump tables from database to specified format.

    Args:
        db_path: Path to the MDB database file
        output_path: Path for output file(s)
        format_name: Export format ('json', 'yaml', 'csv', 'xlsx')
        mode: Browsing mode ('raw', 'dynalite', 'device')
        tables: List of table name patterns or None for all tables
        single_file: If True, export all tables to one file. If False, create separate files.

    Returns:
        Dictionary with export statistics and information

    Raises:
        ValueError: If parameters are invalid or export fails
        IOError: If files cannot be written
    """
    # Get provider and exporter
    provider = get_provider(db_path, mode)
    exporter = get_exporter(provider, format_name)

    # Select tables
    selected_tables = select_tables(provider, tables)

    # Prepare output path
    output_file = Path(output_path)
    if not output_file.suffix:
        # Add appropriate extension if not provided
        output_file = output_file.with_suffix(exporter.get_file_extension())

    # Perform export
    if len(selected_tables) == 1:
        # Single table export
        table_name = selected_tables[0]
        exporter.export_single_table(table_name, output_file)

        return {
            "mode": mode,
            "format": format_name,
            "tables_exported": 1,
            "table_names": selected_tables,
            "output_files": [str(output_file)],
            "single_file": True,
        }
    else:
        # Multiple tables export
        exporter.export_multiple_tables(selected_tables, output_file, single_file)

        if single_file:
            output_files = [str(output_file)]
        else:
            # Calculate separate file names
            base_path = output_file.with_suffix("")
            extension = exporter.get_file_extension()
            output_files = [
                str(base_path.parent / f"{base_path.name}_{table}{extension}")
                for table in selected_tables
            ]

        return {
            "mode": mode,
            "format": format_name,
            "tables_exported": len(selected_tables),
            "table_names": selected_tables,
            "output_files": output_files,
            "single_file": single_file,
        }
