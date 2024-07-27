from pathlib import Path
from pydantic import BaseModel, Field
from .document import Document


MANACOST_MAPPER = {
    "W": "white",
    "U": "blue",
    "B": "black",
    "R": "red",
    "G": "green",
}


class Card(BaseModel):
    _id: str
    name: str
    mana_cost: str
    type: str
    oracle: str
    price: float
    url: str
    power: str = "0"
    toughness: str = "0"
    color_identity: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    rulings: list[Document] = Field(default_factory=list)
    legalities: dict[str, str] = Field(default_factory=dict)
    _image: Path = None

    def __repr__(self) -> str:
        return f"Card({self.name})"

    def to_dict(self) -> dict:
        return self.model_dump()

    def __hash__(self):
        return hash(self.name)

    def to_text(self):
        """parse card data to text format"""

        # power
        power_toughness = ""
        if (self.power != "0") and (self.toughness != "0"):
            power_toughness = f"{str(self.power)}/{str(self.toughness)}"

        # mana
        if self.mana_cost == "":
            mana_cost = "No Mana Cost"
        else:
            mana_cost = "Mana Cost: " + self.mana_cost

        color_identity = " ".join(self.color_identity)

        # rulings
        rulings = "\n".join([ruling.text for ruling in self.rulings])

        text = f"""
        {self.name}
        {mana_cost}
        Type: {self.type} {power_toughness}
        Color Identity: {color_identity}
        Price in EUR: {self.price}

        {self.oracle}
        """

        if rulings:
            text += f"""
        Special Rulings for {self.name}: 
        {rulings}
        """

        return text
