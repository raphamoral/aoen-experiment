# -*- coding: utf-8 -*-
"""
Estudo de ablação — isolando o efeito do prompt do efeito do framework.

A rodada principal (v4) tem uma assimetria conhecida entre os braços: o prompt
do AOEN é 3,3x mais longo que a média dos concorrentes, menciona oito dos nove
critérios da rubrica, e — o mais relevante — exige um esquema de resposta com
17 campos, dez dos quais mapeiam diretamente nos critérios avaliados, contra
10 a 13 campos e 3 a 4 mapeamentos dos concorrentes.

Isso é uma variável de confusão: não se sabe se a vantagem do AOEN vem do
framework ou de o prompt entregar ao modelo um formulário alinhado à rubrica.

Este módulo define três braços de controle que rodam sobre uma subamostra das
mesmas ideias. Todos os três usam o MESMO esquema genérico de saída dos braços
concorrentes, de modo que a única coisa que varia entre eles é o conteúdo
instrucional.

  aoen_reduzido    conteúdo do framework comprimido ao tamanho médio dos
                   concorrentes, com esquema genérico. Responde: o raciocínio
                   do AOEN ajuda quando a saída é estruturada como a dos outros?

  placebo_verboso  conselho genérico de arquitetura, com o comprimento do
                   prompt do AOEN mas sem seus conceitos. Isola o efeito do
                   comprimento puro.

  linha_de_base    só a ideia e o esquema. Sem framework nomeado e sem
                   proibição. É o piso ausente na rodada principal — note que
                   o braço "sem_framework" da v4 não é um controle neutro: ele
                   PROÍBE o uso de padrões, o que o penaliza ativamente.

NÃO substitui a rodada v4. É um estudo complementar, com n menor e pergunta
própria.
"""
import random

# ---------------------------------------------------------------------------
# Subamostra: 30 ideias sorteadas com semente fixa.
# Nunca escolhidas a dedo — seleção manual seria outra variável de confusão.
# ---------------------------------------------------------------------------
SEMENTE = 42
N_IDEIAS = 30
IDEIAS_ABLACAO = sorted(random.Random(SEMENTE).sample(range(100), N_IDEIAS))

# ---------------------------------------------------------------------------
# Esquema de saída — cópia literal do usado pelos braços concorrentes na v4.
# Mantido idêntico de propósito: trocar o instrumento no meio do estudo
# invalidaria a comparação com os dados já coletados.
# ---------------------------------------------------------------------------
ESQUEMA_GENERICO = """{{
  "o_que_construir": "O que você vai construir?",
  "como_comecar": "Por onde começa?",
  "tecnologias": "Que tecnologias usaria?",
  "banco_dados": "Como armazena dados?",
  "interfaces": ["Interfaces previstas"],
  "usuarios": "Quem vai usar?",
  "escalabilidade": "Pensou em escala? Como?",
  "custos": "Pensou em custos operacionais?",
  "monetizacao": "Como o produto se monetiza?",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""


# ---------------------------------------------------------------------------
# BRAÇO 1 — AOEN reduzido
# ---------------------------------------------------------------------------
PROMPT_AOEN_REDUZIDO = """Você é um arquiteto de software que segue o framework AOEN (Arquitetura Orgânica Orientada a Estratégia de Negócio), cujo princípio central é que toda decisão arquitetural deve preservar a capacidade do sistema de evoluir.

Aplique as quatro fases do framework:
1. Núcleo e mercado: identifique o componente diferenciador, sem o qual o produto não existe, e o mercado que ele atende.
2. Interfaces: mapeie os contextos em que o usuário opera e priorize interfaces pelo mercado que abrem.
3. Configuração: mantenha o fluxo fixo no código e torne parametrizável o que varia entre clientes.
4. Isolamento: separe o processamento pesado em execução independente e mensurável.

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Responda em JSON:
""" + ESQUEMA_GENERICO


# ---------------------------------------------------------------------------
# BRAÇO 2 — Placebo verboso
# Mesmo comprimento do prompt do AOEN, densidade comparável, e nenhum dos seus
# conceitos: não menciona núcleo diferenciador, configurabilidade por cliente,
# isolamento de processamento, custo por cliente nem monetização como objetivo.
# ---------------------------------------------------------------------------
PROMPT_PLACEBO_VERBOSO = """Você é um arquiteto de software experiente, com longa prática em sistemas de produção. Projete a arquitetura com o cuidado que um sistema destinado a durar exige, aplicando julgamento maduro de engenharia em cada decisão.

Considere os seguintes aspectos no seu raciocínio:

ORGANIZAÇÃO DO CÓDIGO:
- Escolha uma estrutura de diretórios que comunique a intenção do sistema a quem chegar depois
- Estabeleça convenções de nomenclatura consistentes e aplique-as sem exceção
- Mantenha os módulos com responsabilidades bem delimitadas e fronteiras explícitas
- Prefira composição a herança quando ambas resolverem o problema

