import pytest
import pickle
import json

from pathlib import Path

from mtg.objects import Card


@pytest.fixture(scope="session")
def card_name_2_card() -> dict[str, Card]:
    BLOCKED_CARD_TYPES = ["Card", "Stickers", "Hero"]
    all_cards_file = Path("data/cards/scryfall_all_cards_with_rulings.json")

    with all_cards_file.open("r") as infile:
        cards_data = json.load(infile)

    card_name_2_card = {}
    for card_data in cards_data:
        if (card_data["layout"] != "normal") or (
            card_data["type_line"] in BLOCKED_CARD_TYPES
        ):
            continue
        card_name_2_card[card_data.get("name")] = Card(
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

    return card_name_2_card
