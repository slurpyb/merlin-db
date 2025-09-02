"""Test dump.py export functionality with real MDB data."""

import json
import logging
import tempfile
from pathlib import Path

import pytest
import yaml

# Suppress access-parser logging during tests
logging.getLogger("access_parser").setLevel(logging.ERROR)

from merlindb.exporters import CSVExporter, JSONExporter, YAMLExporter
from merlindb.utils import export_tables, get_database_info, get_exporter, select_tables

# Test data file in project root
TEST_DB_PATH = "test.mdb"


def test_get_database_info_success():
    """Test successful database loading and table retrieval."""
    db, tables = get_database_info(TEST_DB_PATH)

    assert db is not None
    assert isinstance(tables, list)
    assert len(tables) > 0
    assert "GeniSysObjects" in tables


def test_get_database_info_invalid_file():
    """Test error handling for invalid database file."""
    with pytest.raises(ValueError, match="Failed to load database"):
        get_database_info("nonexistent.mdb")


def test_get_exporter_all_formats():
    """Test getting exporters for all supported formats."""
    db, _ = get_database_info(TEST_DB_PATH)

    # Test JSON exporter
    json_exporter = get_exporter(db, "json")
    assert isinstance(json_exporter, JSONExporter)
    assert json_exporter.get_file_extension() == ".json"
    assert json_exporter.get_format_name() == "JSON"

    # Test YAML exporter
    yaml_exporter = get_exporter(db, "yaml")
    assert isinstance(yaml_exporter, YAMLExporter)
    assert yaml_exporter.get_file_extension() == ".yaml"
    assert yaml_exporter.get_format_name() == "YAML"

    # Test CSV exporter
    csv_exporter = get_exporter(db, "csv")
    assert isinstance(csv_exporter, CSVExporter)
    assert csv_exporter.get_file_extension() == ".csv"
    assert csv_exporter.get_format_name() == "CSV"


def test_get_exporter_case_insensitive():
    """Test that exporter format matching is case-insensitive."""
    db, _ = get_database_info(TEST_DB_PATH)

    # Test uppercase formats
    json_exporter = get_exporter(db, "JSON")
    assert isinstance(json_exporter, JSONExporter)

    yaml_exporter = get_exporter(db, "YAML")
    assert isinstance(yaml_exporter, YAMLExporter)

    csv_exporter = get_exporter(db, "CSV")
    assert isinstance(csv_exporter, CSVExporter)


def test_get_exporter_invalid_format():
    """Test error handling for unsupported export format."""
    db, _ = get_database_info(TEST_DB_PATH)

    with pytest.raises(ValueError, match="Unsupported format 'xml'"):
        get_exporter(db, "xml")


def test_select_tables_all():
    """Test selecting all tables when no patterns provided."""
    available_tables = ["Table1", "Table2", "Table3"]

    selected = select_tables(available_tables, None)
    assert selected == available_tables

    selected = select_tables(available_tables, [])
    assert selected == available_tables


def test_select_tables_exact_match():
    """Test exact table name matching."""
    available_tables = ["Config", "Events", "Buttons", "DeviceTypes"]

    selected = select_tables(available_tables, ["Config"])
    assert selected == ["Config"]

    selected = select_tables(available_tables, ["Config", "Events"])
    assert selected == ["Config", "Events"]


def test_select_tables_case_insensitive():
    """Test case-insensitive table matching."""
    available_tables = ["Config", "Events", "Buttons"]

    selected = select_tables(available_tables, ["config"])
    assert selected == ["Config"]

    selected = select_tables(available_tables, ["EVENTS"])
    assert selected == ["Events"]


def test_select_tables_wildcard_patterns():
    """Test wildcard pattern matching."""
    available_tables = ["GeniSysObjects", "GeniSysPanels", "GenisysZones", "Config", "Events"]

    # Match tables starting with "GeniSys"
    selected = select_tables(available_tables, ["GeniSys*"])
    assert "GeniSysObjects" in selected
    assert "GeniSysPanels" in selected
    assert "Config" not in selected

    # Match tables ending with "s"
    selected = select_tables(available_tables, ["*s"])
    assert "GeniSysObjects" in selected
    assert "Events" in selected


def test_select_tables_no_matches():
    """Test error handling when no tables match patterns."""
    available_tables = ["Config", "Events", "Buttons"]

    with pytest.raises(ValueError, match="No tables found matching patterns"):
        select_tables(available_tables, ["NonExistent"])


