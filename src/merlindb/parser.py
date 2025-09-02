"""Core MDB parsing functionality with integrated Pydantic validation."""

from __future__ import annotations

from typing import Any

from access_parser import AccessParser
from pydantic import ValidationError

from merlindb.models.genisys import model_map


def get_mdb(file_path: str) -> AccessParser | None:
    """Load an MDB file and return AccessParser instance.

    Args:
        file_path: Path to the MDB file

    Returns:
        AccessParser instance or None if loading failed
    """
    try:
        return AccessParser(file_path)
    except Exception as e:
        print(f"Error loading MDB file: {e}")
        return None


def get_available_tables(db: AccessParser) -> list[str]:
    """Get list of all available tables in the database.

    Args:
        db: AccessParser instance

    Returns:
        Sorted list of table names
    """
    return sorted(list(db.catalog.keys()))


def get_table_data(db: AccessParser, table_name: str, validate: bool = True) -> dict[str, Any]:
    """Get data for a specific table with optional Pydantic validation.

    Args:
        db: AccessParser instance
        table_name: Name of the table to retrieve
        validate: Whether to validate data using Pydantic models

    Returns:
        Dictionary containing table data with column names as keys

    Raises:
        ValueError: If table doesn't exist or parsing fails
    """
    available_tables = get_available_tables(db)
    if table_name not in available_tables:
        available = ", ".join(available_tables)
        raise ValueError(f"Table '{table_name}' not found. Available tables: {available}")

    try:
        raw_data = db.parse_table(table_name)

        if not validate or table_name not in model_map:
            # Return raw data without validation
            return raw_data

        # Apply Pydantic validation
        return _validate_table_data(table_name, raw_data)

    except Exception as e:
        raise ValueError(f"Failed to parse table '{table_name}': {e}") from e


def _validate_table_data(table_name: str, raw_data: dict[str, Any]) -> dict[str, Any]:
    """Validate table data using Pydantic models.

    Args:
        table_name: Name of the table
        raw_data: Raw table data from AccessParser

    Returns:
        Validated table data

    Raises:
        ValueError: If validation fails
    """
    model_class = model_map[table_name]
    validated_data = {col: [] for col in raw_data.keys()}

    # Convert column-based data to row-based for validation
    if not raw_data:
        return validated_data

    # Get number of rows (length of first column)
    num_rows = len(next(iter(raw_data.values())))
    columns = list(raw_data.keys())

    validation_errors = []

    for row_idx in range(num_rows):
        # Build row dictionary
        row_data = {}
        for col in columns:
            if row_idx < len(raw_data[col]):
                row_data[col] = raw_data[col][row_idx]
            else:
                row_data[col] = None

        # Validate row with Pydantic model
        try:
            validated_row = model_class(**row_data)
            row_dict = validated_row.model_dump()

            # Add validated data back to column format
            for col, value in row_dict.items():
                if col in validated_data:
                    validated_data[col].append(value)

        except ValidationError as e:
            validation_errors.append(f"Row {row_idx}: {e}")
            # Add raw data for failed validation
            for col in columns:
                if col in validated_data:
                    validated_data[col].append(row_data.get(col))

    if validation_errors:
        print(f"Warning: Validation errors in table '{table_name}':")
        for error in validation_errors[:5]:  # Show first 5 errors
            print(f"  {error}")
        if len(validation_errors) > 5:
            print(f"  ... and {len(validation_errors) - 5} more errors")

    return validated_data


def table_to_dicts(table_cols: list[str], table_rows: list[list]) -> list[dict]:
    """Convert table structure to list of dictionaries.

    Args:
        table_cols: List of column names (keys for dictionaries)
        table_rows: List of lists where each inner list contains all values for one column

    Returns:
        List of dictionaries, one per row
    """
    if not table_cols or not table_rows:
        return []

    # Transpose the table_rows to get rows instead of columns
    rows = list(zip(*table_rows, strict=False))

    # Create dictionary for each row
    return [dict(zip(table_cols, row, strict=False)) for row in rows]
