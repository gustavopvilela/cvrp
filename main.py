import sys
import os
import utils
import time
import graficos_resultados as gr
import teste_hipotese as th
from busca_local.busca_lexicografica import shift_inter_rotas, shift_intra_rotas
from busca_local.dois_opt import dois_opt_inter_rota, dois_opt_intra_rota
from heuristicas_construtivas.mole_jameson import mole_jameson
from heuristicas_construtivas.economiasClarkWright import clarke_wright
from heuristicas_construtivas.gillet_miller import GilletMiller
from busca_local.busca_sequencial import busca_sequencial

HEURISTICAS = ["MJ", "CW", "GM"]
BUSCAS_LOCAIS = [
    "LS-MJ-BL-Shift", "LS-CW-BL-Shift", "LS-GM-BL-Shift",
    "LS-MJ-BL-2Opt", "LS-CW-BL-2Opt", "LS-GM-BL-2Opt",
    "LS-CW-BS-Swap", "LS-MJ-BS-Swap", "LS-GM-BS-Swap"
]
GRUPOS_LOTE = ["ALL_H", "ALL_LS_MJ", "ALL_LS_CW", "ALL_LS_GM"]
METODOS_VALIDOS = HEURISTICAS + BUSCAS_LOCAIS
OTIMOS_CONHECIDOS = {
    'A-n80-k10.vrp': 1763.0,
    'CMT10.vrp': 1395.0,
    'E-n101-k14.vrp': 1067.0,
    'F-n72-k4.vrp': 237.0,
    'F-n135-k7.vrp': 1162.0,
    'Golden_3.vrp': 10997.8,
    'Golden_18.vrp': 995.13,
    'Li_21.vrp': 16212.83,
    'Loggi-n601-k42.vrp': 347046.0,
    'M-n151-k12.vrp': 1015.0,
    'tai150b.vrp': 2727.03,
    'tai385.vrp': 24366.41,
    'X-n502-k39.vrp': 69226.0,
    'XL-n1701-k562.vrp': 521136.0,
    'XL-n2541-k121.vrp': 146390.0
}


def executar_metodo(dados_instancia, metodo, solucao_base=None):
    tempo_inicio_geral = time.time()

    if solucao_base is not None:
        rotas, custo_total, custo_sem_penalidade, veiculos_usados = solucao_base
    else:
        if "MJ" in metodo:
            rotas, custo_total, custo_sem_penalidade, veiculos_usados = mole_jameson(dados_instancia, lambda_param=1.0)
        elif "CW" in metodo:
            rotas, custo_total, custo_sem_penalidade, veiculos_usados = clarke_wright(dados_instancia)
        elif "GM" in metodo:
            solver = GilletMiller(dados_instancia)
            rotas, custo_total, custo_sem_penalidade, veiculos_usados = solver.gillet_miller()
        else:
            raise ValueError("Método desconhecido.")

    tempo_fim_construtiva = time.time()

    if metodo in HEURISTICAS:
        return rotas, custo_total, tempo_fim_construtiva - tempo_inicio_geral

    estado = utils.encode(rotas, dados_instancia['demands'], dados_instancia['depot'])
    estado['custo_sem_penalidade'] = custo_sem_penalidade
    estado['veiculos_disponiveis'] = dados_instancia.get('trucks', veiculos_usados)
    estado['custo_total'] = custo_total

    tempo_inicio_bl = time.time()

    if "BL-Shift" in metodo:
        melhoria_geral = True
        max_iteracoes = 100
        iteracao_atual = 0
        while melhoria_geral and iteracao_atual < max_iteracoes:
            melhoria_geral = False
            iteracao_atual += 1
            houve_melhoria, estado, delta = shift_inter_rotas(estado, dados_instancia['distance_matrix'],
                                                              dados_instancia['demands'], dados_instancia['capacity'],
                                                              dados_instancia['depot'])
            if houve_melhoria:
                melhoria_geral = True
                continue
            houve_melhoria, estado, delta = shift_intra_rotas(estado, dados_instancia['distance_matrix'],
                                                              dados_instancia['depot'])
            if houve_melhoria: melhoria_geral = True
        if iteracao_atual >= max_iteracoes: print(
            f"Aviso: busca local interrompida no limite de {max_iteracoes} iterações.")


    elif "BL-2Opt" in metodo:
        melhoria_geral = True
        max_iteracoes = 100
        iteracao_atual = 0

        while melhoria_geral and iteracao_atual < max_iteracoes:
            melhoria_geral = False
            melhoria_inter = True

            while melhoria_inter and iteracao_atual < max_iteracoes:
                iteracao_atual += 1
                melhoria_inter, estado, delta_inter = dois_opt_inter_rota(
                    estado,
                    dados_instancia['distance_matrix'],
                    dados_instancia['demands'],
                    dados_instancia['capacity'],
                    dados_instancia['depot']
                )

                if melhoria_inter:
                    melhoria_geral = True

            melhoria_intra = True
            while melhoria_intra and iteracao_atual < max_iteracoes:
                iteracao_atual += 1
                melhoria_intra, estado, delta_intra = dois_opt_intra_rota(
                    estado,
                    dados_instancia['distance_matrix'],
                    dados_instancia['depot']
                )

                if melhoria_intra:
                    melhoria_geral = True
                    break

    elif "BS-Swap" in metodo:
        houve_melhoria = True
        while houve_melhoria:
            houve_melhoria, estado, delta = busca_sequencial(estado, dados_instancia['distance_matrix'],
                                                             dados_instancia['demands'], dados_instancia['capacity'],
                                                             dados_instancia['depot'])

    tempo_fim_bl = time.time()
    rotas = utils.decode(estado, dados_instancia['depot'])
    custo_total = estado['custo_total']

    print(f"USADOS DEPOIS DA BUSCA LOCAL: {len(rotas)}/{dados_instancia['trucks']}")

    return rotas, custo_total, tempo_fim_bl - tempo_inicio_bl

