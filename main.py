Entry point — Professor Gemini

Orchestrates the full pipeline:
  Phase 0 → receive()       : parse input, build SessionContext
  Phase 1 → survey()        : segment, filter, diagnose
  Phase 2 → build_plan()    : order blocks, attach examples
  Phase 3 → teach()         : build teaching payloads

Modes:
  --interactive   : CLI session (default)
  --file PATH     : read material from file
  --dry-run       : run pipeline and print plan only, no teaching
  --block N       : teach only block N (useful for testing)
"""

import argparse
import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.phase0_reception  import receive, SessionGoal
from core.phase1_survey     import survey
from core.phase2_lesson_plan import build_plan
from core.phase3_teaching   import teach, render_payload


# ─────────────────────────────────────────────
#  INPUT HELPERS
# ─────────────────────────────────────────────

def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_stdin() -> str:
    print("\n Cole ou digite o material da aula. Quando terminar, pressione Enter duas")
    print(" vezes e depois Ctrl+D (Linux/Mac) ou Ctrl+Z + Enter (Windows).\n")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def _ask(prompt: str, default: str = "") -> str:
    val = input(prompt).strip()
    return val if val else default


# ─────────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────────

SEPARATOR = "═" * 62

def _banner():
    print(f"""
{SEPARATOR}
  PROFESSOR GEMINI — Pipeline de Aula
  Versão 1.0 | Aluno: Haecio Medeiros | 4º período
{SEPARATOR}
""")


def _confirm(prompt: str) -> bool:
    resp = input(f"{prompt} [s/n]: ").strip().lower()
    return resp in ("s", "sim", "y", "yes", "")


# ─────────────────────────────────────────────
#  GOAL SELECTOR
# ─────────────────────────────────────────────

_GOALS = {
    "1": SessionGoal.COMPREHENSIVE,
    "2": SessionGoal.EXAM_PREP,
    "3": SessionGoal.SEMINAR,
    "4": SessionGoal.QUICK_REVIEW,
}

def _select_goal() -> str:
    print("  Objetivo da sessão:")
    print("    1. Estudo completo (padrão)")
    print("    2. Preparação para prova")
    print("    3. Preparo de seminário")
    print("    4. Revisão rápida")
    choice = _ask("  Escolha [1-4, Enter = 1]: ", "1")
    return _GOALS.get(choice, SessionGoal.COMPREHENSIVE)


# ─────────────────────────────────────────────
#  PIPELINE RUNNER
# ─────────────────────────────────────────────

def run_pipeline(
    raw_material: str,
    discipline_hint: str = "",
    goal: str = SessionGoal.COMPREHENSIVE,
    constraints: str = "",
    dry_run: bool = False,
    only_block: int = None,
) -> None:
    """
    Run the full Phase 0→3 pipeline and print results.

    In dry_run mode: prints plan only.
    In normal mode: prints each teaching payload in order.
    """

    # ── Phase 0 ──────────────────────────────
    print("\n[Phase 0] Processando contexto da sessão...")
    ctx = receive(
        raw_material    = raw_material,
        discipline_hint = discipline_hint or None,
        goal            = goal,
        constraints     = constraints,
    )
    disc = ctx.matched_discipline
    if disc:
        print(f"  ✓ Disciplina identificada: {disc.name} [{disc.code}]")
    else:
        print("  ⚠ Disciplina não identificada automaticamente.")
        hint = _ask("  Digite o nome ou código da disciplina (opcional): ")
        if hint:
            ctx = receive(raw_material, discipline_hint=hint, goal=goal, constraints=constraints)

    # ── Phase 1 ──────────────────────────────
    print("\n[Phase 1] Mapeando e filtrando material...")
    survey_result = survey(ctx)
    core  = len(survey_result.core_sections)
    noise = len(survey_result.noise_sections)
    ahead = len(survey_result.ahead_sections)
    print(f"  ✓ {core} seções CORE | {noise} filtradas | {ahead} AHEAD")

    if core == 0:
        print("\n  ✗ Nenhuma seção CORE encontrada. Verifique o material e tente novamente.")
        sys.exit(1)

    # ── Phase 2 ──────────────────────────────
    print("\n[Phase 2] Construindo plano de aula...")
    plan = build_plan(survey_result)
    print(plan.display())

    if dry_run:
        print("  [dry-run] Pipeline encerrado antes do ensino.")
        return

    if not _confirm("\n  Confirma o plano acima e deseja iniciar a aula?"):
        print("  Sessão cancelada.")
        return

    # ── Phase 3 ──────────────────────────────
    print("\n[Phase 3] Gerando payloads de ensino...")
    payloads = teach(plan)

    if only_block is not None:
        idx = only_block - 1
        if 0 <= idx < len(payloads):
            payloads = [payloads[idx]]
            print(f"  [--block {only_block}] Ensinando apenas o bloco {only_block}.\n")
        else:
            print(f"  ✗ Bloco {only_block} não existe. Total de blocos: {len(payloads)}")
            sys.exit(1)

    for payload in payloads:
        print("\n" + render_payload(payload))

        if payload != payloads[-1]:
            if not _confirm("\n  Avançar para o próximo bloco?"):
                print("  Sessão pausada. Execute novamente para continuar.")
                break

    # ── Encerramento ─────────────────────────
    if survey_result.ahead_sections:
        print(f"\n{SEPARATOR}")
        print("  ⚠ CONTEÚDO REGISTRADO PARA O FUTURO:")
        for s in survey_result.ahead_sections:
            print(f"    · {s.title} → {s.ahead_discipline}")
        print(SEPARATOR)

    print("\n  Sessão encerrada. Bons estudos, Haécio.\n")


# ─────────────────────────────────────────────
#  CLI ENTRY POINT
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Professor Gemini — Pipeline de Aula"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Caminho para arquivo .txt com a transcrição da aula",
    )
    parser.add_argument(
        "--discipline", "-d",
        type=str,
        default="",
        help="Nome ou código da disciplina (opcional)",
    )
    parser.add_argument(
        "--goal", "-g",
        type=str,
        default=None,
        choices=["comprehensive", "exam", "seminar", "review"],
        help="Objetivo da sessão",
    )
    parser.add_argument(
        "--constraints", "-c",
        type=str,
        default="",
        help="Restrições da sessão (ex: 'apenas 30 minutos', 'pular procedimentos')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Exibe apenas o plano de aula, sem ensinar",
    )
    parser.add_argument(
        "--block", "-b",
        type=int,
        default=None,
        help="Ensinar apenas o bloco N",
    )

    args = parser.parse_args()

    _banner()

    # Read material
    if args.file:
        print(f"  Lendo material de: {args.file}")
        raw = _read_file(args.file)
    else:
        raw = _read_stdin()

    # Goal
    goal_map = {
        "comprehensive": SessionGoal.COMPREHENSIVE,
        "exam":          SessionGoal.EXAM_PREP,
        "seminar":       SessionGoal.SEMINAR,
        "review":        SessionGoal.QUICK_REVIEW,
        None:            None,
    }
    goal = goal_map.get(args.goal)
    if goal is None:
        goal = _select_goal()

    run_pipeline(
        raw_material    = raw,
        discipline_hint = args.discipline,
        goal            = goal,
        constraints     = args.constraints,
        dry_run         = args.dry_run,
        only_block      = args.block,
    )


if __name__ == "__main__":
    main()
