"""
core/phase0_reception.py
------------------------
Phase 0 — Reception

Reads the raw input from the user (material + session context) and returns
a validated SessionContext object that all subsequent phases will consume.

Inputs accepted:
  - Raw transcript or didactic material (plain text)
  - Discipline name or code (optional — inferred if omitted)
  - Session goal (optional — defaults to comprehensive study)

Output:
  - SessionContext dataclass
"""

from dataclasses import dataclass, field
from typing import Optional
import sys
import os

# Allow running from repo root or from core/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from student_profile.profile import STUDENT, StudentProfile
from student_profile.curriculum.grade_curricular import (
    CURRICULUM,
    get_current,
    get_completed,
    CurriculumDiscipline,
)


# ─────────────────────────────────────────────
#  SESSION GOAL OPTIONS
# ─────────────────────────────────────────────

class SessionGoal:
    COMPREHENSIVE   = "comprehensive_study"   # full lesson, all blocks
    EXAM_PREP       = "exam_prep"             # high-yield focus, compressed
    SEMINAR         = "seminar_prep"          # structure + argumentation
    QUICK_REVIEW    = "quick_review"          # surface pass, no deep dives
    CUSTOM          = "custom"                # user-defined


# ─────────────────────────────────────────────
#  OUTPUT DATACLASS
# ─────────────────────────────────────────────

@dataclass
class SessionContext:
    # Raw material
    raw_material: str

    # Student
    student: StudentProfile

    # Discipline matched (None if not identified)
    matched_discipline: Optional[CurriculumDiscipline]

    # Session goal
    goal: str = SessionGoal.COMPREHENSIVE

    # Constraints declared by user (e.g. "only 30 minutes", "skip procedures")
    constraints: str = ""

    # Flags derived from profile
    needs_concrete_before_abstract: bool = True
    has_clinical_intuition: bool = False

    # Knowledge available to the student at this point
    completed_discipline_names: list = field(default_factory=list)
    current_discipline_names: list = field(default_factory=list)

    # Metadata
    material_char_count: int = 0
    material_word_count: int = 0


# ─────────────────────────────────────────────
#  DISCIPLINE MATCHER
# ─────────────────────────────────────────────

def _match_discipline(
    hint: Optional[str],
    material: str,
) -> Optional[CurriculumDiscipline]:
    """
    Try to match a discipline from hint (code or name) or by scanning
    the material for known discipline names.
    Returns the best match or None.
    """
    if not hint and not material:
        return None

    candidates = get_current() + get_completed()

    # 1. Exact code match
    if hint:
        hint_upper = hint.strip().upper()
        for d in candidates:
            if d.code.upper() == hint_upper:
                return d

    # 2. Name substring match (hint)
    if hint:
        hint_lower = hint.strip().lower()
        for d in candidates:
            if hint_lower in d.name.lower():
                return d

    # 3. Scan first 500 chars of material for discipline name keywords
    material_head = material[:500].lower()
    best_match = None
    best_score = 0
    for d in candidates:
        # Score = number of significant words from discipline name found in material
        keywords = [
            w for w in d.name.lower().split()
            if len(w) > 4  # skip short words like "de", "do", "e"
        ]
        score = sum(1 for kw in keywords if kw in material_head)
        if score > best_score:
            best_score = score
            best_match = d

    return best_match if best_score >= 2 else None


# ─────────────────────────────────────────────
#  MAIN FUNCTION
# ─────────────────────────────────────────────

def receive(
    raw_material: str,
    discipline_hint: Optional[str] = None,
    goal: str = SessionGoal.COMPREHENSIVE,
    constraints: str = "",
) -> SessionContext:
    """
    Entry point for Phase 0.

    Parameters
    ----------
    raw_material      : full text of the lecture transcript or didactic material
    discipline_hint   : optional discipline name or code to help matching
    goal              : session goal (use SessionGoal constants)
    constraints       : any user-declared constraints as free text

    Returns
    -------
    SessionContext ready to be passed to phase1_survey.survey()
    """

    if not raw_material or not raw_material.strip():
        raise ValueError(
            "raw_material está vazio. Envie o texto da aula ou material didático."
        )

    matched = _match_discipline(discipline_hint, raw_material)

    completed = get_completed()
    current   = get_current()

    ctx = SessionContext(
        raw_material                 = raw_material.strip(),
        student                      = STUDENT,
        matched_discipline           = matched,
        goal                         = goal,
        constraints                  = constraints.strip(),
        needs_concrete_before_abstract = STUDENT.needs_concrete_before_abstract,
        has_clinical_intuition       = STUDENT.has_clinical_intuition,
        completed_discipline_names   = [d.name for d in completed],
        current_discipline_names     = [d.name for d in current],
        material_char_count          = len(raw_material.strip()),
        material_word_count          = len(raw_material.strip().split()),
    )

    return ctx


# ─────────────────────────────────────────────
#  DISPLAY HELPER
# ─────────────────────────────────────────────

def describe(ctx: SessionContext) -> str:
    disc = ctx.matched_discipline
    disc_str = (
        f"{disc.name} [{disc.code}] — {disc.level}º período ({disc.status.value})"
        if disc else "Não identificada automaticamente"
    )
    lines = [
        "=" * 60,
        "  PHASE 0 — SESSION CONTEXT",
        "=" * 60,
        f"  Aluno          : {ctx.student.name} — {ctx.student.current_period}º período",
        f"  Disciplina     : {disc_str}",
        f"  Objetivo       : {ctx.goal}",
        f"  Restrições     : {ctx.constraints or 'nenhuma'}",
        f"  Material       : {ctx.material_word_count} palavras / {ctx.material_char_count} caracteres",
        f"  Intuição clín. : {'sim' if ctx.has_clinical_intuition else 'não'}",
        "=" * 60,
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    Aula de Semiologia Médica — Semana 3
    Tema: Ausculta Cardíaca
    Professora: Eliauria Rosa Martins

    Hoje vamos aprender a identificar as bulhas cardíacas normais e os principais
    sopros. A primeira bulha (B1) corresponde ao fechamento das valvas mitral e
    tricúspide. A segunda bulha (B2) corresponde ao fechamento das valvas aórtica
    e pulmonar...
    """

    ctx = receive(
        raw_material     = sample,
        discipline_hint  = None,
        goal             = SessionGoal.COMPREHENSIVE,
        constraints      = "",
    )

    print(describe(ctx))
    print(f"\nDisciplinas concluídas disponíveis: {len(ctx.completed_discipline_names)}")
    print(f"Disciplinas atuais disponíveis    : {len(ctx.current_discipline_names)}")
