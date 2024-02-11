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
    "illegal": MessageType.MALICIOUS,
    "cheating": MessageType.MALICIOUS,
    "generate_code": MessageType.MALICIOUS,
}


class TopicClassifier(BaseModel):
    "You are a Magic the Gathering Assistant classify the topic of the user question"

    topic: Literal[
        "rules_question",
        "deck_building",
        "card_info",
        "greeting",
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
