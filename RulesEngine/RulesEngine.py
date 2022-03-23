

class Fact:
    def __init__(self, relation, first, second=None):
        self.relation = relation
        self.first = first
        self.second = second


class Rule:
    def __init__(self, rule_text):
        self._rule_text = rule_text
        parts = rule_text.split("=")
        self.left = parts[0].strip()
        self.right = parts[1].strip()


class RulesEngine:
    def __init__(self):
        self._facts = []
        self._rules = []

        self._default_val = None
        self.replace_none_with_default = False

    def set_default_behavior(self, default_value, replace_none_with_default=True):
        self._default_val = default_value
        self.replace_none_with_default = replace_none_with_default

    def fact_count(self):
        return len(self._facts)

    def add_fact(self, fact: Fact):
        if self.replace_none_with_default and fact.second is None:
            fact.second = self._default_val
        self._facts.append(fact)

    def rule_count(self):
        return len(self._rules)

    def add_rule(self, rule: Rule):
        self._rules.append(rule)

    def query(self, relation, first):
        return self._query_default(relation, first)

    def _query_default(self, relation, first):
        results = []
        for f in self._facts:
            if f.relation == relation and f.first == first:
                results.append(f.second)
                results += self._query_default(relation, f.second)

        # Now eval rules
        if relation == "has_value":
            for r in self._rules:
                if r.left == first:
                    self._set_vals(r.right)
                    self_calc = self._add_self_to_vars(r.right)
                    val = eval(self_calc)
                    self.add_fact(Fact("has_value", first, val))
                    results.append(val)

        return results

    def query_post(self, relation, second):
        results = []
        for f in self._facts:
            if f.relation == relation and f.second == second:
                results.append(f.first)
                results += self.query_post(relation, f.first)
        return results

    def _set_vals(self, calculation):
        for var in calculation.split():
            v_val = self._query_default("has_value", var)
            if len(v_val) > 0:
                self.__dict__[var] = v_val[0]

    def _add_self_to_vars(self, calculation):
        self_calculation = ""
        for var in calculation.split():
            if len(var) > 1:
                self_calculation += f" self.{var}"
            else:
                self_calculation += f" {var}"
        return self_calculation
