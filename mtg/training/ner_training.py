# %%
from mtg.training.process_data import process_reddit_cards_data

data = process_reddit_cards_data(csv_file="data/raw/reddit/reddit_2019.csv")


# %%

test = [d for d in data if "u/mtgcardfetcher" in d["text"]]
test

# %%
import json

with open("data/processed/reddit/reddit_2019.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

data[0]


# %%
from tqdm import tqdm
import random

import spacy
from spacy.training import Example
from spacy.util import minibatch

EPOCHS = 20
BATCH_SIZE = 32

nlp = spacy.load("en_core_web_lg")

# create training data

label = "MTG_CARD"
training_data = []
for sample in data:
    entity_dict = {
        "entities": [
            (entity["start"], entity["end"], label) for entity in sample["entities"]
        ]
    }
    try:
        training_data_sample = Example.from_dict(
            nlp.make_doc(sample["text"]), entity_dict
        )
        training_data.append(training_data_sample)
    except:
        print(sample)

print(f"collected {len(training_data)} Training samples")

# %%


nlp.get_pipe("ner").add_label(label)

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.select_pipes(disable=other_pipes):  # only train NER
    optimizer = nlp.begin_training()
    for epoch in tqdm(range(EPOCHS)):
        random.shuffle(training_data)
        losses = {}
        batches = minibatch(training_data, BATCH_SIZE)
        for batch in batches:
            nlp.update(batch, drop=0.5, sgd=optimizer, losses=losses)
        print("loss:", losses["ner"])


# %%

texts = ["If I have "]

doc = nlp("what cards are similar to Bootleggers` Stash")

[(ent.text, ent.label_) for ent in doc.ents]

# %%
