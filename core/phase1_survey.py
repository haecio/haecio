"""
core/phase1_survey.py
---------------------
Phase 1 — Survey + Filter

Receives a SessionContext from phase0_reception and returns a SurveyResult:
  - Full section map of the material
  - Each section classified (CORE / NOISE / AHEAD / PROFESSOR_EXAMPLE)
  - Each section diagnosed by type and assigned lenses
  - Ordered list of blocks ready for phase2_lesson_plan

This phase does NOT teach. It only reads, classifies, and plans.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import re
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.phase0_reception import SessionContext
from student_profile.curriculum.grade_curricular import (
    CURRICULUM,
    DisciplineStatus,
)


# ─────────────────────────────────────────────
#  CONSTANTS — from filter_rules.md
# ─────────────────────────────────────────────

class Tag:
    CORE              = "CORE"
    NOISE             = "NOISE"
    AHEAD             = "AHEAD"
    PROFESSOR_EXAMPLE = "PROFESSOR_EXAMPLE"

class NoiseReason:
    EXPERT_BLIND_SPOT = "expert_blind_spot"
    SHOWOFF_QUESTION  = "showoff_student_question"
    CARELESS_EXAMPLE  = "careless_professor_example"
    DIGRESSION        = "digression_no_return"

class SectionType:
    DEFINITION        = "definition"
    MECHANISM         = "mechanism"
    TAXONOMY          = "taxonomy"
    QUANT_PROCESS     = "quant_process"
    CLINICAL_DECISION = "clinical_decision"
    PROCEDURE         = "procedure"
    MIXED             = "mixed"


# ─────────────────────────────────────────────
#  DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class SurveySection:
    section_id: int
    title: str
    raw_text: str
    tag: str = Tag.CORE
    noise_reason: Optional[str] = None
    ahead_discipline: Optional[str] = None
    is_professor_example: bool = False
    filter_justification: str = ""
    section_type: str = SectionType.MIXED
    dominant_type: Optional[str] = None
    lenses_required: List[str] = field(default_factory=list)
    lenses_optional: List[str] = field(default_factory=list)
    module_chain: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class SurveyResult:
    ctx: SessionContext
    sections: List[SurveySection]

    @property
    def core_sections(self):
        return [s for s in self.sections if s.tag == Tag.CORE]

    @property
    def professor_examples(self):
        return [s for s in self.sections if s.is_professor_example]

    @property
    def noise_sections(self):
        return [s for s in self.sections if s.tag == Tag.NOISE]

    @property
    def ahead_sections(self):
        return [s for s in self.sections if s.tag == Tag.AHEAD]

    def summary(self) -> str:
        core  = len(self.core_sections)
        noise = len(self.noise_sections)
        ahead = len(self.ahead_sections)
        pex   = len(self.professor_examples)
        lines = [
            "=" * 62,
            "  PHASE 1 — SURVEY RESULT",
            "=" * 62,
            f"  Total de secoes identificadas : {len(self.sections)}",
            f"  CORE  (entrara na aula)       : {core}",
            f"  NOISE (descartado)            : {noise}",
            f"  AHEAD (nivel futuro)          : {ahead}",
            f"  Exemplos do professor         : {pex}",
            "=" * 62,
            "  Secoes CORE:",
        ]
        for s in self.core_sections:
            flag = " [PROFESSOR_EXAMPLE]" if s.is_professor_example else ""
            lines.append(f"    [{s.section_id}] {s.title}{flag}")
            lines.append(f"         tipo  : {s.section_type}")
            lines.append(f"         lenses: {', '.join(s.lenses_required)}")
        if self.ahead_sections:
            lines.append("  Secoes AHEAD:")
            for s in self.ahead_sections:
                lines.append(f"    [{s.section_id}] {s.title} -> {s.ahead_discipline}")
        if self.noise_sections:
            lines.append("  Secoes NOISE (motivo):")
            for s in self.noise_sections:
                lines.append(f"    [{s.section_id}] {s.title} -> {s.noise_reason}")
        lines.append("=" * 62)
        return "\n".join(lines)


# ─────────────────────────────────────────────
#  STEP 1 — SEGMENT
# ─────────────────────────────────────────────

_HEADING = re.compile(
    r"^(?:"
    r"#{1,3} .+"
    r"|[0-9]+[.)]+[ ].+"
    r"|[A-ZÀ-ÿ][A-ZÀ-ÿ ]{5,}"
    r"|[A-ZÀ-ÿ].+—.+"
    r"|[A-ZÀ-ÿ][a-zÀ-ÿ ]{4,}:$"
    r")$"
)


def _segment(raw: str) -> List[dict]:
    sections = []
    current_title = "Introducao"
    current_lines: List[str] = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            if current_lines:
                sections.append({
                    "title": current_title,
                    "text": " ".join(current_lines).strip(),
                })
                current_lines = []
                current_title = f"Bloco {len(sections) + 1}"
            continue
        if _HEADING.match(stripped) and len(stripped) < 100:
            if current_lines:
                sections.append({
                    "title": current_title,
                    "text": " ".join(current_lines).strip(),
                })
                current_lines = []
            current_title = stripped.lstrip("#").strip().rstrip(":")
        else:
            current_lines.append(stripped)

    if current_lines:
        sections.append({"title": current_title, "text": " ".join(current_lines).strip()})

    sections = [s for s in sections if s["text"].strip()]

    if len(sections) <= 1:
        paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
        sections = [{"title": f"Bloco {i+1}", "text": p} for i, p in enumerate(paras)]

    return sections


# ─────────────────────────────────────────────
#  STEP 2 — FILTER (filter_rules.md)
# ─────────────────────────────────────────────

_UPCOMING_SIGNALS = [
    "internato", "residencia", "especialidade", "protocolo avancado",
    "guideline", "meta-analise", "revisao sistematica",
]
_SHOWOFF_SIGNALS = [
    "pergunta do aluno", "aluno perguntou", "aluno questionou",
    "questao levantada", "um aluno disse",
]
_EXAMPLE_SIGNALS = [
    "por exemplo", "imagine que", "pense em", "vamos supor", "caso de",
    "certa vez", "um paciente", "uma paciente", "tive um caso",
    "lembro de um caso", "na minha pratica", "como eu vi",
    "professor contou", "professor disse que", "o professor trouxe",
    "ele contou", "ela contou",
]


def _build_upcoming_names(ctx: SessionContext) -> List[str]:
    return [
        d.name.lower()
        for d in CURRICULUM
        if d.status in (DisciplineStatus.UPCOMING, DisciplineStatus.INTERNSHIP)
    ]


def _filter(title: str, text: str, upcoming_names: List[str]) -> dict:
    combined = (title + " " + text).lower()
    is_prof  = any(sig in combined for sig in _EXAMPLE_SIGNALS)

    # Rule 1.2 — showoff question
    if any(sig in combined for sig in _SHOWOFF_SIGNALS):
        return {"tag": Tag.NOISE, "noise_reason": NoiseReason.SHOWOFF_QUESTION,
                "ahead_discipline": None, "is_professor_example": False,
                "justification": "Pergunta de aluno sem desenvolvimento docente."}

    # Rule 1.4 — too short
    wc = len(text.split())
    if wc < 15 and not is_prof:
        return {"tag": Tag.NOISE, "noise_reason": NoiseReason.DIGRESSION,
                "ahead_discipline": None, "is_professor_example": False,
                "justification": "Trecho muito curto sem conteudo conceitual."}

    # Rule 2 — AHEAD
    matched = None
    for name in upcoming_names:
        kws = [w for w in name.split() if len(w) > 4]
        if sum(1 for kw in kws if kw in combined) >= 2:
            matched = name
            break
    if not matched and any(sig in combined for sig in _UPCOMING_SIGNALS):
        matched = "conteudo de nivel avancado/internato"

    if matched:
        if wc >= 40:
            return {"tag": Tag.AHEAD, "noise_reason": None, "ahead_discipline": matched,
                    "is_professor_example": is_prof,
                    "justification": f"Disciplina futura: {matched}."}
        return {"tag": Tag.NOISE, "noise_reason": NoiseReason.EXPERT_BLIND_SPOT,
                "ahead_discipline": None, "is_professor_example": False,
                "justification": f"Mencao breve a conteudo avancado ({matched})."}

    # Rule 5 — CORE
    return {"tag": Tag.CORE, "noise_reason": None, "ahead_discipline": None,
            "is_professor_example": is_prof,
            "justification": "Conteudo compativel com o nivel atual."}


# ─────────────────────────────────────────────
#  STEP 3 — DIAGNOSE + LENSES (lens_map.md)
# ─────────────────────────────────────────────

_TYPE_KW = {
    SectionType.MECHANISM:         ["mecanismo","cascata","via","patogenese","fisiopatologia",
                                    "processo","cadeia","ativacao","inibicao","leva a","resulta em"],
    SectionType.TAXONOMY:          ["tipos","classificacao","formas","subtipos","fases",
                                    "estagios","categorias"],
    SectionType.QUANT_PROCESS:     ["curva","compartimento","distribuicao","absorcao","eliminacao",
                                    "meia-vida","cinetica","farmacocinetica","dose","concentracao"],
    SectionType.CLINICAL_DECISION: ["diagnostico","sindrome","quadro clinico","conduta","tratamento",
                                    "diferencial","sinal","sintoma","exame","investigacao"],
    SectionType.PROCEDURE:         ["tecnica","procedimento","cirurgia","anestesia","incisao",
                                    "sutura","puncao","radiografia","ultrassom","tomografia"],
    SectionType.DEFINITION:        ["definicao","conceito","o que e","denomina-se","entende-se",
                                    "refere-se","e caracterizado","e definido"],
}

_LENS_MAP = {
    SectionType.DEFINITION:        {"required":["boundary","discrimination","examples_counterexamples"],
                                    "optional":["anchoring"],
                                    "modules":["Modulo 1","Modulo 2","Modulo 5"]},
    SectionType.MECHANISM:         {"required":["mechanism","failure_mode","anchoring"],
                                    "optional":["constraints"],
                                    "modules":["Modulo 0","Modulo 2","Modulo 4"]},
    SectionType.TAXONOMY:          {"required":["taxonomy_contrast","boundary","discrimination"],
                                    "optional":["exceptions"],
                                    "modules":["Modulo 3","Modulo 5"]},
    SectionType.QUANT_PROCESS:     {"required":["quant_representation","boundary","constraints"],
                                    "optional":["anchoring"],
                                    "modules":["Modulo 3","Modulo 4"]},
    SectionType.CLINICAL_DECISION: {"required":["clinical_trigger","discrimination","exceptions"],
                                    "optional":["failure_mode"],
                                    "modules":["Modulo 5","Modulo 6"]},
    SectionType.PROCEDURE:         {"required":["procedure_rationale","failure_mode","boundary"],
                                    "optional":["constraints"],
                                    "modules":["Modulo 2","Modulo 4"]},
    SectionType.MIXED:             {"required":["boundary","discrimination"],
                                    "optional":["anchoring","mechanism"],
                                    "modules":["Modulo 1","Modulo 2"]},
}


def _diagnose(title: str, text: str) -> str:
    combined = (title + " " + text).lower()
    scores = {t: sum(1 for kw in kws if kw in combined) for t, kws in _TYPE_KW.items()}
    best   = max(scores, key=scores.get)
    if scores[best] == 0:
        return SectionType.MIXED
    top2 = sorted(scores.values(), reverse=True)[:2]
    if len(top2) == 2 and top2[0] - top2[1] <= 1:
        return SectionType.MIXED
    return best


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def survey(ctx: SessionContext) -> SurveyResult:
    raw_secs       = _segment(ctx.raw_material)
    upcoming_names = _build_upcoming_names(ctx)
    result: List[SurveySection] = []

    for idx, sec in enumerate(raw_secs):
        title, text = sec["title"], sec["text"]
        f = _filter(title, text, upcoming_names)

        if f["tag"] != Tag.NOISE:
            stype  = _diagnose(title, text)
            lenses = _LENS_MAP.get(stype, _LENS_MAP[SectionType.MIXED])
        else:
            stype  = SectionType.MIXED
            lenses = {"required": [], "optional": [], "modules": []}

        result.append(SurveySection(
            section_id           = idx + 1,
            title                = title,
            raw_text             = text,
            tag                  = f["tag"],
            noise_reason         = f.get("noise_reason"),
            ahead_discipline     = f.get("ahead_discipline"),
            is_professor_example = f.get("is_professor_example", False),
            filter_justification = f.get("justification", ""),
            section_type         = stype,
            lenses_required      = lenses["required"],
            lenses_optional      = lenses["optional"],
            module_chain         = lenses["modules"],
        ))

    return SurveyResult(ctx=ctx, sections=result)


# ─────────────────────────────────────────────
#  QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    from core.phase0_reception import receive, SessionGoal

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

    ctx = receive(sample, discipline_hint="Semiologia")
    result = survey(ctx)
    print(result.summary())
