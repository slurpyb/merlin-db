"""Test core parser functionality with real MDB data."""

import logging

import pytest

# Suppress access-parser logging during tests
logging.getLogger("access_parser").setLevel(logging.ERROR)

from merlindb.models.genisys import model_map
from merlindb.parser import (
    _validate_table_data,
    get_available_tables,
    get_mdb,
    get_table_data,
    table_to_dicts,
)

# Test data file in project root
TEST_DB_PATH = "test.mdb"


def test_get_mdb_success():
    """Test successful MDB file loading."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None
    assert hasattr(db, "catalog")
    assert len(db.catalog) > 0


def test_get_mdb_invalid_file():
    """Test MDB loading with non-existent file."""
    db = get_mdb("nonexistent.mdb")
    assert db is None


def test_get_available_tables():
    """Test retrieving available table names."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    tables = get_available_tables(db)
    assert isinstance(tables, list)
    assert len(tables) > 0
    assert "GeniSysObjects" in tables  # Known table from test.mdb
    assert tables == sorted(tables)  # Should be sorted


def test_get_table_data_without_validation():
    """Test retrieving table data without Pydantic validation."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    # Test with a known table that might not have Pydantic model
    table_data = get_table_data(db, "Config", validate=False)
    assert isinstance(table_data, dict)

    # Test with Config table specifically
    if "Config" in get_available_tables(db):
        config_data = get_table_data(db, "Config", validate=False)
        assert isinstance(config_data, dict)
        # Should have column names as keys
        for _key, values in config_data.items():
            assert isinstance(values, list)


def test_get_table_data_invalid_table():
    """Test error handling for invalid table names."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    with pytest.raises(ValueError, match="Table 'NonExistentTable' not found"):
        get_table_data(db, "NonExistentTable")


def test_get_table_data_with_validation():
    """Test table data retrieval with Pydantic validation."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    # Find a table that has a Pydantic model
    available_tables = get_available_tables(db)
    test_table = None

    for table_name in available_tables:
        if table_name in model_map:
            test_table = table_name
            break

    if test_table:
        # Test with validation enabled
        validated_data = get_table_data(db, test_table, validate=True)
        assert isinstance(validated_data, dict)

        # Test without validation for comparison
        raw_data = get_table_data(db, test_table, validate=False)
        assert isinstance(raw_data, dict)

        # Both should have same column structure
        assert set(validated_data.keys()) == set(raw_data.keys())
    else:
        pytest.skip("No tables with Pydantic models found in test data")


def test_table_to_dicts_basic():
    """Test conversion of table structure to list of dictionaries."""
    cols = ["name", "age", "city"]
    rows = [["Alice", "Bob"], [25, 30], ["NYC", "LA"]]

    result = table_to_dicts(cols, rows)
    expected = [
        {"name": "Alice", "age": 25, "city": "NYC"},
        {"name": "Bob", "age": 30, "city": "LA"},
    ]

    assert result == expected


def test_table_to_dicts_empty_data():
    """Test table_to_dicts with empty data."""
    # Empty columns
    assert table_to_dicts([], []) == []

    # Empty rows
    assert table_to_dicts(["col1", "col2"], []) == []


def test_table_to_dicts_with_real_data():
    """Test table_to_dicts with real MDB data."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    # Get data from a small table for testing
    available_tables = get_available_tables(db)
    test_table = available_tables[0]  # Use first available table

    table_data = get_table_data(db, test_table, validate=False)
    if table_data:
        cols = list(table_data.keys())
        rows = [table_data[col] for col in cols]

        result = table_to_dicts(cols, rows)
        assert isinstance(result, list)

        if result:  # If table has data
            assert isinstance(result[0], dict)
            assert set(result[0].keys()) == set(cols)


def test_validate_table_data_function():
    """Test the _validate_table_data function directly."""
    # Find a table with a Pydantic model for testing
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)
    test_table = None

    for table_name in available_tables:
        if table_name in model_map:
            test_table = table_name
            break

    if test_table:
        # Get raw data
        raw_data = get_table_data(db, test_table, validate=False)

        # Test validation function
        validated_data = _validate_table_data(test_table, raw_data)
        assert isinstance(validated_data, dict)
        assert set(validated_data.keys()) == set(raw_data.keys())
    else:
        pytest.skip("No tables with Pydantic models found for validation testing")


def test_integration_all_tables_accessible():
    """Integration test: verify all tables can be accessed without errors."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)
    accessible_count = 0
    error_tables = []

    for table_name in available_tables:
        try:
            data = get_table_data(db, table_name, validate=False)
            assert isinstance(data, dict)
            accessible_count += 1
        except Exception as e:
            error_tables.append((table_name, str(e)))

    # Most tables should be accessible
    assert accessible_count > len(available_tables) * 0.8  # At least 80% accessible

    if error_tables:
        print(f"Tables with access errors: {error_tables[:5]}")


## Tests for specific test.mdb tables


def test_known_tables_exist():
    """Test that known tables from list_tables.py exist."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)
    known_tables = [
        "GeniSysObjects",
        "Config",
        "DeviceTypes",
        "AreaNames",
        "Buttons",
        "Events",
        "ProjectName",
        "Version",
    ]

    for table_name in known_tables:
        assert table_name in available_tables, f"Expected table '{table_name}' not found"


def test_config_table_structure():
    """Test the Config table structure (commonly available)."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    if "Config" in get_available_tables(db):
        config_data = get_table_data(db, "Config", validate=False)
        assert isinstance(config_data, dict)
        # Config table should have some columns
        assert len(config_data) > 0
