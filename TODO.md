# TODOs: 

# low hanging fruit 
- add double sided cards to card database 
- update scryfall card data + rulings automatically at start of application (data_handler/process_scryfall_data.py)
- create graphic for bot and data flow and add to readme
- add "get data" function, that fetches data folder from a file server

# takes time
- FEATURE: add streaming to gradio to reduce waiting time: https://www.gradio.app/guides/creating-a-chatbot-fast#a-streaming-example-using-openai
- FEATURE: separate rules questions from deck building questions via langchain agents
    - for deckbuilding: fine tune vector search
        - maybe add similarity to cards in question rather than similarity to question itself?
        - what card data information/attributes are relevant? 
        - deckbuilding prompt finetuning 
    - for rules question: add rules from rulebook to context via vector search 
        - decide on how to preprocess and split rules text (bullet points or sentences...)
- implement unit tests for
    - vector search 
    - card data search 
    - llm rules questions 
- FEATURE: card search feature as third branch llm? 
- FEATURE: how sure is the llm when answering rules questions? (metric)
- FEATURE: cli for chatbot (click would be best)
    - bot start
    - bot update_card_data
    - etc.  
    
# difficult to implement
- card identities should stay the same in the whole text example: Anje Falkenrath should stay and not change to Anje, Maid of Dishonor