MODELAGEM DE DADOS:
- Defina as entidades a partir do vocabulário do domínio, não da conveniência da implementação
- Decida cedo entre normalização e desnormalização, e registre a razão da escolha
- Planeje a estratégia de migração de esquema antes da primeira versão em produção
- Considere os padrões de leitura e escrita esperados ao escolher índices

INTERFACES DE PROGRAMAÇÃO:
- Projete contratos estáveis, que possam evoluir sem quebrar os consumidores existentes
- Adote uma política de versionamento explícita desde a primeira publicação
- Padronize o formato de erros e o tratamento de casos de borda
- Documente cada contrato junto ao código que o implementa

QUALIDADE E CONFIABILIDADE:
- Defina a estratégia de testes em camadas, com critérios claros do que cada camada cobre
- Instrumente o sistema com logs estruturados e métricas desde o início
- Planeje como o sistema se comporta sob falha parcial de suas dependências
- Estabeleça o processo de revisão de código e os critérios de aceitação

ENTREGA E OPERAÇÃO:
- Automatize a construção e a publicação de artefatos de forma reproduzível
- Separe configuração de ambiente do código da aplicação
- Planeje a estratégia de reversão antes de precisar dela
- Defina como as dependências externas serão atualizadas e auditadas

SEGURANÇA:
- Trate autenticação e autorização como preocupações distintas
- Valide entradas na fronteira do sistema e não confie em dados externos
- Registre decisões sobre armazenamento de dados sensíveis

DESEMPENHO:
- Estabeleça orçamentos de latência para as operações mais frequentes do sistema
- Identifique de antemão quais consultas tendem a degradar com o volume de dados
- Decida onde vale manter resultados intermediários em memória e por quanto tempo
- Meça antes de otimizar, e mantenha o resultado da medição junto da decisão

DOCUMENTAÇÃO E RASTREABILIDADE:
- Registre as decisões técnicas relevantes com o contexto que as motivou
- Mantenha um diagrama de alto nível atualizado junto ao repositório
- Descreva as dependências entre componentes de forma que um recém-chegado entenda
- Deixe explícito o que foi deliberadamente deixado de fora do escopo inicial

DÍVIDA TÉCNICA:
- Distinga o atalho consciente, com prazo de correção, do descuido acidental
- Mantenha um registro dos pontos que precisarão ser revisitados
- Estabeleça quando uma reescrita parcial é preferível a uma sucessão de remendos
- Evite abstrações prematuras: espere o terceiro caso antes de generalizar

COLABORAÇÃO E MANUTENÇÃO:
- Escreva o código pensando em quem vai lê-lo daqui a um ano, inclusive você
- Prefira soluções óbvias a soluções engenhosas quando ambas resolverem
- Mantenha o tempo de configuração de um ambiente novo na casa dos minutos
- Trate mensagens de commit e histórico como parte da documentação do sistema

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Responda em JSON:
""" + ESQUEMA_GENERICO


# ---------------------------------------------------------------------------
# BRAÇO 3 — Linha de base neutra
# Sem framework nomeado, sem proibição, sem orientação. O piso.
# ---------------------------------------------------------------------------
PROMPT_LINHA_BASE = """Projete a arquitetura do seguinte produto SaaS:

"{ideia}"

Responda em JSON:
""" + ESQUEMA_GENERICO


ABORDAGENS = {
    "aoen_reduzido": PROMPT_AOEN_REDUZIDO,
    "placebo_verboso": PROMPT_PLACEBO_VERBOSO,
    "linha_de_base": PROMPT_LINHA_BASE,
}

# o avaliador é o mesmo da rodada principal — instrumento inalterado
from experimento_aoen import PROMPT_AVALIADOR  # noqa: E402,F401


if __name__ == "__main__":
    import re
    from experimento_aoen import ABORDAGENS as ORIG

    def campos(t):
        return len(re.findall(r'"([a-z0-9_]+)":', t.split("Responda em JSON")[-1]))

    print(f"subamostra ({N_IDEIAS} ideias, semente {SEMENTE}):")
    print(" ", IDEIAS_ABLACAO, "\n")
    print(f"{'braço':18s} {'chars':>6s} {'campos':>7s}")
    print("  --- rodada principal (referência) ---")
    for k, v in sorted(ORIG.items(), key=lambda x: -len(x[1])):
        print(f"{k:18s} {len(v):6d} {campos(v):7d}")
    alvo = sum(len(v) for k, v in ORIG.items() if k != "aoen") / 6
    print(f"\n  média dos seis concorrentes: {alvo:.0f} chars")
    print("  --- braços de ablação ---")
    for k, v in ABORDAGENS.items():
        print(f"{k:18s} {len(v):6d} {campos(v):7d}")
