from typing import Optional, List, Tuple

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
                    expression = format_expression_without_eq(expression, index, open_bracket_index,
                                                              close_bracket_index)
                    break

                if expression[index - 1] == ")" and expression[index + 1] != "(":
                    open_bracket_index = get_bracket_index(index - 2, 0, expression, "open")
                    right_literal_index = get_literal_index(expression, index, "right")
                    expression = format_expression_without_eq(expression, index, open_bracket_index,
                                                              right_literal_index)
                    break

                if expression[index - 1] != ")" and expression[index + 1] == "(":
                    left_literal_index = get_literal_index(expression, index, "left")
                    close_bracket_index = get_bracket_index(index + 2, len(expression), expression, "close")
                    expression = format_expression_without_eq(expression, index, left_literal_index,
                                                              close_bracket_index)
                    break

                if expression[index - 1] != ")" and expression[index + 1] != "(":
                    left_literal_index = get_literal_index(expression, index, "left")
                    right_literal_index = get_literal_index(expression, index, "right")
                    expression = format_expression_without_eq(expression, index, left_literal_index,
                                                              right_literal_index)
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
    resolution_steps, clauses = resolution(clause_list, [])
    unique_literals = sorted(set(literal for clause in clauses for literal in clause))
    resolution_steps.append("Zbytek po použití rezoluční metody: {%s}" % ", ".join(unique_literals))
    result, result_desc = get_result(clauses)
    resolution_steps.append(result_desc)
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


def resolution(clauses, steps):
    steps.append("Použití rezoluční metody:")
    steps.append("Množina klauzulí: %s" % clauses_to_string(clauses))

    # TAUTOLOGY CHECK
    step, clauses = remove_tautologies(clauses)
    steps.extend(step)

    # ONE TYPE LITERAL CHECK
    step, clauses = remove_single_type_occurrences(clauses)
    steps.extend(step)

    # RESOLUTION
    literal_set = get_set_of_literals(clauses)

    # GET POSITIVE AND NEGATIVE INDEXES OF EACH LITERAL
    for literal in literal_set:
        print(literal, "|", clauses)
        neg_literals, pos_literals = get_neg_pos_literal_indexes(clauses, literal)

        # MAKE RESOLVENT
        resolvent_list = []
        for pos_literal in pos_literals:
            for neg_literal in neg_literals:
                resolvent = make_resolvent(copy.deepcopy(clauses[pos_literal]), copy.deepcopy(clauses[neg_literal]))
                steps.append("Z klauzulí: %s a %s vznikne rezolventa: %s" % (clauses_to_string([clauses[pos_literal]]), clauses_to_string([clauses[neg_literal]]), clauses_to_string([resolvent]) if resolvent else "{}"))
                if resolvent:
                    resolvent_list.append(resolvent)

        # REMOVE CLAUSES USED TO COMBINE AND ADD NEW RESOLVENT
        clauses_to_remove = sorted(set(pos_literals + neg_literals), reverse=True)
        print(resolvent_list, "|", clauses_to_remove)
        if len(clauses) > 1 and clauses_to_remove:
            for index in clauses_to_remove:
                clauses.pop(index)
            clauses.extend(resolvent_list)
            clauses = remove_duplicates(clauses)
            steps.append("Množina klauzulí: %s" % clauses_to_string(clauses))

    return steps, clauses

def remove_single_type_occurrences(clauses):
    steps = []
    literal_set = get_set_of_literals(clauses)
    for literal in literal_set:
        neg_literals, pos_literals = get_neg_pos_literal_indexes(clauses, literal)
        step, indexes_to_remove = check_single_type_occurrence(pos_literals, neg_literals, clauses, literal)
        if step:
            for index in sorted(set(indexes_to_remove), reverse=True):
                if index <= len(clauses):
                    clauses.pop(index)
            steps.extend(step)
            steps.append("Množina klauzulí: %s" % clauses_to_string(clauses))
    return steps, clauses


def check_single_type_occurrence(pos_literals: list[int], neg_literals: list[int], clauses: list[list[str]], literal: str) -> Tuple[List, List]:
    """
    If not "a" and "¬a" remove all clauses with that literal.
    """
    if not pos_literals and not neg_literals:
        return [], []

    steps = ""
    if not pos_literals:
        steps += "Literál ¬%s nemá opačný výskyt, klauzule: " % literal
        step = ""
        for index in neg_literals:
            step += "%s" % clauses_to_string([clauses[index]])
        steps += step + " bude/budou odstraněny."
        return [steps], neg_literals

    if not neg_literals:
        steps += "Literál %s nemá opačný výskyt, klauzule: " % literal
        step = ""
        for index in pos_literals:
            step += "%s" % clauses_to_string([clauses[index]])
        steps += step + " bude/budou odstraněny."
        return [steps], pos_literals

    return [], []


def get_set_of_literals(clauses: list[list[str]]) -> list[str]:
    literal_set = set()
    for clause in clauses:
        for literal in clause:
            if len(literal) == 1:
                literal_set.add(literal)
            elif len(literal) == 2:
                literal_set.add(literal[1])

    return sorted(literal_set)

def get_neg_pos_literal_indexes(clauses: list[list[str]], literal) -> tuple[list[int], list[int]]:
    neg_literals = []
    pos_literals = []
    for index, clause in enumerate(clauses):
        for comp_literal in clause:
            if comp_literal.startswith("¬"):
                if literal == comp_literal[1]:
                    neg_literals.append(index)
            else:
                if literal == comp_literal:
                    pos_literals.append(index)

    if not neg_literals or not pos_literals:
        return [], []
    return neg_literals, pos_literals


def remove_tautologies(clauses):
    steps = []
    for index, clause in enumerate(clauses):
        if is_tautology(clause):
            steps.append("Klauzule: %s je tautologie - odstraňuje se." % clauses_to_string([clause]))
            clauses.pop(index)
            steps.append("Množina klauzulí: %s" % clauses_to_string(clauses))
    return steps, clauses


def make_resolvent(clause: list, clause2: list) -> list:
    """
    Return resolvent out of two clauses.
    """
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


def is_tautology(clause: list[str]) -> bool:
    """
    Return bool whether clause is tautology.
    """
    positive_literals = set()
    negative_literals = set()

    for literal in clause:
        if literal.startswith("¬"):
            negative_literals.add(literal[1:])
        else:
            positive_literals.add(literal)

    return not positive_literals.isdisjoint(negative_literals)


def remove_duplicates(list_of_clauses: list[list[str]]) -> list:
    result = []
    for item in list_of_clauses:
        if item not in result:
            result.append(item)
    return result


def clauses_to_string(clauses: list[list[str]]) -> str:
    """
    Convert a set of clauses to string.
    """
    clauses_str = ""
    for clause in clauses:
        clauses_str += "{"
        clauses_str += ", ".join(clause) + "}, "
    return clauses_str[:-1]


def get_result(clauses: list[list[str]]) -> Tuple[bool, str]:
    for clause in clauses:
        if not clause:
            clauses.remove(clause)
    if clauses:
        return False, "Formule není splnitelná"
    else:
        return True, "Formule je splnitelná"
