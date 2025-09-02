"""Command-line interface for MerlinDB with comprehensive functionality."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from merlindb.api import load_database

console = Console()
app = typer.Typer(
    name="merlin-db",
    help="Parse and export Microsoft Access Database files used by GeniSys lighting control software.",
    rich_markup_mode="rich",
)


@app.command("info")
def info(
    file_path: Annotated[str, typer.Argument(help="Path to the MDB database file")],
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Show detailed information")
    ] = False,
):
    """Show database information and summary statistics.

    Examples:

        # Basic database info
        merlin-db info database.mdb

        # Detailed info with table breakdown
        merlin-db info database.mdb --verbose
    """
    try:
        with console.status("[bold blue]Loading database..."):
            db = load_database(file_path)
            summary = db.get_database_summary()

        # Create info panel
        info_text = f"""[bold]Database Summary[/bold]
        
📁 File: [cyan]{summary["file_path"]}[/cyan]
📊 Total Tables: [green]{summary["total_tables"]}[/green]
📋 Tables with Data: [green]{summary["tables_with_data"]}[/green]
📈 Total Records: [green]{summary["total_records"]:,}[/green]
🔧 Model Coverage: [green]{summary["model_coverage"]}[/green]"""

        console.print(Panel(info_text, title="[bold]MerlinDB Info[/bold]", border_style="blue"))

        if verbose:
            # Show table breakdown
            console.print("\n[bold]Table Details:[/bold]")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Table Name", style="cyan")
            table.add_column("Records", justify="right", style="green")
            table.add_column("Columns", justify="right", style="yellow")
            table.add_column("Validated", justify="center", style="blue")

            tables = db.list_tables()
            for table_name in tables[:20]:  # Show first 20 tables
                try:
                    info = db.get_table_info(table_name)
                    validation_status = "✓" if info["has_pydantic_model"] else "○"
                    table.add_row(
                        table_name,
                        f"{info['record_count']:,}",
                        str(info["column_count"]),
                        validation_status,
                    )
                except Exception:
                    table.add_row(table_name, "Error", "Error", "○")

            if len(tables) > 20:
                table.add_row("...", f"({len(tables) - 20} more)", "...", "...")

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("tables")
def list_tables(
    file_path: Annotated[str, typer.Argument(help="Path to the MDB database file")],
    pattern: Annotated[
        str | None, typer.Option("--pattern", "-p", help="Filter tables by pattern")
    ] = None,
    show_info: Annotated[bool, typer.Option("--info", "-i", help="Show table information")] = False,
):
    """List all tables in the database.

    Examples:

        # List all tables
        merlin-db tables database.mdb

        # Filter by pattern
        merlin-db tables database.mdb --pattern "GeniSys*"

        # Show table info
        merlin-db tables database.mdb --info
    """
    try:
        with console.status("[bold blue]Loading database..."):
            db = load_database(file_path)
            tables = db.list_tables()

        # Filter by pattern if provided
        if pattern:
            import fnmatch

            tables = fnmatch.filter(tables, pattern)
            if not tables:
                console.print(f"[yellow]No tables match pattern '{pattern}'[/yellow]")
                return

        if show_info:
            # Show detailed table information
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Table Name", style="cyan")
            table.add_column("Records", justify="right", style="green")
            table.add_column("Columns", justify="right", style="yellow")
            table.add_column("Validated", justify="center", style="blue")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Getting table info...", total=len(tables))

                for table_name in tables:
                    try:
                        info = db.get_table_info(table_name)
                        validation_status = "✓" if info["has_pydantic_model"] else "○"
                        table.add_row(
                            table_name,
                            f"{info['record_count']:,}",
                            str(info["column_count"]),
                            validation_status,
                        )
                    except Exception:
                        table.add_row(table_name, "Error", "Error", "○")

                    progress.update(task, advance=1)

            console.print(table)
        else:
            # Simple table listing
            console.print(f"[bold]Available Tables ({len(tables)}):[/bold]\n")
            for i, table_name in enumerate(tables, 1):
                console.print(f"  {i:2d}. [cyan]{table_name}[/cyan]")

            if pattern:
                console.print(f"\n[dim]Filtered by pattern: {pattern}[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("inspect")
def inspect_table(
    file_path: Annotated[str, typer.Argument(help="Path to the MDB database file")],
    table_name: Annotated[str, typer.Argument(help="Name of the table to inspect")],
    validate: Annotated[
        bool, typer.Option("--validate", "-v", help="Apply Pydantic validation")
    ] = False,
    limit: Annotated[
        int, typer.Option("--limit", "-l", help="Limit number of records to show")
    ] = 10,
):
    """Inspect a specific table's structure and data.

    Examples:

        # Inspect table structure
        merlin-db inspect database.mdb Config

        # Show data with validation
        merlin-db inspect database.mdb Config --validate

        # Limit output
        merlin-db inspect database.mdb Config --limit 5
    """
    try:
        with console.status(f"[bold blue]Loading table '{table_name}'..."):
            db = load_database(file_path)

            if not db.table_exists(table_name):
                console.print(f"[red]❌ Table '{table_name}' not found[/red]")
                similar = [t for t in db.list_tables() if table_name.lower() in t.lower()]
                if similar:
                    console.print(f"[yellow]Did you mean: {', '.join(similar[:5])}?[/yellow]")
                raise typer.Exit(1)

            # Get table info
            info = db.get_table_info(table_name)

            # Get table data
            data = db.get_table(table_name, validate=validate)

        # Display table information
        validation_status = (
            "✓ Pydantic validation available" if info["has_pydantic_model"] else "○ Raw data only"
        )
        info_text = f"""[bold]Table Information[/bold]

