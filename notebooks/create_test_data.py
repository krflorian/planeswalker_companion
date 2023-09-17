# %%
import json


with open("data/raw/scryfall_all_cards.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# %%

TEST_NAMES = [
    "Commandeer",
    "Fling",
    "Chatterfang, Squirrel General",
    "Nekusar, the Mindrazer",
    "Void Winnower",
    "Moonshaker Cavalry",
    "Craterhoof Behemoth",
]

test_data = [d for d in data if d["name"] in TEST_NAMES]
len(test_data)

# %%
with open("tests/data/cards.json", "w", encoding="utf-8") as outfile:
    json.dump(test_data, outfile)
