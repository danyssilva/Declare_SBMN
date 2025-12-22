import re
import json
from collections import defaultdict
from pprint import pprint
from Declare4Py.ProcessMiningTasks.Discovery.DeclareMiner import DeclareMiner
from Declare4Py.D4PyEventLog import D4PyEventLog
from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from numpy import delete
import networkx as nx
from confirmation_functions import confirming_suspected_complex_relations_in_traces
import templates_groups
from templates_groups import ACTIVITIES_TEMPLATES, RESPONSE_TEMPLATES, IMMEDIATE_RESPONSE_TEMPLATES, ONLY_RESPONSE_TEMPLATES, NEGATION_TEMPLATES, IMMEDIATE_NEGATION_TEMPLATES, ONLY_NEGATION_TEMPLATES, NOT_AVAIABLE_FREE_SORTING, INDEPENDENCE_TEMPLATES, PARALLEL_TEMPLATES, GATEWAY_TEMPLATES, EXCLUSIVE_GATEWAY_TEMPLATES, NOT_COEXISTENCE_TEMPLATES
import printing_functions
from printing_functions import print_matrix
import processing_constraints
from processing_constraints import process_constraints, interpreting_constraints_pair, same_depending_relations, same_dependent_gateway_relation_end_point, reprocess_constraints, interpreting_less_precise_constraints
import initialize_functions
from initialize_functions import initialize_matrix, initialize_activities
from assertiontests_functions import SBMNValidator, Situation, Operator
from sbmn_model_functions import parse_sbmn_model



def generate_matrix_activities(constraints_serialized):
    matrix, activities = initialize_matrix(constraints_serialized)
    print("Initialized Activities:")
    for act, props in activities.items():
        print(f" - {act}: {props}")

    matrix, sbmn, firts_constraints = process_constraints(1, constraints_serialized, matrix, activities)
    
    return matrix, sbmn, activities, firts_constraints

def sbmn_mining(constraints_serialized, event_log: D4PyEventLog):
    matrix, sbmn, activities, firts_constraints = generate_matrix_activities(constraints_serialized)

    print("\n=== First Layer Matrix ===")
    print_matrix(matrix)

    print("\n=== First Layer Declarative Model Generated ===")
    for line in sbmn:
        print(line)

    # mining constraints - Second Layer
    discovery_2 = DeclareMiner(
        log=event_log,
        consider_vacuity=False,
        min_support=0.1,
        itemsets_support=0.00001,
        max_declare_cardinality=3)
    discovered_model_second_layer: DeclareModel = discovery_2.run()

    print("\n=== Constraints extraídas ===")
    pprint(discovered_model_second_layer.serialized_constraints)

    matrix_final, sbmn_final = reprocess_constraints(2, discovered_model_second_layer.serialized_constraints, firts_constraints, matrix, activities)

    print("\n=== Second Layer Matrix ===")
    print_matrix(matrix_final)

    print("\n=== Second Layer Declarative Model Generated ===")
    for line in sbmn_final:
        print(line)

    matrix_final, sbmn_final = confirming_suspected_complex_relations_in_traces(matrix_final, event_log)

    print("\n=== After confirmation Matrix ===")
    print_matrix(matrix_final)

    print("\n=== After confirmation Declarative Model Generated ===")
    for line in sbmn_final:
        print(line)


    return matrix_final, sbmn_final


if __name__ == "__main__":
    import sys
    # *Modo 1*: passar um arquivo de texto com uma constraint serializada por linha (ex: declare__debug_full.txt)
    # *Modo 2*: usar um script que carregue discovered_model.constraints / .serialized_constraints e grave em JSON / chame esta função.

    # caminho do seu log
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/JMP2/Teste/saida.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/ComputerRepair_1/RM_ComputerRepair_1.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/ComputerRepair_1/log_sintetico_multimodelo.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/ComputerRepair_2/RM_ComputerRepair_2.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/ComputerRepair_2/log_sintetico_multimodelo.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/permition_2/RM_permition_2proc.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS/E2_proc/RM_E2proc.xes"  # ajuste
    # log_path = r"C:/Users/danys/Downloads/INPUTS/INPUTS/FOLDERS4/ITIL/BPIC14-PreProcessed-Filtered.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/MINIMETAL/mini_metal_log.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/MINIMETAL/metalmec_log.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/SELECAO/log_inscricao.xes"  # ajuste
    log_path = r"C:/Users/danys/Downloads/INPUTS/INPUTS/SELECAO/log_inscricao_candidato.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXEMPLOS/example_1.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/FOLDERS4/ComputerRepair_1/log_sintetico_2_modelos.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXEMPLOS/log_exemplo_paralelismo.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXEMPLOS/log_exemplo_uniao.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXEMPLOS/log_exemplo_xor.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXEMPLOS/log_exemplo_uniao_xor_depc.xes"  # ajuste
    # log_path = r"F:/Danielle/Mestrado/Declare_SBMN/INPUTS/EXEMPLOS/log_exemplo_promiscuityviolation.xes"  # ajuste

    # carregar log
    event_log = D4PyEventLog(case_name="case:concept:name")
    event_log.parse_xes_log(log_path)

    # minerar constraints
    discovery_1 = DeclareMiner(
        log=event_log,
        consider_vacuity=False,
        min_support=0.6,
        itemsets_support=0.01,
        max_declare_cardinality=3)
    discovered_model_first_layer: DeclareModel = discovery_1.run()

    # print("Modelo:", discovered_model.constraints)

    
    print("\n=== Extracted Constraints ===")
    pprint(discovered_model_first_layer.serialized_constraints)
    pprint(discovered_model_first_layer.activities)
    pprint(discovered_model_first_layer.constraints)

     # mine SBMN model

    matrix, sbmn = sbmn_mining(discovered_model_first_layer.serialized_constraints, event_log)

    sbmn_model = parse_sbmn_model(sbmn)

    validator = SBMNValidator()
    result = validator.validate_model(sbmn_model)
    print("\n=== SBMN Model Validation Results ===")
    print(result)
    
    # result é um dicionário, não um objeto
    # if isinstance(result, dict):
    #     issues = result.get('issues', [])
    #     for issue in issues:
    #         print(f"- {issue}")
    # else:
    #     # Se for um objeto
    #     for issue in result.issues:
    #         print(f"- {issue}")

    # Generate JSON of SBMN model
    from sbmn_model_functions import generate_json_from_sbmn
    import os
    
    # Extrair nome base do arquivo de log
    log_name = os.path.basename(log_path).replace('.xes', '')
    output_json_path = f"OUTPUTS/sbmn_{log_name}.json"
    
    # Gerar o JSON
    json_model = generate_json_from_sbmn(matrix, {}, output_json_path)
    print(f"\n=== JSON Model Generated ===")
    print(f"Saved to: {output_json_path}")

