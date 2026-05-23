import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def gerar_boxplot_gaps_heuristicas_construtivas (gaps_mj, gaps_cw, gaps_gm):
    dados_completos = [gaps_mj, gaps_cw, gaps_gm]

    fig, ax = plt.subplots(figsize=(16, 12))

    bplot = ax.boxplot(dados_completos,
                       patch_artist=True,
                       tick_labels=['Mole-Jameson', 'Clark-Wright', 'Gillet-Miller'])

    cores = ['pink', 'lightblue', 'lightgreen']
    for caixa, cor in zip(bplot['boxes'], cores):
        caixa.set_facecolor(cor)

    ax.set_title('Gaps das heurísticas')
    ax.set_ylabel('Gaps (em %)')
    ax.set_xlabel('Heurísticas')
    ax.yaxis.grid(True)

    plt.savefig('grafico_boxplot_gaps.pdf', format='pdf', dpi=300)
    plt.savefig('grafico_boxplot_gaps.png', format='png', dpi=300)
    plt.show()

def gerar_grafico_barras_runtime_heuristicas_construtivas (runtime_mj, runtime_cw, runtime_gm):
    registros = [
        'A-n80-k10',
        'CMT10',
        'E-n101-k14',
        'F-n72-k4',
        'F-n135-k7',
        'Golden_3',
        'Golden_18',
        'Li_21',
        'Loggi-n601-k42',
        'M-n151-k12',
        'tai150b',
        'tai385',
        'X-n502-k39',
        'XL-1701-k562',
        'XL-n2541-k121'
    ]

    x = np.arange(len(registros))
    largura = 0.25

    fig, ax = plt.subplots(figsize=(28, 12))

    ax.bar(x - largura, runtime_mj, largura, label='Mole-Jameson', color='dodgerblue')
    ax.bar(x, runtime_cw, largura, label='Clark-Wright', color='crimson')
    ax.bar(x + largura, runtime_gm, largura, label='Gillet-Miller', color='goldenrod')

    ax.set_ylabel('Runtime (em segundos)')
    ax.set_title('Runtime das heurísticas')

    ax.set_xticks(x)
    ax.set_xticklabels(registros, rotation=45, ha='right')

    ax.legend()
    plt.tight_layout()
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle='-', alpha=0.7)

    plt.savefig('grafico_barras_runtime.pdf', format='pdf', dpi=300)
    plt.savefig('grafico_barras_runtime.png', format='png', dpi=300)
    plt.show()

def gerar_intervalo_confianca_heuristicas_construtivas (gaps_mj, gaps_cw, gaps_gm):
    dados = [gaps_mj, gaps_cw, gaps_gm]
    nomes_heuristicas = ['Mole-Jameson', 'Clark-Wright', 'Gillet-Miller']

    medias = [np.mean(amostra) for amostra in dados]

    margens_erro = []
    nivel_confianca = 0.95

    for amostra in dados:
        n = len(amostra)
        erro_padrao = stats.sem(amostra)
        valor_critico_t = stats.t.ppf((1 + nivel_confianca) / 2.0, n - 1)
        margem = erro_padrao * valor_critico_t
        margens_erro.append(margem)

    fig, ax = plt.subplots(figsize=(16, 12))

    cores = ['#55A868', '#4C72B0', '#C44E52']

    barras = ax.bar(
        nomes_heuristicas,
        medias,
        yerr=margens_erro,
        capsize=10,
        color=cores,
        edgecolor='black',
        alpha=0.85
    )

    ax.set_ylabel('Gap médio (%)', fontsize=12, fontweight='bold')
    ax.set_title('Desempenho das heurísticas (IC de 95%)', fontsize=14, fontweight='bold', pad=15)

    for barra, media in zip(barras, medias):
        altura = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura / 2,
            f'{media:.4f}%',
            ha='center',
            va='center',
            color='white',
            fontweight='bold',
            fontsize=11
        )

    ax.grid(axis='y', linestyle='-', alpha=0.7, zorder=0)
    for patch in ax.patches:
        patch.set_zorder(3)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('grafico_intervalo_confianca.pdf', format='pdf', dpi=300)
    plt.savefig('grafico_intervalo_confianca.png', format='png', dpi=300)
    plt.show()

