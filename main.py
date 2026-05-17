import sys
import os
import utils
import time
import graficos_resultados as gr
import teste_hipotese as th
from mole_jameson import mole_jameson
from economiasClarkWright import clarke_wright
from gillet_miller import GilletMiller

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

def executar_metodo (dados_instancia, metodo):
    if metodo == "MJ":
        tempo_inicio = time.time()
        rotas, custo_total = mole_jameson(dados_instancia, lambda_param=1.0)
        tempo_fim = time.time()
    elif metodo == "CW":
        tempo_inicio = time.time()
        rotas, custo_total = clarke_wright(dados_instancia)
        tempo_fim = time.time()
    elif metodo == "GM":
        tempo_inicio = time.time()
        solver = GilletMiller(dados_instancia)
        rotas, custo_total = solver.gillet_miller()
        tempo_fim = time.time()
    else:
        raise ValueError("Método desconhecido.")

    return rotas, custo_total, tempo_fim - tempo_inicio

def processar_instancia (caminho_arquivo, arquivo_saida, otimo_conhecido, metodo, metodo_nome_saida):
    try:
        dados_instancia = utils.ler_instancia(caminho_arquivo)
    except FileNotFoundError:
        print(f"Erro: o arquivo {caminho_arquivo} não foi encontrado.")
        return

    rotas, custo_total, runtime = executar_metodo(dados_instancia, metodo)

    # Cálculo do gap
    if otimo_conhecido and otimo_conhecido > 0:
        gap = 100 * (abs(custo_total - otimo_conhecido) / otimo_conhecido)
    else:
        gap = -1.0 # Indica que não tem ótimo cadastrado

    # Escrevendo no arquivo de saída
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
        print("Para uma instância:  python main.py <instância> <arquivo_saida> <ótimo> <MJ|CW|GM>")
        print("Para todas:          python main.py ALL <arquivo_saida> 0 <MJ|CW|GM|ALL>")
        sys.exit(1)

    instancia_arg = sys.argv[1]
    arquivo_saida = sys.argv[2]
    otimo_conhecido_arg = float(sys.argv[3])
    heuristica = sys.argv[4]

    # Execução em lote
    if instancia_arg == "ALL":
        if heuristica not in ["MJ", "CW", "GM", "ALL"]:
            print(f"Erro: a heurística {heuristica} não é reconhecida. Use MJ, CW ou GM.")
            sys.exit(1)

        pasta_instancias = "instances/"
        if not os.path.exists(pasta_instancias):
            print(f"Erro: o diretório {pasta_instancias} não existe.")
            sys.exit(1)

        arquivos = [f for f in os.listdir(pasta_instancias) if f.endswith('.vrp')]
        if not arquivos:
            print(f"Nenhum arquivo .vrp encontrado em {pasta_instancias}")
            sys.exit(1)

        if heuristica == "ALL":
            resultados = {
                "MJ": {"gaps": [], "runtimes": []},
                "CW": {"gaps": [], "runtimes": []},
                "GM": {"gaps": [], "runtimes": []},
            }

            for h in ["MJ", "CW", "GM"]:
                print(f"Iniciando benchmarking em lote ({h}) para {len(arquivos)} instâncias...")
                for arquivo in arquivos:
                    caminho_completo = os.path.join(pasta_instancias, arquivo)
                    otimo_dict = OTIMOS_CONHECIDOS.get(arquivo, 0.0)
                    gap, runtime = processar_instancia(caminho_completo, arquivo_saida, otimo_dict, h, h)

                    if gap is not None and runtime is not None:
                        if gap != -1.0:
                            resultados[h]["gaps"].append(gap)
                        resultados[h]["runtimes"].append(runtime)

            print("\nExecução em lote finalizada com sucesso. Gerando gráficos de resultados...")

            gr.gerar_boxplot_gaps(resultados["MJ"]["gaps"], resultados["CW"]["gaps"], resultados["GM"]["gaps"])
            gr.gerar_grafico_barras_runtime(resultados["MJ"]["runtimes"], resultados["CW"]["runtimes"], resultados["GM"]["runtimes"])
            gr.gerar_intervalo_confianca(resultados["MJ"]["gaps"], resultados["CW"]["gaps"], resultados["GM"]["gaps"])
            th.gerar_grafico_diferenca_critica(resultados["MJ"]["gaps"], resultados["CW"]["gaps"], resultados["GM"]["gaps"])
            th.comparar_heuristicas(resultados["MJ"]["gaps"], resultados["CW"]["gaps"], resultados["GM"]["gaps"])
        else:
            print(f"Iniciando benchmarking em lote ({heuristica}) para {len(arquivos)} instâncias...")
            for arquivo in arquivos:
                caminho_completo = os.path.join(pasta_instancias, arquivo)
                otimo_dict = OTIMOS_CONHECIDOS.get(arquivo, 0.0)
                processar_instancia(caminho_completo, arquivo_saida, otimo_dict, heuristica, heuristica)

        print("\nExecução em lote finalizada com sucesso.")
    # Execução de uma instância
    else:
        if heuristica not in ["MJ", "CW", "GM"]:
            print(f"Erro: a heurística {heuristica} não é reconhecida. Use MJ, CW ou GM.")
            sys.exit(1)

        caminho_arquivo = instancia_arg
        if not caminho_arquivo.endswith(".vrp"):
            caminho_arquivo += ".vrp"

        caminho_completo = f"instances/{caminho_arquivo}"
        print(f"Iniciando benchmarking em {caminho_completo}...")
        processar_instancia(caminho_completo, arquivo_saida, otimo_conhecido_arg, heuristica, heuristica)

if __name__ == "__main__":
    main()