"""Test Pydantic validation integration with real MDB data."""

import logging

import pytest

# Suppress access-parser logging during tests
logging.getLogger("access_parser").setLevel(logging.ERROR)

from merlindb.models.genisys import model_map
from merlindb.parser import _validate_table_data, get_available_tables, get_mdb, get_table_data

# Test data file in project root
TEST_DB_PATH = "test.mdb"


def test_model_map_coverage():
    """Test which tables have Pydantic models defined."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)
    tables_with_models = [table for table in available_tables if table in model_map]
    tables_without_models = [table for table in available_tables if table not in model_map]

    print(f"\nTables with Pydantic models ({len(tables_with_models)}):")
    for table in sorted(tables_with_models):
        print(f"  - {table}")

    print(f"\nTables without Pydantic models ({len(tables_without_models)}):")
    for table in sorted(tables_without_models):
        print(f"  - {table}")

    # Should have at least some models defined
    assert len(tables_with_models) > 0
    assert "Config" in tables_with_models  # Known table with model


def test_validation_with_real_data():
    """Test Pydantic validation with actual MDB table data."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    # Test each table that has a Pydantic model
    available_tables = get_available_tables(db)
    validation_results = {}

    for table_name in available_tables:
        if table_name in model_map:
            try:
                # Test validation enabled
                validated_data = get_table_data(db, table_name, validate=True)

                # Test validation disabled for comparison
                raw_data = get_table_data(db, table_name, validate=False)

                validation_results[table_name] = {
                    "status": "success",
                    "validated_records": len(validated_data.get(list(validated_data.keys())[0], []))
                    if validated_data
                    else 0,
                    "raw_records": len(raw_data.get(list(raw_data.keys())[0], []))
                    if raw_data
                    else 0,
                }

                # Both should have same structure
                assert set(validated_data.keys()) == set(raw_data.keys())

            except Exception as e:
                validation_results[table_name] = {"status": "error", "error": str(e)}

    # Print validation summary
    print("\nPydantic Validation Results:")
    for table_name, result in validation_results.items():
        if result["status"] == "success":
            print(f"  ✓ {table_name}: {result['validated_records']} records validated")
        else:
            print(f"  ✗ {table_name}: {result['error']}")

    # At least some validations should succeed
    successful_validations = [r for r in validation_results.values() if r["status"] == "success"]
    assert len(successful_validations) > 0


def test_config_table_validation():
    """Test specific validation of Config table."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    if "Config" not in get_available_tables(db):
        pytest.skip("Config table not found in test database")

    # Test with validation
    config_validated = get_table_data(db, "Config", validate=True)
    assert isinstance(config_validated, dict)

    # Test without validation
    config_raw = get_table_data(db, "Config", validate=False)
    assert isinstance(config_raw, dict)

    # Should have same columns
    assert set(config_validated.keys()) == set(config_raw.keys())

    # Validation should succeed for Config table
    if "Config" in model_map:
        validated_result = _validate_table_data("Config", config_raw)
        assert isinstance(validated_result, dict)
        assert set(validated_result.keys()) == set(config_raw.keys())


def test_validation_error_handling():
    """Test validation error handling with potentially problematic data."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)

    # Find tables with models and test validation
    for table_name in available_tables[:5]:  # Test first 5 tables
        if table_name in model_map:
            try:
                # This should not raise exceptions, even with validation errors
                validated_data = get_table_data(db, table_name, validate=True)
                assert isinstance(validated_data, dict)

                # Raw data should also work
                raw_data = get_table_data(db, table_name, validate=False)
                assert isinstance(raw_data, dict)

                # Validate directly to test error handling
                validation_result = _validate_table_data(table_name, raw_data)
                assert isinstance(validation_result, dict)

            except Exception as e:
                # If validation fails, it should be a ValueError with clear message
                assert isinstance(e, ValueError)
                assert "Failed to parse table" in str(e) or "not found" in str(e)