def processar_instancia(caminho_arquivo, arquivo_saida, otimo_conhecido, metodo, metodo_nome_saida, solucao_base=None, dados_instancia=None):
    if dados_instancia is None:
        try:
            dados_instancia = utils.ler_instancia(caminho_arquivo)
        except FileNotFoundError:
            print(f"Erro: o arquivo {caminho_arquivo} não foi encontrado.")
            return None, None

    rotas, custo_total, runtime = executar_metodo(dados_instancia, metodo, solucao_base)

    if otimo_conhecido and otimo_conhecido > 0:
        gap = 100 * (abs(custo_total - otimo_conhecido) / otimo_conhecido)
    else:
        gap = -1.0

    escrever_cabecalho = not os.path.exists(arquivo_saida)
    nome_instancia_limpo = dados_instancia.get('name', os.path.basename(caminho_arquivo).replace('.vrp', ''))
    with open(arquivo_saida, "a") as arquivo:
        if escrever_cabecalho:
            arquivo.write(f"{'INSTANCE':<15} {'METHOD':<15} {'OBJECTIVE':<15} {'RUNTIME':<15} {'GAP':<15}\n")
        gap_str = f"{gap:<15.2f}" if gap != -1.0 else f"{'N/A':<15}"
        arquivo.write(f"{nome_instancia_limpo:<15} {metodo_nome_saida:<15} {custo_total:<15.2f} {runtime:<15.2f} {gap_str}\n")

    os.makedirs(metodo_nome_saida, exist_ok=True)
    nome_imagem = f"{metodo_nome_saida}/{nome_instancia_limpo}.png"
    utils.plotar_rotas(dados_instancia, rotas, nome_imagem)
    print(f"-> [{nome_instancia_limpo}] concluído. Custo: {custo_total:.2f}")

    return gap, runtime

