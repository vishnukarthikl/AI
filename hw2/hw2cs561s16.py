import re
import sys
from copy import deepcopy
from itertools import chain, imap


class Logger:
    def __init__(self):
        self.output = []

    def log(self, line):
        if len(self.output) == 0:
            self.output.append(line)
        elif self.output[-1] != line:
            self.output.append(line)


def flatmap(f, items):
    return list(chain.from_iterable(imap(f, items)))


def is_constant(variable):
    return variable[0].isupper()


def is_variable(variable):
    return not is_constant(variable)


IMPLICATION = '=>'


def strip(search):
    return map(lambda x: x.strip(), search)


def stringify(sentence, prefix):
    result = prefix + ": "
    result += sentence.predicate + "("
    for j, variable in enumerate(sentence.variables):
        if is_constant(variable):
            result += variable
        else:
            result += "_"
        if j != len(sentence.variables) - 1:
            result += ", "
        else:
            result += ")"
    return result


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

    def has_variables(self):
        return len(self.variables) - len(self.constants()) > 0

    def constants(self):
        return filter(is_constant, self.variables)

    def is_fact(self):
        return len(self.predicate) == 0


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

    def fetch_goals(self, query):
        goals = []
        for knowledge in self.knowledges:
            if self.can_unify(knowledge, query):
                goals.append(knowledge)
        return goals

    def can_unify(self, knowledge, query):
        if knowledge.conclusion.predicate == query.predicate:
            for i, query_variable in enumerate(query.variables):
                knowledge_variable = knowledge.conclusion.variables[i]
                if is_constant(query_variable) and is_constant(knowledge_variable):
                    if query_variable != knowledge_variable:
                        return False
            return True
        else:
            return False


class Knowledge:
    def __init__(self, knowledge):
        self.knowledge = knowledge
        parts = knowledge.split(IMPLICATION)
        parts = map(lambda x: x.strip(), parts)
        if len(parts) == 2:
            self.premise = to_sentences(parts[0])
            self.conclusion = Sentence(parts[1])
        else:
            self.premise = []
            self.conclusion = Sentence(parts[0])

    def __str__(self):
        return self.knowledge

    def all_sentences(self):
        sentences = []
        if len(self.premise) > 0:
            sentences += self.premise
        sentences += [self.conclusion]
        return sentences

    def constants(self):
        return flatmap(lambda x: x.constants(), self.all_sentences())


class InferenceResolver:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.logger = Logger()

    def resolve(self, queries):
        if len(queries) == 1:
            query = queries[0]
            goals = self.kb.fetch_goals(query)
            goals = map(lambda x: self.replace_query(x, query), goals)
            for _ in self.fol_or(goals):
                return True
        else:
            return False

    def fol_or(self, goals):
        for goal in goals:
            success, theta = self.validate(goal)
            if success:
                yield theta

    def validate(self, goal):
        pass

    def replace_query(self, goal, query_sentence):
        replace_map = {}
        new_goal = deepcopy(goal)
        for i, variable in enumerate(goal.conclusion.variables):
            query_variable = query_sentence.variables[i]
            new_goal.conclusion.variables[i] = query_variable
            replace_map[variable] = query_variable

        for predicate in new_goal.premise:
            for i, variable in enumerate(predicate.variables):
                if variable in replace_map:
                    predicate.variables[i] = replace_map[variable]

        return new_goal


input_file = sys.argv[2]
output_file = "output.txt"
kb = KnowledgeBase()
with open(input_file, 'r') as fin:
    query = to_sentences(fin.readline())
    for _ in range(int(fin.readline().strip())):
        kb.add_knowledge(Knowledge(fin.readline()))

resolver = InferenceResolver(kb)
answer = resolver.resolve(query)
with open(output_file, 'w') as f:
    f.truncate()
    for line in resolver.logger.output:
        f.writelines(line + '\n')
    f.writelines(str(answer))
