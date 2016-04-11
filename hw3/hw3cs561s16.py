import itertools
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
        self.probability = {True: {}, False: {}}
        self.set_names(lines)
        self.populate_probability(lines[1:])

    def populate_probability(self, lines):
        if self.is_standalone():
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
        return self.probability[occurence]

    def is_standalone(self):
        return len(self.given) == 0

    def set_names(self, lines):
        event = lines[0]
        split = event.split("|")
        self.name = split[0].strip()
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
        if not q.given:
            return reduce(lambda acc, t: acc * self.calculate(t.name, t.occurence), q.to_calculate, 1)

    def generate_bool_table(self, size):
        permutation = list(itertools.product(*["-+"] * size))
        return map(lambda x: ''.join(map(str, x)), permutation)

    def calculate(self, event, occurence):
        node = self.nodes[event]
        if node.is_standalone():
            return node.get_probability(occurence)
        probability_table = node.get_probability(occurence)
        result = 0
        for parent_occurence, parent_probability in probability_table.iteritems():
            product = parent_probability
            combinations = zip(list(parent_occurence), node.given)
            for combination in combinations:
                product *= self.calculate(combination[1], self.convert(combination[0]))
            result += product
        return result

    def convert(self, str):
        if str == "+":
            return True
        else:
            return False


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
print result
