import random
import json
from uuid import uuid4
from pathlib import Path

from mtg.objects import Message, MessageType, Document
from mtg.utils.logging import get_logger
from .spacy_utils import match_cards
from .data_service import DataService

logger = get_logger(__name__)


class ChatHistory:
    def __init__(self, data_service_host: str = "127.0.0.1"):
        self.chat: list[Message] = []
        self.data_service = DataService(host=data_service_host)
        self.intent = MessageType.CONVERSATION

    @property
    def conversation_topic(self):
        if self.chat:
            return self.chat[-1].type
        logger.debug("did not find a conversation topic")
        return "conversation"

    def add_message(self, message: Message):
        self.chat.append(message)

    def add_user_message(self, query: str) -> None:
        intent = self.classify_intent(
            query  # TODO should be chat instead of last message
        )
        message = self.create_message(query, message_type=intent)
        self.add_message(message)

    def add_assistant_message(self, text: str) -> None:
        message = self.create_message(text, message_type=MessageType.ASSISTANT)
        self.add_message(message)

    def clear(self):
        self.chat = []

    def dump(self, filepath: Path):
        filename = filepath / f"{str(uuid4())}.json"
        logger.info(f"saving chat in {filename}")
        with filename.open("w", encoding="utf-8") as outfile:
            json.dump(
                [message.to_dict() for message in self.chat],
                outfile,
                ensure_ascii=False,
            )

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

    def get_rules_data(self, number_of_messages=4) -> list[str]:
        rule_texts, rule_ids = [], set()
        for message in self.chat[-number_of_messages:]:
            if message.type != MessageType.RULES:
                continue
            for rule in message.rules:
                if rule.name not in rule_ids:
                    rule_ids.add(rule.name)
                    rule_texts.append(rule.text)
            for card in message.cards:
                if card.rulings and card.name not in rule_ids:
                    rule_ids.add(card.name)
                    rule_texts.append(f"Rulings for card {card.name}:")
                    for rule in card.rulings:
                        rule_texts.extend([rule.text for rule in card.rulings])

        if rule_texts:
            return "\n".join(rule_texts)
        else:
            return "No Rules found"

    def get_human_readable_chat(self, number_of_messages=4) -> list[list[str, str]]:
        """Create Chat for display in gradio bot.

        Chat has to be in format list of lists. First message in the list is user second is bot.
        Example:
        chat = [[user, bot], [user, bot]]
        """
        chat = []
        last_message_type = None
        for message in self.chat[-number_of_messages:]:
            if message.type == MessageType.ASSISTANT:
                if not chat or (last_message_type == MessageType.ASSISTANT):
                    chat.append([None, message.processed_text])
                else:
                    chat[-1].append(message.processed_text)
            else:
                chat.append([message.processed_text])
            last_message_type = message.type

        if len(chat[-1]) == 1:
            # no assistant message
            chat[-1].append(None)
        return chat

    def replace_card_names_with_urls(self, text, cards, message_type) -> str:
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
                    if message_type == MessageType.ASSISTANT:
                        text += f"[{token.text}]({card.url})"
                    else:
                        text += f"[{card.name}]({card.url})"
                text += token.whitespace_
            else:
                # add token as text
                text += token.text
                text += token.whitespace_

        return text, filtered_cards

    def create_message(self, text: str, message_type: MessageType) -> Message:
        """Creates processed text (card names as urls), card data and rules data. Only includes card data that is written in the text."""
        logger.info(f"creating {message_type} message")

        # add card data
        if message_type == MessageType.ASSISTANT:
            k = 15
        else:
            k = 5
        all_cards = self.data_service.get_cards(text, k=k)

        processed_text, matched_cards = self.replace_card_names_with_urls(
            text=text, cards=all_cards, message_type=message_type
        )

        # add rules data
        rules = []
        if message_type == MessageType.RULES:
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
            type=message_type,
            processed_text=processed_text,
            cards=matched_cards,
            rules=rules,
        )

        # add additional cards
        if message_type == MessageType.DECKBUILDING:
            message = self.add_additional_cards(message=message, max_number_of_cards=10)

        logger.info(
            f"message created with {len(message.cards)} cards and {len(message.rules)} rules"
        )

        return message

    def create_minimal_message(self, text: str, type: str) -> Message:
        return Message(text=text, type=type, processed_text=text)

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
            additional_cards.extend(
                self.data_service.get_cards(
                    card.to_text(include_price=False),
                    k=5,  # TODO: could be more
                    threshold=threshold,
                    lasso_threshold=lasso_threshold,
                    sample_results=True,
                )
            )

        # from message
        additional_cards.extend(
            self.data_service.get_cards(
                message.text,
                k=max(10, max_number_of_cards),
                threshold=threshold,
                lasso_threshold=lasso_threshold,
                sample_results=True,
            )
        )

        # choose cards
        cards = []
        for card in additional_cards:
            if card not in message.cards and not card in cards:
                cards.append(card)
        cards = random.choices(cards, k=min(len(cards), max_number_of_cards))

        # add additional cards
        message.cards.extend(cards)
        logger.debug(f"added {len(cards)} additional cards")

        return message

    def validate_answer(self, number_of_messages=4):
        message = self.chat[-1]
        if message.type != MessageType.ASSISTANT:
            logger.debug("last chat message is not from assistant")
            return

        documents, rule_ids = [], set()
        for message in self.chat[-number_of_messages:]:
            # add message rules
            for document in message.rules:
                if document.name not in rule_ids:
                    rule_ids.add(document.name)
                    documents.append(document)
            # add message cards
            for card in message.cards:
                if card.name not in rule_ids:
                    rule_ids.add(card.name)
                    documents.extend(card.rulings)
                    for idx, text in enumerate(card.oracle.split("\n")):
                        documents.append(
                            Document(
                                text=text,
                                name=f"Oracle Text {idx} - {card.name}",
                                url=card.url,
                            )
                        )

        logger.info(f"evaluating {len(documents)} against answer")
        validation_text, score = self.data_service.validate_answer(
            message.text, documents
        )

        logger.info(f"validation score {score:.2f}%")

        self.chat.append(
            Message(
                validation_text,
                type=MessageType.ASSISTANT,
                processed_text=validation_text,
            )
        )

    def classify_intent(self, query) -> MessageType:
        """possible values: deckbuilding, rules, conversation, malevolent"""

        intent = self.data_service.classify_intent(query)
        intent = MessageType(intent)
        self.intent = intent
        return intent
