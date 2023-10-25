---
title: MTG Rulebot Nissa
emoji: 🌵🌊🌬🔥🌍
colorFrom: red
colorTo: orange
sdk: gradio
app_file: app.py
app_port: 7860
base_path: /
tags:
  - Magic the Gathering
---


# MTG Rule Bot "Nissa"

Nissa is an open-source chat bot for Magic: The Gathering that answers questions regarding rules and cards and helps with deckbuilding. The bot has access to all card data and rulings for the cards. Nissa is powered by [GPT-3.5-turbo](https://platform.openai.com/docs/models/gpt-3-5),[langchain](https://python.langchain.com/docs/get_started/introduction) and [HNSWLIB](https://github.com/nmslib/hnswlib). 


# Usage
The current version of the bot is deployed on [HuggingFace](https://huggingface.co/spaces/floriankrempl/mtg_rules_bot)
To use the bot, simply type your question in the chat window. Because Nissa has access to all mtg card data she can answer the questions better if you mention card names in your question. You will get Links to all cards recognized by Nissa. 

Here are some examples of questions that the bot can answer correctly:


<u>User</u>:  
What happens if i attack with [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517) and my opponent blocks with [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499)?  

<u>Nissa</u>:  

If you attack with [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517) and your opponent blocks with [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499), the following will happen:  
    - During the declare blockers step, your opponent declares [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) as a blocker for [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517).  
    - Since [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) has first strike, it will deal its combat damage before [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517).  
    - [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) deals 1 damage to [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517).  
    - [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517), being a 2/1 creature, will be destroyed by the 1 damage dealt by [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499).  
    - [Ambush Viper](https://cards.scryfall.io/large/front/0/e/0e386888-57f5-4eb6-88e8-5679bb8eb290.jpg?1608910517) will not deal any damage to [Goblin Striker](https://cards.scryfall.io/large/front/f/7/f7654d8a-7013-4311-b29e-b55aaa1bf502.jpg?1562163499) because it has already been destroyed.


<u>User</u>:  
Tell me 3 Cards that I can add to my [Chatterfang](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) Commander Deck.   

<u>Nissa</u>:  
Sure! Here are three cards that you can consider adding to your [Chatterfang](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) Commander deck:

[Skullclamp](https://cards.scryfall.io/large/front/a/3/a36fd6d8-66a2-49d1-b9f3-b400ebc03674.jpg?1682210228): This artifact allows you to draw cards whenever a creature you control dies with power 1 or less. Since Chatterfang creates 1/1 squirrel tokens, sacrificing them with [Skullclamp](https://cards.scryfall.io/large/front/a/3/a36fd6d8-66a2-49d1-b9f3-b400ebc03674.jpg?1682210228) equipped can provide you with a steady stream of card advantage.

[Beastmaster Ascension](https://cards.scryfall.io/large/front/f/4/f404d133-fc1a-4751-ac72-554e6553e486.jpg?1673484492): This enchantment becomes powerful when you have a wide board of creatures, which Chatterfang can easily generate. Once you have 7 or more creatures, Beastmaster Ascension gives all your creatures +5/+5 until end of turn, allowing you to swing for a massive amount of damage.

[Parallel Lives](https://cards.scryfall.io/large/front/0/1/01033dae-fec1-41f2-b7f2-cc6a43331790.jpg?1562825348): This enchantment doubles the number of tokens you create. With [Chatterfang's](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) ability to create squirrel tokens, [Parallel Lives](https://cards.scryfall.io/large/front/0/1/01033dae-fec1-41f2-b7f2-cc6a43331790.jpg?1562825348) can quickly flood the board with even more tokens, giving you a strong presence and more options for sacrificing creatures.

These cards synergize well with [Chatterfang's](https://cards.scryfall.io/large/front/1/7/1785cf85-1ac0-4246-9b89-1a8221a8e1b2.jpg?1626097239) ability to create squirrel tokens and sacrifice them for various effects. They can help you generate card advantage, boost your creatures' power, and create even more tokens for additional value.


### Attention! Nissa is still in development, so some questions are still too difficult for her: 

<u>User</u>:  

If I pay the kicker cost of [Academy Drake](https://cards.scryfall.io/large/front/f/8/f8bacb12-da46-4b00-804f-9ff6bff452bc.jpg?1562745962) does it get +1/+1 counters when my opponent controlls an [Elesh Norn, Mother of Machines](https://cards.scryfall.io/large/front/4/4/44dcab01-1d13-4dfc-ae2f-fbaa3dd35087.jpg?1675956896)?  

<u>Nissa</u>:  

No, if you pay the kicker cost of [Academy Drake](https://cards.scryfall.io/large/front/f/8/f8bacb12-da46-4b00-804f-9ff6bff452bc.jpg?1562745962), it will not receive +1/+1 counters when your opponent controls Elesh Norn, Mother of Machines. [Elesh Norn's](https://cards.scryfall.io/large/front/4/4/44dcab01-1d13-4dfc-ae2f-fbaa3dd35087.jpg?1675956896) ability specifically states that permanents entering the battlefield don't cause abilities of permanents your opponents control to trigger. Since [Academy Drake's](https://cards.scryfall.io/large/front/f/8/f8bacb12-da46-4b00-804f-9ff6bff452bc.jpg?1562745962) ability to enter the battlefield with +1/+1 counters is a triggered ability, it will not trigger when Elesh Norn is on the battlefield under your opponent's control.

This ruling is based on the interaction between Elesh Norn's ability and [Academy Drake`s](https://cards.scryfall.io/large/front/f/8/f8bacb12-da46-4b00-804f-9ff6bff452bc.jpg?1562745962) triggered ability. Elesh Norn's ability prevents triggered abilities of permanents your opponents control from triggering when a permanent enters the battlefield. Since Academy Drake's ability is a triggered ability that triggers when it enters the battlefield, it will not trigger when Elesh Norn is on the battlefield under your opponent's control.


### There are more examples at `tests/bot/test_qa`

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

