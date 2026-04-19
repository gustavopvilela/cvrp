def clarke_wright(instancia):
    demandas = instancia['demands']
    deposito = instancia['depot']
    capacidade = instancia['capacity']
    matriz_distancias = instancia['distance_matrix']

    #pega todos os IDs de clientes (ignora o depósito)
    clientes = [no for no in instancia['nodes'].keys() if no != deposito]

    #calcula economias (S_ij = C_0i + C_0j - C_ij)
    economias = []
    for i in range(len(clientes)):
        for j in range(i + 1, len(clientes)):
            c1 = clientes[i]
            c2 = clientes[j]
            economia = matriz_distancias[deposito][c1] + matriz_distancias[deposito][c2] - matriz_distancias[c1][c2]
            economias.append((economia, c1, c2))

    #ordenar em ordem decrescente (as maiores economias primeiro)
    economias.sort(key=lambda x: x[0], reverse=True)

    #inicializa rotas (cada cliente em sua própria rota isolada)
    rotas = [[c] for c in clientes]
    #atribui cada rota ao seu indice, ex.: {2: 0, 3: 1, 4: 2, 5: 3}
    cliente_rota = {c: i for i, c in enumerate(clientes)}
    carga_rota = [demandas[c] for c in clientes]

    #fase de mesclagem (regras de Clarke & Wright)
    for economia, c1, c2 in economias:
        idx_rota_1 = cliente_rota[c1]
        idx_rota_2 = cliente_rota[c2]

        #regra 1: precisam estar em rotas distintas
        if idx_rota_1 == idx_rota_2:
            continue

        #regra 2: a união não pode ultrapassar a capacidade Q do veículo
        if carga_rota[idx_rota_1] + carga_rota[idx_rota_2] > capacidade:
            continue

        rota_1 = rotas[idx_rota_1]
        rota_2 = rotas[idx_rota_2]

        #regra 3: os nós precisam estar nas extremidades das suas rotas
        is_c1_extremo = (c1 == rota_1[0] or c1 == rota_1[-1])
        is_c2_extremo = (c2 == rota_2[0] or c2 == rota_2[-1])

        if is_c1_extremo and is_c2_extremo:
            #garantir o alinhamento correto das listas para a fusão
            if c1 == rota_1[0]: rota_1.reverse()
            if c2 == rota_2[-1]: rota_2.reverse()

            #efetivar a mesclagem
            nova_rota = rota_1 + rota_2
            rotas[idx_rota_1] = nova_rota
            rotas[idx_rota_2] = []  # Esvazia a rota que foi absorvida

            #atualizar as cargas
            carga_rota[idx_rota_1] += carga_rota[idx_rota_2]
            carga_rota[idx_rota_2] = 0

            #atualizar os ponteiros de qual rota os clientes estão agora
            for c in rota_2:
                cliente_rota[c] = idx_rota_1

    #finalização e cálculo do custo da função objetivo
    rotas_finais = []
    custo_total = 0.0

    for rota in rotas:
        if rota:  #caso a rota não esteja vazia
            #ida: do depósito até o primeiro cliente
            custo_rota = matriz_distancias[deposito][rota[0]]

            #caminho entre os clientes
            for k in range(len(rota) - 1):
                custo_rota += matriz_distancias[rota[k]][rota[k + 1]]

            #volta: do último cliente para o depósito
            custo_rota += matriz_distancias[rota[-1]][deposito]

            custo_total += custo_rota
            #guardamos a rota apenas com os clientes
            rotas_finais.append(rota)

    #caso aqtd de caminhões ultrapasse o limite
    veiculos_usados = len(rotas_finais)
    veiculos_disponiveis = instancia.get('trucks', veiculos_usados)

    if isinstance(veiculos_disponiveis, int) and veiculos_disponiveis > 0:
        custo_medio_rota = custo_total / veiculos_usados
        alfa = custo_medio_rota * 0.3  #punição por caminhão que sobrou
        beta = custo_medio_rota * 1.5  #punição por caminhão extra

        veiculos_sobraram = max(0, veiculos_disponiveis - veiculos_usados)
        veiculos_faltaram = max(0, veiculos_usados - veiculos_disponiveis)

        penalidade = (alfa * veiculos_sobraram) + (beta * veiculos_faltaram)

        custo_total += penalidade

    return rotas_finais, custo_total