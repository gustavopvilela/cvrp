# Trabalho 1 de Metaheurísticas: Heurísticas construtivas para CVRP

Este repositório contém a implementação e análise comparativa de três heurísticas fundamentais para o **Problema de Roteamento de Veículos Capacitados (CVRP)**. O objetivo é encontrar rotas otimizadas para uma frota de veículos que deve atender a um conjunto de clientes com demandas específicas, respeitando a capacidade máxima de cada veículo.

## Algoritmos implementados

O projeto explora diferentes abordagens de construção de rotas:

1.  **Clarke & Wright (Savings):** Baseado no conceito de "poupança" ao combinar duas rotas em uma. É uma das heurísticas mais conhecidas pela sua eficiência em reduzir a distância total.
2.  **Gillet & Miller (Sweep Algorithm):** Uma abordagem geométrica que utiliza coordenadas polares para agrupar clientes em setores (varredura) antes de definir a sequência de visita.
3.  **Mole & Jameson:** Uma heurística de inserção sequencial que utiliza critérios de economia e refinamento para construir rotas de forma incremental.

## Validação estatística

Para comparar o desempenho dos modelos, foi realizado um pipeline estatístico rigoroso sobre múltiplas instâncias de teste:

* **Teste de Friedman:** Utilizado para verificar se existe diferença global entre os algoritmos.
    * **P-value:** `0.00516` (Rejeita-se a hipótese nula; os modelos não são iguais).
* **Teste Post-hoc de Nemenyi (α = 0.05):** Utilizado para comparações par a par.
    * **MJ vs GM:** Desempenho equivalente (p=0.745).
    * **CW vs GM:** Diferença significativa (p=0.005).
    * **MJ vs CW:** Diferença significativa (p=0.046).

## 📂 Estrutura do Repositório

* `main.py`: Script principal para execução dos testes.
* `economiasClarkWright.py`: Implementação do algoritmo de Savings.
* `gillet_miller.py`: Implementação do algoritmo Sweep.
* `mole_jameson.py`: Implementação da heurística de inserção.
* `teste_hipotese.py`: Código para realização dos testes de Friedman e Nemenyi.
* `utils.py`: Funções auxiliares (leitura de ficheiros `.vrp`, cálculo de distâncias, etc.).
* `instances/`: Pasta contendo instâncias padrão (A, E, F, Golden, Li, Tai, X).
* `GM/`, `MJ/` e `CW/`: Pastas com as visualizações das rotas geradas.

## 🛠 Requisitos e Instalação

As principais dependências são `numpy`, `scipy` (para o Friedman) e `scikit-posthocs` (para o Nemenyi).

```bash
pip install numpy matplotlib scipy scikit-posthocs
```
