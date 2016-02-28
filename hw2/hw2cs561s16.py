import re
import sys
from itertools import chain, imap


def flatmap(f, items):
    return list(chain.from_iterable(imap(f, items)))


IMPLICATION = '=>'


def strip(search):
    return map(lambda x: x.strip(), search)


class Sentence:
    def __init__(self, s):
        self.s = s
        search = re.search(r'(~?)(.*?)\((.*)\)', s)
        if search.group(1) != '':
            self.negated = True
        else:
            self.negated = False
        self.predicate = search.group(2)
        self.variables = strip(search.group(3).split(','))

    def __str__(self):
        return self.s

    def constants(self):
        return filter(lambda x: x.istitle(), self.variables)


def to_sentences(s):
    return map(lambda x: Sentence(x), strip(s.split('&&')))


class KnowledgeBase:
    def __init__(self):
        self.knowledges = []
        self.constants = []

    def add_knowledge(self, knowledge):
        self.knowledges.append(knowledge)
        new_constants = knowledge.constants()
        self.constants += filter(lambda x: x not in self.constants, new_constants)


class Knowledge:
    def __init__(self, knowledge):
        self.knowledge = knowledge
        parts = knowledge.split(IMPLICATION)
        parts = map(lambda x: x.strip(), parts)
        if len(parts) == 2:
            self.premise = to_sentences(parts[0])
            self.conclusion = to_sentences(parts[1])
        else:
            self.premise = []
            self.conclusion = to_sentences(parts[0])

    def __str__(self):
        return self.knowledge

    def all_sentences(self):
        sentences = []
        if len(self.premise) > 0:
            sentences += self.premise
        sentences += self.conclusion
        return sentences

    def constants(self):
        return flatmap(lambda x: x.constants(), self.all_sentences())


input_file = sys.argv[2]
kb = KnowledgeBase()
with open(input_file, 'r') as fin:
    query = fin.readline()
    for _ in range(int(fin.readline().strip())):
        kb.add_knowledge(Knowledge(fin.readline()))

print kb.constants