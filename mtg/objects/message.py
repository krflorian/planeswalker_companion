from dataclasses import dataclass, field
from .card import Card


@dataclass
class Message:
    text: str
    role: str
    processed_text: str
    cards: list[Card] = field(default_factory=list)

    def to_gpt_format(self) -> dict:
        content = ""
        if self.cards and self.role == "user":
            cards_context = "\n".join([card.to_text() for card in self.cards])
            content += f"CONTEXT: \n{cards_context}\n\n"
        content += f"\n{self.text}"
        return {"role": self.role, "content": content}
