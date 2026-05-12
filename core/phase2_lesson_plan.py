"""
core/phase2_lesson_plan.py
--------------------------
Phase 2 — Lesson Plan Builder

Receives a SurveyResult from phase1_survey and returns a LessonPlan:
  - Ordered blocks derived from CORE sections
  - Each block has: title, type, lenses, module chain, depth estimate,
    professor examples attached, and AHEAD notes appended at the end
  - The plan is shown to the student before teaching begins
  - Teaching only starts after student confirmation

This phase does NOT teach. It organises and presents the plan.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.phase1_survey import SurveyResult, SurveySection, Tag, SectionType


# ─────────────────────────────────────────────
#  DEPTH ESTIMATION
# ─────────────────────────────────────────────
# Maps section type + word count to a depth label.
# Used to set student expectations before each block.

class Depth:
    QUICK   = "rápido"        # < 80 words, simple type
    MEDIUM  = "médio"         # 80–250 words or complex type
    DEEP    = "aprofundado"   # > 250 words or mechanism/procedure


def _estimate_depth(section: SurveySection) -> str:
    wc = len(section.raw_text.split())
    deep_types = {SectionType.MECHANISM, SectionType.PROCEDURE, SectionType.QUANT_PROCESS}
    if section.section_type in deep_types or wc > 250:
        return Depth.DEEP
    if wc > 80:
        return Depth.MEDIUM
    return Depth.QUICK


# ─────────────────────────────────────────────
#  BLOCK ORDERING
# ─────────────────────────────────────────────
# Preferred teaching order: definitions first, then mechanisms,
# then taxonomy/quant, then clinical decision, then procedure.
# Mixed and unknown go last within their position.

_TYPE_ORDER = {
    SectionType.DEFINITION:        0,
    SectionType.MECHANISM:         1,
    SectionType.TAXONOMY:          2,
    SectionType.QUANT_PROCESS:     3,
    SectionType.CLINICAL_DECISION: 4,
    SectionType.PROCEDURE:         5,
    SectionType.MIXED:             6,
}


def _sort_key(section: SurveySection):
    # Primary: pedagogical type order
    # Secondary: original position in material (preserves professor's intent)
    return (_TYPE_ORDER.get(section.section_type, 99), section.section_id)


# ─────────────────────────────────────────────
#  DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class LessonBlock:
    block_number: int
    title: str
    section_type: str
    lenses: List[str]
    module_chain: List[str]
    depth: str
    raw_text: str
    professor_examples: List[str] = field(default_factory=list)
    notes: str = ""
    original_section_id: int = 0


@dataclass
class LessonPlan:
    survey: SurveyResult
    blocks: List[LessonBlock]
    ahead_notes: List[str] = field(default_factory=list)
    total_blocks: int = 0

    def display(self) -> str:
        disc = self.survey.ctx.matched_discipline
        disc_str = disc.name if disc else "Disciplina não identificada"
        goal     = self.survey.ctx.goal

        lines = [
            "",
            "╔" + "═" * 60 + "╗",
            "║  PLANO DE AULA".ljust(61) + "║",
            "╠" + "═" * 60 + "╣",
            f"║  Disciplina : {disc_str[:44]}".ljust(61) + "║",
            f"║  Objetivo   : {goal[:44]}".ljust(61) + "║",
            f"║  Blocos     : {self.total_blocks}".ljust(61) + "║",
            "╠" + "═" * 60 + "╣",
        ]

        for b in self.blocks:
            pex = "  💬 exemplo do professor" if b.professor_examples else ""
            lines.append(
                f"║  Bloco {b.block_number:<2}  {b.title[:36]:<36}  [{b.depth}]".ljust(61) + "║"
            )
            lines.append(
                f"║    tipo: {b.section_type:<18} lenses: {len(b.lenses)}".ljust(61) + "║"
            )
            if pex:
                lines.append(f"║{pex}".ljust(61) + "║")
            lines.append("║" + "─" * 60 + "║")

        if self.ahead_notes:
            lines.append("║  ⚠ CONTEÚDO DE NÍVEL FUTURO (registrado):".ljust(61) + "║")
            for note in self.ahead_notes:
                lines.append(f"║    · {note[:53]}".ljust(61) + "║")
            lines.append("║" + "─" * 60 + "║")

        lines += [
            "║  Pronto para começar? Confirme para iniciar o Bloco 1.".ljust(61) + "║",
            "╚" + "═" * 60 + "╝",
            "",
        ]
        return "\n".join(lines)


# ─────────────────────────────────────────────
#  ATTACH PROFESSOR EXAMPLES
# ─────────────────────────────────────────────

def _attach_examples(
    block_section: SurveySection,
    all_sections: List[SurveySection],
) -> List[str]:
    """
    Find professor examples that are thematically close to this block.
    Strategy: if a PROFESSOR_EXAMPLE section immediately precedes or follows
    the block section, or if its raw_text shares keywords with the block.
    """
    examples = []
    block_kws = set(block_section.raw_text.lower().split())
    block_idx  = block_section.section_id

    for sec in all_sections:
        if not sec.is_professor_example:
            continue
        # Proximity: within 2 section IDs
        if abs(sec.section_id - block_idx) <= 2:
            examples.append(sec.raw_text)
            continue
        # Keyword overlap: at least 4 shared non-trivial words
        ex_kws  = set(sec.raw_text.lower().split())
        overlap = {w for w in block_kws & ex_kws if len(w) > 4}
        if len(overlap) >= 4:
            examples.append(sec.raw_text)

    return examples


# ─────────────────────────────────────────────
#  MAIN FUNCTION
# ─────────────────────────────────────────────

def build_plan(survey_result: SurveyResult) -> LessonPlan:
    """
    Entry point for Phase 2.

    Parameters
    ----------
    survey_result : SurveyResult from phase1_survey.survey()

    Returns
    -------
    LessonPlan ready to be displayed to the student and
    passed to phase3_teaching.teach()
    """
    core    = survey_result.core_sections
    all_sec = survey_result.sections

    # Sort blocks in pedagogical order
    ordered = sorted(
        [s for s in core if not s.is_professor_example],
        key=_sort_key,
    )

    blocks: List[LessonBlock] = []
    for i, sec in enumerate(ordered):
        examples = _attach_examples(sec, all_sec)
        blocks.append(LessonBlock(
            block_number        = i + 1,
            title               = sec.title,
            section_type        = sec.section_type,
            lenses              = sec.lenses_required,
            module_chain        = sec.module_chain,
            depth               = _estimate_depth(sec),
            raw_text            = sec.raw_text,
            professor_examples  = examples,
            original_section_id = sec.section_id,
        ))

    # Collect AHEAD notes for display
    ahead_notes = [
        f"{s.title} → {s.ahead_discipline}"
        for s in survey_result.ahead_sections
    ]

    plan = LessonPlan(
        survey       = survey_result,
        blocks       = blocks,
        ahead_notes  = ahead_notes,
        total_blocks = len(blocks),
    )
    return plan


# ─────────────────────────────────────────────
#  QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from core.phase0_reception import receive, SessionGoal
    from core.phase1_survey import survey

    sample = """
    Aula de Semiologia Medica — Ausculta Cardiaca

    INTRODUCAO
    A ausculta cardiaca e uma das habilidades fundamentais do exame fisico.
    O medico utiliza o estetoscopio para identificar sons produzidos pelo coracao.

    BULHAS CARDIACAS — DEFINICAO
    A primeira bulha (B1) e o som produzido pelo fechamento das valvas mitral e
    tricuspide, marcando o inicio da sistole. A segunda bulha (B2) corresponde
    ao fechamento das valvas aortica e pulmonar, marcando o fim da sistole.

    MECANISMO DE PRODUCAO DAS BULHAS
    O fechamento valvar gera uma vibracao nas estruturas cardiacas. Essa vibracao
    propaga-se pelo miocardio e pela parede toracica ate o estetoscopio. B1 e mais
    grave e prolongada. B2 e mais aguda e curta.

    EXEMPLO DO PROFESSOR
    O professor contou: "Tive um paciente com estenose aortica severa. O sopro era
    tao obvio que dava para ouvir sem estetoscopio. O B2 hipofonetico foi o sinal
    que me fez suspeitar da gravidade."

    CLASSIFICACAO DOS SOPROS
    Os sopros sao classificados quanto ao timing (sistolico, diastolico, continuo),
    intensidade (graus I a VI de Levine), localizacao, irradiacao e qualidade.

    PERGUNTA DO ALUNO
    Um aluno perguntou sobre a fisiopatologia da insuficiencia cardiaca congestiva
    descompensada e sua relacao com o BNP e os criterios de Framingham revisados.
    O professor respondeu que seria visto no internato.

    CONDUTA DIAGNOSTICA
    Diante de um sopro, o medico deve identificar o foco de maior intensidade,
    a irradiacao e o timing. Isso orienta o diagnostico diferencial entre
    estenose, insuficiencia e comunicacoes anomalas.
    """

    ctx    = receive(sample, discipline_hint="Semiologia")
    result = survey(ctx)
    plan   = build_plan(result)
    print(plan.display())
