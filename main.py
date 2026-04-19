import sys
import os
import utils
import time
from mole_jameson import mole_jameson
from economiasClarkWright import clarke_wright

def main ():
    if len(sys.argv) != 5:
        print("Insira os argumentos corretamente.")
        print("python main.py <instância> <arquivo de saída> <ótimo conhecido> <heurística>")
        print("Exemplo: python main.py A-n80-k10 resultados_mj.dat 1763 MJ")
        sys.exit(1)

    instancia_arg = sys.argv[1]
    arquivo_saida = sys.argv[2]
    otimo_conhecido = float(sys.argv[3])
    heuristica = sys.argv[4]

    rotas = []
    custo_total = 0

    caminho_arquivo = instancia_arg
    if not caminho_arquivo.endswith(".vrp"):
        caminho_arquivo += ".vrp"

    try:
        dados_instancia = utils.ler_instancia(f"instances/{caminho_arquivo}")
    except FileNotFoundError:
        print(f"Erro: o arquivo {caminho_arquivo} não foi encontrado")
        exit(1)

    if heuristica == "MJ":
        tempo_inicio = time.time()
        rotas, custo_total = mole_jameson(dados_instancia, lambda_param=1.0)
        tempo_fim = time.time()
    elif heuristica == "CW":
        tempo_inicio = time.time()
        rotas, custo_total = clarke_wright(dados_instancia)
        tempo_fim = time.time()
    else:
        print(f"Erro: esta heurística não é implementada neste programa")
        exit(1)

    runtime = tempo_fim - tempo_inicio
    gap = 100 * (abs(custo_total - otimo_conhecido) / otimo_conhecido)

    # Escrevendo no arquivo de saída
    escrever_cabecalho = not os.path.exists(arquivo_saida)
    nome_instancia_limpo = dados_instancia.get('name', instancia_arg.replace('.vrp', ''))

    with open(arquivo_saida, "a") as arquivo:
        if escrever_cabecalho:
            arquivo.write(f"{'INSTANCE':<15} {'METHOD':<15} {'OBJECTIVE':<15} {'RUNTIME':<15} {'GAP':<15}\n")

        arquivo.write(f"{nome_instancia_limpo:<15} {heuristica:<15} {custo_total:<15.2f} {runtime:<15.2f} {gap:<15.2f}\n")

    nome_imagem = f"{heuristica}/{nome_instancia_limpo}.png"
    utils.plotar_rotas(dados_instancia, rotas, nome_imagem)

if __name__ == "__main__":
    main()