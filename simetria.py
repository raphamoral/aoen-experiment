# -*- coding: utf-8 -*-
"""
Estudo de simetria de esquema — nivelando a exigência entre os braços.

MOTIVAÇÃO
Na rodada principal (v4) o prompt do AOEN exigia um esquema de resposta com 17
campos, dez deles mapeando diretamente nos critérios da rubrica, e com exemplos
trabalhados ("Ex: 'Cada análise IA = $0.05 (API) + ...'"). Os concorrentes
respondiam de 10 a 13 campos, com 3 a 4 mapeamentos, e perguntas retóricas no
lugar dos exemplos ("Pensou em custos operacionais?").

Essa assimetria é uma variável de confusão: não se sabe se a vantagem do AOEN
vem do framework ou de o prompt entregar um formulário alinhado à rubrica.

DESENHO
A correção aplicada aqui é nivelar PARA CIMA, não para baixo: em vez de
encolher o AOEN — o que testaria uma caricatura do framework —, cada concorrente
recebe um esquema igualmente rico, expresso no vocabulário canônico da sua
própria fonte, mais a mesma cauda genérica exigente que o AOEN recebeu.

  <framework>_rico    11 campos do vocabulário canônico da fonte + 6 campos da
                      cauda genérica, idênticos aos do AOEN = 17 campos

  linha_base_rica     instrução neutra (sem framework nomeado, sem proibição)
                      com esquema rico de 17 campos. É o controle decisivo: se
                      um prompt neutro com formulário rico pontuar como o AOEN,
                      então o efeito medido era o formulário, não o framework.

  linha_base_simples  instrução neutra com o esquema genérico de 10 campos.
                      O piso.

O braço do AOEN não é reexecutado: reaproveitam-se as respostas da v4 para as
mesmas 30 ideias, geradas com o mesmo modelo e o mesmo prompt.

NÃO substitui a rodada v4. Estudo complementar, com n menor e pergunta própria.
"""
from ablacao import IDEIAS_ABLACAO, SEMENTE, N_IDEIAS  # noqa: F401
from experimento_aoen import PROMPT_AVALIADOR  # noqa: F401

# ---------------------------------------------------------------------------
# Cauda genérica — copiada literalmente do prompt do AOEN da rodada v4.
# É o equalizador: mesma exigência, mesmos exemplos, para todos os braços.
# ---------------------------------------------------------------------------
CAUDA = """  "interfaces": ["Lista de interfaces identificadas"],
  "escalabilidade": "Como o sistema escala com o crescimento da base de clientes?",
  "custo_infra_estimado": "Estimativa de custo mensal de infraestrutura com valores em dólares ou reais: servidor, banco, CDN, armazenamento, banda. Ex: 'Servidor: $50/mês, RDS: $30/mês, S3: $10/mês'",
  "custo_por_cliente": "Custo por cliente/operação com cálculo detalhado. Ex: 'Cada análise IA = $0.05 (API) + $0.01 (storage) + $0.003 (CPU) = $0.063/operação. Cliente com 100 operações/mês = $6.30/mês'",
  "monetizacao": "Modelo de monetização detalhado: tiers, valores por plano, métricas (MRR, LTV, CAC)",
  "stack_sugerida": "Pilha tecnológica sugerida\""""


def montar(intro, campos_proprios):
    return (intro + """

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Responda em JSON com a seguinte estrutura:
{{
""" + campos_proprios + ",\n" + CAUDA + """
}}

Responda APENAS o JSON, sem texto adicional.""")


# --------------------------------------------------------------- Clean Arch
# Campos derivados de Martin (2017), Clean Architecture.
CLEAN = montar(
"""Você é um arquiteto de software que segue estritamente a Clean Architecture de Robert C. Martin.

A regra fundamental é a Regra de Dependência: dependências de código-fonte apontam apenas para dentro, em direção a políticas de mais alto nível. Entidades no centro, casos de uso ao redor, adaptadores de interface em seguida, frameworks e drivers na borda. Detalhes dependem de políticas; políticas nunca dependem de detalhes.""",
"""  "entities": "Entidades de negócio e as regras críticas que elas encapsulam",
  "use_cases": "Casos de uso da aplicação e as regras específicas de aplicação de cada um",
  "interface_adapters": "Adaptadores que convertem dados entre casos de uso e agentes externos",
  "frameworks_drivers": "Frameworks, banco de dados e drivers mantidos na camada mais externa",
  "dependency_rule": "Como a regra de dependência é garantida na prática, com inversão onde necessário",
  "boundaries": "Fronteiras arquiteturais traçadas e o que cada uma protege",
  "crossing_boundaries": "Estruturas de dados que cruzam fronteiras e em que direção",
  "testability": "Como as regras de negócio são testadas sem banco, sem web e sem framework",
  "screaming_architecture": "Como a estrutura de diretórios comunica o domínio, e não o framework",
  "humble_object": "Onde o padrão Humble Object separa o difícil de testar do testável",
  "independence": "Independência de desenvolvimento e de implantação entre componentes""")

