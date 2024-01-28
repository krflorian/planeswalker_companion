from enum import Enum
from dataclasses import dataclass, field
from .card import Card
from .document import Document


class MessageType(Enum):
    DECKBUILDING = "deckbuilding"
    RULES = "rules"
    CONVERSATION = "conversation"
    MALICIOUS = "malevolent"
    ASSISTANT = "assistant"


@dataclass
class Message:
    text: str
    type: MessageType
    processed_text: str
    cards: list[Card] = field(default_factory=list)
    rules: list[Document] = field(default_factory=list)
