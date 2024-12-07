from enum import Enum
from dataclasses import dataclass, field
from .card import Card
from .document import Document


class MessageType(Enum):
    DECKBUILDING = "deckbuilding"
    RULES = "rules"
    CONVERSATION = "conversation"
    MALICIOUS = "malicious"
    ASSISTANT = "assistant"


@dataclass
class Message:
    text: str
    type: MessageType
    processed_text: str
    cards: list[Card] = field(default_factory=list)
    rules: list[Document] = field(default_factory=list)

    def to_dict(self):
        return {
            "text": self.text,
            "type": str(self.type),
            "cards": [card.to_dict() for card in self.cards],
            "rules": [rule.to_dict() for rule in self.rules],
        }

    def to_string(self):
        if self.type == MessageType.ASSISTANT:
            return f"Assistant: {self.text}"
        return f"User: {self.text}"
