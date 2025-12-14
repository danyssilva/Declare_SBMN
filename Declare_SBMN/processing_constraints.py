import re
from collections import defaultdict
from pprint import pprint
from Declare4Py.ProcessMiningTasks.Discovery.DeclareMiner import DeclareMiner
from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from numpy import delete
import networkx as nx
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES
import sbmn_model_functions
from sbmn_model_functions import generating_model
import comparing_constraints_functions
from comparing_constraints_functions import same_relations, same_depending_relations, same_dependent_gateway_relation_end_point, strongest_mutual_dependency, verifying_another_dependency_existence, strongest_dependency
import validating_functions
from validating_functions import validating_constraints_start_end, validating_negative_constraints, validating_independence_constraints, validating_parallel_constraints, validating_response_constraints, validating_xor_existence_interpretation, validating_loop_in_constraint, validating_mutual_dependencies_existence, validating_circunstancial_dependencies, validating_parallelism_chain_existence, validating_parallelism_existence
import activities_functions
from activities_functions import depending_relations_list
import initialize_functions
from initialize_functions import initialize_activities

def reinterpreting_less_precise_constraints_pair(constraints_list, first_constraints, matrix, activity1, activity2):
    templates = constraints_list.get((activity1, activity2), [])
    first_templates = first_constraints.get((activity1, activity2), [])

    print("First templates:", first_templates)
    print("Current templates:", templates)
    
    count_dep_first = 0
    count_uni_first = 0
    count_xor_first = 0
    count_choice_first = 0
    count_indep_first = 0
    count_negation_first = 0
    count_indep_negation_first = 0
    for temp in first_templates:
        if temp in tuple(RESPONSE_TEMPLATES):
            count_dep_first += 1
        elif temp in tuple(NOT_AVAIABLE_FREE_SORTING):
            count_indep_negation_first += 1
        elif temp in tuple(PARALLEL_TEMPLATES):
            count_uni_first += 1
        elif temp in tuple(GATEWAY_TEMPLATES) or temp in tuple(EXCLUSIVE_GATEWAY_TEMPLATES):
            count_choice_first += 1
        elif temp in tuple(NOT_COEXISTENCE_TEMPLATES):
            count_xor_first += 1
        elif temp in tuple(INDEPENDENCE_TEMPLATES):
            count_indep_first += 1
        elif temp in tuple(NEGATION_TEMPLATES):
            count_negation_first += 1
    
    count_dep = 0
    count_uni = 0
    count_xor = 0
    count_choice = 0
    count_indep = 0
    count_negation = 0
    count_indep_negation = 0
    for temp in templates:
        if temp in tuple(ONLY_RESPONSE_TEMPLATES):
            count_dep += 1
        elif temp in tuple(NOT_AVAIABLE_FREE_SORTING):
            count_indep_negation += 1
        elif temp in tuple(PARALLEL_TEMPLATES):
            count_uni += 1
        elif temp in tuple(GATEWAY_TEMPLATES) or temp in tuple(EXCLUSIVE_GATEWAY_TEMPLATES):
            count_choice += 1
        elif temp in tuple(NOT_COEXISTENCE_TEMPLATES):
            count_xor += 1
        elif temp in tuple(INDEPENDENCE_TEMPLATES):
            count_indep += 1
        elif temp in tuple(NEGATION_TEMPLATES):
            count_negation += 1

    dep_factor = 1 if count_dep > (count_uni + count_xor + count_choice) and count_dep > (count_indep + count_negation) else 0
    # depc_factor = 1 if count_choice > 0 and count_indep > 0 and count_xor > 0 and count_indep_negation > 0 and count_dep == 0 and count_uni == 0 and count_negation == 0 else 0
    depc_factor = 1 if count_choice > 1 and count_indep > 0 and count_xor == 0 and count_dep == 0 and count_uni == 0 and count_negation == 0 else 0
    uni_factor = 1 if (count_uni + count_choice + count_indep) > (count_dep + count_xor + count_negation) and (count_choice + count_uni > 0)  and count_uni > 0 and count_choice > 0 and count_indep_negation == 0 else 0
    xor_factor = 1 if (count_xor + count_negation) > (count_dep + count_uni + count_indep) and count_xor > 0 else 0

    if dep_factor > 0 and not verifying_another_dependency_existence(matrix, activity1, activity2):
        print("Interpreted as DEP between", activity1, "and", activity2)
        return 'DEP'
    if depc_factor > 0 and count_negation_first < count_choice_first:
        # if count_choice_first > 0 and count_negation_first > 0:
        #     print("Interpreted as XOR between", activity1, "and", activity2)
        #     return 'XOR'
        # else:
        if not verifying_another_dependency_existence(matrix, activity1, activity2):
            print("Interpreted as DEPC between", activity1, "and", activity2)
            return 'DEPC'
        elif strongest_dependency(matrix, activity1, activity2) == True:
            print("Interpreted as DEP between", activity1, "and", activity2, "due to strongest dependency")
            return 'DEPC'
        else:
            return None
    if uni_factor > 0:
        if same_depending_relations(constraints_list, matrix, activity1, activity2) and same_dependent_gateway_relation_end_point(constraints_list, matrix, activity1, activity2) and count_indep_negation_first == 0:
            print("Interpreted as UNI between", activity1, "and", activity2)
            return 'UNI'
        else:
            print("Interpreted as DEP between", activity1, "and", activity2, "due to non union relations")
            return 'DEP'
    if xor_factor > 0 and count_dep_first == 0:
        print("Interpreted as XOR between", activity1, "and", activity2)
        return 'XOR'
    return None

