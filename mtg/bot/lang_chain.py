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
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain.prompts import PromptTemplate

GENERAL_PROMPT = """
You are Nissa a Magic the Gathering Assistant, that explains rules and gives deckbuilding advice.
{human_input}
"""

DECKBUILDING_PROMPT = """
Card data: {card_data}

Remember:  You are Nissa a Magic the Gathering Assistant that helps with deckbuilding. Give your advice on which cards are best for the users deck.
Let`s think step by step which cards from the card data in context are best for the users deck.
Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.

{human_input}
"""

RULES_QUESTION_PROMPT = """
Card data: {card_data}

Rules data: {rules_data}

Remember:  You are Nissa a Magic the Gathering Assistant, that explains rules.
For every user question first give a short summary of the answer, then, if possible explain your summary with the rulings and card data.
Let`s think step by step how the ruling is relevant to the question.
Do not answer questions unrelated to Magic the Gathering. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.

{human_input}
"""


general_prompt = PromptTemplate.from_template(GENERAL_PROMPT)
deckbuilding_prompt = PromptTemplate.from_template(DECKBUILDING_PROMPT)
rules_question_prompt = PromptTemplate.from_template(RULES_QUESTION_PROMPT)

prompt_branch = RunnableBranch(
    (lambda x: x["topic"] == "deck building", deckbuilding_prompt),
    (lambda x: x["topic"] == "rules question", rules_question_prompt),
    general_prompt,
)


prompt_branch

# %%


from typing import Literal

from langchain.pydantic_v1 import BaseModel
from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.utils.openai_functions import convert_pydantic_to_openai_function


class TopicClassifier(BaseModel):
    "Classify the topic of the user question"

    topic: Literal["deck building", "rules question"]
    "The topic of the user question. The user can either ask about deck building advice or he has a question about a Magic the Gathering rule."


openai_api_key = "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"
classifier_function = convert_pydantic_to_openai_function(TopicClassifier)
llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-3.5-turbo").bind(
    functions=[classifier_function], function_call={"name": "TopicClassifier"}
)
parser = PydanticAttrOutputFunctionsParser(
    pydantic_schema=TopicClassifier, attr_name="topic"
)
classifier_chain = llm | parser

# %%

question = "Tell me 3 cards for my chatterfang commander deck"
question = "what happens if i attack with a 5/5 creature with trample and my opponent blocks with a 5/1 creature?"

classifier_chain.invoke(question)


# %%
"""
chain = create_chat_model(max_responses=3, temperature=0.7)

response = chain.generate(
    input_list=[
        {"human_input": "hi!, how are you", "card_data": "", "chat_history": []}
    ]
)
"""
