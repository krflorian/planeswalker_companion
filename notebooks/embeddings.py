# %%
from pathlib import Path
from mtg.data_handler import CardDB
from mtg.data_handler.vector_db import VectorDB
import pickle
import numpy as np

vector_db_file = Path("data/artifacts/card_vector_db.p")


# %%

with vector_db_file.open("rb") as infile:
    card_vector_db = pickle.load(infile)

# %%

labels_and_embeddings = []
for idx, card_name in card_vector_db.ids_2_labels.items():
    embedding = card_vector_db.graph.get_items([idx])
    embedding = np.array(embedding[0])
    labels_and_embeddings.append((card_name, embedding))

labels_and_embeddings[17]
# %%

vector_db = VectorDB([])
vector_db.create_graph(labels_and_embeddings=labels_and_embeddings)
vector_db.query("what cards add to my chatterfang deck?", threshold=0.3)

# %%

with vector_db_file.open("wb") as outfile:
    pickle.dump(vector_db, outfile)

# %%

with vector_db_file.open("rb") as infile:
    card_vector_db = pickle.load(infile)

# %%

card_vector_db.query("what cards add to my chatterfang deck?", k=10, threshold=0.5)
