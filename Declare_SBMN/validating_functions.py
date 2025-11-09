<<<<<<< HEAD
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES
import activities_functions
from activities_functions import depending_relations_list
import comparing_constraints_functions
from comparing_constraints_functions import same_relations, same_depending_relations, same_dependent_gateway_relation_end_point, strongest_mutual_dependency

def validating_constraints_start_end(constraints_list, start, end):
    for (act1, act2), templates in constraints_list.items():
        if act1 in end or act2 in start:
            for temp in templates:
                print("temp:", temp)
                if temp in RESPONSE_TEMPLATES:
                    print(f"Atention: Activity '{act1}' set as END or '{act2}' set as BEGIN, but has link constraint ({temp}) that will not be processed")
                    constraints_list[(act1, act2)].remove(temp)
                    continue
    return constraints_list

def validating_negative_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_neg = 0
        count_pos = 0
        # count_almost_pos = 0
        for temp in sorted(templates):
            # print(f"Analyzing constraint '{temp}' between '{act1}' and '{act2}'")
            if temp in sorted(tuple(NEGATION_TEMPLATES)):
                # print(f"Found Negative Constraint '{temp}' between '{act1}' and '{act2}'")
                count_neg += 1
            elif temp in sorted(tuple(RESPONSE_TEMPLATES)):
                # print(f"Found Positive Constraint '{temp}' between '{act1}' and '{act2}'")
                count_pos += 1
            # elif temp in tuple(ONLY_RESPONSE_TEMPLATES):
            #     # print(f"Found Positive Constraint '{temp}' between '{act1}' and '{act2}'")
            #     count_almost_pos += 1
        if count_neg > count_pos:
            # and count_neg > count_almost_pos:
            # print(f"Atention: Negative Constraints between '{act1}' and '{act2}' greater than positive ones, removing all others constraints between them")
            for temp in sorted(templates):
                # print(f"Testing constraint '{temp}' between '{act1}' and '{act2}'")
                if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                    print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                    constraints_list[(act1, act2)].remove(temp)
        elif count_neg == count_pos:
            print(f"Atention: Negative and Positive Constraints between '{act1}' and '{act2}' are equal, removing all")
            for temp in sorted(templates):
                if temp in sorted(tuple(RESPONSE_TEMPLATES)) or temp in sorted(tuple(NEGATION_TEMPLATES)):
                    print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                    constraints_list[(act1, act2)].remove(temp)
        else:
            # print(f"Atention: Positive Constraint between '{act1}' and '{act2}' greater than negative ones, removing all negative constraints between them")
            for temp in sorted(templates):
                if temp in sorted(tuple(NEGATION_TEMPLATES)):
                    print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                    constraints_list[(act1, act2)].remove(temp)
    return constraints_list

def validating_independence_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_ind = 0
        count_pos = 0
        for temp in templates:
            if temp in INDEPENDENCE_TEMPLATES:
                count_ind += 1
            elif temp in sorted(tuple(RESPONSE_TEMPLATES)):
                count_pos += 1
        print(f"Between '{act1}' and '{act2}': count_ind={count_ind}, count_pos={count_pos}")
        if count_ind  > count_pos:
           for temp in sorted(templates):
               if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                   constraints_list[(act1, act2)].remove(temp)

        if count_ind < count_pos:
            for temp in sorted(templates):
                if temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                    constraints_list[(act1, act2)].remove(temp)
    return constraints_list

