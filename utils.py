import math
import os
import matplotlib.pyplot as plt

def distancia_euclidiana (coord1, coord2):
    dx = coord1[0] - coord2[0]
    dy = coord1[1] - coord2[1]
    return math.sqrt(dx**2 + dy**2)

def ler_instancia (instancia):
    dados_instancia = {
        'name': '',
        'dimension': 0,
        'capacity': 0,
        'nodes': {}, # Formato: {ID: (x, y)}
        'demands': {}, # Formato: {ID: demanda}
        'depot': 1
    }

    secao_atual = None

    with open(instancia, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha == "EOF":
                continue

            if linha.startswith("NODE_COORD_SECTION"):
                secao_atual = "COORD"
                continue
            elif linha.startswith("DEMAND_SECTION"):
                secao_atual = "DEMAND"
                continue
            elif linha.startswith("DEPOT_SECTION"):
                secao_atual = "DEPOT"
                continue

            # Leitura do cabeçalho do arquivo
            if secao_atual is None:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip()
                    valor = valor.strip()

                    if chave == "NAME": dados_instancia['name'] = valor
                    elif chave == "DIMENSION": dados_instancia['dimension'] = int(valor)
                    elif chave == "CAPACITY": dados_instancia['capacity'] = int(valor)

            # Leitura das coordenadas
            elif secao_atual == "COORD":
                partes = linha.split()
                no_id = int(partes[0])
                x, y = float(partes[1]), float(partes[2])
                dados_instancia['nodes'][no_id] = (x, y)

            # Leitura das demandas
            elif secao_atual == "DEMAND":
                partes = linha.split()
                no_id = int(partes[0])
                demanda = int(partes[1])
                dados_instancia['demands'][no_id] = demanda

            # Leitura do depósito
            elif secao_atual == "DEPOT":
                valor = int(linha.strip())
                if valor != -1: dados_instancia['depot'] = valor

        # Calculando matriz de distâncias dos nós
        matriz_distancias = {}
        nos = dados_instancia['nodes']
        for i in nos:
            matriz_distancias[i] = {}
            for j in nos:
                if i == j: matriz_distancias[i][j] = 0.0
                else:
                    matriz_distancias[i][j] = distancia_euclidiana(nos[i], nos[j])

        # Adicionando os caminhões manualmente pois não há forma padronizada de consegui-los no arquivo
        trucks = {
            'instances/A-n80-k10.vrp': 10,
            'instances/CMT10.vrp': 18,
            'instances/E-n101-k14.vrp': 14,
            'instances/F-n72-k4.vrp': 7,
            'instances/F-n135-k7.vrp': 4,
            'instances/Golden_3.vrp': 27,
            'instances/Golden_18.vrp': 9,
            'instances/Li_21.vrp': 10,
            'instances/Loggi-n601-k42.vrp': 42,
            'instances/M-n151-k12.vrp': 12,
            'instances/tai150b.vrp': 14,
            'instances/tai385.vrp': 46,
            'instances/X-n502-k39.vrp': 39,
            'instances/XL-n1701-k562.vrp': 562,
            'instances/XL-n2541-k121.vrp': 121
        }

        dados_instancia['distance_matrix'] = matriz_distancias
        dados_instancia['trucks'] = trucks[instancia]

        return dados_instancia

def plotar_rotas (dados_instancia, rotas, arquivo_saida="rotas_cvrp.png"):
    nos = dados_instancia['nodes']
    deposito = dados_instancia['depot']
    coordenadas_deposito = nos[deposito]

    plt.figure(figsize=(20,16))

    cores = ['red', 'green', 'blue', 'orange', 'purple', 'magenta',
             'brown', 'cyan', 'lightseagreen', 'teal', 'navy', 'gold',
             'violet', 'chocolate', 'saddlebrown', 'indianred',
             'dimgray', 'royalblue', 'mediumvioletred']

    # Plotando clientes
    cliente_x = [nos[i][0] for i in nos if i != deposito]
    cliente_y = [nos[i][1] for i in nos if i != deposito]
    plt.scatter(cliente_x, cliente_y, c='black', label='Clientes', marker='o', alpha=0.5)

    # Plotando depósito
    plt.scatter(coordenadas_deposito[0], coordenadas_deposito[1], c='black', label='Depósito', marker='s', s=100, edgecolor='none')

    # Plotando rotas
    for i, rota in enumerate(rotas):
        if not rota: continue

        caminho_completo = [deposito] + rota + [deposito]
        coordenadas_x = [nos[j][0] for j in caminho_completo]
        coordenadas_y = [nos[j][1] for j in caminho_completo]
        cor = cores[i % len(cores)]
        plt.plot(coordenadas_x, coordenadas_y, color=cor, linewidth=2, linestyle='-')

    plt.title(f"Rotas da instância {dados_instancia['name']}")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.5)

    pasta = arquivo_saida.split("/")[0]
    if not os.path.exists(pasta): os.makedirs(pasta)
    plt.savefig(arquivo_saida)
    plt.close()
    print(f"Gráfico da instância {dados_instancia['name']} salvo em {arquivo_saida}")