from __future__ import annotations

from typing import Any

from access_parser import AccessParser
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
)
from typing_extensions import override

from merlindb.providers import (
    DataProvider,
    DeviceDataProvider,
    DynaliteDataProvider,
    RawDataProvider,
)
from merlindb.utils import get_mdb


class TableBrowser(App[None]):
    """Interactive table browser for MerlinDB databases."""

    CSS_PATH = "browser.tcss"  # pyright: ignore
    BINDINGS = [  # pyright: ignore
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("f", "search_mode", "Search"),
        ("r", "refresh", "Refresh"),
        ("h", "help", "Help"),
    ]

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path: str = file_path
        self.db: AccessParser | None = None
        self.current_provider: DataProvider | None = None
        self.current_table: str | None = None
        self.table_data: dict[str, Any] = {}
        self.filtered_data: list[list[str]] = []
        self.search_term: str = ""

        # Available data providers
        self.providers: dict[str, type[DataProvider]] = {
            "Raw": RawDataProvider,
            "Dynalite": DynaliteDataProvider,
            "Device": DeviceDataProvider,
        }

    @override
    def compose(self) -> ComposeResult:
        """Create the application layout."""
        yield Header()
        yield Horizontal(
            Vertical(
                Label("Mode:", classes="label"),
                Select[str]((), id="mode_select"),
                Label("Tables:", classes="label"),
                Select[str]((), id="table_select"),
                Label("Search:", classes="label"),
                Input(placeholder="Filter rows...", id="search_input"),
                Button("Clear", id="clear_button"),
                id="sidebar",
            ),
            DataTable(id="main_table"),
            id="main_container",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the application when mounted."""
        # Load database
        self.db = get_mdb(self.file_path)
        if not self.db:
            self.exit(message="Failed to load database")
            return

        # Populate mode selector
        mode_select = self.query_one("#mode_select", Select)
        mode_options = []
        for mode_name, provider_class in self.providers.items():
            # Create temporary provider to get description
            temp_provider = provider_class(self.db)
            description = temp_provider.get_mode_description()
            mode_options.append((f"{mode_name}: {description}", mode_name))
        mode_select.set_options(mode_options)  # pyright: ignore

        # Set default mode to Raw
        self._set_mode("Raw")

        # Set initial focus
        mode_select.focus()

    @on(Select.Changed, "#mode_select")
    def on_mode_selected(self, event: Select.Changed) -> None:  # pyright: ignore
        """Handle mode selection."""
        if event.value is None:
            return

        mode_name = str(event.value)
        self._set_mode(mode_name)

    @on(Select.Changed, "#table_select")
    def on_table_selected(self, event: Select.Changed) -> None:  # pyright: ignore
        """Handle table selection."""
        if event.value is None:
            return

        self.current_table = str(event.value)
        self._load_table_data()
        self._update_display()

    @on(Input.Changed, "#search_input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.search_term = event.value.lower()
        self._update_display()

    @on(Button.Pressed, "#clear_button")
    def on_clear_pressed(self) -> None:
        """Clear search and reset view."""
        search_input = self.query_one("#search_input", Input)
        search_input.value = ""
        self.search_term = ""
        self._update_display()

    def _set_mode(self, mode_name: str) -> None:
        """Set the current browsing mode and update the table list.

        Args:
            mode_name: Name of the mode to activate
        """
        if not self.db or mode_name not in self.providers:
            return

        # Create new provider instance
        provider_class = self.providers[mode_name]
        self.current_provider = provider_class(self.db)

        # Update table selector with tables from this provider
        table_select = self.query_one("#table_select", Select)
        try:
            tables = self.current_provider.get_available_tables()
            table_select.set_options([(table, table) for table in tables])  # pyright: ignore

            # Clear current selection
            self.current_table = None
            self.table_data = {}
            self._update_display()

            self.notify(f"Switched to {mode_name} mode")
        except Exception as e:
            self.notify(f"Error switching to {mode_name} mode: {e}", severity="error")

    def _load_table_data(self) -> None:
        """Load data for the currently selected table using the current provider."""
        if not self.current_provider or not self.current_table:
            return

        try:
            self.table_data = self.current_provider.get_table_data(self.current_table)
        except NotImplementedError as e:
            self.table_data = {}
            self.notify(str(e), severity="warning")
        except Exception as e:
            self.table_data = {}
            self.notify(f"Error loading table: {e}", severity="error")

    def _update_display(self) -> None:
        """Update the data table display with current data and filters."""
        data_table = self.query_one("#main_table", DataTable)
        data_table.clear(columns=True)

        if not self.table_data:
            return

        # Set up columns
        columns = list(self.table_data.keys())
        for col in columns:
            data_table.add_column(col, key=col)

        # Prepare row data
        if not columns:
            return

        num_rows = len(self.table_data[columns[0]])
        rows = []

        for i in range(num_rows):
            row = []
            for col in columns:
                value = self.table_data[col][i] if i < len(self.table_data[col]) else ""
                row.append(str(value) if value is not None else "")
            rows.append(row)

        # Apply search filter
        if self.search_term:
            filtered_rows = []
            for row in rows:
                if any(self.search_term in str(cell).lower() for cell in row):
                    filtered_rows.append(row)
            rows = filtered_rows

        # Add rows to table
        for i, row in enumerate(rows):
            data_table.add_row(*row, key=str(i))

        # Update title
        table_name = self.current_table or "No table selected"
        search_info = (
            f" (filtered: {len(rows)} rows)" if self.search_term else f" ({len(rows)} rows)"
        )
        # Update title (ignoring type issue with textual)
        try:
            data_table.title = f"{table_name}{search_info}"  # pyright: ignore
        except AttributeError:
            pass

    def action_search_mode(self) -> None:
        """Focus search input."""
        search_input = self.query_one("#search_input", Input)
        search_input.focus()

    def action_refresh(self) -> None:
        """Refresh current table data."""
        if self.current_table:
            self._load_table_data()
            self._update_display()
            self.notify("Table refreshed")

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
        Interactive Table Browser - Keyboard Shortcuts:
        
        Navigation:
        • Tab/Shift+Tab    - Navigate between controls
        • Enter           - Select table/confirm input
        • Arrow keys      - Navigate table data
        
        Actions:
        • F                - Focus search box
        • R                - Refresh current table
        • Q or Ctrl+C      - Quit application
        • H                - Show this help
        
        Search:
        • Type in search box to filter rows
        • Search is case-insensitive
        • Matches any column content
        """
        self.notify(help_text)


def browse_database(file_path: str) -> None:
    """Launch the interactive database browser."""
    app = TableBrowser(file_path)
    app.run()
