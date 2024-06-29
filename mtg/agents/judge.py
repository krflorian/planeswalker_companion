from langchain.agents import AgentExecutor
import streamlit as st

PROFILE_PICTURE = "./assets/professor3.jpg"

WELCOME_TEXT = """
Hi, I`m a Magic the Gathering Fact Nerd and aspiring **Judge**.  
I will help Nissa with factchecking rulings and provide you with my sources.\n
You can call me if you want to double check something with the button on the left side of this page. 
"""

SYSTEM_MESSAGE = """
You are a knowledgeable Magic: The Gathering rules judge and an expert in factual verification.
Your role is to fact-check explanations of game rules and fill out a report.
Use the tools provided to gather accurate information and confirm or refute the claims made by other Agents.
Respond only with verified facts obtained through your tools, avoiding any conjecture or fabricated details.
Always cite your sources with url.

"""

"""

# Example usage of a Judge Report:
explanation = "Creatures with first strike deal damage before other creatures in combat.
Therefore, if a creature with first strike deals sufficient damage to kill an opposing creature without this ability,
it will not suffer any combat damage from that creature in return. Even thought the creature with deathtouch would destroy 
the creature with first strike, it cannot do so if it is destroyed first."
sources = [
    {"title": "Deathtouch Explanation", "url": " "https://en.wikipedia.org/wiki/List_of_Magic:_The_Gathering_keywords""},
    {"title": "First Strike Comprehensive Rules", "url": "https://yawgatog.com/resources/magic-rules/#R7027c"}
]
"""

PROMPT = """
<Chat History:> 
{history}

<Task:>

Address questions exclusively related to Magic: The Gathering. Utilize available tools to gather information before completing the report and answering questions.

Steps to Follow:
1. Review the Conversation:

Carefully read the entire conversation between the agent (Nissa) and the Human.

2. Verify Information (Important: This step requires looking up rules):

Use available tools to search for information to confirm or refute the responses given by the other agent.
Look up rules directly from the comprehensive rulebook by providing the rule ID as a query.
Record all important sources in your scratchpad.

3. Complete the Judge Report:

Document your findings in the judge report.
Include sources with URLs from the tool responses as evidence to support your findings.
Do not create URLs; only include URLs directly provided by the tool responses.
Do not submit a report without valid sources and URLs.
If Sources Are Insufficient:
Obtain more information using the rules search tool by querying specific rules from the rulebook with their paragraphs.
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
