# %%

from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.schema import SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseMemory

from dotenv import load_dotenv
from functools import cache
import logging

load_dotenv()


@cache
def create_llm(model_name: str = "gpt-4o"):
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.001,
        n=1,
        streaming=True,
    )
    logging.info("loaded chatopenai with model version: ", model_name)

    return llm


def create_memory(llm):
    memory = ConversationBufferMemory(
        llm=llm,
        memory_key="history",
        input_key="human_input",
        output_key="output",
        return_messages=True,
        max_token_limit=3000,
    )
    memory.ai_prefix = "Nissa"
    return memory


def create_chat_agent(
    tools: list[BaseTool],
    system_message: str,
    prompt: str,
    memory: BaseMemory,
    model_name: str = "gpt-4o",
):
    """Create a Chat Agent with access to tools and chat history."""
    llm = create_llm(model_name)

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(prompt),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # setup chain
    functions = [convert_to_openai_function(t) for t in tools]
    llm_with_functions = llm.bind(functions=functions)
    agent_chain = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            )
        )
        | prompt
        | llm_with_functions
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(
        agent=agent_chain,
        tools=tools,
        verbose=False,
        memory=memory,
        handle_parsing_errors=True,
    )

    return agent_executor


"""
# stop after judge report 
import json
from langchain_core.agents import AgentActionMessageLog, AgentFinish


def parse(output):
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"output": output.content}, log=output.content)

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the Response function was invoked, return to the user with the function inputs
    if name == "Response":
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )
"""


def create_judge_agent(
    tools: list[BaseTool],
    system_message: str,
    prompt: str,
    memory: BaseMemory,
    model_name: str = "gpt-4o",
):
    llm = create_llm(model_name)

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_message),
            HumanMessagePromptTemplate.from_template(prompt),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # setup chain
    functions = [convert_to_openai_function(t) for t in tools]
    llm_with_functions = llm.bind(functions=functions)
    agent_chain = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            )
        )
        | RunnablePassthrough.assign(
            history=RunnableLambda(lambda x: memory.buffer_as_str)
        )
        | prompt
        | llm_with_functions
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(
        agent=agent_chain, tools=tools, verbose=False, handle_parsing_errors=True
    )

    return agent_executor