def validating_parallel_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_par = 0
        count_ind = 0
        count_pos = 0
        count_choice = 0
        count_almost_pos = 0
        for temp in sorted(templates):
            if temp in sorted(tuple(PARALLEL_TEMPLATES)):
                # Considering the presence of Co-Existence constraint having a greater weight
                count_par += 2
            elif temp in sorted(tuple(GATEWAY_TEMPLATES)):
                count_choice += 1
            elif temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                count_ind += 1
            elif temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)):
                count_pos += 1
            elif temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                count_almost_pos += 1
        print(f"Between '{act1}' and '{act2}': count_par={count_par}, count_pos={count_pos}, count_almost_pos={count_almost_pos}")
        if count_par > (count_ind + count_choice) and count_almost_pos > count_pos:
           for temp in sorted(templates):
               if temp not in sorted(tuple(PARALLEL_TEMPLATES)) and temp not in sorted(tuple(GATEWAY_TEMPLATES)) and temp not in sorted(tuple(INDEPENDENCE_TEMPLATES)) and temp not in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                   print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                   constraints_list[(act1, act2)].remove(temp)
        elif count_par < (count_ind + count_choice) and count_pos > count_almost_pos:
            for temp in sorted(templates):
                if temp in sorted(tuple(PARALLEL_TEMPLATES)) or temp in sorted(tuple(GATEWAY_TEMPLATES)) or temp in sorted(tuple(INDEPENDENCE_TEMPLATES)) or temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                   print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                   constraints_list[(act1, act2)].remove(temp)
    return constraints_list

def validating_response_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_resp = 0
        count_gateway = 0
        for temp in templates:
            if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                count_resp += 1
            elif temp in sorted(tuple(GATEWAY_TEMPLATES)) or temp in sorted(tuple(EXCLUSIVE_GATEWAY_TEMPLATES)):
                count_gateway += 1
        if count_gateway  > count_resp:
           for temp in sorted(templates):
               if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                   constraints_list[(act1, act2)].remove(temp)
        # if count_gateway < count_resp:
        #     for temp in sorted(templates):
        #         if temp in sorted(tuple(GATEWAY_TEMPLATES)) or temp in sorted(tuple(EXCLUSIVE_GATEWAY_TEMPLATES)):
        #             constraints_list[(act1, act2)].remove(temp)

    return constraints_list

