import requests
from mtg.objects import Card, Rule
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
    ):
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

        rules = []
        for rule in response:
            rule_data = rule["rule"]
            distance = rule["distance"]
            rule = Rule(**rule_data)
            logger.debug(
                f"received rule {rule.rule_id} from chapter {rule.chapter} distance {distance:.2f}"
            )
            rules.append(rule)

        return rules

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

    def validate_answer(self, answer: str, rules: list[Rule]) -> tuple[str, float]:
        if not rules:
            return (
                "I could not find any relevant rules for this question",
                0.0,
            )

        rule_texts = [rule.to_text() for rule in rules]
        response = requests.post(
            self.url + "hallucination/",
            json={
                "text": answer,
                "chunks": rule_texts,
            },
        )
        response = response.json()
        relevant_rules = []
        for idx, chunk in enumerate(response):
            logger.debug(
                f"hallucination score: {chunk['score']:2f}, ID: {rules[idx].rule_id} {rules[idx].chapter}"
            )
            relevant_rules.append((chunk["score"], rules[idx]))
        relevant_rules = sorted(relevant_rules, key=lambda x: x[0], reverse=True)[:3]

        if relevant_rules[0][0] >= 0.8:
            validation_text = f"I am very confident in my answer ({relevant_rules[0][0]*100:.2f}%). It is based on: \n"
        elif relevant_rules[0][0] >= 0.5:
            validation_text = f"I am pretty sure this is true ({relevant_rules[0][0]*100:.2f}%). If you want to double check, my answer is based on: \n"
        else:
            validation_text = "I could not find any relevant rules in my database. The most fitting are: \n"

        # TODO threshold for relevant rules
        for score, rule in relevant_rules:
            validation_text += f" - {rule.chapter}: "
            if rule.subchapter:
                validation_text += f"{rule.subchapter}, "
            validation_text += f"{rule.rule_id}\n"

        return validation_text, relevant_rules[0][0]

    def classify_intent(self, text: str) -> str:
        response = requests.post(
            self.url + "nli/",
            json={
                "text": text,
            },
        )
        response = response.json()
        logger.info(
            f"question classified as {response['intent']}: {response['score']:.2f}"
        )
        return response["intent"]
