from pathlib import Path
from pydantic import BaseModel, Field
from .rule import Rule


class Card(BaseModel):
    _id: str
    name: str
    mana_cost: str
    type: str
    oracle: str
    image_url: str
    price: float
    power: str = "0"
    toughness: str = "0"
    color_identity: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    rulings: list[Rule] = Field(default_factory=list)
    _image: Path = None

    def __repr__(self) -> str:
        return f"Card({self.name})"

    def to_text(self, include_price: bool = True):
        """parse card data to text format"""
        text = []
        text.append(self.name)
        text.append(f"type: {self.type}")
        text.append(f"cost: {self.mana_cost}")
        if (self.power != "0") and (self.toughness != "0"):
            text.append(f"power/toughness: {str(self.power)}/{str(self.toughness)}")
        if self.keywords:
            text.append("keywords: " + " ".join(self.keywords))
        if self.color_identity:
            text.append("color identity: " + " ".join(self.color_identity))
        text.append(self.oracle)

        # price
        if include_price:
            if self.price != 0.0:
                text.append(f"price in EUR: {self.price}")

        return "\n".join(text)
