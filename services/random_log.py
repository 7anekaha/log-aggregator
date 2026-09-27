import asyncio
import random
from datetime import datetime

from definitions.log import Log

from .base import Service


class RandomLogService(Service):
    async def _run(self):
        try:
            while True:
                await asyncio.sleep(random.uniform(0.1, 1.0))
                log = Log(
                    ts=datetime.now(), service=self.name, message=f"Log message from {self.name}", color=self.color
                )
                await self.queue.put(log)
        except asyncio.CancelledError:
            print(f"{self.name} has been cancelled.")
