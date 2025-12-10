import pandas as pd
import openpyxl
from lxml import etree

# Carregar a planilha
df = pd.read_excel(r"C:/Users/Danielle S Castro/Downloads/Extracao_dados_Auditoria_selecao_Danielle_mineracao.xlsx")

# Filtrar registros com usuarioID válido
df = df[df['usuarioID'] != 0]

# Converter coluna de data para datetime
df['data'] = pd.to_datetime(df['data'])

# Criar raiz do XML
root = etree.Element("log", xes_version="1.0", xes_features="nested-attributes", xmlns="http://www.xes-standard.org")

# Agrupar por usuarioID para formar os traces
for usuario_id, group in df.groupby("usuarioID"):
    if usuario_id != 0:
        group_sorted = group.sort_values("data")
        
        # Encontrar todos os índices onde metodo == "SelecionarVagasViewModel"
        inicios = group_sorted[group_sorted["metodo"] == "SelecionarVagasViewModel"].index.tolist()
        
        if not inicios:
            continue
        
        # Criar um trace para cada "início"
        for i, inicio_idx in enumerate(inicios):
            # Encontrar posição do início no group_sorted
            inicio_pos = group_sorted.index.get_loc(inicio_idx)
            
            # Determinar posição do fim
            if i+1 < len(inicios):
                fim_pos = group_sorted.index.get_loc(inicios[i+1])
            else:
                fim_pos = len(group_sorted)
            
            # Selecionar eventos entre início e fim usando posições (iloc)
            eventos_trace = group_sorted.iloc[inicio_pos:fim_pos]
            
            # Criar trace
            trace = etree.SubElement(root, "trace")
            etree.SubElement(trace, "string", key="concept:name", value=f"usuarioID_{usuario_id}_trace_{i+1}")
            
            # Adicionar eventos
            for _, row in eventos_trace.iterrows():
                if row["metodo"] in ["SelecionarVagasViewModel", "ConfirmarInscricaoViewModel", "ListarTitulosExperienciasViewModel", "ListarTitulosExperiencias", "ObterDadosPessoaisViewModel", "ConfirmarInscricaoViewModel", "SEDU2016_EducacaoProfissional"]:
                    event = etree.SubElement(trace, "event")
                    if row["action"] == "SEDU2016_EducacaoProfissional":
                        row["metodo"] = "ConsultarTempoServico"
                    if row["metodo"] == "SelecionarVagasViewModel":
                        row["metodo"] = "SelecionarVagas"
                        
                    if row["metodo"] == "ConfirmarRequisitosViewModel":
                        row["metodo"] = "ConfirmarRequisitos"
                    if row["metodo"] == "ListarTitulosExperienciasViewModel":
                        row["metodo"] = "ListarTitulosExperiencias"
                    if row["metodo"] == "ObterDadosPessoaisViewModel":
                        row["metodo"] = "ConfirmarDadosPessoais"
                    if row["metodo"] == "ConfirmarInscricaoViewModel":
                        row["metodo"] = "ConfirmarInscricao"
                    
                    # if row["action"] == "Index" and row["metodo"] == "ObterIndexViewModel":
                    #     row["action"] = "Obter"+row["controller"]
                    # elif row["action"] == "Index" and row["metodo"] != "ObterIndexViewModel":
                    #     row["action"] = row["metodo"]
                    # if row["metodo"] == "ManterInscricao":
                    #     row["action"] = "Alterar"+row["action"]
                    # if row["action"] == "Listar" and row["metodo"] == "ObterIndexViewModel":
                    #     row["action"] = "Listar"+row["controller"]
                    # if row["action"] == "Cadastro":
                    #     row["action"] = "ObterCadastro"+row["controller"]
                    # if row["action"] == "PesquisarListaNew":
                    #     row["action"] = "PesquisarLista"+row["controller"]
                    # if row["action"] == "ClassificacaoGeral" and row["metodo"] == "GetNomeConcurso":
                    #     row["action"] = "ObterNomeConcurso"
                    # elif row["action"] == "ClassificacaoGeral" and row["metodo"] != "GerarClassificacaoGeral":
                    #     row["action"] = row["metodo"]
                    # if row["action"] == "DadosPessoais" and row["metodo"] != "ManterInscricao":
                    #     row["action"] = "Obter"+row["action"]
                    # if row["action"] == "ConfirmarInscricao":

                    # etree.SubElement(event, "string", key="concept:name", value="login_successful")
                    etree.SubElement(event, "string", key="concept:name", value=row["metodo"])
                    etree.SubElement(event, "string", key="action", value=row["action"])
                    etree.SubElement(event, "date", key="time:timestamp", value=row["data"].isoformat())
                    etree.SubElement(event, "string", key="controller", value=row["controller"])
                    etree.SubElement(event, "string", key="classe", value=row["classe"])
                    if row["metodo"] == "SelecionarVagas":
                        etree.SubElement(event, "string", key="lifecycle:transition", value="start")
                    elif row["metodo"] == "ConfirmarInscricao":
                        etree.SubElement(event, "string", key="lifecycle:transition", value="end")
                    else:
                        etree.SubElement(event, "string", key="lifecycle:transition", value="complete")
                    etree.SubElement(event, "string", key="url", value=row["interface"])

# Salvar o arquivo .xes
tree = etree.ElementTree(root)
tree.write("log_inscricao_candidato.xes", pretty_print=True, xml_declaration=True, encoding="UTF-8")