"""
core/phase3_teaching.py
-----------------------
Phase 3 — Block Teaching

Receives a LessonBlock from phase2_lesson_plan and produces a TeachingSession:
  - Applies the correct module chain based on the block's lenses
  - Runs Módulo 0 (Hook de Ancoragem) silently in background
  - Flags professor examples with explicit attribution
  - Pauses after each block and waits for student confirmation
  - Handles student questions before advancing

The actual natural-language output is produced by the LLM (Gemini).
This module generates the INSTRUCTION PAYLOAD that tells Gemini exactly
what to do, in what order, with what constraints, for each block.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.phase2_lesson_plan import LessonBlock, LessonPlan
from core.phase1_survey import SectionType
from student_profile.profile import STUDENT
from student_profile.curriculum.grade_curricular import get_completed, get_current


# ─────────────────────────────────────────────
#  MODULE REGISTRY
#  Maps each lens to the module instruction it triggers.
#  Based on lens_map.md + the original modulo*.py files.
# ─────────────────────────────────────────────

from modules.modulo0_hook     import MODIFICADOR_PASSIVO
from modules.modulo1_context  import MODULO_1
from modules.modulo2_causal   import MODULO_2
from modules.modulo3_analogy  import MODULO_3
from modules.modulo4_failure  import MODULO_4
from modules.modulo5_test     import MODULO_5
from modules.modulo6_transfer import MODULO_6

MODULE_INSTRUCTIONS = {
    # Lens → authoritative instruction from its module
    "boundary":                MODULO_1["instrucao_central"],
    "mechanism":               MODULO_2["instrucao_central"],
    "anchoring":               MODIFICADOR_PASSIVO["instrucao_central"],
    "failure_mode":            MODULO_4["instrucao_central"],
    "discrimination":          MODULO_5["instrucao_central"],   # test drives discrimination
    "taxonomy_contrast":       MODULO_3["instrucao_central"],   # analogy drives contrast
    "quant_representation":    MODULO_3["instrucao_central"],
    "constraints":             MODULO_4["instrucao_central"],
    "exceptions":              MODULO_4["instrucao_central"],
    "clinical_trigger":        MODULO_6["instrucao_central"],   # transfer drives clinical logic
    "procedure_rationale":     MODULO_2["instrucao_central"],   # causal chain for procedures
    "examples_counterexamples":MODULO_1["instrucao_central"],
}

# Module 1 and Module 5 instructions (always run, not lens-driven)
MODULE_1_INSTRUCTION = MODULO_1["instrucao_central"]
MODULE_5_INSTRUCTION = MODULO_5["instrucao_central"]

# Competency targets per section type (backward design)
COMPETENCY_TARGETS = {
    "definition": MODULO_5["sinal_que_funcionou"],
    "mechanism":  MODULO_2["sinal_que_funcionou"],
    "taxonomy":   MODULO_3["sinal_que_funcionou"],
    "quant_process":      MODULO_2["sinal_que_funcionou"],
    "clinical_decision":  MODULO_6["sinal_que_funcionou"],
    "procedure":          MODULO_4["sinal_que_funcionou"],
    "mixed":              MODULO_5["sinal_que_funcionou"],
}


# ─────────────────────────────────────────────
#  PROFESSOR EXAMPLE WRAPPER
# ─────────────────────────────────────────────

PROFESSOR_EXAMPLE_HEADER = (
    "
💬 *Este exemplo foi dado pelo professor em aula.*
"
)


def _wrap_professor_examples(examples: List[str]) -> str:
    if not examples:
        return ""
    parts = [PROFESSOR_EXAMPLE_HEADER]
    for ex in examples:
        parts.append(ex.strip())
    return "

".join(parts)


# ─────────────────────────────────────────────
#  MODULE 1 — CONTEXT BEFORE CONTENT
#  Always runs first, regardless of section type.
# ─────────────────────────────────────────────

MODULE_1_INSTRUCTION = (
    "ANTES de qualquer definição, mecanismo ou terminologia técnica: "
    "apresente uma situação narrativa com personagem, verbos e sequência temporal. "
    "Inclua DESFECHO INESPERADO — uma consequência real e concreta, não um cenário vago. "
    "Termine com UMA pergunta genuína que o aluno não consegue responder ainda. "
    "Frase de transição: 'É exatamente isso que [conceito X] responde. "
    "Vamos construir o mecanismo do zero.' "
    "NÃO resolva a pergunta ainda. NÃO use jargão técnico na situação."
)


# ─────────────────────────────────────────────
#  MODULE 5 — COMPREHENSION TEST
#  Always runs after the main content.
# ─────────────────────────────────────────────

MODULE_5_INSTRUCTION = (
    "Formule 1 pergunta de teste que: "
    "(a) use linguagem DIFERENTE da usada na explicação, "
    "(b) exija reconstrução do mecanismo, não repetição, "
    "(c) seja respondível apenas com o que foi ensinado neste bloco. "
    "Após a resposta do aluno: identifique o elo causal faltante, "
    "não apenas diga certo/errado. "
    "NÃO avance para o próximo bloco antes de receber e processar a resposta."
)


# ─────────────────────────────────────────────
#  TEACHING PAYLOAD
# ─────────────────────────────────────────────

@dataclass
class TeachingPayload:
    """
    Complete instruction set for Gemini to teach one block.
    This is what gets injected into the LLM prompt for each block.
    """
    block: LessonBlock
    step_instructions: List[str]          # ordered list of what to do
    professor_example_text: str           # pre-formatted example with header
    anchoring_context: str                # completed disciplines for Módulo 0
    student_profile_summary: str          # key profile facts
    block_intro: str                      # brief framing shown before teaching
    mandatory_pause: str                  # text shown after block ends


def _build_step_instructions(block: LessonBlock) -> List[str]:
    steps = []

    # Step 0: always open with Módulo 1 (context before content)
    steps.append(f"ETAPA 1 — SITUAÇÃO CONCRETA (Módulo 1)
{MODULE_1_INSTRUCTION}")

    # Steps 1-N: apply lenses in order
    step_num = 2
    for lens in block.lenses:
        instr = MODULE_INSTRUCTIONS.get(lens)
        if not instr:
            continue
        # anchoring is silent — mark it differently
        if lens == "anchoring":
            steps.append(
                f"ETAPA {step_num} — ANCORAGEM SILENCIOSA (Módulo 0, background)
{instr}"
            )
        else:
            steps.append(f"ETAPA {step_num} — {lens.upper()}
{instr}")
        step_num += 1

    # Professor example step (if present)
    if block.professor_examples:
        steps.append(
            f"ETAPA {step_num} — EXEMPLO DO PROFESSOR
"
            "Reuse o exemplo abaixo exatamente como dado em aula. "
            "Sinalize explicitamente com '💬 Este exemplo foi dado pelo professor em aula.' "
            "Conecte o exemplo ao mecanismo explicado antes dele."
        )
        step_num += 1

    # Always close with Módulo 5
    steps.append(f"ETAPA {step_num} — TESTE DE COMPREENSÃO (Módulo 5)
{MODULE_5_INSTRUCTION}")

    return steps


def _build_anchoring_context() -> str:
    completed = get_completed()
    lines = ["Disciplinas concluídas pelo aluno (use para ancoragem — Módulo 0):"]
    for d in completed:
        entry = f"  · {d.name}"
        if d.notes:
            entry += f": {d.notes}"
        lines.append(entry)
    return "
".join(lines)


def _build_student_summary() -> str:
    s = STUDENT
    return (
        f"Aluno: {s.name} | {s.current_period}º período | {s.institution}
"
        f"Aprende melhor com: {'; '.join(s.learns_best_with)}
"
        f"Background prévio: {'; '.join(s.prior_background)}
"
        f"Intuição clínica: {'sim' if s.has_clinical_intuition else 'não — ancoragem concreta obrigatória'}
"
        f"Regra: concreto antes do abstrato. Nunca abrir com definição formal."
    )


# ─────────────────────────────────────────────
#  MAIN FUNCTION
# ─────────────────────────────────────────────

def build_payload(block: LessonBlock) -> TeachingPayload:
    """
    Build the complete instruction payload for a single block.

    Parameters
    ----------
    block : LessonBlock from phase2_lesson_plan.build_plan()

    Returns
    -------
    TeachingPayload — inject into Gemini system prompt + user turn
    """
    return TeachingPayload(
        block                  = block,
        step_instructions      = _build_step_instructions(block),
        professor_example_text = _wrap_professor_examples(block.professor_examples),
        anchoring_context      = _build_anchoring_context(),
        student_profile_summary= _build_student_summary(),
        block_intro            = (
            f"Bloco {block.block_number} de {block.block_number} iniciado: "
            f"**{block.title}** [{block.depth}]"
        ),
        mandatory_pause        = (
            "---
"
            "Bloco concluído. Responda à pergunta de teste acima antes de continuarmos.
"
            "Quando estiver pronto, diga **'próximo'** para o Bloco seguinte."
        ),
    )


def render_payload(payload: TeachingPayload) -> str:
    """
    Render the TeachingPayload as a formatted prompt string
    ready to be injected into the Gemini session.
    """
    lines = [
        "═" * 62,
        f"BLOCO {payload.block.block_number} — {payload.block.title.upper()}",
        f"Tipo: {payload.block.section_type} | Profundidade: {payload.block.depth}",
        "═" * 62,
        "",
        "### PERFIL DO ALUNO",
        payload.student_profile_summary,
        "",
        "### CONTEXTO DE ANCORAGEM (Módulo 0)",
        payload.anchoring_context,
        "",
        "### CONTEÚDO BRUTO DO BLOCO",
        payload.block.raw_text,
        "",
    ]

    if payload.professor_example_text:
        lines += [
            "### EXEMPLO DO PROFESSOR (preservar integralmente)",
            payload.professor_example_text,
            "",
        ]

    lines += [
        "### INSTRUÇÕES DE ENSINO (executar em ordem)",
        "─" * 40,
    ]
    for i, step in enumerate(payload.step_instructions):
        lines.append(f"
{step}")

    lines += [
        "",
        "─" * 40,
        "### ENCERRAMENTO DO BLOCO",
        payload.mandatory_pause,
        "═" * 62,
    ]

    return "
".join(lines)


# ─────────────────────────────────────────────
#  LESSON ORCHESTRATOR
#  Iterates over all blocks in the plan.
# ─────────────────────────────────────────────

def teach(plan: LessonPlan) -> List[TeachingPayload]:
    """
    Build all TeachingPayloads for a complete lesson plan.
    Returns list in teaching order — one payload per block.
    Each payload is independent and self-contained for injection into Gemini.
    """
    return [build_payload(block) for block in plan.blocks]


# ─────────────────────────────────────────────
#  QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from core.phase0_reception import receive
    from core.phase1_survey import survey
    from core.phase2_lesson_plan import build_plan

    sample = """
    Aula de Semiologia Medica — Ausculta Cardiaca

    MECANISMO DE PRODUCAO DAS BULHAS
    O fechamento valvar gera uma vibracao nas estruturas cardiacas. Essa vibracao
    propaga-se pelo miocardio e pela parede toracica ate o estetoscopio. B1 e mais
    grave e prolongada. B2 e mais aguda e curta. A diferenca acustica resulta das
    propriedades fisicas distintas das valvas aortica, pulmonar, mitral e tricuspide.
    O intervalo entre B1 e B2 corresponde a sistole. O intervalo entre B2 e B1
    corresponde a diastole.

    EXEMPLO DO PROFESSOR
    O professor contou: "Tive um paciente com estenose aortica severa. O sopro era
    tao obvio que dava para ouvir sem estetoscopio. O B2 hipofonetico foi o sinal
    que me fez suspeitar da gravidade antes mesmo do ecocardiograma."
    """

    ctx     = receive(sample, discipline_hint="Semiologia")
    result  = survey(ctx)
    plan    = build_plan(result)
    payloads = teach(plan)

    if payloads:
        print(render_payload(payloads[0]))
    else:
        print("Nenhum bloco gerado.")
