# -*- coding: utf-8 -*-
"""Refazer Fig 2 com bolinhas coloridas e legenda estilo Fig 3."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

COLORS = {
    'aoen': '#1B4332', 'clean_arch': '#E76F51', 'hexagonal': '#264653',
    '12factor': '#E9C46A', 'evolutionary': '#2A9D8F', 'arch_flow': '#F4A261',
    'togaf': '#999999', 'zachman': '#999999'
}

fig, ax = plt.subplots(1, 1, figsize=(9, 7))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(-0.5, 10.5)
ax.set_xlabel('Orientacao a negocio  ->', fontsize=12, fontfamily='Arial', labelpad=10)
ax.set_ylabel('Implementacao Concluida  ->', fontsize=12, fontfamily='Arial', labelpad=10)
ax.set_xticks([])
ax.set_yticks([])
ax.axhline(y=5, color='#DDDDDD', linestyle='--', linewidth=0.8)
ax.axvline(x=5, color='#DDDDDD', linestyle='--', linewidth=0.8)

ax.text(2.5, 9.8, 'Tecnico + Concreto', ha='center', fontsize=8, fontfamily='Arial', color='#AAAAAA', fontstyle='italic')
ax.text(7.5, 9.8, 'Negocio + Concreto', ha='center', fontsize=8, fontfamily='Arial', color='#AAAAAA', fontstyle='italic')
ax.text(2.5, 0.2, 'Tecnico + Abstrato', ha='center', fontsize=8, fontfamily='Arial', color='#AAAAAA', fontstyle='italic')
ax.text(7.5, 0.2, 'Negocio + Abstrato', ha='center', fontsize=8, fontfamily='Arial', color='#AAAAAA', fontstyle='italic')

fws = [
    {"n": "TOGAF", "x": 7, "y": 1.5, "c": COLORS['togaf']},
    {"n": "Zachman", "x": 6, "y": 1, "c": COLORS['zachman']},
    {"n": "Clean Arch.", "x": 2, "y": 7.5, "c": COLORS['clean_arch']},
    {"n": "Hexagonal", "x": 2.5, "y": 7, "c": COLORS['hexagonal']},
    {"n": "12-Factor", "x": 3.5, "y": 8, "c": COLORS['12factor']},
    {"n": "Evolutionary", "x": 4, "y": 5.5, "c": COLORS['evolutionary']},
    {"n": "Arch. for Flow", "x": 6.5, "y": 4, "c": COLORS['arch_flow']},
    {"n": "AOEN", "x": 8, "y": 8, "c": COLORS['aoen']},
]

for fw in fws:
    ia = fw["n"] == "AOEN"
    ms = 180 if ia else 80
    ax.scatter(fw["x"], fw["y"], s=ms, c=fw["c"], edgecolors='black',
               linewidth=2 if ia else 1, zorder=5)
    ax.annotate(fw["n"], xy=(fw["x"], fw["y"]), xytext=(12, 12),
                textcoords='offset points', fontsize=10 if ia else 9,
                fontfamily='Arial', fontweight='bold' if ia else 'normal',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor=fw["c"], linewidth=1.2 if ia else 0.6, alpha=0.95))

for s in ax.spines.values():
    s.set_color('black')
    s.set_linewidth(1.5)

# Legenda com bolinhas estilo fig3
legend_items = []
for fw in fws:
    legend_items.append(Line2D([0], [0], marker='o', color='w',
                                markerfacecolor=fw["c"], markersize=10,
                                markeredgecolor='black', markeredgewidth=0.8,
                                label=fw["n"]))

ax.legend(handles=legend_items, fontsize=9, ncol=4, loc='lower center',
          bbox_to_anchor=(0.5, -0.15), frameon=True, edgecolor='black',
          handletextpad=0.3, columnspacing=1.0)

plt.tight_layout()
plt.savefig('fig2_posicionamento.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print("fig2 OK")
