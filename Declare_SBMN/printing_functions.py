<<<<<<< HEAD
from collections import defaultdict
from pprint import pprint


def print_matrix(matrix):
    activities = [act for act in matrix.keys() if act not in ['BEGIN', 'END']]
    greater_activity_len = max(len(act) for act in activities)

    linhas = len(activities)
    colunas = linhas

    print(f" " * greater_activity_len + "   " + "-" * greater_activity_len + f"Colunas" + "-" * greater_activity_len)
    print(f" " * greater_activity_len + "   | BEGIN | " + f"{' | '.join(sorted(activities))}" + " | END |")
    diff = greater_activity_len - len("BEGIN") - 1
    str = f"| " + f"BEGIN" + f" " * diff + "  | " + f" " * len("BEGIN") + " |"
    for k in sorted(matrix["BEGIN"].keys()):
        if len(k) % 2 == 0:
            l = int(len(k)/2)
            str += (f" " * (l+1)) + f"{matrix['BEGIN'][k]}" + (f" " * l) + "|"
        else:
            l = int(len(k)/2)
            str += (f" " * l) + f"{matrix['BEGIN'][k]}" + (f" " * (l+1)) + " |"
    str += f" " * len("END") + "  |"
    print(str)

    for act in sorted(activities):
        len_activity = len(act)
        diff = greater_activity_len - len_activity
        if diff > 0:
          str = f"| " + f"{act}" + " " * diff + " | "
        else:
          str = f"| " + f"{act}" + " | "
        str += f" " * len("BEGIN") + " |"
        for k in sorted(matrix[act].keys()):
            if len(k) % 2 == 0:
                l = int(len(k)/2)
                str += (f" " * (l+1)) + f"{matrix[act][k]}" + (f" " * l) + "|"
            else:
                l = int(len(k)/2)
                str += (f" " * l) + f"{matrix[act][k]}" + (f" " * (l+1)) + " |"
        str += f" " * len("END") + "  |"
        print(str)

    diff = greater_activity_len - len("END") - 1
    str = f"| " + f"END" + f" " * diff + "  | " + f" " * len("BEGIN") + " |"
    for k in sorted(matrix["END"].keys()):
        if len(k) % 2 == 0:
            l = int(len(k)/2)
            str += (f" " * (l+1)) + f"{matrix['END'][k]}" + (f" " * l) + "|"
        else:
            l = int(len(k)/2)
            str += (f" " * l) + f"{matrix['END'][k]}" + (f" " * (l+1)) + " |"
    str += f" " * len("END") + "  |"
    print(str)
=======
from collections import defaultdict
from pprint import pprint


def print_matrix(matrix):
    activities = [act for act in matrix.keys() if act not in ['BEGIN', 'END']]
    greater_activity_len = max(len(act) for act in activities)

    linhas = len(activities)
    colunas = linhas

    print(f" " * greater_activity_len + "   " + "-" * greater_activity_len + f"Colunas" + "-" * greater_activity_len)
    print(f" " * greater_activity_len + "   | BEGIN | " + f"{' | '.join(sorted(activities))}" + " | END |")
    diff = greater_activity_len - len("BEGIN") - 1
    str = f"| " + f"BEGIN" + f" " * diff + "  | " + f" " * len("BEGIN") + " |"
    for k in sorted(matrix["BEGIN"].keys()):
        if len(k) % 2 == 0:
            l = int(len(k)/2)
            str += (f" " * (l+1)) + f"{matrix['BEGIN'][k]}" + (f" " * l) + "|"
        else:
            l = int(len(k)/2)
            str += (f" " * l) + f"{matrix['BEGIN'][k]}" + (f" " * (l+1)) + " |"
    str += f" " * len("END") + "  |"
    print(str)

    for act in sorted(activities):
        len_activity = len(act)
        diff = greater_activity_len - len_activity
        if diff > 0:
          str = f"| " + f"{act}" + " " * diff + " | "
        else:
          str = f"| " + f"{act}" + " | "
        str += f" " * len("BEGIN") + " |"
        for k in sorted(matrix[act].keys()):
            if len(k) % 2 == 0:
                l = int(len(k)/2)
                str += (f" " * (l+1)) + f"{matrix[act][k]}" + (f" " * l) + "|"
            else:
                l = int(len(k)/2)
                str += (f" " * l) + f"{matrix[act][k]}" + (f" " * (l+1)) + " |"
        str += f" " * len("END") + "  |"
        print(str)

    diff = greater_activity_len - len("END") - 1
    str = f"| " + f"END" + f" " * diff + "  | " + f" " * len("BEGIN") + " |"
    for k in sorted(matrix["END"].keys()):
        if len(k) % 2 == 0:
            l = int(len(k)/2)
            str += (f" " * (l+1)) + f"{matrix['END'][k]}" + (f" " * l) + "|"
        else:
            l = int(len(k)/2)
            str += (f" " * l) + f"{matrix['END'][k]}" + (f" " * (l+1)) + " |"
    str += f" " * len("END") + "  |"
    print(str)
>>>>>>> 616cea218b0ecea37f4460362e93cb29a982065b
