from __future__ import annotations

from typing import Any

from .base import DataProvider


class DynaliteDataProvider(DataProvider):
    """Dynalite data provider that transforms MDB data into Dynalite-specific views.

    This provider parses the raw MDB data to present tables relevant to Dynalite
    lighting control systems including dimmers, modules, channels, areas, panels, and presets.
    """

    # Define the table structure that this provider will expose
    _DYNALITE_TABLES = {
        "dimmers_boxes": "Physical dimmer units and control boxes",
        "modules": "Dynalite network modules and their configurations",
        "physical_channels": "Physical channel assignments on modules",
        "logical_channels": "Logical channel mappings and groupings",
        "areas": "Lighting control areas and their configurations",
        "panels": "Control panels and their button mappings",
        "presets": "Lighting presets and their channel configurations",
    }

    def get_available_tables(self) -> list[str]:
        """Get list of Dynalite-specific table names.

        Returns:
            List of transformed table names for Dynalite view
        """
        return sorted(self._DYNALITE_TABLES.keys())

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get transformed Dynalite table data.

        Args:
            table_name: Name of the Dynalite table to retrieve

        Returns:
            Dictionary containing transformed table data

        Raises:
            ValueError: If table_name is not available in Dynalite mode
            NotImplementedError: Parser logic not yet implemented
        """
        if not self.supports_table(table_name):
            available = ", ".join(self.get_available_tables())
            raise ValueError(
                f"Dynalite table '{table_name}' not found. Available tables: {available}"
            )

        # TODO: Implement actual parsing logic for each table type
        raise NotImplementedError(
            f"Dynalite parser for table '{table_name}' not yet implemented. "
            f"This will parse raw MDB data into: {self._DYNALITE_TABLES[table_name]}"
        )

    def get_mode_name(self) -> str:
        """Get the display name for Dynalite mode.

        Returns:
            Human-readable name for this browsing mode
        """
        return "Dynalite"

    def get_mode_description(self) -> str:
        """Get description of what Dynalite mode shows.

        Returns:
            Description of Dynalite-specific browsing mode
        """
        return "Parsed view showing Dynalite lighting control components"

    def get_table_description(self, table_name: str) -> str:
        """Get description of what a specific Dynalite table contains.

        Args:
            table_name: Name of the table to describe

        Returns:
            Description of the table's contents

        Raises:
            ValueError: If table_name is not available in this mode
        """
        if not self.supports_table(table_name):
            available = ", ".join(self.get_available_tables())
            raise ValueError(
                f"Dynalite table '{table_name}' not found. Available tables: {available}"
            )

        return self._DYNALITE_TABLES[table_name]