def gerar_boxplot_gaps_busca_local (gaps_shift, gaps_bl1, gaps_bl2):
    dados_completos = [gaps_shift, gaps_bl1, gaps_bl2]

    fig, ax = plt.subplots(figsize=(16, 12))

    bplot = ax.boxplot(dados_completos,
                       patch_artist=True,
                       tick_labels=['Shift', 'Busca local 1', 'Busca local 2'])

    cores = ['pink', 'lightblue', 'lightgreen']
    for caixa, cor in zip(bplot['boxes'], cores):
        caixa.set_facecolor(cor)

    ax.set_title('Gaps das vizinhanças')
    ax.set_ylabel('Gaps (em %)')
    ax.set_xlabel('Tipos de vizinhanças')
    ax.yaxis.grid(True)

    plt.savefig('grafico_boxplot_gaps_busca_local.pdf', format='pdf', dpi=300)
    plt.savefig('grafico_boxplot_gaps_busca_local.png', format='png', dpi=300)
    plt.show()

def gerar_grafico_barras_runtime_busca_local (runtime_shift, runtime_bl1, runtime_bl2):
    registros = [
        'A-n80-k10',
        'CMT10',
        'E-n101-k14',
        'F-n72-k4',
        'F-n135-k7',
        'Golden_3',
        'Golden_18',
        'Li_21',
        'Loggi-n601-k42',
        'M-n151-k12',
        'tai150b',
        'tai385',
        'X-n502-k39',
        'XL-1701-k562',
        'XL-n2541-k121'
    ]

    x = np.arange(len(registros))
    largura = 0.25

    fig, ax = plt.subplots(figsize=(28, 12))

    ax.bar(x - largura, runtime_shift, largura, label='Shift', color='dodgerblue')
    ax.bar(x, runtime_bl1, largura, label='Busca local 1', color='crimson')
    ax.bar(x + largura, runtime_bl2, largura, label='Busca local 2', color='goldenrod')

    ax.set_ylabel('Runtime (em segundos)')
    ax.set_title('Runtime das vizinhanças')

    ax.set_xticks(x)
    ax.set_xticklabels(registros, rotation=45, ha='right')

    ax.legend()
    plt.tight_layout()
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle='-', alpha=0.7)

    plt.savefig('grafico_barras_runtime_busca_local.pdf', format='pdf', dpi=300)
    plt.savefig('grafico_barras_runtime_busca_local.png', format='png', dpi=300)
    plt.show()

def gerar_intervalo_confianca_busca_local (gaps_shift, gaps_bl1, gaps_bl2):
    dados = [gaps_shift, gaps_bl1, gaps_bl2]
    nomes_vizinhancas = ['Shift', 'Busca local 1', 'Busca local 2']

    medias = [np.mean(amostra) for amostra in dados]

    erros_inferiores = []
    erros_superiores = []
    nivel_confianca = 0.95

    for amostra, media in zip(dados, medias):
        amostra_tupla =(amostra,)
        res = stats.bootstrap(
            amostra_tupla,
            np.mean,
            confidence_level=nivel_confianca,
            method='BCa'
        )
        erro_inf = media - res.confidence_interval.low
        erro_sup = media - res.confidence_interval.high

        erros_inferiores.append(erro_inf)
        erros_superiores.append(erro_sup)

    margens_erro_assimetricas = [erros_inferiores, erros_superiores]

    fig, ax = plt.subplots(figsize=(16, 12))
    cores = ['#55A868', '#4C72B0', '#C44E52']

    barras = ax.bar(
        nomes_vizinhancas,
        medias,
        yerr=margens_erro_assimetricas,
        capsize=10,
        color=cores,
        edgecolor='black',
        alpha=0.85
    )

    ax.set_ylabel('Gap médio (%)', fontsize=12, fontweight='bold')
    ax.set_title('Desempenho das vizinhanças (IC de 95%)', fontsize=14, fontweight='bold', pad=15)

    for barra, media in zip(barras, medias):
        altura = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura / 2,
            f'{media:.4f}%',
            ha='center',
            va='center',
            color='white',
            fontweight='bold',
            fontsize=11,
        )

    ax.grid(axis='y', linestyle='-', alpha=0.7, zorder=0)
    for patch in ax.patches:
        patch.set_zorder(3)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('grafico_intervalo_confianca_busca_local.pdf', format='pdf', dpi=300)
    plt.savefig('grafico_intervalo_confianca_busca_local.png', format='png', dpi=300)
    plt.show()