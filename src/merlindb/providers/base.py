from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from access_parser import AccessParser


class DataProvider(ABC):
    """Abstract base class for data providers that transform MDB data for different browsing modes."""

    def __init__(self, db: AccessParser) -> None:
        """Initialize the data provider with a database connection.

        Args:
            db: AccessParser instance for the MDB database
        """
        self.db = db

    @abstractmethod
    def get_available_tables(self) -> list[str]:
        """Get list of available table names for this browsing mode.

        Returns:
            List of table names that can be browsed in this mode
        """
        pass

    @abstractmethod
    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get data for a specific table in this browsing mode.

        Args:
            table_name: Name of the table to retrieve

        Returns:
            Dictionary containing table data with column names as keys
            and lists of values as values

        Raises:
            ValueError: If table_name is not available in this mode
        """
        pass

    @abstractmethod
    def get_mode_name(self) -> str:
        """Get the human-readable name of this browsing mode.

        Returns:
            Display name for this browsing mode
        """
        pass

    @abstractmethod
    def get_mode_description(self) -> str:
        """Get a description of what this browsing mode shows.

        Returns:
            Brief description of the data this mode provides
        """
        pass

    def supports_table(self, table_name: str) -> bool:
        """Check if this provider supports a given table.

        Args:
            table_name: Name of the table to check

        Returns:
            True if the table is available in this mode
        """
        return table_name in self.get_available_tables()