📋 Name: [cyan]{table_name}[/cyan]
📊 Records: [green]{info["record_count"]:,}[/green]
📝 Columns: [green]{info["column_count"]}[/green]
🔧 Validation: [blue]{validation_status}[/blue]"""

        console.print(
            Panel(info_text, title=f"[bold]Table: {table_name}[/bold]", border_style="green")
        )

        if data and info["record_count"] > 0:
            # Show column information
            console.print(f"\n[bold]Columns ({len(data)}):[/bold]")
            columns = list(data.keys())
            for i, col in enumerate(columns, 1):
                sample_values = data[col][:3] if data[col] else ["(empty)"]
                console.print(f"  {i:2d}. [cyan]{col}[/cyan] - Sample: {sample_values}")

            # Show sample data
            if limit > 0:
                console.print(
                    f"\n[bold]Sample Data (first {min(limit, info['record_count'])} records):[/bold]"
                )

                table = Table(show_header=True, header_style="bold magenta")
                for col in columns[:10]:  # Show first 10 columns
                    table.add_column(col, style="white", overflow="fold")

                num_records = min(limit, len(data[columns[0]]) if columns and data else 0)
                for i in range(num_records):
                    row = []
                    for col in columns[:10]:
                        value = data[col][i] if i < len(data[col]) else None
                        row.append(str(value) if value is not None else "(null)")
                    table.add_row(*row)

                console.print(table)

                if len(columns) > 10:
                    console.print(f"[dim]... and {len(columns) - 10} more columns[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("export")
def export(
    file_path: Annotated[str, typer.Argument(help="Path to the MDB database file")],
    output: Annotated[str, typer.Argument(help="Output file path")],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Export format (json, yaml, csv)")
    ] = "json",
    tables: Annotated[
        list[str] | None, typer.Option("--table", "-t", help="Table patterns to export")
    ] = None,
    separate_files: Annotated[
        bool, typer.Option("--separate", "-s", help="Create separate files for each table")
    ] = False,
    validate: Annotated[
        bool, typer.Option("--validate", "-v", help="Apply Pydantic validation during export")
    ] = False,
):
    """Export database tables to various formats.

    Examples:

        # Export all tables to JSON
        merlin-db export database.mdb output.json

        # Export specific tables to YAML
        merlin-db export database.mdb output.yaml --format yaml --table Config --table Events

        # Export with wildcards to separate CSV files
        merlin-db export database.mdb data.csv --format csv --table "GeniSys*" --separate

        # Export with validation
        merlin-db export database.mdb output.json --validate
    """
    try:
        with console.status("[bold blue]Loading database..."):
            db = load_database(file_path)

        # Override get_table method if validation requested
        if validate:
            original_get_table = db.get_table
            db.get_table = lambda name, validate=False: original_get_table(name, validate=True)

        with console.status("[bold blue]Exporting data..."):
            if format.lower() == "json":
                result = db.export_json(output, tables=tables, separate_files=separate_files)
            elif format.lower() == "yaml":
                result = db.export_yaml(output, tables=tables, separate_files=separate_files)
            elif format.lower() == "csv":
                result = db.export_csv(output, tables=tables, separate_files=separate_files)
            else:
                result = db.export(
                    output, format=format, tables=tables, separate_files=separate_files
                )

        # Display results
        console.print("[green]✓ Export completed successfully![/green]")
        console.print(f"  [bold]Format:[/bold] {result['format'].upper()}")
        console.print(f"  [bold]Tables exported:[/bold] {result['tables_exported']}")
        console.print(f"  [bold]Output files:[/bold] {len(result['output_files'])}")

        if result["tables_exported"] <= 10:
            tables_str = ", ".join(result["table_names"])
            console.print(f"  [bold]Tables:[/bold] {tables_str}")

        console.print("\n[bold]Output files:[/bold]")
        for output_file in result["output_files"]:
            file_path = Path(output_file)
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                console.print(f"  → [cyan]{output_file}[/cyan] ({size_kb:.1f} KB)")
            else:
                console.print(f"  → [cyan]{output_file}[/cyan]")

    except Exception as e:
        console.print(f"[red]❌ Export failed: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("validate")
def validate_data(
    file_path: Annotated[str, typer.Argument(help="Path to the MDB database file")],
    table: Annotated[
        str | None, typer.Option("--table", "-t", help="Specific table to validate")
    ] = None,
    summary_only: Annotated[
        bool, typer.Option("--summary", "-s", help="Show summary only")
    ] = False,
):
    """Validate database tables using Pydantic models.

    Examples:

        # Validate all tables
        merlin-db validate database.mdb

        # Validate specific table
        merlin-db validate database.mdb --table Config

        # Show validation summary only
        merlin-db validate database.mdb --summary
    """
    try:
        with console.status("[bold blue]Loading database and validating..."):
            db = load_database(file_path)

            tables_to_validate = [table] if table else db.list_tables()
            validation_results = {}

            for table_name in tables_to_validate:
                if not db.table_exists(table_name):
                    console.print(f"[red]❌ Table '{table_name}' not found[/red]")
                    continue

                try:
                    info = db.get_table_info(table_name)
                    if info["has_pydantic_model"]:
                        # Test validation
                        db.get_table(table_name, validate=True)
                        validation_results[table_name] = {
                            "status": "success",
                            "records": info["record_count"],
                        }
                    else:
                        validation_results[table_name] = {
                            "status": "no_model",
                            "records": info["record_count"],
                        }
                except Exception as e:
                    validation_results[table_name] = {
                        "status": "error",
                        "error": str(e),
                        "records": 0,
                    }

        # Display results
        if summary_only:
            success_count = sum(1 for r in validation_results.values() if r["status"] == "success")
            no_model_count = sum(
                1 for r in validation_results.values() if r["status"] == "no_model"
            )
            error_count = sum(1 for r in validation_results.values() if r["status"] == "error")
            total_validated_records = sum(
                r["records"] for r in validation_results.values() if r["status"] == "success"
            )

            summary_text = f"""[bold]Validation Summary[/bold]

