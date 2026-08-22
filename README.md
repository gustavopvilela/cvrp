# Trabalho 1 de Metaheurísticas: Heurísticas construtivas e buscas locais para o problema CVRP

Implementação, execução em lote e análise estatística de métodos heurísticos para o **Problema de Roteamento de Veículos Capacitados** (*Capacitated Vehicle Routing Problem* — CVRP), desenvolvido para a disciplina de Metaheurísticas.

Dado um depósito, um conjunto de clientes com demandas conhecidas e uma frota de veículos com capacidade `Q`, o objetivo é construir um conjunto de rotas que:

* comece e termine no depósito;
* atenda cada cliente exatamente uma vez;
* nunca exceda a capacidade do veículo;
* minimize a distância total percorrida.

O projeto cobre as duas etapas clássicas de solução: **construção** de uma solução inicial viável e **refinamento** por busca local sobre vizinhanças.

---

## Visão geral do fluxo

```
instances/*.vrp
      │
      ▼
utils.ler_instancia()      → coordenadas, demandas, capacidade, matriz de distâncias
      │
      ▼
Heurística construtiva     → MJ | CW | GM          (solução inicial viável)
      │
      ▼
utils.encode()             → giant tour + cargas   (representação linear da solução)
      │
      ▼
Busca local                → BL-Shift | BL-2Opt | BS-Swap
      │
      ▼
utils.decode() ──► plot da rota (.png) + linha no arquivo de resultados (.dat)
      │
      ▼
graficos_resultados.py + teste_hipotese.py → boxplots, IC, Friedman, Nemenyi, CD
```

### Representação da solução

Internamente, as rotas são convertidas em um **giant tour**: um único vetor em que o depósito funciona como separador entre rotas (`[1, 5, 8, 1, 3, 9, 2, 1, ...]`), acompanhado do vetor de cargas por rota. Isso torna os movimentos de vizinhança inter e intra-rota uniformes e baratos de avaliar. `utils.encode()` e `utils.decode()` fazem a conversão entre lista de rotas e giant tour.

### Função objetivo e penalização

Além da distância total, o custo considera uma **penalidade sobre o número de veículos** em relação à frota disponível na instância (`trucks`):

```
custo_total = custo_base + α · (veículos ociosos) + β · (veículos excedentes)
```

com `α = 0.3 · custo_médio_por_rota` e `β = 1.5 · custo_médio_por_rota`. O peso assimétrico (`β ≫ α`) torna soluções inviáveis por excesso de veículos fortemente desencorajadas, sem impedir que a busca as explore temporariamente.

---

## Heurísticas construtivas

| Sigla | Método | Ideia central |
|-------|--------|---------------|
| `CW` | **Clarke & Wright (Savings)** | Parte de uma rota dedicada por cliente e funde pares de rotas na ordem decrescente da economia `s(i,j) = d(0,i) + d(0,j) − d(i,j)`, respeitando a capacidade. |
| `GM` | **Gillet & Miller (Sweep)** | Abordagem geométrica: converte os clientes para coordenadas polares em torno do depósito, varre angularmente formando clusters até saturar a capacidade e resolve cada cluster com vizinho mais próximo. |
| `MJ` | **Mole & Jameson** | Inserção sequencial: abre a rota no cliente mais distante do depósito e insere iterativamente o cliente que maximiza o critério `σ = λ · d(0,k) − custo_de_inserção`, escolhendo a melhor aresta de inserção. O parâmetro `λ` controla o equilíbrio entre proximidade e economia. |

Arquivos em `heuristicas_construtivas/`.

## Buscas locais

