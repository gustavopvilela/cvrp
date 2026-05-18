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
        'nodes': {},
        'demands': {},
        'depot': 1,
        'edge_weight_type': 'EUC_2D',
        'edge_weight_format': '',
        'explicit_weights': []
    }

    secao_atual = None
    with open(instancia, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha == "EOF": continue

            if linha.startswith("NODE_COORD_SECTION"):
                secao_atual = "COORD"
                continue
            elif linha.startswith("DEMAND_SECTION"):
                secao_atual = "DEMAND"
                continue
            elif linha.startswith("DEPOT_SECTION"):
                secao_atual = "DEPOT"
                continue
            elif linha.startswith("EDGE_WEIGHT_SECTION"):
                secao_atual = "EDGE_WEIGHT"
                continue

            # Cabeçalho
            if secao_atual is None:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip()
                    valor = valor.strip()

                    if chave == "NAME": dados_instancia['name'] = valor
                    elif chave == "DIMENSION": dados_instancia['dimension'] = int(valor)
                    elif chave == "CAPACITY": dados_instancia['capacity'] = int(valor)
                    elif chave == "EDGE_WEIGHT_TYPE": dados_instancia['edge_weight_type'] = valor
                    elif chave == "EDGE_WEIGHT_FORMAT": dados_instancia['edge_weight_format'] = valor
            # Coordenadas (EUC_2D)
            elif secao_atual == "COORD":
                partes = linha.split()
                no_id = int(partes[0])
                x, y = float(partes[1]), float(partes[2])
                dados_instancia['nodes'][no_id] = (x, y)
            # Demandas
            elif secao_atual == "DEMAND":
                partes = linha.split()
                no_id = int(partes[0])
                demanda = int(partes[1])
                dados_instancia['demands'][no_id] = demanda
            # Depósito
            elif secao_atual == "DEPOT":
                valor = int(linha.strip())
                if valor != -1: dados_instancia['depot'] = valor
            # Distâncias explícitas
            elif secao_atual == "EDGE_WEIGHT":
                dados_instancia['explicit_weights'].extend([float(v) for v in linha.split()])

    # Calculando a matriz de distâncias
    matriz_distancias = {}
    dimension = dados_instancia['dimension']

    if dados_instancia['edge_weight_type'] == 'EUC_2D' or (dados_instancia['nodes'] and not dados_instancia['explicit_weights']):
        nos = dados_instancia['nodes']
        for i in nos:
            matriz_distancias[i] = {}
            for j in nos:
                if i == j: matriz_distancias[i][j] = 0.0
                else: matriz_distancias[i][j] = distancia_euclidiana(nos[i], nos[j])
    elif dados_instancia['edge_weight_type'] == 'EXPLICIT':
        for i in range(1, dimension + 1):
            matriz_distancias[i] = {}
            for j in range(1, dimension + 1):
                matriz_distancias[i][j] = 0.0

        if dados_instancia['edge_weight_format'] == 'LOWER_ROW':
            pesos = dados_instancia['explicit_weights']
            idx_peso = 0

            for i in range(2, dimension + 1):
                for j in range(1, i):
                    if idx_peso < len(pesos):
                        dist = pesos[idx_peso]
                        matriz_distancias[i][j] = dist
                        matriz_distancias[j][i] = dist
                        idx_peso += 1

    del dados_instancia['explicit_weights']

    # Adicionando os caminhões manualmente
    trucks = {
        'instances/A-n80-k10.vrp': 10,
        'instances/CMT10.vrp': 18,
        'instances/E-n101-k14.vrp': 14,
        'instances/F-n72-k4.vrp': 4,
        'instances/F-n135-k7.vrp': 7,
        'instances/Golden_3.vrp': 9,
        'instances/Golden_18.vrp': 27,
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

# Transforma a lista de listas em um único vetor com todas as rotas
def encode (rotas, demandas, id_deposito=1):
    giant_tour = []
    cargas_rotas = []

    for rota in rotas:
        giant_tour.extend(rota[:-1])
        carga = sum(demandas[no] for no in rota if no != id_deposito)
        cargas_rotas.append(carga)

    if giant_tour: giant_tour.append(id_deposito)

    estado = {
        'tour': giant_tour,         # [deposito, 1, 2, deposito, 3, deposito]
        'cargas': cargas_rotas      # [45, 30]
    }

    return estado

# Transforma um único vetor em uma lista de listas para plotagem
def decode (estado, id_deposito=1):
    giant_tour = estado['tour']
    rotas_lista = []
    rota_atual = []

    for no in giant_tour:
        rota_atual.append(no)
        if no == id_deposito and len(rota_atual) > 1:
            rotas_lista.append(rota_atual)
            rota_atual = [id_deposito]

    return rotas_lista