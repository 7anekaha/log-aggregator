import asyncio
from abc import ABC, abstractmethod
from definitions.log import Log

class Service(ABC):
    def __init__(self, name, queue: asyncio.PriorityQueue[Log], color: str):
        self.name = name
        self.queue = queue
        self.color = color
        self._task = None  # Holds the asyncio task for the service's log generation

    def start(self) -> asyncio.Task:
        """Start sending logs to the queue asynchronously."""
        self._task = asyncio.create_task(self._run())
        return self._task

    async def stop(self):
        """Stop sending logs to the queue asynchronously."""
        if self._task and not self._task.done():
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)

    @abstractmethod
    async def _run(self):
        """Run the service's log generation loop asynchronously."""
        pass