def validating_loop_in_constraint(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        count_jmp = 0
        count_neg = 0
        count_ind = 0
        count_choice = 0
        print(f"Analyzing loop possibility between '{act1}' and '{act2}'")
        for temp in templates:
            if temp in sorted(tuple(NEGATION_TEMPLATES)):
                count_neg += 1
            if temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                count_ind += 1
            if temp in sorted(tuple(GATEWAY_TEMPLATES)):
                count_choice += 1
        print(f"count_neg={count_neg}, count_ind={count_ind}, count_choice={count_choice} between '{act1}' and '{act2}'")
        if count_neg > 0 and count_ind > 0 and count_choice > 0:
            count_jmp = 1
        if count_jmp > 0:
            act2_ocurrence = int(activities[act2]['Existence']) if 'Existence' in activities[act2] else 0
            act2_max_ocurrence = int(activities[act2]['Absence']) if 'Absence' in activities[act2] else 0
            act2_exactly_ocurrence = int(activities[act2]['Exactly']) if 'Exactly' in activities[act2] else 0   
            print(f"act2_ocurrence={act2_ocurrence}, act2_max_ocurrence={act2_max_ocurrence}, act2_exactly_ocurrence={act2_exactly_ocurrence} for activity '{act2}'")
            if act2_ocurrence > 1 and act2_max_ocurrence > 1 and act2_exactly_ocurrence > 1:
                for (act3, act4), templates in constraints_list.items():
                    if act3 == act2 and act4 == act1:
                        for temp in sorted(templates):
                            if temp == "Alternate Response" and matrix[act3][act4] == "DEP" and count_jmp > 0:
                                print(f"Setting JMP between '{act1}' and '{act2}' due to loop possibility")
                                matrix[act1][act2] = "JMP"
                                break
                    continue
    return constraints_list, matrix

def verifying_self_loops(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        count_resp = 0
        count_neg = 0
        count_ind = 0
        count_choice = 0
        for temp in templates:
            if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                count_resp += 1
            if temp in sorted(tuple(NEGATION_TEMPLATES)):
                count_neg += 1
            if temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                count_ind += 1
            if temp in sorted(tuple(GATEWAY_TEMPLATES)):
                count_choice += 1
        if count_resp > 0 and count_neg > 0 and count_ind > 0 and count_choice > 0:
            act2_ocurrence = int(activities[act2]['Existence']) if 'Existence' in activities[act2] else 0
            act2_max_ocurrence = int(activities[act2]['Absence']) if 'Absence' in activities[act2] else 0
            act2_exactly_ocurrence = int(activities[act2]['Exactly']) if 'Exactly' in activities[act2] else 0
            if act2_ocurrence > 1 and act2_max_ocurrence > 1 and act2_exactly_ocurrence > 1:
                for temp in sorted(templates):
                    if temp == "Alternate Response" and matrix[act2][act1] == "DEP":
                        act2_temp = [templates for (act3, act4), templates in constraints_list.items() if act3 == act2 and act4 == act1]
                        if "Alternate Precedence" in act2_temp:
                            matrix[act2][act2] = "JMP"
                            break
    return constraints_list, matrix

def validating_xor_existence_interpretation(constraints_list, matrix, activities):
    for act, item in activities.items():
        if act not in ["BEGIN", "END"]:
            for col, item in activities.items():
                if col not in ["BEGIN", "END"] and act != col:
                    if (act, col) not in constraints_list and (col, act) not in constraints_list:
                        print("Validating XOR existence between", act, "and", col)
                        if same_depending_relations(constraints_list, matrix, act, col, "XOR"):
                            print("Found same relations for XOR between", act, "and", col)  
                            matrix[act][col] = "XOR"
                            # print("Matrix:", matrix)

    return matrix

def validating_parallelism_existence(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print("Validating parallelism existence between pair (", act1, ",", act2, ")")
        # if same_templates(constraints_list, act1, act2, templates):
        #     matrix[act1][act2] = "UNI"
        if matrix[act1][act2] == "DEP" and same_depending_relations(constraints_list, matrix, act1, act2, "UNI") and same_dependent_gateway_relation_end_point(constraints_list, matrix, act1, act2, "UNI"):
            print("Found parallelism between", act1, "and", act2)
            matrix[act1][act2] = "UNI"
        elif matrix[act1][act2] == '0' and same_depending_relations(constraints_list, matrix, act1, act2, "UNI") and same_dependent_gateway_relation_end_point(constraints_list, matrix, act1, act2, "UNI"):
            print("Found parallelism between", act1, "and", act2)
            matrix[act1][act2] = "UNI"
    return constraints_list, matrix

def validating_parallelism_chain_existence(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print("Validating parallelism chain existence between pair (", act1, ",", act2, ")")
        if matrix[act1][act2] == "DEP":
            count_immediate = 0
            count_only_response = 0
            print("Templates between", act1, "and", act2, ":", templates)
            for temp in sorted(tuple(templates)):
                if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)):
                    count_immediate += 1
                elif temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                    count_only_response += 1

            if count_immediate < count_only_response:
                print("Seeking parallelism chain validation between", act1, "and", act2, "due to higher only response constraints")
                activity2_depending_relations = depending_relations_list(constraints_list, matrix, act2)
                print("00 - Activity2 Depending Relations:", activity2_depending_relations)

                if act1 in sorted(tuple(activity2_depending_relations)):
                    activity2_depending_relations.remove(act1)
                    print(f"Removed {act1} from {act2} depending relations to avoid self-loop")

                depending_chain_count = 0
                uni_chain_count = 0
                for act in sorted(tuple(activity2_depending_relations)):
                    if matrix[act1][act] == "UNI" and matrix[act][act2] == "DEP":
                            uni_chain_count += 1
                    if matrix[act][act2] == "DEP" and matrix[act1][act] == "DEP":
                        depending_chain_count += 1
                
                if uni_chain_count > depending_chain_count:
                    print("Found parallelism chain between", act1, "and", act2, "because", act2, "depends on", act, "and", act1, "and", act, "are in parallel")
                    matrix[act1][act2] = "UNI"
                    matrix[act2][act1] = "UNI"

    return constraints_list, matrix

def validating_mutual_dependencies_existence(constraints_list, matrix):
    for (act1, act2), templates in constraints_list.items():
        print("0 - Validating mutual dependencies between pair (", act1, ",", act2, ")")
        count_activity1_power = 0
        count_activity2_power = 0
        if matrix[act1][act2] == "DEP" and matrix[act2][act1] == "DEP":
            activity1_depending_relations = depending_relations_list(constraints_list, matrix, act1)
            activity2_depending_relations = depending_relations_list(constraints_list, matrix, act2)

            print("00 - Activity1 Depending Relations before removal:", activity1_depending_relations)
            print("00 - Activity2 Depending Relations before removal:", activity2_depending_relations)

            for dep in activity1_depending_relations:
                if dep == act2:
                    activity1_depending_relations.remove(dep)

            for dep in activity2_depending_relations:
                if dep == act1:
                    activity2_depending_relations.remove(dep)

            print("01 - Activity1 Depending Relations after removal:", activity1_depending_relations)
            print("01 - Activity2 Depending Relations after removal:", activity2_depending_relations)

            if sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)):
                print("Found same mutual dependencies between", act1, "and", act2)
                for dep in activity1_depending_relations:
                    print("Testing dependency from", dep, "to", act1, "and", act2)
                    if strongest_mutual_dependency(constraints_list, act1, act2, dep) == act1:
                        count_activity1_power += 1
                    elif strongest_mutual_dependency(constraints_list, act1, act2, dep) == act2:
                        count_activity2_power += 1
                if count_activity1_power > count_activity2_power:
                    print("Activity1", act1, "has stronger mutual dependency than", act2)
                    matrix[act2][act1] = "0"
                    for (a, b), template in constraints_list.items():
                        if a == act2 and b == act1:
                            print(f"0001 - Constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print("RESPONSE_TEMPLATES:", RESPONSE_TEMPLATES)
                            print("template:", sorted(tuple(template)))
                            for t in sorted(tuple(template)):
                                print("Testing template:", t)
                                if t in sorted(tuple(RESPONSE_TEMPLATES)):
                                    print(f"Removing constraint '{t}' between '{act2}' and '{act1}' due to weaker dependency")
                                    constraints_list[(a, b)].remove(t)
                                    print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
                    
                elif count_activity2_power > count_activity1_power:
                    print("Activity2", act2, "has stronger mutual dependency than", act1)
                    matrix[act1][act2] = "0"
                    for (a, b), template in constraints_list.items():
                        if a == act1 and b == act2:
                            print(f"0002 - Constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print("RESPONSE_TEMPLATES:", RESPONSE_TEMPLATES)
                            print("template:", sorted(tuple(template)))
                            for t in sorted(tuple(template)):
                                print("Testing template:", t)
                                if t in sorted(tuple(RESPONSE_TEMPLATES)):
                                    print(f"Removing constraint '{t}' between '{act1}' and '{act2}' due to weaker dependency")
                                    constraints_list[(a, b)].remove(t)
                                    print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
    return constraints_list, matrix

def verifying_xor_existence(constraints_list, matrix, activity):
    print("Verifying XOR existence for activity", activity)
    print("Matrix keys:", matrix)
    for act1 in matrix.keys():
        print("Checking relation with activity:", act1)
        if act1 == activity:
            for act2 in matrix[act1]:
                if act2 != act1 and matrix[act1][act2] == "XOR":
                    return act2
    return None

def validating_circunstancial_dependencies(constraints_list, matrix):
    for (act1, act2), templates in constraints_list.items():
        print("Validating circunstancial dependencies between pair (", act1, ",", act2, ")")
        if matrix[act1][act2] == "DEP":
            xor_activity = verifying_xor_existence(constraints_list, matrix, act1)
            act2_dependencies_list = depending_relations_list(constraints_list, matrix, act2)
            print("Found XOR existence for", xor_activity, " listed as a depending relation of",  act1)
            if xor_activity is not None and xor_activity in sorted(tuple(act2_dependencies_list)):
                print("Actually this is a circunstancial dependency relation between", act1, "and", act2, "due to XOR dependency with", xor_activity)
                matrix[act1][act2] = "DEPC"
                print("Updated matrix:", matrix)

    return constraints_list, matrix
=======
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES
import activities_functions
from activities_functions import depending_relations_list
import comparing_constraints_functions
from comparing_constraints_functions import same_relations, same_depending_relations, same_dependent_gateway_relation_end_point, strongest_mutual_dependency

def validating_constraints_start_end(constraints_list, start, end):
    for (act1, act2), templates in constraints_list.items():
        if act1 in end or act2 in start:
            for temp in templates:
                print("temp:", temp)
                if temp in RESPONSE_TEMPLATES:
                    print(f"Atention: Activity '{act1}' set as END or '{act2}' set as BEGIN, but has link constraint ({temp}) that will not be processed")
                    constraints_list[(act1, act2)].remove(temp)
                    continue
    return constraints_list

def validating_negative_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_neg = 0
        count_pos = 0
        # count_almost_pos = 0
        for temp in sorted(templates):
            # print(f"Analyzing constraint '{temp}' between '{act1}' and '{act2}'")
            if temp in sorted(tuple(NEGATION_TEMPLATES)):
                # print(f"Found Negative Constraint '{temp}' between '{act1}' and '{act2}'")
                count_neg += 1
            elif temp in sorted(tuple(RESPONSE_TEMPLATES)):
                # print(f"Found Positive Constraint '{temp}' between '{act1}' and '{act2}'")
                count_pos += 1
            # elif temp in tuple(ONLY_RESPONSE_TEMPLATES):
            #     # print(f"Found Positive Constraint '{temp}' between '{act1}' and '{act2}'")
            #     count_almost_pos += 1
        if count_neg > count_pos:
            # and count_neg > count_almost_pos:
            # print(f"Atention: Negative Constraints between '{act1}' and '{act2}' greater than positive ones, removing all others constraints between them")
            for temp in sorted(templates):
                # print(f"Testing constraint '{temp}' between '{act1}' and '{act2}'")
                if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                    print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                    constraints_list[(act1, act2)].remove(temp)
        elif count_neg == count_pos:
            print(f"Atention: Negative and Positive Constraints between '{act1}' and '{act2}' are equal, removing all")
            for temp in sorted(templates):
                if temp in sorted(tuple(RESPONSE_TEMPLATES)) or temp in sorted(tuple(NEGATION_TEMPLATES)):
                    print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                    constraints_list[(act1, act2)].remove(temp)
        else:
            # print(f"Atention: Positive Constraint between '{act1}' and '{act2}' greater than negative ones, removing all negative constraints between them")
            for temp in sorted(templates):
                if temp in sorted(tuple(NEGATION_TEMPLATES)):
                    print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                    constraints_list[(act1, act2)].remove(temp)
    return constraints_list

def validating_independence_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_ind = 0
        count_pos = 0
        for temp in templates:
            if temp in INDEPENDENCE_TEMPLATES:
                count_ind += 1
            elif temp in sorted(tuple(RESPONSE_TEMPLATES)):
                count_pos += 1
        print(f"Between '{act1}' and '{act2}': count_ind={count_ind}, count_pos={count_pos}")
        if count_ind  > count_pos:
           for temp in sorted(templates):
               if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                   constraints_list[(act1, act2)].remove(temp)

        if count_ind < count_pos:
            for temp in sorted(templates):
                if temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                    constraints_list[(act1, act2)].remove(temp)
    return constraints_list

def validating_parallel_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_par = 0
        count_ind = 0
        count_pos = 0
        count_choice = 0
        count_almost_pos = 0
        for temp in sorted(templates):
            if temp in sorted(tuple(PARALLEL_TEMPLATES)):
                # Considering the presence of Co-Existence constraint having a greater weight
                count_par += 2
            elif temp in sorted(tuple(GATEWAY_TEMPLATES)):
                count_choice += 1
            elif temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                count_ind += 1
            elif temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)):
                count_pos += 1
            elif temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                count_almost_pos += 1
        print(f"Between '{act1}' and '{act2}': count_par={count_par}, count_pos={count_pos}, count_almost_pos={count_almost_pos}")
        if count_par > (count_ind + count_choice) and count_almost_pos > count_pos:
           for temp in sorted(templates):
               if temp not in sorted(tuple(PARALLEL_TEMPLATES)) and temp not in sorted(tuple(GATEWAY_TEMPLATES)) and temp not in sorted(tuple(INDEPENDENCE_TEMPLATES)) and temp not in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                   print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                   constraints_list[(act1, act2)].remove(temp)
        elif count_par < (count_ind + count_choice) and count_pos > count_almost_pos:
            for temp in sorted(templates):
                if temp in sorted(tuple(PARALLEL_TEMPLATES)) or temp in sorted(tuple(GATEWAY_TEMPLATES)) or temp in sorted(tuple(INDEPENDENCE_TEMPLATES)) or temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                   print(f"Removing constraint '{temp}' between '{act1}' and '{act2}'")
                   constraints_list[(act1, act2)].remove(temp)
    return constraints_list

