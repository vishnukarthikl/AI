import re
import sys


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
        self.given = []
        self.probability = {}
        self.set_names(lines)
        self.populate_probability(lines[1:])

    def populate_probability(self, lines):
        if self.standalone():
            self.probability["*"] = float(lines[0])
        else:
            for line in lines:
                split = line.split(" ")
                p = float(split[0])
                occurence = "".join(split[1:])
                self.probability[occurence] = p

    def standalone(self):
        return len(self.given) == 0

    def set_names(self, lines):
        event = lines[0]
        split = event.split("|")
        self.name = split[0]
        if len(split) > 1:
            self.given = split[1].strip().split(" ")

    def __str__(self):
        if len(self.given) == 0:
            return self.name
        else:
            return self.name + "|" + str(self.given)


class BayesNet:
    def __init__(self):
        self.nodes = {}

    def add(self, node):
        self.nodes[node.name] = node

    def process(self, q):
        pass


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
        if len(lines) == 0:
            return nodes
        else:
            nodes.append(node)


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
