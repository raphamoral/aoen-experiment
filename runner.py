# -*- coding: utf-8 -*-
"""
Runner retomável do experimento AOEN.

Diferenças em relação ao run_experiment.py original:
  * Nunca grava artefato inválido. `ERROR:` ou JSON malformado não viram arquivo,
    então retomar de verdade retoma (o script antigo gravava o erro e pulava
    pra sempre, que foi o que truncou a rodada em 21 ideias).
  * Retenta com backoff e distingue falha de cota de falha de conteúdo.
  * Para limpo por Ctrl+C, por arquivo-sentinela STOP ou por cota esgotada,
    sempre com checkpoint gravado.
  * Trilha de auditoria em JSONL: uma linha por tentativa.
  * Consolidação se recusa a agregar dataset incompleto.

Uso:
    python runner.py --status
    python runner.py --dry-run
    python runner.py --ideias 0-1                # smoke test
    python runner.py                             # roda tudo (100 x 7)
    python runner.py --retry-failed              # só o que ficou pendente
    python runner.py --consolidate
"""
import argparse
import json
import os
import random
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = Path(__file__).resolve().parent
EXPERIMENT_DIR = BASE / "experimento"
sys.path.insert(0, str(BASE))
from experimento_aoen import ABORDAGENS, PROMPT_AVALIADOR  # noqa: E402

CRITERIOS = [
    "core_diferenciador", "visao_mercado", "multi_interface",
    "configurabilidade", "isolamento_processamento",
    "consideracao_custo", "monetizacao", "evolucao", "coerencia",
]

# returncode != 0 com stderr vazio foi a assinatura exata da queda de abril.
PADRAO_COTA = re.compile(
    r"rate.?limit|quota|usage limit|credit|overloaded|429|too many requests|"
    r"insufficient|billing|upgrade your plan",
    re.I,
)

_parar = threading.Event()
_lock = threading.Lock()


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(texto):
    import hashlib
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- infraestrutura

