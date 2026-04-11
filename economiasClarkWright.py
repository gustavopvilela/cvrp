import math
import sys
import matplotlib.pyplot as plt
import time
import os
import time
import os

def ler_instancia_cvrp(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()

    dimensao = 0
    capacidade = 0
    coordenadas = {}
    demandas = {}

    secao_atual = None

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        #lendo os metadados do cabeçalho
        if linha.startswith("DIMENSION"):
            dimensao = int(linha.split(":")[-1].strip())
        elif linha.startswith("CAPACITY"):
            capacidade = int(linha.split(":")[-1].strip())

        #identificando a mudança de seções
        elif linha.startswith("NODE_COORD_SECTION"):
            secao_atual = "COORD"
        elif linha.startswith("DEMAND_SECTION"):
            secao_atual = "DEMAND"
        elif linha.startswith("DEPOT_SECTION"):
            secao_atual = "DEPOT"
        elif linha == "EOF":
            break

        #lendo os dados das seções
        elif secao_atual == "COORD":
            partes = linha.split()
            if len(partes) >= 3:
                #subtraímos 1 do ID para que o depósito (nó 1 no arquivo) seja o índice 0 no Python, facilitando o uso de listas.
                id_no = int(partes[0]) - 1
                x, y = float(partes[1]), float(partes[2])
                coordenadas[id_no] = (x, y)

        elif secao_atual == "DEMAND":
            partes = linha.split()
            if len(partes) >= 2:
                id_no = int(partes[0]) - 1
                demanda = int(partes[1])
                demandas[id_no] = demanda

    return dimensao, capacidade, coordenadas, demandas


def calcular_matriz_distancias(coordenadas, dimensao):
    #inicializa uma matriz de zeros
    matriz = [[0 for _ in range(dimensao)] for _ in range(dimensao)]

    for i in range(dimensao):
        for j in range(dimensao):
            if i != j:
                x1, y1 = coordenadas[i]
                x2, y2 = coordenadas[j]

                #o padrão TSPLIB/CVRPLIB usa a distância euclidiana arredondada para o inteiro mais próximo. Isso é vital para o cálculo do GAP!
                distancia = round(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
                matriz[i][j] = distancia

    return matriz


# --- Testando o código ate aqui ---
#dim, cap, coords, dem = ler_instancia_cvrp("A-n80-k10.vrp")
#distancias = calcular_matriz_distancias(coords, dim)
#print(f"Capacidade do veículo: {cap}")
#print(f"Demanda do cliente 7: {dem[7]}")
#print(f"Distância do depósito (0) para o cliente 1: {distancias[0][1]}")

def calcular_economias(matriz_distancias, dimensao):
    economias = []

    #o depósito é o índice 0. O loop de clientes começa no índice 1.
    for i in range(1, dimensao):
        #o j começa em i + 1 para evitar pares repetidos (ex: se já fez 1 e 2, não faz 2 e 1) e também evita fazer i = j (cliente com ele mesmo)
        for j in range(i + 1, dimensao):
            #s_ij = C(0,i) + C(0,j) - C(i,j)
            s_ij = matriz_distancias[0][i] + matriz_distancias[0][j] - matriz_distancias[i][j]

            #guardamos uma tupla com o valor da economia e os dois nós envolvidos
            economias.append((s_ij, i, j))

    #ordena a lista de economias do maior valor para o menor (decrescente)
    #a chave de ordenação (key) é o primeiro elemento da tupla (índice 0, o s_ij)
    economias.sort(key=lambda x: x[0], reverse=True)

    return economias

# --- Testando o código das economias---
#lista_economias = calcular_economias(distancias, dim)
#print("Top 5 maiores economias:")
#for i in range(5):
#    print(f"Economia de {lista_economias[i][0]} unindo nós {lista_economias[i][1]} e {lista_economias[i][2]}")


def mesclar_rotas(economias, dimensao, demandas, capacidade):
    #constrói as rotas do CVRP usando a lista ordenada de economias de Clarke e Wright.

    #Estado Inicial: cada cliente em sua própria rota (sem o depósito por enquanto)
    #ex: rotas = [[1], [2], [3], ..., [n-1]]
    rotas = [[i] for i in range(1, dimensao)]

    #estruturas de controle para performance O(1)
    #mapeia ID do cliente -> Índice da sua rota atual na lista 'rotas'
    cliente_rota = {i: i - 1 for i in range(1, dimensao)}

    #controla a soma das demandas d_i de cada rota para não exceder Q
    carga_rota = [demandas[i] for i in range(1, dimensao)]

    #Fase Gulosa: avaliar as economias
    for economia, i, j in economias:
        idx_rota_i = cliente_rota[i]
        idx_rota_j = cliente_rota[j]

        #REGRA 1: Devem estar em rotas distintas
        if idx_rota_i == idx_rota_j:
            continue

        #REGRA 2: Respeitar a capacidade Q do veículo
        if carga_rota[idx_rota_i] + carga_rota[idx_rota_j] > capacidade:
            continue

        rota_i = rotas[idx_rota_i]
        rota_j = rotas[idx_rota_j]

        #REGRA 3: Precisam estar nas extremidades das suas rotas
        #como estamos sem o depósito nas listas, as extremidades são os índices 0 e -1
        is_i_extremo = (i == rota_i[0] or i == rota_i[-1])
        is_j_extremo = (j == rota_j[0] or j == rota_j[-1])

        if is_i_extremo and is_j_extremo:
            #SUCESSO! Todas as regras passaram, vamos mesclar.
            #precisamos alinhar as rotas para que os nós 'i' e 'j' fiquem "colados".

            #se 'i' está no começo da rota_i, invertemos a rota para ele ir pro final
            if i == rota_i[0]:
                rota_i.reverse()

            #se 'j' está no final da rota_j, invertemos a rota para ele ir pro começo
            if j == rota_j[-1]:
                rota_j.reverse()

            #agora 'i' está garantidamente no final da rota_i e 'j' no começo da rota_j
            nova_rota = rota_i + rota_j

            #atualizar os controles
            rotas[idx_rota_i] = nova_rota
            rotas[idx_rota_j] = []  # Esvazia a rota j que foi absorvida

            #atualiza a capacidade acumulada
            carga_rota[idx_rota_i] += carga_rota[idx_rota_j]
            carga_rota[idx_rota_j] = 0

            #atualiza o ponteiro de todos os clientes que vieram da rota_j
            for cliente in rota_j:
                cliente_rota[cliente] = idx_rota_i

    #limpar rotas vazias e adicionar o depósito (nó 0)
    rotas_finais = []
    for rota in rotas:
        if rota:  #se a lista não estiver vazia
            rota_com_deposito = [0] + rota + [0]
            rotas_finais.append(rota_com_deposito)

    return rotas_finais


def calcular_custo_total(rotas_finais, matriz_distancias):
    custo_total = 0
    for rota in rotas_finais:
        #a rota já está no formato [0, i, j, ..., 0]
        for i in range(len(rota) - 1):
            no_atual = rota[i]
            proximo_no = rota[i + 1]
            custo_total += matriz_distancias[no_atual][proximo_no]

    return custo_total


def calcular_gap(custo_obtido, custo_otimo):
    if custo_otimo == 0:
        return 0.0  #prevenção caso o ótimo não seja passado

    gap = 100 * (abs(custo_obtido - custo_otimo) / custo_otimo)
    return round(gap, 2)


def salvar_saida_ascii(nome_arquivo_saida, instancia, metodo, custo, tempo, gap):
    #Gera o arquivo de saída tabular ASCII.
    #Usa modo 'a' (append) para ir adicionando linhas a cada nova execução.

    cabecalho = f"{'INSTANCE':<15} {'METHOD':<10} {'OBJECTIVE':<15} {'RUNTIME':<10} {'GAP':<10}\n"
    #formatando números com 2 casas decimais, conforme o padrão do exemplo
    linha = f"{instancia:<15} {metodo:<10} {custo:<15.2f} {tempo:<10.2f} {gap:<10.2f}\n"

    #verifica se o arquivo existe e se está vazio para colocar o cabeçalho
    precisa_cabecalho = not os.path.exists(nome_arquivo_saida) or os.stat(nome_arquivo_saida).st_size == 0

    with open(nome_arquivo_saida, 'a') as f:
        if precisa_cabecalho:
            f.write(cabecalho)
        f.write(linha)


def plotar_rotas(coordenadas, rotas_finais, nome_instancia):
    plt.figure(figsize=(10, 8))

    #plota todos os clientes (pontos azuis)
    x_clientes = [coordenadas[i][0] for i in coordenadas if i != 0]
    y_clientes = [coordenadas[i][1] for i in coordenadas if i != 0]
    plt.scatter(x_clientes, y_clientes, c='blue', marker='o', label='Clientes', s=30)

    #plota o depósito (ponto vermelho maior)
    x_deposito, y_deposito = coordenadas[0]
    plt.scatter([x_deposito], [y_deposito], c='red', marker='s', label='Depósito', s=100)

    #traça as rotas (linhas coloridas)
    for idx_rota, rota in enumerate(rotas_finais):
        x_rota = [coordenadas[no][0] for no in rota]
        y_rota = [coordenadas[no][1] for no in rota]

        #parâmetro zorder garante que as linhas fiquem atrás dos pontos
        plt.plot(x_rota, y_rota, linestyle='-', linewidth=1.5, zorder=1)

    #ajustes visuais finais
    plt.title(f"Roteamento CVRP - Instância: {nome_instancia}")
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(True, linestyle='--', alpha=0.5)

    #salva a imagem com o nome da instância
    nome_arquivo_png = f"{nome_instancia}.png"
    plt.savefig(nome_arquivo_png, dpi=300, bbox_inches='tight')
    plt.close()  #limpa a memória

def main():
    #captura os parâmetros da linha de comando
    #ignoramos sys.argv[0] que é o nome do próprio script
    instancia = sys.argv[1]
    arquivo_saida = sys.argv[2]
    melhor_opt = float(sys.argv[3])
    metodo = sys.argv[4]

    caminho_arquivo = f"{instancia}.vrp"  #assume que os arquivos estão na mesma pasta

    #fase de Leitura (Fora do cronômetro)
    dim, cap, coords, dem = ler_instancia_cvrp(caminho_arquivo)
    matriz_dist = calcular_matriz_distancias(coords, dim)

    #CRONÔMETRO INICIA (Apenas para o cálculo)
    inicio_tempo = time.time()

    if metodo == "CW":
        economias = calcular_economias(matriz_dist, dim)
        rotas = mesclar_rotas(economias, dim, dem, cap)
    else:
        #espaço para outras heuristicas
        rotas = []

    custo_final = calcular_custo_total(rotas, matriz_dist)

    #CRONÔMETRO PARA
    fim_tempo = time.time()
    tempo_execucao = fim_tempo - inicio_tempo

    #cálculos finais e Escrita (Fora do cronômetro)
    gap = calcular_gap(custo_final, melhor_opt)
    salvar_saida_ascii(arquivo_saida, instancia, metodo, custo_final, tempo_execucao, gap)

    plotar_rotas(coords, rotas, instancia)

    print(f"Execução concluída! Instância: {instancia} | Custo: {custo_final} | Gap: {gap}%")


if __name__ == "__main__":
    #garante que o usuário passou o número certo de parâmetros
    if len(sys.argv) == 5:
        main()
    else:
        print("Sintaxe incorreta. Use: python economiasClarkWright.py <instancia> <saida> <melhor_opt> <metodo>")