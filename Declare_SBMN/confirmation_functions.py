from log_functions import extract_traces_from_log
from sbmn_model_functions import generating_model

class HeuristicAccuracyTracker:
    """Rastreia taxa de acerto das heurísticas de confirmação."""
    
    def __init__(self):
        self.metrics = {
            'XOR': {'acertos': 0, 'erros': 0},
            'DEP': {'acertos': 0, 'erros': 0},
            'DEPC': {'acertos': 0, 'erros': 0},
            'UNI': {'acertos': 0, 'erros': 0},
            'JMP': {'acertos': 0, 'erros': 0},
        }
    
    def record(self, relation_type, acertou):
        """
        Registra acerto ou erro de uma heurística.
        
        Args:
            relation_type: Tipo de relação (XOR, DEP, DEPC, etc.)
            acertou: True se acertou, False se errou
        """
        if relation_type not in self.metrics:
            self.metrics[relation_type] = {'acertos': 0, 'erros': 0}
        
        if acertou:
            self.metrics[relation_type]['acertos'] += 1
        else:
            self.metrics[relation_type]['erros'] += 1
    
    def get_taxa_acerto(self, relation_type):
        """Retorna taxa de acerto para um tipo de relação."""
        if relation_type not in self.metrics:
            return 0
        
        m = self.metrics[relation_type]
        total = m['acertos'] + m['erros']
        
        if total == 0:
            return 0
        
        return (m['acertos'] / total) * 100
    
    def get_summary(self):
        """Retorna resumo de todas as métricas."""
        summary = {}
        for relation_type in sorted(self.metrics.keys()):
            m = self.metrics[relation_type]
            total = m['acertos'] + m['erros']
            
            if total > 0:
                taxa = (m['acertos'] / total) * 100
                summary[relation_type] = {
                    'acertos': m['acertos'],
                    'erros': m['erros'],
                    'total': total,
                    'taxa_acerto': taxa
                }
        
        return summary
    
    def print_report(self):
        """Imprime relatório simples de taxa de acerto."""
        print("\n" + "="*80)
        print("TAXA DE ACERTO DAS HEURÍSTICAS")
        print("="*80)
        
        summary = self.get_summary()
        
        if not summary:
            print("Nenhuma métrica registrada.")
            return
        
        for relation_type, metrics in summary.items():
            print(f"\n{relation_type}:")
            print(f"  Acertos: {metrics['acertos']}")
            print(f"  Erros: {metrics['erros']}")
            print(f"  Total: {metrics['total']}")
            print(f"  Taxa de Acerto: {metrics['taxa_acerto']:.1f}%")


# Instância global para rastreamento
accuracy_tracker = HeuristicAccuracyTracker()



