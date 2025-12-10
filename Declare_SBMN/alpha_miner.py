import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from sklearn import tree  # ✅ nome correto
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.algo.filtering.log.variants import variants_filter

def extrair_relacoes_alpha(net):
    relacoes = []
    for arc in net.arcs:
        src = getattr(arc.source, "label", None)
        tgt = getattr(arc.target, "label", None)
        if src and tgt:
            relacoes.append((src, tgt))
    return relacoes

if __name__ == "__main__":
    # Carrega o log
    # log = xes_importer.apply("saida.xes")
    # log_path = "F:/Danielle/Mestrado/BPMN_Novo/JMP2/Teste/saida.xes"  # ajuste
    log_path = r"F:/Danielle/Mestrado/BPMN_Novo/MINIMETAL/metalmec_log.xes"  # ajuste
    log = xes_importer.apply(log_path)

    # Remove variantes muito raras
    # variants = variants_filter.get_variants(log)
    # filtered_log = variants_filter.apply_variants_by_coverage(log, variants, 0.9)

    # Aplica o Alpha Miner
    # net, initial_marking, final_marking = alpha_miner.apply(log)
    # net, initial_marking, final_marking = alpha_miner.apply(log, parameters={"remove_unconnected": True}, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS)
    net, initial_marking, final_marking = alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS)

    # Visualiza a Rede de Petri
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.view(gviz)

    # converte para bpmn
    bpmn_model = pm4py.convert_to_bpmn(net, initial_marking, final_marking)
    pm4py.view_bpmn(bpmn_model)

    # Exibe as relações diretas (dependências)
    # for arc in net.arcs:
    #     print("Arc:", arc.source)
    #     print("Arc:", arc.target)
    #     if hasattr(arc.source, "label") and hasattr(arc.target, "label"):
    #         print(f"{arc.source.label} -> {arc.target.label}")
    
    # print("Net:", net)

    # relacoes = extrair_relacoes_alpha(net)
    # for a, b in relacoes:
    #     print(f"{a} DEP {b}")
