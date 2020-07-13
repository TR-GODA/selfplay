import json
import random
import csv
import selfplay.User
import selfplay.Bot


def _read_from_file(file_name, utf8=True):
    # open slot file
    if utf8:
        file = open(file_name, "r", encoding="utf-8")
    else:
        file = open(file_name, "r")

    intents = []
    buff_list = []
    buff_dict = {}

    if file.mode == 'r':
        contents = file.readlines()

    for i in range(len(contents)):
        if contents[i][0] == "#":
            if buff_list:
                buff_list.append(buff_dict)
                intents.append(buff_list)
                buff_list = []
                buff_dict = {}

            contents[i] = contents[i].strip()
            contents[i] = contents[i][2:]
            buff_list.append(contents[i])
        else:
            if contents[i].isspace():
                continue

            contents[i] = contents[i].strip()
            buff_dict[contents[i]] = ""

    buff_list.append(buff_dict)
    intents.append(buff_list)

    return intents


def _read_db(file_name, utf8=True):
    if utf8:
        with open(file_name, encoding="utf-8") as json_file:
            data = json.load(json_file)
    else:
        with open(file_name) as json_file:
            data = json.load(json_file)

    return data


def _format_goal(user_goal, intents):
    for i in list(user_goal):
        if i not in intents[1] and i + "*" not in intents[1]:
            del user_goal[i]

    ask = [elem[:len(elem) - 1] for elem in intents[1] if elem.endswith('+')]
    return ask


def get_dialogue(user, bot, acts_file="acts.json", lang="tr"):

    acts = _read_db(acts_file)
    for i in acts:
        if i["language"] == lang:
            end_condition = i["bye"].replace(" ", "_") + "()"
            break

    arr = []
    out = ""
    first_turn = random.randint(0, 1)
    while True:
        if first_turn:
            out = user.bot_handler(out)
            print(out)
            arr.append("K: " + out)
        else:
            first_turn = 1

        out = bot.bot_handler(out)
        print(out)
        arr.append("S: " + out)

        if out == end_condition:
            break

    return arr


def get_dialogues(user, bot, size=100, output_file="generated_dialogues", acts_file="acts.json", utf8=True, newline='',
                  lang="tr"):
    if utf8:
        file = open(output_file + ".csv", 'w', encoding="utf-8", newline=newline)
    else:
        file = open(output_file + ".csv", 'w', newline=newline)

    csv_writer = csv.writer(file)
    csv_writer.writerow(['id', 'log'])

    id = 0
    for i in range(0, size):
        arr = get_dialogue(user, bot, acts_file, lang)
        row = {
            "id": id,
            "log": arr
        }

        csv_writer.writerow(row.values())
        id += 1

    file.close()


def get_user(domain, db_file="data.json", slots_file="slots.txt", acts_file="acts.json", intent=0, lang="tr", delete_rate=70,
                backup_rate=30, verbose=0, flexibility=0, ask_for_repeat=0, randomness=0):

    # read restaurant data from file
    db = _read_db(db_file)

    # read intents and slots from file
    slots = _read_from_file(slots_file)

    acts = _read_db(acts_file)
    for i in acts:
        if i["language"] == lang:
            d_acts = i

    for i in d_acts:
        d_acts[i] = d_acts[i].replace(" ", "_")

    # define goal
    index = random.randint(0, len(db) - 1)
    user_goal = db[index].copy()
    backup_goal = {}
    c_acts = slots.copy()

    ask = _format_goal(user_goal, c_acts[intent])

    # delete user goal from db with %delete_rate probability, give backup goal with %back_up_rate probability
    if random.randint(0, 100) < delete_rate:
        del db[index]
        if random.randint(0, 100) < backup_rate:
            backup_goal = db[random.randint(0, len(db) - 1)].copy()
            _format_goal(backup_goal, slots[intent])

    return selfplay.User.User(d_acts, user_goal, domain, backup_goal, ask, slots[intent][0], slots, verbose,
                              flexibility, ask_for_repeat, randomness)


def get_system(domain, slots_file="slots.txt", db_file="data.json", acts_file="acts.json", lang="tr"):
    # read restaurant data from file
    db = _read_db(db_file)

    # read intents and slots from file
    slots = _read_from_file(slots_file)

    acts = _read_db(acts_file)
    for i in acts:
        if i["language"] == lang:
            d_acts = i

    for i in d_acts:
        d_acts[i] = d_acts[i].replace(" ", "_")

    return selfplay.Bot.Bot(domain, slots, db, d_acts)
