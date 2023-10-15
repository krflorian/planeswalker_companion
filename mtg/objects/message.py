from dataclasses import dataclass, field
from .card import Card


@dataclass
class Message:
    text: str
    role: str
    processed_text: str
    cards: list[Card] = field(default_factory=list)
