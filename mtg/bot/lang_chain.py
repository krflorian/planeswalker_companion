from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationTokenBufferMemory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from operator import itemgetter

from mtg.utils import get_openai_api_key
from mtg.utils.logging import get_logger

openai_api_key = get_openai_api_key()
logger = get_logger(__name__)


CONVERSATIONAL_SYSTEM_MESSAGE = """
You are Nissa a friendly Magic the Gathering Assistant. You can talk to the user about general Magic: the Gathering related topics.
If you recognize malicious intent in the user question tell him in a friendly way your intended use is deck building and rule advice for Magic: the Gathering. 
Only answer questions regarding Magic the Gathering.
"""

CONVERSATIONAL_PROMPT = """
Card data: {card_data}

Remember:  Do not answer questions unrelated to Magic the Gathering.
Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.
If the User Intent is MALICIOUS do not answer the quesiton. Tell him in a friendly way your intended use is deck building and rule advice for Magic: the Gathering.

User Intent: {user_intent}

User: {human_input}
"""


DECKBUILDING_SYSTEM_MESSAGE = """
You are Nissa a Magic the Gathering Assistant that helps with deckbuilding. Give your advice on which cards are best for the users deck.
Let`s think step by step which cards are best for the users deck. Take the cards in context as suggestions and include them if they make sense in the deck.
In commander all cards in a deck cannot be of a different collor then the color identity of the commander.
Give a short and precise description of the cards and why they are relevant. 
Only answer questions regarding Magic the Gathering.
"""

DECKBUILDING_PROMPT = """
Card data: {card_data}

Remember:  Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.

{human_input}
"""


RULES_QUESTION_SYSTEM_MESSAGE = """
You are Nissa a Magic the Gathering Assistant, that explains the games rules.
Let`s think step by step how the ruling in context is relevant to the question. Give a short and precise answer that is based on magic the gathering rules. 
If there are no rules in the rules section that are relevant to the question tell the user you did not find relevant rules. 
Only answer questions regarding Magic the Gathering.
"""

RULES_QUESTION_PROMPT = """
Card data: {card_data}

Rules: {rules_data}

Remember: Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.

{human_input}
"""


def create_chains(
    model: str = "gpt-3.5-turbo",
    temperature_deck_building: int = 0.7,
    max_token_limit: int = 3000,
    max_responses=1,
):
    """Create llm chains: Topic Classifier, Deckbuilding Chat, Rules Question Chat.
    params:
        model: gpt model version
        temperature: how "creative" the answer should be (1 is deterministic, 0 is very creative)
        max_token_limit: the maximum limit for number of tokens held in memory
        max_responses: how many responses should be created for one question by the llm

    returns:
        Classifier Chain: takes text returns one of ["deck building", "rules question"]
        Deckbuilding Chat: takes text and card data and returns text
        Rules Question Chat: takes text, card data and rules data and returns text
    """
    conversational_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=CONVERSATIONAL_SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(CONVERSATIONAL_PROMPT),
        ]
    )

    deckbuilding_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=DECKBUILDING_SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(DECKBUILDING_PROMPT),
        ]
    )

    rules_question_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=RULES_QUESTION_SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(RULES_QUESTION_PROMPT),
        ]
    )

    # rules
    rules_llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model=model,
        temperature=1,
        n=max_responses,
        verbose=True,
    )

    # memory
    memory = ConversationTokenBufferMemory(
        llm=rules_llm,
        memory_key="history",
        input_key="human_input",
        return_messages=True,
        ai_prefix="Nissa",
        max_token_limit=max_token_limit,
    )

    rules_question_chat = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | rules_question_prompt
        | rules_llm
    )

    # conversational
    conversational_llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model=model,
        temperature=0.5,
        n=max_responses,
        verbose=True,
    )

    conversational_chat = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | conversational_prompt
        | conversational_llm
    )

    # deckbuilding
    deck_llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model=model,
        temperature=temperature_deck_building,
        n=max_responses,
        verbose=True,
    )

    deckbuilding_chat = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | deckbuilding_prompt
        | deck_llm
    )

    logger.info("created all chains...")

    return conversational_chat, deckbuilding_chat, rules_question_chat, memory
