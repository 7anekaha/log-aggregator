from dataclasses import dataclass, field
import re
from .log import Log


@dataclass
class Filter:
    keyword: str
    pattern: re.Pattern = field(init=False)
    is_valid_regex: bool = field(default=True, init=False)

    def __post_init__(self):
        try:
            # Case-insensitive regex matching
            self.pattern = re.compile(self.keyword, re.IGNORECASE)
            self.is_valid_regex = True
        except re.error:
            # Fallback for invalid regex patterns during live typing
            self.is_valid_regex = False

    def matches(self, log: Log) -> bool:
        if not self.is_valid_regex:
            # Fallback to plain substring search if regex syntax is invalid
            kw = self.keyword.lower()
            return kw in log.message.lower() or kw in log.service.lower()

        return bool(
            self.pattern.search(log.message) or self.pattern.search(log.service) or self.pattern.search(str(log.ts))
        )
