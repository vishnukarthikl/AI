import re
import sys
from itertools import chain, imap, product


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


def all_same(variable_assignment):
    return len(set(variable_assignment)) == 1


def assignment_valid(variable_assignment):
    for key, value in variable_assignment.items():
        if not all_same(value):
            return False
    return True


class InferenceResolver:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def resolve(self, queries):
        can_resolve = False
        if len(queries) == 1:
            query = queries[0]
            if query.has_variables():
                for constant in kb.constants:
                    scope = {}
                    for variable in query.variables:
                        if not query.is_constant(variable):
                            scope[variable] = constant
                    can_resolve = self.validate(query, scope)
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
        return can_resolve

    def validate(self, query, scope):
        dependents = self.search(query.predicate)
        is_valid = False
        for dependent in dependents:
            to_resolve = dependent.conclusion
            if len(dependent.premise) == 0:
                is_valid = True
                for i, parameter in enumerate(to_resolve.variables):
                    if to_resolve.is_constant(parameter):
                        if not query.is_constant(query.variables[i]):
                            if parameter != scope[query.variables[i]]:
                                is_valid = False
                        else:
                            if parameter != query.variables[i]:
                                is_valid = False
                if is_valid:
                    return True

            else:
                resolved_scope = self.resolve_variables(query, to_resolve, scope)
                valid_scopes = [{}]
                for i, premise in enumerate(dependent.premise):
                    is_valid = False
                    updated_new_valid_scopes = []
                    for valid_scope in valid_scopes:
                        new_scope, unknown_arguments = self.combine_scope(valid_scope, resolved_scope, premise)
                        if len(unknown_arguments) == 0:
                            if self.validate(premise, new_scope):
                                is_valid = True
                                updated_new_valid_scopes.append(new_scope)
                        else:
                            for generated_scope in self.generate_scope_for_unknowns(unknown_arguments, new_scope):
                                if self.validate(premise, generated_scope):
                                    is_valid = True
                                    updated_new_valid_scopes.append(generated_scope)

                    # some premise was not valid for any assignments
                    if not is_valid:
                        break
                    # the last premise was true for some assignment so return that
                    if i == len(dependent.premise) - 1:
                        return True
                    valid_scopes = updated_new_valid_scopes
                # see if there is some assignment of variables that satisfy all premise
                if is_valid:
                    return True

        return False

    def resolve_variables(self, query, to_resolve, scope):
        resolved_scope = {}
        for i, parameter in enumerate(to_resolve.variables):
            if not to_resolve.is_constant(parameter):
                if query.is_constant(query.variables[i]):
                    resolved_scope[parameter] = query.variables[i]
                else:
                    resolved_scope[parameter] = scope[query.variables[i]]
        return resolved_scope

    def generate_scope_for_unknowns(self, unknown_arguments, scope):
        scopes = []
        combinations = product(set(self.kb.constants), repeat=len(unknown_arguments))
        for combination in combinations:
            generated_scope = scope.copy()
            for i, unknown_argument in enumerate(unknown_arguments):
                generated_scope[unknown_argument] = combination[i]
            scopes.append(generated_scope)
        return scopes

    def search(self, predicate):
        return filter(lambda knowledge: knowledge.conclusion.predicate == predicate, self.kb.knowledges)

    def combine_scope(self, valid_scope, resolved_scope, premise):
        new_scope = valid_scope.copy()
        unknown_arguments = []
        for argument in premise.variables:
            if not premise.is_constant(argument):
                if argument in resolved_scope:
                    new_scope[argument] = resolved_scope[argument]
                if argument not in new_scope:
                    unknown_arguments.append(argument)
        return new_scope, unknown_arguments


input_file = sys.argv[2]
kb = KnowledgeBase()
with open(input_file, 'r') as fin:
    query = to_sentences(fin.readline())
    for _ in range(int(fin.readline().strip())):
        kb.add_knowledge(Knowledge(fin.readline()))

resolver = InferenceResolver(kb)
print resolver.resolve(query)
