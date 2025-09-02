"""Test the new comprehensive CLI interface."""

import logging
import tempfile
from pathlib import Path

# Suppress access-parser logging during tests
logging.getLogger("access_parser").setLevel(logging.ERROR)

from typer.testing import CliRunner

from merlindb.cli import app

# Test data file in project root
TEST_DB_PATH = "test.mdb"
runner = CliRunner()


class TestCLIHelp:
    """Test CLI help and version commands."""

    def test_main_help(self):
        """Test main CLI help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Parse and export Microsoft Access Database files" in result.stdout
        assert "info" in result.stdout
        assert "tables" in result.stdout
        assert "export" in result.stdout

    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "MerlinDB" in result.stdout
        assert "v1.0.0" in result.stdout

    def test_command_help(self):
        """Test individual command help."""
        commands = ["info", "tables", "inspect", "export", "validate"]

        for cmd in commands:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0
            assert "Examples:" in result.stdout


class TestInfoCommand:
    """Test the info command."""

    def test_info_basic(self):
        """Test basic info command."""
        result = runner.invoke(app, ["info", TEST_DB_PATH])
        assert result.exit_code == 0
        assert "MerlinDB Info" in result.stdout
        assert "Total Tables: 64" in result.stdout
        assert "Total Records: 2,512" in result.stdout

    def test_info_verbose(self):
        """Test verbose info command."""
        result = runner.invoke(app, ["info", TEST_DB_PATH, "--verbose"])
        assert result.exit_code == 0
        assert "Table Details:" in result.stdout
        assert "Config" in result.stdout
        assert "GeniSysButtonFunctions" in result.stdout  # This appears in first 20 tables

    def test_info_invalid_file(self):
        """Test info with invalid file."""
        result = runner.invoke(app, ["info", "nonexistent.mdb"])
        assert result.exit_code == 1
        assert "Error:" in result.stdout


class TestTablesCommand:
    """Test the tables command."""

    def test_tables_list_all(self):
        """Test listing all tables."""
        result = runner.invoke(app, ["tables", TEST_DB_PATH])
        assert result.exit_code == 0
        assert "Available Tables (64)" in result.stdout
        assert "Config" in result.stdout
        assert "GeniSysObjects" in result.stdout

    def test_tables_with_pattern(self):
        """Test table filtering with pattern."""
        result = runner.invoke(app, ["tables", TEST_DB_PATH, "--pattern", "GeniSys*"])
        assert result.exit_code == 0
        assert "Available Tables (3)" in result.stdout
        assert "GeniSysObjects" in result.stdout
        assert "Filtered by pattern: GeniSys*" in result.stdout

    def test_tables_with_info(self):
        """Test table listing with detailed info."""
        result = runner.invoke(app, ["tables", TEST_DB_PATH, "--info"])
        assert result.exit_code == 0
        assert "Table Name" in result.stdout
        assert "Records" in result.stdout
        assert "Columns" in result.stdout

    def test_tables_no_match_pattern(self):
        """Test pattern with no matches."""
        result = runner.invoke(app, ["tables", TEST_DB_PATH, "--pattern", "NonExistent*"])
        assert result.exit_code == 0
        assert "No tables match pattern" in result.stdout


class TestInspectCommand:
    """Test the inspect command."""

    def test_inspect_basic(self):
        """Test basic table inspection."""
        result = runner.invoke(app, ["inspect", TEST_DB_PATH, "Config"])
        assert result.exit_code == 0
        assert "Table: Config" in result.stdout
        assert "Records: 1" in result.stdout
        assert "Pydantic validation available" in result.stdout

    def test_inspect_with_validation(self):
        """Test inspection with validation."""
        result = runner.invoke(app, ["inspect", TEST_DB_PATH, "Config", "--validate"])
        assert result.exit_code == 0
        assert "Table: Config" in result.stdout

    def test_inspect_with_limit(self):
        """Test inspection with record limit."""
        result = runner.invoke(app, ["inspect", TEST_DB_PATH, "Config", "--limit", "5"])
        assert result.exit_code == 0
        assert "Sample Data" in result.stdout

    def test_inspect_invalid_table(self):
        """Test inspection with invalid table name."""
        result = runner.invoke(app, ["inspect", TEST_DB_PATH, "NonExistentTable"])
        assert result.exit_code == 1
        assert "Table 'NonExistentTable' not found" in result.stdout

    def test_inspect_suggestions(self):
        """Test inspection with similar table name suggestions."""
        result = runner.invoke(app, ["inspect", TEST_DB_PATH, "config"])  # lowercase
        assert result.exit_code == 1
        assert "Did you mean: Config" in result.stdout


class TestExportCommand:
    """Test the export command."""

    def test_export_json_single_table(self):
        """Test JSON export of single table."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.json"

            result = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--table", "Config"]
            )

            assert result.exit_code == 0
            assert "Export completed successfully!" in result.stdout
            assert "Format: JSON" in result.stdout
            assert "Tables exported: 1" in result.stdout
            assert output_file.exists()

    def test_export_yaml_multiple_tables(self):
        """Test YAML export of multiple tables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.yaml"

            result = runner.invoke(
                app,
                [
                    "export",
                    TEST_DB_PATH,
                    str(output_file),
                    "--format",
                    "yaml",
                    "--table",
                    "Config",
                    "--table",
                    "DeviceTypes",
                ],
            )

            assert result.exit_code == 0
            assert "Format: YAML" in result.stdout
            assert "Tables exported: 2" in result.stdout

    def test_export_csv_separate_files(self):
        """Test CSV export to separate files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.csv"

            result = runner.invoke(
                app,
                [
                    "export",
                    TEST_DB_PATH,
                    str(output_file),
                    "--format",
                    "csv",
                    "--table",
                    "Config",
                    "--table",
                    "DeviceTypes",
                    "--separate",
                ],
            )

            assert result.exit_code == 0
            assert "Format: CSV" in result.stdout
            assert "Tables exported: 2" in result.stdout

    def test_export_with_validation(self):
        """Test export with Pydantic validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "validated.json"

            result = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--table", "Config", "--validate"]
            )

            assert result.exit_code == 0
            assert "Export completed successfully!" in result.stdout

    def test_export_wildcards(self):
        """Test export with wildcard patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "genisys.json"

            result = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--table", "GeniSys*"]
            )

            assert result.exit_code == 0
            assert "Tables exported: 3" in result.stdout

    def test_export_all_tables(self):
        """Test export of all tables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "all.json"

            result = runner.invoke(app, ["export", TEST_DB_PATH, str(output_file)])

            assert result.exit_code == 0
            assert "Tables exported: 64" in result.stdout

    def test_export_invalid_format(self):
        """Test export with invalid format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test.xml"

            result = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--format", "xml"]
            )

            assert result.exit_code == 1
            assert "Export failed:" in result.stdout


