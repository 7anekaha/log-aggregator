from enum import Enum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, model_validator


class ServiceType(str, Enum):
    random = "random"
    aws = "aws"


class ServiceConfig(BaseModel):
    name: str
    color: str
    type: ServiceType
    arn: str | None = None

    @model_validator(mode="after")
    def check_arn_for_aws(self) -> Self:
        # Access properties directly on `self` instead of using `.get()`
        if self.type == ServiceType.aws and not self.arn:
            raise ValueError("ARN must be provided for AWS service type")
        return self


class ServicesConfig(BaseModel):
    services: list[ServiceConfig]

    @staticmethod
    def load_from_file(file_path: Path) -> "ServicesConfig":
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)

        return ServicesConfig.model_validate(raw_data)
