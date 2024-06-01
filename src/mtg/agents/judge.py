from langchain.agents import AgentExecutor
import streamlit as st

PROFILE_PICTURE = "./assets/professor3.jpg"

WELCOME_TEXT = """
Hi, I`m a Magic the Gathering Fact Nerd and aspiring Judge.  
I will help Nissa with factchecking rulings and provide you with my sources.
"""

SYSTEM_MESSAGE = """
You are a knowledgeable Magic: The Gathering rules judge and an expert in factual verification.
Your role is to fact-check explanations of game rules.
Use the tools provided to gather accurate information and confirm or refute the claims made by other AIs.
Respond only with verified facts obtained through your tools, avoiding any conjecture or fabricated details.
Always cite your sources with url at the end of your response.
This is very important: If you did not find any sources that either proof or disproof the other agent: tell the user that you cannot prove that this is right. 
"""

PROMPT = """
Remember: Do not answer questions unrelated to Magic the Gathering.
Allway use tools to gather more Information about rules and cards before you answer.
Do not use tools more than 4 times before answering the user. 
Always cite your sources for rules and cards with the received url at the end of your response.
"""


async def astream_response(agent_executor: AgentExecutor, container: st.container):

    chunks = []
    with container("thinking...") as status:
        async for event in agent_executor.astream_events({}, version="v1"):
            kind = event["event"]
            if kind == "on_tool_start":
                status.update(
                    label=f"Looking up Infos with {event['name']}...", state="running"
                )
                query = event["data"].get("input").get("query", None)
                if query is not None:
                    st.write(f"using {event['name']} to search for: '{query}'")
                else:
                    st.write(f"using {event['name']}")

            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    status.update(label=f"Finished research...", state="complete")
                    # Empty content in the context of OpenAI means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content
                    chunks.append(content)
                    yield content
