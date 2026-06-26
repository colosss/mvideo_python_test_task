from dataclasses import dataclass

@dataclass(frozen=True)
class CreateLogDTO:
    log: str