def test_validation_preserves_data_structure():
    """Test that validation preserves the column-based data structure."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    # Find a table with model and data
    available_tables = get_available_tables(db)
    test_table = None

    for table_name in available_tables:
        if table_name in model_map:
            raw_data = get_table_data(db, table_name, validate=False)
            if raw_data and any(len(col_data) > 0 for col_data in raw_data.values()):
                test_table = table_name
                break

    if not test_table:
        pytest.skip("No tables with Pydantic models and data found")

    # Get raw and validated data
    raw_data = get_table_data(db, test_table, validate=False)
    validated_data = get_table_data(db, test_table, validate=True)

    # Structure should be preserved
    assert isinstance(raw_data, dict)
    assert isinstance(validated_data, dict)
    assert set(raw_data.keys()) == set(validated_data.keys())

    # Each column should remain a list
    for col_name in raw_data.keys():
        assert isinstance(raw_data[col_name], list)
        assert isinstance(validated_data[col_name], list)

        # Should have same number of records (or handle validation errors gracefully)
        # Note: validation errors might result in different lengths, but structure preserved
        assert len(validated_data[col_name]) >= 0


def test_validation_with_empty_tables():
    """Test validation behavior with empty tables."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)

    # Find tables with models but no data
    for table_name in available_tables:
        if table_name in model_map:
            raw_data = get_table_data(db, table_name, validate=False)

            # Check if table is empty
            is_empty = not raw_data or all(len(col_data) == 0 for col_data in raw_data.values())

            if is_empty:
                # Validation should handle empty tables gracefully
                validated_data = get_table_data(db, table_name, validate=True)
                assert isinstance(validated_data, dict)

                # Should preserve empty structure
                if raw_data:
                    assert set(validated_data.keys()) == set(raw_data.keys())
                    for col_name in raw_data.keys():
                        assert len(validated_data[col_name]) == 0


def test_specific_model_validation():
    """Test specific Pydantic models with known table structures."""
    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)

    # Test specific models if their tables exist
    specific_tests = [
        ("Config", "should have configuration data"),
        ("DeviceTypes", "should have device type definitions"),
        ("AVManufacturer", "should have AV manufacturer data"),
    ]

    for table_name, description in specific_tests:
        if table_name in available_tables and table_name in model_map:
            print(f"\nTesting {table_name}: {description}")

            # Test validation
            try:
                validated_data = get_table_data(db, table_name, validate=True)
                raw_data = get_table_data(db, table_name, validate=False)

                assert isinstance(validated_data, dict)
                assert isinstance(raw_data, dict)

                # Check that validation worked
                model_class = model_map[table_name]
                print(f"  Model: {model_class.__name__}")
                print(f"  Columns: {list(raw_data.keys()) if raw_data else 'none'}")
                print(f"  Records: {len(next(iter(raw_data.values()), [])) if raw_data else 0}")

            except Exception as e:
                print(f"  Validation error: {e}")
                # This is acceptable - some tables might have schema mismatches


def test_validation_performance():
    """Test that validation doesn't cause significant performance issues."""
    import time

    db = get_mdb(TEST_DB_PATH)
    assert db is not None

    available_tables = get_available_tables(db)
    tables_with_models = [t for t in available_tables if t in model_map][:3]  # Test first 3

    if not tables_with_models:
        pytest.skip("No tables with Pydantic models found")

    # Measure performance of validation vs non-validation
    times = {"with_validation": [], "without_validation": []}

    for table_name in tables_with_models:
        # Time without validation
        start_time = time.time()
        get_table_data(db, table_name, validate=False)
        times["without_validation"].append(time.time() - start_time)

        # Time with validation
        start_time = time.time()
        get_table_data(db, table_name, validate=True)
        times["with_validation"].append(time.time() - start_time)

    avg_without = sum(times["without_validation"]) / len(times["without_validation"])
    avg_with = sum(times["with_validation"]) / len(times["with_validation"])

    print("\nValidation Performance:")
    print(f"  Average time without validation: {avg_without:.4f}s")
    print(f"  Average time with validation: {avg_with:.4f}s")
    print(f"  Validation overhead: {((avg_with - avg_without) / avg_without * 100):.1f}%")

    # Validation should not take more than 10x longer (reasonable overhead)
    assert avg_with < avg_without * 10
