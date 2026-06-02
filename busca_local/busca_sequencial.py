"""
Busca local sequencial com vizinhança de Swap
Estratégia: Next-Improvement
"""

def busca_sequencial(estado, matriz_distancias, demandas, capacidade, id_deposito=1):
    tour = estado['tour']
    cargas = estado['cargas']

    #o número de veículos nuca muda, então a penalidade continua igual
    custo_base_atual = estado.get('custo_sem_penalidade', estado['custo_total'])

    #acumulando os resultados de uma passada inteira pelo mapa
    houve_melhoria_nessa_passada = False
    delta_acumulado = 0.0
    caminhao_i = 0

    #percorre o tour gigante buscando o primeiro nó da troca
    #vai de 1 ate len(tour)-2 pra ignorar os depositos que ficam nas extremidades
    for i in range(1, len(tour) - 2):
        #se tem um deposito no caminho é pq a rota do caminhão acabou e começa a do proximo
        if tour[i] == id_deposito:
            caminhao_i += 1
            continue

        no_i = tour[i]
        ant_i = tour[i - 1]
        prox_i = tour[i + 1]

        #calcula a média do custo das arestas que ligam o cliente i a sua rota atual
        #para o swap dar lucro, o novo local deve ter conexões mais baratas que esse alfa calculado
        alfa = (matriz_distancias[ant_i][no_i] + matriz_distancias[no_i][prox_i]) / 2.0

        caminhao_j = caminhao_i

        #busca o segundo nó para realizar a troca com i
        #começa em i+1 ao inves de 0 pq o swap é simétricos (trocar 5 por 10 é o mesmo que trocar 10 por 5)
        for j in range(i + 1, len(tour) - 1):

            #conta a passagem para saber em qual caminhão o cliente j está
            if tour[j] == id_deposito:
                caminhao_j += 1
                continue

            no_j = tour[j]

            #evita trocar o cliente com ele mesmo
            if no_i == no_j: continue

            ant_j = tour[j - 1]
            prox_j = tour[j + 1]

            #testa se as novas arestas cruzadas seriam formadas pela troca são menores que o alfa
            #se nenhuma for menor a troca não tem como dar lucro
            if not (matriz_distancias[ant_j][no_i] < alfa or matriz_distancias[no_i][prox_j] < alfa or
                    matriz_distancias[ant_i][no_j] < alfa or matriz_distancias[no_j][prox_i] < alfa):
                continue

            #se os clientes estão no mesmo caminhão a troca não altera o peso total do veiculo, então só precisa checar a capac. se a troca for entre caminhões diferentes
            if caminhao_i != caminhao_j:
                nova_carga_i = cargas[caminhao_i] - demandas[no_i] + demandas[no_j]
                nova_carga_j = cargas[caminhao_j] - demandas[no_j] + demandas[no_i]

                #se estourar a capacidade de qualquer um dos caminhões o movimento é inválido
                if nova_carga_i > capacidade or nova_carga_j > capacidade:
                    continue

            #o delta é a diferença entre o custo das arestas a serem criadas e o custo das arestas a serem destruídas
            #existe um caso especial: j estar imediatamente após i. Se não tratar isso, poderia subtrair e somar a resta que liga i a j duas vezes
            if j == i + 1:
                custo_remocao = matriz_distancias[ant_i][no_i] + matriz_distancias[no_i][no_j] + \
                                matriz_distancias[no_j][prox_j]
                custo_insercao = matriz_distancias[ant_i][no_j] + matriz_distancias[no_j][no_i] + \
                                 matriz_distancias[no_i][prox_j]
            else:
                custo_remocao = matriz_distancias[ant_i][no_i] + matriz_distancias[no_i][prox_i] + \
                                matriz_distancias[ant_j][no_j] + matriz_distancias[no_j][prox_j]
                custo_insercao = matriz_distancias[ant_i][no_j] + matriz_distancias[no_j][prox_i] + \
                                 matriz_distancias[ant_j][no_i] + matriz_distancias[no_i][prox_j]

            delta = custo_insercao - custo_remocao

            #FIRST-IMPROVEMENT
            #se o delta for negativo significa que a distancia total da rota diminuiu e gerou luvro
            if delta < -0.0001: #usa-se -0.0001 como margem de segurança devido a imprecisões de ponto flutuante no pythin
                #aplica a troca física no array
                tour[i], tour[j] = tour[j], tour[i]

                #se a troca foi entre caminhões diferentes atualiza o vetor de pesos
                if caminhao_i != caminhao_j:
                    cargas[caminhao_i] = nova_carga_i
                    cargas[caminhao_j] = nova_carga_j

                delta_acumulado += delta
                houve_melhoria_nessa_passada = True

                break

    if houve_melhoria_nessa_passada:
        estado['tour'] = tour
        estado['cargas'] = cargas
        estado['custo_sem_penalidade'] += delta_acumulado
        estado['custo_total'] += delta_acumulado

        return True, estado, delta_acumulado

    #se varreu o array inteiro e não achou nada, o algoritmo chegou no Ótimo Local
    return False, estado, 0