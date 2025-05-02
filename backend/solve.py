from sympy import symbols  # type: ignore
from sympy.logic.boolalg import to_cnf  # type: ignore
from sympy.logic.inference import satisfiable  # type: ignore
import re
import copy

OPERATOR_DICT = {
    "¬": "~",
    "∧": "&",
    "∨": "|",
    "→": ">>",
}

OPERATOR_TRANSLATOR = str.maketrans(OPERATOR_DICT)

REVERSE_OPERATOR_DICT = {
    "~": "¬",
    "&": "∧",
    "|": "∨",
    ">>": "→",
}


def get_bracket_index(start, stop, expr, br_type):
    br_count = 1
    br_index = 0
    first_br = "("
    second_br = ")"
    step = 1

    if br_type == "open":
        first_br = "("
        second_br = ")"
        step = -1
    elif br_type == "close":
        first_br = ")"
        second_br = "("
        step = 1

    for index in range(start, stop, step):
        if expr[index] == first_br:
            br_count -= 1
            if br_count < 1:
                br_index = index
                break
        elif expr[index] == second_br:
            br_count += 1
    return br_index


def get_literal_index(expr, index, side):
    if side == "left":
        if expr[index - 2] == "~":
            return index - 2
        else:
            return index - 1
    elif side == "right":
        if expr[index + 1] == "~":
            return index + 2
        else:
            return index + 1

def format_expression_without_eq(expr, eq_index, first_part_index, second_part_index):
    first_part = "(" + "~" + expr[first_part_index:eq_index] + "|" + expr[eq_index + 1:second_part_index + 1] + ")"
    second_part = "(" + expr[first_part_index:eq_index] + "|" + "~" + expr[eq_index + 1:second_part_index + 1] + ")"
    return expr[0:first_part_index] + first_part + "&" + second_part + expr[second_part_index + 1:]

def rewrite_equivalence(expression):
    eq_count = expression.count("↔")
    for i in range(0, eq_count + 1):
        for index, char in enumerate(expression):
            if char == "↔":
                if expression[index - 1] == ")" and expression[index + 1] == "(":
                    open_bracket_index = get_bracket_index(index - 2, 0, expression, "open")
                    close_bracket_index = get_bracket_index(index + 2, len(expression), expression, "close")
                    expression = format_expression_without_eq(expression, index, open_bracket_index, close_bracket_index)
                    break

                if expression[index - 1] == ")" and expression[index + 1] != "(":
                    open_bracket_index = get_bracket_index(index - 2, 0, expression, "open")
                    right_literal_index = get_literal_index(expression, index, "right")
                    expression = format_expression_without_eq(expression, index, open_bracket_index, right_literal_index)
                    break

                if expression[index - 1] != ")" and expression[index + 1] == "(":
                    left_literal_index = get_literal_index(expression, index, "left")
                    close_bracket_index = get_bracket_index(index + 2, len(expression), expression, "close")
                    expression = format_expression_without_eq(expression, index, left_literal_index, close_bracket_index)
                    break

                if expression[index - 1] != ")" and expression[index + 1] != "(":
                    left_literal_index = get_literal_index(expression, index, "left")
                    right_literal_index = get_literal_index(expression, index, "right")
                    expression = format_expression_without_eq(expression, index, left_literal_index, right_literal_index)
                    break

    return expression


def translate_back(expression: str) -> str:
    for key, value in REVERSE_OPERATOR_DICT.items():
        expression = expression.replace(key, value)
    return expression


def solve(formula: str):
    steps = []
    formated_formula = prepare_for_cnf(formula)
    steps.append("Rozložení ekvivalencí: %s" % translate_back(formated_formula))
    found_symbols = init_symbols(formated_formula)
    expression = eval(formated_formula, found_symbols)
    cnf = to_cnf(expression)
    cnf_str = str(cnf)
    back_translated_formula = translate_back(cnf_str)
    steps.append("Převod do kunjuktivní normální formy: %s" % back_translated_formula)
    clause_list = split_to_list_of_literals(back_translated_formula)
    resolution_steps, result = resolution(clause_list)
    steps.extend(resolution_steps)
    return steps, result


def prepare_for_cnf(formula: str) -> str:
    translated_formula = formula.translate(OPERATOR_TRANSLATOR)
    formula_without_equivalence = rewrite_equivalence(translated_formula)
    return formula_without_equivalence


def init_symbols(formula: str) -> dict:
    variables = set(re.findall(r"[A-Za-z]", formula))
    return {var: symbols(var) for var in variables}


def split_to_list_of_literals(formula: str) -> list[list[str]]:
    clauses = []
    clauses_str = formula.split(' ∧ ')
    for clause in clauses_str:
        clause = clause.replace("(", "").replace(")", "")
        current_clause = clause.split(' ∨ ')
        clauses.append(current_clause)
    return clauses


def resolution(clauses):
    if clauses[0][0] == "True":
        return ["Formule je tautologie, není potřeba použít rezoluční metodu."]
    else:
        steps = ["Použití rezoluční metody:", "Množina klauzulí: %s" % clauses_to_string(clauses)]

    def update_clauses(clause1, clause2):
        resolvent = make_resolvent(copy.deepcopy(clause1), copy.deepcopy(clause2))
        steps.append("Z klauzulí: " + clauses_to_string([clause1]) + " a " + clauses_to_string([clause2]) + " vznikne resolventa: " + clauses_to_string([resolvent]))
        clauses.remove(clause1)
        clauses.remove(clause2)
        clauses.append(resolvent)
        steps.append("Zbývající klauzule: %s" % clauses_to_string(clauses))

    found = False
    while True:
        if found:
            found = False
        for i, clause in enumerate(clauses):
            for literal in clause:
                for j, compared_clause in enumerate(clauses):
                    if i == j:
                        break
                    for compared_literal in compared_clause:
                        if len(literal) == 2 and len(compared_literal) == 1:
                            if literal[1] == compared_literal:
                                update_clauses(clause, compared_clause)
                                found = True
                                break

                        elif len(literal) == 1 and len(compared_literal) == 2:
                            if literal == compared_literal[1]:
                                update_clauses(clause, compared_clause)
                                found = True
                                break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        if not found:
            steps.pop()
            result = get_result(clauses)
            steps.append("Zbytek po použití rezoluční metody: %s" % clauses_to_string(result))
            if result:
                steps.append("Formule není splnitelná")
                return steps, False
            else:
                steps.append("Formule je splnitelná")
                return steps, True



def make_resolvent(clause: list, clause2: list) -> list:
    resolvent = set(clause + clause2)
    resolvent_copy = resolvent.copy()
    for literal in resolvent_copy:
        if literal.startswith("¬"):
            opposite = literal[1:]
        else:
            opposite = "¬" + literal
        if opposite in resolvent:
            resolvent.remove(literal)
            resolvent.remove(opposite)

    return list(resolvent)


def clauses_to_string(clauses: list[list[str]]) -> str:
    clauses_str = ""
    for clause in clauses:
        clauses_str += "{"
        clauses_str += ", ".join(clause) + "},"
    return clauses_str[:-1]


def get_result(clauses):
    for clause in clauses:
        if not clause:
            clauses.remove(clause)
    print(clauses)
    return clauses