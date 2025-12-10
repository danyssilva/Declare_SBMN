from assertiontests_functions import Situation, Operator


def parse_sbmn_model(model_strings):
    sbmn_model = []

    allowed_ops = {"DEP", "DEPC", "XOR", "UNI"}

    for line in model_strings:
        line = line.strip()

        # Loop / JMP armazenado separado
        if line.startswith("JMP"):
            # loops.append(line)
            continue

        words = line.split()

        # localizar onde está o operador
        op_index = None
        for i, w in enumerate(words):
            if w in allowed_ops:
                op_index = i
                break

        if op_index is None:
            print(f"Aviso: linha ignorada (sem operador): {line}")
            continue

        op = words[op_index]
        left = " ".join(words[:op_index])          # tudo antes do operador
        right = " ".join(words[op_index + 1:])     # tudo depois do operador

        if not left or not right:
            print(f"Aviso: linha mal formatada: {line}")
            continue

        try:
            sbmn_model.append(Situation(left, right, Operator[op]))
        except KeyError:
            print(f"Aviso: operador desconhecido: {line}")

    return sbmn_model


def generating_model(matrix):
    model = []
    for act1 in sorted(matrix.keys()):
        for act2 in sorted(matrix[act1].keys()):
            relation = matrix[act1][act2]
            str = ""
            if relation in ['DEP', 'DEPC', 'UNI', 'XOR']:
                str = f"{act2} {relation} {act1}"
            if relation == 'JMP':
                str = f"JMP({act1}, {act2})"
            if str != "":
                model.append(str)
    return model


def generate_json_from_sbmn(matrix, activities, output_path=None):
    """
    Converts the SBMN matrix to JSON in the format:
    {
      "Atividades": [{"id": "T0", "nome": "...", "tipo": "Tarefa"}, ...],
      "Situacoes": [{"esquerda": [{"id": "T0"}], "operador": "DEP", "direita": [{"id": "T1"}]}, ...]
    }
    
    The reading is directly from the matrix: matrix[index1][index2]
    - index1 is always on the right
    - index2 is always on the left
    - operator is the value in the matrix
    - Except for JMP, which keeps the original order.
    
    Args:
        matrix: Matrix of relations between activities (matrix[left][right] = operator)
        activities: Dictionary with properties of activities (not currently used)
        output_path: Path to save the JSON file (optional)
    
    Returns:
        dict: JSON structure of the SBMN model
    """
    import json
    
    # Collect all activity names (except BEGIN and END)
    names = set()
    for act1 in matrix.keys():
        if act1 not in ['BEGIN', 'END']:
            names.add(act1)
        for act2 in matrix[act1].keys():
            if act2 not in ['BEGIN', 'END']:
                names.add(act2)
    
    sorted_names = sorted(names)
    
    # Generate stable IDs: T0, T1, T2, ...
    id_map = {name: f"T{i}" for i, name in enumerate(sorted_names)}
    
    # Create list of Activities
    activities = [
        {"id": id_map[n], "name": n, "type": "Task"} 
        for n in sorted_names
    ]
    
    # Prepare situations directly from the matrix
    # matrix[left][right] -> always right operator left, except for JMP
    situations = []
    
    for left in sorted(matrix.keys()):
        if left in ['BEGIN', 'END']:
            continue
            
        for right in sorted(matrix[left].keys()):
            if right in ['BEGIN', 'END']:
                continue
            
            operator = matrix[left][right]
            
            # Ignore if no relation
            if operator == '0':
                continue
            
            operator = str(operator).upper()
            
            if operator == 'JMP':
                # For JMP, keep the original order
                situations.append({
                    "left": [{"id": id_map[left]}],
                    "operator": operator,
                    "right": [{"id": id_map[right]}]
                })
                continue
            else:
                # For all other operators: right operator left
                situations.append({
                    "left": [{"id": id_map[right]}],
                    "operator": operator,
                    "right": [{"id": id_map[left]}]
                })
    
    # Create final JSON structure
    json_structure = {
        "Activities": activities,
        "Situations": situations
    }
    
    # Save file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=2, ensure_ascii=False)
        print(f"JSON saved at: {output_path}")
    
    return json_structure
