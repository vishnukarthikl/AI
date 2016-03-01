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

    def has_variables(self):
        return len(self.variables) - len(self.constants())

    def constants(self):
        return filter(lambda x: self.is_constant(x), self.variables)

    def is_constant(self, variable):
        return variable[0].isupper()


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

    def resolve(self, queries):
        can_resolve = False
        if len(queries) == 1:
            query = queries[0]
            if query.has_variables():
                for constant in kb.constants:
                    can_resolve = self.validate(query, {query.variables[0]: constant})
                    if can_resolve:
                        return True
            else:
                return self.validate(query, {})
        else:
            for query in queries:
                can_resolve = self.validate(query, {})
            if not can_resolve:
                return False
            return True

    def validate(self, query, scope):
        dependent = self.search(query.predicate)
        to_resolve = dependent.conclusion
        if len(dependent.premise) == 0:
            for i, parameter in enumerate(to_resolve.variables):
                if to_resolve.is_constant(parameter) and to_resolve.variables[i] != query.variables[i]:
                    return False
            return True
        else:
            for i, parameter in enumerate(to_resolve.variables):
                if not to_resolve.is_constant(parameter):
                    scope[parameter] = query.variables[i]

            for premise in dependent.premise:
                is_valid = self.validate(premise, scope.copy())
                if not is_valid:
                    return False
            return True

    def search(self, predicate):
        for knowledge in self.kb.knowledges:
            if knowledge.conclusion.predicate == predicate:
                return knowledge
        return None


input_file = sys.argv[2]
kb = KnowledgeBase()
with open(input_file, 'r') as fin:
    query = to_sentences(fin.readline())
    for _ in range(int(fin.readline().strip())):
        kb.add_knowledge(Knowledge(fin.readline()))

resolver = InferenceResolver(kb)
resolver.resolve(query)
