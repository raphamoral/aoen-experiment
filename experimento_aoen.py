# -*- coding: utf-8 -*-
"""
Experimento AOEN: 100 ideias x 7 abordagens = 700 execuções.
Gera ideias, executa agentes, consolida resultados e gera gráficos.
"""
import json
import os
import subprocess
import random
import time
from pathlib import Path

# =====================================================================
# 100 IDEIAS DE SAAS/PRODUTO
# =====================================================================

IDEIAS = [
    "Plataforma de telemedicina veterinária com IA para diagnóstico por imagem",
    "SaaS de gestão de frotas para entregas last-mile com rastreamento em tempo real",
    "Marketplace de freelancers especializados em compliance regulatório",
    "App de monitoramento de saúde mental para empresas com relatórios anônimos",
    "Plataforma de leilão reverso para compras corporativas de TI",
    "SaaS de automação de contratos imobiliários com assinatura digital",
    "App de nutrição personalizada com IA baseada em exames laboratoriais",
    "Plataforma de microlearning gamificado para treinamento corporativo",
    "SaaS de gestão de resíduos industriais com rastreabilidade blockchain",
    "Marketplace de equipamentos médicos usados com certificação de qualidade",
    "App de gestão financeira para MEIs com emissão automática de nota fiscal",
    "Plataforma de matchmaking entre startups e investidores-anjo regionais",
    "SaaS de monitoramento de qualidade do ar para indústrias",
    "App de reserva e gestão de espaços de coworking descentralizados",
    "Plataforma de tradução simultânea para reuniões corporativas multilíngues",
    "SaaS de precificação dinâmica para e-commerces de moda",
    "App de logística reversa para devoluções de e-commerce",
    "Plataforma de certificação digital de cursos livres com verificação pública",
    "SaaS de análise preditiva de churn para operadoras de telecom",
    "App de agendamento inteligente para clínicas odontológicas",
    "Plataforma de crowdsourced testing de software com gamificação",
    "SaaS de gestão de manutenção predial preventiva com IoT",
    "Marketplace de ingredientes orgânicos B2B para restaurantes",
    "App de assistente jurídico com IA para pequenos escritórios",
    "Plataforma de gestão de licenças de software corporativo",
    "SaaS de otimização de rotas para coleta de lixo reciclável",
    "App de acompanhamento pós-operatório com IA e teleconsulta",
    "Plataforma de gestão de eventos corporativos híbridos",
    "SaaS de compliance LGPD automatizado para PMEs",
    "Marketplace de profissionais de energia solar para residências",
    "App de controle de estoque com visão computacional para varejo",
    "Plataforma de mentoria online pareada por IA",
    "SaaS de análise de sentimento de reviews para hotelaria",
    "App de gestão de condomínios com votação digital e transparência financeira",
    "Plataforma de simulação financeira para planejamento de aposentadoria",
    "SaaS de detecção de fraudes em transações de marketplace",
    "App de gestão de prescrições médicas com alerta de interações medicamentosas",
    "Plataforma de orçamento automatizado para reformas residenciais",
    "SaaS de monitoramento de concorrentes para e-commerce",
    "Marketplace de serviços de drone para agricultura de precisão",
    "App de triagem médica com IA para pronto-atendimento",
    "Plataforma de gestão de portfólio de patentes para empresas de tecnologia",
    "SaaS de automação de relatórios ESG para empresas listadas",
    "App de comparação de planos de saúde com recomendação personalizada",
    "Plataforma de recrutamento técnico com avaliação automatizada de código",
    "SaaS de gestão de cadeia de frio para transporte farmacêutico",
    "App de personal trainer virtual com IA e visão computacional",
    "Plataforma de arbitragem online para disputas de pequeno valor",
    "SaaS de previsão de demanda para supermercados regionais",
    "Marketplace de profissionais de acessibilidade digital",
    "App de gestão de frotas de bicicletas compartilhadas para cidades",
    "Plataforma de due diligence automatizada para fusões e aquisições",
    "SaaS de gestão de qualidade para indústria alimentícia com APPCC",
    "App de rastreamento de hábitos sustentáveis com gamificação corporativa",
    "Plataforma de criação de chatbots customizados sem código para PMEs",
    "SaaS de gestão de turnos para hospitais com otimização por IA",
    "Marketplace de peças industriais com entrega expressa regional",
    "App de controle parental inteligente com relatórios de bem-estar digital",
    "Plataforma de seguro parametrizado para agricultura familiar",
    "SaaS de automação de onboarding de funcionários com workflows configuráveis",
    "App de inspeção predial com realidade aumentada e checklist digital",
    "Plataforma de matching entre ONGs e voluntários por competências",
    "SaaS de gestão de royalties para editoras musicais independentes",
    "App de detecção de pragas agrícolas por fotografia com IA",
    "Plataforma de licitação eletrônica simplificada para prefeituras",
    "SaaS de análise de produtividade de equipes remotas sem invasão de privacidade",
    "Marketplace de serviços de tradução técnica com especialização por indústria",
    "App de gestão de pacientes crônicos com alertas proativos",
    "Plataforma de financiamento coletivo para projetos de infraestrutura local",
    "SaaS de automação de testes de acessibilidade web com relatórios WCAG",
    "App de gestão de pet shops com agendamento e prontuário veterinário",
    "Plataforma de certificação de origem para cadeias de café especial",
    "SaaS de previsão de falhas em máquinas industriais com machine learning",
    "App de coaching de comunicação com análise de voz por IA",
    "Plataforma de gestão de propriedade intelectual para universidades",
    "SaaS de orquestração de microsserviços com observabilidade integrada",
    "Marketplace de serviços de reabilitação pós-COVID com teleconsulta",
    "App de gestão de fazendas solares com monitoramento IoT",
    "Plataforma de empréstimo entre pessoas com scoring alternativo por IA",
    "SaaS de gestão de recall de produtos com rastreabilidade por lote",
    "App de realidade aumentada para treinamento de operadores industriais",
    "Plataforma de gestão de créditos de carbono para PMEs",
    "SaaS de automação de atendimento ao cliente com IA conversacional multicanal",
    "Marketplace de materiais de construção sustentáveis com certificação ambiental",
    "App de diagnóstico automotivo por OBD com recomendação de oficinas",
    "Plataforma de gestão de programas de fidelidade multi-marca",
    "SaaS de análise de risco para seguradoras de nicho",
    "App de gestão de quadras esportivas com reserva e pagamento integrado",
    "Plataforma de supply chain finance para pequenos fornecedores",
    "SaaS de planejamento de safra com dados climáticos e satelitais",
    "App de gestão de clínicas de fisioterapia com evolução por sessão",
    "Plataforma de ensino de programação para crianças com IA adaptativa",
    "SaaS de gestão de contratos SaaS para empresas com otimização de licenças",
    "Marketplace de serviços de cibersegurança para PMEs",
    "App de gestão de obras com timeline visual e controle de custos em tempo real",
    "Plataforma de telemedicina especializada em dermatologia com análise de imagem",
    "SaaS de automação de processos de RH para empresas em expansão internacional",
    "App de matchmaking de caronas corporativas com roteirização inteligente",
    "Plataforma de gestão de franquias com padronização e benchmarking entre unidades",
    "SaaS de monitoramento de reputação online com análise de sentimento para marcas",
]

