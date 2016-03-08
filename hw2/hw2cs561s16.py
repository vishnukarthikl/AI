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
            print line
        elif self.output[-1] != line:
            self.output.append(line)
            print line


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
        return self.predicate + "(" + ','.join(self.variables) + ")"

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
        self.random_variables = 0

    def add_knowledge(self, knowledge):
        self.knowledges.append(knowledge)
        new_constants = knowledge.constants()
        self.constants += filter(lambda x: x not in self.constants, new_constants)

    def fetch_rules(self, query):
        goals = []
        for knowledge in self.knowledges:
            if self.can_unify(knowledge, query):
                goals.append(knowledge)
        return self.standardize(goals)

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

    def standardize_all(self):
        self.knowledges = self.standardize(self.knowledges)

    def standardize(self, rules):
        standardized_rules = []
        for knowledge in rules:
            variable_changes = {}
            knowledge = deepcopy(knowledge)
            for i, variable in enumerate(knowledge.conclusion.variables):
                if is_variable(variable):
                    if variable not in variable_changes:
                        variable_changes[variable] = self.generate_variable()
                    knowledge.conclusion.variables[i] = variable_changes[variable]

            for premise in knowledge.premise:
                for i, premise_variable in enumerate(premise.variables):
                    if is_variable(premise_variable):
                        if premise_variable not in variable_changes:
                            variable_changes[premise_variable] = self.generate_variable()
                        premise.variables[i] = variable_changes[premise_variable]

            standardized_rules.append(knowledge)

        return standardized_rules

    def generate_variable(self):
        self.random_variables += 1
        return "a" + str(self.random_variables)


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
        if len(self.premise) == 0:
            return self.conclusion.__str__()
        else:
            return " && ".join(
                    map(lambda x: x.__str__(), self.premise)) + " " + IMPLICATION + " " + self.conclusion.__str__()

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
        self.random_variables = 0

    def resolve(self, queries):
        self.kb.standardize_all()
        if len(queries) == 1:
            query = queries[0]
            for theta in self.fol_or(query, {}):
                if theta:
                    return True
            return False
        else:
            for query in queries:
                valid = False
                for _ in self.fol_or(query, {}):
                    valid = True
                    self.logger.log(stringify(self.substitute({}, query), "True"))
                    break
                if not valid:
                    return False
            return True

    def fol_or(self, goal, theta):
        rules = self.kb.fetch_rules(goal)
        self.logger.log(stringify(self.substitute(theta, goal), "Ask"))
        valid = False
        for rule in rules:
            self.logger.log(stringify(self.substitute(theta, goal), "Ask"))
            for theta in self.fol_and(rule.premise, self.unify(rule.conclusion, goal, deepcopy(theta)),
                                      rule.conclusion):
                valid = True
                self.logger.log(stringify(self.substitute(theta, rule.conclusion), "True"))
                yield self.original_substituted_theta(theta, rule.conclusion)
        if not valid:
            self.logger.log(stringify(self.substitute(theta, goal), "False"))

    def fol_and(self, goals, theta, parent):
        if len(goals) == 0:
            yield theta
        else:
            first, rest = goals[0], goals[1:]
            valid = False
            for theta1 in self.fol_or(self.substitute(theta, first), deepcopy(theta)):
                valid = True
                for theta2 in self.fol_and(rest, deepcopy(theta1), parent):
                    yield self.original_substituted_theta(theta2, parent)
            if not valid:
                self.logger.log(stringify(self.substitute(theta, first), "False"))
                self.logger.log(stringify(self.substitute(theta, parent), "Ask"))

    def original_substituted_theta(self, theta, succeeded_rule):
        theta = deepcopy(theta)
        standardized_variables = succeeded_rule.variables
        for i, variable in enumerate(standardized_variables):
            if is_variable(variable):
                to_substitute = [k for k, v in theta.iteritems() if v == variable]
                for substitution in to_substitute:
                    theta[substitution] = theta[variable]
        return theta

    def unify(self, x, y, theta):
        theta = deepcopy(theta)
        if x.predicate != y.predicate:
            return None
        for i, x_variable in enumerate(x.variables):
            y_variable = y.variables[i]
            if is_constant(x_variable) and is_constant(y_variable) and x_variable != y_variable:
                return None
            elif is_variable(x_variable) and is_constant(y_variable) and x_variable not in theta:
                theta[x_variable] = y_variable
            elif is_variable(y_variable) and is_constant(x_variable) and y_variable not in theta:
                theta[y_variable] = x_variable
            elif is_variable(x_variable) and is_variable(y_variable) and y_variable not in theta:
                theta[y_variable] = x_variable

        return theta

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

    def substitute(self, theta, sentence):
        substituted_sentence = deepcopy(sentence)
        for i, variable in enumerate(sentence.variables):
            if is_variable(variable) and variable in theta:
                substituted_sentence.variables[i] = theta[variable]
        return substituted_sentence


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
