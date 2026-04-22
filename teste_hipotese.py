import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
import scikit_posthocs as sp

def comparar_heuristicas (gaps_mj, gaps_cw, gaps_gm):
    dados = np.array([gaps_mj, gaps_cw, gaps_gm]).T

    # Teste de Friedman
    print("=== TESTE DE FRIEDMAN ===")
    stat, p_value = stats.friedmanchisquare(*dados.T)

    print(f"Estatística de teste: {stat:.6f}")
    print(f"P-value: {p_value:.10f}")

    if p_value < 0.05:
        print("=== TESTE DE NEMENYI ===")
        resultado_nemenyi = sp.posthoc_nemenyi_friedman(dados)

        resultado_nemenyi.columns = ['MJ', 'CW', 'GM']
        resultado_nemenyi.index = ['MJ', 'CW', 'GM']

        print("Matriz de p-values unificada:")
        print(resultado_nemenyi)

        print("\nConclusão de Nemenyi (alfa = 0.05):")
        if resultado_nemenyi.loc['MJ', 'GM'] < 0.05:
            print("- MJ é estatisticamente diferente de GM")
        else:
            print("- MJ e GM tiveram desempenho estatisticamente equivalente")

        if resultado_nemenyi.loc['CW', 'GM'] < 0.05:
            print("- CW é estatisticamente diferente de GM")
        else:
            print("- CW e GM tiveram desempenho estatisticamente equivalente")

        if resultado_nemenyi.loc['MJ', 'CW'] < 0.05:
            print("- MJ é estatisticamente diferente de CW")
        else:
            print("- MJ e CW tiveram desempenho estatisticamente equivalente")

def gerar_grafico_diferenca_critica (gaps_mj, gaps_cw, gaps_gm):
    dados = np.array([gaps_mj, gaps_cw, gaps_gm]).T
    ranks = np.array([stats.rankdata(linha) for linha in dados])

    rank_medio_mole_jameson = np.mean(ranks[:, 0])
    rank_medio_clark_wright = np.mean(ranks[:, 1])
    rank_medio_gillet_miller = np.mean(ranks[:, 2])

    nomes = ['Mole-Jameson', 'Clark-Wright', 'Gillet-Miller']
    medias = [rank_medio_mole_jameson, rank_medio_clark_wright, rank_medio_gillet_miller]

    fig, ax = plt.subplots(figsize=(20, 8))
    ax.hlines(1, 1, 3, color='black', linewidth=2)

    for tick in np.arange(1.0, 3.1, 0.5):
        ax.vlines(tick, 0.95, 1.05, color='black', linewidth=1.5)
        ax.text(tick, 0.85, f'{tick:.1f}', ha='center', va='top', fontsize=12)

    cores = ['#55A868', '#4C72B0', '#C44E52']
    for i, media in enumerate(medias):
        ax.plot(media, 1, 'o', markersize=15, color=cores[i], zorder=5)
        ax.text(media, 1.15, nomes[i], ha='center', va='bottom', fontsize=14, fontweight='bold', color=cores[i])

    y_pos_mj_gm = 1.6
    ax.hlines(y_pos_mj_gm, rank_medio_mole_jameson, rank_medio_gillet_miller, color='black', linewidth=4, zorder=3)
    ax.vlines([rank_medio_mole_jameson, rank_medio_gillet_miller], y_pos_mj_gm - 0.05, y_pos_mj_gm + 0.05,
              color='black', linewidth=2)
    ax.text((rank_medio_mole_jameson + rank_medio_gillet_miller) / 2, y_pos_mj_gm + 0.05, 'Empate (p=0.408)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

    y_pos_mj_cw = 1.4
    ax.hlines(y_pos_mj_cw, rank_medio_mole_jameson, rank_medio_clark_wright, color='gray', linewidth=4, zorder=3)
    ax.vlines([rank_medio_mole_jameson, rank_medio_clark_wright], y_pos_mj_cw - 0.05, y_pos_mj_cw + 0.05, color='gray',
              linewidth=2)
    ax.text((rank_medio_mole_jameson + rank_medio_clark_wright) / 2, y_pos_mj_cw + 0.05, 'Empate (p=0.161)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_title('Gráfico de Diferença Crítica (Teste de Nemenyi)', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')  # Esconde as bordas do gráfico padrão
    ax.set_ylim(0.5, 2.0)  # Ajusta o enquadramento

    plt.tight_layout()
    plt.savefig('grafico_diferenca_critica.png', dpi=300, bbox_inches='tight')
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

    comparar_heuristicas(gaps_mole_jameson, gaps_clark_wright, gaps_gillet_miller)
    gerar_grafico_diferenca_critica(gaps_mole_jameson, gaps_clark_wright, gaps_gillet_miller)


