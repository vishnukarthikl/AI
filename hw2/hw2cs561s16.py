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
        dependents = self.search(query.predicate)
        for dependent in dependents:
            to_resolve = dependent.conclusion
            if len(dependent.premise) == 0:
                for i, parameter in enumerate(to_resolve.variables):
                    if to_resolve.is_constant(parameter):
                        if not query.is_constant(query.variables[i]):
                            if parameter != scope[query.variables[i]]:
                                return False
                        else:
                            if parameter != query.variables[i]:
                                return False
                return True
            else:
                resolved_scope = {}
                for i, parameter in enumerate(to_resolve.variables):
                    if not to_resolve.is_constant(parameter):
                        if query.is_constant(query.variables[i]):
                            resolved_scope[parameter] = query.variables[i]
                        else:
                            resolved_scope[parameter] = scope[query.variables[i]]

                valid_scopes = {}
                all_unknown_variables = set()
                is_valid = False
                for i, premise in enumerate(dependent.premise):
                    is_valid = False
                    new_scope = {}
                    valid_scopes[i] = []
                    unknown_arguments = []
                    for argument in premise.variables:
                        if not premise.is_constant(argument):
                            if argument in resolved_scope:
                                new_scope[argument] = resolved_scope[argument]
                            else:
                                unknown_arguments.append(argument)

                    for unknown_argument in unknown_arguments:
                        all_unknown_variables.add(unknown_argument)

                    if len(unknown_arguments) == 0:
                        if self.validate(premise, new_scope):
                            is_valid = True
                            valid_scopes[i].append(new_scope)
                    else:
                        for generated_scope in self.generate_scope_for_unknowns(unknown_arguments, new_scope):
                            if self.validate(premise, generated_scope):
                                is_valid = True
                                valid_scopes[i].append(generated_scope)

                    # some premise was not valid for any assignments
                    if not is_valid:
                        break

                # see if there is some assignment of variables that satisfy all premise
                if is_valid and self.variables_valid(valid_scopes, all_unknown_variables):
                    return True
            return False

    def generate_scope_for_unknowns(self, unknown_arguments, scope):
        scopes = []
        all_constants = self.kb.constants
        combinations = product(all_constants, repeat=len(unknown_arguments))
        for combination in combinations:
            generated_scope = scope.copy()
            for i, unknown_argument in enumerate(unknown_arguments):
                generated_scope[unknown_argument] = combination[i]
            scopes.append(generated_scope)
        return scopes

    def search(self, predicate):
        return filter(lambda knowledge: knowledge.conclusion.predicate == predicate, self.kb.knowledges)

    def variables_valid(self, valid_scopes, variables):
        if len(valid_scopes.keys()) == 1 or len(variables) == 0:
            return True
        combinations = product(*valid_scopes.values())
        for assignment in combinations:
            variable_assignment = {}
            for variable in variables:
                variable_assignment[variable] = []

            for variable in variables:
                for scope in assignment:
                    if variable in scope:
                        variable_assignment[variable].append(scope[variable])
            if assignment_valid(variable_assignment):
                return True

        return False


input_file = sys.argv[2]
kb = KnowledgeBase()
with open(input_file, 'r') as fin:
    query = to_sentences(fin.readline())
    for _ in range(int(fin.readline().strip())):
        kb.add_knowledge(Knowledge(fin.readline()))

resolver = InferenceResolver(kb)
print resolver.resolve(query)