| Sigla | Vizinhança | Estratégia | Arquivo |
|-------|-----------|------------|---------|
| `BL-Shift` | **Shift (relocate)** inter e intra-rota — move um cliente para outra posição/rota | Busca lexicográfica: aplica shift inter-rotas até esgotar, depois intra-rotas | `busca_local/busca_lexicografica.py` |
| `BL-2Opt` | **2-opt** inter e intra-rota — reversão de segmentos e troca de caudas entre rotas | Busca lexicográfica com laços aninhados por tipo de movimento | `busca_local/dois_opt.py` |
| `BS-Swap` | **Swap** — troca dois clientes de posição | Busca sequencial com *next-improvement* e filtro `α` que descarta trocas sem potencial de ganho antes de avaliá-las | `busca_local/busca_sequencial.py` |

Todas operam sobre o giant tour, avaliam movimentos por **delta de custo** (sem recalcular a solução inteira) e verificam a viabilidade de capacidade antes de aceitar movimentos inter-rota. As buscas lexicográficas têm limite de 100 iterações como salvaguarda contra ciclos.

Cada combinação heurística × busca local recebe um identificador no formato `LS-<HEURÍSTICA>-<BUSCA>`, por exemplo `LS-CW-BL-2Opt`.

---

## Instalação

Requer Python 3.9+.

```bash
git clone https://github.com/gustavopvilela/cvrp.git
cd cvrp
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install numpy matplotlib scipy scikit-posthocs seaborn pandas
```

## Uso

```bash
python main.py <instância> <arquivo_saida> <ótimo_conhecido> <MÉTODO>
```

| Argumento | Descrição |
|-----------|-----------|
| `<instância>` | Nome do arquivo em `instances/` (extensão `.vrp` opcional) ou `ALL` para rodar todas |
| `<arquivo_saida>` | Arquivo `.dat` onde os resultados são acumulados (criado com cabeçalho se não existir) |
| `<ótimo_conhecido>` | Valor ótimo/BKS para cálculo do gap; use `0` quando `ALL` (a tabela interna é consultada automaticamente) |
| `<MÉTODO>` | Um método individual ou um grupo de lote |

**Métodos individuais:** `MJ`, `CW`, `GM`, `LS-{MJ,CW,GM}-BL-Shift`, `LS-{MJ,CW,GM}-BL-2Opt`, `LS-{MJ,CW,GM}-BS-Swap`

**Grupos de lote:** `ALL_H` (as três construtivas), `ALL_LS_MJ`, `ALL_LS_CW`, `ALL_LS_GM` (as três buscas locais sobre a mesma solução inicial)

### Exemplos

```bash
# Uma instância, uma heurística construtiva
python main.py A-n80-k10 resultados.dat 1763 CW

# Uma instância com refinamento por 2-opt sobre Clarke & Wright
python main.py Golden_3 resultados.dat 10997.8 LS-CW-BL-2Opt

# Todas as instâncias, todas as construtivas + gráficos + testes estatísticos
python main.py ALL resultados_construtivas.dat 0 ALL_H

# Todas as instâncias, as três buscas locais sobre a solução do Mole & Jameson
python main.py ALL resultados_mj.dat 0 ALL_LS_MJ
```

Nos modos de lote (`ALL_*`), a solução construtiva é calculada **uma única vez por instância** e reaproveitada pelas três buscas locais — garantindo comparação justa e evitando trabalho redundante.

### Saídas geradas

* **`<arquivo_saida>.dat`** — tabela com `INSTANCE`, `METHOD`, `OBJECTIVE`, `RUNTIME` e `GAP` (%).
* **`<MÉTODO>/<instância>.png`** — visualização das rotas, uma pasta por método.
* **Gráficos agregados** (apenas nos modos de lote): boxplot de gaps, barras de runtime e intervalo de confiança.
* **Testes estatísticos** (apenas nos modos de lote): matriz de p-values de Nemenyi e gráfico de diferença crítica.

O gap é calculado como `100 · |custo − ótimo| / ótimo`; instâncias sem ótimo cadastrado aparecem como `N/A`.

---

## Instâncias

`instances/` reúne 15 instâncias de benchmark públicas, de 72 a 2541 clientes, cobrindo diferentes famílias e escalas:

