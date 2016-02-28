import re
import sys

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


def to_sentences(s):
    return map(lambda x: Sentence(x), strip(s.split('&&')))


class Knowledge:
    def __init__(self, knowledge):
        self.knowledge = knowledge
        parts = knowledge.split(IMPLICATION)
        parts = map(lambda x: x.strip(), parts)
        if len(parts) == 2:
            self.premise = to_sentences(parts[0])
            self.conclusion = to_sentences(parts[1])
        else:
            self.conclusion = to_sentences(parts[0])

    def __str__(self):
        return self.knowledge


input_file = sys.argv[2]
sentences = []
with open(input_file, 'r') as fin:
    query = fin.readline()
    for _ in range(int(fin.readline().strip())):
        sentence = Knowledge(fin.readline())
        sentences.append(sentence)

for sentence in sentences:
    print sentence.conclusion[0]
