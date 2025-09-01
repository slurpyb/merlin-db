from __future__ import annotations

from typing import Any

from .base import DataProvider


class RawDataProvider(DataProvider):
    """Raw data provider that shows the MDB database tables as-is without transformation."""

    def get_available_tables(self) -> list[str]:
        """Get list of all tables directly from the MDB database.

        Returns:
            List of table names from the database catalog
        """
        return sorted(list(self.db.catalog.keys()))  # pyright: ignore

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get raw table data directly from the MDB database.

        Args:
            table_name: Name of the table to retrieve from the database

        Returns:
            Dictionary containing raw table data with column names as keys

        Raises:
            ValueError: If table_name doesn't exist in the database
        """
        if not self.supports_table(table_name):
            available = ", ".join(self.get_available_tables())
            raise ValueError(f"Table '{table_name}' not found. Available tables: {available}")

        try:
            return self.db.parse_table(table_name)  # pyright: ignore
        except Exception as e:
            raise ValueError(f"Failed to parse table '{table_name}': {e}") from e

    def get_mode_name(self) -> str:
        """Get the display name for raw mode.

        Returns:
            Human-readable name for this browsing mode
        """
        return "Raw"

    def get_mode_description(self) -> str:
        """Get description of what raw mode shows.

        Returns:
            Description of raw database browsing mode
        """
        return "Direct view of MDB database tables without transformation"
