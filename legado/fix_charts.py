# -*- coding: utf-8 -*-
"""Corrigir figuras 5, 6 e 8."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLORS = {
    'aoen': '#1B4332', 'clean_arch': '#E76F51', 'hexagonal': '#264653',
    '12factor': '#E9C46A', 'evolutionary': '#2A9D8F', 'arch_flow': '#F4A261',
    'sem_framework': '#BFBFBF'
}
LABELS = ["AOEN", "Clean Arch", "Hexagonal", "12-Factor", "Evolutionary", "Arch Flow", "Sem Framework"]
KEYS = ["aoen", "clean_arch", "hexagonal", "12factor", "evolutionary", "arch_flow", "sem_framework"]
C = [COLORS[k] for k in KEYS]


def fig5():
    """Barras por criterio - mais espaçadas e legíveis."""
    fig, ax = plt.subplots(1, 1, figsize=(18, 8))
    cr = ["Core\nDiferenciador", "Visao de\nMercado", "Multi-\nInterface",
          "Configura-\nbilidade", "Isolamento\nProcess.", "Consideracao\nde Custo",
          "Moneti-\nzacao", "Evolucao", "Coerencia"]
    data = {
        "aoen": [8.6, 8.9, 9.4, 7.5, 5.7, 4.4, 4.3, 8.7, 8.5],
        "clean_arch": [5.4, 4.7, 3.4, 4.1, 3.4, 2.2, 3.3, 6.9, 6.3],
        "hexagonal": [7.5, 5.9, 9.0, 5.0, 6.4, 4.6, 5.0, 8.6, 8.0],
        "12factor": [5.0, 3.4, 4.6, 5.1, 7.6, 5.0, 2.7, 7.9, 7.8],
        "evolutionary": [6.5, 5.3, 4.2, 5.4, 6.8, 5.9, 2.6, 9.0, 8.1],
        "arch_flow": [8.1, 8.0, 5.7, 6.0, 6.9, 5.8, 7.1, 8.0, 8.1],
        "sem_framework": [5.8, 7.7, 8.1, 3.5, 6.6, 6.5, 4.6, 6.6, 7.7],
    }
    x = np.arange(len(cr))
    w = 0.12
    total = len(KEYS)

    for i, (k, l) in enumerate(zip(KEYS, LABELS)):
        offset = (i - total / 2 + 0.5) * w
        bars = ax.bar(x + offset, data[k], w, label=l, color=COLORS[k],
                      edgecolor='black', linewidth=0.5)
        # Valor em cima de cada barra do AOEN
        if k == 'aoen':
            for bar, val in zip(bars, data[k]):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                        f'{val:.1f}', ha='center', va='bottom', fontsize=7,
                        fontfamily='Arial', fontweight='bold', color=COLORS['aoen'])

    ax.set_xlabel('Criterio de Avaliacao', fontsize=12, fontfamily='Arial')
    ax.set_ylabel('Nota Media (0-10)', fontsize=12, fontfamily='Arial')
    ax.set_title('Comparacao de abordagens arquiteturais por criterio (100 ideias)',
                 fontsize=14, fontfamily='Arial', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cr, fontsize=10, fontfamily='Arial')
    ax.set_ylim(0, 11)
    ax.legend(fontsize=10, ncol=7, loc='upper center', bbox_to_anchor=(0.5, -0.1),
              frameon=True, edgecolor='black')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ax.spines.values():
        s.set_linewidth(1.5)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('fig5_criterios.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig5 OK")


def fig6():
    """Scatter de eficiencia - redesenhado com clareza."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    ep = [44, 28, 30, 31, 30, 58, 32]
    lo = [4027, 5347, 4998, 1851, 3714, 6866, 1627]
    sv = [49, 4, 59, 15, 33, 55, 0]

    # Quadrantes
    ax.axhline(y=35, color='#EEEEEE', linestyle='-', linewidth=15, alpha=0.5)
    ax.axvline(x=4000, color='#EEEEEE', linestyle='-', linewidth=15, alpha=0.5)

    # Anotacoes de quadrante
    ax.text(2500, 55, 'IDEAL\nMenos codigo,\nmais endpoints', ha='center', va='center',
            fontsize=9, fontfamily='Arial', color='#228B22', fontstyle='italic', alpha=0.6)
    ax.text(6000, 25, 'INEFICIENTE\nMuito codigo,\npoucos endpoints', ha='center', va='center',
            fontsize=9, fontfamily='Arial', color='#B22222', fontstyle='italic', alpha=0.6)

    # Pontos
    for i in range(len(LABELS)):
        ax.scatter(lo[i], ep[i], s=sv[i] * 10 + 100, c=C[i],
                   edgecolors='black', linewidth=2, zorder=5, alpha=0.9)

    # Labels com posicoes manuais pra nao sobrepor
    positions = {
        0: (200, 4),     # AOEN
        1: (200, -3),    # Clean Arch
        2: (200, 3),     # Hexagonal
        3: (-100, -4),   # 12-Factor
        4: (200, -3),    # Evolutionary
        5: (100, 3),     # Arch Flow
        6: (-100, 3),    # Sem Framework
    }

    for i, l in enumerate(LABELS):
        ox, oy = positions[i]
        fw = 'bold' if i == 0 else 'normal'
        ax.annotate(f'{l}\n({sv[i]} servicos)',
                    (lo[i], ep[i]),
                    xytext=(ox, oy * 5),
                    textcoords='offset points',
                    fontsize=9, fontfamily='Arial', fontweight=fw,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=C[i], linewidth=1.5),
                    arrowprops=dict(arrowstyle='->', color=C[i], lw=1))

    ax.set_xlabel('Linhas de Codigo Funcional (menos = mais eficiente)',
                  fontsize=11, fontfamily='Arial')
    ax.set_ylabel('Endpoints de API (mais = mais funcionalidade)',
                  fontsize=11, fontfamily='Arial')
    ax.set_title('Eficiencia: funcionalidade entregue vs codigo necessario\n'
                 'Tamanho do ponto = quantidade de servicos implementados',
                 fontsize=13, fontfamily='Arial', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ax.spines.values():
        s.set_linewidth(1.5)
    ax.grid(alpha=0.2, linestyle='--')
    plt.tight_layout()
    plt.savefig('fig6_eficiencia_poc.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig6 OK")


def fig8():
    """Negocio vs tecnica - com analise do Arch Flow."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))

    lo = ["AOEN", "Arch Flow", "Sem FW", "Hexagonal", "Evolutionary", "12-Factor", "Clean Arch"]
    ko = ["aoen", "arch_flow", "sem_framework", "hexagonal", "evolutionary", "12factor", "clean_arch"]
    neg = [37, 45, 3, 9, 10, 5, 12]
    tec = [10, 14, 2, 15, 20, 12, 35]
    ratios = [3.7, 3.2, 1.5, 0.6, 0.5, 0.4, 0.3]
    co = [COLORS[k] for k in ko]

    x = np.arange(len(lo))
    w = 0.35

    bars1 = ax.bar(x - w / 2, neg, w, label='Mencoes a negocio',
                   color=co, edgecolor='black', linewidth=0.8)
    bars2 = ax.bar(x + w / 2, tec, w, label='Mencoes tecnicas',
                   color='white', edgecolor=co, linewidth=2, hatch='///')

    # Ratio acima de cada par
    for i in range(len(lo)):
        max_val = max(neg[i], tec[i])
        color = '#228B22' if ratios[i] > 1 else '#B22222'
        ax.text(x[i], max_val + 1.5, f'{ratios[i]}x',
                ha='center', va='bottom', fontsize=10, fontfamily='Arial',
                fontweight='bold', color=color)

    ax.set_xlabel('Abordagem', fontsize=11, fontfamily='Arial')
    ax.set_ylabel('Quantidade de mencoes nos READMEs', fontsize=11, fontfamily='Arial')
    ax.set_title('Orientacao a negocio vs tecnica na documentacao gerada\n'
                 '(valores acima das barras = razao negocio/tecnica)',
                 fontsize=13, fontfamily='Arial', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(lo, fontsize=10, fontfamily='Arial')
    ax.legend(fontsize=10, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ax.spines.values():
        s.set_linewidth(1.5)
    ax.set_ylim(0, 52)
    plt.tight_layout()
    plt.savefig('fig8_negocio_vs_tecnica.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig8 OK")


if __name__ == '__main__':
    fig5()
    fig6()
    fig8()
    print("\nFiguras 5, 6 e 8 corrigidas!")
