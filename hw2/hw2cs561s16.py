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

    def copy(self):
        return deepcopy(self)

    def are_variables_same(self, other):
        return self.variables != other.variables

    def unifiable_variables(self, other):
        for i, this_variable in enumerate(self.variables):
            that_variable = other.variables[i]
            if this_variable != that_variable:
                if is_constant(this_variable) and is_constant(that_variable):
                    return False
        return True


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
        return deepcopy(goals)

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
        for query in queries:
            if not self.validate(query):
                return False
        return True

    def validate(self, query):
        for unified_result_query in self.fol_or(query):
            if unified_result_query is None:
                self.logger.log(stringify(query, str(False)))
                return False
            else:
                self.logger.log(stringify(unified_result_query, str(True)))
                return True

        self.logger.log(stringify(query, str(False)))
        return False

    def fol_or(self, goal):
        rules = self.kb.fetch_rules(goal)
        if len(rules) == 0:
            self.logger.log(stringify(goal, "Ask"))
            yield None

        for rule in rules:
            self.logger.log(stringify(goal, "Ask"))
            goal_copy = goal.copy()
            if len(rule.premise) == 0:
                scope = {}
                ret = True
                if rule.conclusion.are_variables_same(goal):
                    for i, conclusion_variable in enumerate(rule.conclusion.variables):
                        goal_variable = goal.variables[i]
                        if conclusion_variable != goal_variable and is_variable(goal_variable):
                            scope[goal_variable] = conclusion_variable
                        elif conclusion_variable != goal_variable and is_constant(goal_variable):
                            ret = False
                    if not ret:
                        continue

                    for i, variables in enumerate(goal_copy.variables):
                        if goal_copy.variables[i] in scope:
                            goal_copy.variables[i] = scope[goal.variables[i]]
                yield goal_copy
            else:
                unified_goal, unified_rule = self.unify(goal_copy, rule)
                for scope in self.fol_and(unified_rule.premise):
                    if scope is not None:
                        rule_copy = deepcopy(unified_rule)
                        rule_copy.conclusion = self.substitute(rule_copy.conclusion, scope)
                        if unified_goal.unifiable_variables(rule_copy.conclusion):
                            yield self.rewrite_query(rule_copy.conclusion, unified_goal)
                    else:
                        break

    def fol_and(self, goals):
        if len(goals) == 0:
            yield {}
        else:
            scope = {}
            first, rest = goals[0], goals[1:]
            for result_query in self.fol_or(deepcopy(first)):
                if result_query is None:
                    self.logger.log(stringify(first, "False"))
                    yield None
                    return
                else:
                    self.logger.log(stringify(result_query, "True"))
                    inner_scope = self.substitute_premise(rest, first, result_query)
                    scope.update(inner_scope)
                    for subMapO in self.fol_and(deepcopy(rest)):
                        if subMapO is not None and len(subMapO) > 0:
                            inner_scope.update(subMapO)
                        if subMapO is None:
                            break
                        yield inner_scope
            yield None

    def unify(self, goal, rule):
        goal, rule = deepcopy(goal), deepcopy(rule)
        scope = {}
        for i, goal_variable in enumerate(goal.variables):
            rule_variable = rule.conclusion.variables[i]
            if is_constant(goal_variable) and is_variable(rule_variable):
                scope[rule_variable] = goal_variable
                rule.conclusion.variables[i] = goal_variable

        for premise in rule.premise:
            for i, pred_variable in enumerate(premise.variables):
                if pred_variable in scope:
                    premise.variables[i] = scope[pred_variable]

        return goal, rule

    def replace_query(self, goal, query_sentence):
        replace_map = {}
        new_goal = deepcopy(goal)
        for i, variable in enumerate(goal.conclusion.variables):
            query_variable = query_sentence.variables[i]
            new_goal.conclusion.variables[i] = query_variable
            replace_map[variable] = query_variable

        for premise in new_goal.premise:
            for i, variable in enumerate(premise.variables):
                if variable in replace_map:
                    premise.variables[i] = replace_map[variable]

        return new_goal

    def substitute(self, sentence, theta):
        substituted_sentence = deepcopy(sentence)
        for i, variable in enumerate(sentence.variables):
            if is_variable(variable) and variable in theta:
                substituted_sentence.variables[i] = theta[variable]
        return substituted_sentence

    def rewrite_query(self, conclusion, goal):
        query = goal.copy()
        for i, query_variable in enumerate(query.variables):
            conclusion_variable = conclusion.variables[i]
            if is_variable(query_variable) and is_constant(conclusion_variable):
                query.variables[i] = conclusion_variable
        return query

    def substitute_premise(self, rest, first, query):
        scope = {}
        rest = deepcopy(rest)
        for i, variables in enumerate(first.variables):
            var = first.variables[i]
            query_var = query.variables[i]
            if is_variable(var) and is_constant(query_var):
                scope[var] = query_var

        for premise in rest:
            for i, premise_variable in enumerate(premise.variables):
                if premise_variable in scope:
                    premise.variables[i] = scope[premise_variable]

        return scope


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
