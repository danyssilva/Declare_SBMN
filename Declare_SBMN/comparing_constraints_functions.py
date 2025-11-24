import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES

def strongest_mutual_dependency(constraints_list, activity1, activity2, activity_tested):
    count_activity1_dep = 0
    count_activity2_dep = 0
    print("02 - Checking strongest mutual dependency between", activity1, "and", activity2, "for activity", activity_tested)
    for (act1, act2), templates in constraints_list.items():
        if act2 == activity1 and act1 == activity_tested:
            for temp in templates:
                if temp in {'Chain Response', 'Chain Precedence', 'Chain Succession', 'Alternate Precedence'}:
                    count_activity1_dep += 1
    for (act1, act2), templates in constraints_list.items():
        if act2 == activity2 and act1 == activity_tested:
            for temp in templates:
                if temp in {'Chain Response', 'Chain Precedence', 'Chain Succession', 'Alternate Precedence'}:
                    count_activity2_dep += 1
    print("03 - count_activity1_dep:", count_activity1_dep, "and count_activity2_dep:", count_activity2_dep)
    if count_activity1_dep > count_activity2_dep:
        return activity1
    elif count_activity2_dep > count_activity1_dep:
        return activity2
    return None


def same_relations(constraints_list, matrix, activity1, activity2):
    activity1_depending_relations = []
    activity2_depending_relations = []
    activity1_dependent_relations = []
    activity2_dependent_relations = []

    print("1 - Checking same relations between", activity1, "and", activity2)

    for (act1, act2), templates in constraints_list.items():
        if (act2 == activity1):
            # print("Analyzing depending relation for activity1:", act1, "->", act2, "Templates:", templates)
            count_imediate_response = sum(1 for temp in templates if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)))
            count_only_response = sum(1 for temp in templates if temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)))
            # print("Count Immediate Response:", count_imediate_response)
            # print("Count Only Response:", count_only_response)
            if count_imediate_response >= count_only_response and count_imediate_response > 0:
                activity1_depending_relations.append(act1)
                # print("Added depending relation for activity1:", act1, "->", act2)
    for (act1, act2), templates in constraints_list.items():
        if (act2 == activity2):
            # print("Analyzing depending relation for activity2:", act1, "->", act2, "Templates:", templates)
            count_imediate_response = sum(1 for temp in templates if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)))
            count_only_response = sum(1 for temp in templates if temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)))
            # print("Count Immediate Response:", count_imediate_response)
            # print("Count Only Response:", count_only_response)
            if count_imediate_response >= count_only_response and count_imediate_response > 0:
                activity2_depending_relations.append(act1)
                # print("Added depending relation for activity2:", act1, "->", act2)

    for (act1, act2), templates in constraints_list.items():
        if (act1 == activity1):
            # print("Analyzing dependent relation for activity1:", act1, "->", act2, "Templates:", templates)
            count_imediate_response = sum(1 for temp in templates if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)))
            count_only_response = sum(1 for temp in templates if temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)))
            # print("Count Immediate Response:", count_imediate_response)
            # print("Count Only Response:", count_only_response)
            if count_imediate_response >= count_only_response and count_imediate_response > 0:
                activity1_dependent_relations.append(act2)
                # print("Added dependent relation for activity1:", act1, "->", act2)
    for (act1, act2), templates in constraints_list.items():
        if (act1 == activity2):
            # print("Analyzing dependent relation for activity2:", act1, "->", act2, "Templates:", templates)
            count_imediate_response = sum(1 for temp in templates if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)))
            count_only_response = sum(1 for temp in templates if temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)))
            # print("Count Immediate Response:", count_imediate_response)
            # print("Count Only Response:", count_only_response)
            if count_imediate_response >= count_only_response and count_imediate_response > 0:
                activity2_dependent_relations.append(act2)
                # print("Added dependent relation for activity2:", act1, "->", act2)

    print("1 - Activity1 Depending Relations:", activity1_depending_relations)
    print("1 - Activity2 Depending Relations:", activity2_depending_relations)
    # print("Activity1 Dependent Relations:", activity1_dependent_relations)
    # print("Activity2 Dependent Relations:", activity2_dependent_relations)

    print("len(activity1_depending_relations):", len(activity1_depending_relations), "and len(activity1_dependent_relations):", len(activity1_dependent_relations), "and len(activity2_depending_relations):", len(activity2_depending_relations), "and len(activity2_dependent_relations):", len(activity2_dependent_relations))

    if activity1_depending_relations == activity2_depending_relations and activity1_dependent_relations == activity2_dependent_relations:
        print("True: Same relations found between", activity1, "and", activity2)
        return True

    return False


