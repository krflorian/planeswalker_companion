# %%
from pathlib import Path
from mtg.data_handler import CardDB

all_cards_file = Path("data/raw/scryfall_all_cards_with_rulings.json")
db = CardDB(all_cards_file)


# %%

text = "can i untap land cap when i have a counter on it?"
text = "what happens if i attack with a 1/1 deathouch creature and my opponent blocks with a 2/2 token?"
text = "how many cards named frodo can i put into my deck?"
text = "can i put frodo adventurous hobbit and frodo determined hero in the same deck?"
text = "what cards can i add to my chatterfang commander deck?"

message = db.create_message(text, role="user")
message.cards

# %%

print(message.processed_text)

# %%
import pickle

with open("data/artifacts/card_db.p", "wb") as outfile:
    pickle.dump(db, outfile)

# %%

import random

cards = [card for card in all_cards if "chatterfang" in card.name.lower()]
cards.extend([card for card in all_cards if "land cap" in card.name.lower()])
cards.extend([card for card in all_cards if "frodo" in card.name.lower()])
cards.extend(random.choices(all_cards, k=10))
all_cards = cards