class TestValidateCommand:
    """Test the validate command."""

    def test_validate_all_tables(self):
        """Test validation of all tables."""
        result = runner.invoke(app, ["validate", TEST_DB_PATH])
        assert result.exit_code == 0
        assert "Validation Results:" in result.stdout
        assert "Config:" in result.stdout

    def test_validate_specific_table(self):
        """Test validation of specific table."""
        result = runner.invoke(app, ["validate", TEST_DB_PATH, "--table", "Config"])
        assert result.exit_code == 0
        assert "Config:" in result.stdout

    def test_validate_summary_only(self):
        """Test validation summary."""
        result = runner.invoke(app, ["validate", TEST_DB_PATH, "--summary"])
        assert result.exit_code == 0
        assert "Validation Summary" in result.stdout
        assert "Validated Successfully:" in result.stdout
        assert "63 tables" in result.stdout

    def test_validate_invalid_table(self):
        """Test validation with invalid table."""
        result = runner.invoke(app, ["validate", TEST_DB_PATH, "--table", "NonExistent"])
        assert result.exit_code == 0  # Should continue with warning
        assert "Table 'NonExistent' not found" in result.stdout


class TestErrorHandling:
    """Test CLI error handling."""

    def test_invalid_database_file(self):
        """Test commands with invalid database file."""
        commands_to_test = [
            ["info", "nonexistent.mdb"],
            ["tables", "nonexistent.mdb"],
            ["inspect", "nonexistent.mdb", "Config"],
            ["validate", "nonexistent.mdb"],
        ]

        for cmd in commands_to_test:
            result = runner.invoke(app, cmd)
            assert result.exit_code == 1
            assert "Error:" in result.stdout

    def test_missing_arguments(self):
        """Test commands with missing required arguments."""
        # Missing database file
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 2  # Typer exit code for missing argument

        # Missing table name for inspect
        result = runner.invoke(app, ["inspect", TEST_DB_PATH])
        assert result.exit_code == 2

        # Missing output file for export
        result = runner.invoke(app, ["export", TEST_DB_PATH])
        assert result.exit_code == 2


class TestIntegration:
    """Integration tests combining multiple CLI operations."""

    def test_workflow_inspect_then_export(self):
        """Test workflow: inspect table then export it."""
        # First inspect
        result1 = runner.invoke(app, ["inspect", TEST_DB_PATH, "Config", "--limit", "0"])
        assert result1.exit_code == 0
        assert "Table: Config" in result1.stdout

        # Then export based on inspection
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "config.json"

            result2 = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--table", "Config"]
            )

            assert result2.exit_code == 0
            assert output_file.exists()

    def test_workflow_validate_then_export_with_validation(self):
        """Test workflow: validate table then export with validation."""
        # First validate
        result1 = runner.invoke(app, ["validate", TEST_DB_PATH, "--table", "Config"])
        assert result1.exit_code == 0
        assert "Config:" in result1.stdout

        # Then export with validation
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "validated_config.json"

            result2 = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--table", "Config", "--validate"]
            )

            assert result2.exit_code == 0
            assert output_file.exists()

    def test_workflow_info_tables_export(self):
        """Test workflow: get info, list tables, then export filtered tables."""
        # Get info
        result1 = runner.invoke(app, ["info", TEST_DB_PATH])
        assert result1.exit_code == 0

        # List filtered tables
        result2 = runner.invoke(app, ["tables", TEST_DB_PATH, "--pattern", "GeniSys*"])
        assert result2.exit_code == 0

        # Export filtered tables
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "genisys_export.json"

            result3 = runner.invoke(
                app, ["export", TEST_DB_PATH, str(output_file), "--table", "GeniSys*"]
            )

            assert result3.exit_code == 0
            assert output_file.exists()


class TestOutputFormatting:
    """Test CLI output formatting and styling."""

    def test_rich_formatting_in_output(self):
        """Test that Rich formatting works correctly."""
        result = runner.invoke(app, ["info", TEST_DB_PATH])
        assert result.exit_code == 0
        # Rich formatting should be present but we can't test exact formatting
        # Just ensure no errors and key content is there
        assert "MerlinDB Info" in result.stdout
        assert "📁" in result.stdout or "File:" in result.stdout  # Emojis may not render in tests

    def test_table_formatting(self):
        """Test table formatting in verbose output."""
        result = runner.invoke(app, ["tables", TEST_DB_PATH, "--info"])
        assert result.exit_code == 0
        # Should contain table headers
        assert "Table Name" in result.stdout
        assert "Records" in result.stdout
