# -*- coding: utf-8 -*-
"""Regenera as figuras 1, 5, 6, 7 e 8 do TCC na paleta validada.

Os dados das POCs (Tabelas 7, 8 e 9) não foram reexecutados: são transcritos
das tabelas do próprio documento, para que figura e tabela não divirjam.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

KEYS = ["aoen", "clean_arch", "hexagonal", "12factor",
        "evolutionary", "arch_flow", "sem_framework"]
ROT = {"aoen": "AOEN", "clean_arch": "Clean Arch", "hexagonal": "Hexagonal",
       "12factor": "12-Factor", "evolutionary": "Evolutionary",
       "arch_flow": "Arch Flow", "sem_framework": "Sem framework"}
COR = {"aoen": "#2a78d6", "clean_arch": "#eb6834", "hexagonal": "#1baf7a",
       "12factor": "#eda100", "evolutionary": "#e87ba4",
       "arch_flow": "#008300", "sem_framework": "#ab8d68"}
MARCA = {"sem_framework": "D"}
NEUTRO = "#8a8984"
TINTA, TINTA2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
GRADE = "#d8d7d2"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": TINTA2, "axes.labelcolor": TINTA, "text.color": TINTA,
    "xtick.color": TINTA2, "ytick.color": TINTA2,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
})


def limpar(ax, eixo="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=eixo, alpha=0.3, linewidth=0.6, color=GRADE)
    ax.set_axisbelow(True)


def legenda(ax, keys=KEYS, ncol=4, y=-0.14):
    h = [Line2D([0], [0], marker=MARCA.get(k, "o"), color="w",
                markerfacecolor=COR[k], markersize=9, label=ROT[k]) for k in keys]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, y), ncol=ncol,
              frameon=False, fontsize=9.5, columnspacing=1.4)


# ============================================================ Figura 1
def fig1_fases():
    """Quatro fases sequenciais: rampa de uma cor, escura -> clara indica ordem."""
    fig, ax = plt.subplots(figsize=(12, 4.9))
    ax.set_xlim(-0.3, 11.3); ax.set_ylim(0.15, 4.75); ax.axis("off")
    passo = ["#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]
    tinta = ["#0b0b0b", "#0b0b0b", "#ffffff", "#ffffff"]
    fases = [
        ("Fase 1", "Núcleo +\nvisão de mercado", "VALOR", '"O que construir\ne para quem?"'),
        ("Fase 2", "Interfaces\nmúltiplas", "ALCANCE", '"Onde está\no usuário?"'),
        ("Fase 3", "Orientado a\nconfiguração", "ESCALA", '"Como escalar sem\ncusto de engenharia?"'),
        ("Fase 4", "Isolamento de\nprocessamento", "CUSTO", '"Quanto custa\ncada cliente?"'),
    ]
    x0, w, h, y0 = 0.4, 2.3, 2.1, 1.35
    for i, (tt, sub, lab, q) in enumerate(fases):
        x = x0 + i * 2.72
        ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.12",
                                    facecolor=passo[i], edgecolor="none"))
        ax.text(x + w / 2, y0 + h - 0.4, tt, ha="center", va="center",
                fontsize=12.5, fontweight="bold", color=tinta[i])
        ax.text(x + w / 2, y0 + h / 2 - 0.05, sub, ha="center", va="center",
                fontsize=10, color=tinta[i])
        ax.text(x + w / 2, y0 + 0.32, lab, ha="center", va="center", fontsize=9.5,
                fontweight="bold", color=tinta[i], alpha=0.85)
        ax.text(x + w / 2, y0 - 0.62, q, ha="center", va="center", fontsize=8.5,
                fontstyle="italic", color=TINTA2)
        if i < 3:
            ax.annotate("", xy=(x + w + 0.38, y0 + h / 2), xytext=(x + w + 0.04, y0 + h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=NEUTRO, lw=1.8))
    ax.text(5.7, 4.15, "Princípio: toda decisão arquitetural deve preservar "
            "a capacidade do sistema de evoluir",
            ha="center", va="center", fontsize=10.5, fontstyle="italic", color=TINTA,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#eef4fd", edgecolor=GRADE))
    fig.tight_layout()
    fig.savefig("fig1_fases_aoen.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print("fig1_fases_aoen.png")


# ============================================================ Figura 5
def fig5_eficiencia():
    """Tabela 7 — média por repositório (a figura antiga somava os 3 repos)."""
    # abordagem: (arquivos, LOC, endpoints, modelos, servicos)
    T7 = {"aoen": (21, 1486, 15, 24, 16), "arch_flow": (69, 2522, 19, 76, 18),
          "hexagonal": (52, 1852, 10, 46, 20), "evolutionary": (30, 1403, 10, 20, 11),
          "12factor": (20, 811, 10, 11, 5), "clean_arch": (58, 1930, 9, 66, 1),
          "sem_framework": (3, 626, 11, 0, 0)}
    fig, ax = plt.subplots(figsize=(10.5, 7))
    for k in KEYS:
        _, loc, ep, _, sv = T7[k]
        ax.scatter(loc, ep, s=sv * 26 + 110, color=COR[k], alpha=0.85,
                   marker=MARCA.get(k, "o"), edgecolor=SURF, linewidth=2,
                   zorder=4 if k == "aoen" else 3)
    desloc = {"aoen": (14, 18), "arch_flow": (-14, -14), "hexagonal": (14, 18),
              "evolutionary": (-16, 20), "12factor": (14, -30),
              "clean_arch": (14, -22), "sem_framework": (14, 16)}
    for k in KEYS:
        _, loc, ep, _, sv = T7[k]
        dx, dy = desloc[k]
        ax.annotate(f"{ROT[k]}\n{sv} serviço{'s' if sv != 1 else ''} · {loc} LOC", (loc, ep),
                    xytext=(dx, dy), textcoords="offset points", fontsize=9,
                    fontweight="bold" if k == "aoen" else "normal",
                    ha="left" if dx > 0 else "right", color=TINTA,
                    bbox=dict(boxstyle="round,pad=0.28", facecolor=SURF,
                              edgecolor=COR[k], linewidth=1.2, alpha=0.96),
                    arrowprops=dict(arrowstyle="-", color=COR[k], lw=1))
    ax.set_xlabel("Linhas de código por projeto  (menos = mais eficiente)", color=TINTA2)
    ax.set_ylabel("Endpoints de API por projeto  (mais = mais funcionalidade)", color=TINTA2)
    ax.set_title("Eficiência: funcionalidade entregue por volume de código",
                 fontsize=13, fontweight="bold", loc="left", pad=30)
    ax.text(0, 1.015, "média dos 3 projetos de cada abordagem · área do ponto "
            "proporcional ao número de serviços", transform=ax.transAxes,
            fontsize=9.5, color=TINTA2)
    ax.set_xlim(330, 2980); ax.set_ylim(7.4, 20.6)
    limpar(ax, "both")
    fig.tight_layout()
    fig.savefig("fig6_eficiencia_poc.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print("fig6_eficiencia_poc.png")


# ============================================================ Figura 6
def fig6_decisoes():
    """Tabela 8 — matriz de pontos: 3 marcas por célula, preenchidas = presença."""
    cat = ["Camada de\nserviços", "Núcleo\nisolado", "Configuração\npor cliente", "Testes"]
    T8 = {"aoen": [3, 3, 3, 0], "clean_arch": [1, 0, 1, 0], "hexagonal": [3, 3, 0, 0],
          "12factor": [2, 0, 3, 0], "evolutionary": [3, 2, 2, 3],
          "arch_flow": [2, 3, 1, 0], "sem_framework": [0, 0, 0, 0]}
    ordem = sorted(T8, key=lambda k: -sum(T8[k]))
    fig, ax = plt.subplots(figsize=(10, 6.6))
    dx = [-0.17, 0.0, 0.17]
    for r, k in enumerate(ordem):
        y = len(ordem) - 1 - r
        for c, n in enumerate(T8[k]):
            for j in range(3):
                cheio = j < n
                ax.scatter(c + dx[j], y, s=190,
                           facecolor=COR[k] if cheio else "none",
                           edgecolor=COR[k] if cheio else "#cfcec9",
                           linewidth=1.5, zorder=3)
        ax.text(3.72, y, f"{sum(T8[k])}/12", va="center", fontsize=10,
                color=TINTA if k == "aoen" else TINTA2,
                fontweight="bold" if k == "aoen" else "normal")
    ax.set_yticks(range(len(ordem)))
    ax.set_yticklabels([ROT[k] for k in ordem][::-1], fontsize=11)
    for rot, k in zip(ax.get_yticklabels(), ordem[::-1]):
        if k == "aoen":
            rot.set_fontweight("bold"); rot.set_color(TINTA)
    ax.set_xticks(range(len(cat)))
    ax.set_xticklabels(cat, fontsize=10.5)
    ax.xaxis.set_ticks_position("top"); ax.xaxis.set_label_position("top")
    ax.set_xlim(-0.45, 4.05); ax.set_ylim(-0.6, len(ordem) - 0.4)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.tick_params(length=0)
    for c in range(1, len(cat)):
        ax.axvline(c - 0.5, color=GRADE, linewidth=0.7, zorder=1)
    # título e subtítulo em coordenadas de figura: os rótulos de coluna ficam
    # no topo do eixo, então o cabeçalho precisa de espaço reservado acima deles
    fig.subplots_adjust(top=0.76, left=0.16, right=0.97, bottom=0.04)
    fig.text(0.012, 0.975, "Decisões arquiteturais presentes no código gerado",
             fontsize=13, fontweight="bold", va="top")
    fig.text(0.012, 0.905, "cada marca é um dos 3 projetos da abordagem · "
             "cheia = decisão presente, vazia = ausente",
             fontsize=9.5, color=TINTA2, va="top")
    fig.savefig("fig7_decisoes_poc.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print("fig7_decisoes_poc.png")


# ============================================================ Figura 7
def fig7_negocio():
    """Tabela 9 — a razão é o ponto, então a razão é a barra.

    A versão anterior punha as contagens absolutas na altura e a razão no rótulo:
    o Arch Flow ficava com a barra mais alta (45) e o rótulo menor (3,2x) que o
    AOEN (37 / 3,7x), e o gráfico contradizia o próprio rótulo.
    """
    T9 = {"aoen": (37, 10), "arch_flow": (45, 14), "sem_framework": (3, 2),
          "hexagonal": (9, 15), "evolutionary": (10, 20), "12factor": (5, 12),
          "clean_arch": (12, 35)}
    razao = {k: n / t for k, (n, t) in T9.items()}
    ordem = sorted(razao, key=lambda k: razao[k])
    fig, ax = plt.subplots(figsize=(10, 5.8))
    barras = ax.barh([ROT[k] for k in ordem], [razao[k] for k in ordem],
                     color=[COR[k] for k in ordem], height=0.6, zorder=3)
    ax.axvline(1, color=TINTA2, linewidth=1.2, linestyle="--", zorder=4)
    ax.text(1, len(ordem) - 0.35, "  equilíbrio", fontsize=9, color=TINTA2,
            style="italic", va="center")
    for k, b in zip(ordem, barras):
        n, t = T9[k]
        ax.text(b.get_width() + 0.08, b.get_y() + b.get_height() / 2,
                f"{razao[k]:.1f}×".replace(".", ",") + f"   ({n} a negócio · {t} técnicas)",
                va="center", fontsize=9.5,
                fontweight="bold" if k == "aoen" else "normal",
                color=TINTA if k == "aoen" else TINTA2)
    for rot, k in zip(ax.get_yticklabels(), ordem):
        if k == "aoen":
            rot.set_fontweight("bold"); rot.set_color(TINTA)
    ax.set_xlabel("Razão entre menções a negócio e menções técnicas", color=TINTA2)
    ax.set_xlim(0, 5.6)
    ax.set_xticks([0, 1, 2, 3, 4])
    limpar(ax, "x")
    ax.set_title("Orientação a negócio versus técnica na documentação gerada",
                 fontsize=13, fontweight="bold", loc="left", pad=30)
    ax.text(0, 1.03, "acima de 1: o README fala mais de negócio que de técnica",
            transform=ax.transAxes, fontsize=9.5, color=TINTA2)
    fig.tight_layout()
    fig.savefig("fig8_negocio_vs_tecnica.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print("fig8_negocio_vs_tecnica.png")


# ============================================================ Figura 8
def fig8_posicionamento():
    """Mapa conceitual de posicionamento (não é dado medido)."""
    fig, ax = plt.subplots(figsize=(9.5, 7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xticks([]); ax.set_yticks([])
    ax.axhline(5, color=GRADE, linewidth=0.9)
    ax.axvline(5, color=GRADE, linewidth=0.9)
    for xq, yq, txt in [(2.5, 9.5, "técnico + concreto"), (7.5, 9.5, "negócio + concreto"),
                        (2.5, 0.35, "técnico + abstrato"), (7.5, 0.35, "negócio + abstrato")]:
        ax.text(xq, yq, txt, ha="center", fontsize=8.5, color="#a9a8a3", fontstyle="italic")
    pts = [("TOGAF", 7.0, 1.5, NEUTRO), ("Zachman", 6.0, 1.0, NEUTRO),
           ("Clean Arch", 2.0, 7.5, COR["clean_arch"]), ("Hexagonal", 2.6, 6.9, COR["hexagonal"]),
           ("12-Factor", 3.5, 8.0, COR["12factor"]), ("Evolutionary", 4.0, 5.5, COR["evolutionary"]),
           ("Arch Flow", 6.5, 4.0, COR["arch_flow"]), ("AOEN", 8.0, 8.0, COR["aoen"])]
    for n, px, py, c in pts:
        eh = n == "AOEN"
        ax.scatter(px, py, s=210 if eh else 95, color=c, edgecolor=SURF,
                   linewidth=2, zorder=5)
        ax.annotate(n, (px, py), xytext=(11, 10), textcoords="offset points",
                    fontsize=10.5 if eh else 9.5, fontweight="bold" if eh else "normal",
                    color=TINTA)
    ax.set_xlabel("Orientação a negócio  →", color=TINTA2, labelpad=8)
    ax.set_ylabel("Concretude da prescrição  →", color=TINTA2, labelpad=8)
    for s in ax.spines.values():
        s.set_color(GRADE)
    ax.set_title("Posicionamento do AOEN frente a frameworks existentes",
                 fontsize=13, fontweight="bold", loc="left", pad=14)
    fig.tight_layout()
    fig.savefig("fig2_posicionamento.png", dpi=220, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print("fig2_posicionamento.png")


if __name__ == "__main__":
    fig1_fases(); fig5_eficiencia(); fig6_decisoes(); fig7_negocio(); fig8_posicionamento()