def reinterpreting_less_precise_constraints(step, constraints_list, first_constraints, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print(f"\nReinterpreting less precise constraints between '{act1}' and '{act2}': {templates}")
        interpreted_less_precise_pair = reinterpreting_less_precise_constraints_pair(constraints_list, first_constraints, matrix, act1, act2)

        print("Setting less precise interpretation comparing the results in the matrix.")
        if matrix[act1][act2] == '0' and interpreted_less_precise_pair is not None:
            matrix[act1][act2] = interpreted_less_precise_pair

        # if xor_factor > 0:
        #     inverted_pair = interpreting_less_precise_constraints_pair(constraints_list, matrix, act2, act1)
        #     if inverted_pair == 'XOR':
        #         matrix[act1][act2] = 'XOR'
    constraints_list, matrix = validating_mutual_dependencies_existence(constraints_list, matrix)
    constraints_list, matrix = validating_loop_in_constraint(constraints_list, matrix, activities)
    # constraints_list, matrix = verifying_self_loops(constraints_list, matrix, activities)
    constraints_list, matrix = validating_parallelism_existence(constraints_list, matrix, activities)
    matrix = validating_xor_existence_interpretation(constraints_list, matrix, activities)
    constraints_list, matrix = validating_circunstancial_dependencies(constraints_list, matrix)

    return matrix

def interpreting_less_precise_constraints_pair(constraints_list, matrix, activity1, activity2):
    templates = constraints_list.get((activity1, activity2), [])
    count_dep = 0
    count_uni = 0
    count_xor = 0
    count_choice = 0
    count_indep = 0
    count_negation = 0
    count_indep_negation = 0
    for temp in templates:
        if temp in tuple(ONLY_RESPONSE_TEMPLATES):
            count_dep += 1
        elif temp in tuple(NOT_AVAIABLE_FREE_SORTING):
            count_indep_negation += 1
        elif temp in tuple(PARALLEL_TEMPLATES):
            count_uni += 1
        elif temp in tuple(GATEWAY_TEMPLATES) or temp in tuple(EXCLUSIVE_GATEWAY_TEMPLATES):
            count_choice += 1
        elif temp in tuple(NOT_COEXISTENCE_TEMPLATES):
            count_xor += 1
        elif temp in tuple(INDEPENDENCE_TEMPLATES):
            count_indep += 1
        elif temp in tuple(NEGATION_TEMPLATES):
            count_negation += 1

    dep_factor = 1 if count_dep > (count_uni + count_xor + count_choice) and count_dep > (count_indep + count_negation) else 0
    depc_factor = 1 if count_choice > 0 and count_indep > 0 and count_xor > 0 and count_indep_negation > 0 and count_dep == 0 and count_uni == 0 and count_negation == 0 else 0
    uni_factor = 1 if (count_uni + count_choice + count_indep) > (count_dep + count_xor + count_negation) and (count_choice + count_uni > 0)  and count_uni > 0 and count_choice > 0 else 0
    xor_factor = 1 if (count_xor + count_negation) > (count_dep + count_uni + count_indep) and count_xor > 0 else 0

    if dep_factor > 0:
        print("Interpreted as DEP between", activity1, "and", activity2)
        return 'DEP'
    if depc_factor > 0:
        print("Interpreted as DEPC between", activity1, "and", activity2)
        return 'DEPC'
    if uni_factor > 0:
        if same_depending_relations(constraints_list, matrix, activity1, activity2) and same_dependent_gateway_relation_end_point(constraints_list, matrix, activity1, activity2):
            print("Interpreted as UNI between", activity1, "and", activity2)
            return 'UNI'
        else:
            print("Interpreted as DEP between", activity1, "and", activity2, "due to non parallelism relations")
            return 'DEP'
    if xor_factor > 0:
        print("Interpreted as XOR between", activity1, "and", activity2)
        return 'XOR'
    return None


def interpreting_less_precise_constraints(step, constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print(f"\nInterpreting less precise constraints between '{act1}' and '{act2}': {templates}")
        interpreted_less_precise_pair = interpreting_less_precise_constraints_pair(constraints_list, matrix, act1, act2)

        if step == 1:
            if interpreted_less_precise_pair == 'DEP':
                matrix[act1][act2] = 'DEP'
            if interpreted_less_precise_pair == 'DEPC':
                inverted_pair = interpreting_constraints_pair(constraints_list, matrix, act2, act1)
                if inverted_pair == 'XOR':
                    matrix[act1][act2] = 'DEPC'
            if interpreted_less_precise_pair == 'UNI':
                if same_depending_relations(constraints_list, matrix, act1, act2) and same_dependent_gateway_relation_end_point(constraints_list, matrix, act1, act2):
                    matrix[act1][act2] = 'UNI'
                else:
                    matrix[act1][act2] = 'DEP'
        elif step == 2:
            print("Setting less precise interpretation comparing the results in the matrix.")
            if matrix[act1][act2] == '0' and interpreted_less_precise_pair is not None:
                matrix[act1][act2] = interpreted_less_precise_pair

        print("Interpreted less precise pair:", interpreted_less_precise_pair)
        print("Current matrix value:", matrix[act1][act2])


        # if xor_factor > 0:
        #     inverted_pair = interpreting_less_precise_constraints_pair(constraints_list, matrix, act2, act1)
        #     if inverted_pair == 'XOR':
        #         matrix[act1][act2] = 'XOR'
    # constraints_list, matrix = validating_mutual_dependencies_existence(constraints_list, matrix)
    # constraints_list, matrix = validating_loop_in_constraint(constraints_list, matrix, activities)
    # constraints_list, matrix = verifying_self_loops(constraints_list, matrix, activities)
    # constraints_list, matrix = validating_parallelism_existence(constraints_list, matrix, activities)
    # matrix = validating_xor_existence_interpretation(constraints_list, matrix, activities)
    # constraints_list, matrix = validating_circunstancial_dependencies(constraints_list, matrix)

    return matrix

def interpreting_constraints_pair(constraints_list, matrix, activity1, activity2):
    templates = constraints_list.get((activity1, activity2), [])
    count_dep = 0
    count_almost_dep = 0
    count_uni = 0
    count_xor = 0
    count_choice = 0
    count_indep = 0
    count_negation = 0
    count_indep_negation = 0
    for temp in templates:
        if temp in tuple(IMMEDIATE_RESPONSE_TEMPLATES):
            count_dep += 1
        elif temp in tuple(ONLY_RESPONSE_TEMPLATES):
            count_almost_dep += 1
        elif temp in tuple(NOT_AVAIABLE_FREE_SORTING):
            count_indep_negation += 1
        elif temp in tuple(PARALLEL_TEMPLATES):
            count_uni += 1
        elif temp in tuple(GATEWAY_TEMPLATES) or temp in tuple(EXCLUSIVE_GATEWAY_TEMPLATES):
            count_choice += 1
        elif temp in tuple(NOT_COEXISTENCE_TEMPLATES):
            count_xor += 1
        elif temp in tuple(INDEPENDENCE_TEMPLATES):
            count_indep += 1
        elif temp in tuple(NEGATION_TEMPLATES):
            count_negation += 1

    dep_factor = 1 if (count_dep + count_almost_dep) > (count_uni + count_xor + count_choice) and count_dep > (count_indep + count_negation) else 0
    depc_factor = 1 if count_choice > 0 and count_indep > 0 and count_xor > 0 and count_indep_negation > 0 and count_dep == 0 and count_almost_dep == 0 and count_uni == 0 and count_negation == 0 else 0
    uni_factor = 1 if (count_uni + count_choice + count_indep) > (count_dep + count_almost_dep + count_xor + count_negation) and count_uni > 0 and count_choice > 0 else 0
    xor_factor = 1 if (count_xor + count_negation) > (count_dep + count_almost_dep + count_uni + count_choice + count_indep) and count_xor > 0 else 0

    if dep_factor > 0:
        print("Interpreted as DEP between", activity1, "and", activity2)
        return 'DEP'
    if depc_factor > 0:
        print("Interpreted as DEPC between", activity1, "and", activity2)
        return 'DEPC'
    if uni_factor > 0:
        if same_depending_relations(constraints_list, matrix, activity1, activity2) and same_dependent_gateway_relation_end_point(constraints_list, matrix, activity1, activity2):
            print("Interpreted as UNI between", activity1, "and", activity2)
            return 'UNI'
        else:
            print("Interpreted as DEP between", activity1, "and", activity2, "due to non parallelism relations")
            return 'DEP'
    if xor_factor > 0:
        print("Interpreted as XOR between", activity1, "and", activity2)
        return 'XOR'
    return None


def interpreting_constraints(step, constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print(f"\nInterpreting constraints between '{act1}' and '{act2}': {templates}")

        interpreted_pair = interpreting_constraints_pair(constraints_list, matrix, act1, act2)
        if interpreted_pair == 'DEP':
            matrix[act1][act2] = 'DEP'
        if interpreted_pair == 'DEPC':
            inverted_pair = interpreting_constraints_pair(constraints_list, matrix, act2, act1)
            if inverted_pair == 'XOR':
                matrix[act1][act2] = 'DEPC'
        if interpreted_pair == 'UNI':
            if same_depending_relations(constraints_list, matrix, act1, act2) and same_dependent_gateway_relation_end_point(constraints_list, matrix, act1, act2):
                matrix[act1][act2] = 'UNI'
            else:
                matrix[act1][act2] = 'DEP'
        # if xor_factor > 0:
        #     if interpreting_constraints_pair(constraints_list, matrix, act2, act1) == 'XOR':
        #         matrix[act1][act2] = 'XOR'
    # constraints_list, matrix = validating_mutual_dependencies_existence(constraints_list, matrix)
    # constraints_list, matrix = validating_loop_in_constraint(constraints_list, matrix, activities)
    # constraints_list, matrix = verifying_self_loops(constraints_list, matrix, activities)
    # constraints_list, matrix = validating_parallelism_existence(constraints_list, matrix, activities)
    # constraints_list, matrix = validating_parallelism_chain_existence(constraints_list, matrix, activities)
    # matrix = validating_xor_existence_interpretation(constraints_list, matrix, activities)
    # constraints_list, matrix = validating_circunstancial_dependencies(constraints_list, matrix)

    count_total_pairs = 0
    count_no_relations = 0
    for act1 in matrix.keys():
        for act2 in matrix[act1].keys():
            count_total_pairs += 1
            if matrix[act1][act2] == '0':
                count_no_relations += 1
    if count_no_relations / count_total_pairs > 0.8:
        print("High number of no relations found, re-interpreting constraints with less precision")
        matrix = interpreting_less_precise_constraints(1, constraints_list, matrix, activities)

    return matrix

def process_constraints(step, constraints, matrix, activities):
    constraints_list = {}
    for cnst in constraints:
        if not cnst.startswith(tuple(ACTIVITIES_TEMPLATES)):
            pattern = r"^'?([^[]+)\[([^,]+)\s*,\s*([^\]]+)\]\s*\|\s*\|?'?$"
            m = re.match(pattern, cnst.strip())

            if not m:
                print("Constraint não reconhecida:", cnst)
                continue

            template = m.group(1).strip()
            activity1 = m.group(2).strip()
            activity2 = m.group(3).strip()
            key = (activity1, activity2)
            if key not in constraints_list:
                constraints_list[key] = [template]
            else:
                constraints_list[key].append(template)
    
    start = [act for act in matrix['BEGIN'] if int(matrix['BEGIN'][act]) > 0]
    end = [act for act in matrix['END'] if int(matrix['END'][act]) > 0]
    pre_processed_constraints_list = validating_constraints_start_end(constraints_list, start, end)

    for (act1, act2), templates in pre_processed_constraints_list.items():
        print(f"\n1 - Constraints entre '{act1}' e '{act2}': {templates}")

    processed_constraints_against_negative = validating_negative_constraints(pre_processed_constraints_list)

    for (act1, act2), templates in processed_constraints_against_negative.items():
        print(f"\n2 - Constraints entre '{act1}' e '{act2}': {templates}")

    processed_constraints_against_independence = validating_independence_constraints(processed_constraints_against_negative)
    for (act1, act2), templates in processed_constraints_against_independence.items():
        print(f"\n3 - Constraints entre '{act1}' e '{act2}': {templates}")
    
    processed_constraints_against_parallel = validating_parallel_constraints(processed_constraints_against_independence)
    for (act1, act2), templates in processed_constraints_against_parallel.items():
        print(f"\n4 - Constraints entre '{act1}' e '{act2}': {templates}")

    processed_constraints_against_response = validating_response_constraints(processed_constraints_against_parallel)
    for (act1, act2), templates in processed_constraints_against_response.items():
        print(f"\n5 - Constraints entre '{act1}' e '{act2}': {templates}")

    matrix = interpreting_constraints(step, processed_constraints_against_response, matrix, activities)
    matrix = interpreting_less_precise_constraints(step, processed_constraints_against_response, matrix, activities)
    
    sbmn = generating_model(matrix)

    return matrix, sbmn, processed_constraints_against_response

def reprocess_constraints(step, constraints, first_constraints, matrix, firts_activities):
    constraints_list = {}
    activities = initialize_activities(constraints)

    for act, item in activities.items():
        if matrix['BEGIN'][act] == '0' or matrix['END'][act] == '0':
            for temp, card in item.items():
                if temp == 'Init':
                    matrix['BEGIN'][act] = card
                elif temp == 'End':
                    matrix['END'][act] = card

    for cnst in constraints:
        if not cnst.startswith(tuple(ACTIVITIES_TEMPLATES)):
            pattern = r"^'?([^[]+)\[([^,]+)\s*,\s*([^\]]+)\]\s*\|\s*\|?'?$"
            m = re.match(pattern, cnst.strip())

            if not m:
                print("Constraint não reconhecida:", cnst)
                continue

            template = m.group(1).strip()
            activity1 = m.group(2).strip()
            activity2 = m.group(3).strip()
            key = (activity1, activity2)
            if key not in constraints_list:
                constraints_list[key] = [template]
            else:
                constraints_list[key].append(template)
    
    start = [act for act in matrix['BEGIN'] if int(matrix['BEGIN'][act]) > 0]
    end = [act for act in matrix['END'] if int(matrix['END'][act]) > 0]
    pre_processed_constraints_list = validating_constraints_start_end(constraints_list, start, end)

    for (act1, act2), templates in pre_processed_constraints_list.items():
        print(f"\n1 - Constraints entre '{act1}' e '{act2}': {templates}")

    processed_constraints_against_negative = validating_negative_constraints(pre_processed_constraints_list)

    for (act1, act2), templates in processed_constraints_against_negative.items():
        print(f"\n2 - Constraints entre '{act1}' e '{act2}': {templates}")

    processed_constraints_against_independence = validating_independence_constraints(processed_constraints_against_negative)
    for (act1, act2), templates in processed_constraints_against_independence.items():
        print(f"\n3 - Constraints entre '{act1}' e '{act2}': {templates}")
    
    processed_constraints_against_parallel = validating_parallel_constraints(processed_constraints_against_independence)
    for (act1, act2), templates in processed_constraints_against_parallel.items():
        print(f"\n4 - Constraints entre '{act1}' e '{act2}': {templates}")

    processed_constraints_against_response = validating_response_constraints(processed_constraints_against_parallel)
    for (act1, act2), templates in processed_constraints_against_response.items():
        print(f"\n5 - Constraints entre '{act1}' e '{act2}': {templates}")

    print("6 - Comparing first layer and second layer constraints")
    touched_pairs = []
    for act1 in activities.keys():
        for act2 in activities.keys():
            if act1 != act2 and (act1, act2) not in touched_pairs and (act2, act1) not in touched_pairs:
                touched_pairs.append((act1, act2))
                touched_pairs.append((act2, act1))
                print(f"\nComparing constraints between '{act1}' and '{act2}'")
                first_layer_templates = first_constraints.get((act1, act2), [])
                second_layer_templates = processed_constraints_against_response.get((act1, act2), [])
                print(f" First layer templates: {first_layer_templates}")
                print(f" Second layer templates: {second_layer_templates}")
                print(f"\nComparing constraints between '{act2}' and '{act1}'")
                first_inverted_templates = first_constraints.get((act2, act1), [])
                second_inverted_templates = processed_constraints_against_response.get((act2, act1), [])
                print(f" First layer inverted templates: {first_inverted_templates}")
                print(f" Second layer inverted templates: {second_inverted_templates}")
        

    matrix = reinterpreting_less_precise_constraints(step, processed_constraints_against_response, first_constraints, matrix, activities)
    
    sbmn = generating_model(matrix)

    return matrix, sbmn
