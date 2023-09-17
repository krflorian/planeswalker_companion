from dataclasses import dataclass, field
from pathlib import Path
import urllib


CACHE_PATH = Path(".cache/")


@dataclass
class Card:
    _id: str
    name: str
    mana_cost: str
    type: str
    oracle: str
    image_url: str
    power: int = 0
    toughness: int = 0
    color_identity: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    rulings: list[str] = field(default_factory=list)
    _image: Path = None

    def __repr__(self) -> str:
        return f"Card({self.name})"

    @property
    def image(self):
        if self._image:
            return self._image
        # TODO not allways download check first if id is file
        print(f"downloading image for {self.name}")
        card_image_file = CACHE_PATH / f"{self._id}.png"
        urllib.request.urlretrieve(self.image_url, card_image_file)
        self._image = card_image_file
        return card_image_file

    def to_text(self):
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
        if self.rulings:
            text.append("Rulings for this card: ")
            text.append("\n".join(self.rulings))
        return "\n".join(text)
