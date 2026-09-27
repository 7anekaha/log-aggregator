import asyncio
from datetime import datetime, timedelta
from textual.widgets import RichLog
from textual import events
from rich.text import Text

from definitions.filter import Filter
from definitions.log import Log


class Consumer:
    def __init__(self, priority_queue: asyncio.PriorityQueue[Log], log_widget: RichLog, filters: list[Filter], start_event: asyncio.Event, window_size: int = 5):
        self.priority_queue = priority_queue
        self.console = log_widget
        self.filters = filters
        self.start_event = start_event
        self._task = None
        self.window_size = window_size # Window size in seconds for log display cutoff

    def start(self) -> asyncio.Task:
        self._task = asyncio.create_task(self._run())
        return self._task

    async def _run(self):
        buffer: list[Log] = []

        while True:
            # Pause logging execution if start_event is cleared
            await self.start_event.wait()

            # 1. Drain available logs into buffer
            while not self.priority_queue.empty():
                log = self.priority_queue.get_nowait()

                if log.service == "Sentinel":
                    self.console.write("Received sentinel value. Stopping log consumption.")
                    self.priority_queue.task_done()
                    return  # Use return to stop the consumer task completely

                buffer.append(log)
                self.priority_queue.task_done()

            # 2. Sort buffer chronologically
            buffer.sort(key=lambda log: log.ts)

            # 3. Partition logs by window size cutoff
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_size)

            logs_ready = [log for log in buffer if log.ts <= cutoff]
            buffer = [log for log in buffer if log.ts > cutoff]

            # 4. Display ready logs
            for log in logs_ready:
                if self.apply_filters(log):
                    self.console.write(self._build_text(log))

            # 5. Prevent CPU spinning when queue/buffer are idle
            await asyncio.sleep(0.2)

    async def wait_until_done(self):
        if self._task:
            await self._task

    def apply_filters(self, log: Log) -> str | None:
        return log.message if all(f.matches(log) for f in self.filters) else None

    def _build_text(self, log: Log) -> Text:
        text = Text()
        text.append(f"[{log.ts}] ", style="dim")
        text.append(f"{log.service}: ", style=log.color)
        text.append(log.message)
        return text
