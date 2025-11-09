import re
from collections import defaultdict
from pprint import pprint
from Declare4Py.ProcessMiningTasks.Discovery.DeclareMiner import DeclareMiner
from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.DeclareModel import DeclareModel
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES
import printing_functions

def normalize_label(s):
    return ' '.join(s.split()).strip()

def extract_activities_from_constraint(c):
    # use parsed activities if present, otherwise parse raw between []
    acts = c.get('activities') or []
    if acts:
        return [normalize_label(a) for a in acts]
    raw = c.get('raw','')
    m = re.search(r'\[([^\]]+)\]', raw)
    if not m:
        return []
    parts = [normalize_label(p) for p in m.group(1).split(',')]
    return [p for p in parts if p]

def normalize_activity_name(s):
    return re.sub(r'\s+', ' ', s).strip()

def initialize_matrix(constraints_serialized):
    activities = {}
    matrix = defaultdict(lambda: defaultdict(int))

    for cnst in constraints_serialized:
        # print("\n=== Processando constraint ===")
        # pprint(cnst)

        if cnst.startswith(tuple(ACTIVITIES_TEMPLATES)):
            pattern = r"^'?([^[]+)\[([^\]]*)\]\s*\|\s*\|'?$"
            m = re.match(pattern, cnst.strip())

            if not m:
                print("Constraint não reconhecida:", cnst)
                continue

            template = m.group(1).rstrip('0123456789')
            cardinality = m.group(1)[len(template):]
            activity_name = m.group(2).strip()

            # print("Template extraido:", template)
            # print("Cardinalidade extraida:", cardinality)
            # print("Atividade extraida:", activity_name)

            if template == 'Init' or template == 'End':
                cardinality = '1'

            if template == 'Absence':
                cardinality = int(cardinality) - 1
                cardinality = str(cardinality)
            
            if activity_name in activities and template in activities[activity_name]:
                for temp in activities[activity_name]:
                    if temp == template and cardinality > activities[activity_name][temp]:
                        activities[activity_name][temp] = cardinality
            elif activity_name in activities and template not in activities[activity_name]:
                activities[activity_name][template] = cardinality
            elif activity_name not in activities:
                activities[activity_name] = {template: cardinality}
        else:
            break

    # print("\n=== Atividades extraídas com cardinalidade e template ===")
    # for act, item in activities.items():
    #     print(f"Atividade: {act}")
    #     for temp, card in item.items():
    #         print(f"Template: {temp}, Cardinalidade: {card}")

    for act, item in activities.items():
        for temp, card in item.items():
            if temp == 'Absence' and card == '1':
                # print(f"Removendo atividade {act} com cardinalidade 1 no template Absence - Nunca pode ocorrer")
                del activities[act]
                continue

    # print("\n=== Atividades que podem ocorrer com cardinalidade e template ===")
    # for act, item in activities.items():
    #     # print(f"Atividade: {act}")
    #     for temp, card in item.items():
    #         print(f"Template: {temp}, Cardinalidade: {card}")

    for act, item in activities.items():
        matrix['BEGIN'][act] = '0'
        matrix['END'][act] = '0'
        for act2 in activities.keys():
            matrix[act][act2] = '0'
        for temp, card in item.items():
            if temp == 'Init':
                matrix['BEGIN'][act] = card
            elif temp == 'End':
                matrix['END'][act] = card
    return matrix, activities
