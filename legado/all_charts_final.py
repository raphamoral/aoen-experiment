# -*- coding: utf-8 -*-
"""Regenerar TODOS os 8 gráficos com acentuação correta e legenda padronizada."""
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
KEYS = list(COLORS.keys())
C = [COLORS[k] for k in KEYS]


def legend_circles(ax, keys=None, labels=None, ncol=7, bbox=(0.5, -0.12)):
    if keys is None: keys = KEYS
    if labels is None: labels = LABELS
    h = [Line2D([0],[0], marker='o', color='w', markerfacecolor=COLORS[k],
         markersize=10, markeredgecolor='black', markeredgewidth=0.8, label=l)
         for k, l in zip(keys, labels)]
    ax.legend(handles=h, fontsize=9, ncol=ncol, loc='upper center',
              bbox_to_anchor=bbox, frameon=True, edgecolor='black',
              handletextpad=0.3, columnspacing=1.0)


# ============================================================
# FIGURA 1 — Fases AOEN
# ============================================================
def fig1():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6.5))
    ax.set_xlim(-0.5, 11); ax.set_ylim(-2, 4.5); ax.axis('off')
    pc = ['#1B4332', '#264653', '#2A9D8F', '#E9C46A']
    tc = ['white', 'white', 'white', 'black']
    phases = [
        {"x":0.5,"y":1.5,"w":2.2,"h":2.2,"t":"Fase 1","s":"Núcleo +\nVisão de Mercado","l":"VALOR"},
        {"x":3.2,"y":1.5,"w":2.2,"h":2.2,"t":"Fase 2","s":"Multi-Interface\nAdaptativa","l":"ALCANCE"},
        {"x":5.9,"y":1.5,"w":2.2,"h":2.2,"t":"Fase 3","s":"Configuration-\nDriven","l":"ESCALA"},
        {"x":8.6,"y":1.5,"w":2.2,"h":2.2,"t":"Fase 4","s":"Isolamento de\nProcessamento","l":"CUSTO"},
    ]
    for i, ph in enumerate(phases):
        rect = FancyBboxPatch((ph["x"],ph["y"]),ph["w"],ph["h"],boxstyle="round,pad=0.15",facecolor=pc[i],edgecolor='black',linewidth=2)
        ax.add_patch(rect)
        ax.text(ph["x"]+ph["w"]/2,ph["y"]+ph["h"]-0.35,ph["t"],ha='center',va='center',fontsize=13,fontweight='bold',fontfamily='Arial',color=tc[i])
        ax.text(ph["x"]+ph["w"]/2,ph["y"]+ph["h"]/2,ph["s"],ha='center',va='center',fontsize=10,fontfamily='Arial',color=tc[i])
        ax.text(ph["x"]+ph["w"]/2,ph["y"]+0.35,ph["l"],ha='center',va='center',fontsize=10,fontfamily='Arial',fontstyle='italic',color=tc[i],fontweight='bold')
    for i in range(3):
        ax.annotate("",xy=(phases[i+1]["x"]-0.05,2.6),xytext=(phases[i]["x"]+phases[i]["w"]+0.05,2.6),arrowprops=dict(arrowstyle="-|>",color="black",lw=2))
    ax.text(5.65,4.2,'Princípio: "Toda decisão arquitetural deve preservar a capacidade do sistema de evoluir"',ha='center',va='center',fontsize=10,fontfamily='Arial',fontstyle='italic',bbox=dict(boxstyle='round,pad=0.5',facecolor='#F0F0F0',edgecolor='black',linewidth=1.5))
    qs = ['"O que construir\ne para quem?"','"Onde está\no usuário?"','"Como escalar\nsem deploy?"','"Quanto custa\ncada cliente?"']
    for i, q in enumerate(qs):
        ax.text(phases[i]["x"]+phases[i]["w"]/2,1.05,q,ha='center',va='center',fontsize=8,fontfamily='Arial',fontstyle='italic',color='#555555')
    ll = ["Fase 1: Núcleo + Visão de Mercado (VALOR)","Fase 2: Multi-Interface Adaptativa (ALCANCE)","Fase 3: Configuration-Driven (ESCALA)","Fase 4: Isolamento de Processamento (CUSTO)"]
    h = [Line2D([0],[0],marker='o',color='w',markerfacecolor=pc[i],markersize=10,markeredgecolor='black',markeredgewidth=0.8,label=ll[i]) for i in range(4)]
    ax.legend(handles=h,fontsize=9,ncol=2,loc='lower center',bbox_to_anchor=(0.45,-0.15),frameon=True,edgecolor='black',handletextpad=0.5,columnspacing=1.5)
    plt.tight_layout()
    plt.savefig('fig1_fases_aoen.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig1 OK")


# ============================================================
# FIGURA 2 — Posicionamento
# ============================================================
def fig2():
    fig, ax = plt.subplots(1,1,figsize=(9,7))
    ax.set_xlim(-0.5,10.5);ax.set_ylim(-0.5,10.5)
    ax.set_xlabel('Orientação a negócio  →',fontsize=12,fontfamily='Arial',labelpad=10)
    ax.set_ylabel('Nível de implementação  →',fontsize=12,fontfamily='Arial',labelpad=10)
    ax.set_xticks([]);ax.set_yticks([])
    ax.axhline(y=5,color='#DDDDDD',linestyle='--',linewidth=0.8)
    ax.axvline(x=5,color='#DDDDDD',linestyle='--',linewidth=0.8)
    ax.text(2.5,9.8,'Técnico + Concreto',ha='center',fontsize=8,fontfamily='Arial',color='#AAAAAA',fontstyle='italic')
    ax.text(7.5,9.8,'Negócio + Concreto',ha='center',fontsize=8,fontfamily='Arial',color='#AAAAAA',fontstyle='italic')
    ax.text(2.5,0.2,'Técnico + Abstrato',ha='center',fontsize=8,fontfamily='Arial',color='#AAAAAA',fontstyle='italic')
    ax.text(7.5,0.2,'Negócio + Abstrato',ha='center',fontsize=8,fontfamily='Arial',color='#AAAAAA',fontstyle='italic')
    fws = [
        {"n":"TOGAF","x":7,"y":1.5,"c":"#999999"},{"n":"Zachman","x":6,"y":1,"c":"#999999"},
        {"n":"Clean Arch.","x":2,"y":7.5,"c":COLORS['clean_arch']},{"n":"Hexagonal","x":2.5,"y":7,"c":COLORS['hexagonal']},
        {"n":"12-Factor","x":3.5,"y":8,"c":COLORS['12factor']},{"n":"Evolutionary","x":4,"y":5.5,"c":COLORS['evolutionary']},
        {"n":"Arch. for Flow","x":6.5,"y":4,"c":COLORS['arch_flow']},{"n":"AOEN","x":8,"y":8,"c":COLORS['aoen']},
    ]
    for fw in fws:
        ia = fw["n"]=="AOEN"
        ax.scatter(fw["x"],fw["y"],s=180 if ia else 80,c=fw["c"],edgecolors='black',linewidth=2 if ia else 1,zorder=5)
        ax.annotate(fw["n"],xy=(fw["x"],fw["y"]),xytext=(12,12),textcoords='offset points',fontsize=10 if ia else 9,fontfamily='Arial',fontweight='bold' if ia else 'normal',bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor=fw["c"],linewidth=1.2 if ia else 0.6,alpha=0.95))
    for s in ax.spines.values():s.set_color('black');s.set_linewidth(1.5)
    h = [Line2D([0],[0],marker='o',color='w',markerfacecolor=fw["c"],markersize=10,markeredgecolor='black',markeredgewidth=0.8,label=fw["n"]) for fw in fws]
    ax.legend(handles=h,fontsize=9,ncol=4,loc='lower center',bbox_to_anchor=(0.5,-0.15),frameon=True,edgecolor='black',handletextpad=0.3,columnspacing=1.0)
    plt.tight_layout()
    plt.savefig('fig2_posicionamento.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig2 OK")


# ============================================================
# FIGURA 3 — Média geral
# ============================================================
def fig3():
    fig, ax = plt.subplots(1,1,figsize=(10,7))
    medias = [7.31,4.42,6.67,5.44,5.99,7.08,6.34]
    order = sorted(range(len(medias)),key=lambda i:medias[i])
    bars = ax.barh([LABELS[i] for i in order],[medias[i] for i in order],color=[C[i] for i in order],edgecolor='black',linewidth=0.8,height=0.6)
    ax.set_xlabel('Nota Média Geral (0-10)',fontsize=12,fontfamily='Arial')
    ax.set_title('Média geral por abordagem arquitetural (100 ideias)',fontsize=14,fontfamily='Arial',fontweight='bold')
    ax.set_xlim(0,10.5)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    for bar,val in zip(bars,[medias[i] for i in order]):
        ax.text(bar.get_width()+0.15,bar.get_y()+bar.get_height()/2,f'{val:.1f}',va='center',fontsize=12,fontfamily='Arial',fontweight='bold')
    ax.grid(axis='x',alpha=0.2,linestyle='--')
    legend_circles(ax, [KEYS[i] for i in order[::-1]], [LABELS[i] for i in order[::-1]], ncol=4, bbox=(0.5,-0.15))
    plt.tight_layout()
    plt.savefig('fig3_media_geral.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig3 OK")


# ============================================================
# FIGURA 4 — Radar
# ============================================================
def fig4():
    fig, ax = plt.subplots(1,1,figsize=(10,10),subplot_kw=dict(polar=True))
    cl = ["Core\nDiferenciador","Visão de\nMercado","Multi-\nInterface","Configura-\nbilidade","Isolamento\nProcess.","Consideração\nde Custo","Moneti-\nzação","Evolução","Coerência"]
    angles = np.linspace(0,2*np.pi,9,endpoint=False).tolist()+[0]
    rd = {"AOEN":[8.6,8.9,9.4,7.5,5.7,4.4,4.3,8.7,8.5],"Clean Arch":[5.4,4.7,3.4,4.1,3.4,2.2,3.3,6.9,6.3],"Hexagonal":[7.5,5.9,9.0,5.0,6.4,4.6,5.0,8.6,8.0],"Sem Framework":[5.8,7.7,8.1,3.5,6.6,6.5,4.6,6.6,7.7]}
    rc = [COLORS['aoen'],COLORS['clean_arch'],COLORS['hexagonal'],COLORS['sem_framework']]
    rs = ['-','--','-.',':'];rw = [3,1.5,1.5,1.5]
    for (n,v),c,s,w in zip(rd.items(),rc,rs,rw):
        vv = v+v[:1]; ax.plot(angles,vv,s,linewidth=w,label=n,color=c); ax.fill(angles,vv,alpha=0.08,color=c)
    ax.set_xticks(angles[:-1]);ax.set_xticklabels(cl,fontsize=8,fontfamily='Arial');ax.set_ylim(0,10)
    ax.set_title('Perfil comparativo: AOEN vs selecionados',fontsize=13,fontfamily='Arial',fontweight='bold',pad=20)
    ax.legend(loc='upper right',bbox_to_anchor=(1.3,1.1),fontsize=10)
    plt.tight_layout()
    plt.savefig('fig4_radar.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig4 OK")


# ============================================================
# FIGURA 5 — Barras por critério
# ============================================================
def fig5():
    fig, ax = plt.subplots(1,1,figsize=(18,8))
    cr = ["Core\nDiferenciador","Visão de\nMercado","Multi-\nInterface","Configura-\nbilidade","Isolamento\nProcess.","Consideração\nde Custo","Moneti-\nzação","Evolução","Coerência"]
    data = {"aoen":[8.6,8.9,9.4,7.5,5.7,4.4,4.3,8.7,8.5],"clean_arch":[5.4,4.7,3.4,4.1,3.4,2.2,3.3,6.9,6.3],"hexagonal":[7.5,5.9,9.0,5.0,6.4,4.6,5.0,8.6,8.0],"12factor":[5.0,3.4,4.6,5.1,7.6,5.0,2.7,7.9,7.8],"evolutionary":[6.5,5.3,4.2,5.4,6.8,5.9,2.6,9.0,8.1],"arch_flow":[8.1,8.0,5.7,6.0,6.9,5.8,7.1,8.0,8.1],"sem_framework":[5.8,7.7,8.1,3.5,6.6,6.5,4.6,6.6,7.7]}
    x = np.arange(len(cr));w = 0.12;total = len(KEYS)
    for i,(k,l) in enumerate(zip(KEYS,LABELS)):
        offset = (i-total/2+0.5)*w
        bars = ax.bar(x+offset,data[k],w,color=COLORS[k],edgecolor='black',linewidth=0.5)
        if k=='aoen':
            for bar,val in zip(bars,data[k]):
                ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.15,f'{val:.1f}',ha='center',va='bottom',fontsize=7,fontfamily='Arial',fontweight='bold',color=COLORS['aoen'])
    ax.set_xlabel('Critério de Avaliação',fontsize=12,fontfamily='Arial')
    ax.set_ylabel('Nota Média (0-10)',fontsize=12,fontfamily='Arial')
    ax.set_title('Comparação de abordagens arquiteturais por critério (100 ideias)',fontsize=14,fontfamily='Arial',fontweight='bold')
    ax.set_xticks(x);ax.set_xticklabels(cr,fontsize=10,fontfamily='Arial');ax.set_ylim(0,11)
    ax.grid(axis='y',alpha=0.3,linestyle='--')
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    legend_circles(ax)
    plt.tight_layout()
    plt.savefig('fig5_criterios.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig5 OK")


# ============================================================
# FIGURA 6 — Eficiência POC
# ============================================================
def fig6():
    fig, ax = plt.subplots(1,1,figsize=(12,9))
    ep = [44,28,30,31,30,58,32];lo = [4027,5347,4998,1851,3714,6866,1627];sv = [49,4,59,15,33,55,0]
    for i in range(len(LABELS)):
        ax.scatter(lo[i],ep[i],s=sv[i]*12+120,c=C[i],edgecolors='black',linewidth=2,zorder=5,alpha=0.9)
    offsets = {0:(15,25),1:(15,-25),2:(15,15),3:(-15,-25),4:(15,-25),5:(15,15),6:(-15,15)}
    for i,l in enumerate(LABELS):
        ox,oy = offsets[i]
        ax.annotate(f'{l}\n{sv[i]} serviços | {lo[i]} LOC',(lo[i],ep[i]),xytext=(ox,oy),textcoords='offset points',fontsize=9,fontfamily='Arial',fontweight='bold' if i==0 else 'normal',ha='left' if ox>0 else 'right',bbox=dict(boxstyle='round,pad=0.3',facecolor='white',edgecolor=C[i],linewidth=1.5,alpha=0.95),arrowprops=dict(arrowstyle='->',color=C[i],lw=1.2))
    ax.set_xlabel('Linhas de Código Funcional (menos = mais eficiente)',fontsize=12,fontfamily='Arial')
    ax.set_ylabel('Endpoints de API (mais = mais funcionalidade)',fontsize=12,fontfamily='Arial')
    ax.set_title('Eficiência: funcionalidade entregue vs código necessário\nTamanho do ponto = quantidade de serviços implementados',fontsize=13,fontfamily='Arial',fontweight='bold')
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    ax.grid(alpha=0.15,linestyle='--')
    legend_circles(ax,ncol=4,bbox=(0.5,-0.15))
    plt.tight_layout()
    plt.savefig('fig6_eficiencia_poc.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig6 OK")


# ============================================================
# FIGURA 7 — Decisões arquiteturais
# ============================================================
def fig7():
    fig, ax = plt.subplots(1,1,figsize=(10,6))
    cat = ["Service\nLayer","Core\nIsolado","Config\nTenant","Testes"]
    d = {"aoen":[3,3,3,0],"clean_arch":[1,0,1,0],"hexagonal":[3,3,0,0],"12factor":[2,0,3,0],"evolutionary":[3,2,2,3],"arch_flow":[2,3,1,0],"sem_framework":[0,0,0,0]}
    x = np.arange(len(cat));w = 0.11
    for i,k in enumerate(KEYS):
        ax.bar(x+i*w-3*w,d[k],w,color=COLORS[k],edgecolor='black',linewidth=0.5)
    ax.set_xlabel('Decisão Arquitetural',fontsize=11,fontfamily='Arial')
    ax.set_ylabel('Presença nos 3 projetos (0-3)',fontsize=11,fontfamily='Arial')
    ax.set_title('Decisões arquiteturais presentes no código gerado',fontsize=12,fontfamily='Arial',fontweight='bold')
    ax.set_xticks(x);ax.set_xticklabels(cat,fontsize=10,fontfamily='Arial');ax.set_ylim(0,3.8);ax.set_yticks([0,1,2,3])
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    legend_circles(ax,ncol=7,bbox=(0.5,-0.18))
    plt.tight_layout()
    plt.savefig('fig7_decisoes_poc.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig7 OK")


# ============================================================
# FIGURA 8 — Negócio vs Técnica
# ============================================================
def fig8():
    fig, ax = plt.subplots(1,1,figsize=(12,7))
    lo = ["AOEN","Arch Flow","Sem FW","Hexagonal","Evolutionary","12-Factor","Clean Arch"]
    ko = ["aoen","arch_flow","sem_framework","hexagonal","evolutionary","12factor","clean_arch"]
    neg = [37,45,3,9,10,5,12];tec = [10,14,2,15,20,12,35]
    ratios = [3.7,3.2,1.5,0.6,0.5,0.4,0.3]
    co = [COLORS[k] for k in ko]
    x = np.arange(len(lo));w = 0.35
    ax.bar(x-w/2,neg,w,label='Menções a negócio',color=co,edgecolor='black',linewidth=0.8)
    ax.bar(x+w/2,tec,w,label='Menções técnicas',color='white',edgecolor=co,linewidth=2,hatch='///')
    for i in range(len(lo)):
        mv = max(neg[i],tec[i])
        color = '#228B22' if ratios[i]>1 else '#B22222'
        ax.text(x[i],mv+1.5,f'{ratios[i]}x',ha='center',va='bottom',fontsize=10,fontfamily='Arial',fontweight='bold',color=color)
    ax.set_xlabel('Abordagem',fontsize=11,fontfamily='Arial')
    ax.set_ylabel('Quantidade de menções nos READMEs',fontsize=11,fontfamily='Arial')
    ax.set_title('Orientação a negócio vs técnica na documentação gerada\n(valores acima das barras = razão negócio/técnica)',fontsize=13,fontfamily='Arial',fontweight='bold')
    ax.set_xticks(x);ax.set_xticklabels(lo,fontsize=10,fontfamily='Arial')
    ax.legend(fontsize=10,loc='upper right')
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    ax.set_ylim(0,52)
    plt.tight_layout()
    plt.savefig('fig8_negocio_vs_tecnica.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig8 OK")


if __name__ == '__main__':
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); fig7(); fig8()
    print("\nTodos os 8 gráficos com acentuação correta!")