# =====================================================================
# PROMPTS POR ABORDAGEM
# =====================================================================

PROMPT_AOEN = """Você é um arquiteto de software que segue o framework AOEN (Arquitetura Orgânica Orientada a Estratégia de Negócio).

O AOEN tem um princípio central: "Toda decisão arquitetural deve preservar a capacidade do sistema de evoluir — crescer sem quebrar."

O framework se estrutura em 4 fases sequenciais:

FASE 1 - NÚCLEO + VISÃO DE MERCADO (VALOR):
Pergunta: "O que construir e para quem?"
- Identificar o núcleo diferenciador do produto (o coração — sem ele o produto não existe)
- Usar abstração deliberada: afastar-se das tecnologias, enxergar o sistema como fluxo de entradas/transformação/saídas
- O núcleo deve ser extensível (não depender de um único fornecedor)

FASE 2 - MULTI-INTERFACE ADAPTATIVA (ALCANCE):
Pergunta: "Onde está o usuário?"
- Mapear perfis de usuário e seu contexto operacional (onde estão, que dispositivos usam, que complexidade toleram)
- Cada interface é uma porta de entrada para um segmento de mercado
- Priorizar interfaces pelo mercado que abrem, não por conveniência técnica
- Usar Service Layer para desacoplar lógica de negócio das interfaces

FASE 3 - CONFIGURATION-DRIVEN (ESCALA):
Pergunta: "Como escalar clientes sem custo de engenharia?"
- Critério: "O que consigo tornar genérico o suficiente para servir N contextos?"
- Fluxo é fixo no código, parâmetros são configuráveis
- Novo cliente = novos parâmetros, não novo código
- Funções genéricas que absorvem demanda crescente ao longo do tempo

FASE 4 - ISOLAMENTO DE PROCESSAMENTO (CUSTO + MEDIÇÃO):
Pergunta: "Quanto custa cada cliente e como não gastar à toa?"
- Identificar o core da Fase 1 e isolá-lo (é o coração — se parar, o produto morre)
- Três razões: continuidade operacional, manutenibilidade, e custo total mensurável
- Custo total por cliente = custo do core (IA, GPU, API) + custo de infra proporcional (servidor, banco, CDN, armazenamento, banda) + custos operacionais
- Sem saber o custo total por cliente, não é possível precificar corretamente
- Processamento pesado em processos separados, assíncronos, escaláveis independentemente

OBJETIVO FINAL: Monetização viável — software economicamente sustentável desde o dia zero até a escala.

---

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Aplique as 4 fases do AOEN e responda em JSON com a seguinte estrutura:
{{
  "fase1_core": "Qual é o núcleo diferenciador?",
  "fase1_mercado": "Para quem? Qual mercado-alvo?",
  "fase1_extensivel": "O core é substituível/extensível? Como?",
  "fase2_interfaces": ["Lista de interfaces identificadas"],
  "fase2_justificativa_mercado": "Por que cada interface abre um mercado?",
  "fase2_service_layer": "Como a lógica fica desacoplada das interfaces?",
  "fase3_fluxo_fixo": "Qual fluxo é fixo no código?",
  "fase3_parametros_configuraveis": ["Lista de parâmetros configuráveis por cliente"],
  "fase3_novo_cliente": "Como onboardar novo cliente sem código?",
  "fase4_core_isolado": "Qual processo do core será isolado e como (subprocess, worker, fila)?",
  "fase4_custo_infra_estimado": "Estimativa de custo mensal de infraestrutura com valores em dólares ou reais: servidor, banco, CDN, armazenamento, banda. Ex: 'Servidor: $50/mês, RDS: $30/mês, S3: $10/mês'",
  "fase4_custo_por_cliente": "Custo por cliente/operação com cálculo detalhado. Ex: 'Cada análise IA = $0.05 (API) + $0.01 (storage) + $0.003 (CPU) = $0.063/operação. Cliente com 100 operações/mês = $6.30/mês'",
  "fase4_margem_por_cliente": "Receita por cliente - custo por cliente = margem. O negócio é sustentável?",
  "fase4_continuidade": "Como a falha do core não derruba o resto?",
  "fase4_manutencao": "Como trocar a tecnologia do core sem parar?",
  "monetizacao": "Modelo de monetização detalhado: tiers, valores por plano, métricas (MRR, LTV, CAC)",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""

PROMPT_CLEAN_ARCH = """Você é um arquiteto de software que segue estritamente a Clean Architecture de Robert C. Martin.

