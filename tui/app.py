import asyncio
from datetime import datetime
from typing import Sequence

from textual.app import App, ComposeResult, on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, RichLog

from definitions.filter import Filter
from definitions.log import Log
from services.base import Service
from services.consumer import Consumer
from tui.filter import FilterChip, FilterInput


class LogApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit Application"),
        ("f", "focus_input", "Focus Filter Input"),
        ("r", "focus_filters", "Remove / Select Filter Chips"),
        ("p", "pause_logging", "Pause Logging"),
    ]

    def __init__(self, services: Sequence[Service]):
        super().__init__()
        self.active_filters: list[Filter] = []
        self.services = list(services)
        self.start_event = asyncio.Event()  # Initially not set, will be used to control logging start
        self.start_event.set() # allow logging to start immediately

    def compose(self) -> ComposeResult:
        with Vertical(id="controls-container"):
            yield FilterInput(placeholder="Type regex filter and press Enter (Esc to unfocus)...")
            with Horizontal(id="filter-bar"):
                yield Label("Active Filters: ", id="filter-label")
                yield Horizontal(id="chips-container")
        yield RichLog(highlight=True, markup=True)

    async def action_quit(self) -> None:
        if not self.start_event.is_set():
            self.start_event.set()  # Ensure logging is resumed before quitting
        priority_queue = self.services[0].queue
        priority_queue.put_nowait(Log(service="Sentinel", ts=datetime.now(), message="Sentinel", color="dim"))
        await priority_queue.join()  # Wait until the sentinel is processed
        await asyncio.sleep(0.2)  # Give some time for the consumer to process the sentinel
        await asyncio.gather(*[service.stop() for service in self.services], return_exceptions=True)
        self.exit()

    def action_focus_input(self) -> None:
        self.query_one(FilterInput).focus()

    def action_focus_filters(self) -> None:
        """Focus the first filter chip in the bar when 'r' is pressed."""
        chips = self.query(FilterChip)
        if chips:
            chips.first().focus()

    def action_pause_logging(self) -> None:
        """Pause the logging when 'p' is pressed."""
        if self.start_event.is_set():
            self.start_event.clear()
        else:
            self.start_event.set()

    def on_mount(self) -> None:
        log_widget = self.query_one(RichLog)
        self.run_worker(self.run_main(log_widget), exclusive=True)

    @on(Input.Submitted)
    def create_filter(self, event: Input.Submitted) -> None:
        keyword: str = event.value.strip()
        log_widget = self.query_one(RichLog)

        if keyword and not any(f.keyword.lower() == keyword.lower() for f in self.active_filters):
            # Add filter object
            new_filter = Filter(keyword)
            self.active_filters.append(new_filter)

            # Mount dynamic chip button UI
            chips_container = self.query_one("#chips-container", Horizontal)
            chips_container.mount(FilterChip(keyword))

            log_widget.write(f"[bold yellow]Added filter:[/bold yellow] '{keyword}'")
            event.input.value = ""

    @on(Button.Pressed)
    def remove_filter(self, event: Button.Pressed) -> None:
        if isinstance(event.button, FilterChip):
            keyword = event.button.keyword

            # Remove from model
            self.active_filters[:] = [f for f in self.active_filters if f.keyword.lower() != keyword.lower()]

            # Determine next element to focus before removing current button
            chips = list(self.query(FilterChip))
            current_index = chips.index(event.button) if event.button in chips else -1

            event.button.remove()

            # Shift focus to remaining adjacent chip or return to app
            remaining_chips = [c for c in chips if c != event.button]
            if remaining_chips:
                next_index = min(current_index, len(remaining_chips) - 1)
                remaining_chips[next_index].focus()
            else:
                self.set_focus(None)

            log_widget = self.query_one(RichLog)
            log_widget.write(f"[bold red]Removed filter:[/bold red] '{keyword}'")

    async def run_main(self, log_widget: RichLog):
        if not self.services:
            log_widget.write("[bold red]No services configured.[/bold red]")
            return

        # All services must share the same queue consumed below.
        priority_queue = self.services[0].queue
        for service in self.services:
            service.start()

        self.consumer = Consumer(priority_queue, log_widget, filters=self.active_filters, start_event=self.start_event)
        self.consumer.start()

        # await asyncio.gather(*[service.stop() for service in self.services], return_exceptions=True)
        # await priority_queue.put(Log(ts=datetime.max, service="Sentinel", message="Stop", color="grey"))
        await self.consumer.wait_until_done()