def same_depending_relations(constraints_list, matrix, activity1, activity2, relation_type):
    activity1_depending_relations = []
    activity2_depending_relations = []

    IMMEDIATE_RESPONSE_TEMPLATES = {"Chain Response", "Chain Precedence", "Chain Succession", "Alternate Precedence"}
    ONLY_RESPONSE_TEMPLATES = {"Response", "Precedence", "Succession", "Alternate Response"}
    print("3 - Checking same relations between", activity1, "and", activity2)

    for (act1, act2), templates in constraints_list.items():
        if (act2 == activity1):
            # print("Analyzing depending relation for activity1:", act1, "->", act2, "Templates:", templates)
            count_imediate_response = sum(1 for temp in templates if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)))
            count_only_response = sum(1 for temp in templates if temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)))
            # print("Count Immediate Response:", count_imediate_response)
            # print("Count Only Response:", count_only_response)
            if count_imediate_response >= count_only_response and count_imediate_response > 0:
                activity1_depending_relations.append(act1)
                # print("Added depending relation for activity1:", act1, "->", act2)
    for (act1, act2), templates in constraints_list.items():
        if (act2 == activity2):
            # print("Analyzing depending relation for activity2:", act1, "->", act2, "Templates:", templates)
            count_imediate_response = sum(1 for temp in templates if temp in sorted(tuple(IMMEDIATE_RESPONSE_TEMPLATES)))
            count_only_response = sum(1 for temp in templates if temp in sorted(tuple(ONLY_RESPONSE_TEMPLATES)))
            # print("Count Immediate Response:", count_imediate_response)
            # print("Count Only Response:", count_only_response)
            if count_imediate_response >= count_only_response and count_imediate_response > 0:
                activity2_depending_relations.append(act1)
                # print("Added depending relation for activity2:", act1, "->", act2)

    
    print("4 - Activity1 Depending Relations:", activity1_depending_relations)
    print("4 - Activity2 Depending Relations:", activity2_depending_relations)

    if relation_type == "UNI":
        activity1_dependency_activity2 = False
        activity2_dependency_activity1 = False

        for act in sorted(activity1_depending_relations):
            if act == activity2:
                activity1_depending_relations.remove(act)
                activity1_dependency_activity2 = True
        for act in sorted(activity2_depending_relations):
            if act == activity1:
                activity2_depending_relations.remove(act)
                activity2_dependency_activity1 = True

        print("5 - Activity1 Depending Relations:", activity1_depending_relations)
        print("5 - Activity2 Depending Relations:", activity2_depending_relations)
        print("6 - activity1_dependency_activity2:", activity1_dependency_activity2)
        print("6 - activity2_dependency_activity1:", activity2_dependency_activity1)
        print("7 - len(activity1_depending_relations):", len(activity1_depending_relations), "and len(activity2_depending_relations):", len(activity2_depending_relations))
        print("7 - matrix[activity1][activity2]:", matrix[activity1][activity2], "and matrix[activity2][activity1]:", matrix[activity2][activity1])

        if sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)) and (activity1_dependency_activity2 == True and activity2_dependency_activity1 == True):
            print("True: Same depending relations found between", activity1, "and", activity2)
            return True
        elif sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)) and (matrix[activity1][activity2] == "DEP" and matrix[activity2][activity1] == "DEP"):
            print("True: Same depending relations found between", activity1, "and", activity2)
            return True
        elif sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)) and (matrix[activity1][activity2] == "DEP" and matrix[activity2][activity1] == "UNI"):
            print("True: Same depending relations found between", activity1, "and", activity2)
            return True
        elif sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)) and (matrix[activity1][activity2] == "UNI" and matrix[activity2][activity1] == "DEP"):
            print("True: Same depending relations found between", activity1, "and", activity2)
            return True
    elif relation_type == "XOR":
        for act in sorted(activity1_depending_relations):
            if matrix[activity1][act] == "UNI":
                activity1_depending_relations.remove(act)
        for act in sorted(activity2_depending_relations):
            if matrix[activity2][act] == "UNI":
                activity2_depending_relations.remove(act)

        if sorted(tuple(activity1_depending_relations)) == sorted(tuple(activity2_depending_relations)):
            print("True: Same depending relations found between", activity1, "and", activity2)
            return True


    # if activity1_depending_relations == activity2_depending_relations:
    #     print("True: Same depending relations found between", activity1, "and", activity2)
    #     return True

    return False

