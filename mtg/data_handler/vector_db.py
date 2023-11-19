import hnswlib
import openai
import numpy as np
from tqdm import tqdm
import re

from mtg.utils import get_openai_api_key
from mtg.utils.logging import get_logger

logger = get_logger(__name__)

openai.api_key = get_openai_api_key()


class VectorDB:
    def __init__(self, labels_and_texts: list[tuple[str, str]]):
        """Initialize HNSW Graph.

        Infos and Documentation: https://github.com/nmslib/hnswlib
        """
        self.graph: hnswlib.Index = None
        self.ids_2_labels: dict[int, str] = None

        labels_and_embeddings = self.get_embeddings(labels_and_texts)
        self.create_graph(labels_and_embeddings=labels_and_embeddings)

    def get_embeddings(
        self, labels_and_texts: list[tuple[str, str]]
    ) -> tuple[str, np.ndarray]:
        labels_and_embeddings = []
        logger.info(f"Vector DB: adding {len(labels_and_texts)} embeddings")
        for label, text in tqdm(labels_and_texts):
            try:
                embeddings = self.vectorize_text(text)
                labels_and_embeddings.append((label, np.array(embeddings)))
            except:
                # when TimeOut return current list
                logger.info(
                    f"Vector DB: downloaded {len(labels_and_embeddings)} embeddings"
                )
                return labels_and_embeddings
        return labels_and_embeddings

    def create_graph(
        self,
        labels_and_embeddings: list[tuple[str, np.ndarray]],
        ef: int = 10000,
        M: int = 16,
    ) -> None:
        """Create the Search Graph.

        Parameters:
            labels_and_embeddings: a list of tuples (label, vector)
            ef: parameter that controls speed/accuracy trade-off during the index construction
            M: parameter that defines the maximum number of outgoing connections in the graph
        """
        # Generating sample data
        if not labels_and_embeddings:
            return
        labels, embeddings = zip(*labels_and_embeddings)
        data = np.array(embeddings)
        ids = np.arange(len(data))

        # Declaring index
        graph = hnswlib.Index(space="cosine", dim=len(data[0]))
        graph.init_index(max_elements=len(embeddings), ef_construction=ef, M=M)
        graph.add_items(data, ids)
        graph.set_ef(ef)

        self.graph = graph
        self.ids_2_labels = {idx: label for idx, label in zip(ids, labels)}

        return

    def add(self, labels_and_embeddings) -> None:
        """Add labels and embeddings to the Search Graph."""
        labels, embeddings = zip(*labels_and_embeddings)
        old_index_size = self.graph.get_max_elements()
        new_index_size = old_index_size + len(labels_and_embeddings)
        idxs = [old_index_size + i for i in range(len(embeddings))]

        self.graph.resize_index(new_index_size)
        self.graph.add_items(data=embeddings, ids=idxs)
        self.ids_2_labels.update({idx: label for idx, label in zip(idxs, labels)})

    def query(
        self,
        text: str,
        k: int = 5,
        threshold=0.2,
        lasso_threshold: int = 0.02,
        split_pattern: str = "\.|\?",
    ) -> list[str, float]:
        """Search for similar entries in Vector DB.

        Parameters:
            text: query text
            k: how many results should be returned
            threshhold: what is the max distance for the search query
            lasso_threshold: distance between most similar and everything else
            split_pattern: how the query text is processed

        Returns: a list of entries in the vector db and their distance to the search query text.
        """
        search_results = []
        sentences = [s for s in re.split(split_pattern, text) if s != ""]
        for sentence in sentences:
            embedding = self.vectorize_text(sentence)
            idxs, distances = self.graph.knn_query(embedding, k=k)

            baseline_distance = distances[0][0]
            for idx, distance in zip(idxs[0], distances[0]):
                if (distance - baseline_distance < lasso_threshold) and (
                    distance < threshold
                ):
                    search_results.append((self.ids_2_labels.get(idx, None), distance))

        search_results = sorted(search_results, key=lambda x: x[1])[:k]
        print(search_results)
        return search_results

    def vectorize_text(self, text: str) -> np.ndarray:
        """Create a np.array from text."""
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        embedding = np.array(response["data"][0]["embedding"])
        return embedding

    def sample_results(self, search_results: tuple[str, float], k: 5) -> list[str]:
        """Create a random sample of the results weighted with their distance to the search query."""

        if not search_results:
            return []

        k = min(k, len(search_results))
        weights = [result[1] for result in search_results]
        normalized_weights = normalize_weights(weights)

        return list(
            np.random.choice(
                [result[0] for result in search_results],
                size=k,
                replace=False,
                p=normalized_weights,
            )
        )


def normalize_weights(weights):
    normalized_weights = np.array(weights) / np.sum(weights)

    # Check if the sum is exactly 1
    if not np.isclose(np.sum(normalized_weights), 1.0):
        # Adjust the last element to make the sum exactly 1
        normalized_weights[-1] += 1.0 - np.sum(normalized_weights)

    return normalized_weights
