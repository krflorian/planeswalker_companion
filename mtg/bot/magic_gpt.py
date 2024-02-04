from pathlib import Path
from langchain.chains import LLMChain

from mtg.utils.logging import get_logger
from mtg.history import ChatHistory
from mtg.objects import MessageType
from .lang_chain import create_chains

logger = get_logger(__name__)


class MagicGPT:
    def __init__(
        self,
        chat_history: ChatHistory,
        model: str = "gpt-3.5-turbo",
        temperature_deck_building: int = 0.7,
        max_token_limit: int = 3000,
        max_responses: int = 1,
        data_filepath: Path = Path("data/messages"),
    ):
        (
            conversational_chat,
            deckbuilding_chat,
            rules_question_chat,
            memory,
        ) = create_chains(
            model=model,
            temperature_deck_building=temperature_deck_building,
            max_token_limit=max_token_limit,
            max_responses=max_responses,
        )

        self.data_filepath: Path = data_filepath
        (self.data_filepath / "liked").mkdir(exist_ok=True)
        (self.data_filepath / "disliked").mkdir(exist_ok=True)

        self.chat_history: ChatHistory = chat_history
        self.memory = memory
        self.conversational_chat: LLMChain = conversational_chat
        self.deckbuilding_chat: LLMChain = deckbuilding_chat
        self.rules_question_chat: LLMChain = rules_question_chat
        self.conversation_topic: str = None  # TODO should be ENUM

    def clear_memory(self):
        self.memory.clear()
        self.chat_history.clear()
        logger.info("memory cleared")

    def process_user_query(self, query):
        self.chat_history.add_user_message(query)
        chat = self.chat_history.get_human_readable_chat(number_of_messages=6)

        return chat

    def ask(self):
        try:
            topic = self.chat_history.conversation_topic
            if topic == MessageType.DECKBUILDING:
                response_iterator = self._ask_deckbuilding_question()
            elif topic == MessageType.RULES:
                response_iterator = self._ask_rules_question()
            else:
                response_iterator = self._ask_conversational_question()

            # stream response
            for response in response_iterator:
                message = self.chat_history.create_minimal_message(
                    text=response, type=MessageType.ASSISTANT
                )
                if not self.chat_history.chat:
                    self.chat_history.chat.append(message)
                elif self.chat_history.chat[-1].type != MessageType.ASSISTANT:
                    self.chat_history.chat.append(message)
                else:
                    self.chat_history.chat[-1] = message
                chat = self.chat_history.get_human_readable_chat(number_of_messages=6)
                yield chat

            # create final message
            message = self.chat_history.create_message(
                response, message_type=MessageType.ASSISTANT
            )
            self.chat_history.chat[-1] = message
            chat = self.chat_history.get_human_readable_chat(number_of_messages=6)
            self.memory.save_context(
                inputs={"human_input": self.chat_history.chat[-2].text},
                outputs={"assistant": self.chat_history.chat[-1].text},
            )
            yield chat

            # check rules
            if topic == MessageType.RULES:
                self.chat_history.validate_answer()
                chat = self.chat_history.get_human_readable_chat(number_of_messages=6)
                yield chat

        except Exception as e:
            logger.exception(e)
            self.clear_memory()

            yield [
                [
                    None,
                    f"Something went wrong, I am restarting. Please ask the question again.",
                ]
            ]

    def _ask_conversational_question(self) -> str:
        logger.info("invoking conversational chain")

        card_data = self.chat_history.get_card_data(
            number_of_messages=2,
            max_number_of_cards=6,
            include_price=True,
        )

        partial_message = ""
        for response in self.conversational_chat.stream(
            {
                "human_input": self.chat_history.chat[-1].text,
                "card_data": card_data,
                "user_intent": self.chat_history.intent,
            }
        ):
            partial_message += response.content
            yield partial_message

    def _ask_deckbuilding_question(self) -> str:
        logger.info("invoking deck building chain")

        card_data = self.chat_history.get_card_data(
            number_of_messages=1,
            max_number_of_cards=12,
            include_price=True,
        )

        partial_message = ""
        for response in self.deckbuilding_chat.stream(
            {"human_input": self.chat_history.chat[-1].text, "card_data": card_data}
        ):
            partial_message += response.content
            yield partial_message

    def _ask_rules_question(self):
        logger.info("invoking rules chain")

        card_data = self.chat_history.get_card_data(
            number_of_messages=2,
            max_number_of_cards=6,
            include_price=False,
        )
        rules_data = self.chat_history.get_rules_data()

        # TODO add rules data
        print("starting stream...")
        partial_message = ""
        for response in self.rules_question_chat.stream(
            {
                "human_input": self.chat_history.chat[-1].text,
                "card_data": card_data,
                "rules_data": rules_data,
            }
        ):
            partial_message += response.content
            yield partial_message

    def save_chat(self, liked: bool, message_index: list[int]) -> None:
        print("message index ", message_index)
        if liked:
            self.chat_history.dump(self.data_filepath / "liked")
        else:
            self.chat_history.dump(self.data_filepath / "disliked")