def validating_response_constraints(constraints_list):
    for (act1, act2), templates in constraints_list.items():
        count_resp = 0
        count_gateway = 0
        for temp in templates:
            if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                count_resp += 1
            elif temp in sorted(tuple(GATEWAY_TEMPLATES)) or temp in sorted(tuple(EXCLUSIVE_GATEWAY_TEMPLATES)):
                count_gateway += 1
        if count_gateway  > count_resp:
           for temp in sorted(templates):
               if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                   constraints_list[(act1, act2)].remove(temp)
        # if count_gateway < count_resp:
        #     for temp in sorted(templates):
        #         if temp in sorted(tuple(GATEWAY_TEMPLATES)) or temp in sorted(tuple(EXCLUSIVE_GATEWAY_TEMPLATES)):
        #             constraints_list[(act1, act2)].remove(temp)

    return constraints_list

def validating_loop_in_constraint(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        count_jmp = 0
        count_neg = 0
        count_ind = 0
        count_choice = 0
        print(f"Analyzing loop possibility between '{act1}' and '{act2}'")
        for temp in templates:
            if temp in sorted(tuple(NEGATION_TEMPLATES)):
                count_neg += 1
            if temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                count_ind += 1
            if temp in sorted(tuple(GATEWAY_TEMPLATES)):
                count_choice += 1
        print(f"count_neg={count_neg}, count_ind={count_ind}, count_choice={count_choice} between '{act1}' and '{act2}'")
        if count_neg > 0 and count_ind > 0 and count_choice > 0:
            count_jmp = 1
        if count_jmp > 0:
            act2_ocurrence = int(activities[act2]['Existence']) if 'Existence' in activities[act2] else 0
            act2_max_ocurrence = int(activities[act2]['Absence']) if 'Absence' in activities[act2] else 0
            act2_exactly_ocurrence = int(activities[act2]['Exactly']) if 'Exactly' in activities[act2] else 0   
            print(f"act2_ocurrence={act2_ocurrence}, act2_max_ocurrence={act2_max_ocurrence}, act2_exactly_ocurrence={act2_exactly_ocurrence} for activity '{act2}'")
            if act2_ocurrence > 1 and act2_max_ocurrence > 1 and act2_exactly_ocurrence > 1:
                for (act3, act4), templates in constraints_list.items():
                    if act3 == act2 and act4 == act1:
                        for temp in sorted(templates):
                            if temp == "Alternate Response" and matrix[act3][act4] == "DEP" and count_jmp > 0:
                                print(f"Setting JMP between '{act1}' and '{act2}' due to loop possibility")
                                matrix[act1][act2] = "JMP"
                                break
                    continue
    return constraints_list, matrix

def verifying_self_loops(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        count_resp = 0
        count_neg = 0
        count_ind = 0
        count_choice = 0
        for temp in templates:
            if temp in sorted(tuple(RESPONSE_TEMPLATES)):
                count_resp += 1
            if temp in sorted(tuple(NEGATION_TEMPLATES)):
                count_neg += 1
            if temp in sorted(tuple(INDEPENDENCE_TEMPLATES)):
                count_ind += 1
            if temp in sorted(tuple(GATEWAY_TEMPLATES)):
                count_choice += 1
        if count_resp > 0 and count_neg > 0 and count_ind > 0 and count_choice > 0:
            act2_ocurrence = int(activities[act2]['Existence']) if 'Existence' in activities[act2] else 0
            act2_max_ocurrence = int(activities[act2]['Absence']) if 'Absence' in activities[act2] else 0
            act2_exactly_ocurrence = int(activities[act2]['Exactly']) if 'Exactly' in activities[act2] else 0
            if act2_ocurrence > 1 and act2_max_ocurrence > 1 and act2_exactly_ocurrence > 1:
                for temp in sorted(templates):
                    if temp == "Alternate Response" and matrix[act2][act1] == "DEP":
                        act2_temp = [templates for (act3, act4), templates in constraints_list.items() if act3 == act2 and act4 == act1]
                        if "Alternate Precedence" in act2_temp:
                            matrix[act2][act2] = "JMP"
                            break
    return constraints_list, matrix

def validating_xor_existence_interpretation(constraints_list, matrix, activities):
    for act, item in activities.items():
        if act not in ["BEGIN", "END"]:
            for col, item in activities.items():
                if col not in ["BEGIN", "END"] and act != col:
                    if (act, col) not in constraints_list and (col, act) not in constraints_list:
                        print("Validating XOR existence between", act, "and", col)
                        if same_depending_relations(constraints_list, matrix, act, col, "XOR"):
                            print("Found same relations for XOR between", act, "and", col)  
                            matrix[act][col] = "XOR"
                            # print("Matrix:", matrix)

    return matrix

def validating_parallelism_existence(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print("Validating parallelism existence between pair (", act1, ",", act2, ")")
        # if same_templates(constraints_list, act1, act2, templates):
        #     matrix[act1][act2] = "UNI"
        if matrix[act1][act2] == "DEP" and same_depending_relations(constraints_list, matrix, act1, act2, "UNI") and same_dependent_gateway_relation_end_point(constraints_list, matrix, act1, act2, "UNI"):
            print("Found parallelism between", act1, "and", act2)
            matrix[act1][act2] = "UNI"
        elif matrix[act1][act2] == '0' and same_depending_relations(constraints_list, matrix, act1, act2, "UNI") and same_dependent_gateway_relation_end_point(constraints_list, matrix, act1, act2, "UNI"):
            print("Found parallelism between", act1, "and", act2)
            matrix[act1][act2] = "UNI"
    return constraints_list, matrix

def validating_parallelism_chain_existence(constraints_list, matrix, activities):
    for (act1, act2), templates in constraints_list.items():
        print("Validating parallelism chain existence between pair (", act1, ",", act2, ")")
        if matrix[act1][act2] == "DEP":
            count_immediate = 0
            count_only_response = 0
            print("Templates between", act1, "and", act2, ":", templates)
            for temp in sorted(tuple(templates)):
                if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)):
                    count_immediate += 1
                elif temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)):
                    count_only_response += 1

            if count_immediate < count_only_response:
                print("Seeking parallelism chain validation between", act1, "and", act2, "due to higher only response constraints")
                activity2_depending_relations = depending_relations_list(constraints_list, matrix, act2)
                print("00 - Activity2 Depending Relations:", activity2_depending_relations)

                if act1 in sorted(tuple(activity2_depending_relations)):
                    activity2_depending_relations.remove(act1)
                    print(f"Removed {act1} from {act2} depending relations to avoid self-loop")

                depending_chain_count = 0
                uni_chain_count = 0
                for act in sorted(tuple(activity2_depending_relations)):
                    if matrix[act1][act] == "UNI" and matrix[act][act2] == "DEP":
                            uni_chain_count += 1
                    if matrix[act][act2] == "DEP" and matrix[act1][act] == "DEP":
                        depending_chain_count += 1
                
                if uni_chain_count > depending_chain_count:
                    print("Found parallelism chain between", act1, "and", act2, "because", act2, "depends on", act, "and", act1, "and", act, "are in parallel")
                    matrix[act1][act2] = "UNI"
                    matrix[act2][act1] = "UNI"

    return constraints_list, matrix

