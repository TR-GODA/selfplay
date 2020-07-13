# Selfplay

Selfplay is a framework to simulate a dialogue between a user and a system to obtain training data for goal-oriented dialogue systems in **any language, any domain with three lines of code**. Based on an article called "[Building a Conversational Agent Overnight with Dialogue Self-Play](https://arxiv.org/abs/1801.04871)".

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Selfplay.

```bash
pip install selfplay
```

## How it's work?

First, program reads data file(data.json) and slot file(slots.txt) that you gave. Then it chooses an element from data file randomly, to create a goal for user. Then, it rearrange the goal. Also, it reads dialogue acts file(acts.json) to speak in given language (default Turkish).

After that, it deletes the goal from the database with probability of delete_rate(%30) and creates a back-up plan with probability of backup_rate(%30). So, every 1 out of 3 query, user couldn't be able to fulfill her goal and every 1 out of 3 failure scenario, user will changes her goal with another one, by default. You can give your own values to changes these probabilities.

Then, the program determines whether user or system will make the conversation started with equal chances. Finally, it will make two bots speak till end condition is satisfied.

### Data file
Data file should be in .json format and it should be arranged as list of dictionaries with key values are entity names. User bot will choose one of these elements as it's goal. Example data file can be found in main directory. Default name is "data.json". 

### Slot file
Slot names should be indicated in a file which is in .txt format as shown below. Default name is "slots.txt".
Slot names with '*' shows "mandatory slots" which bot has to ask user to fill this slot. Slot names with '+' indicates that, user might ask bot to fill this slots (think it as address or telefon number). Other slot names are optional, bot will not ask them. However user might fill them.
    
    # Intent1
        SlotName1*
        SlotName2
        SlotName3+
    
    # Intent2
        SlotName1*
        SlotName2*
        SlotName3+

### Dialogue act file
Selfplay is designed to cover as much aspect as possible for a goal oriented agent. It has 10 dialogue acts with supporting 5 elements that you need to give. Dialogue acts are greet, inform, choose, ask_alternative, ask, bye, refuse, ask_for_repeat, change and offer. Supporting parameters are language, intent, anyway, failure and success. Example dialogue act file can be found in the main directory.


### User bot

```python
import selfplay as sp

user = sp.Dialogues.get_user(domain) # you can use default values

user = sp.Dialogues.get_user(domain, verbose=0.2, flexibility=0.3, ask_for_repeat=0.4) # or you can fill some of them
```
**Verbose**: Represents how talkative the user is. (How many slots will be informed at once)

**Flexibility**: Indicates user's response when there isn't matching results for goal.

**Ask For Repeat**: Represents how frequently the user will ask for repeat.

**Randomness**: Indicates probability of illogical behaviour of the user.

&nbsp;

**Domain**: Domain of the dialogue. For instance, "cinema" for buying a cinema ticket or "hotel" for hotel booking (more specifically the thing that is searched for).

**Intent**: Indicates user intent from slots.txt file. (E.g. 0 for #intent1)

**Lang**: Language of the dialogue.

**Delete rate**: Probability of deleting user goal from database.

**Back-up rate**: Probability of giving user a backup goal.

### System bot

```python
import selfplay as sp

bot= sp.Dialogues.get_system(domain) # you can use default values

bot= sp.Dialogues.get_system(domain, slots_file="slots", db_file="data") # or you can fill some of them
```

## Usage

To obtain dialogues, 3 steps are required.
1. Create an user bot
2. Create a system bot
3. Make them talk each other. (e.g. say "come on guys, don't be shy")

```python
import selfplay as sp

user = sp.Dialogues.get_user(domain)

bot = sp.Dialogues.get_system(domain)


dialogue = sp.Dialogues.get_dialogue(user, bot) # you can take one dialogue

dialogues = sp.Dialogues.get_dialogues(user, bot, 100) # or you can take as much as you want

```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)