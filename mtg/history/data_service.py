import requests
from mtg.objects import Card, Document
from mtg.utils.logging import get_logger

logger = get_logger(__name__)


# TODO make async calls
class DataService:
    def __init__(self, host: str):
        self.url = f"http://{host}:8000/"

    def get_rules(
        self,
        question: str,
        k: int = 5,
        threshold: float = 0.2,
        lasso_threshold: float = 0.05,
    ) -> list[Document]:
        response = requests.post(
            self.url + "rules/",
            json={
                "text": question,
                "k": k,
                "threshold": threshold,
                "lasso_threshold": lasso_threshold,
            },
        )
        response = response.json()

        documents = []
        for resp in response:
            document = resp["document"]
            distance = resp["distance"]
            document = Document(**document)
            logger.debug(f"received rule {document.name} distance {distance:.2f}")
            documents.append(document)

        return documents

    def get_cards(
        self,
        question: str,
        k: int = 5,
        threshold: float = 0.4,
        lasso_threshold: float = 0.1,
        sample_results: bool = False,
    ) -> list[Card]:
        response = requests.post(
            self.url + "cards/",
            json={
                "text": question,
                "k": k,
                "threshold": threshold,
                "lasso_threshold": lasso_threshold,
                "sample_results": sample_results,
            },
        )
        response = response.json()

        cards = []
        for card in response:
            card_data = card["card"]
            distance = card["distance"]
            card = Card(**card_data)
            logger.debug(f"received card {card.name} distance {distance:.2f}")
            cards.append(card)

        return cards

    def validate_answer(
        self, answer: str, documents: list[Document]
    ) -> tuple[str, float]:
        if not documents:
            return (
                "I could not find any relevant rules for this question",
                0.0,
            )

        response = requests.post(
            self.url + "hallucination/",
            json={
                "text": answer,
                "chunks": [doc.text for doc in documents],
            },
        )
        response = response.json()
        relevant_documents = []
        for idx, chunk in enumerate(response):
            logger.debug(
                f"hallucination score: {chunk['score']:2f}, ID: {documents[idx].name}"
            )
            relevant_documents.append((chunk["score"], documents[idx]))

        relevant_documents = [doc for doc in relevant_documents if doc[0] >= 0.5]
        relevant_documents = sorted(
            relevant_documents, key=lambda x: x[0], reverse=True
        )[:5]

        # validation text
        validation_text = [
            "Attention! The documents I found do not match with my answer."
        ]
        score = 0.0
        if relevant_documents:
            score = relevant_documents[0][0]
            if score >= 0.8 and len(relevant_documents) > 1:
                validation_text = [
                    f"I am very confident in my answer ({score*100:.2f}%). It is based on:"
                ]

            elif score >= 0.5:
                validation_text = [
                    f"I am pretty sure this is true ({score*100:.2f}%). If you want to double check, my answer is based on:"
                ]

            for score, doc in relevant_documents:
                validation_text.append(f"- [{doc.name}]({doc.url})")

        else:
            for doc in documents:
                validation_text.append(f"- [{doc.name}]({doc.url})")

        # finish text
        validation_text = "\n".join(validation_text)
        return validation_text, score
