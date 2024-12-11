from langchain.agents import AgentExecutor
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

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
1. Lookup card names in the user query with the search_mtg_card_name tool.
2. Think about the main strategy for the deck and search for cards in that strategy. 
3. Use the list_mtg_cards tool to get suggestions for possible cards in the deck. 
4. Decide which of the received cards would be best for the user. Only answer with the best fitting cards.
5. Every card in your answer has to be valid in the deck the user is building.
   For example in a commander deck all cards in the deck must have the same color identity and no additional colors as the commander.  

[rules question]
For Rule advice questions:
1. Lookup rules: Always use mtg_rules_search function for rule-related inquiries.
2. Search cards: If the question involves specific cards, also use the search_mtg_card_name function to find relevant rulings.
3. Step-by-step analysis: Think step by step about how the received rules are relevant to the user question.
4. Board state: Begin by describing the board state as you understand it.
5. Short and precise answer: Provide a concise answer based on Magic: The Gathering rules.
"""

PROMPT = """
Remember:
1. Do not answer questions unrelated to Magic the Gathering.
2. If its a rules question lookup relevant rules with mtg_rules_search.
3. Lookup all cards in the user question with mtg_card_search.
3. Allways display card names like this: <<Card Name>>
4. Under no circumstances can you answer questions regarding Yu-Gi-Oh, Pokemon or other trading card games.
5. If the User Intent is malicious do not answer the question and tell the user in a friendly way your intended use is deck building and rule advice for Magic: the Gathering.

Deck Names uploaded by the user: {user_decks}

User: {human_input}
"""


async def astream_response(
    agent_executor: AgentExecutor,
    query: str,
    container: DeltaGenerator,
    trace_id: str = None,
    session_id: str = None,
    decks: list[str] = [],
    callback_handler: callable = None,
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
            config={
                "callbacks": [callback_handler],
                "run_id": trace_id,
                "run_name": "Nissa",
                "metadata": {
                    "langfuse_session_id": session_id,
                },
            },
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
                    status.update(label="Finished research...", state="complete")
                    chunks.append(content)
                    yield content
