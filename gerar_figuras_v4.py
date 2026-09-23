# -*- coding: utf-8 -*-
"""Regenera as figuras do experimento a partir de consolidated_v4.json.

Nada é hardcoded: todo número sai do dataset. Paleta validada pelos seis
checks (banda de luminância, piso de croma, separação CVD, piso de visão
normal, contraste) — ver validate_palette.js.
"""
import json
import statistics as st
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

DADOS = "experimento/consolidated_v4.json"

CRIT = ["core_diferenciador", "visao_mercado", "multi_interface", "configurabilidade",
        "isolamento_processamento", "consideracao_custo", "monetizacao",
        "evolucao", "coerencia"]
CRIT_PT = ["Core\ndiferenciador", "Visão de\nmercado", "Multi-\ninterface",
           "Configura-\nbilidade", "Isolamento\nprocess.", "Consideração\nde custo",
           "Moneti-\nzação", "Evolução", "Coerência"]
CRIT_PT1 = ["Core diferenciador", "Visão de mercado", "Multi-interface",
            "Configurabilidade", "Isolamento de processamento", "Consideração de custo",
            "Monetização", "Evolução", "Coerência"]

# ordem estável de identidade (não por ranking — cor segue a entidade)
KEYS = ["aoen", "clean_arch", "hexagonal", "12factor",
        "evolutionary", "arch_flow", "sem_framework"]
ROTULO = {"aoen": "AOEN", "clean_arch": "Clean Arch", "hexagonal": "Hexagonal",
          "12factor": "12-Factor", "evolutionary": "Evolutionary",
          "arch_flow": "Arch Flow", "sem_framework": "Sem framework"}
MARCA = {"sem_framework": "D"}   # controle ganha forma própria (codificação secundária)
COR = {"aoen": "#2a78d6", "clean_arch": "#eb6834", "hexagonal": "#1baf7a",
       "12factor": "#eda100", "evolutionary": "#e87ba4",
       "arch_flow": "#008300", "sem_framework": "#ab8d68"}
CINZA = "#b9b8b3"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
SURF = "#fcfcfb"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": TINTA2, "axes.labelcolor": TINTA,
    "text.color": TINTA, "xtick.color": TINTA2, "ytick.color": TINTA2,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
})


def carregar():
    d = json.load(open(DADOS, encoding="utf-8"))
    regs = d["avaliacoes"]
    porcrit = defaultdict(lambda: defaultdict(list))
    geral = defaultdict(list)
    for r in regs:
        a = r["abordagem"]
        for c in CRIT:
            porcrit[a][c].append(r["scores"][c])
        geral[a].append(st.mean(r["scores"][c] for c in CRIT))
    media = {a: st.mean(v) for a, v in geral.items()}
    mediac = {a: {c: st.mean(v) for c, v in cs.items()} for a, cs in porcrit.items()}
    return media, mediac, d["_meta"]


