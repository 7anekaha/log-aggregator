from dataclasses import dataclass, field
from datetime import datetime

@dataclass(order=True)
class Log:
    ts: datetime
    service: str = field(compare=False)
    message: str = field(compare=False)
    color: str = field(compare=False)
