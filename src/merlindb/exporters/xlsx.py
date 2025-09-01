from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from typing_extensions import override

from .base import DataExporter


class XLSXExporter(DataExporter):
    """XLSX exporter for table data with worksheet support for multiple tables."""

    @override
    def get_file_extension(self) -> str:
        """Get the file extension for XLSX format.

        Returns:
            File extension for Excel files
        """
        return ".xlsx"

    @override
    def get_format_name(self) -> str:
        """Get the human-readable format name.

        Returns:
            Display name for XLSX format
        """
        return "Excel (XLSX)"

    @override
    def export_single_table(self, table_name: str, output_path: Path) -> None:
        """Export a single table to an XLSX file.

        Args:
            table_name: Name of the table to export
            output_path: Path where the XLSX file should be written

        Raises:
            ValueError: If table_name is not available in the provider
            IOError: If file cannot be written
        """
        self.validate_tables([table_name])
        self.ensure_output_directory(output_path)

        table_data = self.get_table_data(table_name)

        if not table_data:
            print("No data found for table:", table_name)
            # Create empty Excel file with one worksheet
            with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
                pd.DataFrame().to_excel(writer, sheet_name=table_name[:31], index=False)
            return

        # Convert to pandas DataFrame
        df = pd.DataFrame(table_data)

        # Create Excel file with single worksheet
        # Truncate sheet name to 31 characters (Excel limitation)
        sheet_name = table_name[:31]

        with pd.ExcelWriter(output_path, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Auto-adjust column widths for better readability
            worksheet = writer.sheets[sheet_name]
            self._auto_adjust_columns(worksheet, df)

    @override
    def export_multiple_tables(
        self, table_names: list[str], output_path: Path, single_file: bool = True
    ) -> None:
        """Export multiple tables to XLSX file(s).

        Args:
            table_names: List of table names to export
            output_path: Base path for output files
            single_file: If True, create one file with multiple worksheets.
                        If False, create separate XLSX files.

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
        """Export multiple tables to a single XLSX file with separate worksheets."""
        self.ensure_output_directory(output_path)

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for table_name in table_names:
                table_data = self.get_table_data(table_name)

                # Truncate sheet name to 31 characters (Excel limitation)
                sheet_name = table_name[:31]

                if table_data:
                    df = pd.DataFrame(table_data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Auto-adjust column widths
                    worksheet = writer.sheets[sheet_name]
                    self._auto_adjust_columns(worksheet, df)
                else:
                    # Create empty worksheet for tables with no data
                    pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)

    def _export_multiple_separate_files(self, table_names: list[str], output_path: Path) -> None:
        """Export multiple tables to separate XLSX files."""
        base_path = output_path.with_suffix("")  # Remove extension

        for table_name in table_names:
            file_path = base_path.parent / f"{base_path.name}_{table_name}.xlsx"
            self.export_single_table(table_name, file_path)

    def _auto_adjust_columns(self, worksheet: Any, df: pd.DataFrame) -> None:
        """Auto-adjust column widths based on content length.

        Args:
            worksheet: openpyxl worksheet object
            df: pandas DataFrame with the data
        """
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            # Check header length
            if len(df.columns) > 0:
                header_idx = column[0].column - 1
                if header_idx < len(df.columns):
                    header_length = len(str(df.columns[header_idx]))
                    max_length = max(max_length, header_length)

            # Check data lengths
            for cell in column:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            # Set column width with some padding, but cap at reasonable maximum
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
