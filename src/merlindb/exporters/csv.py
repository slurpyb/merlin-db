from __future__ import annotations

from pathlib import Path

import pandas as pd
from typing_extensions import override

from .base import DataExporter


class CSVExporter(DataExporter):
    """CSV exporter for table data with single and multi-table support."""

    @override
    def get_file_extension(self) -> str:
        """Get the file extension for CSV format.

        Returns:
            File extension for CSV files
        """
        return ".csv"

    @override
    def get_format_name(self) -> str:
        """Get the human-readable format name.

        Returns:
            Display name for CSV format
        """
        return "CSV"

    @override
    def export_single_table(self, table_name: str, output_path: Path) -> None:
        """Export a single table to a CSV file.

        Args:
            table_name: Name of the table to export
            output_path: Path where the CSV file should be written

        Raises:
            ValueError: If table_name is not available in the provider
            IOError: If file cannot be written
        """
        self.validate_tables([table_name])
        self.ensure_output_directory(output_path)

        table_data = self.get_table_data(table_name)

        if not table_data:
            # Create empty CSV with headers
            pd.DataFrame().to_csv(output_path, index=False)
            return

        # Convert to pandas DataFrame for easy CSV export
        df = pd.DataFrame(table_data)

        # Write to CSV with UTF-8 encoding
        df.to_csv(output_path, index=False, encoding="utf-8")

    @override
    def export_multiple_tables(
        self, table_names: list[str], output_path: Path, single_file: bool = True
    ) -> None:
        """Export multiple tables to CSV file(s).

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
        """Export multiple tables to a single CSV file with table separators."""
        self.ensure_output_directory(output_path)

        combined_data = []

        for i, table_name in enumerate(table_names):
            table_data = self.get_table_data(table_name)

            if table_data:
                df = pd.DataFrame(table_data)

                # Add table identifier column
                df.insert(0, "table_name", table_name)
                combined_data.append(df)

            # Add separator row between tables (except for the last table)
            if i < len(table_names) - 1 and table_data:
                separator_data = {col: "---" for col in ["table_name"] + list(table_data.keys())}
                separator_df = pd.DataFrame([separator_data])
                combined_data.append(separator_df)

        if combined_data:
            final_df = pd.concat(combined_data, ignore_index=True)
            final_df.to_csv(output_path, index=False, encoding="utf-8")
        else:
            # Create empty CSV if no data
            pd.DataFrame().to_csv(output_path, index=False)

    def _export_multiple_separate_files(self, table_names: list[str], output_path: Path) -> None:
        """Export multiple tables to separate CSV files."""
        base_path = output_path.with_suffix("")  # Remove extension

        for table_name in table_names:
            file_path = base_path.parent / f"{base_path.name}_{table_name}.csv"
            self.export_single_table(table_name, file_path)
