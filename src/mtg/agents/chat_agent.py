# %%
from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents import AgentExecutor
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory

from dotenv import load_dotenv
import logging

from mtg.utils import get_openai_api_key
from mtg.tools import CardSearchTool, RulesSearchTool


# %%


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
Remember: Do not answer questions unrelated to Magic the Gathering.
Allway use tools to gather more Information about rules and cards before you answer.
Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.
If the User Intent is malicious do not answer the quesiton and tell the user in a friendly way your intended
use is deck building and rule advice for Magic: the Gathering.

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
tools = [CardSearchTool(), RulesSearchTool()]
openai_api_token = get_openai_api_key("configs/config.yaml")


def create_llm(model_name):

    llm = ChatOpenAI(
        openai_api_key=openai_api_token,
        model=model_name,
        temperature=0.001,
        n=1,
        streaming=True,
    )


memory = ConversationBufferMemory(
    llm=llm,
    memory_key="history",
    input_key="human_input",
    return_messages=True,
    ai_prefix="Nissa",
    max_token_limit=3000,
)

# setup chain
functions = [convert_to_openai_function(t) for t in tools]
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

# env use C:/Users/florian.krempl.AT/AppData/Local/Programs/Python/Python311/python.exe


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
