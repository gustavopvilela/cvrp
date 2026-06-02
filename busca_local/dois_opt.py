def dois_opt_intra_rota(estado, matriz_distancias, id_deposito=1):
    """
    Busca local 2-Opt (intra-rotas)
    Estratégia: Best Improvement
    """
    tour = estado['tour']
    melhor_delta = 0
    melhor_movimento = None

    index_deposito = [idx for idx, val in enumerate(tour) if val == id_deposito]

    for k in range(len(index_deposito) - 1):
        start_idx = index_deposito[k]
        end_idx = index_deposito[k + 1]

        if end_idx - start_idx <= 2:
            continue

        for i in range(start_idx + 1, end_idx - 1):
            for j in range(i + 1, end_idx):
                no_i_ant, no_i = tour[i - 1], tour[i]
                no_j, no_j_prox = tour[j], tour[j + 1]

                custo_atual = matriz_distancias[no_i_ant][no_i] + matriz_distancias[no_j][no_j_prox]
                custo_novo = matriz_distancias[no_i_ant][no_j] + matriz_distancias[no_i][no_j_prox]
                delta_total = custo_novo - custo_atual

                if delta_total < melhor_delta - 1e-6:
                    melhor_delta = delta_total
                    melhor_movimento = {'i': i, 'j': j, 'delta': delta_total}

    if melhor_movimento:
        i, j = melhor_movimento['i'], melhor_movimento['j']
        tour[i: j + 1] = reversed(tour[i: j + 1])
        estado['tour'] = tour
        estado['custo_sem_penalidade'] += melhor_movimento['delta']
        estado['custo_total'] += melhor_movimento['delta']
        return True, estado, melhor_movimento['delta']

    return False, estado, 0

def dois_opt_inter_rota(estado, matriz_distancias, demandas, capacidade, id_deposito=1):
    """
    Busca local 2-Opt* (inter-rotas - Tail Swap)
    Estratégia: Best Improvement com cálculo de penalidade e carga.
    """
    tour = estado['tour']
    cargas = estado['cargas']
    custo_base_atual = estado.get('custo_sem_penalidade', estado['custo_total'])
    veiculos_disponiveis = estado.get('veiculos_disponiveis', 0)

    veiculos_atuais = contar_veiculos_ativos(tour, id_deposito)
    penalidade_atual = calcular_penalidade(custo_base_atual, veiculos_atuais, veiculos_disponiveis)
    custo_total_atual = custo_base_atual + penalidade_atual

    melhor_delta = 0
    melhor_movimento = None

    index_deposito = [idx for idx, val in enumerate(tour) if val == id_deposito]

    for r1 in range(len(index_deposito) - 1):
        for r2 in range(r1 + 1, len(index_deposito) - 1):
            start1, end1 = index_deposito[r1], index_deposito[r1 + 1]
            start2, end2 = index_deposito[r2], index_deposito[r2 + 1]

            for i in range(start1, end1):
                for j in range(start2, end2):
                    no_i, no_i_prox = tour[i], tour[i + 1]
                    no_j, no_j_prox = tour[j], tour[j + 1]
                    demanda_tail1 = sum(demandas[tour[k]] for k in range(i + 1, end1))
                    demanda_tail2 = sum(demandas[tour[k]] for k in range(j + 1, end2))

                    carga_r1_nova = cargas[r1] - demanda_tail1 + demanda_tail2
                    carga_r2_nova = cargas[r2] - demanda_tail2 + demanda_tail1

                    if carga_r1_nova > capacidade or carga_r2_nova > capacidade:
                        continue

                    delta_base = (matriz_distancias[no_i][no_j_prox] + matriz_distancias[no_j][no_i_prox]) - \
                                 (matriz_distancias[no_i][no_i_prox] + matriz_distancias[no_j][no_j_prox])
                    custo_base_vizinho = custo_base_atual + delta_base

                    veiculos_vizinho = veiculos_atuais

                    tamanho_orig_r1 = end1 - start1
                    tamanho_orig_r2 = end2 - start2
                    tamanho_novo_r1 = (i - start1) + (end2 - j)
                    tamanho_novo_r2 = (j - start2) + (end1 - i)

                    if tamanho_orig_r1 > 1 and tamanho_novo_r1 == 1:
                        veiculos_vizinho -= 1
                    elif tamanho_orig_r1 == 1 and tamanho_novo_r1 > 1:
                        veiculos_vizinho += 1

                    if tamanho_orig_r2 > 1 and tamanho_novo_r2 == 1:
                        veiculos_vizinho -= 1
                    elif tamanho_orig_r2 == 1 and tamanho_novo_r2 > 1:
                        veiculos_vizinho += 1

                    penalidade_vizinho = calcular_penalidade(custo_base_vizinho, veiculos_vizinho, veiculos_disponiveis)
                    custo_total_vizinho = custo_base_vizinho + penalidade_vizinho

                    delta_total = custo_total_vizinho - custo_total_atual

                    if delta_total < melhor_delta - 1e-6:
                        melhor_delta = delta_total
                        melhor_movimento = {
                            'i': i, 'end1': end1, 'r1': r1, 'carga_r1_nova': carga_r1_nova,
                            'j': j, 'end2': end2, 'r2': r2, 'carga_r2_nova': carga_r2_nova,
                            'custo_base_vizinho': custo_base_vizinho,
                            'custo_total_vizinho': custo_total_vizinho,
                            'delta': delta_total
                        }

    if melhor_movimento:
        i, j = melhor_movimento['i'], melhor_movimento['j']
        end1, end2 = melhor_movimento['end1'], melhor_movimento['end2']

        cargas[melhor_movimento['r1']] = melhor_movimento['carga_r1_nova']
        cargas[melhor_movimento['r2']] = melhor_movimento['carga_r2_nova']

        # Fatiamento e reconstrução das rotas com os finais trocados
        tail1 = tour[i + 1: end1]
        tail2 = tour[j + 1: end2]

        prefix = tour[: i + 1]
        middle = tour[end1: j + 1]
        suffix = tour[end2:]

        estado['tour'] = prefix + tail2 + middle + tail1 + suffix
        estado['cargas'] = cargas
        estado['custo_sem_penalidade'] = melhor_movimento['custo_base_vizinho']
        estado['custo_total'] = melhor_movimento['custo_total_vizinho']

        return True, estado, melhor_movimento['delta']

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