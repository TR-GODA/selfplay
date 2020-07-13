import copy


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


def format_intents(intents):
    buff = copy.deepcopy(intents)
    for i in range(len(intents)):
        for m in intents[i][1]:
            if m.endswith('*'):
                del buff[i][1][m]
                buff[i][1][m[:-1]] = ""
            else:
                del buff[i][1][m]
                buff[i][1][m] = ""

    return buff


class Bot:

    def __init__(self, domain, intents, db, acts):
        self.domain = domain
        self.intents = format_intents(intents)
        self.acts = acts
        self.marked_intents = intents
        self.current_intent = ""
        self.db = db
        self.offered = []
        self.current_offer = []
        self.lastUtter = ""
        self.over = False

    def bot_handler(self, utter):
        utter = reformat(utter)

        if not utter or utter[0] == "" or utter[0] == self.acts["greet"] + "()":
            self.lastUtter = self.request()
        elif utter[0] == self.acts["inform"] or utter[0] == self.acts["change"]:
            if len(utter) % 2 != 1:
                del utter[len(utter) - 1]

            flag = 0
            for i in range(1, len(utter), 2):
                out = self.getInformed(utter[i], utter[i + 1])
                if out == 0:
                    self.lastUtter = self.acts["ask"] + "(" + self.acts["intent"] + ")"
                elif out == -2:
                    flag = 1

            if flag:
                self.lastUtter = self.offer()
                return self.lastUtter
            else:
                self.lastUtter = self.request()
        elif utter[0] == self.acts["ask_alternative"]:
            self.lastUtter = self.offer(0)
        elif utter[0] == self.acts["choose"]:
            self.lastUtter = self.choose(utter[2])
        elif utter[0] == self.acts["ask"]:
            self.lastUtter = self.ask_info(utter[1:])
        elif utter[0] == self.acts["bye"] or utter[0] == self.acts["refuse"]:
            self.lastUtter = self.acts["bye"] + "()"
        elif utter[0] == self.acts["ask_for_repeat"]:
            if self.lastUtter == "":
                self.lastUtter = self.request()
            else:
                self.lastUtter = self.lastUtter
        else:
            self.lastUtter = self.request()

        return self.lastUtter

    def request(self):
        if self.current_intent == "":
            return self.acts["ask"] + "(" + self.acts["intent"] + ")"

        for i in self.marked_intents:
            if i[0] == self.current_intent:
                utter = i[1]
                break

        utterList = [[k, v] for k, v in utter.items()]

        utterList = [elem for elem in utterList if elem[1] == '' and elem[0].endswith('*')]

        if len(utterList) < 1:
            return self.offer()

        ask = utterList[0][0][:-1]
        answer = self.acts["ask"] + "(" + ask + ")"

        return answer

    def offer(self, code=1):
        if self.current_intent == "":
            return self.acts["ask"] + "(" + self.acts["intent"] + ")"
        result = self.find_sample()

        answer = self.acts["offer"] + "("
        counter = 1
        if code == 0:
            self.current_offer = []
            for i in result:
                if i in self.offered:
                    continue
                self.offered.append(i)
                self.current_offer.append(i)

                if counter == 1:
                    answer = answer + self.domain + "=" + i[self.domain]
                else:
                    answer = answer + "," + self.domain + "=" + i[self.domain]
                counter += 1

                if counter > 3 or counter > len(result):
                    break

            if answer == self.acts["offer"] + "(":
                return self.acts["inform"] + "(" + self.acts["failure"] + ")"
            else:
                return answer + ")"

        if len(result) == 0:
            return self.acts["inform"] + "(" + self.acts["failure"] + ")"
        else:
            self.current_offer = []
            for i in result:
                if i not in self.offered:
                    self.offered.append(i)
                self.current_offer.append(i)

                if counter == 1:
                    answer = answer + self.domain + "=" + i[self.domain]
                else:
                    answer = answer + "," + self.domain + "=" + i[self.domain]
                counter += 1

                if counter > 3 or counter > len(result):
                    break

        return answer + ")"

    def getInformed(self, slot_name, slot_value):

        self.current_offer = []
        if slot_name == self.acts["intent"]:
            flag = 0
            for i in self.intents:
                if i[0] == slot_value:
                    flag = 1
                    self.current_intent = slot_value

            for i in range(len(self.intents)):
                if self.intents[i][0] == self.current_intent:
                    for m in self.intents[i][1]:
                        self.intents[i][1][m] = ""
                        if m + "*" in self.marked_intents[i][1]:
                            self.marked_intents[i][1][m + "*"] = ""

            if flag == 0:
                return flag
        else:
            flag = -1
            for i in range(len(self.intents)):
                if self.intents[i][0] == self.current_intent:
                    for m in self.intents[i][1]:
                        if m == slot_name:
                            self.intents[i][1][m] = slot_value
                            if m + "*" in self.marked_intents[i][1]:
                                self.marked_intents[i][1][m + "*"] = slot_value
                            flag = 1

        result = self.find_sample()
        if len(result) < 4:
            return -2
        return flag

    def check_finished(self):
        for i in self.intents:
            for m in i[1]:
                if i[1][m] is "":
                    return 0

        return 1

    def find_sample(self):
        result = []

        if self.intents == "" or self.current_intent == "":
            return result

        for i in self.intents:
            if i[0] == self.current_intent:
                utter = i[1]
                break

        utterList = [[k, v] for k, v in utter.items()]
        utterList = [elem for elem in utterList if elem[1] != '' and elem[1] != self.acts["anyway"]]

        for i in self.db:
            flag = 1
            for m in utterList:
                if m[0] not in i:
                    continue
                if i[m[0]] != m[1]:
                    flag = 0
                    break
            if flag:
                result.append(i)

        return result

    def choose(self, chosen):
        flag = 0

        for i in self.offered:
            if chosen in i.values():
                flag = 1
                buff = i.copy()

        self.offered.clear()
        self.offered = buff

        if flag:
            return self.acts["success"] + "(" + chosen + ")"
        else:
            return chosen + " " + self.acts["failure"]

    def ask_info(self, utter):

        answer = self.acts["inform"] + "("
        for i in range(len(utter)):
            buff = self.offered[utter[i]]
            if i == 0:
                answer += utter[i] + "=" + buff
            else:
                answer += "," + utter[i] + "=" + buff
        answer += ")"

        return answer