def same_dependent_gateway_relation_end_point(constraints_list, matrix, activity1, activity2, relation_type):
    activity1_relations = []
    activity2_relations = []

    # Implementar  uma função que não compara só as mesmas relações de entrada e saída, mas as relações de saída da cadeia de atividades das duas atividades até sair do choice.
    # Verificar se as cadeias de atividades são iguais
    print("6 - Checking same dependent gateway relations between", activity1, "and", activity2)

    for (act1, act2), templates in constraints_list.items():
        if (act1 == activity1):
            activity1_relations.append(act2)
        if (act1 == activity2):
            activity2_relations.append(act2)

    print("7 - Activity1 Relations:", activity1_relations)
    print("7 - Activity2 Relations:", activity2_relations)

    if relation_type == "UNI":
        activity1_dependency_activity2 = False
        activity2_dependency_activity1 = False

        for act in sorted(activity1_relations):
            if act == activity2:
                activity1_relations.remove(act)
                activity1_dependency_activity2 = True
        for act in sorted(activity2_relations):
            if act == activity1:
                activity2_relations.remove(act)
                activity2_dependency_activity1 = True

        print("8 - Activity1 Relations:", activity1_relations)
        print("8 - Activity2 Relations:", activity2_relations)
        print("9 - activity1_dependency_activity2:", activity1_dependency_activity2)
        print("9 - activity2_dependency_activity1:", activity2_dependency_activity1)
        print("10 - len(activity1_relations):", len(activity1_relations), "and len(activity2_relations):", len(activity2_relations))

        if len(activity1_relations) > len(activity2_relations):
            if sorted(tuple(activity2_relations)) in sorted(tuple(activity1_relations)) and activity1_dependency_activity2 == True and activity2_dependency_activity1 == True:
                print("True: Same dependent relations found between", activity1, "and", activity2)
                return True
        elif len(activity2_relations) > len(activity1_relations):
            if sorted(tuple(activity1_relations)) in sorted(tuple(activity2_relations)) and activity1_dependency_activity2 == True and activity2_dependency_activity1 == True:
                print("True: Same dependent relations found between", activity1, "and", activity2)
                return True
        else:
            if sorted(tuple(activity1_relations)) == sorted(tuple(activity2_relations)) and activity1_dependency_activity2 == True and activity2_dependency_activity1 == True:
                print("True: Same dependent relations found between", activity1, "and", activity2)
                return True
    elif relation_type == "XOR":
        for act in sorted(activity1_relations):
            if matrix[activity1][act] == "UNI" or matrix[activity1][act] == 0:
                activity1_relations.remove(act)
        for act in sorted(activity2_relations):
            if matrix[activity2][act] == "UNI" or matrix[activity2][act] == 0:
                activity2_relations.remove(act)
        print("11 - Activity1 Relations:", activity1_relations)
        print("11 - Activity2 Relations:", activity2_relations)
        if len(activity1_relations) > len(activity2_relations):
            if sorted(tuple(activity2_relations)) in sorted(tuple(activity1_relations)):
                print("True: Same dependent relations found between", activity1, "and", activity2)
                return True
        elif len(activity2_relations) > len(activity1_relations):
            if sorted(tuple(activity1_relations)) in sorted(tuple(activity2_relations)):
                print("True: Same dependent relations found between", activity1, "and", activity2)
                return True
        else:
            if sorted(tuple(activity1_relations)) == sorted(tuple(activity2_relations)):
                print("True: Same dependent relations found between", activity1, "and", activity2)
                return True
    return False
