def dois_opt(estado, matriz_distancias, id_deposito=1):
    """
    Busca local 2-Opt (intra-rotas)
    Estratégia: Best Improvement

    """
    tour = estado['tour']
    melhor_delta = 0
    melhor_movimento = None

    # Encontra os index de início e fim de cada rota dentro do giant_tour
    index_deposito = []
    for idx in range(len(tour)):
        if tour[idx] == id_deposito:
            index_deposito.append(idx)

    # Itera sobre cada rota individualmente usando os limites dos depósitos
    for k in range(len(index_deposito) - 1):
        start_idx = index_deposito[k]
        end_idx = index_deposito[k + 1]

        # Se a rota tem 2 clientes ou menos n tem arestas cruzadas para otimizar
        if end_idx - start_idx <= 2:
            continue

        # Avalia todas as combinações (i, j) possiveis dentro da rota
        for i in range(start_idx + 1, end_idx - 1):
            for j in range(i + 1, end_idx):
                no_i_ant = tour[i - 1]
                no_i = tour[i]
                no_j = tour[j]
                no_j_prox = tour[j + 1]

                custo_atual = matriz_distancias[no_i_ant][no_i] + matriz_distancias[no_j][no_j_prox]
                custo_novo = matriz_distancias[no_i_ant][no_j] + matriz_distancias[no_i][no_j_prox]

                delta_total = custo_novo - custo_atual

                # Se o ganho for melhor que o melhor encontrado até agora, salva os dados deste movimento como o melhor candidato
                if delta_total < melhor_delta - 1e-6:
                    melhor_delta = delta_total
                    melhor_movimento = {
                        'i': i,
                        'j': j,
                        'delta': delta_total
                    }

    # Se encontrou algum aprimoramento em qualquer rota, aplica a inversao
    if melhor_movimento:
        i = melhor_movimento['i']
        j = melhor_movimento['j']

        tour[i: j + 1] = reversed(tour[i: j + 1])

        estado['tour'] = tour
        estado['custo_sem_penalidade'] += melhor_movimento['delta']
        estado['custo_total'] += melhor_movimento['delta']

        return True, estado, melhor_movimento['delta']

    return False, estado, 0