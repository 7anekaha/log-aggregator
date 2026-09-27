import asyncio
import json
from datetime import datetime, timezone

import aioboto3
from botocore.exceptions import BotoCoreError, ClientError

from definitions.log import Log

from .base import Service


class AWSCloudTrailService(Service):
    """
    Service producer that streams real-time AWS CloudTrail events using start_live_tail.
    """

    def __init__(
        self,
        name: str,
        color: str,
        queue: asyncio.PriorityQueue[Log],
        arn: str | None = None,
        aws_region: str = "eu-west-1",
    ):
        super().__init__(name=name, color=color, queue=queue)
        self.arn = arn
        self.aws_region = aws_region

    async def _run(self) -> None:
        session = aioboto3.Session()

        try:
            async with session.client("cloudtrail", region_name=self.aws_region) as client:
                # Prepare stream parameters
                kwargs = {}
                if self.arn:
                    # Filter events specifically for this EventDataStore or Trail ARN if provided
                    kwargs["eventDataStore"] = self.arn

                # Initiate the streaming Live Tail session
                response = await client.start_live_tail(**kwargs)
                event_stream = response.get("eventStream")

                if not event_stream:
                    raise RuntimeError("Failed to establish CloudTrail Live Tail event stream.")

                # Process event stream as it arrives
                async for event in event_stream:
                    if "eventRecord" in event:
                        record = event["eventRecord"]

                        # Parse the event JSON body
                        event_data = json.loads(record.get("eventData", "{}"))

                        # Extract event details
                        event_name = event_data.get("eventName", "UnknownEvent")
                        event_source = event_data.get("eventSource", "unknown.aws")
                        user_arn = event_data.get("userIdentity", {}).get("arn") or event_data.get(
                            "userIdentity", {}
                        ).get("type", "UnknownUser")

                        formatted_msg = f"[{event_source}] {event_name} by {user_arn}"

                        log = Log(
                            ts=datetime.now(timezone.utc),
                            service=self.name,
                            message=formatted_msg,
                            color=self.color,
                        )
                        await self.queue.put(log)

                    elif "exception" in event:
                        # Stream error sent by CloudTrail
                        exc = event["exception"]
                        error_log = Log(
                            ts=datetime.now(timezone.utc),
                            service=self.name,
                            message=f"[CLOUDTRAIL STREAM ERROR] {exc.get('message')}",
                            color="red",
                        )
                        await self.queue.put(error_log)

        except (BotoCoreError, ClientError) as err:
            error_log = Log(
                ts=datetime.now(timezone.utc),
                service=self.name,
                message=f"[AWS CLIENT ERROR] {err}",
                color="red",
            )
            await self.queue.put(error_log)

        except asyncio.CancelledError:
            print(f"{self.name} CloudTrail service has been cancelled.")
