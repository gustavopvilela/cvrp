import math

class GilletMiller:
    def __init__(self, dados_instancia):
        self.dados = dados_instancia
        self.capacidade = dados_instancia['capacity']
        self.demandas = dados_instancia['demands']
        self.deposito = dados_instancia['depot']
        self.nos = dados_instancia['nodes']
        self.matriz_distancias = dados_instancia['distance_matrix']

        self.rotas = []
        self.custo_total = 0.0

    def calcular_angulos(self):
        deposito_x, deposito_y = self.nos[self.deposito]
        clientes_angulos = []

        for no_id, (x, y) in self.nos.items():
            if no_id == self.deposito: continue
            angulo = math.atan2(y - deposito_y, x - deposito_x)
            clientes_angulos.append((angulo, no_id))

        clientes_angulos.sort()
        return clientes_angulos

    def calcula_custo(self):
        custo = 0.0
        for rota in self.rotas:
            if not rota: continue
            custo += self.matriz_distancias[self.deposito][rota[0]]
            for i in range(len(rota) - 1):
                custo += self.matriz_distancias[rota[i]][rota[i + 1]]
            custo += self.matriz_distancias[rota[-1]][self.deposito]
        return custo

    def k_otimo(self, rota_cluster):
        #se a rota tem 1 ou 2 clientes entao nao tem o que otimizar com k-otimo
        if len(rota_cluster) <= 2:
            return rota_cluster

        rota = [self.deposito] + rota_cluster + [self.deposito]
        melhoria = True

        while melhoria:
            melhoria = False
            # Percorre todas as combinações de duas arestas para quebrar e reconectar
            for i in range(1, len(rota) - 2):
                for j in range(i + 1, len(rota) - 1):
                    no_i_ant = rota[i - 1]
                    no_i = rota[i]
                    no_j = rota[j]
                    no_j_prox = rota[j + 1]

                    #custo:
                    custo_atual = self.matriz_distancias[no_i_ant][no_i] + self.matriz_distancias[no_j][no_j_prox]
                    #custo se ineverter o caminho:
                    custo_novo = self.matriz_distancias[no_i_ant][no_j] + self.matriz_distancias[no_i][no_j_prox]

                    if custo_novo < custo_atual - 1e-6:
                        rota[i:j + 1] = reversed(rota[i:j + 1])
                        melhoria = True

        return rota[1:-1]

    def gillet_miller(self):
        clientes_ordenados = self.calcular_angulos()

        #F := N \ {x1} (Lista de clientes q n foram roteados ainda)
        F = [cliente_id for angulo, cliente_id in clientes_ordenados]
        self.rotas = []

        #Enquanto F != vazio
        while len(F) > 0:
            rota_atual = []
            carga_atual = 0
            clientes_para_remover = []

            #agrupar:
            for xs in F:
                demanda_xs = self.demandas[xs]

                if carga_atual + demanda_xs <= self.capacidade:
                    rota_atual.append(xs)
                    carga_atual += demanda_xs
                    clientes_para_remover.append(xs)

            #F := F \ {xs}
            for xs in clientes_para_remover:
                F.remove(xs)

            #chama k-otimo:
            rota_otimizada = self.k_otimo(rota_atual)
            self.rotas.append(rota_otimizada)

        self.custo_total = self.calcula_custo()

        return self.rotas, self.custo_total