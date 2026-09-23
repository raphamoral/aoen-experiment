from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from shared.kernel.domain.base_entity import Entity


class TipoQuestao(str, Enum):
    MULTIPLA_ESCOLHA = "multipla_escolha"
    VERDADEIRO_FALSO = "verdadeiro_falso"


class StatusTentativa(str, Enum):
    EM_ANDAMENTO = "em_andamento"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"


@dataclass
class Alternativa(Entity):
    texto: str = ""
    correta: bool = False


@dataclass
class Questao(Entity):
    """
    Questão de avaliação com peso configurável.
    Linguagem ubíqua: 'Questão' — não 'Pergunta', 'Item' ou 'Question'.
    Wardley: Custom — lógica de pesos e correção é diferencial competitivo.
    """
    enunciado: str = ""
    tipo: TipoQuestao = TipoQuestao.MULTIPLA_ESCOLHA
    alternativas: List[Alternativa] = field(default_factory=list)
    peso: float = 1.0

    @property
    def alternativa_correta(self) -> Optional[Alternativa]:
        return next((a for a in self.alternativas if a.correta), None)


@dataclass
class Avaliacao(Entity):
    """
    Agregado raiz do contexto Avaliação.
    Avaliação final que habilita a emissão de certificado.
    """
    curso_id: str = ""
    titulo: str = ""
    nota_minima_aprovacao: float = 7.0
    tentativas_maximas: int = 3
    questoes: List[Questao] = field(default_factory=list)

    @property
    def total_pontos(self) -> float:
        return sum(q.peso for q in self.questoes)


@dataclass
class RespostaQuestao(Entity):
    questao_id: str = ""
    alternativa_id: str = ""


@dataclass
class Tentativa(Entity):
    """
    Registro de uma tentativa de avaliação por um estudante.
    Linguagem ubíqua: 'Tentativa' — cada submissão é uma nova tentativa.
    Invariante: nota calculada no momento da finalização; imutável depois.
    """
    avaliacao_id: str = ""
    estudante_id: str = ""
    status: StatusTentativa = StatusTentativa.EM_ANDAMENTO
    respostas: List[RespostaQuestao] = field(default_factory=list)
    nota: float = 0.0
    iniciada_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finalizada_em: Optional[datetime] = None

    def finalizar(self, avaliacao: Avaliacao) -> None:
        self.nota = self._calcular_nota(avaliacao)
        self.finalizada_em = datetime.now(timezone.utc)
        self.status = (
            StatusTentativa.APROVADO
            if self.nota >= avaliacao.nota_minima_aprovacao
            else StatusTentativa.REPROVADO
        )
        self.tocar()

    def _calcular_nota(self, avaliacao: Avaliacao) -> float:
        if not avaliacao.questoes or avaliacao.total_pontos == 0:
            return 0.0
        pontos = 0.0
        for questao in avaliacao.questoes:
            resposta = next((r for r in self.respostas if r.questao_id == questao.id), None)
            if resposta and questao.alternativa_correta:
                if resposta.alternativa_id == questao.alternativa_correta.id:
                    pontos += questao.peso
        return (pontos / avaliacao.total_pontos) * 10