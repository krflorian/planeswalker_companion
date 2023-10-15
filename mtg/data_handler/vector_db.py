import os
import yaml
import logging
import hnswlib
import openai
import numpy as np
from tqdm import tqdm

from mtg.objects import Card

try:
    with open("config/config.yaml", "r") as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    openai.api_key = config.get("open_ai_token")
    logging.info("loaded open ai token from config file ")
except:
    logging.warn("did not find config file")
    openai.api_key = os.environ["open_ai_token"]
    logging.info("loaded open ai token from environment")


class VectorDB:
    def __init__(self, cards: list[Card]):
        # TODO should not be cards but list of str
        self.graph: hnswlib.Index = None
        self.ids_2_card_name: dict[int, str] = None

        names_and_embeddings = self.get_embeddings(cards)
        self.create_graph(names_and_embeddings=names_and_embeddings)

    def get_embeddings(self, cards: list[Card]) -> tuple[str, np.ndarray]:
        names_and_embeddings = []
        print(f"adding {len(cards)} embeddings")
        for card in tqdm(cards):
            try:
                response = openai.Embedding.create(
                    input=card.to_text(), model="text-embedding-ada-002"
                )
                embeddings = response["data"][0]["embedding"]
                names_and_embeddings.append((card.name, np.array(embeddings)))
            except:
                print(f"downloaded {len(names_and_embeddings)} embeddings")
                return names_and_embeddings
        return names_and_embeddings

    def create_graph(
        self, names_and_embeddings: tuple[str, np.ndarray], ef: int = 10000, M: int = 16
    ) -> None:
        # Generating sample data
        names, embeddings = zip(*names_and_embeddings)
        data = np.array(embeddings)
        ids = np.arange(len(data))

        # Declaring index
        graph = hnswlib.Index(space="cosine", dim=len(data[0]))
        graph.init_index(max_elements=len(embeddings), ef_construction=ef, M=M)
        graph.add_items(data, ids)
        graph.set_ef(ef)

        self.graph = graph
        self.ids_2_card_name = {idx: name for idx, name in zip(ids, names)}

        return

    def add(self, names_and_embeddings) -> None:
        names, embeddings = zip(*names_and_embeddings)
        old_index_size = self.graph.get_max_elements()
        new_index_size = old_index_size + len(names_and_embeddings)
        idxs = [old_index_size + i for i in range(len(embeddings))]

        self.graph.resize_index(new_index_size)
        self.graph.add_items(data=embeddings, ids=idxs)
        self.ids_2_card_name.update({i: name for i, name in zip(idxs, names)})

    def query(
        self, text: str, k: int = 3, threshhold=0.2, lasso_threshhold: int = 0.02
    ):
        card_names = set()
        sentences = text.split(".")
        for sentence in sentences:
            response = openai.Embedding.create(
                input=sentence, model="text-embedding-ada-002"
            )
            embedding = response["data"][0]["embedding"]
            labels, distances = self.graph.knn_query(np.array(embedding), k=k)

            initial_distance = distances[0][0]
            for label, distance in zip(labels[0], distances[0]):
                if (distance - initial_distance > lasso_threshhold) or (
                    distance > threshhold
                ):
                    break
                card_name = self.ids_2_card_name.get(label, None)
                print(f"adding {card_name} - distance {distance}")
                card_names.add(card_name)

        return list(card_names)
