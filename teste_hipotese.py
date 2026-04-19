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

    # TODO: colocar os dados reais
    # Linha 1: CW e MJ empataram (p = 0.22)
    # ax.hlines(1.4, rank_medio_clark_wright, rank_medio_mole_jameson, color='black', linewidth=4, zorder=3)
    # ax.vlines([rank_medio_clark_wright, rank_medio_mole_jameson], 1.35, 1.45, color='black', linewidth=2)
    # ax.text((rank_medio_clark_wright + rank_medio_mole_jameson) / 2, 1.45, 'Empate (p=0.22)', ha='center', va='bottom', fontsize=10)

    # Linha 2: MJ e GM empataram (p = 0.51)
    # ax.hlines(1.6, rank_medio_mole_jameson, rank_medio_gillet_miller, color='black', linewidth=4, zorder=3)
    # ax.vlines([rank_medio_mole_jameson, rank_medio_gillet_miller], 1.55, 1.65, color='black', linewidth=2)
    # ax.text((rank_medio_mole_jameson + rank_medio_gillet_miller) / 2, 1.65, 'Empate (p=0.51)', ha='center', va='bottom', fontsize=10)

    ax.set_title('Gráfico de Diferença Crítica (Teste de Nemenyi)', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')  # Esconde as bordas do gráfico padrão
    ax.set_ylim(0.5, 2.0)  # Ajusta o enquadramento

    plt.tight_layout()
    plt.savefig('cd_diagram.png', dpi=300, bbox_inches='tight')
    print("Gráfico salvo como 'cd_diagram.png'!")
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
        89.7265838,
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
    gaps_gillet_miller = [42.19, 87.59, 15.03, 3.99, 64.28, 91.50, 28.19, 55.40, 73.19, 9.88, 34.50, 81.11, 49.99, 67.20, 12.49]

    comparar_heuristicas(gaps_mole_jameson, gaps_clark_wright, gaps_gillet_miller)
    gerar_grafico_diferenca_critica(gaps_mole_jameson, gaps_clark_wright, gaps_gillet_miller)


