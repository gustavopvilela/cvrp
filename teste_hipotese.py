import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import stats
import scikit_posthocs as sp

def comparar_heuristicas(gaps_mj, gaps_cw, gaps_gm):
    dados = np.array([gaps_mj, gaps_cw, gaps_gm]).T
    nomes = ['MJ', 'CW', 'GM']

    sns.set_theme(style="white", font_scale=1.1)
    stat, p_value = stats.friedmanchisquare(*dados.T)

    fig, ax = plt.subplots(figsize=(8, 6))
    titulo_friedman = f"Teste de Friedman\nEstatística: {stat:.3f} | p-value: {p_value:.4e}"

    if p_value < 0.05:
        # Teste de Nemenyi
        resultado_nemenyi = sp.posthoc_nemenyi_friedman(dados)
        resultado_nemenyi.columns = nomes
        resultado_nemenyi.index = nomes
        mask = np.triu(np.ones_like(resultado_nemenyi, dtype=bool))
        sns.heatmap(resultado_nemenyi, annot=True, mask=mask, cmap="Blues",
                    vmin=0, vmax=1, cbar_kws={'label': 'p-value'},
                    linewidths=1, ax=ax, fmt=".3f", square=True)

        plt.title(f"Teste Post-Hoc de Nemenyi (Matriz de p-values)\n\n{titulo_friedman}",
                  pad=15, fontweight='bold')

    plt.tight_layout()
    nome_arquivo = 'resultado_testes_estatisticos.png'
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"-> Imagem dos testes estatísticos salva como: {nome_arquivo}")

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

def comparar_buscas_locais(gaps_shift, gaps_2opt, gaps_swap):
    dados = np.array([gaps_shift, gaps_2opt, gaps_swap]).T
    nomes = ['Shift', '2-Opt', 'Swap']

    sns.set_theme(style="white", font_scale=1.1)
    stat, p_value = stats.friedmanchisquare(*dados.T)

    fig, ax = plt.subplots(figsize=(8, 6))
    titulo_friedman = f"Teste de Friedman\nEstatística: {stat:.3f} | p-value: {p_value:.4e}"

    if p_value < 0.05:
        # Teste de Nemenyi (só faz sentido se Friedman apontar diferença p < 0.05)
        resultado_nemenyi = sp.posthoc_nemenyi_friedman(dados)
        resultado_nemenyi.columns = nomes
        resultado_nemenyi.index = nomes
        mask = np.triu(np.ones_like(resultado_nemenyi, dtype=bool))
        sns.heatmap(resultado_nemenyi, annot=True, mask=mask, cmap="Blues",
                    vmin=0, vmax=1, cbar_kws={'label': 'p-value'},
                    linewidths=1, ax=ax, fmt=".3f", square=True)

        plt.title(f"Teste Post-Hoc de Nemenyi (Matriz de p-values)\n\n{titulo_friedman}",
                  pad=15, fontweight='bold')
    else:
        # Se não houver diferença estátistica, plota apenas um aviso
        ax.text(0.5, 0.5, f"Não houve diferença estatística significativa\n{titulo_friedman}",
                ha='center', va='center', fontsize=12)
        ax.axis('off')

    plt.tight_layout()
    nome_arquivo = 'resultado_testes_estatisticos_bl.png'
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"-> Imagem dos testes estatísticos salva como: {nome_arquivo}")