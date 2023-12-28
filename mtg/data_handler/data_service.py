import requests
from mtg.objects import Card, Rule
from mtg.utils.logging import get_logger

logger = get_logger(__name__)

# TODO make async calls


class DataService:
    url = "http://127.0.0.1:8000/"

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
    ):
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
