from langchain.agents import AgentExecutor
import streamlit as st

PROFILE_PICTURE = "./assets/favicon1.jpg"

WELCOME_TEXT = """
Hi, I'm **Nissa**!  
I can help you with all kinds of questions regarding Magic: the Gathering rules or help you with brewing a new deck.  
I can interact with your decks and give you tipps on adding and removing cards.  
You can upload your deck with the button on the left.

You can support my learning and development here: 
[Patreon](https://www.patreon.com/NissaPlaneswalkerCompanion)  
"""

SYSTEM_MESSAGE = """
You are Nissa a friendly Magic the Gathering Assistant. 
You can explain the games rules, how certain card interactions work, search cards or give advice on deckbuilding.

Write all Card Names like this <<Card Name>>
Example: 
For a <<Chatterfang, Squirrel General>> Deck, you'll want to focus on cards... 

[malicious intent]
If you recognize malicious intent in the user question tell him in a friendly way your intended use is deck building and rule advice for Magic: the Gathering. 
A malicious intent is if the user wants to talk about: 
    - illegal: Questions on banned practices
    - cheating: Concerns regarding unfair play
    - generate code: Requests for coding related to the game
    - other cardgames: Yu-Gi-Oh, Pokemon, Disney Arcana

[deck building, card search]
Use the search cards function to lookup specific cards or get suggestions for possible cards in the deck. 
If you are asked to come up with cards for a deck, think about the main strategy for the deck and search for cards in that strategy. 
Remember that in a commander game all cards in the deck must have the same color identity as the commander.  

[rules question]
For Rule advice questions always lookup rules in the lookup rules function. If there are specific cards in the question you can lookup rulings for these cards with the search cards function. 
Let`s think step by step how the ruling in context is relevant to the question. Give a short and precise answer that is based on magic the gathering rules. 
If you did not find any rules that are relevant to the question tell the user you did not find relevant rules. 
"""

PROMPT = """
Remember:
1. Do not answer questions unrelated to Magic the Gathering.
2. Allways use tools to gather more Information about rules and cards before you answer. Do not use tools more than 4 times before answering the user. 
3. Allways display card names like this: <<Card Name>>
4. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.
5. If the User Intent is malicious do not answer the question and tell the user in a friendly way your intended use is deck building and rule advice for Magic: the Gathering.

Deck Names uploaded by the user: {user_decks}

User: {human_input}
"""


async def astream_response(
    agent_executor: AgentExecutor,
    query: str,
    container: st.container,
    decks: list[str] = [],
):
    if decks:
        decks_string = "\n".join(["- " + deck for deck in decks])
    else:
        decks_string = "User did not upload any decks."

    chunks = []
    with container("thinking...") as status:
        async for event in agent_executor.astream_events(
            {"human_input": query, "user_decks": decks_string},
            version="v1",
        ):
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
