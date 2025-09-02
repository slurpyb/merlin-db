"""Programmatic API for MerlinDB - Clean interface for Python applications."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .parser import get_available_tables, get_mdb, get_table_data
from .utils import export_tables as dump_tables


class MerlinDB:
    """Main interface for programmatic access to MDB files.

    Provides a clean, object-oriented interface for loading, querying,
    and exporting Microsoft Access Database files used by GeniSys software.

    Examples:
        # Basic usage
        db = MerlinDB("database.mdb")
        tables = db.list_tables()
        data = db.get_table("Config")

        # Export to different formats
        db.export_json("output.json")
        db.export_yaml("output.yaml", tables=["Config", "Events"])
        db.export_csv("output.csv", separate_files=True)

        # With validation
        validated_data = db.get_table("Config", validate=True)
    """

    def __init__(self, file_path: str | Path):
        """Initialize MerlinDB with an MDB file.

        Args:
            file_path: Path to the MDB database file

        Raises:
            FileNotFoundError: If MDB file doesn't exist
            ValueError: If MDB file cannot be loaded
        """
        self.file_path = str(file_path)
        self._db = None
        self._available_tables = None

        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"MDB file not found: {file_path}")

        # Test loading the database
        self._db = get_mdb(self.file_path)
        if not self._db:
            raise ValueError(f"Failed to load MDB file: {file_path}")

    def list_tables(self) -> list[str]:
        """Get list of all available tables in the database.

        Returns:
            Sorted list of table names
        """
        if self._available_tables is None:
            self._available_tables = get_available_tables(self._db)
        return self._available_tables.copy()

    def get_table(self, table_name: str, validate: bool = False) -> dict[str, Any]:
        """Get data from a specific table.

        Args:
            table_name: Name of the table to retrieve
            validate: Whether to apply Pydantic validation to the data

        Returns:
            Dictionary with column names as keys and lists of values

        Raises:
            ValueError: If table doesn't exist or cannot be parsed

        Examples:
            # Get raw data
            config_data = db.get_table("Config")

            # Get validated data (if Pydantic model exists)
            config_data = db.get_table("Config", validate=True)
        """
        return get_table_data(self._db, table_name, validate=validate)

    def export_json(
        self, output_path: str | Path, tables: list[str] | None = None, separate_files: bool = False
    ) -> dict[str, Any]:
        """Export tables to JSON format.

        Args:
            output_path: Path for the output file(s)
            tables: List of table patterns to export (None for all tables)
            separate_files: Create separate files for each table

        Returns:
            Export result metadata

        Examples:
            # Export all tables to single JSON file
            result = db.export_json("all_data.json")

            # Export specific tables
            result = db.export_json("config.json", tables=["Config", "Events"])

            # Export to separate files
            result = db.export_json("data.json", separate_files=True)
        """
        return dump_tables(
            db_path=self.file_path,
            output_path=str(output_path),
            format_name="json",
            tables=tables,
            single_file=not separate_files,
        )

    def export_yaml(
        self, output_path: str | Path, tables: list[str] | None = None, separate_files: bool = False
    ) -> dict[str, Any]:
        """Export tables to YAML format.

        Args:
            output_path: Path for the output file(s)
            tables: List of table patterns to export (None for all tables)
            separate_files: Create separate files for each table

        Returns:
            Export result metadata

        Examples:
            # Export all tables to YAML
            result = db.export_yaml("data.yaml")

            # Export with wildcards
            result = db.export_yaml("genisys.yaml", tables=["GeniSys*"])
        """
        return dump_tables(
            db_path=self.file_path,
            output_path=str(output_path),
            format_name="yaml",
            tables=tables,
            single_file=not separate_files,
        )

    def export_csv(
        self, output_path: str | Path, tables: list[str] | None = None, separate_files: bool = False
    ) -> dict[str, Any]:
        """Export tables to CSV format.

        Args:
            output_path: Path for the output file(s)
            tables: List of table patterns to export (None for all tables)
            separate_files: Create separate files for each table

        Returns:
            Export result metadata

        Examples:
            # Export single table to CSV
            result = db.export_csv("config.csv", tables=["Config"])

            # Export all tables to separate CSV files
            result = db.export_csv("data.csv", separate_files=True)
        """
        return dump_tables(
            db_path=self.file_path,
            output_path=str(output_path),
            format_name="csv",
            tables=tables,
            single_file=not separate_files,
        )

    def export(
        self,
        output_path: str | Path,
        format: str = "json",
        tables: list[str] | None = None,
        separate_files: bool = False,
    ) -> dict[str, Any]:
        """Generic export method for any supported format.

        Args:
            output_path: Path for the output file(s)
            format: Export format ("json", "yaml", "csv")
            tables: List of table patterns to export (None for all tables)
            separate_files: Create separate files for each table

        Returns:
            Export result metadata

        Raises:
            ValueError: If format is not supported

        Examples:
            # Generic export
            result = db.export("data.json", format="json")
            result = db.export("data.yaml", format="yaml")
            result = db.export("data.csv", format="csv")
        """
        return dump_tables(
            db_path=self.file_path,
            output_path=str(output_path),
            format_name=format,
            tables=tables,
            single_file=not separate_files,
        )

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        return table_name in self.list_tables()

    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """Get metadata about a table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table metadata

        Raises:
            ValueError: If table doesn't exist
        """
        if not self.table_exists(table_name):
            available = ", ".join(self.list_tables())
            raise ValueError(f"Table '{table_name}' not found. Available: {available}")

        try:
            data = self.get_table(table_name, validate=False)
            columns = list(data.keys()) if data else []
            record_count = len(data[columns[0]]) if columns and data else 0

            return {
                "name": table_name,
                "columns": columns,
                "column_count": len(columns),
                "record_count": record_count,
                "has_pydantic_model": table_name in self._get_model_map(),
            }
        except Exception as e:
            return {
                "name": table_name,
                "error": str(e),
                "columns": [],
                "column_count": 0,
                "record_count": 0,
                "has_pydantic_model": False,
            }

    def get_database_summary(self) -> dict[str, Any]:
        """Get summary information about the entire database.

        Returns:
            Dictionary with database summary
        """
        tables = self.list_tables()
        total_records = 0
        tables_with_data = 0
        tables_with_models = 0

        model_map = self._get_model_map()

        for table_name in tables:
            try:
                data = self.get_table(table_name, validate=False)
                if data:
                    columns = list(data.keys())
                    if columns:
                        record_count = len(data[columns[0]])
                        total_records += record_count
                        if record_count > 0:
                            tables_with_data += 1

                if table_name in model_map:
                    tables_with_models += 1

            except Exception:
                # Skip tables that can't be read
                continue

        return {
            "file_path": self.file_path,
            "total_tables": len(tables),
            "tables_with_data": tables_with_data,
            "tables_with_models": tables_with_models,
            "total_records": total_records,
            "model_coverage": f"{(tables_with_models / len(tables) * 100):.1f}%"
            if tables
            else "0%",
        }

    def _get_model_map(self) -> dict[str, Any]:
        """Get the Pydantic model mapping (internal method)."""
        try:
            from .models.genisys import model_map

            return model_map
        except ImportError:
            return {}

    def __repr__(self) -> str:
        """String representation of the MerlinDB instance."""
        try:
            table_count = len(self.list_tables())
            return f"MerlinDB('{self.file_path}', {table_count} tables)"
        except Exception:
            return f"MerlinDB('{self.file_path}', error)"

    def __enter__(self) -> MerlinDB:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Clean up resources if needed
        pass


# Convenience functions for quick access
def load_database(file_path: str | Path) -> MerlinDB:
    """Load an MDB database file.

    Args:
        file_path: Path to the MDB file

    Returns:
        MerlinDB instance

    Example:
        db = load_database("database.mdb")
        tables = db.list_tables()
    """
    return MerlinDB(file_path)


def quick_export(
    mdb_file: str | Path,
    output_file: str | Path,
    format: str = "json",
    tables: list[str] | None = None,
) -> dict[str, Any]:
    """Quick export function for simple use cases.

    Args:
        mdb_file: Path to the MDB file
        output_file: Path for the output file
        format: Export format ("json", "yaml", "csv")
        tables: List of table patterns to export (None for all)

    Returns:
        Export result metadata

    Example:
        result = quick_export("database.mdb", "output.json", format="json")
        result = quick_export("database.mdb", "config.yaml", format="yaml", tables=["Config"])
    """
    with MerlinDB(mdb_file) as db:
        return db.export(output_file, format=format, tables=tables)


def list_tables(mdb_file: str | Path) -> list[str]:
    """Quick function to list tables in an MDB file.

    Args:
        mdb_file: Path to the MDB file

    Returns:
        List of table names

    Example:
        tables = list_tables("database.mdb")
        print(f"Found {len(tables)} tables")
    """
    with MerlinDB(mdb_file) as db:
        return db.list_tables()


def get_database_info(mdb_file: str | Path) -> dict[str, Any]:
    """Quick function to get database summary information.

    Args:
        mdb_file: Path to the MDB file

    Returns:
        Database summary dictionary

    Example:
        info = get_database_info("database.mdb")
        print(f"Database has {info['total_tables']} tables with {info['total_records']} records")
    """
    with MerlinDB(mdb_file) as db:
        return db.get_database_summary()
