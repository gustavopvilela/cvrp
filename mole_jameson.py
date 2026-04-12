class Rota:
    def __init__(self, deposito):
        self.caminho = [deposito, deposito] # A rota sempre começa e termina no depósito
        self.carga_atual = 0
        self.custo_atual = 0.0

    def consegue_inserir (self, demanda_no, capacidade):
        return self.carga_atual + demanda_no <= capacidade

    def inserir (self, no, index, demanda, custo_insercao):
        self.caminho.insert(index, no)
        self.carga_atual += demanda
        self.custo_atual += custo_insercao

    def get_arestas_para_insercao (self):
        return [
            (self.caminho[k], self.caminho[k + 1])
            for k in range(len(self.caminho) - 1)
        ]

def mole_jameson(instancia, lambda_param=1.0):
    demandas = instancia['demands']
    deposito = instancia['depot']
    capacidade = instancia['capacity']
    matriz_distancias = instancia['distance_matrix']

    clientes_sem_rota = set(instancia['nodes'].keys())
    clientes_sem_rota.remove(deposito)

    rotas = []
    custo_total = 0.0

    while clientes_sem_rota and len(rotas) < instancia['trucks']:
        # Abre um novo caminhão a partir do depósito
        rota_atual = Rota(deposito)

        # Primeiro cliente da rota: pode haver vários critérios, o escolhido foi o cliente mais longe
        no_mais_longe = max(clientes_sem_rota, key=lambda no: matriz_distancias[deposito][no])

        custo_inicial = matriz_distancias[deposito][no_mais_longe] * 2

        rota_atual.inserir(no=no_mais_longe, index=1, demanda=demandas[no_mais_longe], custo_insercao=custo_inicial)
        clientes_sem_rota.remove(no_mais_longe)

        # Construindo a rota
        while True:
            melhor_no = None
            melhor_indice_aresta = None
            melhor_custo_e = None
            melhor_sigma = -float('inf')

            # MV (Melhor Vértice) para inserir atualmente
            for no in clientes_sem_rota:
                if rota_atual.consegue_inserir(demandas[no], capacidade):
                    arestas_insercao = rota_atual.get_arestas_para_insercao()
                    melhor_custo_e_no = float('inf')
                    melhor_indice_no = None

                    for idx, aresta in enumerate(arestas_insercao):
                        custo_e = matriz_distancias[aresta[0]][no] + matriz_distancias[no][aresta[1]] - matriz_distancias[aresta[0]][aresta[1]]
                        if custo_e < melhor_custo_e_no:
                            melhor_custo_e_no = custo_e
                            melhor_indice_no = idx + 1

                    if melhor_custo_e_no != float('inf'):
                        sigma = (lambda_param * matriz_distancias[deposito][no]) - melhor_custo_e_no
                        if sigma > melhor_sigma:
                            melhor_sigma = sigma
                            melhor_no = no
                            melhor_indice_aresta = melhor_indice_no
                            melhor_custo_e = melhor_custo_e_no

            # Se o melhor nó continua None, significa que não
            # cabe mais nenhum cliente no caminhão
            if melhor_no is None:
                break
            # Caso achou, coloca na rota
            rota_atual.inserir(no=melhor_no, index=melhor_indice_aresta, demanda=demandas[melhor_no], custo_insercao=melhor_custo_e)
            clientes_sem_rota.remove(melhor_no)

        rotas.append(rota_atual.caminho)
        custo_total += rota_atual.custo_atual

    return rotas, custo_total