def confirming_xor_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected XOR relations by analyzing the event log traces
    print("Confirming XOR suspected relations in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    # print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == 'XOR':
                        # Heurística previu XOR
                        acertou = True  # Assume acerto até encontrar prova do contrário
                        
                        # Analyze traces to confirm XOR relation
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            # print(f"  Checking trace: {trace}")
                            if act1 in trace and act2 in trace:
                                # print(f"    Both activities {act1} and {act2} found in trace, removing XOR relation - bad inference.")
                                # Both activities appear in the same trace, heurística ERROU
                                acertou = False
                                # Both activities appear in the same trace, remove XOR relation
                                matrix[act1][act2] = '0'
                                matrix[act2][act1] = '0'
                                break
                        
                        # Registrar se acertou ou errou
                        accuracy_tracker.record('XOR', acertou)
                        
                        if matrix[act2][act1] == 'XOR':
                            matrix[act2][act1] = '0'
    return matrix

def confirming_non_seen_xor_relations_in_traces(matrix, traces):
    # To be implemented: Confirm non-seen XOR relations by analyzing the event log traces
    print("Confirming non-seen XOR relations in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    # print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == '0':
                        # Heurística previu NADA
                        count_xor = 0               # Analyze traces to confirm non-seen XOR relation
                        count_not_xor = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            # print(f"  Checking trace: {trace}")
                            if act1 in trace and act2 not in trace:
                                count_xor += 1
                            if act1 in trace and act2 in trace:
                                count_not_xor += 1
                            if act1 not in trace and act2 in trace:
                                count_xor += 1
                        
                        if count_xor > 0 and count_not_xor == 0 and matrix[act2][act1] == '0':
                            other_xor_relations = True if 'XOR' in [matrix[a][act2] for a in matrix.keys() if a != act2 and a not in ['BEGIN', 'END']] else False
                            if not other_xor_relations:
                                # print(f"    Confirming XOR relation between {act1} and {act2} based on traces analysis.")
                                # Both activities not appear in the same trace, heurística ERROU
                                acertou = False
                                # Both activities not appear in the same trace, register non-seen XOR relation
                                matrix[act1][act2] = 'XOR'
                                # Registrar se acertou ou errou
                                accuracy_tracker.record('XOR', acertou)
                                break
                        
    return matrix

def checking_lost_strict_dependencys_in_traces(matrix, traces):
    # To be implemented: Check strict dependencies by analyzing the event log traces
    print("Checking lost strict dependencies in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END'] and act1 != act2:
                    operator = matrix[act1][act2]
                    if operator == '0' and matrix['END'][act1] == '0' and matrix['BEGIN'][act2] == '0':
                        # Heurística previu NADA
                        # acertou = True  # Assume acerto até encontrar prova do contrário
                        # print(f"Analyzing pair: ({act1}, {act2}) for lost strict dependency.")
                        found_strict = False
                        count_strict = 0
                        count_not_strict = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            # print(f"  Checking trace: {trace}")
                            if act2 in trace and act1 not in trace:
                                # print(f"  Activity {act2} found without {act1} in trace: {trace}")
                                count_not_strict += 1
                            if act1 in trace and act2 in trace:
                                # print(f"  Both activities {act1} and {act2} found in trace: {trace}")
                                act1_index = trace.index(act1)
                                act2_index = trace.index(act2)
                                # print(f"    Indices in trace - {act1}: {act1_index}, {act2}: {act2_index}")
                                if act1_index < act2_index and abs(act2_index - act1_index) == 1:
                                    # print(f"  Strict dependency found in trace: {trace}")
                                    # print(f"  Check if there are no other activities between act1 and act2")
                                    found_strict = True
                                    count_strict += 1
                                    # break
                                elif act1_index < act2_index and abs(act2_index - act1_index) > 1:
                                    count_not_strict += 1
                        # print(f"    Strict dependency counts - strict: {count_strict}, not strict: {count_not_strict}")
                        if found_strict and count_strict > count_not_strict:
                            other_dependencys = True if 'DEP' in [matrix[a][act2] for a in matrix.keys() if a != act2 and a not in ['BEGIN', 'END']] else False
                            if not other_dependencys:
                                # print(f"Restoring DEP relation between {act1} and {act2} due to strict dependency found in traces.")
                                matrix[act1][act2] = 'DEP'
                                acertou = False  # Assume acerto até encontrar prova do contrário
                                # Registrar se acertou ou errou
                                accuracy_tracker.record('DEP', acertou)

    return matrix

def confirming_depc_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected Dependency relations by analyzing the event log traces
    print("Confirming DEPC suspected relations in traces...")
    count_traces = len(traces)
    print("Totals traces to analyze for DEPC:", count_traces)
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    # print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == 'DEP' or operator == 'DEPC':
                        acertou = True
                        # Analyze traces to confirm Dependency relation
                        found_act1_circunstancially = False
                        found_act1_dependency = False
                        count_act1_in_traces = 0
                        count_act1_not_in_traces = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            # print(f"  Checking trace: {trace}")
                            if act2 in trace and act1 not in trace:
                                found_act1_circunstancially = True
                                count_act1_not_in_traces += 1

                            if act1 in trace and act2 in trace and trace.index(act1) < trace.index(act2):
                                # print(f"    Activity {act1} found before {act2} in trace.")
                                found_act1_dependency = True
                                count_act1_in_traces += 1

                        # print(f"    Activity {act1} not found in {count_act1_not_in_traces} traces, found with dependency in {count_act1_in_traces} traces.")
                        if found_act1_circunstancially and found_act1_dependency and count_act1_in_traces < count_act1_not_in_traces*0.9 and operator == 'DEP':
                            # print(f"    Activity {act1} not frequently found in trace, removing DEP relation.")
                            matrix[act1][act2] = 0
                            acertou = False
                        elif found_act1_circunstancially and found_act1_dependency and count_act1_not_in_traces > count_act1_in_traces*0.3 and count_act1_in_traces > count_act1_not_in_traces and operator == 'DEP':
                            # print(f"    Activity {act1} found circunstancially in trace, removing DEP relation - bad inference - actually DEPC.")
                            matrix[act1][act2] = 'DEPC'
                            acertou = False
                        elif not (found_act1_circunstancially) and found_act1_dependency and count_act1_in_traces > 0 and operator == 'DEPC':
                            # print(f"    Activity {act1} never found circunstancially in trace, removing DEPC relation - bad inference - actually DEP.")
                            matrix[act1][act2] = 'DEP'
                            acertou = False
                        elif found_act1_circunstancially < (found_act1_dependency*0.1) and operator == 'DEPC':
                            # print(f"    Activity {act1} never found circunstancially in trace, removing DEPC relation - bad inference - actually DEP.")
                            matrix[act1][act2] = 'DEP'
                            acertou = False
                        # Registrar se acertou ou errou
                        accuracy_tracker.record(operator, acertou)
    return matrix

def confirming_nearest_denpendencys_in_traces(matrix, traces):
    # To be implemented: Confirm nearest dependencies by analyzing the event log traces
    print("Confirming nearest dependencies in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    operator = matrix[act1][act2]
                    if operator == 'DEP':
                        acertou = True
                        # Analyze traces to confirm NEDEP relation
                        found_nearest = False
                        count_nearest = 0
                        count_not_nearest = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            if act1 in trace and act2 in trace:
                                act1_index = trace.index(act1)
                                act2_index = trace.index(act2)
                                if act2_index - act1_index == 1:
                                    found_nearest = True
                                    count_nearest += 1
                                    # break
                                if act2_index - act1_index > 1:
                                    # There are activities between act1 and act2, not nearest
                                    count_not_nearest += 1

                        if not found_nearest or count_nearest < count_not_nearest*0.2:
                            # print(f"Removing DEP relation between {act1} and {act2} due to lack of nearest dependency in traces.")
                            matrix[act1][act2] = '0'
                            acertou = False
                        # Registrar se acertou ou errou
                        accuracy_tracker.record(operator, acertou)
    return matrix

def confirming_nearest_circunstancial_denpendencys_in_traces(matrix, traces):
    # To be implemented: Confirm nearest dependencies by analyzing the event log traces
    print("Confirming nearest circunstancial dependencies in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    operator = matrix[act1][act2]
                    if operator == 'DEPC':
                        acertou = True
                        # Analyze traces to confirm NEDEP relation
                        found_nearest = False
                        count_nearest = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            if act1 in trace and act2 in trace:
                                act1_index = trace.index(act1)
                                act2_index = trace.index(act2)
                                if abs(act1_index - act2_index) == 1:
                                    found_nearest = True
                                    count_nearest += 1
                                    # break
                        if not found_nearest or count_nearest < len(traces)*0.1:
                            # print(f"Removing DEPC relation between {act1} and {act2} due to lack of nearest circunstancial dependency in traces.")
                            matrix[act1][act2] = '0'
                            acertou = False
                        # Registrar se acertou ou errou
                        accuracy_tracker.record(operator, acertou)

    return matrix


def confirming_parallel_independence_suspected_relations_in_traces(matrix, traces):                        
    # To be implemented: Confirm suspected Parallel relations by analyzing the event log traces
    print("Confirming PAR suspected relations in traces...")
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    operator = matrix[act1][act2]
                    if (operator == 'DEP' and matrix[act2][act1] == 'DEP') or (operator == 'DEPC' and matrix[act2][act1] == 'DEPC'):
                        acertou = True
                        # Analyze traces to confirm Parallel relation
                        found_act1 = 0
                        found_act2 = 0
                        first_order = False
                        second_order = False
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
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
                            trace = [activity.rstrip() for activity in trace]
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
                            # print(f"Confirming PAR relation between {act1} and {act2}.")
                            matrix[act1][act2] = '0'
                            matrix[act2][act1] = '0'
                            acertou = False
                        # Registrar se acertou ou errou
                        accuracy_tracker.record(operator, acertou)
    return matrix

def confirming_union_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected Union relations by analyzing the event log traces
    print("Confirming UNION suspected relations in traces...")
    count_traces = len(traces)
    # print("Totals traces to analyze for UNION:", count_traces)
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    # print(f"Analyzing pair: ({act1}, {act2}) with operator {matrix[act1][act2]}")
                    operator = matrix[act1][act2]
                    if operator == 'UNI':
                        acertou = True
                        # Analyze traces to confirm Union relation
                        first_order = False
                        second_order = False
                        third_order = False
                        fourth_order = False
                        count_firts_order = 0
                        count_second_order = 0
                        count_third_order = 0
                        count_fourth_order = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            found_act1 = 0
                            found_act2 = 0
                            if act1 in trace:
                                found_act1 = trace.index(act1)
                            if act2 in trace:
                                found_act2 = trace.index(act2)
                            if found_act1 > found_act2 and found_act1 != 0 and found_act2 != 0:
                                # Both activities appear in the log, confirm Union relation
                                first_order = True
                                count_firts_order += 1
                            elif found_act1 < found_act2 and found_act1 != 0 and found_act2 != 0:
                                # Both activities appear in the log, confirm Union relation
                                second_order = True
                                count_second_order += 1
                            elif found_act1 > 0 and found_act2 == 0:
                                third_order = True
                                count_third_order += 1
                            elif found_act1 == 0 and found_act2 > 0:
                                fourth_order = True
                                count_fourth_order += 1
                        is_union = (count_firts_order >= count_traces*0.25  and count_second_order >= count_traces*0.25 and count_third_order >= count_traces*0.25 and count_fourth_order >= count_traces*0.25)
                        # print(f"    Orders count - first: {count_firts_order}, second: {count_second_order}, third: {count_third_order}, fourth: {count_fourth_order}")
                        # print(f"    Orders found - first: {first_order}, second: {second_order}, third: {third_order}, fourth: {fourth_order}")
                        # print(f"    Is UNION confirmed? {is_union} for activities {act1} and {act2}.")
                        if not (first_order and second_order and third_order and fourth_order) or is_union == False:
                            # All three conditions met, confirm Union relation
                            # print(f"    Removing UNI relation between {act1} and {act2} due to lack of sufficient evidence in traces.")
                            matrix[act1][act2] = '0'
                            matrix[act2][act1] = '0'
                            acertou = False
                        elif first_order and second_order and third_order and fourth_order and is_union == True:
                            if matrix[act2][act1] == 'UNI':
                                # Both directions are UNI, keep only one
                                # print(f"    Removing duplicate UNI relation between {act2} and {act1}.")
                                matrix[act2][act1] = '0'
                        # Registrar se acertou ou errou
                        accuracy_tracker.record(operator, acertou)
                        
    return matrix

def confirming_jmp_suspected_relations_in_traces(matrix, traces):
    # To be implemented: Confirm suspected JMP relations by analyzing the event log traces
    print("Confirming JMP suspected relations in traces...")
    count_traces = len(traces)
    # print("Totals traces to analyze for JMP:", count_traces)
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            for act2 in matrix[act1].keys():
                if act2 not in ['BEGIN', 'END']:
                    operator = matrix[act1][act2]
                    if operator == 'JMP':
                        # print(f"Analyzing pair: ({act1}, {act2}) for JMP confirmation.")
                        # Analyze traces to confirm JMP relation
                        acertou = True
                        found_jmp = False
                        count_jmp = 0
                        for trace in traces:
                            trace = [activity.rstrip() for activity in trace]
                            act1_counter = trace.count(act1)
                            if act1_counter > 1:
                                act1_position = trace.index(act1) if act1 in trace else -1
                                # print(f"  Checking trace: {trace} with {act1} count: {act1_counter} and {act2} position: {act1_position}")
                                if act1_position != -1:
                                    found_act1 = False
                                    found_act2 = False
                                    # Check if act1 is followed by act2
                                    for i in range(act1_position+1, len(trace)-1):
                                        if trace[i] == act2 and trace[i+1] == act1:
                                            found_act1 = True
                                            # print(f"    Found {act2} followed by {act1} in trace: {trace}")
                                    # Check if act2 is followed by act1
                                    for i in range(0, act1_position):
                                        if trace[i] == act2:
                                            found_act2 = True
                                            # print(f"    Found {act2} followed by {act1} in trace: {trace}")
                                    if found_act1 and found_act2:
                                        # print(f"    Both orders found for {act1} and {act2} in trace: {trace}")
                                        # Both orders found, confirm JMP relation
                                        found_jmp = True
                                        count_jmp += 1
                                        # break
                        if not found_jmp or count_jmp < count_traces*0.1:
                            # print(f"Removing JMP relation between {act1} and {act2} due to lack of evidence in traces.")
                            matrix[act1][act2] = '0'
                            acertou = False
                        # Registrar se acertou ou errou
                        accuracy_tracker.record(operator, acertou)
    return matrix

def finding_self_loops_in_traces(matrix, traces):
    # To be implemented: Find self-loops by analyzing the event log traces
    print("Finding self-loops in traces...")
    count_traces = len(traces)
    # print("Totals traces to analyze for self-loops:", count_traces)
    for act in matrix.keys():
        if act not in ['BEGIN', 'END']:
            count_self_loops_in_traces = 0
            not_self_loop_counter = 0
            for trace in traces:
                trace = [activity.rstrip() for activity in trace]
                act_counter = trace.count(act)
                # print(f"Trace: {trace}")
                # print(f"Analyzing activity {act} in trace with count {act_counter}")
                if act_counter > 1:
                    k = trace.index(act)
                    # print(f"First occurrence of {act} at position {k}")
                    for i in range(k, len(trace) - 1):
                        if trace[i] == act and trace[i + 1] == act:
                            count_self_loops_in_traces += 1
                    if count_self_loops_in_traces != act_counter-1:
                        not_self_loop_counter += 1
                elif act_counter == 1:
                    not_self_loop_counter += 1 
            
            # print(f"Activity {act} - Self-loops found in traces: {count_self_loops_in_traces}, Not self-loop occurrences: {not_self_loop_counter}") 
            if count_self_loops_in_traces > not_self_loop_counter*0.1 and count_self_loops_in_traces > count_traces*0.1:
                # print(f"Self-loop detected for activity {act} in more traces where {act} appears.")
                # Self-loop detected
                matrix[act][act] = 'JMP'
                accuracy_tracker.record('JMP', False)
    return matrix

def confirming_suspected_complex_relations_in_traces(matrix, event_log):
    # To be implemented: Confirm suspected relations by analyzing the event log traces
    global accuracy_tracker
    accuracy_tracker = HeuristicAccuracyTracker()  # Reset para cada processamento
    
    traces = extract_traces_from_log(event_log)
    # print("Extracted Traces for Confirmation:")
    # for t in traces:
    #     print(f" - {t}")
    matrix = confirming_xor_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_non_seen_xor_relations_in_traces(matrix, traces)
    matrix = checking_lost_strict_dependencys_in_traces(matrix, traces)
    matrix = confirming_nearest_denpendencys_in_traces(matrix, traces)
    matrix = confirming_depc_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_nearest_circunstancial_denpendencys_in_traces(matrix, traces)
    matrix = confirming_parallel_independence_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_union_suspected_relations_in_traces(matrix, traces)
    matrix = confirming_jmp_suspected_relations_in_traces(matrix, traces)
    matrix = finding_self_loops_in_traces(matrix, traces)

    sbmn = generating_model(matrix)
    
    # Imprimir relatório de taxa de acerto
    # accuracy_tracker.print_report()
    
    # Retornar matriz, modelo SBMN e métricas de acurácia
    return matrix, sbmn, accuracy_tracker.get_summary()