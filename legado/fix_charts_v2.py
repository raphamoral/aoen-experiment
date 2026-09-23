# -*- coding: utf-8 -*-
"""Corrigir figuras 1, 3, 5 e 6 com cores e legenda padronizada."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

COLORS = {
    'aoen': '#1B4332', 'clean_arch': '#E76F51', 'hexagonal': '#264653',
    '12factor': '#E9C46A', 'evolutionary': '#2A9D8F', 'arch_flow': '#F4A261',
    'sem_framework': '#BFBFBF'
}
LABELS = ["AOEN", "Clean Arch", "Hexagonal", "12-Factor", "Evolutionary", "Arch Flow", "Sem Framework"]
KEYS = ["aoen", "clean_arch", "hexagonal", "12factor", "evolutionary", "arch_flow", "sem_framework"]
C = [COLORS[k] for k in KEYS]


def make_legend(ax, ncol=7, loc='upper center', bbox=(0.5, -0.1)):
    """Legenda padronizada com bolinhas coloridas."""
    handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS[k],
                       markersize=10, markeredgecolor='black', markeredgewidth=0.8,
                       label=l) for k, l in zip(KEYS, LABELS)]
    ax.legend(handles=handles, fontsize=9, ncol=ncol, loc=loc,
              bbox_to_anchor=bbox, frameon=True, edgecolor='black',
              handletextpad=0.3, columnspacing=1.0)


def fig1():
    """Fases AOEN com cores e legenda no canto inferior."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 6.5))
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-2, 4.5)
    ax.axis('off')

    pc = ['#1B4332', '#264653', '#2A9D8F', '#E9C46A']
    tc = ['white', 'white', 'white', 'black']
    phase_labels = ['VALOR', 'ALCANCE', 'ESCALA', 'CUSTO']

    phases = [
        {"x": 0.5, "y": 1.5, "w": 2.2, "h": 2.2, "t": "Fase 1", "s": "Nucleo +\nVisao de Mercado"},
        {"x": 3.2, "y": 1.5, "w": 2.2, "h": 2.2, "t": "Fase 2", "s": "Multi-Interface\nAdaptativa"},
        {"x": 5.9, "y": 1.5, "w": 2.2, "h": 2.2, "t": "Fase 3", "s": "Configuration-\nDriven"},
        {"x": 8.6, "y": 1.5, "w": 2.2, "h": 2.2, "t": "Fase 4", "s": "Isolamento de\nProcessamento"},
    ]

    for i, p in enumerate(phases):
        rect = FancyBboxPatch((p["x"], p["y"]), p["w"], p["h"],
                               boxstyle="round,pad=0.15", facecolor=pc[i],
                               edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(p["x"]+p["w"]/2, p["y"]+p["h"]-0.35, p["t"],
                ha='center', va='center', fontsize=13, fontweight='bold',
                fontfamily='Arial', color=tc[i])
        ax.text(p["x"]+p["w"]/2, p["y"]+p["h"]/2, p["s"],
                ha='center', va='center', fontsize=10, fontfamily='Arial', color=tc[i])
        ax.text(p["x"]+p["w"]/2, p["y"]+0.35, phase_labels[i],
                ha='center', va='center', fontsize=10, fontfamily='Arial',
                fontstyle='italic', color=tc[i], fontweight='bold')

    # Setas entre fases
    for i in range(3):
        xs = phases[i]["x"] + phases[i]["w"] + 0.05
        xe = phases[i+1]["x"] - 0.05
        ax.annotate("", xy=(xe, 2.6), xytext=(xs, 2.6),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=2))

    # Principio central
    ax.text(5.65, 4.2,
            'Principio: "Toda decisao arquitetural deve preservar a capacidade do sistema de evoluir"',
            ha='center', va='center', fontsize=10, fontfamily='Arial', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F0F0F0', edgecolor='black', linewidth=1.5))

    # Monetizacao
    ax.annotate("", xy=(11, 2.6), xytext=(phases[3]["x"]+phases[3]["w"]+0.05, 2.6),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=2))

    # Perguntas abaixo
    qs = ['"O que construir\ne para quem?"', '"Onde esta\no usuario?"',
          '"Como escalar\nsem deploy?"', '"Quanto custa\ncada cliente?"']
    for i, q in enumerate(qs):
        ax.text(phases[i]["x"]+phases[i]["w"]/2, 1.05, q,
                ha='center', va='center', fontsize=8, fontfamily='Arial',
                fontstyle='italic', color='#555555')

    # Legenda no canto inferior
    legend_items = []
    legend_labels_custom = ["Fase 1: Nucleo + Visao de Mercado (VALOR)",
                            "Fase 2: Multi-Interface Adaptativa (ALCANCE)",
                            "Fase 3: Configuration-Driven (ESCALA)",
                            "Fase 4: Isolamento de Processamento (CUSTO)"]
    for i in range(4):
        legend_items.append(Line2D([0], [0], marker='s', color='w',
                                    markerfacecolor=pc[i], markersize=12,
                                    markeredgecolor='black', markeredgewidth=0.8,
                                    label=legend_labels_custom[i]))

    ax.legend(handles=legend_items, fontsize=9, ncol=2, loc='lower center',
              bbox_to_anchor=(0.45, -0.15), frameon=True, edgecolor='black',
              handletextpad=0.5, columnspacing=1.5)

    plt.tight_layout()
    plt.savefig('fig1_fases_aoen.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig1 OK")


def fig3():
    """Media geral com cores e legenda com bolinhas."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))

    medias = [7.31, 4.42, 6.67, 5.44, 5.99, 7.08, 6.34]
    order = sorted(range(len(medias)), key=lambda i: medias[i])

    bars = ax.barh([LABELS[i] for i in order], [medias[i] for i in order],
                   color=[C[i] for i in order], edgecolor='black', linewidth=0.8, height=0.6)

    ax.set_xlabel('Nota Media Geral (0-10)', fontsize=12, fontfamily='Arial')
    ax.set_title('Media geral por abordagem arquitetural (100 ideias)',
                 fontsize=14, fontfamily='Arial', fontweight='bold')
    ax.set_xlim(0, 10.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ax.spines.values():
        s.set_linewidth(1.5)

    for bar, val in zip(bars, [medias[i] for i in order]):
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}', va='center', fontsize=12, fontfamily='Arial', fontweight='bold')

    ax.grid(axis='x', alpha=0.2, linestyle='--')

    # Legenda com bolinhas no canto inferior
    handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=C[i],
                       markersize=10, markeredgecolor='black', markeredgewidth=0.8,
                       label=LABELS[i]) for i in order[::-1]]
    ax.legend(handles=handles, fontsize=9, ncol=4, loc='lower center',
              bbox_to_anchor=(0.5, -0.18), frameon=True, edgecolor='black')

    plt.tight_layout()
    plt.savefig('fig3_media_geral.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig3 OK")


def fig5():
    """Barras por criterio com cores e legenda com bolinhas."""
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
        bars = ax.bar(x + offset, data[k], w, color=COLORS[k],
                      edgecolor='black', linewidth=0.5)
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
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ax.spines.values():
        s.set_linewidth(1.5)

    # Legenda com bolinhas
    make_legend(ax, ncol=7, bbox=(0.5, -0.12))

    plt.tight_layout()
    plt.savefig('fig5_criterios.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig5 OK")


def fig6():
    """Scatter limpo com legenda padronizada no canto inferior."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))

    ep = [44, 28, 30, 31, 30, 58, 32]
    lo = [4027, 5347, 4998, 1851, 3714, 6866, 1627]
    sv = [49, 4, 59, 15, 33, 55, 0]

    # Pontos
    for i in range(len(LABELS)):
        ax.scatter(lo[i], ep[i], s=sv[i] * 12 + 120, c=C[i],
                   edgecolors='black', linewidth=2, zorder=5, alpha=0.9)

    # Labels - só nome e servicos, posicionados pra não sobrepor
    offsets = {
        0: (15, 25),    # AOEN
        1: (15, -25),   # Clean Arch
        2: (15, 15),    # Hexagonal
        3: (-15, -25),  # 12-Factor
        4: (15, -25),   # Evolutionary
        5: (15, 15),    # Arch Flow
        6: (-15, 15),   # Sem Framework
    }

    for i, l in enumerate(LABELS):
        ox, oy = offsets[i]
        fw = 'bold' if i == 0 else 'normal'
        ax.annotate(f'{l}\n{sv[i]} servicos | {lo[i]} LOC',
                    (lo[i], ep[i]),
                    xytext=(ox, oy),
                    textcoords='offset points',
                    fontsize=9, fontfamily='Arial', fontweight=fw,
                    ha='left' if ox > 0 else 'right',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=C[i], linewidth=1.5, alpha=0.95),
                    arrowprops=dict(arrowstyle='->', color=C[i], lw=1.2))

    ax.set_xlabel('Linhas de Codigo Funcional (menos = mais eficiente)',
                  fontsize=12, fontfamily='Arial')
    ax.set_ylabel('Endpoints de API (mais = mais funcionalidade)',
                  fontsize=12, fontfamily='Arial')
    ax.set_title('Eficiencia: funcionalidade entregue vs codigo necessario\n'
                 'Tamanho do ponto = quantidade de servicos implementados',
                 fontsize=13, fontfamily='Arial', fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for s in ax.spines.values():
        s.set_linewidth(1.5)
    ax.grid(alpha=0.15, linestyle='--')

    # Legenda com bolinhas no canto inferior
    make_legend(ax, ncol=4, loc='lower center', bbox=(0.5, -0.18))

    plt.tight_layout()
    plt.savefig('fig6_eficiencia_poc.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    print("fig6 OK")


if __name__ == '__main__':
    fig1()
    fig3()
    fig5()
    fig6()
    print("\nFiguras 1, 3, 5 e 6 corrigidas!")