class Log:
    """Trilha de auditoria: uma linha JSON por tentativa, append-only."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

    def registrar(self, **campos):
        campos["ts"] = agora()
        linha = json.dumps(campos, ensure_ascii=False)
        with _lock:
            with open(self.caminho, "a", encoding="utf-8") as f:
                f.write(linha + "\n")


class Estado:
    """Checkpoint legível: onde parou e por quê."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.dados = {}
        if caminho.exists():
            try:
                self.dados = json.loads(caminho.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.dados = {}

    def gravar(self, **campos):
        with _lock:
            self.dados.update(campos)
            self.dados["atualizado_em"] = agora()
            tmp = self.caminho.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(self.dados, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            tmp.replace(self.caminho)


# ---------------------------------------------------------------- chamada ao CLI

class CotaEsgotada(Exception):
    pass


def _matar_grupo(proc):
    """Mata o processo E os netos. Sem isso, um neto segurando o pipe deixa
    o communicate() preso pra sempre mesmo depois do filho morrer."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.kill()
        except Exception:
            pass


def chamar_claude(prompt, modelo, timeout):
    """Uma invocação. Devolve (ok, texto, meta)."""
    t0 = time.time()
    try:
        proc = subprocess.Popen(
            ["claude", "-p", "--model", modelo],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            start_new_session=True,   # grupo próprio, pra poder matar a árvore toda
        )
    except Exception as e:
        return False, "", {"erro": f"spawn: {e}", "cota": False, "dur": time.time() - t0}

    class _R:
        pass
    r = _R()
    try:
        r.stdout, r.stderr = proc.communicate(prompt, timeout=timeout)
        r.returncode = proc.returncode
    except subprocess.TimeoutExpired:
        _matar_grupo(proc)
        try:
            proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            pass
        return False, "", {"erro": "timeout", "cota": False, "dur": time.time() - t0}
    except Exception as e:
        _matar_grupo(proc)
        return False, "", {"erro": str(e), "cota": False, "dur": time.time() - t0}

    dur = time.time() - t0
    err = (r.stderr or "").strip()
    if r.returncode != 0:
        # stderr vazio + returncode != 0 = assinatura de cota/limite no claude CLI
        cota = bool(PADRAO_COTA.search(err)) or err == ""
        return False, "", {"erro": err or f"returncode={r.returncode}",
                           "cota": cota, "rc": r.returncode, "dur": dur}
    saida = (r.stdout or "").strip()
    if not saida:
        return False, "", {"erro": "stdout vazio", "cota": True, "dur": dur}
    return True, saida, {"dur": dur, "cota": False}


def extrair_json(texto):
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass
    i, j = texto.find("{"), texto.rfind("}") + 1
    if i >= 0 and j > i:
        try:
            return json.loads(texto[i:j])
        except json.JSONDecodeError:
            pass
    return None


# ---------------------------------------------------------------- validação

def gen_valida(obj):
    """Geração válida: dict com conteúdo, sem marca de erro."""
    if not isinstance(obj, dict) or not obj:
        return False, "resposta não é objeto JSON"
    if "raw_response" in obj or "error" in obj:
        return False, "resposta sem JSON extraível"
    if len(json.dumps(obj, ensure_ascii=False)) < 200:
        return False, "resposta curta demais"
    return True, ""


def eval_valida(obj):
    """Avaliação válida: os 9 critérios, todos numéricos entre 0 e 10."""
    if not isinstance(obj, dict):
        return False, "scores não é objeto"
    faltando = [c for c in CRITERIOS if c not in obj]
    if faltando:
        return False, f"critérios ausentes: {','.join(faltando)}"
    for c in CRITERIOS:
        v = obj[c]
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            return False, f"{c} não é numérico ({v!r})"
        if not 0 <= v <= 10:
            return False, f"{c} fora da escala ({v})"
    return True, ""


def artefato_ok(caminho, tipo):
    """Um artefato só conta como pronto se existir E for válido."""
    if not caminho.exists():
        return False
    try:
        d = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if tipo == "gen":
        return gen_valida(d.get("response"))[0]
    return eval_valida(d.get("scores"))[0]


# ---------------------------------------------------------------- tarefas

class Executor:
    def __init__(self, cfg, log, estado):
        self.cfg = cfg
        self.log = log
        self.estado = estado
        self.contagem = {"ok": 0, "retry": 0, "falha": 0, "pulado": 0}
        self.chars = {"in": 0, "out": 0}

    def _tentar(self, tarefa, prompt, validador, modelo):
        """Executa com retry. Devolve (obj, motivo_falha)."""
        tipo, idx, abordagem = tarefa
        ultimo = "não executado"
        for tentativa in range(1, self.cfg.max_attempts + 1):
            if _parar.is_set():
                return None, "interrompido"

            ok, texto, meta = chamar_claude(prompt, modelo, self.cfg.timeout)
            registro = {
                "tipo": tipo, "ideia": idx, "abordagem": abordagem,
                "modelo": modelo,
                "tentativa": tentativa, "dur_s": round(meta.get("dur", 0), 1),
                "chars_in": len(prompt),
            }

            if ok:
                obj = extrair_json(texto)
                valido, motivo = validador(obj) if obj is not None else (False, "sem JSON")
                registro.update(status="ok" if valido else "invalido",
                                chars_out=len(texto), motivo=motivo or None)
                self.log.registrar(**registro)
                with _lock:
                    self.chars["in"] += len(prompt)
                    self.chars["out"] += len(texto)
                if valido:
                    return obj, ""
                ultimo = motivo
            else:
                registro.update(status="erro", erro=meta.get("erro"),
                                cota=meta.get("cota", False))
                self.log.registrar(**registro)
                ultimo = meta.get("erro", "erro")
                if meta.get("cota"):
                    # Cota/limite: não adianta insistir no mesmo segundo.
                    if tentativa >= self.cfg.quota_attempts:
                        raise CotaEsgotada(ultimo)
                    espera = self.cfg.backoff * (3 ** tentativa)
                    espera += random.uniform(0, espera * 0.2)
                    print(f"    cota/limite — aguardando {espera:.0f}s "
                          f"(tentativa {tentativa}/{self.cfg.quota_attempts})")
                    if _parar.wait(espera):
                        return None, "interrompido"
                    continue

            if tentativa < self.cfg.max_attempts:
                espera = self.cfg.backoff * (2 ** (tentativa - 1))
                espera += random.uniform(0, espera * 0.3)
                if _parar.wait(espera):
                    return None, "interrompido"
        return None, ultimo

    def gerar(self, idx, ideia, abordagem):
        arq = self.cfg.results / f"idea_{idx:03d}_{abordagem}.json"
        if artefato_ok(arq, "gen"):
            self.contagem["pulado"] += 1
            return "pulado"

        template = ABORDAGENS[abordagem]
        prompt = template.format(ideia=ideia)
        obj, motivo = self._tentar(("gen", idx, abordagem), prompt, gen_valida,
                                   self.cfg.model)
        if obj is None:
            self.contagem["falha"] += 1
            return motivo

        arq.write_text(json.dumps({
            "ideia_idx": idx, "ideia": ideia, "abordagem": abordagem,
            "response": obj,
            "_meta": {"modelo": self.cfg.model, "prompt_sha": sha(template),
                      "gerado_em": agora(), "runner": "runner.py"},
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        self.contagem["ok"] += 1
        return "ok"

    def avaliar(self, idx, ideia, abordagem):
        arq = self.cfg.results / f"eval_{idx:03d}_{abordagem}.json"
        if artefato_ok(arq, "eval"):
            self.contagem["pulado"] += 1
            return "pulado"

        fonte = self.cfg.results / f"idea_{idx:03d}_{abordagem}.json"
        if not artefato_ok(fonte, "gen"):
            self.contagem["falha"] += 1
            return "geração ausente"

        resposta = json.loads(fonte.read_text(encoding="utf-8"))["response"]
        texto = json.dumps(resposta, ensure_ascii=False, indent=2)
        if self.cfg.eval_truncate:
            texto = texto[: self.cfg.eval_truncate]
        prompt = PROMPT_AVALIADOR.format(ideia=ideia, abordagem=abordagem, resposta=texto)

        obj, motivo = self._tentar(("eval", idx, abordagem), prompt, eval_valida,
                                   self.cfg.eval_model)
        if obj is None:
            self.contagem["falha"] += 1
            return motivo

        arq.write_text(json.dumps({
            "ideia_idx": idx, "abordagem": abordagem, "scores": obj,
            "_meta": {"modelo_avaliador": self.cfg.eval_model,
                      "modelo_gerador": self.cfg.model,
                      "prompt_sha": sha(PROMPT_AVALIADOR),
                      "truncagem": self.cfg.eval_truncate, "avaliado_em": agora()},
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        self.contagem["ok"] += 1
        return "ok"


# ---------------------------------------------------------------- orquestração

def parar_solicitado(cfg):
    return _parar.is_set() or (cfg.results / "STOP").exists() or (BASE / "STOP").exists()


def rodar_fase(cfg, ex, fase, ideias, idxs):
    tarefas = [(i, ab) for i in idxs for ab in ABORDAGENS]
    pendentes = [
        (i, ab) for i, ab in tarefas
        if not artefato_ok(
            cfg.results / f"{'idea' if fase == 'gen' else 'eval'}_{i:03d}_{ab}.json", fase
        )
    ]
    print(f"\n=== fase {fase}: {len(pendentes)} pendentes de {len(tarefas)} ===")
    if not pendentes:
        return True

    feitos = 0
    cota = False
    fn = ex.gerar if fase == "gen" else ex.avaliar
    with ThreadPoolExecutor(max_workers=cfg.workers) as pool:
        futuros = {}
        for i, ab in pendentes:
            if parar_solicitado(cfg):
                break
            futuros[pool.submit(fn, i, ideias[i], ab)] = (i, ab)

        for fut in as_completed(futuros):
            i, ab = futuros[fut]
            feitos += 1
            try:
                r = fut.result()
            except CotaEsgotada as e:
                cota = True
                _parar.set()
                r = f"COTA: {e}"
            except Exception as e:
                r = f"exceção: {e}"
            marca = "ok" if r in ("ok", "pulado") else "FALHA"
            print(f"  [{feitos}/{len(futuros)}] ideia {i:03d} {ab:14s} {marca}"
                  + ("" if marca == "ok" else f" — {r}"))
            if feitos % 10 == 0 or cota:
                ex.estado.gravar(fase=fase, ultima_ideia=i, contagem=ex.contagem,
                                 chars=ex.chars)

    ex.estado.gravar(fase=fase, contagem=ex.contagem, chars=ex.chars,
                     interrompido_por_cota=cota)
    if cota:
        print("\n!! Cota/limite esgotado. Estado gravado — retome com o mesmo comando.")
        return False
    return not parar_solicitado(cfg)


def cmd_status(cfg):
    ideias = json.loads((EXPERIMENT_DIR / "ideias.json").read_text(encoding="utf-8"))
    total = len(ideias) * len(ABORDAGENS)
    linhas = []
    for fase, pref in (("gen", "idea"), ("eval", "eval")):
        ok = sum(
            artefato_ok(cfg.results / f"{pref}_{i:03d}_{ab}.json", fase)
            for i in range(len(ideias)) for ab in ABORDAGENS
        )
        linhas.append((fase, ok, total))
    print(f"\nresultados em: {cfg.results}")
    for fase, ok, tot in linhas:
        pct = 100 * ok / tot if tot else 0
        print(f"  {fase:5s} {ok:4d}/{tot} ({pct:5.1f}%)  faltam {tot - ok}")
    por_ab = {}
    for ab in ABORDAGENS:
        g = sum(artefato_ok(cfg.results / f"idea_{i:03d}_{ab}.json", "gen")
                for i in range(len(ideias)))
        e = sum(artefato_ok(cfg.results / f"eval_{i:03d}_{ab}.json", "eval")
                for i in range(len(ideias)))
        por_ab[ab] = (g, e)
    print("\n  por abordagem (gen/eval):")
    for ab, (g, e) in por_ab.items():
        print(f"    {ab:15s} {g:3d} / {e:3d}")
    est = cfg.results / "_state.json"
    if est.exists():
        d = json.loads(est.read_text(encoding="utf-8"))
        print(f"\n  último checkpoint: {d.get('atualizado_em')}")
        print(f"  contagem: {d.get('contagem')}")
        c = d.get("chars") or {}
        if c:
            tk = (c.get("in", 0) + c.get("out", 0)) / 3.3
            print(f"  tokens de conteúdo consumidos (estimado): {tk/1e6:.2f} M")
        if d.get("interrompido_por_cota"):
            print("  >> última parada foi por cota. Basta rodar de novo.")
    log = cfg.results / "_attempts.jsonl"
    if log.exists():
        linhas = log.read_text(encoding="utf-8").strip().splitlines()
        erros = [json.loads(l) for l in linhas if '"status": "erro"' in l]
        print(f"\n  tentativas registradas: {len(linhas)} | com erro: {len(erros)}")


def cmd_dry_run(cfg, idxs):
    ideias = json.loads((EXPERIMENT_DIR / "ideias.json").read_text(encoding="utf-8"))
    tin = tout = 0
    n_gen = n_eval = 0
    for i in idxs:
        for ab, tmpl in ABORDAGENS.items():
            if not artefato_ok(cfg.results / f"idea_{i:03d}_{ab}.json", "gen"):
                n_gen += 1
                tin += len(tmpl.format(ideia=ideias[i]))
                tout += 8400
            if not artefato_ok(cfg.results / f"eval_{i:03d}_{ab}.json", "eval"):
                n_eval += 1
                corpo = cfg.eval_truncate or 8400
                tin += len(PROMPT_AVALIADOR) + len(ideias[i]) + corpo
                tout += 200
    print(f"\nplano: {n_gen} gerações + {n_eval} avaliações = {n_gen + n_eval} chamadas")
    print(f"  entrada ~{tin/3.3/1e6:.2f} M tokens | saída ~{tout/3.3/1e6:.2f} M tokens")
    print(f"  conteúdo total ~{(tin+tout)/3.3/1e6:.2f} M tokens (fora overhead do CLI)")
    print(f"  gerador: {cfg.model} | avaliador: {cfg.eval_model} | "
          f"workers: {cfg.workers} | "
          f"truncagem da avaliação: {cfg.eval_truncate or 'nenhuma'}")


def cmd_consolidate(cfg):
    ideias = json.loads((EXPERIMENT_DIR / "ideias.json").read_text(encoding="utf-8"))
    registros, buracos = [], []
    for i in range(len(ideias)):
        for ab in ABORDAGENS:
            arq = cfg.results / f"eval_{i:03d}_{ab}.json"
            if artefato_ok(arq, "eval"):
                registros.append(json.loads(arq.read_text(encoding="utf-8")))
            else:
                buracos.append(f"{i:03d}/{ab}")
    if buracos and not cfg.force:
        print(f"\nRECUSADO: {len(buracos)} avaliações ausentes ou inválidas.")
        print("  primeiras:", ", ".join(buracos[:10]))
        print("  rode o runner até o fim, ou use --force para consolidar parcial")
        print("  (com --force o arquivo registra a cobertura real).")
        return 1
    destino = EXPERIMENT_DIR / cfg.out
    destino.write_text(json.dumps({
        "_meta": {
            "modelo_gerador": cfg.model, "modelo_avaliador": cfg.eval_model,
            "gerado_em": agora(),
            "ideias_no_conjunto": len(ideias), "abordagens": list(ABORDAGENS),
            "avaliacoes": len(registros),
            "esperadas": len(ideias) * len(ABORDAGENS),
            "cobertura_pct": round(100 * len(registros) /
                                   (len(ideias) * len(ABORDAGENS)), 1),
            "buracos": buracos,
            "pontos_de_dados": len(registros) * len(CRITERIOS),
        },
        "avaliacoes": registros,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nconsolidado: {len(registros)} avaliações "
          f"({len(registros)*len(CRITERIOS)} pontos de dados) -> {destino}")
    if buracos:
        print(f"  ATENÇÃO: cobertura parcial, {len(buracos)} buracos registrados no _meta")
    return 0


def parse_ideias(spec, total):
    if not spec:
        return list(range(total))
    out = []
    for parte in spec.split(","):
        if "-" in parte:
            a, b = parte.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(parte))
    return [i for i in out if 0 <= i < total]


def main():
    p = argparse.ArgumentParser(description="Runner retomável do experimento AOEN")
    p.add_argument("--model", default="claude-sonnet-5",
                   help="id do modelo gerador (fixo, não usar alias)")
    p.add_argument("--eval-model", default=None,
                   help="id do modelo avaliador; se omitido, usa --model")
    p.add_argument("--results", default="experimento/results_v4")
    p.add_argument("--ideias", default=None, help="ex: 0-99 ou 0,5,7")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--timeout", type=int, default=240)
    p.add_argument("--max-attempts", type=int, default=4)
    p.add_argument("--quota-attempts", type=int, default=3,
                   help="tentativas em caso de cota antes de parar tudo")
    p.add_argument("--backoff", type=float, default=20.0)
    p.add_argument("--eval-truncate", type=int, default=0,
                   help="0 = manda a resposta inteira ao avaliador")
    p.add_argument("--only", choices=["gen", "eval", "both"], default="both")
    p.add_argument("--status", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--consolidate", action="store_true")
    p.add_argument("--out", default="consolidated_v4.json")
    p.add_argument("--force", action="store_true")
    cfg = p.parse_args()
    cfg.eval_model = cfg.eval_model or cfg.model
    cfg.results = (BASE / cfg.results) if not Path(cfg.results).is_absolute() else Path(cfg.results)
    cfg.results.mkdir(parents=True, exist_ok=True)

    ideias = json.loads((EXPERIMENT_DIR / "ideias.json").read_text(encoding="utf-8"))
    idxs = parse_ideias(cfg.ideias, len(ideias))

    if cfg.status:
        return cmd_status(cfg) or 0
    if cfg.dry_run:
        return cmd_dry_run(cfg, idxs) or 0
    if cfg.consolidate:
        return cmd_consolidate(cfg)

    def ao_sinal(signum, frame):
        if _parar.is_set():
            print("\n(segundo sinal — saindo já)")
            os._exit(130)
        print("\n>> parada solicitada: terminando as chamadas em voo e gravando estado...")
        _parar.set()

    signal.signal(signal.SIGINT, ao_sinal)
    try:
        signal.signal(signal.SIGTERM, ao_sinal)
    except (AttributeError, ValueError):
        pass

    log = Log(cfg.results / "_attempts.jsonl")
    estado = Estado(cfg.results / "_state.json")
    try:
        versao = subprocess.run(["claude", "--version"], capture_output=True,
                                text=True, timeout=30).stdout.strip()
    except Exception:
        versao = "desconhecida"

    estado.gravar(iniciado_em=agora(), modelo=cfg.model,
                  modelo_avaliador=cfg.eval_model, cli=versao,
                  workers=cfg.workers, eval_truncate=cfg.eval_truncate,
                  ideias=f"{min(idxs)}-{max(idxs)}" if idxs else "-",
                  interrompido_por_cota=False)

    print(f"runner AOEN | gerador={cfg.model} | avaliador={cfg.eval_model} "
          f"| cli={versao}")
    print(f"resultados: {cfg.results}")
    print(f"ideias: {len(idxs)} x {len(ABORDAGENS)} abordagens")
    print("pare com Ctrl+C ou criando o arquivo STOP nesta pasta.")

    ex = Executor(cfg, log, estado)
    t0 = time.time()
    completo = True
    if cfg.only in ("gen", "both"):
        completo = rodar_fase(cfg, ex, "gen", ideias, idxs)
    if completo and cfg.only in ("eval", "both"):
        completo = rodar_fase(cfg, ex, "eval", ideias, idxs)

    estado.gravar(contagem=ex.contagem, chars=ex.chars, concluido=completo,
                  duracao_s=round(time.time() - t0))
    tk = (ex.chars["in"] + ex.chars["out"]) / 3.3
    print(f"\n{'='*60}")
    print(f"{'CONCLUÍDO' if completo else 'PARADO (retomável)'} em "
          f"{(time.time()-t0)/60:.1f} min")
    print(f"  ok={ex.contagem['ok']} pulado={ex.contagem['pulado']} "
          f"falha={ex.contagem['falha']}")
    print(f"  tokens de conteúdo nesta sessão: ~{tk/1e6:.3f} M")
    print(f"  estado: {cfg.results / '_state.json'}")
    print(f"  log:    {cfg.results / '_attempts.jsonl'}")
    if not completo:
        print("\n  para continuar: rode exatamente o mesmo comando.")
    return 0 if completo else 2


if __name__ == "__main__":
    sys.exit(main())