def validating_mutual_dependencies_existence(constraints_list, matrix):
    for (act1, act2), templates in constraints_list.items():
        print("0 - Validating mutual dependencies between pair (", act1, ",", act2, ")")
        count_activity1_power = 0
        count_activity2_power = 0
        if matrix[act1][act2] == "DEP" and matrix[act2][act1] == "DEP":
            activity1_depending_relations = depending_relations_list(constraints_list, matrix, act1)
            activity2_depending_relations = depending_relations_list(constraints_list, matrix, act2)

            print("00 - Activity1 Depending Relations before removal:", activity1_depending_relations)
            print("00 - Activity2 Depending Relations before removal:", activity2_depending_relations)

            for dep in activity1_depending_relations:
                if dep == act2:
                    activity1_depending_relations.remove(dep)

            for dep in activity2_depending_relations:
                if dep == act1:
                    activity2_depending_relations.remove(dep)

            print("01 - Activity1 Depending Relations after removal:", activity1_depending_relations)
            print("01 - Activity2 Depending Relations after removal:", activity2_depending_relations)

            if sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)):
                print("Found same mutual dependencies between", act1, "and", act2)
                for dep in activity1_depending_relations:
                    print("Testing dependency from", dep, "to", act1, "and", act2)
                    if strongest_mutual_dependency(constraints_list, act1, act2, dep) == act1:
                        count_activity1_power += 1
                    elif strongest_mutual_dependency(constraints_list, act1, act2, dep) == act2:
                        count_activity2_power += 1
                if count_activity1_power > count_activity2_power:
                    print("Activity1", act1, "has stronger mutual dependency than", act2)
                    matrix[act2][act1] = "0"
                    for (a, b), template in constraints_list.items():
                        if a == act2 and b == act1:
                            print(f"0001 - Constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print("RESPONSE_TEMPLATES:", RESPONSE_TEMPLATES)
                            print("template:", sorted(tuple(template)))
                            for t in sorted(tuple(template)):
                                print("Testing template:", t)
                                if t in sorted(tuple(RESPONSE_TEMPLATES)):
                                    print(f"Removing constraint '{t}' between '{act2}' and '{act1}' due to weaker dependency")
                                    constraints_list[(a, b)].remove(t)
                                    print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
                    
                elif count_activity2_power > count_activity1_power:
                    print("Activity2", act2, "has stronger mutual dependency than", act1)
                    matrix[act1][act2] = "0"
                    for (a, b), template in constraints_list.items():
                        if a == act1 and b == act2:
                            print(f"0002 - Constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print("RESPONSE_TEMPLATES:", RESPONSE_TEMPLATES)
                            print("template:", sorted(tuple(template)))
                            for t in sorted(tuple(template)):
                                print("Testing template:", t)
                                if t in sorted(tuple(RESPONSE_TEMPLATES)):
                                    print(f"Removing constraint '{t}' between '{act1}' and '{act2}' due to weaker dependency")
                                    constraints_list[(a, b)].remove(t)
                                    print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
                            print(f"Updated constraints_list ({a}, {b}):", constraints_list[(a, b)])
    return constraints_list, matrix

def verifying_xor_existence(constraints_list, matrix, activity):
    print("Verifying XOR existence for activity", activity)
    print("Matrix keys:", matrix)
    for act1 in matrix.keys():
        print("Checking relation with activity:", act1)
        if act1 == activity:
            for act2 in matrix[act1]:
                if act2 != act1 and matrix[act1][act2] == "XOR":
                    return act2
    return None

def validating_circunstancial_dependencies(constraints_list, matrix):
    for (act1, act2), templates in constraints_list.items():
        print("Validating circunstancial dependencies between pair (", act1, ",", act2, ")")
        if matrix[act1][act2] == "DEP":
            xor_activity = verifying_xor_existence(constraints_list, matrix, act1)
            act2_dependencies_list = depending_relations_list(constraints_list, matrix, act2)
            print("Found XOR existence for", xor_activity, " listed as a depending relation of",  act1)
            if xor_activity is not None and xor_activity in sorted(tuple(act2_dependencies_list)):
                print("Actually this is a circunstancial dependency relation between", act1, "and", act2, "due to XOR dependency with", xor_activity)
                matrix[act1][act2] = "DEPC"
                print("Updated matrix:", matrix)

    return constraints_list, matrix
>>>>>>> 616cea218b0ecea37f4460362e93cb29a982065b
