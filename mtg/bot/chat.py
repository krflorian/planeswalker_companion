# %%
import os
import yaml

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationTokenBufferMemory

from mtg.utils import get_openai_api_key

openai_api_key = get_openai_api_key()

SYSTEM_MESSAGE = """
You are Nissa a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
Do not answer questions unrelated to Magic the Gathering. If possible explain your answers with the rulings in context.
"""

HUMAN_PROMPT = """
Card data: {card_data}

Remember:  You are Nissa a Magic the Gathering Assistant, that explains rules, cards and gives advice on playstyles.
For every user question first give a short summary of the answer, then, if possible explain your summary with the rulings and card data.
Let`s think step by step how the ruling is relevant to the question.
Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.

{human_input}
"""


def create_chat_model(
    model: str = "gpt-3.5-turbo",
    temperature: int = 1,
    max_token_limit: int = 3000,
    max_responses=1,
):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=SYSTEM_MESSAGE),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
        ]
    )

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model=model,
        temperature=temperature,
        n=max_responses,
    )

    memory = ConversationTokenBufferMemory(
        llm=llm,
        memory_key="chat_history",
        input_key="human_input",
        return_messages=True,
        ai_prefix="Nissa",
        max_token_limit=max_token_limit,
    )

    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    return chat_llm_chain


# %%

"""
chain = create_chat_model(max_responses=3, temperature=0.7)

response = chain.generate(
    input_list=[
        {"human_input": "hi!, how are you", "card_data": "", "chat_history": []}
    ]
)
"""
