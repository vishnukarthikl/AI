import sys


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
queries = []

with open(input_file, 'r') as fin:
    lines = fin.readlines()

lines = map(lambda x: x.strip(), lines)

queries, lines = get_queries(lines)
nodes = get_nodes(lines)
print nodes
