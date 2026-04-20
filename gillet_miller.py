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


    # Calcula o ângulo polar de cada cliente em relaçao ao deposito
    def calcular_angulos(self):
        deposito_x, deposito_y = self.nos[self.deposito]
        clientes_angulos = []

        for no_id, (x, y) in self.nos.items():
            if no_id == self.deposito: continue
            angulo = math.atan2(y - deposito_y, x - deposito_x)
            clientes_angulos.append((angulo, no_id))

        # Ordena a lista pelo ângulo, criando a ordem de varredura
        clientes_angulos.sort()
        return clientes_angulos


    # Calcula o custo da distancia total percorrida por todas as rotas
    def calcula_custo(self):
        custo = 0.0
        for rota in self.rotas:
            if not rota: continue
            # custo depósito ate o primeiro cliente
            custo += self.matriz_distancias[self.deposito][rota[0]]
            # custo entre os clientes da rota
            for i in range(len(rota) - 1):
                custo += self.matriz_distancias[rota[i]][rota[i + 1]]
            # custo do ultimo cliente voltando pra rota
            custo += self.matriz_distancias[rota[-1]][self.deposito]
        return custo

    # Busca local 2-opt
    def dois_opt(self, rota_cluster):
        # Se a rota tem 1 ou 2 clientes entao nao tem o que otimizar com dois_opt
        if len(rota_cluster) <= 2:
            return rota_cluster

        rota = [self.deposito] + rota_cluster + [self.deposito]
        melhoria = True

        # Itera até que nenhuma troca melhore o custo da rota mais
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
                    #custo se inverter o caminho:
                    custo_novo = self.matriz_distancias[no_i_ant][no_j] + self.matriz_distancias[no_i][no_j_prox]

                    # Usa - 1e-6 que é um valor mto pequeno como tolerancia pra evitar problema de ponto flutuante
                    if custo_novo < custo_atual - 1e-6:
                        rota[i:j + 1] = reversed(rota[i:j + 1])
                        melhoria = True

        return rota[1:-1]

    # Foi adaptado do livro do Goldbarg e Luna "Otimização Combinatória e Programação Linear"
    def gillet_miller(self):
        # Pega a ordem polar dos clientes em relação ao deposito
        clientes_ordenados = self.calcular_angulos()

        # clientes que nao foram roteados ainda
        F = [cliente_id for angulo, cliente_id in clientes_ordenados]
        self.rotas = []

        while len(F) > 0:
            rota_atual = []
            carga_atual = 0

            # Vai guardar quem NÃO couber no caminhão
            clientes_que_sobraram = []

            # Agrupar:
            for xs in F:
                demanda_xs = self.demandas[xs]

                if carga_atual + demanda_xs <= self.capacidade:
                    rota_atual.append(xs)
                    carga_atual += demanda_xs
                else:
                    # Se não cabe guarda pro prox caminhão
                    clientes_que_sobraram.append(xs)

            # Atualiza F para conter apenas os clientes que não couberam nesta rota
            F = clientes_que_sobraram

            # Chama 2-opt
            rota_otimizada = self.dois_opt(rota_atual)
            self.rotas.append(rota_otimizada)

        self.custo_total = self.calcula_custo()

        # Como Gillet Miller não prevê limite de frota, penalizei o custo se a quantidade ultrapassar K
        veiculos_usados = len(self.rotas)
        veiculos_disponiveis = self.dados.get('trucks', veiculos_usados)

        if type(veiculos_disponiveis) == int and veiculos_usados > veiculos_disponiveis:
            rotas_extras = veiculos_usados - veiculos_disponiveis
            penalidade = rotas_extras * (self.custo_total / veiculos_usados) * 1.5;
            self.custo_total += penalidade

        return self.rotas, self.custo_total