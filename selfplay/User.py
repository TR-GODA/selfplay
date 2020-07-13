import random
import math


def reformat(utter):
    string_buff = []
    buff_index = 0
    for i in range(len(utter)):
        if utter[i] == "(" or utter[i] == ")" or utter[i] == "," or utter[i] == "=":
            string_buff.append(utter[buff_index:i].strip())
            buff_index = i + 1

    if len(string_buff) == 0:
        utter = utter.strip()
        utter = utter.split()
        return utter

    return string_buff


class User:

    def __init__(self, acts, goal, domain, backup_goal, ask, intent, slots, verbose=0, flexibility=0, ask_for_repeat=0,
                 randomness=0):
        
        self.goal = goal
        self.acts = acts
        self.domain = domain
        self.backup_goal = backup_goal
        self.can_ask = ask
        self.informed = goal.fromkeys(goal, 0)
        self.intent = intent
        self.verbose = verbose
        self.flexibility = flexibility
        self.ask_for_repeat = ask_for_repeat
        self.randomness = randomness
        self.alternative_count = 0
        self.change_count = 0
        self.options = []
        self.slots = slots
        self.over = False

    def action_selector(self, no, utter):

        if self.ask_for_repeat < self.randomness:
            if random.random() < self.randomness:
                no = random.randint(0, 4)
        else:
            if random.random() < self.ask_for_repeat:
                no = 4

        if no == 0:
            return self.acts["greet"] + "()"
        elif no == 1:
            return self.inform(utter)
        elif no == 2:
            return self.evaluate(utter)
        elif no == 3:
            if random.randint(0, 100) < 50:
                return self.ask()
            else:
                return self.acts["bye"] + "()"
        elif no == 4:
            return self.acts["ask_for_repeat"] + "()"

    def bot_handler(self, utter):
        utter = reformat(utter)

        if len(utter) == 0:
            return self.action_selector(0, utter)
        if utter[0] == self.acts["ask"]:
            return self.action_selector(1, utter)
        elif utter[0] == self.acts["offer"]:
            return self.action_selector(2, utter)
        elif utter[0] == self.acts["success"]:
            return self.action_selector(3, utter)
        elif utter[0] == self.acts["inform"]:
            return self.action_selector(2, utter)
        elif utter[0] == self.acts["bye"]:
            return self.action_selector(3, utter)

    def inform(self, variable):

        verbose = len(self.goal) * self.verbose

        if len(variable) < 2:
            index = random.randint(0, len(self.goal) - 1)

            counter = 0
            for i in self.goal:
                if counter == index:
                    variable = i
                    break
                counter += 1
        else:
            buff = ""
            variable = variable[1:]
            for i in variable:
                buff += i + " "

            variable = buff.strip()

        answer = self.acts["inform"] + "(" + variable + "="

        if variable == self.acts["intent"]:
            answer += self.intent
            verbose -= 1
        else:
            for i in self.goal:
                if i == variable and self.informed[i] != 1:
                    if self.goal[i] is None:
                        answer += self.acts["anyway"]
                    else:
                        answer += self.goal[i]
                        self.informed[i] = 1

                    verbose -= 1

        if verbose > -1:
            while verbose > -1:
                index = random.randint(0, len(self.goal))

                counter = 0
                for i in self.goal:
                    if counter == index and self.informed[i] != 1:
                        answer += "," + i + "=" + self.goal[i]
                        self.informed[i] = 1
                        break
                    counter += 1

                verbose -= 1

        return answer + ")"

    def evaluate(self, utter):

        if utter[0] == self.acts["offer"]:
            utter = utter[1:]

            for i in range(1, len(utter), 2):
                if utter[i] not in self.options:
                    self.options.append(utter[i])

            prob = random.randint(0, 100)

            if prob < 20:
                return self.acts["refuse"] + "()"
            elif prob < 50 and self.alternative_count < 1:
                self.alternative_count += 1
                return self.acts["ask_alternative"] + "()"
            else:
                name = utter[random.randrange(1, len(utter), 2)]
                return self.choose(name)

        elif utter[0] == self.acts["inform"]:
            if utter[1] == self.acts["failure"]:
                if self.options:
                    if random.random() < self.flexibility:
                        name = self.options[random.randrange(0, len(self.options))]
                        return self.choose(name)
                    else:
                        return self.acts["bye"] + "()"
                else:
                    if random.random() < self.flexibility and self.change_count < 3:
                        informed_goals = [elem for elem in self.informed if
                                          self.informed[elem] == 1 and self.goal[elem] != self.acts["anyway"]]

                        if len(informed_goals) < 1:
                            return self.acts["ask"] + "()"

                        index = random.randint(0, len(informed_goals) - 1)

                        counter = 0
                        for i in informed_goals:
                            if counter == index:
                                self.goal[i] = self.acts["anyway"]
                                self.change_count += 1
                                return self.acts["change"] + "(" + i + "=" + self.goal[i] + ")"
                            counter += 1
                    else:
                        if self.backup_goal:
                            self.goal = self.backup_goal
                            self.alternative_count = 0
                            self.informed = self.goal.fromkeys(self.goal, 0)
                            self.alternative_count = 0
                            self.change_count = 0
                            self.options = []
                            return self.bot_handler(self.acts["ask"] + self.acts["intent"])
                        else:
                            return self.acts["bye"] + "()"
            else:
                return self.action_selector(3, "")

    def choose(self, name):
        return self.acts["choose"] + "(" + self.domain + "=" + name + ")"

    def ask_alternatives(self):
        return self.acts["ask_alternative"] + "()"

    def ask(self):
        if self.can_ask:
            verbose = math.ceil(len(self.can_ask) * self.verbose)

            answer = self.acts["ask"] + "("

            counter = 1
            buff = self.can_ask.copy()
            for i in range(verbose):
                if counter == 1:
                    answer = answer + buff[i]
                else:
                    answer = answer + "," + buff[i]
                self.can_ask.remove(buff[i])
                counter += 1

            return answer + ")"
        else:
            return self.acts["bye"] + "()"
