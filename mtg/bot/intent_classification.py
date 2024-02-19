# %%

from langchain.pydantic_v1 import BaseModel
from typing import Literal

from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.utils.openai_functions import convert_pydantic_to_openai_function

from mtg.objects.message import MessageType


# INTENT CLASSIFIER
INTENT_MAPPER = {
    "rules_question": MessageType.RULES,
    "card_info": MessageType.DECKBUILDING,
    "deck_building": MessageType.DECKBUILDING,
    "greeting": MessageType.CONVERSATION,
    "game_info": MessageType.CONVERSATION,
    "illegal": MessageType.MALICIOUS,
    "cheating": MessageType.MALICIOUS,
    "generate_code": MessageType.MALICIOUS,
}


class TopicClassifier(BaseModel):
    """
    This classifier organizes user queries for a Magic the Gathering Assistant into specific topics for precise responses. The topics are:

    - rules_question: Inquiries about game rules or mechanics.
    - deck_building: Advice on building decks.
    - card_info: Information on specific cards.
    - greeting: Basic conversational interactions.
    - game_info: General information about the game.
    - illegal: Questions on banned practices.
    - cheating: Concerns regarding unfair play.
    - generate_code: Requests for coding related to the game.

    This classification scheme ensures that the assistant can provide specific, relevant information across a broad spectrum of topics related to Magic the Gathering, enhancing the user's experience and engagement with the game.
    """

    topic: Literal[
        "rules_question",
        "deck_building",
        "card_info",
        "greeting",
        "game_info",
        "illegal",
        "cheating",
        "generate_code",
    ]
    """The topic of the user question"""


def create_intent_classifier(llm):

    classifier_function = convert_pydantic_to_openai_function(TopicClassifier)
    classifier = llm.bind(
        functions=[classifier_function], function_call={"name": "TopicClassifier"}
    )
    parser = PydanticAttrOutputFunctionsParser(
        attr_name="topic",
        pydantic_schema=TopicClassifier,
    )

    return classifier | parser
