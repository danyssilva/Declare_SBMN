<<<<<<< HEAD
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
=======
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
>>>>>>> 616cea218b0ecea37f4460362e93cb29a982065b
