from pathlib import Path
import json
from spacy.tokens import Doc

from mtg.objects import Card
from .spacy_utils import load_spacy_model

BLOCKED_CARD_TYPES = ["Card", "Stickers", "Hero"]


class CardDB:
    def __init__(
        self, all_cards_file: Path, spacy_model_name: str = "en_core_web_lg"
    ) -> None:
        # read set data
        all_cards, all_sets = [], set()

        # create cache
        Path(".cache/").mkdir(exist_ok=True, parents=True)

        # load card data
        if isinstance(all_cards_file, str):
            all_cards_file = Path(all_cards_file)

        with all_cards_file.open("r", encoding="utf-8") as infile:
            data = json.load(infile)

        for card_data in data:
            if (card_data["layout"] != "normal") or (
                card_data["type_line"] in BLOCKED_CARD_TYPES
            ):
                continue
            all_sets.add(card_data.get("set_name"))
            all_cards.append(
                Card(
                    _id=card_data.get("id"),
                    name=card_data.get("name"),
                    mana_cost=card_data.get("mana_cost"),
                    type=card_data.get("type_line"),
                    power=card_data.get("power", 0),
                    toughness=card_data.get("toughness", 0),
                    oracle=card_data.get("oracle_text", ""),
                    color_identity=card_data.get("color_identity", []),
                    keywords=card_data.get("keywords", []),
                    image_url=card_data["image_uris"].get("large"),
                    rulings=card_data.get("rulings", []),
                )
            )
        print(f"loaded {len(all_cards)} cards...")

        # initialize spacy model
        nlp = load_spacy_model(spacy_model_name, [c.name for c in all_cards])

        # init variables
        self.card_name_2_card: dict[str, Card] = {c.name: c for c in all_cards}
        self.all_sets: set[str] = all_sets
        self.nlp = nlp

        print("Card Data Handler ready!")

    def process_text(self, text: str) -> Doc:
        """Fuzzy search for card names and add entities"""
        return self.nlp(text)

    def process_texts(self, texts: list[str]) -> list[Doc]:
        """Fuzzy search for card names and add entities"""

        return self.nlp.pipe(texts)

    def extract_card_data_from_doc(self, doc: str) -> list[Card]:
        """Search for card objects corresponding to doc"""
        return [self.card_name_2_card.get(card_name) for card_name in doc._.card_names]

    def replace_card_names_with_urls(self, doc) -> str:
        text = ""
        for token in doc:
            if token.ent_type_:
                card = self.card_name_2_card[token.ent_type_]
                text += f"[{card.name}]({card.image_url})"
                text += token.whitespace_
            else:
                text += token.text
                text += token.whitespace_

        return text
