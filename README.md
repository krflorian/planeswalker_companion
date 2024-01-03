
# MTG Rule Bot "Nissa"

Every avid Magic player has found themselves in this scenario: engrossed in a Commander match with their playgroup, someone introduces a new card, and a lively discussion ensues about its interactions within the game. As the debate intensifies, reaching a resolution becomes challenging, prompting a trip to Google in search of answers. However, the process is often time-consuming, requiring cross-referencing various sources like Reddit and card rulings before a consensus is reached. This frequent interruption hinders the flow of your games. Introducing Nissa, an intelligent chatbot designed to swiftly address your inquiries related to Magic: The Gathering.

Nissa stands as an open-source chatbot tailored for Magic: The Gathering enthusiasts, providing insightful responses to inquiries about rules, cards, and even offering assistance in the realm of creative deckbuilding. With comprehensive access to card data and rulings, Nissa serves as a reliable source for resolving queries. Whether you seek clarification on game mechanics or details about a specific card, Nissa diligently references the "Magic: The Gathering Comprehensive Rules" and external data to provide clear explanations. Additionally, if you're in need of deckbuilding guidance, Nissa effortlessly browses through every single available card, and suggests optimal matches and explains the reasons behind their inclusion in your deck.

Nissa is build as `RAG` architecture, powered by [GPT-4](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo), [langchain](https://python.langchain.com/docs/get_started/introduction) and [HNSWLIB](https://github.com/nmslib/hnswlib). 


# Usage
The current version of the bot is deployed on [https://nissa.planeswalkercompanion.com/](https://nissa.planeswalkercompanion.com/)
To use the bot, simply type your question in the chat window. Because Nissa has access to all mtg card data she can answer the questions better if you mention card names in your question. You will get Links to all cards recognized by Nissa. 

Here are some examples of questions that the bot can answer correctly:

## Rules Questions: 

<u>User</u>:  
What happens if i attack with [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517) and my opponent blocks with [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499)?  

<u>Nissa</u>:  
If you attack with [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517) and your opponent blocks with [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499), the following will happen:  
    1. During the declare blockers step, your opponent declares [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) as a blocker for [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517).  
    2. Since [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) has first strike, it will deal its combat damage before [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517).  
    3. [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) deals 1 damage to [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517).  
    4. [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517), being a 2/1 creature, will be destroyed by the 1 damage dealt by [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499).  
    5. [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517) will not deal any damage to [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) because it has already been destroyed.  

<u>User</u>:  
Can you explain the stack in Magic: The Gathering and how it works? I'm having trouble understanding the order in which spells and abilities resolve during a turn.

<u>Nissa</u>:  
The stack in Magic: The Gathering is a conceptual place where spells and abilities are put when they are cast or activated, and before they resolve and have their effect on the game. The stack is fundamental to understanding how spells and abilities work in sequence. Here's how it operates:

1. <b>Spell/Ability</b> Casting or Activation: Any time a spell is cast or an ability is activated, it goes on the stack. This doesn't cause it to resolve immediately; it merely announces the intention to use that spell or ability.

2. <b>Priority:</b> After putting a spell or ability on the stack, the player who cast the spell or activated the ability gets priority back. They may choose to cast another spell or activate another ability. If they choose not to do anything else, they pass priority to their opponent. Only when both players pass priority in succession does the stack start to resolve.

3. <b>The Last-In, First-Out (LIFO) Principle:</b> Spells and abilities on the stack resolve in reverse order of how they were put there. This means the last spell or ability added to the stack is the first one to resolve.

4. <b>Resolution:</b> When a spell or ability is resolving, no player has priority, and no other spells or abilities can be added to the stack. Players must wait for the current spell or ability to finish resolving before doing anything else. Once it resolves, its effects occur. Then, the player whose turn it is gets priority again, and the stack can start to resolve the next item.

5. <b>Responding:</b> Any time a player adds something to the stack and then passes priority, the opponent can respond by adding their own spells or abilities to the stack before the first item resolves. This can continue back and forth as long as both players have things they want to cast or activate and the mana to do so.

6. <b>Completing the Stack:</b> The stack keeps resolving in this way until it is empty. No new spells or abilities can resolve until the stack is entirely clear, and no player can take any game actions outside of casting instants or activating abilities while the stack is resolving.

The stack is a crucial concept for timing and strategy in the game, as it determines the order of operations for spells and abilities and allows players to respond to their opponent's actions before they take effect. Understanding how the stack works is essential for making informed decisions during gameplay.  

## Deck Building Advice

<u>User</u>:  
Tell me 3 Cards that I can add to my [Chatterfang](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) Commander Deck.   

<u>Nissa</u>:  
Sure! Here are three cards that you can consider adding to your [Chatterfang](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) Commander deck:

[Skullclamp](https://cards.scryfall.io/large/front/a/3/a36fd6d8-66a2-49d1-b9f3-b400ebc03674.jpg?1682210228): This artifact allows you to draw cards whenever a creature you control dies with power 1 or less. Since Chatterfang creates 1/1 squirrel tokens, sacrificing them with [Skullclamp](https://cards.scryfall.io/large/front/a/3/a36fd6d8-66a2-49d1-b9f3-b400ebc03674.jpg?1682210228) equipped can provide you with a steady stream of card advantage.

[Beastmaster Ascension](https://cards.scryfall.io/large/front/f/4/f404d133-fc1a-4751-ac72-554e6553e486.jpg?1673484492): This enchantment becomes powerful when you have a wide board of creatures, which Chatterfang can easily generate. Once you have 7 or more creatures, Beastmaster Ascension gives all your creatures +5/+5 until end of turn, allowing you to swing for a massive amount of damage.

[Parallel Lives](https://cards.scryfall.io/large/front/0/1/01033dae-fec1-41f2-b7f2-cc6a43331790.jpg?1562825348): This enchantment doubles the number of tokens you create. With [Chatterfang's](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) ability to create squirrel tokens, [Parallel Lives](https://cards.scryfall.io/large/front/0/1/01033dae-fec1-41f2-b7f2-cc6a43331790.jpg?1562825348) can quickly flood the board with even more tokens, giving you a strong presence and more options for sacrificing creatures.

These cards synergize well with [Chatterfang's](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) ability to create squirrel tokens and sacrifice them for various effects. They can help you generate card advantage, boost your creatures' power, and create even more tokens for additional value.

<u>User</u>:  
What is the main strategy for a [Chatterfang, Squirrel General](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) commander deck?  

<u>Nissa</u>:  
A Chatterfang, Squirrel General Commander deck revolves around a token-based strategy, particularly focusing on generating a large number of Squirrel tokens and leveraging Chatterfang's abilities to control the board and finish off opponents.

Here are the key components of a Chatterfang Commander deck strategy:

<b>Token Generation:</b> Since Chatterfang creates additional Squirrel tokens whenever you create one or more tokens, the deck should be packed with ways to generate tokens. Cards like Squirrel Nest, Chatter of the Squirrel, and Squirrel Sanctuary are great for this, constantly providing you with a stream of Squirrel tokens.

<b>Token Synergies:</b> Cards that benefit from having a lot of tokens on the battlefield, such as Chitterspitter, can increase the power of your Squirrel army. With Chitterspitter, sacrificing tokens for acorn counters can significantly buff your Squirrels, potentially leading to overwhelming combat phases.

<b>Sacrifice Outlets:</b> Chatterfang also has an activated ability that allows you to sacrifice Squirrels for a combat trick, giving a creature +X/-X until the end of the turn. This can be used both defensively and offensively to remove threats or make way for your attacks.

<b>Token Buffs:</b> Including enchantments and artifacts that buff your tokens, like Coat of Arms or Parallel Lives (outside of Chatterfang's ability), can quickly turn a board of small Squirrels into a lethal threat.

<b>Utilizing Black's Strengths:</b> Chatterfang's color identity includes black, which allows you to use black's removal, recursion, and card draw capabilities. Cards like Squirrel-Powered Scheme, while more niche, can be included for specific synergies or to enhance certain die-rolling cards if they fit your strategy.

<b>Protecting Chatterfang:</b> Since Chatterfang is key to your strategy, you'll want to include ways to protect it. This can include cards like Heroic Intervention or Lightning Greaves to keep Chatterfang safe from removal.

<b>Versatility and Interaction:</b> It's important to have answers to what your opponents are doing. Cards like Mistakes Were Made allow you to handle artifacts and enchantments while still staying on theme by creating Squirrel tokens.

<b>Combo Potential:</b> There may also be room for combo finishes. For example, Earthcraft (if legal in your playgroup) can combo with Squirrel Nest for infinite Squirrels, and with Chatterfang on the battlefield, this can lead to an instant win through combat damage or direct life loss via Chatterfang's sacrifice ability.

<b>Win Conditions:</b> In addition to winning through combat with a large Squirrel army, you may want to include alternative win conditions or ways to use your tokens for value, such as Ashnod's Altar for mana generation or Skullclamp for card draw.

The key to a successful Chatterfang deck is to create and protect a large number of Squirrel tokens, enhance their abilities, and use them to control the game until you can swing in for lethal damage or utilize an alternative win condition.

# RAG Architecture  

The bot currently has two datastreams.  
One for deckbuilding, where the prompt gets augmented with a lot of data about cards. The data gets sampled from the most similar cards to the question and to the card in the question.  
The other one for Rules questions. Here the prompt gets augmented with the card data mentioned in the question with rulings for those cards. It also gets augmented with the best fitting Rules from the Comprehensive Rulebook. It is planned to add a Halucination Model that checks how well the response is supported by the rules in context. If the rules do not match the response the bot gets the whole chapter with the most significant rule and can answer again.  

![RAG Architecture](data/architecture/dataflow%20nissa.drawio.png)


# Support the Project 

You can support the project on [Patreon](https://www.patreon.com/user?u=112353036&fan_landing=true&view_as=public) #TODO add correct link 

# Contributing
If you’d like to contribute to this project, please follow these steps:

Create a new branch.
Make your changes.
Test your changes.
Submit a pull request.

# Installation
To install the bot, follow these steps:

1. Clone the repository (make sure you have git-lfs installed)
2. Install the required dependencies with poetry 
```shell 
cd your/working/directory
pip install --upgrade poetry 
poetry install 
```
3. create a config.yml file with your OpenAI API Key.
```shell
cp ./config/config_example.yaml ./config/config.yaml && nano ./config/config.yaml
```
4. Run the bot:
```shell 
poetry shell 
python app.py 
```

# License
This project is licensed under the MIT License.

