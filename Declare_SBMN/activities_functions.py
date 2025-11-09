<<<<<<< HEAD
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES

def depending_relations_list (constraints_list, matrix, activity):
    activity_depending_relations = []

    for (act1, act2), templates in constraints_list.items():
        if (act1 != activity) and (act2 == activity):
            for temp in templates:
                if temp in sorted(tuple(templates_groups.IMMEDIATE_RESPONSE_TEMPLATES)) and act1 not in activity_depending_relations:
                    activity_depending_relations.append(act1)
    return activity_depending_relations
=======
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES

def depending_relations_list (constraints_list, matrix, activity):
    activity_depending_relations = []

    for (act1, act2), templates in constraints_list.items():
        if (act1 != activity) and (act2 == activity):
            for temp in templates:
                if temp in sorted(tuple(templates_groups.IMMEDIATE_RESPONSE_TEMPLATES)) and act1 not in activity_depending_relations:
                    activity_depending_relations.append(act1)
    return activity_depending_relations
>>>>>>> 616cea218b0ecea37f4460362e93cb29a982065b