def test_export_tables_json_single_file():
    """Test dumping tables to single JSON file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.json"

        result = export_tables(
            TEST_DB_PATH, str(output_path), format_name="json", tables=["Config"], single_file=True
        )

        # Check result metadata
        assert result["format"] == "json"
        assert result["tables_exported"] == 1
        assert result["table_names"] == ["Config"]
        assert len(result["output_files"]) == 1
        assert str(output_path) in result["output_files"]

        # Check output file exists and contains valid JSON
        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert "tables" in data
            assert "Config" in data["tables"]


def test_export_tables_yaml_single_file():
    """Test dumping tables to single YAML file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.yaml"

        result = export_tables(
            TEST_DB_PATH, str(output_path), format_name="yaml", tables=["Config"], single_file=True
        )

        assert result["format"] == "yaml"
        assert output_path.exists()

        with open(output_path) as f:
            data = yaml.safe_load(f)
            assert isinstance(data, dict)
            assert "tables" in data
            assert "Config" in data["tables"]


def test_export_tables_csv_single_file():
    """Test dumping tables to single CSV file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.csv"

        result = export_tables(
            TEST_DB_PATH, str(output_path), format_name="csv", tables=["Config"], single_file=True
        )

        assert result["format"] == "csv"
        assert output_path.exists()

        # CSV should contain table data
        content = output_path.read_text()
        assert len(content) > 0


def test_export_tables_multiple_files():
    """Test dumping tables to separate files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.json"

        result = export_tables(
            TEST_DB_PATH,
            str(output_path),
            format_name="json",
            tables=["Config", "DeviceTypes"],
            single_file=False,
        )

        assert result["format"] == "json"
        assert result["tables_exported"] == 2
        assert len(result["output_files"]) == 2

        # Check that separate files were created
        config_file = Path(temp_dir) / "test_output_Config.json"
        devicetypes_file = Path(temp_dir) / "test_output_DeviceTypes.json"

        assert config_file.exists()
        assert devicetypes_file.exists()

        # Verify file contents
        with open(config_file) as f:
            config_data = json.load(f)
            assert isinstance(config_data, dict)

        with open(devicetypes_file) as f:
            devicetypes_data = json.load(f)
            assert isinstance(devicetypes_data, dict)


def test_export_tables_all_tables():
    """Test dumping all available tables."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "all_tables.json"

        result = export_tables(
            TEST_DB_PATH,
            str(output_path),
            format_name="json",
            tables=None,  # All tables
            single_file=True,
        )

        assert result["tables_exported"] > 10  # Should export many tables
        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert "tables" in data
            assert len(data["tables"]) == result["tables_exported"]


def test_export_tables_with_patterns():
    """Test dumping tables using wildcard patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "genisys_tables.json"

        result = export_tables(
            TEST_DB_PATH,
            str(output_path),
            format_name="json",
            tables=["GeniSys*"],  # All GeniSys tables
            single_file=True,
        )

        assert result["tables_exported"] > 0
        assert all("GeniSys" in table for table in result["table_names"])
        assert output_path.exists()


def test_export_tables_invalid_table():
    """Test error handling for invalid table names."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.json"

        with pytest.raises(ValueError, match="No tables found matching patterns"):
            export_tables(
                TEST_DB_PATH,
                str(output_path),
                format_name="json",
                tables=["NonExistentTable"],
                single_file=True,
            )


def test_export_tables_invalid_database():
    """Test error handling for invalid database file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.json"

        with pytest.raises(ValueError, match="Export failed"):
            export_tables(
                "nonexistent.mdb",
                str(output_path),
                format_name="json",
                tables=["Config"],
                single_file=True,
            )


def test_export_tables_backward_compatibility():
    """Test backward compatibility with mode parameter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_output.json"

        # Mode parameter should be ignored but not cause errors
        result = export_tables(
            TEST_DB_PATH,
            str(output_path),
            format_name="json",
            mode="raw",  # This should be ignored
            tables=["Config"],
            single_file=True,
        )

        assert result["format"] == "json"
        assert output_path.exists()


## Integration tests


def test_integration_export_formats():
    """Integration test: export same table in all formats."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        formats = ["json", "yaml", "csv"]
        table_name = "Config"

        for fmt in formats:
            output_file = temp_path / f"config.{fmt}"

            result = export_tables(
                TEST_DB_PATH,
                str(output_file),
                format_name=fmt,
                tables=[table_name],
                single_file=True,
            )

            assert result["format"] == fmt
            assert output_file.exists()
            assert output_file.stat().st_size > 0


def test_integration_large_export():
    """Integration test: export many tables to verify no memory issues."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "large_export.json"

        # Get first 10 tables for testing
        db, all_tables = get_database_info(TEST_DB_PATH)
        test_tables = all_tables[:10]

        result = export_tables(
            TEST_DB_PATH, str(output_path), format_name="json", tables=test_tables, single_file=True
        )

        assert result["tables_exported"] == len(test_tables)
        assert output_path.exists()

        # Verify all tables are in output
        with open(output_path) as f:
            data = json.load(f)
            assert "tables" in data
            for table in test_tables:
                assert table in data["tables"]
