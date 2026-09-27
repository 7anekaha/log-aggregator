import asyncio
from pathlib import Path

from definitions.service_config import ServicesConfig, ServiceType
from services.random_log import RandomLogService
from tui.app import LogApp


if __name__ == "__main__":
    shared_queue = asyncio.PriorityQueue()

    config = ServicesConfig.load_from_file(Path("configuration.yaml"))
    services = []
    for service in config.services:
        if service.type == ServiceType.random:
            services.append(RandomLogService(service.name, shared_queue, service.color))

    app = LogApp(services=services)
    app.run()
