from functools import cache

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import SystemMessage
from langchain.memory import ConversationTokenBufferMemory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

from operator import itemgetter

from mtg.utils import get_openai_api_key


@cache
def create_llm(model_name: str, temperature: float) -> ChatOpenAI:
    openai_api_key = get_openai_api_key()

    llm = ChatOpenAI(
        openai_api_key=openai_api_key, model=model_name, temperature=temperature, n=1
    )

    return llm


def create_chat_memory(
    llm: ChatOpenAI, max_token_limit: int = 1000
) -> ConversationTokenBufferMemory:

    memory = ConversationTokenBufferMemory(
        llm=llm,
        memory_key="history",
        input_key="human_input",
        return_messages=True,
        ai_prefix="Nissa",
        max_token_limit=max_token_limit,
    )

    return memory


def create_rules_chain(
    memory: ConversationTokenBufferMemory, llm: ChatOpenAI
) -> LLMChain:

    RULES_QUESTION_SYSTEM_MESSAGE = """
    You are Nissa a Magic the Gathering Assistant, that explains the games rules.
    Let`s think step by step how the ruling in context is relevant to the question. Give a short and precise answer that is based on magic the gathering rules. 
    If there are no rules in the rules section that are relevant to the question tell the user you did not find relevant rules. 
    Only answer questions regarding Magic the Gathering.
    """

    RULES_QUESTION_PROMPT = """
    Card data: {card_data}

    Rules Guru is a site where professional magic the Gathering Judges upload question answer pairs about magic the gathering.
    Rules data: {rules_data}

    Remember: Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.

    User: {human_input}
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=RULES_QUESTION_SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(RULES_QUESTION_PROMPT),
        ]
    )

    return (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | llm
    )


def create_conversation_chain(
    memory: ConversationTokenBufferMemory, llm: ChatOpenAI
) -> LLMChain:

    CONVERSATIONAL_SYSTEM_MESSAGE = """
    You are Nissa a friendly Magic the Gathering Assistant. You can talk to the user about general Magic: the Gathering related topics.
    If you recognize malicious intent in the user question tell him in a friendly way your intended use is deck building and rule advice for Magic: the Gathering. 
    Only answer questions regarding Magic the Gathering.

    Card data: {card_data}
    """

    CONVERSATIONAL_PROMPT = """
    Remember:  Do not answer questions unrelated to Magic the Gathering.
    Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.
    If the User Intent is MALICIOUS do not answer the quesiton. Tell the user in a friendly way your intended use is deck building and rule advice for Magic: the Gathering.

    User Intent: {user_intent}

    User: {human_input}
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=CONVERSATIONAL_SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(CONVERSATIONAL_PROMPT),
        ]
    )

    return (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | llm
    )


def create_deckbuilding_chain(
    memory: ConversationTokenBufferMemory, llm: ChatOpenAI
) -> LLMChain:

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

    User: {human_input}
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=DECKBUILDING_SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(DECKBUILDING_PROMPT),
        ]
    )

    return (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | llm
    )