| Família | Instâncias |
|---------|-----------|
| Augerat A/E/F/M | `A-n80-k10`, `E-n101-k14`, `F-n72-k4`, `F-n135-k7`, `M-n151-k12` |
| Christofides | `CMT10` |
| Golden | `Golden_3`, `Golden_18` |
| Li | `Li_21` |
| Rochat & Taillard | `tai150b`, `tai385` |
| Uchoa X / XL | `X-n502-k39`, `XL-n1701-k562`, `XL-n2541-k121` |
| Loggi | `Loggi-n601-k42` |

O parser (`utils.ler_instancia`) suporta o formato TSPLIB/VRPLIB com `NODE_COORD_SECTION`, `DEMAND_SECTION`, `DEPOT_SECTION` e matrizes explícitas via `EDGE_WEIGHT_SECTION`. Os melhores valores conhecidos (BKS) estão na tabela `OTIMOS_CONHECIDOS`, em `main.py`.

---

## Metodologia de avaliação estatística

Como os gaps não seguem distribuição normal e as instâncias funcionam como blocos pareados, a comparação usa testes **não paramétricos**:

1. **Teste de Friedman** — verifica se existe diferença global entre os três métodos comparados.
2. **Post-hoc de Nemenyi** (`α = 0.05`) — se Friedman rejeita a hipótese nula, faz as comparações par a par e gera a matriz de p-values.
3. **Gráfico de diferença crítica (CD)** — ranks médios com a barra de diferença crítica, agrupando métodos estatisticamente equivalentes.

Complementarmente, `graficos_resultados.py` produz boxplots de gap, gráficos de barras de runtime e intervalos de confiança de 95% da média dos gaps.

### Resultado obtido para as heurísticas construtivas

Teste de Friedman sobre os gaps nas instâncias de benchmark:

* **p-value = `0.00516`** → rejeita-se a hipótese nula: os métodos **não** são equivalentes.

Post-hoc de Nemenyi (`α = 0.05`):

| Comparação | p-value | Conclusão |
|------------|---------|-----------|
| MJ vs GM | 0.745 | Desempenho estatisticamente equivalente |
| CW vs GM | 0.005 | Diferença significativa |
| MJ vs CW | 0.046 | Diferença significativa |

Clarke & Wright destaca-se como a construtiva de melhor qualidade média, enquanto Mole & Jameson e Gillet & Miller não se separam estatisticamente entre si.

---

## Estrutura do repositório

```
.
├── main.py                          # CLI: orquestra execuções individuais e em lote
├── utils.py                         # parser .vrp, distâncias, encode/decode, plotagem
├── graficos_resultados.py           # boxplots, barras de runtime, intervalos de confiança
├── teste_hipotese.py                # Friedman, Nemenyi e gráfico de diferença crítica
├── heuristicas_construtivas/
│   ├── economiasClarkWright.py      # Clarke & Wright (savings)
│   ├── gillet_miller.py             # Sweep (classe GilletMiller)
│   └── mole_jameson.py              # Inserção sequencial (classe Rota + mole_jameson)
├── busca_local/
│   ├── busca_lexicografica.py       # Shift inter/intra-rota + penalização
│   ├── dois_opt.py                  # 2-opt inter/intra-rota
│   └── busca_sequencial.py          # Swap com next-improvement
├── instances/                       # 15 instâncias .vrp de benchmark
├── resultados_busca_local/          # resultados e gráficos das buscas locais
└── <MÉTODO>/                        # imagens das rotas por método (GM/, MJ/, LS-CW-BL-2Opt/, ...)
```

> **Nota:** arquivos `.png`, `.pdf` e `.dat` estão no `.gitignore` — os artefatos são regenerados localmente ao executar os benchmarks.

---

## Autoria

Desenvolvido por [Gustavo Vilela](https://github.com/gustavopvilela), [Iasmim Garcia](https://github.com/iasmimgarcia) e [Patrick Costa](https://github.com/patrickncosta) como trabalho da disciplina de Metaheurísticas.
