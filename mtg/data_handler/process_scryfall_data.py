# %%
# download bulk data
import json
from pathlib import Path
import requests
import random
from tqdm import tqdm

cards_data_path = Path("data/cards")

# %%
# download info

lookup_url = "https://api.scryfall.com/bulk-data"
bulk_requests_info = requests.get(lookup_url)
bulk_requests_info = bulk_requests_info.json()

# %%
# download cards data

oracl_card_info = [
    info for info in bulk_requests_info["data"] if info["type"] == "oracle_cards"
][0]
oracle_cards_url = oracl_card_info["download_uri"]
oracle_card_data = requests.get(oracle_cards_url)
oracle_card_data = oracle_card_data.json()


# %%
# download rulings

rulings_info = [
    info for info in bulk_requests_info["data"] if info["type"] == "rulings"
][0]
rulings_info_url = rulings_info["download_uri"]
rulings_data = requests.get(rulings_info_url)
rulings_data = rulings_data.json()


# %%
# combine

idx_2_card_data = {card_data["oracle_id"]: card_data for card_data in oracle_card_data}

for ruling in tqdm(rulings_data):
    oracle_id = ruling["oracle_id"]
    if "rulings" not in idx_2_card_data[oracle_id]:
        idx_2_card_data[oracle_id]["rulings"] = []
    idx_2_card_data[oracle_id]["rulings"].append(ruling["comment"])


# %%
# save all cards
BLOCKED_CARD_TYPES = ["Card", "Stickers", "Hero"]

processed_data = [
    card
    for card in idx_2_card_data.values()
    if (card["type_line"] not in BLOCKED_CARD_TYPES) and (card["layout"] == "normal")
]
print(f"saving cards data with {len(processed_data)} cards")
all_cards_file = Path("data/cards/scryfall_all_cards_with_rulings.json")

with all_cards_file.open("w", encoding="utf-8") as outfile:
    json.dump(processed_data, outfile)


# %%
# save sample

all_cards_sample_file = Path("data/cards/scryfall_all_cards_with_rulings_sample.json")
sample = random.choices(
    [card for card in processed_data if card.get("rulings", [])], k=10
)
with all_cards_sample_file.open("w", encoding="utf-8") as outfile:
    json.dump(sample, outfile)

# %%

print(
    "there are ",
    len([c for c in processed_data if c.get("rulings")]),
    "cards with rulings",
)

# %%