def main ():
    if len(sys.argv) != 5:
        print("Insira os argumentos corretamente.")
        print("Para uma instância: python main.py <instância> <arquivo_saida> <ótimo> <MÉTODO>")
        print(
            "Para todas:         python main.py ALL <arquivo_saida> 0 <MÉTODO | ALL_H | ALL_LS_MJ | ALL_LS_CW | ALL_LS_GM>")
        print(f"Heurísticas:        {', '.join(HEURISTICAS)}")
        print(f"Buscas Locais:      {', '.join(BUSCAS_LOCAIS)}")
        sys.exit(1)

    instancia_arg = sys.argv[1]
    arquivo_saida = sys.argv[2]
    otimo_conhecido_arg = float(sys.argv[3])
    metodo = sys.argv[4]

    if metodo == "ALL":
        metodo = "ALL_H"

    if instancia_arg == "ALL":
        if metodo not in METODOS_VALIDOS and metodo not in GRUPOS_LOTE:
            print(f"Erro: o método '{metodo}' não é reconhecido.")
            sys.exit(1)

        pasta_instancias = "instances/"
        if not os.path.exists(pasta_instancias):
            print(f"Erro: o diretório {pasta_instancias} não existe.")
            sys.exit(1)

        arquivos = [f for f in os.listdir(pasta_instancias) if f.endswith(".vrp")]
        if not arquivos:
            print(f"Nenhum arquivo .vrp encontrado em {pasta_instancias}.")
            sys.exit(1)

        lista_metodos = []
        if metodo in GRUPOS_LOTE:
            if metodo == "ALL_H":
                lista_metodos = HEURISTICAS
            elif metodo == "ALL_LS_MJ":
                lista_metodos = ["LS-MJ-BL-Shift", "LS-MJ-BL-2Opt", "LS-MJ-BS-Swap"]
            elif metodo == "ALL_LS_CW":
                lista_metodos = ["LS-CW-BL-Shift", "LS-CW-BL-2Opt", "LS-CW-BS-Swap"]
            elif metodo == "ALL_LS_GM":
                lista_metodos = ["LS-GM-BL-Shift", "LS-GM-BL-2Opt", "LS-GM-BS-Swap"]

            resultados = {m: {"gaps": [], "runtimes": []} for m in lista_metodos}

            if metodo == "ALL_H":
                for m in lista_metodos:
                    print(f"Iniciando benchmarking em lote ({m}) para {len(arquivos)} instâncias...")
                    for arquivo in arquivos:
                        caminho_completo = os.path.join(pasta_instancias, arquivo)
                        otimo_dict = OTIMOS_CONHECIDOS.get(arquivo, 0.0)
                        gap, runtime = processar_instancia(caminho_completo, arquivo_saida, otimo_dict, m, m)
                        if gap is not None and runtime is not None:
                            if gap != -1.0: resultados[m]["gaps"].append(gap)
                            resultados[m]["runtimes"].append(runtime)
            else:
                print(f"Iniciando benchmarking em lote (Grupo {metodo}) para {len(arquivos)} instâncias...")
                for arquivo in arquivos:
                    caminho_completo = os.path.join(pasta_instancias, arquivo)
                    otimo_dict = OTIMOS_CONHECIDOS.get(arquivo, 0.0)

                    try:
                        dados_instancia = utils.ler_instancia(caminho_completo)
                    except FileNotFoundError:
                        continue

                    if metodo == "ALL_LS_MJ":
                        solucao_base = mole_jameson(dados_instancia, lambda_param=1.0)
                    elif metodo == "ALL_LS_CW":
                        solucao_base = clarke_wright(dados_instancia)
                    elif metodo == "ALL_LS_GM":
                        solver = GilletMiller(dados_instancia)
                        solucao_base = solver.gillet_miller()

                    for m in lista_metodos:
                        gap, runtime = processar_instancia(
                            caminho_completo, arquivo_saida, otimo_dict, m, m,
                            solucao_base=solucao_base, dados_instancia=dados_instancia
                        )
                        if gap is not None and runtime is not None:
                            if gap != -1.0: resultados[m]["gaps"].append(gap)
                            resultados[m]["runtimes"].append(runtime)

            print(f"\nExecução em lote ({metodo}) finalizada. Gerando gráficos...")

            if metodo == "ALL_H":
                gr.gerar_boxplot_gaps_heuristicas_construtivas(resultados["MJ"]["gaps"], resultados["CW"]["gaps"],
                                                               resultados["GM"]["gaps"])
                gr.gerar_grafico_barras_runtime_heuristicas_construtivas(resultados["MJ"]["runtimes"],
                                                                         resultados["CW"]["runtimes"],
                                                                         resultados["GM"]["runtimes"])
                gr.gerar_intervalo_confianca_heuristicas_construtivas(resultados["MJ"]["gaps"],
                                                                      resultados["CW"]["gaps"],
                                                                      resultados["GM"]["gaps"])
                th.gerar_grafico_diferenca_critica(resultados["MJ"]["gaps"], resultados["CW"]["gaps"],
                                                   resultados["GM"]["gaps"])
                th.comparar_heuristicas(resultados["MJ"]["gaps"], resultados["CW"]["gaps"], resultados["GM"]["gaps"])
            else:
                m1, m2, m3 = lista_metodos
                gr.gerar_boxplot_gaps_busca_local(resultados[m1]["gaps"], resultados[m2]["gaps"],
                                                  resultados[m3]["gaps"])
                gr.gerar_grafico_barras_runtime_busca_local(resultados[m1]["runtimes"], resultados[m2]["runtimes"],
                                                            resultados[m3]["runtimes"])
                gr.gerar_intervalo_confianca_busca_local(resultados[m1]["gaps"], resultados[m2]["gaps"],
                                                         resultados[m3]["gaps"])
                th.comparar_buscas_locais(resultados[m1]["gaps"], resultados[m2]["gaps"], resultados[m3]["gaps"])
        else:
            print(f"Iniciando benchmarking em lote ({metodo}) para {len(arquivos)} instâncias...")
            for arquivo in arquivos:
                caminho_completo = os.path.join(pasta_instancias, arquivo)
                otimo_dict = OTIMOS_CONHECIDOS.get(arquivo, 0.0)
                processar_instancia(caminho_completo, arquivo_saida, otimo_dict, metodo, metodo)
        print("\nExecução em lote finalizada com sucesso.")
    else:
        if metodo not in METODOS_VALIDOS:
            print(f"Erro: o método '{metodo}' não é reconhecido. Verifique as opções.")
            sys.exit(1)

        caminho_arquivo = instancia_arg
        if not caminho_arquivo.endswith(".vrp"):
            caminho_arquivo += ".vrp"

        caminho_completo = f"instances/{caminho_arquivo}"
        print(f"Iniciando benchmarking em {caminho_completo} com o método {metodo}...")
        processar_instancia(caminho_completo, arquivo_saida, otimo_conhecido_arg, metodo, metodo)

if __name__ == "__main__":
    main()