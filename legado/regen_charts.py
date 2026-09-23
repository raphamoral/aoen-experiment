# -*- coding: utf-8 -*-
"""Regenerar todos os gráficos com cores profissionais."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

COLORS = {
    'aoen': '#1B4332',
    'clean_arch': '#E76F51',
    'hexagonal': '#264653',
    '12factor': '#E9C46A',
    'evolutionary': '#2A9D8F',
    'arch_flow': '#F4A261',
    'sem_framework': '#BFBFBF'
}
LABELS = ["AOEN", "Clean Arch", "Hexagonal", "12-Factor", "Evolutionary", "Arch Flow", "Sem Framework"]
KEYS = ["aoen", "clean_arch", "hexagonal", "12factor", "evolutionary", "arch_flow", "sem_framework"]
C = [COLORS[k] for k in KEYS]

def fig1():
    fig, ax = plt.subplots(1, 1, figsize=(10, 5.5))
    ax.set_xlim(-0.5, 10.5); ax.set_ylim(-1.5, 4); ax.axis('off')
    pc = ['#1B4332', '#264653', '#2A9D8F', '#E9C46A']
    tc = ['white', 'white', 'white', 'black']
    phases = [
        {"x":0.5,"y":1.5,"w":2,"h":2,"t":"Fase 1","s":"Nucleo +\nVisao de Mercado","l":"VALOR"},
        {"x":3,"y":1.5,"w":2,"h":2,"t":"Fase 2","s":"Multi-Interface\nAdaptativa","l":"ALCANCE"},
        {"x":5.5,"y":1.5,"w":2,"h":2,"t":"Fase 3","s":"Configuration-\nDriven","l":"ESCALA"},
        {"x":8,"y":1.5,"w":2,"h":2,"t":"Fase 4","s":"Isolamento de\nProcessamento","l":"CUSTO"},
    ]
    for i, p in enumerate(phases):
        rect = FancyBboxPatch((p["x"],p["y"]),p["w"],p["h"],boxstyle="round,pad=0.1",facecolor=pc[i],edgecolor='black',linewidth=1.5)
        ax.add_patch(rect)
        ax.text(p["x"]+p["w"]/2,p["y"]+p["h"]-0.3,p["t"],ha='center',va='center',fontsize=11,fontweight='bold',fontfamily='Arial',color=tc[i])
        ax.text(p["x"]+p["w"]/2,p["y"]+p["h"]/2,p["s"],ha='center',va='center',fontsize=9,fontfamily='Arial',color=tc[i])
        ax.text(p["x"]+p["w"]/2,p["y"]+0.3,p["l"],ha='center',va='center',fontsize=9,fontfamily='Arial',fontstyle='italic',color=tc[i])
    for i in range(3):
        ax.annotate("",xy=(phases[i+1]["x"]-0.05,2.5),xytext=(phases[i]["x"]+phases[i]["w"]+0.05,2.5),arrowprops=dict(arrowstyle="->",color="black",lw=1.5))
    ax.text(5.25,3.8,'Principio: "Toda decisao arquitetural deve preservar a capacidade do sistema de evoluir"',ha='center',va='center',fontsize=9,fontfamily='Arial',fontstyle='italic',bbox=dict(boxstyle='round,pad=0.4',facecolor='#F8F8F8',edgecolor='black',linewidth=1))
    ax.annotate("",xy=(10.3,2.5),xytext=(10.05,2.5),arrowprops=dict(arrowstyle="->",color="black",lw=1.5))
    ax.text(10.4,2.5,"Monetizacao\nviavel",ha='left',va='center',fontsize=9,fontfamily='Arial',fontweight='bold',bbox=dict(boxstyle='round,pad=0.3',facecolor='#1B4332',edgecolor='black',linewidth=1),color='white')
    qs = ['"O que construir\ne para quem?"','"Onde esta\no usuario?"','"Como escalar\nsem deploy?"','"Quanto custa\ncada cliente?"']
    for i, q in enumerate(qs):
        ax.text(phases[i]["x"]+phases[i]["w"]/2,1.1,q,ha='center',va='center',fontsize=7.5,fontfamily='Arial',fontstyle='italic',color='#444444')
    plt.tight_layout()
    plt.savefig('fig1_fases_aoen.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig1 OK")

def fig2():
    fig, ax = plt.subplots(1,1,figsize=(8,6))
    ax.set_xlim(-0.5,10.5);ax.set_ylim(-0.5,10.5)
    ax.set_xlabel('Orientacao a negocio  ->',fontsize=11,fontfamily='Arial',labelpad=10)
    ax.set_ylabel('Concretude de implementacao  ->',fontsize=11,fontfamily='Arial',labelpad=10)
    ax.set_xticks([]);ax.set_yticks([])
    ax.axhline(y=5,color='#CCCCCC',linestyle='--',linewidth=0.8)
    ax.axvline(x=5,color='#CCCCCC',linestyle='--',linewidth=0.8)
    ax.text(2.5,9.5,'Tecnico + Concreto',ha='center',fontsize=8,fontfamily='Arial',color='#999999',fontstyle='italic')
    ax.text(7.5,9.5,'Negocio + Concreto',ha='center',fontsize=8,fontfamily='Arial',color='#999999',fontstyle='italic')
    ax.text(2.5,0.5,'Tecnico + Abstrato',ha='center',fontsize=8,fontfamily='Arial',color='#999999',fontstyle='italic')
    ax.text(7.5,0.5,'Negocio + Abstrato',ha='center',fontsize=8,fontfamily='Arial',color='#999999',fontstyle='italic')
    fws = [
        {"n":"TOGAF","x":7,"y":1.5,"c":"#AAAAAA"},{"n":"Zachman","x":6,"y":1,"c":"#AAAAAA"},
        {"n":"Clean Arch.","x":2,"y":7.5,"c":COLORS['clean_arch']},{"n":"Hexagonal","x":2.5,"y":7,"c":COLORS['hexagonal']},
        {"n":"12-Factor","x":3.5,"y":8,"c":COLORS['12factor']},{"n":"Evolutionary\nArch.","x":4,"y":5.5,"c":COLORS['evolutionary']},
        {"n":"Arch. for\nFlow","x":6.5,"y":4,"c":COLORS['arch_flow']},{"n":"AOEN","x":8,"y":8,"c":COLORS['aoen']},
    ]
    for fw in fws:
        ia = fw["n"]=="AOEN"
        ax.scatter(fw["x"],fw["y"],s=150 if ia else 70,c=fw["c"],edgecolors='black',linewidth=1.5 if ia else 0.8,zorder=5)
        ax.annotate(fw["n"],xy=(fw["x"],fw["y"]),xytext=(10,10),textcoords='offset points',fontsize=10 if ia else 9,fontfamily='Arial',fontweight='bold' if ia else 'normal',bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor=fw["c"],linewidth=1 if ia else 0.5,alpha=0.9))
    for s in ax.spines.values(): s.set_color('black');s.set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig('fig2_posicionamento.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig2 OK")

def fig3():
    fig, ax = plt.subplots(1,1,figsize=(10,6))
    medias = [7.31,4.42,6.67,5.44,5.99,7.08,6.34]
    order = sorted(range(len(medias)),key=lambda i:medias[i])
    bars = ax.barh([LABELS[i] for i in order],[medias[i] for i in order],color=[C[i] for i in order],edgecolor='black',linewidth=0.8)
    ax.set_xlabel('Nota Media Geral (0-10)',fontsize=11,fontfamily='Arial')
    ax.set_title('Media geral por abordagem arquitetural',fontsize=13,fontfamily='Arial',fontweight='bold')
    ax.set_xlim(0,10.5)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    for bar,val in zip(bars,[medias[i] for i in order]):
        ax.text(bar.get_width()+0.15,bar.get_y()+bar.get_height()/2,f'{val:.1f}',va='center',fontsize=11,fontfamily='Arial')
    plt.tight_layout()
    plt.savefig('fig3_media_geral.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig3 OK")

def fig4():
    fig, ax = plt.subplots(1,1,figsize=(10,10),subplot_kw=dict(polar=True))
    cl = ["Core\nDiferenciador","Visao de\nMercado","Multi-\nInterface","Configura-\nbilidade","Isolamento\nProcess.","Consideracao\nde Custo","Moneti-\nzacao","Evolucao","Coerencia"]
    angles = np.linspace(0,2*np.pi,9,endpoint=False).tolist()+[0]
    rd = {"AOEN":[8.6,8.9,9.4,7.5,5.7,4.4,4.3,8.7,8.5],"Clean Arch":[5.4,4.7,3.4,4.1,3.4,2.2,3.3,6.9,6.3],"Hexagonal":[7.5,5.9,9.0,5.0,6.4,4.6,5.0,8.6,8.0],"Sem Framework":[5.8,7.7,8.1,3.5,6.6,6.5,4.6,6.6,7.7]}
    rc = [COLORS['aoen'],COLORS['clean_arch'],COLORS['hexagonal'],COLORS['sem_framework']]
    rs = ['-','--','-.',':']
    rw = [3,1.5,1.5,1.5]
    for (n,v),c,s,w in zip(rd.items(),rc,rs,rw):
        vv = v+v[:1]
        ax.plot(angles,vv,s,linewidth=w,label=n,color=c)
        ax.fill(angles,vv,alpha=0.08,color=c)
    ax.set_xticks(angles[:-1]);ax.set_xticklabels(cl,fontsize=8,fontfamily='Arial')
    ax.set_ylim(0,10)
    ax.set_title('Perfil comparativo: AOEN vs selecionados',fontsize=13,fontfamily='Arial',fontweight='bold',pad=20)
    ax.legend(loc='upper right',bbox_to_anchor=(1.3,1.1),fontsize=10)
    plt.tight_layout()
    plt.savefig('fig4_radar.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig4 OK")

def fig5():
    fig, ax = plt.subplots(1,1,figsize=(16,8))
    cr = ["Core\nDiferenciador","Visao de\nMercado","Multi-\nInterface","Configura-\nbilidade","Isolamento\nProcess.","Consideracao\nde Custo","Moneti-\nzacao","Evolucao","Coerencia"]
    data = {"aoen":[8.6,8.9,9.4,7.5,5.7,4.4,4.3,8.7,8.5],"clean_arch":[5.4,4.7,3.4,4.1,3.4,2.2,3.3,6.9,6.3],"hexagonal":[7.5,5.9,9.0,5.0,6.4,4.6,5.0,8.6,8.0],"12factor":[5.0,3.4,4.6,5.1,7.6,5.0,2.7,7.9,7.8],"evolutionary":[6.5,5.3,4.2,5.4,6.8,5.9,2.6,9.0,8.1],"arch_flow":[8.1,8.0,5.7,6.0,6.9,5.8,7.1,8.0,8.1],"sem_framework":[5.8,7.7,8.1,3.5,6.6,6.5,4.6,6.6,7.7]}
    x = np.arange(len(cr)); w = 0.11
    for i,(k,l) in enumerate(zip(KEYS,LABELS)):
        ax.bar(x+i*w-3*w,data[k],w,label=l,color=COLORS[k],edgecolor='black',linewidth=0.5)
    ax.set_xlabel('Criterio de Avaliacao',fontsize=11,fontfamily='Arial')
    ax.set_ylabel('Nota Media (0-10)',fontsize=11,fontfamily='Arial')
    ax.set_title('Comparacao de abordagens arquiteturais por criterio',fontsize=13,fontfamily='Arial',fontweight='bold')
    ax.set_xticks(x);ax.set_xticklabels(cr,fontsize=9,fontfamily='Arial');ax.set_ylim(0,10.5)
    ax.legend(fontsize=9,ncol=7,loc='upper center',bbox_to_anchor=(0.5,-0.12))
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig('fig5_criterios.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig5 OK")

def fig6():
    fig, ax = plt.subplots(1,1,figsize=(10,6))
    ep = [44,28,30,31,30,58,32]; lo = [4027,5347,4998,1851,3714,6866,1627]; sv = [49,4,59,15,33,55,0]
    ax.scatter(lo,ep,s=[s*8+50 for s in sv],c=C,edgecolors='black',linewidth=1.5,zorder=5)
    for i,l in enumerate(LABELS):
        ox,oy = 150,1.5
        if i==0: oy=3
        ax.annotate(l,(lo[i],ep[i]),xytext=(ox,oy),textcoords='offset points',fontsize=9,fontfamily='Arial',fontweight='bold' if i==0 else 'normal',bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor=C[i],linewidth=1.2))
    ax.set_xlabel('Linhas de Codigo Funcional',fontsize=11,fontfamily='Arial')
    ax.set_ylabel('Endpoints de API',fontsize=11,fontfamily='Arial')
    ax.set_title('Eficiencia: endpoints entregues vs codigo necessario\n(tamanho do ponto = quantidade de servicos)',fontsize=12,fontfamily='Arial',fontweight='bold')
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig('fig6_eficiencia_poc.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig6 OK")

def fig7():
    fig, ax = plt.subplots(1,1,figsize=(10,6))
    cat = ["Service\nLayer","Core\nIsolado","Config\nTenant","Testes"]
    d = {"aoen":[3,3,3,0],"clean_arch":[1,0,1,0],"hexagonal":[3,3,0,0],"12factor":[2,0,3,0],"evolutionary":[3,2,2,3],"arch_flow":[2,3,1,0],"sem_framework":[0,0,0,0]}
    x = np.arange(len(cat));w = 0.11
    for i,k in enumerate(KEYS):
        ax.bar(x+i*w-3*w,d[k],w,label=LABELS[i],color=COLORS[k],edgecolor='black',linewidth=0.5)
    ax.set_xlabel('Decisao Arquitetural',fontsize=11,fontfamily='Arial')
    ax.set_ylabel('Presenca nos 3 projetos (0-3)',fontsize=11,fontfamily='Arial')
    ax.set_title('Decisoes arquiteturais presentes no codigo gerado',fontsize=12,fontfamily='Arial',fontweight='bold')
    ax.set_xticks(x);ax.set_xticklabels(cat,fontsize=10,fontfamily='Arial');ax.set_ylim(0,3.8);ax.set_yticks([0,1,2,3])
    ax.legend(fontsize=8,ncol=7,loc='upper center',bbox_to_anchor=(0.5,-0.15))
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig('fig7_decisoes_poc.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig7 OK")

def fig8():
    fig, ax = plt.subplots(1,1,figsize=(10,6))
    lo = ["AOEN","Arch\nFlow","Sem\nFW","Hexagonal","Evolu-\ntionary","12-\nFactor","Clean\nArch"]
    ko = ["aoen","arch_flow","sem_framework","hexagonal","evolutionary","12factor","clean_arch"]
    neg = [37,45,3,9,10,5,12]; tec = [10,14,2,15,20,12,35]
    co = [COLORS[k] for k in ko]
    x = np.arange(len(lo));w = 0.35
    ax.bar(x-w/2,neg,w,label='Mencoes a negocio',color=co,edgecolor='black',linewidth=0.5)
    ax.bar(x+w/2,tec,w,label='Mencoes tecnicas',color='white',edgecolor=[co[i] for i in range(len(co))],linewidth=1.5,hatch='///')
    ax.set_xlabel('Abordagem',fontsize=11,fontfamily='Arial')
    ax.set_ylabel('Quantidade de mencoes nos READMEs',fontsize=11,fontfamily='Arial')
    ax.set_title('Orientacao a negocio vs tecnica na documentacao gerada',fontsize=12,fontfamily='Arial',fontweight='bold')
    ax.set_xticks(x);ax.set_xticklabels(lo,fontsize=9,fontfamily='Arial')
    ax.legend(fontsize=10)
    ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
    for s in ax.spines.values():s.set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig('fig8_negocio_vs_tecnica.png',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close()
    print("fig8 OK")

if __name__ == '__main__':
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6(); fig7(); fig8()
    print("\nTodos os graficos regenerados com cores!")
