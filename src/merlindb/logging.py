import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")


def print_table(name: str, columns: list[str], rows: list[list[str]]) -> None:
    table = Table(title=name)
    for col in columns:
        table.add_column(col, justify="right", style="cyan", no_wrap=True)
    for row in rows:
        table.add_row(*row)
    console = Console()
    console.print(table)
