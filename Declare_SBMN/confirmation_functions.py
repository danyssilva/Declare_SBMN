from log_functions import extract_traces_from_log
from sbmn_model_functions import generating_model

def confirming_xor_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected XOR relations by analyzing the event log traces
    print("Confirming XOR suspected relations in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == 'XOR':
                        # Analyze traces to confirm XOR relation
                        for trace in traces:
                            print(f"  Checking trace: {trace}")
                            if act1 in trace and act2 in trace:
                                print(f"    Both activities {act1} and {act2} found in trace, removing XOR relation - bad inference.")
                                # Both activities appear in the same trace, remove XOR relation
                                matrix[act1][act2] = '0'
                                matrix[act2][act1] = '0'
                                break
                        if matrix[act2][act1] == 'XOR':
                            matrix[act2][act1] = '0'
    return matrix

def confirming_depc_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected Dependency relations by analyzing the event log traces
    print("Confirming DEPC suspected relations in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == 'DEP' or operator == 'DEPC':
                        # Analyze traces to confirm Dependency relation
                        found_act1_circunstancially = False
                        found_act1_dependency = False
                        count_act1_in_traces = 0
                        count_act1_not_in_traces = 0
                        for trace in traces:
                            print(f"  Checking trace: {trace}")
                            if act2 in trace and act1 not in trace:
                                found_act1_circunstancially = True
                                count_act1_not_in_traces += 1
                            if act1 in trace and act2 in trace:
                                found_act1_dependency = True
                                count_act1_in_traces += 1
                        print(f"    Activity {act1} not found in {count_act1_not_in_traces} traces, found with dependency in {count_act1_in_traces} traces.")
                        if found_act1_circunstancially and found_act1_dependency and operator == 'DEP':
                            print(f"    Activity {act1} found circunstancially in trace, removing DEP relation - bad inference - actually DEPC.")
                            matrix[act1][act2] = 'DEPC'
                        elif not (found_act1_circunstancially and found_act1_dependency) and operator == 'DEPC':
                            print(f"    Activity {act1} never found circunstancially in trace, removing DEPC relation - bad inference - actually DEP.")
                            matrix[act1][act2] = 'DEP'
    return matrix


def confirming_parallel_independence_suspected_relations_in_traces(matrix, traces):                        
    # To be implemented: Confirm suspected Parallel relations by analyzing the event log traces
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    operator = matrix[act1][act2]
                    if (operator == 'DEP' and matrix[act2][act1] == 'DEP') or (operator == 'DEPC' and matrix[act2][act1] == 'DEPC'):
                        # Analyze traces to confirm Parallel relation
                        found_act1 = 0
                        found_act2 = 0
                        first_order = False
                        second_order = False
                        for trace in traces:
                            if act1 in trace:
                                found_act1 = trace.index(act1)
                            if act2 in trace:
                                found_act2 = trace.index(act2)
                            if found_act1 < found_act2 and found_act1 != 0 and found_act2 != 0:
                                # Both activities appear in the same trace, confirm Parallel relation
                                first_order = True
                                break
                        found_act1 = 0
                        found_act2 = 0
                        for trace in traces:
                            if act1 in trace:
                                found_act1 = trace.index(act1)
                            if act2 in trace:
                                found_act2 = trace.index(act2)
                            if found_act1 > found_act2 and found_act1 != 0 and found_act2 != 0:
                                # Both activities appear in the same trace, confirm Parallel relation
                                second_order = True
                                break
                        if (first_order and second_order):
                        # Both orders found, confirm Parallel relation
                            matrix[act1][act2] = '0'
                            matrix[act2][act1] = '0'
    return matrix

def confirming_union_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected Union relations by analyzing the event log traces
    print("Confirming UNION suspected relations in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == 'UNI':
                        # Analyze traces to confirm Union relation
                        first_order = False
                        second_order = False
                        third_order = False
                        fourth_order = False
                        for trace in traces:
                            found_act1 = 0
                            found_act2 = 0
                            if act1 in trace:
                                found_act1 = trace.index(act1)
                            if act2 in trace:
                                found_act2 = trace.index(act2)
                            if found_act1 > found_act2 and found_act1 != 0 and found_act2 != 0:
                                # Both activities appear in the log, confirm Union relation
                                first_order = True
                            elif found_act1 < found_act2 and found_act1 != 0 and found_act2 != 0:
                                # Both activities appear in the log, confirm Union relation
                                second_order = True
                            elif found_act1 > 0 and found_act2 == 0:
                                third_order = True
                            elif found_act1 == 0 and found_act2 > 0:
                                fourth_order = True
                        print(f"    Orders found - first: {first_order}, second: {second_order}, third: {third_order}, fourth: {fourth_order}")
                        if not (first_order and second_order and third_order and fourth_order):
                            # All three conditions met, confirm Union relation
                            matrix[act1][act2] = '0'
                            matrix[act2][act1] = '0'
                        elif first_order and second_order and third_order and fourth_order:
                            if matrix[act2][act1] == 'UNI':
                                # Both directions are UNI, keep only one
                                matrix[act2][act1] = '0'
    return matrix

def confirming_jmp_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected JMP relations by analyzing the event log traces
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    operator = matrix[act1][act2]
                    if operator == 'JMP':
                        # Analyze traces to confirm JMP relation
                        found_jmp = False
                        for trace in traces:
                            act1_counter = trace.count(act1)
                            if act1_counter > 1:
                                act2_position = trace.index(act2) if act2 in trace else -1
                                if act2_position != -1:
                                    found_act1 = False
                                    found_act2 = False
                                    # Check if act1 is followed by act2
                                    for i in range(0, act2_position-1):
                                        if trace[i] == act1 and trace[i+1] == act2:
                                            found_act1 = True
                                    # Check if act2 is followed by act1
                                    for i in range(act2_position + 1, len(trace)):
                                        if trace[i] == act1:
                                            found_act2 = True
                                    if found_act1 and found_act2:
                                        # Both orders found, confirm JMP relation
                                        found_jmp = True
                                        break
                        if not found_jmp:
                            matrix[act1][act2] = '0'
    return matrix

def finding_self_loops_in_traces(matrix, traces):
    # To be implemented: Find self-loops by analyzing the event log traces
    for act in matrix.keys():
        if act not in ['BEGIN', 'END']:
            for trace in traces:
                act_counter = trace.count(act)
                if act_counter > 1:
                    for i in range(0, len(trace) - 1):
                        if trace[i] == act and trace[i + 1] == act:
                            # Self-loop detected
                            matrix[act][act] = 'JMP'
    return matrix

def confirming_suspected_complex_relations_in_traces(matrix, event_log):
    # To be implemented: Confirm suspected relations by analyzing the event log traces
    traces = extract_traces_from_log(event_log)
    print("Extracted Traces for Confirmation:")
    for t in traces:
        print(f" - {t}")
    matrix = confirming_xor_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_depc_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_parallel_independence_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_union_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_jmp_suspected_relations_in_traces(matrix, traces)
    matrix = finding_self_loops_in_traces(matrix, traces)

    sbmn = generating_model(matrix)
    
    return matrix, sbmn