Princípios fundamentais:
- Separação em 4 camadas concêntricas: Entities, Use Cases, Interface Adapters, Frameworks & Drivers
- A Regra de Dependência: dependências de código-fonte só apontam para dentro
- Independência de framework, UI, banco de dados e agências externas
- Testabilidade sem dependências externas

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Projete a arquitetura seguindo Clean Architecture e responda em JSON:
{{
  "entities": "Quais são as entidades de negócio?",
  "use_cases": "Quais são os casos de uso principais?",
  "interface_adapters": "Quais adaptadores de interface são necessários?",
  "frameworks_drivers": "Quais frameworks e drivers serão usados?",
  "dependency_rule": "Como a regra de dependência é aplicada?",
  "testability": "Como o sistema será testável?",
  "interfaces": ["Interfaces previstas"],
  "escalabilidade": "Como o sistema escala?",
  "custos": "Considerações de custo operacional",
  "monetizacao": "Como o produto se monetiza?",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""

PROMPT_HEXAGONAL = """Você é um arquiteto de software que segue estritamente a Hexagonal Architecture (Ports & Adapters) de Alistair Cockburn.

Princípios fundamentais:
- Separação entre inside (lógica de negócio) e outside (infraestrutura)
- Ports são interfaces abstratas que definem conversas possíveis
- Adapters são implementações concretas que conectam ao mundo externo
- A aplicação pode ser dirigida igualmente por usuários, testes ou scripts
- Tratamento simétrico de todos os sistemas externos

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Projete a arquitetura seguindo Hexagonal Architecture e responda em JSON:
{{
  "core_domain": "Qual é o domínio central?",
  "primary_ports": ["Portas primárias (driving)"],
  "secondary_ports": ["Portas secundárias (driven)"],
  "primary_adapters": ["Adaptadores primários"],
  "secondary_adapters": ["Adaptadores secundários"],
  "isolation": "Como o core é isolado do mundo externo?",
  "interfaces": ["Interfaces previstas"],
  "escalabilidade": "Como o sistema escala?",
  "custos": "Considerações de custo operacional",
  "monetizacao": "Como o produto se monetiza?",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""

PROMPT_12FACTOR = """Você é um arquiteto de software que segue estritamente o manifesto The Twelve-Factor App de Adam Wiggins.

Os 12 fatores:
1. Codebase: Um codebase, muitos deploys
2. Dependencies: Declarar e isolar dependências
3. Config: Configuração no ambiente
4. Backing Services: Serviços de apoio como recursos
5. Build/Release/Run: Separar build e execução
6. Processes: Processos stateless
7. Port Binding: Exportar serviços via porta
8. Concurrency: Escalar via processos
9. Disposability: Startup rápido, shutdown gracioso
10. Dev/Prod Parity: Ambientes similares
11. Logs: Streams de eventos
12. Admin Processes: Tarefas admin como processos pontuais

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Projete a arquitetura seguindo os 12 Fatores e responda em JSON:
{{
  "codebase": "Estratégia de codebase",
  "dependencies": "Gestão de dependências",
  "config": "Estratégia de configuração",
  "backing_services": "Serviços de apoio necessários",
  "build_release_run": "Pipeline de deploy",
  "processes": "Modelo de processos",
  "concurrency": "Estratégia de concorrência e escala",
  "disposability": "Resiliência e disponibilidade",
  "interfaces": ["Interfaces previstas"],
  "escalabilidade": "Como o sistema escala?",
  "custos": "Considerações de custo operacional",
  "monetizacao": "Como o produto se monetiza?",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""

PROMPT_EVOLUTIONARY = """Você é um arquiteto de software que segue a Evolutionary Architecture de Neal Ford, Rebecca Parsons e Patrick Kua.

Princípios fundamentais:
- Guided, incremental change across multiple dimensions
- Fitness functions para avaliar características arquiteturais
- Decisões devem ser reversíveis quando possível
- Arquitetura que suporta mudança constante
- Last responsible moment para decisões irreversíveis

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Projete a arquitetura seguindo Evolutionary Architecture e responda em JSON:
{{
  "architecture_characteristics": ["Características arquiteturais prioritárias"],
  "fitness_functions": ["Fitness functions para validar as características"],
  "incremental_change": "Estratégia de mudança incremental",
  "reversibility": "Quais decisões são reversíveis?",
  "coupling": "Estratégia de acoplamento",
  "interfaces": ["Interfaces previstas"],
  "escalabilidade": "Como o sistema escala?",
  "custos": "Considerações de custo operacional",
  "monetizacao": "Como o produto se monetiza?",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""

PROMPT_ARCH_FLOW = """Você é um arquiteto de software que segue Architecture for Flow de Susanne Kaiser, combinando Domain-Driven Design, Wardley Mapping e Team Topologies.

Princípios fundamentais:
- Wardley Mapping para entender a cadeia de valor e evolução de componentes
- DDD para definir bounded contexts e linguagem ubíqua
- Team Topologies para organizar times ao redor do fluxo de valor
- Decisões baseadas na maturidade do componente (genesis → custom → product → commodity)

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Projete a arquitetura seguindo Architecture for Flow e responda em JSON:
{{
  "value_chain": "Cadeia de valor do produto",
  "bounded_contexts": ["Bounded contexts identificados"],
  "component_evolution": "Maturidade dos componentes (genesis/custom/product/commodity)",
  "team_topology": "Organização de times sugerida",
  "flow_optimization": "Como o fluxo de valor é otimizado?",
  "interfaces": ["Interfaces previstas"],
  "escalabilidade": "Como o sistema escala?",
  "custos": "Considerações de custo operacional",
  "monetizacao": "Como o produto se monetiza?",
  "stack_sugerida": "Pilha tecnológica sugerida"
}}

Responda APENAS o JSON, sem texto adicional."""

PROMPT_SEM_FRAMEWORK = """Você é um desenvolvedor que vai construir um produto de software. Você NÃO pode usar nenhum padrão ou framework de arquitetura de software. Não pode mencionar Clean Architecture, Hexagonal, MVC, microserviços, camadas, DDD, ou qualquer padrão conhecido. Pense apenas de forma intuitiva sobre como construir o produto.

Dada a seguinte ideia de produto SaaS:

"{ideia}"

Descreva como você construiria esse produto e responda em JSON:
{{
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

ABORDAGENS = {
    "aoen": PROMPT_AOEN,
    "clean_arch": PROMPT_CLEAN_ARCH,
    "hexagonal": PROMPT_HEXAGONAL,
    "12factor": PROMPT_12FACTOR,
    "evolutionary": PROMPT_EVOLUTIONARY,
    "arch_flow": PROMPT_ARCH_FLOW,
    "sem_framework": PROMPT_SEM_FRAMEWORK,
}

# =====================================================================
# CRITÉRIOS DE AVALIAÇÃO (aplicados por avaliador IA depois)
# =====================================================================

PROMPT_AVALIADOR = """Você é um avaliador neutro de arquiteturas de software. Analise a seguinte proposta arquitetural para o produto "{ideia}" e avalie cada critério com uma nota de 0 a 10.

Proposta (abordagem: {abordagem}):
{resposta}

Avalie com notas de 0 a 10 para cada critério:
{{
  "core_diferenciador": <0-10: Identificou um núcleo tecnológico diferenciador claro?>,
  "visao_mercado": <0-10: Considerou o mercado-alvo e proposta de valor?>,
  "multi_interface": <0-10: Previu múltiplas interfaces para diferentes contextos de uso?>,
  "configurabilidade": <0-10: Previu comportamento configurável por cliente sem código?>,
  "isolamento_processamento": <0-10: Isolou processamento pesado/caro do resto?>,
  "consideracao_custo": <0-10: Considerou custos operacionais e como controlá-los?>,
  "monetizacao": <0-10: Previu modelo de monetização viável?>,
  "evolucao": <0-10: A arquitetura permite evoluir sem reescrever?>,
  "coerencia": <0-10: As decisões se conectam e reforçam mutuamente?>
}}

Responda APENAS o JSON com as notas numéricas, sem texto adicional."""


def save_config():
    """Salva configuração do experimento."""
    config = {
        "total_ideias": len(IDEIAS),
        "abordagens": list(ABORDAGENS.keys()),
        "total_execucoes": len(IDEIAS) * len(ABORDAGENS),
        "criterios_avaliacao": [
            "core_diferenciador", "visao_mercado", "multi_interface",
            "configurabilidade", "isolamento_processamento",
            "consideracao_custo", "monetizacao", "evolucao", "coerencia"
        ]
    }
    os.makedirs("experimento", exist_ok=True)
    with open("experimento/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    with open("experimento/ideias.json", "w", encoding="utf-8") as f:
        json.dump(IDEIAS, f, ensure_ascii=False, indent=2)
    print(f"Configuração salva: {len(IDEIAS)} ideias x {len(ABORDAGENS)} abordagens = {len(IDEIAS) * len(ABORDAGENS)} execuções")


if __name__ == "__main__":
    save_config()
    print("\nPróximo passo: executar com 'python experimento_aoen.py run'")
    print("Ou prototipar com 'python experimento_aoen.py proto'")