✓ [green]Validated Successfully:[/green] {success_count} tables ({total_validated_records:,} records)
○ [yellow]No Pydantic Model:[/yellow] {no_model_count} tables  
✗ [red]Validation Errors:[/red] {error_count} tables"""

            console.print(
                Panel(summary_text, title="[bold]Validation Results[/bold]", border_style="blue")
            )
        else:
            # Detailed results
            console.print("[bold]Validation Results:[/bold]\n")

            for table_name, result in validation_results.items():
                if result["status"] == "success":
                    console.print(
                        f"  ✓ [green]{table_name}[/green]: {result['records']:,} records validated"
                    )
                elif result["status"] == "no_model":
                    console.print(f"  ○ [yellow]{table_name}[/yellow]: No Pydantic model available")
                elif result["status"] == "error":
                    console.print(
                        f"  ✗ [red]{table_name}[/red]: {result.get('error', 'Validation failed')}"
                    )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command("version")
def version():
    """Show MerlinDB version information."""
    try:
        version_info = "1.0.0"  # Could be dynamic from package

        console.print(
            Panel(
                f"[bold]MerlinDB[/bold] v{version_info}\n\nParse and export Microsoft Access Database files\nused by GeniSys lighting control software.",
                title="[bold]Version Info[/bold]",
                border_style="blue",
            )
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
