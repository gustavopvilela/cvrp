"""
Busca local lexicográfica com vizinhança de realocação (shift inter-rotas)
Estratégia: best improvement
"""
def busca_lexicografica (estado, matriz_distancias, demandas, capacidade, id_deposito=1):
    tour = estado['tour']
    cargas = estado['cargas']

    custo_base_atual = estado.get('custo_sem_penalidade', estado['custo_total'])
    veiculos_disponiveis = estado.get('veiculos_disponiveis', 0)

    veiculos_atuais = contar_veiculos_ativos(tour, id_deposito)
    penalidade_atual = calcular_penalidade(custo_base_atual, veiculos_atuais, veiculos_disponiveis)
    custo_total_atual = custo_base_atual + penalidade_atual

    melhor_delta = 0
    melhor_movimento = None
    caminhao_origem = 0

    # Percorre o vetor de rotas para selecionar o nó a remover
    for i in range(1, len(tour) - 1):
        if tour[i] == id_deposito:
            caminhao_origem += 1
            continue

        no_cliente = tour[i]
        demanda_cliente = demandas[no_cliente]
        no_anterior_origem = tour[i - 1]
        no_proximo_origem = tour[i + 1]

        delta_remocao = matriz_distancias[no_anterior_origem][no_proximo_origem] - (matriz_distancias[no_anterior_origem][no_cliente] + matriz_distancias[no_cliente][no_proximo_origem])
        caminhao_destino = 0

        # Percorre o vetor para encontrar a posição de inserção
        for j in range(len(tour) - 1):
            if tour[j] == id_deposito and j > 0:
                caminhao_destino += 1

            # Não permite que se faça a troca intra-rotas, somente inter-rotas
            if caminhao_origem == caminhao_destino: continue
            if cargas[caminhao_destino] + demanda_cliente > capacidade: continue

            no_anterior_destino = tour[j]
            no_proximo_destino = tour[j + 1]
            delta_insercao = (matriz_distancias[no_anterior_destino][no_cliente] + matriz_distancias[no_cliente][no_proximo_destino]) - matriz_distancias[no_anterior_destino][no_proximo_destino]

            delta_base = delta_remocao + delta_insercao
            custo_base_vizinho = custo_base_atual + delta_base
            veiculos_vizinho = veiculos_atuais

            if no_anterior_origem == id_deposito and no_proximo_origem == id_deposito:
                veiculos_vizinho -= 1

            if no_anterior_destino == id_deposito and no_proximo_destino == id_deposito:
                veiculos_vizinho += 1

            penalidade_vizinho = calcular_penalidade(custo_base_vizinho, veiculos_vizinho, veiculos_disponiveis)
            custo_total_vizinho = custo_base_vizinho + penalidade_vizinho

            delta_total = custo_total_vizinho - custo_total_atual

            # Se encontrar mudança que melhore a rota
            if delta_total < melhor_delta:
                melhor_delta = delta_total
                melhor_movimento = {
                    'index_remocao': i,
                    'index_insercao': j, # Insere-se o nó após o índice j
                    'caminhao_origem': caminhao_origem,
                    'caminhao_destino': caminhao_destino,
                    'no_cliente': no_cliente,
                    'demanda': demanda_cliente,
                    'custo_base_vizinho': custo_base_vizinho,
                    'custo_total_vizinho': custo_total_vizinho,
                    'delta_total': delta_total
                }

    if melhor_movimento:
        index_remocao = melhor_movimento['index_remocao']
        index_insercao = melhor_movimento['index_insercao']
        no = melhor_movimento['no_cliente']

        cargas[melhor_movimento['caminhao_origem']] -= melhor_movimento['demanda']
        cargas[melhor_movimento['caminhao_destino']] += melhor_movimento['demanda']

        tour.pop(index_remocao)

        # Se o índice de inserção estava à frente do de remoção, o pop()
        # anterior recuou todos os elementos à direita em uma podição, é
        # necessário ajustar
        if index_insercao >= index_remocao:
            index_insercao -= 1

        tour.insert(index_insercao + 1, no)

        estado['tour'] = tour
        estado['cargas'] = cargas
        estado['custo_sem_penalidade'] = melhor_movimento['custo_base_vizinho']
        estado['custo_total'] = melhor_movimento['custo_total_vizinho']

        return True, estado, melhor_movimento['delta_total']

    return False, estado, 0

def calcular_penalidade (custo_base, veiculos_usados, veiculos_disponiveis):
    if not isinstance(veiculos_disponiveis, int) or veiculos_disponiveis <= 0:
        return 0
    if veiculos_usados == 0: return 0

    custo_medio_rota = custo_base / veiculos_usados
    alfa = custo_medio_rota * 0.3
    beta = custo_medio_rota * 1.5

    veiculos_sobraram = max(0, veiculos_disponiveis - veiculos_usados)
    veiculos_faltaram = max(0, veiculos_usados - veiculos_disponiveis)

    return (alfa * veiculos_sobraram) + (beta * veiculos_faltaram)

def contar_veiculos_ativos (tour, deposito_id=1):
    usados = 0
    for i in range(len(tour) - 1):
        if tour[i] == deposito_id and tour[i + 1] != deposito_id:
            usados += 1
    return usados