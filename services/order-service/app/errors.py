from dataclasses import dataclass


@dataclass
class ServiceError(Exception):
    status_code: int
    code: str
    message: str
