"""Test the programmatic Python API interface."""

import json
import logging
import tempfile
from pathlib import Path

import pytest
import yaml

# Suppress access-parser logging during tests
logging.getLogger("access_parser").setLevel(logging.ERROR)

from merlindb import (
    MerlinDB,
    get_database_info,
    list_tables,
    load_database,
    quick_export,
)

# Test data file in project root
TEST_DB_PATH = "test.mdb"


class TestMerlinDBClass:
    """Test the main MerlinDB class."""

    def test_initialization_success(self):
        """Test successful database initialization."""
        db = MerlinDB(TEST_DB_PATH)
        assert db.file_path == TEST_DB_PATH
        assert db._db is not None

        # Test with Path object
        db2 = MerlinDB(Path(TEST_DB_PATH))
        assert db2.file_path == TEST_DB_PATH

    def test_initialization_file_not_found(self):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError, match="MDB file not found"):
            MerlinDB("nonexistent.mdb")

    def test_initialization_invalid_file(self):
        """Test initialization with invalid MDB file."""
        with tempfile.NamedTemporaryFile(suffix=".mdb", delete=False) as temp_file:
            temp_file.write(b"invalid content")
            temp_file.flush()

            with pytest.raises(ValueError, match="Failed to load MDB file"):
                MerlinDB(temp_file.name)

            Path(temp_file.name).unlink()

    def test_list_tables(self):
        """Test listing available tables."""
        db = MerlinDB(TEST_DB_PATH)
        tables = db.list_tables()

        assert isinstance(tables, list)
        assert len(tables) > 0
        assert "Config" in tables
        assert "GeniSysObjects" in tables
        assert tables == sorted(tables)  # Should be sorted

        # Should return a copy, not reference
        tables2 = db.list_tables()
        assert tables == tables2
        assert tables is not tables2

    def test_get_table_success(self):
        """Test getting table data successfully."""
        db = MerlinDB(TEST_DB_PATH)

        # Test without validation
        config_data = db.get_table("Config")
        assert isinstance(config_data, dict)
        assert len(config_data) > 0

        # Test with validation
        config_validated = db.get_table("Config", validate=True)
        assert isinstance(config_validated, dict)
        assert set(config_data.keys()) == set(config_validated.keys())

    def test_get_table_invalid_table(self):
        """Test error handling for invalid table names."""
        db = MerlinDB(TEST_DB_PATH)

        with pytest.raises(ValueError, match="Table 'NonExistentTable' not found"):
            db.get_table("NonExistentTable")

    def test_table_exists(self):
        """Test table existence checking."""
        db = MerlinDB(TEST_DB_PATH)

        assert db.table_exists("Config") is True
        assert db.table_exists("GeniSysObjects") is True
        assert db.table_exists("NonExistentTable") is False

    def test_get_table_info(self):
        """Test getting table metadata."""
        db = MerlinDB(TEST_DB_PATH)

        info = db.get_table_info("Config")
        assert isinstance(info, dict)
        assert info["name"] == "Config"
        assert isinstance(info["columns"], list)
        assert isinstance(info["column_count"], int)
        assert isinstance(info["record_count"], int)
        assert isinstance(info["has_pydantic_model"], bool)
        assert info["column_count"] == len(info["columns"])

    def test_get_table_info_invalid_table(self):
        """Test table info for non-existent table."""
        db = MerlinDB(TEST_DB_PATH)

        with pytest.raises(ValueError, match="Table 'NonExistentTable' not found"):
            db.get_table_info("NonExistentTable")

    def test_get_database_summary(self):
        """Test getting database summary."""
        db = MerlinDB(TEST_DB_PATH)
        summary = db.get_database_summary()

        assert isinstance(summary, dict)
        assert summary["file_path"] == TEST_DB_PATH
        assert isinstance(summary["total_tables"], int)
        assert isinstance(summary["tables_with_data"], int)
        assert isinstance(summary["tables_with_models"], int)
        assert isinstance(summary["total_records"], int)
        assert isinstance(summary["model_coverage"], str)

        assert summary["total_tables"] > 0
        assert summary["total_records"] > 0
        assert "%" in summary["model_coverage"]

    def test_export_json(self):
        """Test JSON export functionality."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.json"

            result = db.export_json(output_file, tables=["Config"])

            assert result["format"] == "json"
            assert result["tables_exported"] == 1
            assert "Config" in result["table_names"]
            assert output_file.exists()

            # Verify JSON content
            with open(output_file) as f:
                data = json.load(f)
                assert "tables" in data
                assert "Config" in data["tables"]

    def test_export_yaml(self):
        """Test YAML export functionality."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.yaml"

            result = db.export_yaml(output_file, tables=["Config"])

            assert result["format"] == "yaml"
            assert result["tables_exported"] == 1
            assert output_file.exists()

            # Verify YAML content
            with open(output_file) as f:
                data = yaml.safe_load(f)
                assert "tables" in data
                assert "Config" in data["tables"]

    def test_export_csv(self):
        """Test CSV export functionality."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.csv"

            result = db.export_csv(output_file, tables=["Config"])

            assert result["format"] == "csv"
            assert result["tables_exported"] == 1
            assert output_file.exists()

            # Verify CSV content
            content = output_file.read_text()
            assert len(content) > 0

    def test_export_generic(self):
        """Test generic export method."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test different formats
            for format_name, extension in [("json", ".json"), ("yaml", ".yaml"), ("csv", ".csv")]:
                output_file = Path(temp_dir) / f"test{extension}"

                result = db.export(output_file, format=format_name, tables=["Config"])

                assert result["format"] == format_name
                assert result["tables_exported"] == 1
                assert output_file.exists()

    def test_export_separate_files(self):
        """Test export with separate files."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.json"

            result = db.export_json(
                output_file, tables=["Config", "DeviceTypes"], separate_files=True
            )

            assert result["tables_exported"] == 2
            assert len(result["output_files"]) == 2

            # Check separate files exist
            config_file = Path(temp_dir) / "test_Config.json"
            device_types_file = Path(temp_dir) / "test_DeviceTypes.json"
            assert config_file.exists()
            assert device_types_file.exists()

    def test_export_with_wildcards(self):
        """Test export with wildcard patterns."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "genisys.json"

            result = db.export_json(output_file, tables=["GeniSys*"])

            assert result["tables_exported"] > 0
            for table_name in result["table_names"]:
                assert table_name.startswith("GeniSys")

    def test_context_manager(self):
        """Test context manager functionality."""
        with MerlinDB(TEST_DB_PATH) as db:
            tables = db.list_tables()
            assert len(tables) > 0

            data = db.get_table("Config")
            assert isinstance(data, dict)

    def test_repr(self):
        """Test string representation."""
        db = MerlinDB(TEST_DB_PATH)
        repr_str = repr(db)

        assert "MerlinDB" in repr_str
        assert TEST_DB_PATH in repr_str
        assert "tables" in repr_str


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_load_database(self):
        """Test load_database convenience function."""
        db = load_database(TEST_DB_PATH)
        assert isinstance(db, MerlinDB)
        assert db.file_path == TEST_DB_PATH

        # Test with Path object
        db2 = load_database(Path(TEST_DB_PATH))
        assert isinstance(db2, MerlinDB)

    def test_list_tables_function(self):
        """Test list_tables convenience function."""
        tables = list_tables(TEST_DB_PATH)

        assert isinstance(tables, list)
        assert len(tables) > 0
        assert "Config" in tables

    def test_get_database_info_function(self):
        """Test get_database_info convenience function."""
        info = get_database_info(TEST_DB_PATH)

        assert isinstance(info, dict)
        assert "total_tables" in info
        assert "total_records" in info
        assert info["file_path"] == TEST_DB_PATH

    def test_quick_export(self):
        """Test quick_export convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "quick.json"

            result = quick_export(TEST_DB_PATH, output_file, format="json", tables=["Config"])

            assert result["format"] == "json"
            assert result["tables_exported"] == 1
            assert output_file.exists()

    def test_quick_export_all_formats(self):
        """Test quick_export with all formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            for format_name, extension in [("json", ".json"), ("yaml", ".yaml"), ("csv", ".csv")]:
                output_file = Path(temp_dir) / f"quick{extension}"

                result = quick_export(
                    TEST_DB_PATH, output_file, format=format_name, tables=["Config"]
                )

                assert result["format"] == format_name
                assert output_file.exists()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_export_format(self):
        """Test error handling for invalid export format."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.xml"

            with pytest.raises(ValueError, match="Unsupported format"):
                db.export(output_file, format="xml")

    def test_invalid_table_patterns(self):
        """Test error handling for invalid table patterns."""
        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.json"

            with pytest.raises(ValueError, match="No tables found matching patterns"):
                db.export_json(output_file, tables=["NonExistentPattern*"])

    def test_permission_errors(self):
        """Test handling of permission errors."""
        db = MerlinDB(TEST_DB_PATH)

        # Try to write to root directory (should fail on most systems)
        with pytest.raises((PermissionError, OSError)):
            db.export_json("/root/test.json", tables=["Config"])


class TestIntegration:
    """Integration tests combining multiple API features."""

    def test_full_workflow(self):
        """Test complete workflow: load -> inspect -> export."""
        # Load database
        db = load_database(TEST_DB_PATH)

        # Get summary
        summary = db.get_database_summary()
        assert summary["total_tables"] > 0

        # List tables
        tables = db.list_tables()
        assert len(tables) == summary["total_tables"]

        # Get specific table info
        if "Config" in tables:
            info = db.get_table_info("Config")
            assert info["name"] == "Config"

        # Export to all formats
        with tempfile.TemporaryDirectory() as temp_dir:
            for fmt in ["json", "yaml", "csv"]:
                output_file = Path(temp_dir) / f"export.{fmt}"
                result = db.export(output_file, format=fmt, tables=["Config"])
                assert result["format"] == fmt
                assert output_file.exists()

    def test_data_consistency(self):
        """Test data consistency across different access methods."""
        db = MerlinDB(TEST_DB_PATH)

        # Get data through different methods
        raw_data = db.get_table("Config", validate=False)
        validated_data = db.get_table("Config", validate=True)

        # Should have same structure
        assert set(raw_data.keys()) == set(validated_data.keys())

        # Export and re-import to verify consistency
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "test.json"

            # Export
            result = db.export_json(json_file, tables=["Config"])
            assert result["tables_exported"] == 1

            # Read back
            with open(json_file) as f:
                exported_data = json.load(f)

            assert "tables" in exported_data
            assert "Config" in exported_data["tables"]

            # Compare structure
            config_export = exported_data["tables"]["Config"]
            assert "columns" in config_export
            assert "records" in config_export
            assert set(config_export["columns"]) == set(raw_data.keys())

    def test_large_dataset_handling(self):
        """Test handling of larger datasets."""
        db = MerlinDB(TEST_DB_PATH)

        # Find table with most data
        tables_info = {}
        for table in db.list_tables()[:10]:  # Test first 10 tables
            try:
                info = db.get_table_info(table)
                tables_info[table] = info["record_count"]
            except Exception:
                continue

        if tables_info:
            largest_table = max(tables_info.keys(), key=lambda t: tables_info[t])

            # Test with largest table
            data = db.get_table(largest_table)
            assert isinstance(data, dict)

            # Export largest table
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = Path(temp_dir) / "large.json"
                result = db.export_json(output_file, tables=[largest_table])
                assert result["tables_exported"] == 1
                assert output_file.exists()

    def test_batch_processing_simulation(self):
        """Test batch processing simulation."""
        # Simulate processing multiple MDB files
        test_files = [TEST_DB_PATH]  # In real scenario, would be multiple files

        results = []
        for file_path in test_files:
            try:
                with load_database(file_path) as db:
                    summary = db.get_database_summary()

                    # Process each database
                    with tempfile.TemporaryDirectory() as temp_dir:
                        output_file = Path(temp_dir) / f"{Path(file_path).stem}.json"
                        db.export_json(output_file)

                        results.append(
                            {
                                "file": file_path,
                                "tables": summary["total_tables"],
                                "records": summary["total_records"],
                                "export_status": "success",
                            }
                        )

            except Exception as e:
                results.append({"file": file_path, "error": str(e), "export_status": "failed"})

        assert len(results) == len(test_files)
        assert all(r["export_status"] == "success" for r in results)


class TestPerformance:
    """Basic performance tests."""

    def test_initialization_performance(self):
        """Test that initialization is reasonably fast."""
        import time

        start_time = time.time()
        db = MerlinDB(TEST_DB_PATH)
        initialization_time = time.time() - start_time

        # Should initialize within reasonable time
        assert initialization_time < 5.0  # 5 seconds max

        # Subsequent operations should be fast
        start_time = time.time()
        tables = db.list_tables()
        list_time = time.time() - start_time

        assert list_time < 1.0  # 1 second max
        assert len(tables) > 0

    def test_export_performance(self):
        """Test export performance."""
        import time

        db = MerlinDB(TEST_DB_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "perf_test.json"

            start_time = time.time()
            result = db.export_json(output_file, tables=["Config", "DeviceTypes", "Events"])
            export_time = time.time() - start_time

            # Should complete within reasonable time
            assert export_time < 10.0  # 10 seconds max
            assert result["tables_exported"] == 3
