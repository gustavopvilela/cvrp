import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def gerar_boxplot_gaps (gaps_mj, gaps_cw, gaps_gm):
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

def gerar_grafico_barras_runtime (runtime_mj, runtime_cw, runtime_gm):
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

def gerar_intervalo_confianca (gaps_mj, gaps_cw, gaps_gm):
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

if __name__ == '__main__':
    gaps_mole_jameson = [
        8.530913216,
        19.82877816,
        24.44892221,
        86.38818565,
        20.90189329,
        18.12817109,
        10.9332449,
        32.40945597,
        2.734162042,
        25.37339901,
        17.31480768,
        15.39972446,
        4.042411811,
        17.76320193,
        8.590327208
    ]
    gaps_clark_wright = [
        5.55530346,
        1.756635742,
        6.754451734,
        40.52320675,
        4.932874355,
        16.81790904,
        13.04754153,
        21.13992437,
        2.932406655,
        12.35665025,
        5.990766512,
        13.55960931,
        3.72410655,
        19.77714646,
        7.231504884
    ]
    gaps_gillet_miller = [
        27.54566081,
        16.52756385,
        32.51452671,
        62.42194093,
        49.39500861,
        7.503409773,
        12.80938169,
        13.02857058,
        19.50378336,
        27.70541872,
        46.21914684,
        51.75407456,
        6.384277584,
        41.17839297,
        25.71127809
    ]

    runtime_mole_jameson = [
        0,
        0.04,
        0.01,
        0.01,
        0.03,
        0.62,
        0.12,
        1.59,
        0.69,
        0.02,
        0.02,
        0.24,
        0.44,
        2.54,
        24.66
    ]
    runtime_clark_wright = [
        0.00,
        0.01,
        0.00,
        0.00,
        0.01,
        0.05,
        0.03,
        0.10,
        0.17,
        0.01,
        0.01,
        0.05,
        0.10,
        1.60,
        4.11
    ]
    runtime_gillet_miller = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.01,
        0.0,
        0.02,
        0.01,
        0.0,
        0.0,
        0.0,
        0.01,
        0.04,
        0.06
    ]

    gerar_boxplot_gaps(gaps_mole_jameson, gaps_clark_wright, gaps_gillet_miller)
    gerar_grafico_barras_runtime(runtime_mole_jameson, runtime_clark_wright, runtime_gillet_miller)
    gerar_intervalo_confianca(gaps_mole_jameson, gaps_clark_wright, gaps_gillet_miller)

