# %%
from langchain.schema.agent import AgentFinish
from langchain.agents import tool

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.format_scratchpad import format_to_openai_functions

from langchain.agents import AgentExecutor
from langchain.schema.runnable import RunnablePassthrough

from mtg.objects import Card, Document

import requests


# %%
# data service

import aiohttp
from langchain.tools import BaseTool

from pydantic import BaseModel, Field

from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from mtg.utils.logging import get_logger

logger = get_logger(__name__)


@tool()
async def search_cards(query: str, include_price: bool = False) -> str:
    """Search for cards in a magic the gathering card database with all cards up to 14.05.2024. You will receive all card info including card specific rulings, attributes and price"""

    print("searching for cards with query: ", query)
    url = f"http://localhost:8000/"
    k: int = 10
    threshold: float = 0.4
    lasso_threshold: float = 0.1
    sample_results: bool = False

    response = requests.post(
        url + "cards/",
        json={
            "text": query,
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
        print(f"received card {card.name} distance {distance:.2f}")
        cards.append(card)

    return "\n".join([card.to_text(include_price=include_price) for card in cards])


@tool
async def lookup_rules(
    query: str,
) -> str:
    """Lookup Magic the Gathering rules and information about various keywords from various sources: Comprehensive Rulebook, Rulesguru.com, Stackexchange, Wikipedia."""

    k: int = 10
    threshold: float = 0.3
    lasso_threshold: float = 0.1
    url = f"http://localhost:8000/"

    print("looking up rules for query: ", query)
    response = requests.post(
        url + "rules/",
        json={
            "text": query,
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
        print(f"received rule {document.name} distance {distance:.2f}")
        documents.append(document)

    print(f"found {len(documents)} relevant documents")

    origin_2_doc = {}
    for doc in documents:
        origin = doc.metadata.get("origin", "other rules:")
        if origin not in origin_2_doc:
            origin_2_doc[origin] = []
        origin_2_doc[origin].append(doc.text)

    # merge texts
    rule_texts = ""
    for origin, texts in origin_2_doc.items():
        rule_texts += origin + ":\n"
        for text in texts:
            rule_texts += f"{text}\n"
    if rule_texts:
        return rule_texts
    else:
        return "No Rules found"


# %%


from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory

SYSTEM_MESSAGE = """
You are Nissa a friendly Magic the Gathering Assistant. 
You can explain the games rules, how certain card interactions work, search cards or give advice on deckbuilding.

[malicious intent]
If you recognize malicious intent in the user question tell him in a friendly way your intended use is deck building and rule advice for Magic: the Gathering. 
A malicious intent is if the user wants to talk about: 
    - illegal: Questions on banned practices
    - cheating: Concerns regarding unfair play
    - generate code: Requests for coding related to the game
    - other cardgames: Yu-Gi-Oh, Pokemon, Disney Arcana

[deck building, card search]
Use the search cards function to lookup specific cards or get suggestions for possible cards in the deck. 
Remember that in a commander game all cards in the deck must have the same color identity as the commander.  

[rules question]
For Rule advice questions always lookup rules in the lookup rules function. If there are specific cards in the question you can lookup rulings for these cards with the search cards function. 
Let`s think step by step how the ruling in context is relevant to the question. Give a short and precise answer that is based on magic the gathering rules. 
If you did not find any rules that are relevant to the question tell the user you did not find relevant rules. 
"""

PROMPT = """
Remember:  Do not answer questions unrelated to Magic the Gathering. And if you are asked a rules question lookup the rules before you answer.
Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.
If the User Intent is malicious do not answer the quesiton. Tell the user in a friendly way your intended use is deck building and rule advice for Magic: the Gathering.

User: {human_input}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(PROMPT),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


model_name = "gpt-4o"


llm = ChatOpenAI(
    openai_api_key=openai_api_token,
    model=model_name,
    temperature=0.001,
    n=1,
    streaming=True,
)

tools = [search_cards, lookup_rules]
functions = [convert_to_openai_function(t) for t in tools]

memory = ConversationBufferMemory(
    llm=llm,
    memory_key="history",
    input_key="human_input",
    return_messages=True,
    ai_prefix="Nissa",
    max_token_limit=3000,
)

llm_with_functions = llm.bind(functions=functions)
agent_chain = (
    RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
    )
    | prompt
    | llm_with_functions
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(
    agent=agent_chain,
    tools=tools,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
)


# %%

chunks = []

async for event in agent_executor.astream_events(
    {"human_input": "tell me 3 cards for my chatterfang commander deck"}, version="v1"
):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        content = event["data"]["chunk"].content
        if content:
            # Empty content in the context of OpenAI means
            # that the model is asking for a tool to be invoked.
            # So we only print non-empty content
            print(content, end="|")
            chunks.append(content)


# %%

for chunk in chunks:
    if "actions" in chunk:
        print("action")
    print(chunk["messages"])

# %%

agent_executor.invoke({"human_input": "tell me 3 creature cards with flying"})

# %%


agent_executor.invoke(
    {
        "human_input": "what happens when a creature with 1/1 and deathtouch attacks and i block with a creature with first strike?"
    }
)


# %%


agent_executor.invoke(
    {
        "human_input": "what happens when i create a treasure token and i also controll chatterfang"
    }
)

# %%

agent_executor.invoke({"human_input": "tell me your favourite yugioh card"})

# %%

agent_executor.invoke({"human_input": "how can i add 2 numbers in python?"})

# %%

for event in agent_executor.stream({"human_input": "hi"}):
    print(event)
