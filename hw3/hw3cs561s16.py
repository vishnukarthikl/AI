import re
import sys
from decimal import Decimal


class QueryEvent():
    def __init__(self, str):
        self.str = str
        split = str.split("=")
        self.name = split[0].strip()
        occurence = split[1].strip()
        if occurence == "+":
            self.occurence = True
        else:
            self.occurence = False

    def __str__(self):
        return str


class ProbabiltyQuery():
    def __init__(self, query):
        self.query = query
        self.to_calculate = []
        self.given = []
        m = re.search(r"P\((.*?)\)", query)
        q = m.group(1)
        split = q.split("|")
        event, given = split[0], split[1:]
        self.set_to_calculate(event)
        self.set_given(given)

    def set_to_calculate(self, event):
        split = event.split(", ")
        self.to_calculate = map(lambda s: QueryEvent(s), split)

    def set_given(self, given):
        if given:
            split = given[0].split(", ")
            self.given = map(lambda s: QueryEvent(s), split)

    def __str__(self):
        return self.query


class Node():
    def __init__(self, lines):
        self.parents = []
        self.probability = {True: {}, False: {}}
        self.set_names(lines)
        self.populate_probability(lines[1:])

    def populate_probability(self, lines):
        if self.is_root():
            self.probability[True] = float(lines[0])
            self.probability[False] = 1 - float(lines[0])
        else:
            for line in lines:
                split = line.split(" ")
                p = float(split[0])
                occurence = "".join(split[1:])
                self.probability[True][occurence] = p
                self.probability[False][occurence] = 1 - p

    def get_probability(self, occurence):
        if self.is_root():
            return {'': self.probability[occurence]}
        return self.probability[occurence]

    def is_root(self):
        return len(self.parents) == 0

    def set_names(self, lines):
        event = lines[0]
        split = event.split("|")
        self.name = split[0].strip()
        if len(split) > 1:
            self.parents = split[1].strip().split(" ")

    def __str__(self):
        if len(self.parents) == 0:
            return self.name
        else:
            return self.name + "|" + str(self.parents)


class BayesNet:
    def __init__(self):
        self.nodes = {}

    def add(self, node):
        self.nodes[node.name] = node

    def process(self, q):
        answer = self.enumerate_all(self.nodes.copy(), q.to_calculate + q.given) / self.enumerate_all(self.nodes.copy(),
                                                                                                      q.given)
        return Decimal(str(answer)).quantize(Decimal('.01'))

    def convert(self, str):
        if str == "+":
            return True
        else:
            return False

    def enumerate_all(self, vars, evidence, event=None):
        if len(vars) == 0:
            return 1.0
        if not event:
            event = vars.keys()[0]
        start_node = self.nodes[event]
        parents = start_node.parents

        for p in parents:
            if not self.event_in_evidence(p, evidence):
                return self.enumerate_all(vars, evidence, p)

        result = 0
        if self.event_in_evidence(event, evidence):
            occurence = self.event_occurence(event, evidence)
            key = self.convert_to_key(parents, evidence)
            cp = start_node.get_probability(occurence)[key]
            result = cp * self.enumerate_all(self.remove(vars, start_node), evidence)
        else:
            for possible_occurence in [True, False]:
                cp = start_node.get_probability(possible_occurence)[self.convert_to_key(parents, evidence)]
                result += cp * self.enumerate_all(self.remove(vars, start_node),
                                                  self.add_evidence(evidence, start_node, possible_occurence))
        return result

    def event_in_evidence(self, event, evidence):
        for e in evidence:
            if e.name == event:
                return True
        return False

    def event_occurence(self, event, evidence):
        for e in evidence:
            if e.name == event:
                return e.occurence
        return False

    def convert_to_key(self, parents, evidence):
        return ''.join(map(lambda parent: self.convert_to_str(self.event_occurence(parent, evidence)), parents))

    def convert_to_str(self, bool):
        if bool:
            return "+"
        else:
            return "-"

    def remove(self, vars, node):
        copied = vars.copy()
        if node.name in copied:
            del copied[node.name]
        return copied

    def add_evidence(self, evidence, event, occurence):
        return evidence + [QueryEvent(event.name + "=" + self.convert_to_str(occurence))]


class Event:
    def __init__(self, probability, happened):
        self.probability = probability
        self.happened = happened

    def probability(self, happen):
        if happen and self.happened or (not happen and not self.happened):
            return self.probability
        else:
            return 1 - self.probability


def get_till(lines, delimiter):
    queries = []
    for i, line in enumerate(lines):
        if line == delimiter:
            return queries, lines[i + 1:]
        queries.append(line)
    return queries, []


def get_queries(lines):
    return get_till(lines, "******")


def get_nodes(lines):
    nodes = []
    while True:
        node, lines = get_till(lines, "***")
        nodes.append(node)
        if len(lines) == 0:
            return nodes


input_file = sys.argv[2]
output_file = "output.txt"

with open(input_file, 'r') as fin:
    lines = fin.readlines()
lines = map(lambda x: x.strip(), lines)
queries, lines = get_queries(lines)
queries = map(lambda q: ProbabiltyQuery(q), queries)

bayesNet = BayesNet()
nodes = map(lambda n: Node(n), get_nodes(lines))
for node in nodes:
    bayesNet.add(node)

result = map(lambda q: bayesNet.process(q), queries)
for r in result:
    print r
