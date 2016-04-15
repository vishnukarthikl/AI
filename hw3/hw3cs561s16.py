import itertools
import re
import sys
from decimal import Decimal


class Query():
    def __init__(self, regex, query):
        self.query = ""
        self.to_calculate = []
        self.given = []
        self.query = query
        m = re.search(regex, query)
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


class ProbabiltyQuery(Query):
    def __init__(self, query):
        Query.__init__(self, r"P\((.*?)\)", query)

    def __str__(self):
        return self.query


class ExpectedUtilityQuery(Query):
    def __init__(self, query):
        Query.__init__(self, r"EU\((.*?)\)", query)


class Node():
    def __init__(self, lines):
        self.parents = []
        self.set_names(lines)
        self.set_type(lines)
        if not self.decision:
            self.populate_probability(lines[1:])

    def populate_probability(self, lines):
        self.probability = {True: {}, False: {}}
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
            if self.decision:
                return {'': 1.0}
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

    def set_type(self, lines):
        if lines[1] == 'decision':
            self.decision = True
        else:
            self.decision = False


class BayesNet:
    def __init__(self):
        self.nodes = {}

    def add(self, node):
        self.nodes[node.name] = node

    def generate_bool_table(self, size):
        permutation = list(itertools.product(*["-+"] * size))
        return map(lambda x: ''.join(map(str, x)), permutation)

    def process(self, q):
        if isinstance(q, ProbabiltyQuery):
            answer = self.enumerate_all(self.nodes.copy(), q.to_calculate + q.given) / self.enumerate_all(
                    self.nodes.copy(),
                    q.given)
            return Decimal(str(answer)).quantize(Decimal('.01'))
        elif isinstance(q, ExpectedUtilityQuery):
            total_utility = 0
            for occurence, value in utility.utility.iteritems():
                evidence_combination = map(lambda x: QueryEvent(x[1] + "=" + x[0]), zip(occurence, utility.events))
                if self.check(evidence_combination, q.to_calculate + q.given):
                    p1 = self.enumerate_all(self.nodes.copy(), evidence_combination + q.to_calculate + q.given)
                    p2 = self.enumerate_all(self.nodes.copy(), q.given + q.to_calculate)
                    probability = p1 / p2
                    total_utility += probability * value
            return int(round(total_utility))

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

    def add_utility(self, utility):
        self.utility = utility

    def check(self, combination, given):
        for c in combination:
            event = self.get_event(c.name, given)
            if event:
                if event.occurence != c.occurence:
                    return False
        return True

    def get_event(self, event, evidence):
        for e in evidence:
            if e.name == event:
                return e
        return None


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


def get_utility(lines):
    return get_till(lines, "")[0]


def get_nodes(lines):
    nodes = []
    while True:
        node, lines = get_till(lines, "***")
        nodes.append(node)
        if len(lines) == 0:
            return nodes, []


class Utility:
    def __init__(self, lines):
        self.utility = {}
        self.populate_events(lines[0])
        self.populate_utility_values(lines[1:])

    def populate_events(self, line):
        events = line.split("|")[1]
        self.events = map(lambda e: e.strip(), events.split())

    def populate_utility_values(self, lines):
        for line in lines:
            split = line.split(" ")
            value = int(split[0])
            occurence = "".join(split[1:])
            self.utility[occurence] = value


def convert_to_query(query):
    if query.startswith('P'):
        return ProbabiltyQuery(query)
    elif query.startswith('EU'):
        return ExpectedUtilityQuery(query)


input_file = sys.argv[2]
output_file = "output.txt"

with open(input_file, 'r') as fin:
    lines = fin.readlines()
lines = map(lambda x: x.strip(), lines)
queries, lines = get_queries(lines)
queries = map(lambda q: convert_to_query(q), queries)

bayesNet = BayesNet()
node_lines, lines = get_till(lines, "******")
nodes = map(lambda n: Node(n), get_nodes(node_lines)[0])
for node in nodes:
    bayesNet.add(node)
if lines:
    utility = Utility(get_utility(lines))
    bayesNet.add_utility(utility)

result = map(lambda q: bayesNet.process(q), queries)
with open('output.txt', 'w') as f:
    f.truncate()
    for r in result:
        print r
        f.write(r.__str__() + "\n")
