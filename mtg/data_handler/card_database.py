from pathlib import Path
import json
import pickle
import time

from mtg.objects import Card, Message
from .vector_db import VectorDB
from .spacy_utils import match_cards
from mtg.utils.logging import get_logger

logger = get_logger(__name__)

BLOCKED_CARD_TYPES = ["Card", "Stickers", "Hero"]


class CardDB:
    def __init__(
        self,
        all_cards_file: Path,
        vector_db_file: Path = Path(
            "data/artifacts/card_vector_db.p",
        ),
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
                    price=card_data.get("prices", {}).get("eur", 0.0),
                    color_identity=card_data.get("color_identity", []),
                    keywords=card_data.get("keywords", []),
                    image_url=card_data["image_uris"].get("large"),
                    rulings=card_data.get("rulings", []),
                )
            )
        logger.info(f"loaded {len(all_cards)} cards...")

        # init variables
        self.card_name_2_card: dict[str, Card] = {c.name: c for c in all_cards}
        self.all_sets: set[str] = all_sets

        # init card vector db
        try:
            with vector_db_file.open("rb") as infile:
                self.card_vector_db: VectorDB = pickle.load(infile)
            logger.info("loaded Card Vector DB from Filesystem")
        except:
            self.card_vector_db: VectorDB = VectorDB(cards=all_cards)

        # update vector db
        updated = self.update_card_vector_db()
        if updated:
            with vector_db_file.open("wb") as outfile:
                pickle.dump(self.card_vector_db, outfile)
            logger.info("Saved updated Vector DB")
        logger.info("Card Data Handler ready!")

    def update_card_vector_db(self) -> bool:
        cards_in_vector_db = list(self.card_vector_db.ids_2_card_name.values())
        missing_cards = [
            card
            for card_name, card in self.card_name_2_card.items()
            if card_name not in cards_in_vector_db
        ]
        if missing_cards:
            names_and_embeddings = self.card_vector_db.get_embeddings(missing_cards)
            self.card_vector_db.add(names_and_embeddings)
            return True
        return False

    def replace_card_names_with_urls(self, text, cards, role="user") -> str:
        """Find Card Names in text and replace them with their URL. Return only Cards that are found in the text."""

        if not cards:
            return text, cards

        doc = match_cards(text=text, cards=cards)
        text = ""
        filtered_cards = []
        for token in doc:
            if token.ent_type_:
                # add token as url
                card = self.card_name_2_card.get(token.ent_type_)
                if card is None:
                    text += token.text
                else:
                    if card not in filtered_cards:
                        filtered_cards.append(card)
                    if role == "assistant":
                        text += f"[{token.text}]({card.image_url})"
                    else:
                        text += f"[{card.name}]({card.image_url})"
                text += token.whitespace_
            else:
                # add token as text
                text += token.text
                text += token.whitespace_

        return text, filtered_cards

    def create_message(
        self,
        text: str,
        role: str,
        max_number_of_cards: int = 3,
        threshhold: float = 0.2,
        append_all_cards: bool = False,
    ) -> Message:
        start = time.time()
        logger.info(f"creating message for {role}")

        card_names = self.card_vector_db.query(
            text, k=max_number_of_cards, threshhold=threshhold
        )
        checkpoint_vector_query = time.time()

        all_cards = [self.card_name_2_card.get(card_name) for card_name in card_names]

        processed_text, matched_cards = self.replace_card_names_with_urls(
            text=text, cards=all_cards, role=role
        )
        checkpoint_processed_text = time.time()

        cards = all_cards if append_all_cards else matched_cards
        message = Message(
            text=text, role=role, processed_text=processed_text, cards=cards
        )
        logger.info(
            f"message created with {len(cards)} cards: {' '.join([str(c) for c in cards])}"
        )
        checkpoint_end = time.time()
        logger.debug(
            f"query runtime: {checkpoint_vector_query-start:.2f}sec, text processing runtime: {checkpoint_processed_text-checkpoint_vector_query:.2f}sec, total runtime {checkpoint_end-start:.2f}sec"
        )
        return message
