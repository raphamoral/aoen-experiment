from dataclasses import dataclass, field
from enum import Enum
from typing import List

from shared.kernel.domain.base_entity import Entity


class MaturidadeCurso(str, Enum):
    """
    Posição do curso na curva de evolução de Wardley.
    Orienta decisões de time e investimento: Genesis exige mais inovação;
    Commodity exige eficiência operacional.
    """
    GENESIS = "genesis"       # Conteúdo experimental, sem equivalente no mercado
    CUSTOM = "custom"         # Diferenciado, mas não padronizado
    PRODUTO = "produto"       # Bem definido, comparável a concorrentes
    COMMODITY = "commodity"   # Amplamente disponível (ex: Excel básico, Git intro)


class StatusCurso(str, Enum):
    RASCUNHO = "rascunho"
    PUBLICADO = "publicado"
    ARQUIVADO = "arquivado"


@dataclass
class Instrutor(Entity):
    """Instrutor responsável pela autoria e qualidade do curso."""
    nome: str = ""
    email: str = ""
    especialidade: str = ""


@dataclass
class Aula(Entity):
    """
    Unidade atômica de aprendizado.
    Linguagem ubíqua: 'Aula' — não 'Lesson', 'Lecture' ou 'Video'.
    """
    titulo: str = ""
    descricao: str = ""
    duracao_minutos: int = 0
    ordem: int = 0


@dataclass
class Modulo(Entity):
    """Agrupamento temático de aulas dentro de um curso."""
    titulo: str = ""
    descricao: str = ""
    ordem: int = 0
    aulas: List[Aula] = field(default_factory=list)

    @property
    def duracao_total_minutos(self) -> int:
        return sum(a.duracao_minutos for a in self.aulas)


@dataclass
class Curso(Entity):
    """
    Agregado raiz do contexto Catálogo de Cursos.
    Um curso livre completo com carga horária certificável.
    Invariante: não pode ser publicado sem módulos.
    """
    titulo: str = ""
    descricao: str = ""
    carga_horaria: int = 0
    maturidade: MaturidadeCurso = MaturidadeCurso.CUSTOM
    status: StatusCurso = StatusCurso.RASCUNHO
    instrutor_id: str = ""
    modulos: List[Modulo] = field(default_factory=list)
    nota_minima_aprovacao: float = 7.0

    def publicar(self) -> None:
        if not self.modulos:
            raise ValueError("Curso não pode ser publicado sem módulos.")
        self.status = StatusCurso.PUBLICADO
        self.tocar()

    def arquivar(self) -> None:
        self.status = StatusCurso.ARQUIVADO
        self.tocar()

    @property
    def total_aulas(self) -> int:
        return sum(len(m.aulas) for m in self.modulos)

    @property
    def esta_disponivel(self) -> bool:
        return self.status == StatusCurso.PUBLICADO