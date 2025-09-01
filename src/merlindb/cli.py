from typing import Annotated

import typer

from merlindb.browser import browse_database
from merlindb.dump import dump_tables
from merlindb.logging import log
from merlindb.utils import get_mdb, load_all, read_areas, read_tables

app = typer.Typer()


@app.command()
def load(file_path: str):
    db = get_mdb(file_path)
    if db:
        log.info(load_all(db))


@app.command()
def dump(file_path: str):
    db = get_mdb(file_path)
    if db:
        db.print_database()


@app.command()
def inspect(file_path: str):
    db = get_mdb(file_path)
    if db:
        log.info(db.parse_msys_table())


@app.command()
def areas(file_path: str):
    db = get_mdb(file_path)
    if db:
        read_areas(db)


@app.command()
def tables(file_path: str):
    db = get_mdb(file_path)
    if db:
        read_tables(db)


@app.command()
def browse(file_path: str):
    """Launch interactive table browser for exploring database contents."""
    browse_database(file_path)


@app.command()
def dump(
    file_path: str,
    output: str,
    format: Annotated[str, typer.Option("--format", "-f", help="Export format")] = "json",
    mode: Annotated[str, typer.Option("--mode", "-m", help="Browsing mode")] = "raw",
    tables: Annotated[
        list[str], typer.Option("--table", "-t", help="Table patterns to export")
    ] = None,
    separate_files: Annotated[
        bool, typer.Option("--separate", help="Create separate files for each table")
    ] = False,
    list_tables: Annotated[
        bool, typer.Option("--list", help="List available tables and exit")
    ] = False,
):
    """Dump database tables to JSON, YAML, CSV, or XLSX files.

    Examples:

        # Dump all tables to JSON (default)
        merlin-db dump database.mdb output.json

        # Dump specific tables to YAML
        merlin-db dump database.mdb output.yaml --format yaml --table Areas --table Presets

        # Dump all tables using wildcard patterns to CSV with separate files
        merlin-db dump database.mdb export --format csv --table "Area*" --separate

        # Dump using Dynalite mode to Excel
        merlin-db dump database.mdb output.xlsx --format xlsx --mode dynalite

        # List available tables in Device mode
        merlin-db dump database.mdb output.json --mode device --list
    """
    try:
        if list_tables:
            # List tables and exit
            from merlindb.dump import get_provider

            provider = get_provider(file_path, mode)
            available_tables = provider.get_available_tables()

            print(f"Available tables in {mode.upper()} mode:")
            for table in available_tables:
                print(f"  - {table}")
            print(f"\nTotal: {len(available_tables)} tables")
            return

        # Perform the dump
        result = dump_tables(
            db_path=file_path,
            output_path=output,
            format_name=format,
            mode=mode,
            tables=tables,
            single_file=not separate_files,
        )

        # Display results
        print("✓ Export completed successfully!")
        print(f"  Mode: {result['mode'].upper()}")
        print(f"  Format: {result['format'].upper()}")
        print(f"  Tables exported: {result['tables_exported']}")
        print(f"  Output files: {len(result['output_files'])}")

        if result["tables_exported"] <= 10:
            print(f"  Tables: {', '.join(result['table_names'])}")

        for output_file in result["output_files"]:
            print(f"    → {output_file}")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        raise typer.Exit(1)