def limpar(ax, eixo="y"):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis=eixo, alpha=0.25, linestyle="-", linewidth=0.6, color="#d8d7d2")
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- Figura 2
def fig_media_geral(media, meta):
    """Uma série, e o AOEN é o ponto: ênfase (destaca um, cinza no resto)."""
    ordem = sorted(media, key=lambda a: media[a])
    fig, ax = plt.subplots(figsize=(9, 5.2))
    cores = [COR["aoen"] if a == "aoen" else CINZA for a in ordem]
    barras = ax.barh([ROTULO[a] for a in ordem], [media[a] for a in ordem],
                     color=cores, height=0.62, zorder=3)
    for b in barras:
        b.set_joinstyle("round")
    for a, b in zip(ordem, barras):
        negrito = "bold" if a == "aoen" else "normal"
        ax.text(b.get_width() + 0.12, b.get_y() + b.get_height() / 2,
                f"{media[a]:.2f}".replace(".", ","), va="center", fontsize=11,
                fontweight=negrito, color=TINTA if a == "aoen" else TINTA2)
    for r, a in zip(ax.get_yticklabels(), ordem):
        if a == "aoen":
            r.set_fontweight("bold")
            r.set_color(TINTA)
    ax.set_xlabel("Nota média geral (escala 0–10)", color=TINTA2)
    ax.set_xlim(0, 10)
    limpar(ax, "x")
    ax.set_title("Média geral por abordagem arquitetural",
                 fontsize=13, fontweight="bold", loc="left", pad=32)
    ax.text(0, 1.018, f"{meta['ideias_no_conjunto']} ideias de produto · "
            f"{meta['avaliacoes']} avaliações · {meta['pontos_de_dados']} pontos de dados",
            transform=ax.transAxes, fontsize=9.5, color=TINTA2)
    fig.tight_layout()
    fig.savefig("fig3_media_geral.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("fig3_media_geral.png")


# ---------------------------------------------------------------- Figura 3
def fig_radar(mediac):
    """Perfil do AOEN contra selecionados, nos 9 critérios."""
    import numpy as np
    sel = ["aoen", "arch_flow", "clean_arch", "sem_framework"]
    ang = np.linspace(0, 2 * np.pi, len(CRIT), endpoint=False).tolist()
    ang += ang[:1]
    fig, ax = plt.subplots(figsize=(7.4, 7.4), subplot_kw=dict(polar=True))
    estilo = {"aoen": ("-", 2.6, 1.0), "arch_flow": ("--", 1.8, 0.85),
              "clean_arch": ("-.", 1.8, 0.85), "sem_framework": (":", 1.8, 0.85)}
    for a in sel:
        v = [mediac[a][c] for c in CRIT]
        v += v[:1]
        ls, lw, al = estilo[a]
        ax.plot(ang, v, ls, linewidth=lw, color=COR[a], alpha=al,
                label=ROTULO[a], zorder=3 if a == "aoen" else 2)
        if a == "aoen":
            ax.fill(ang, v, color=COR[a], alpha=0.10, zorder=1)
    ax.set_xticks(ang[:-1])
    ax.set_xticklabels(CRIT_PT, fontsize=9, color=TINTA2)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color=TINTA2)
    ax.set_rlabel_position(20)   # entre raios, longe das linhas de dados
    ax.grid(color="#d8d7d2", linewidth=0.6)
    ax.spines["polar"].set_color("#d8d7d2")
    ax.set_title("Perfil comparativo do AOEN por critério",
                 fontsize=13, fontweight="bold", pad=26)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=4,
              frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig("fig4_radar.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("fig4_radar.png")


# ---------------------------------------------------------------- Figura 4
def fig_criterios(mediac):
    """7 séries x 9 critérios: dot plot (63 barras agrupadas são ilegíveis)."""
    fig, ax = plt.subplots(figsize=(10, 7.6))
    ys = list(range(len(CRIT)))[::-1]
    for i, (c, y) in enumerate(zip(CRIT, ys)):
        vals = [(a, mediac[a][c]) for a in KEYS]
        ax.plot([min(v for _, v in vals), max(v for _, v in vals)], [y, y],
                color="#d8d7d2", linewidth=1.4, zorder=1, solid_capstyle="round")
        for a, v in vals:
            m = MARCA.get(a, "o")
            ax.scatter(v, y, s=(95 if a == "aoen" else 70) * (0.9 if m == "D" else 1),
                       color=COR[a], marker=m, edgecolor=SURF, linewidth=1.6,
                       zorder=4 if a == "aoen" else 3)
        va = mediac["aoen"][c]
        ax.annotate(f"{va:.2f}".replace(".", ","), (va, y), textcoords="offset points",
                    xytext=(0, 11), ha="center", fontsize=8.5,
                    fontweight="bold", color=COR["aoen"])
    ax.set_yticks(ys)
    ax.set_yticklabels(CRIT_PT1, fontsize=10.5)
    ax.set_xlabel("Nota média (escala 0–10)", color=TINTA2)
    ax.set_xlim(3.8, 10.2)
    limpar(ax, "x")
    ax.set_title("Comparação das sete abordagens por critério de avaliação",
                 fontsize=13, fontweight="bold", loc="left", pad=34)
    handles = [Line2D([0], [0], marker=MARCA.get(a, "o"), color="w",
                      markerfacecolor=COR[a], markersize=9, label=ROTULO[a])
               for a in KEYS]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.085),
              ncol=4, frameon=False, fontsize=9.5, columnspacing=1.4)
    fig.tight_layout()
    fig.savefig("fig5_criterios.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("fig5_criterios.png")


if __name__ == "__main__":
    media, mediac, meta = carregar()
    fig_media_geral(media, meta)
    fig_radar(mediac)
    fig_criterios(mediac)
    print("\nmédias usadas:",
          {a: round(v, 2) for a, v in sorted(media.items(), key=lambda x: -x[1])})
