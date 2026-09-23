from shared.kernel.domain.events import AvaliacaoAprovadaEvento
from shared.kernel.infrastructure.event_bus import BarramentoDeEventos
from .dto import CriarAvaliacaoRequest, SubmeterTentativaRequest, TentativaResponse
from ..domain.models import Alternativa, Avaliacao, Questao, RespostaQuestao, Tentativa, TipoQuestao
from ..domain.repositories import RepositorioDeAvaliacao, RepositorioDeTentativa


class CriarAvaliacao:
    def __init__(self, repo: RepositorioDeAvaliacao):
        self._repo = repo

    def executar(self, request: CriarAvaliacaoRequest) -> Avaliacao:
        questoes = [
            Questao(
                enunciado=q.enunciado,
                tipo=TipoQuestao(q.tipo),
                peso=q.peso,
                alternativas=[Alternativa(texto=a.texto, correta=a.correta) for a in q.alternativas],
            )
            for q in request.questoes
        ]
        avaliacao = Avaliacao(
            curso_id=request.curso_id,
            titulo=request.titulo,
            nota_minima_aprovacao=request.nota_minima_aprovacao,
            tentativas_maximas=request.tentativas_maximas,
            questoes=questoes,
        )
        return self._repo.salvar(avaliacao)


class SubmeterTentativa:
    def __init__(self, repo_avaliacao: RepositorioDeAvaliacao, repo_tentativa: RepositorioDeTentativa):
        self._repo_avaliacao = repo_avaliacao
        self._repo_tentativa = repo_tentativa

    async def executar(self, avaliacao_id: str, request: SubmeterTentativaRequest) -> TentativaResponse:
        avaliacao = self._repo_avaliacao.buscar_por_id(avaliacao_id)
        if not avaliacao:
            raise ValueError(f"Avaliação {avaliacao_id} não encontrada.")

        tentativas_feitas = self._repo_tentativa.contar_tentativas(request.estudante_id, avaliacao_id)
        if tentativas_feitas >= avaliacao.tentativas_maximas:
            raise ValueError("Número máximo de tentativas atingido.")

        tentativa = Tentativa(
            avaliacao_id=avaliacao_id,
            estudante_id=request.estudante_id,
            respostas=[
                RespostaQuestao(questao_id=r.questao_id, alternativa_id=r.alternativa_id)
                for r in request.respostas
            ],
        )
        tentativa.finalizar(avaliacao)
        salva = self._repo_tentativa.salvar(tentativa)

        if salva.status.value == "aprovado":
            await BarramentoDeEventos.publicar(
                AvaliacaoAprovadaEvento(
                    estudante_id=request.estudante_id,
                    curso_id=avaliacao.curso_id,
                    tentativa_id=salva.id,
                    nota=salva.nota,
                )
            )

        return TentativaResponse(
            id=salva.id,
            avaliacao_id=salva.avaliacao_id,
            estudante_id=salva.estudante_id,
            status=salva.status.value,
            nota=salva.nota,
        )