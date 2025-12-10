from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Set, Tuple, Optional


class Operator(str, Enum):
    DEP = "DEP"    # dependência estrita
    DEPC = "DEPC"  # dependência circunstancial
    XOR = "XOR"    # exclusão mútua
    UNI = "UNI"    # união inclusiva


@dataclass(frozen=True)
class Situation:
    left: str
    right: str
    op: Operator

    def is_choice(self) -> bool:
        # XOR / UNI são situações de escolha
        return self.op in {Operator.XOR, Operator.UNI}

    def contains_operand(self, task: str) -> bool:
        return self.left == task or self.right == task


class SBMNValidator:
    """
    Validador de modelos SBMN baseado nos testes assertivos do artigo
    (Equivalent Operators, Cyclic Dependency, Blocking of Indirect Dependency,
    Promiscuity, Dual Dependency). :contentReference[oaicite:2]{index=2}
    """

    def __init__(self, enable_dual_dependency: bool = True):
        # Se quiser reproduzir o estado atual da classe Caminho,
        # pode passar enable_dual_dependency=False, pois lá está comentado.
        self.enable_dual_dependency = enable_dual_dependency
        self.situations: List[Situation] = []
        # grafo direcionado apenas com DEP (dependência estrita)
        self.dep_graph: Dict[str, Set[str]] = {}

    # ====================== util do grafo de DEP ======================

    def _ensure_vertex(self, v: str):
        if v not in self.dep_graph:
            self.dep_graph[v] = set()

    def _add_edge(self, u: str, v: str) -> bool:
        """
        Adiciona aresta u->v no grafo de dependência.
        Retorna False se criar ciclo (reverte).
        Implementa a parte central do Teste 2 (Cyclic Dependency). :contentReference[oaicite:3]{index=3}
        """
        self._ensure_vertex(u)
        self._ensure_vertex(v)

        # já existe u -> v (duplicata)?
        if v in self.dep_graph[u]:
            return False

        # já existe v -> u (ciclo 2 nós)?
        if u in self.dep_graph.get(v, set()):
            return False

        self.dep_graph[u].add(v)
        if self._has_cycle():
            # reverte se criou ciclo
            self.dep_graph[u].remove(v)
            return False
        return True

    def _remove_edge(self, u: str, v: str):
        if u in self.dep_graph and v in self.dep_graph[u]:
            self.dep_graph[u].remove(v)

    def _has_cycle(self) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {v: WHITE for v in self.dep_graph}

        def dfs(u: str) -> bool:
            color[u] = GRAY
            for w in self.dep_graph[u]:
                if color[w] == GRAY:
                    return True
                if color[w] == WHITE and dfs(w):
                    return True
            color[u] = BLACK
            return False

        for v in list(self.dep_graph.keys()):
            if color[v] == WHITE and dfs(v):
                return True
        return False

    # ====================== Teste 1: Equivalent Operators ======================

    def _check_equivalent_operators(self, v: Situation) -> bool:
        """
        Retorna True se já existe qualquer situação entre o mesmo par de tarefas
        (independente do operador). :contentReference[oaicite:4]{index=4}
        """
        for s in self.situations:
            same_pair = (
                (v.left == s.left and v.right == s.right) or
                (v.left == s.right and v.right == s.left)
            )
            if same_pair:
                return True
        return False

    # ====================== Teste 4: Promiscuity ======================

    def _check_promiscuity(self, s: Situation) -> bool:
        """
        Detecta se a nova situação conecta operandos que já participam de escolhas
        conflitantes (XOR/UNI) com outros nós. :contentReference[oaicite:5]{index=5}
        """
        eesq = False
        edir = False
        op_esq: Optional[Operator] = None
        op_dir: Optional[Operator] = None

        for v in self.situations:
            if not v.is_choice():
                continue

            if v.contains_operand(s.left):
                eesq = True
                op_esq = v.op

            if v.contains_operand(s.right):
                edir = True
                op_dir = v.op

            if eesq and edir:
                # se os operadores são diferentes entre si, ou diferentes do operador
                # da nova situação, temos promiscuidade
                if (op_esq != op_dir) or (op_esq != s.op) or (op_dir != s.op):
                    return True

        return False

    # ====================== Teste 2: Cyclic Dependency ======================

    def _insert_dependency(self, v: Situation) -> bool:
        """
        Insere DEP em dep_graph e em situations se não gerar ciclo.
        Implementa a lógica descrita para insereSituacaoDependencia. :contentReference[oaicite:6]{index=6}
        """
        assert v.op == Operator.DEP

        # caso inicial
        if not self.situations and not self.dep_graph:
            self._ensure_vertex(v.left)
            self._ensure_vertex(v.right)
            self.dep_graph[v.left].add(v.right)
            self.situations.append(v)
            return True

        # já existe DEP direta ou inversa
        if (
            v.left in self.dep_graph and v.right in self.dep_graph[v.left]
        ) or (
            v.right in self.dep_graph and v.left in self.dep_graph[v.right]
        ):
            return False

        if not self._add_edge(v.left, v.right):
            return False

        self.situations.append(v)
        return True

    # ====================== Teste 3: Blocking of Indirect Dependency ======================

    def _simulate_dependency(self, v: Situation) -> bool:
        """
        Simula DEP (dummy) entre v.left->v.right, usando a mesma lógica de ciclo,
        mas sempre revertendo. Usado para testar escolhas (XOR/UNI). :contentReference[oaicite:7]{index=7}
        """
        assert v.op == Operator.DEP

        # bloqueio direto/inverso
        if (
            v.left in self.dep_graph and v.right in self.dep_graph[v.left]
        ) or (
            v.right in self.dep_graph and v.left in self.dep_graph[v.right]
        ):
            return False

        if not self._add_edge(v.left, v.right):
            return False

        # reverte sempre, pois é simulação
        self._remove_edge(v.left, v.right)
        return True

    def _insert_choice(self, v: Situation) -> bool:
        """
        Insere XOR/UNI testando se seria possível uma DEP em ambos sentidos
        entre os operandos. Se não for, a escolha bloquearia dependências indiretas. :contentReference[oaicite:8]{index=8}
        """
        assert v.is_choice()

        # testa se seria possível esq -> dir
        dummy1 = Situation(v.left, v.right, Operator.DEP)
        if not self._simulate_dependency(dummy1):
            return False

        # testa se seria possível dir -> esq
        dummy2 = Situation(v.right, v.left, Operator.DEP)
        if not self._simulate_dependency(dummy2):
            return False

        # se passou, a escolha é compatível com o grafo de DEP
        self.situations.append(v)
        return True

    def _test_choice_against_graph(self, v: Situation) -> bool:
        """
        Reaplica o teste de escolha após inserção de uma nova DEP.
        Se a escolha se tornar incompatível, há Blocking of Indirect Dependency. :contentReference[oaicite:9]{index=9}
        """
        dummy1 = Situation(v.left, v.right, Operator.DEP)
        if not self._simulate_dependency(dummy1):
            return False
        dummy2 = Situation(v.right, v.left, Operator.DEP)
        if not self._simulate_dependency(dummy2):
            return False
        return True

    # ====================== Teste 5: Dual Dependency ======================

    def _check_dual_dependency(self, v: Situation) -> bool:
        """
        Retorna True se houver violação de Dual Dependency:
        - tarefa depende de dois nós que são XOR entre si; ou
        - é criada XOR entre dois nós já ambos dependidos por um mesmo nó. :contentReference[oaicite:10]{index=10}
        """
        if not self.enable_dual_dependency:
            return False

        # Só XOR é realmente excludente; UNI não entra aqui.
        if v.is_choice():
            if v.op != Operator.XOR:
                return False

            # Caso 1: v é escolha XOR; checa se existe x tal que x->left e x->right
            for x in self.dep_graph:
                if (
                    v.left in self.dep_graph.get(x, set()) and
                    v.right in self.dep_graph.get(x, set())
                ):
                    return True
            return False

        else:
            # Caso 2: v é dependência estrita; DEPC não é considerada aqui
            if v.op != Operator.DEP:
                return False

            # insere temporariamente no grafo
            inserted = self._add_edge(v.left, v.right)
            if not inserted:
                # se não conseguiu inserir, não vamos atribuir isso a dual dependency
                return False

            try:
                for s in self.situations:
                    if not s.is_choice() or s.op != Operator.XOR:
                        continue
                    # padrão: v.left -> s.left e v.left -> s.right
                    if (
                        s.left in self.dep_graph.get(v.left, set()) and
                        s.right in self.dep_graph.get(v.left, set())
                    ):
                        return True
                return False
            finally:
                # reverte aresta temporária
                self._remove_edge(v.left, v.right)

    # ====================== Inserção com todos os testes ======================

    def insert_situation(self, v: Situation) -> Tuple[bool, Optional[str]]:
        """
        Tenta inserir uma situação.
        Retorna (ok, motivo_erro).
        motivo_erro é None se ok == True.
        """
        # 1) Equivalent Operators
        if self._check_equivalent_operators(v):
            return False, "EquivalentOperators"

        # 2) Promiscuity
        if self._check_promiscuity(v):
            return False, "Promiscuity"

        # 3) Dual Dependency
        if self._check_dual_dependency(v):
            return False, "DualDependency"

        # 4) Dependência (DEP/DEPC) vs Escolha (XOR/UNI)
        if not v.is_choice():
            # DEP ou DEPC
            if v.op == Operator.DEP:
                if not self._insert_dependency(v):
                    return False, "CyclicDependencyOrInvalidDependency"
            else:
                # DEPC: não entra no grafo de DEP (gdep), mas fica registrada
                self.situations.append(v)

            # depois de inserir DEP/DEPC, revalidar todas as escolhas (Blocking)
            for s in list(self.situations):
                if s.is_choice():
                    if not self._test_choice_against_graph(s):
                        # rollback da situação recém inserida
                        if v in self.situations:
                            self.situations.remove(v)
                        if v.op == Operator.DEP:
                            self._remove_edge(v.left, v.right)
                        return False, "BlockingOfIndirectDependency"

            return True, None

        else:
            # XOR / UNI: insere escolha com simulação de DEP
            if not self._insert_choice(v):
                return False, "BlockingOfIndirectDependency"
            return True, None

    # ====================== API principal ======================

    def validate_model(self, situations: List[Situation]):
        """
        Valida uma lista de situações SBMN.
        Retorna:
        {
          "valid": bool,
          "accepted": [Situation, ...],
          "errors": [{"situation": Situation, "reason": str}, ...],
          "dep_graph": { tarefa: [sucessores], ... }
        }
        """
        self.situations = []
        self.dep_graph = {}
        errors = []

        for s in situations:
            ok, reason = self.insert_situation(s)
            if not ok:
                errors.append({"situation": s, "reason": reason})

        return {
            "valid": len(errors) == 0,
            "accepted": list(self.situations),
            "errors": errors,
            "dep_graph": {k: sorted(v) for k, v in self.dep_graph.items()},
        }
