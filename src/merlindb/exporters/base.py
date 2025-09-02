from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Protocol


class DataProvider(Protocol):
    """Protocol for data providers to ensure compatibility."""

    def get_available_tables(self) -> list[str]:
        """Get list of available table names."""
        ...

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get data for a specific table."""
        ...


class DataExporter(ABC):
    """Abstract base class for data exporters that write table data to files."""

    def __init__(self, provider: DataProvider) -> None:
        """Initialize the exporter with a data provider.

        Args:
            provider: DataProvider instance to source data from
        """
        self.provider = provider

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this export format.

        Returns:
            File extension including the dot (e.g., '.json', '.csv')
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Get the human-readable format name.

        Returns:
            Display name for this export format
        """
        pass

    @abstractmethod
    def export_single_table(self, table_name: str, output_path: Path) -> None:
        """Export a single table to a file.

        Args:
            table_name: Name of the table to export
            output_path: Path where the file should be written

        Raises:
            ValueError: If table_name is not available in the provider
            IOError: If file cannot be written
        """
        pass

    @abstractmethod
    def export_multiple_tables(
        self, table_names: list[str], output_path: Path, single_file: bool = True
    ) -> None:
        """Export multiple tables to file(s).

        Args:
            table_names: List of table names to export
            output_path: Base path for output files
            single_file: If True, combine all tables in one file. If False, create separate files.

        Raises:
            ValueError: If any table_name is not available in the provider
            IOError: If files cannot be written
        """
        pass

    def get_available_tables(self) -> list[str]:
        """Get list of available tables from the data provider.

        Returns:
            List of table names that can be exported
        """
        return self.provider.get_available_tables()

    def validate_tables(self, table_names: list[str]) -> None:
        """Validate that all specified tables are available.

        Args:
            table_names: List of table names to validate

        Raises:
            ValueError: If any table is not available
        """
        available = set(self.get_available_tables())
        invalid = [name for name in table_names if name not in available]
        if invalid:
            available_str = ", ".join(sorted(available))
            invalid_str = ", ".join(invalid)
            raise ValueError(
                f"Invalid table names: {invalid_str}. Available tables: {available_str}"
            )

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get data for a specific table.

        Args:
            table_name: Name of the table to retrieve

        Returns:
            Dictionary containing table data
        """
        return self.provider.get_table_data(table_name)

    def ensure_output_directory(self, output_path: Path) -> None:
        """Ensure the output directory exists.

        Args:
            output_path: Path to check/create directory for
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
