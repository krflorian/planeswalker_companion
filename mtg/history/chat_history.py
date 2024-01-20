from mtg.objects import Message, Rule
from mtg.utils.logging import get_logger
from .spacy_utils import match_cards
from .data_service import DataService

logger = get_logger(__name__)


class ChatHistory:
    def __init__(self, data_service_host: str = "127.0.0.1"):
        self.chat: list[Message] = []
        self.data_service = DataService(host=data_service_host)

    def add_message(self, message: Message):
        self.chat.append(message)

    def clear(self):
        self.chat = []

    def get_card_data(
        self,
        number_of_messages=2,
        max_number_of_cards=4,
        include_price: bool = False,
    ):
        """Get Card data from last n messages in text form."""
        card_data = ""
        cards = []
        for message in reversed(self.chat[-number_of_messages:]):
            cards.extend(message.cards)

        card_data += "\n\n".join(
            [
                card.to_text(include_price=include_price)
                for card in cards[:max_number_of_cards]
            ]
        )
        if card_data == "":
            card_data = "No Card Data."
        return card_data

    def get_rules_data(self, number_of_messages=4):
        rules = []
        for message in self.chat[-number_of_messages:]:
            if message.role == "user" and message.rules:
                rules.extend(message.rules)
                for card in message.cards:
                    rules.extend(card.rulings)

        if rules:
            return "\n".join([rule.to_text() for rule in rules])
        else:
            return "No Rules found"

    def get_human_readable_chat(self, number_of_messages=4) -> list[list[str, str]]:
        """Create Chat for display in gradio bot.

        Chat has to be in format list of lists. First message in the list is user second is bot.
        Example:
        chat = [[user, bot], [user, bot]]
        """
        chat = []
        last_message_role = None
        for message in self.chat[-number_of_messages:]:
            if message.role == "user":
                chat.append([message.processed_text])
            if message.role == "assistant":
                if not chat or (last_message_role == "assistant"):
                    chat.append([None, message.processed_text])
                else:
                    chat[-1].append(message.processed_text)
            last_message_role = message.role

        if len(chat[-1]) == 1:
            # no assistant message
            chat[-1].append(None)
        return chat

    def replace_card_names_with_urls(self, text, cards, role="user") -> str:
        """Find Card Names in text and replace them with their URL. Return only Cards that are found in the text."""

        if not cards:
            return text, cards

        doc = match_cards(text=text, cards=cards)
        text = ""
        filtered_cards = []
        for token in doc:
            if token.ent_type_:
                # add token as url
                card = [card for card in cards if token.ent_type_ == card.name][0]
                if card is None:
                    text += token.text
                else:
                    if card not in filtered_cards:
                        filtered_cards.append(card)
                    if role == "assistant":
                        text += f"[{token.text}]({card.image_url})"
                    else:
                        text += f"[{card.name}]({card.image_url})"
                text += token.whitespace_
            else:
                # add token as text
                text += token.text
                text += token.whitespace_

        return text, filtered_cards

    def create_message(
        self, text: str, role: str, include_rules: bool = False
    ) -> Message:
        """Creates processed text (card names as urls), card data and rules data. Only includes card data that is written in the text."""
        logger.info(f"creating message for {role}")

        # add card data
        if role == "assistant":
            k = 15
        else:
            k = 5
        all_cards = self.data_service.get_cards(text, k=k)

        processed_text, matched_cards = self.replace_card_names_with_urls(
            text=text, cards=all_cards, role=role
        )

        # add rules data
        rules = []
        if include_rules:
            # get rules from rulebook
            rules = self.data_service.get_rules(text)
            # get rules from keywords
            # TODO could be straight search not vector search
            keywords = []
            for card in matched_cards:
                keywords.extend(card.keywords)
            if keywords:
                rules.extend(self.data_service.get_rules(".".join(keywords)))

        # create message
        message = Message(
            text=text,
            role=role,
            processed_text=processed_text,
            cards=matched_cards,
            rules=rules,
        )
        logger.info(
            f"message created with {len(matched_cards)} cards and {len(rules)} rules"
        )

        return message

    def create_minimal_message(self, text: str, role: str) -> Message:
        return Message(text=text, role=role, processed_text=text)

    def add_additional_cards(
        self,
        message: Message,
        max_number_of_cards: int = 5,
        threshold: float = 0.5,
        lasso_threshold: float = 0.03,
    ) -> Message:
        additional_cards = []
        for card in message.cards:
            # for each card in message get max_number_of_cards
            additional_cards = self.data_service.get_cards(
                card.to_text(include_price=False),
                k=max_number_of_cards,  # TODO: could be more
                threshold=threshold,
                lasso_threshold=lasso_threshold,
                sample_results=True,
            )

        for card in additional_cards:
            if card not in message.cards:
                message.cards.append(card)
                logger.debug(f"added additional card: {card.name}")

        return message

    def validate_answer(self, number_of_messages=4):
        message = self.chat[-1]
        if message.role != "assistant":
            logger.debug("last chat message is not from assistant")
            return

        rules = []
        for message in self.chat[-number_of_messages:]:
            if message.role == "user" and message.rules:
                rules.extend(message.rules)
                for card in message.cards:
                    rules.extend(card.rulings)
                    for text in card.oracle.split("\n"):
                        rules.append(
                            Rule(text=text, chapter=card.name, rule_id="oracle text")
                        )

        logger.info(f"evaluating {len(rules)} against answer")
        validation_text, score = self.data_service.validate_answer(message.text, rules)

        logger.info(f"validation score {score:.2f}%")

        self.chat.append(
            Message(validation_text, role="assistant", processed_text=validation_text)
        )
