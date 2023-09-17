# %%
import json
from pathlib import Path
import requests
import logging
from tqdm import tqdm

all_cards_file = Path("data/raw/scryfall_all_cards.json")
with all_cards_file.open("r", encoding="utf-8") as infile:
    data = json.load(infile)

idx_2_card_data = {card_data["id"]: card_data for card_data in data}

# %%

BLOCKED_CARD_TYPES = ["Card", "Stickers", "Hero"]
for card_data in tqdm(data):
    if (card_data["layout"] != "normal") or (
        card_data["type_line"] in BLOCKED_CARD_TYPES
    ):
        continue

    card_id = card_data.get("id", None)
    url = f"https://api.scryfall.com/cards/{card_id}/rulings"

    response = requests.get(url)
    json_response = response.json()
    if json_response.get("data", []) and (response.status_code != 404):
        logging.debug(
            f"adding {len(json_response['data'])} rulings for {card_data.get('name')}"
        )
        rulings = [ruling["comment"] for ruling in json_response["data"]]
        idx_2_card_data[card_id]["rulings"] = rulings


# %%
# save all cards
processed_data = list(idx_2_card_data.values())
all_cards_file = Path("data/raw/scryfall_all_cards_with_rulings.json")

with all_cards_file.open("w", encoding="utf-8") as outfile:
    json.dump(processed_data, outfile)


# %%
# save sample
import random

all_cards_sample_file = Path("data/raw/scryfall_all_cards_with_rulings_sample.json")
sample = random.choices(
    [card for card in processed_data if card.get("rulings", [])], k=10
)
with all_cards_sample_file.open("w", encoding="utf-8") as outfile:
    json.dump(sample, outfile)

# %%

print(len([c for c in processed_data if c.get("rulings")]), "cards with rulings")

# %%
