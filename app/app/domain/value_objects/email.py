"""Value Object Email: garante formato válido na fronteira do domínio."""
from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    address: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.address):
            raise ValueError("EMAIL_INVALIDO")
        object.__setattr__(self, "address", self.address.lower().strip())

    def __str__(self) -> str:
        return self.address
