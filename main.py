import asyncio
from pathlib import Path

from definitions.service_config import ServicesConfig, ServiceType
from services.random_log import RandomLogService
from services.aws_log import AWSCloudTrailService
from tui.app import LogApp

def construct_services(config: ServicesConfig, shared_queue: asyncio.PriorityQueue) -> list:
    map_obj = {
        ServiceType.random: RandomLogService,
        ServiceType.aws: AWSCloudTrailService,
    }
    services = []
    for service in config.services:
        service_class = map_obj.get(service.type)
        args = [service.name, service.color, shared_queue]
        if service.type == ServiceType.aws:
            args.append(service.arn)
        services.append(service_class(*args))
    return services

if __name__ == "__main__":
    shared_queue = asyncio.PriorityQueue()

    config = ServicesConfig.load_from_file(Path("configuration.yaml"))
    services = construct_services(config, shared_queue)

    app = LogApp(services=services)
    app.run()