# --------------------------------------------------------------- Hexagonal
# Campos derivados de Cockburn (2005), Ports and Adapters.
HEX = montar(
"""Você é um arquiteto de software que segue estritamente a Hexagonal Architecture (Ports & Adapters) de Alistair Cockburn.

A aplicação é isolada no centro e se comunica com o exterior apenas por portas. Cada porta é um contrato; cada adaptador é uma implementação intercambiável desse contrato. Há simetria entre o lado que aciona a aplicação e o lado que é acionado por ela.""",
"""  "domain_core": "Domínio isolado e as regras que ele contém, sem dependência de tecnologia",
  "driving_ports": "Portas primárias: contratos pelos quais a aplicação é acionada",
  "driven_ports": "Portas secundárias: contratos pelos quais a aplicação aciona o exterior",
  "driving_adapters": "Adaptadores primários previstos e o que cada um expõe",
  "driven_adapters": "Adaptadores secundários previstos: persistência, mensageria, serviços externos",
  "application_services": "Serviços de aplicação que orquestram o domínio sem conter regra de negócio",
  "domain_isolation": "Como o domínio permanece ignorante de qualquer tecnologia de borda",
  "test_doubles": "Como cada porta é substituída por dublê em teste",
  "configuration_wiring": "Como adaptadores são ligados às portas na inicialização",
  "technology_substitution": "Que tecnologia de borda poderia ser trocada e a que custo",
  "symmetry": "Como a simetria entre os dois lados é preservada""")

# --------------------------------------------------------------- 12-Factor
# Campos derivados de Wiggins (2011), The Twelve-Factor App.
FACTOR = montar(
"""Você é um arquiteto de software que segue estritamente o Twelve-Factor App de Adam Wiggins.

A aplicação é declarativa na automação da configuração, tem contrato limpo com o sistema operacional, é apta a implantação em plataformas de nuvem, minimiza divergência entre desenvolvimento e produção e escala sem mudança significativa de arquitetura.""",
"""  "codebase": "Base de código única sob controle de versão, com múltiplas implantações",
  "dependencies": "Declaração e isolamento explícitos de dependências",
  "config": "Configuração no ambiente, e o que exatamente varia entre implantações",
  "backing_services": "Serviços de apoio tratados como recursos anexados e intercambiáveis",
  "build_release_run": "Separação estrita entre construção, versão e execução",
  "processes": "Processos sem estado, e onde o estado persistente de fato reside",
  "port_binding": "Exportação de serviços por vinculação de porta",
  "concurrency": "Escala por modelo de processos e tipos de processo previstos",
  "disposability": "Inicialização rápida e desligamento gracioso",
  "dev_prod_parity": "Como as divergências de tempo, pessoal e ferramenta são reduzidas",
  "logs_admin": "Logs como fluxo de eventos e processos administrativos pontuais""")

# --------------------------------------------------------------- Evolutionary
# Campos derivados de Ford, Parsons e Kua (2017), Building Evolutionary Architectures.
EVO = montar(
"""Você é um arquiteto de software que segue a Evolutionary Architecture de Neal Ford, Rebecca Parsons e Patrick Kua.

A arquitetura suporta mudança guiada e incremental ao longo de múltiplas dimensões, e essa capacidade é protegida por funções de aptidão que verificam objetivamente se as características desejadas continuam válidas conforme o sistema evolui.""",
"""  "architectural_quantum": "Quantum arquitetural: a menor unidade implantável independentemente",
  "fitness_functions": "Funções de aptidão definidas e o que cada uma verifica objetivamente",
  "evolvable_dimensions": "Dimensões que precisam evoluir: técnica, dados, segurança, operacional",
  "incremental_change": "Como a mudança é feita de forma incremental e guiada",
  "coupling_management": "Acoplamento aferente e eferente entre componentes, e o que é deliberado",
  "deployment_pipeline": "Pipeline que executa as funções de aptidão de forma contínua",
  "data_evolution": "Como o esquema de dados evolui sem interromper o serviço",
  "experimentation": "Como hipóteses de produto são testadas na arquitetura",
  "sacrificial_parts": "Que partes são deliberadamente descartáveis e quando serão substituídas",
  "guardrails": "Limites que impedem a erosão arquitetural ao longo do tempo",
  "tradeoffs": "Compromissos assumidos entre as dimensões evolutivas""")

