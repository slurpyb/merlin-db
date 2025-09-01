from __future__ import annotations

from typing import Any

from .base import DataProvider


class DeviceDataProvider(DataProvider):
    """Device data provider that transforms MDB data into user-friendly device views.

    This provider presents the database as logical devices that users interact with,
    such as lights, fans, curtains, and other controllable objects, abstracting away
    the technical Dynalite implementation details.
    """

    # Define the device-centric table structure that this provider will expose
    _DEVICE_TABLES = {
        "lights": "All lighting devices including dimmable and switch-only lights",
        "fans": "Ceiling fans and ventilation devices with speed control",
        "curtains": "Motorized curtains, blinds, and window coverings",
        "scenes": "User-defined lighting and device scenes/moods",
        "rooms": "Room-based device groupings and control",
        "schedules": "Time-based automation and scheduling",
        "sensors": "Motion sensors, daylight sensors, and other inputs",
        "controllers": "Physical control interfaces (wall panels, remotes)",
    }

    def get_available_tables(self) -> list[str]:
        """Get list of device-centric table names.

        Returns:
            List of device table names for user-friendly view
        """
        return sorted(self._DEVICE_TABLES.keys())

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get transformed device table data.

        Args:
            table_name: Name of the device table to retrieve

        Returns:
            Dictionary containing device-oriented table data

        Raises:
            ValueError: If table_name is not available in Device mode
            NotImplementedError: Parser logic not yet implemented
        """
        if not self.supports_table(table_name):
            available = ", ".join(self.get_available_tables())
            raise ValueError(
                f"Device table '{table_name}' not found. Available tables: {available}"
            )

        # TODO: Implement actual device parsing logic for each table type
        raise NotImplementedError(
            f"Device parser for table '{table_name}' not yet implemented. "
            f"This will parse raw MDB data into: {self._DEVICE_TABLES[table_name]}"
        )

    def get_mode_name(self) -> str:
        """Get the display name for Device mode.

        Returns:
            Human-readable name for this browsing mode
        """
        return "Device"

    def get_mode_description(self) -> str:
        """Get description of what Device mode shows.

        Returns:
            Description of device-centric browsing mode
        """
        return "User-friendly view of controllable devices and automation"

    def get_table_description(self, table_name: str) -> str:
        """Get description of what a specific device table contains.

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
                f"Device table '{table_name}' not found. Available tables: {available}"
            )

        return self._DEVICE_TABLES[table_name]
