from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from typing_extensions import override

from .base import DataExporter


class YAMLExporter(DataExporter):
    """YAML exporter for table data with single and multi-table support."""

    @override
    def get_file_extension(self) -> str:
        """Get the file extension for YAML format.

        Returns:
            File extension for YAML files
        """
        return ".yaml"

    @override
    def get_format_name(self) -> str:
        """Get the human-readable format name.

        Returns:
            Display name for YAML format
        """
        return "YAML"

    @override
    def export_single_table(self, table_name: str, output_path: Path) -> None:
        """Export a single table to a YAML file.

        Args:
            table_name: Name of the table to export
            output_path: Path where the YAML file should be written

        Raises:
            ValueError: If table_name is not available in the provider
            IOError: If file cannot be written
        """
        self.validate_tables([table_name])
        self.ensure_output_directory(output_path)

        table_data = self.get_table_data(table_name)

        # Convert table data to list of records for better YAML structure
        records = self._convert_to_records(table_data)

        export_data = {
            "table_name": table_name,
            "provider_mode": self.provider.get_mode_name(),
            "record_count": len(records),
            "columns": list(table_data.keys()) if table_data else [],
            "records": records,
        }

        with output_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                export_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
            )

    @override
    def export_multiple_tables(
        self, table_names: list[str], output_path: Path, single_file: bool = True
    ) -> None:
        """Export multiple tables to YAML file(s).

        Args:
            table_names: List of table names to export
            output_path: Base path for output files
            single_file: If True, combine all tables in one file. If False, create separate files.

        Raises:
            ValueError: If any table_name is not available in the provider
            IOError: If files cannot be written
        """
        self.validate_tables(table_names)

        if single_file:
            self._export_multiple_single_file(table_names, output_path)
        else:
            self._export_multiple_separate_files(table_names, output_path)

    def _export_multiple_single_file(self, table_names: list[str], output_path: Path) -> None:
        """Export multiple tables to a single YAML file."""
        self.ensure_output_directory(output_path)

        tables_data = {}
        total_records = 0

        for table_name in table_names:
            table_data = self.get_table_data(table_name)
            records = self._convert_to_records(table_data)
            tables_data[table_name] = {
                "columns": list(table_data.keys()) if table_data else [],
                "record_count": len(records),
                "records": records,
            }
            total_records += len(records)

        export_data = {
            "provider_mode": self.provider.get_mode_name(),
            "table_count": len(table_names),
            "total_records": total_records,
            "tables": tables_data,
        }

        with output_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                export_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
            )

    def _export_multiple_separate_files(self, table_names: list[str], output_path: Path) -> None:
        """Export multiple tables to separate YAML files."""
        base_path = output_path.with_suffix("")  # Remove extension

        for table_name in table_names:
            file_path = base_path.parent / f"{base_path.name}_{table_name}.yaml"
            self.export_single_table(table_name, file_path)

    def _convert_to_records(self, table_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert table data from column-oriented to record-oriented format.

        Args:
            table_data: Dictionary with column names as keys and lists of values

        Returns:
            List of dictionaries, each representing a record
        """
        if not table_data:
            return []

        columns = list(table_data.keys())
        if not columns:
            return []

        # Get the number of rows from the first column
        num_rows = len(table_data[columns[0]])

        records = []
        for i in range(num_rows):
            record = {}
            for column in columns:
                # Handle cases where columns might have different lengths
                if i < len(table_data[column]):
                    value = table_data[column][i]
                    record[column] = value if value is not None else None
                else:
                    record[column] = None
            records.append(record)

        return records