# --------------------------------------------------------------- Arch for Flow
# Campos derivados de Kaiser (2023), Architecture for Flow.
FLOW = montar(
"""Você é um arquiteto de software que segue Architecture for Flow de Susanne Kaiser, combinando Domain-Driven Design, Wardley Mapping e Team Topologies.

A arquitetura é desenhada para otimizar o fluxo de valor: o mapa de evolução dos componentes orienta o que construir e o que comprar, os limites de domínio orientam a decomposição, e a topologia de times orienta quem é dono de quê.""",
"""  "value_chain": "Cadeia de valor do produto, da necessidade do usuário aos componentes",
  "wardley_map": "Posição de cada componente no eixo de evolução: gênese, sob medida, produto, commodity",
  "build_buy_decisions": "O que construir, o que comprar e o que usar como commodity, com a razão",
  "core_domain": "Domínio central que justifica investimento sob medida",
  "bounded_contexts": "Contextos delimitados identificados e a linguagem ubíqua de cada um",
  "context_mapping": "Relações entre contextos: parceria, cliente-fornecedor, camada anticorrupção",
  "team_topologies": "Tipos de time previstos: fluxo, plataforma, subsistema complicado, habilitação",
  "cognitive_load": "Como a carga cognitiva de cada time é mantida dentro do limite",
  "interaction_modes": "Modos de interação entre times: colaboração, X-as-a-Service, facilitação",
  "flow_optimization": "Como o fluxo de valor é otimizado e onde estão os gargalos",
  "independent_streams": "Como os fluxos de valor permanecem independentes entre si""")

# --------------------------------------------------------------- Linha de base rica
# Sem framework nomeado, sem proibição, esquema rico e neutro.
# Controle decisivo: isola o efeito do formulário.
BASE_RICA = montar(
"""Você é um arquiteto de software experiente. Projete a arquitetura do produto descrito a seguir, detalhando cada aspecto solicitado.""",
"""  "o_que_construir": "O que será construído e qual problema resolve",
  "publico_alvo": "Quem usa o produto e em que contexto",
  "componente_central": "Qual componente é o mais importante do sistema e por quê",
  "fluxo_principal": "Fluxo principal de dados, da entrada à saída",
  "decomposicao": "Como o sistema é decomposto em partes e por que assim",
  "modelo_dados": "Entidades principais e como são armazenadas",
  "contratos": "Contratos entre as partes do sistema",
  "variacao_por_cliente": "O que pode variar de um cliente para outro e como isso é tratado",
  "processamento_pesado": "Que processamento é caro ou demorado e como é executado",
  "falhas": "Como o sistema se comporta sob falha de suas partes",
  "manutencao": "Como o sistema é mantido e alterado ao longo do tempo""")

# --------------------------------------------------------------- Linha de base simples
from ablacao import ESQUEMA_GENERICO  # noqa: E402

BASE_SIMPLES = """Projete a arquitetura do seguinte produto SaaS:

"{ideia}"

Responda em JSON:
""" + ESQUEMA_GENERICO


ABORDAGENS = {
    "clean_arch_rico": CLEAN,
    "hexagonal_rico": HEX,
    "12factor_rico": FACTOR,
    "evolutionary_rico": EVO,
    "arch_flow_rico": FLOW,
    "linha_base_rica": BASE_RICA,
    "linha_base_simples": BASE_SIMPLES,
}


if __name__ == "__main__":
    import re
    from experimento_aoen import ABORDAGENS as V4

    def campos(t):
        return len(re.findall(r'"([a-z0-9_]+)":', t.split("estrutura:")[-1].split("Responda em JSON")[-1]))

    print(f"{'braço':22s} {'chars':>6s} {'campos':>7s}")
    print("  --- referência v4 ---")
    for k in ("aoen", "clean_arch", "hexagonal", "12factor", "evolutionary", "arch_flow"):
        print(f"{k:22s} {len(V4[k]):6d} {campos(V4[k]):7d}")
    print("  --- braços nivelados ---")
    for k, v in ABORDAGENS.items():
        print(f"{k:22s} {len(v):6d} {campos(v):7d}")
    print(f"\nideias: {N_IDEIAS} (semente {SEMENTE})")
    print(f"chamadas: {len(ABORDAGENS)*N_IDEIAS} gerações + {len(ABORDAGENS)*N_IDEIAS} avaliações")
