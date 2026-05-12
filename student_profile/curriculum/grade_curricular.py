from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class DisciplineStatus(Enum):
    COMPLETED = "completed"       # períodos anteriores ao atual
    CURRENT = "current"           # período atual
    UPCOMING = "upcoming"         # períodos futuros
    INTERNSHIP = "internship"     # internato (9º–12º)


class DisciplineType(Enum):
    MANDATORY = "obrigatória"
    ELECTIVE = "optativa"


@dataclass
class CurriculumDiscipline:
    code: str
    name: str
    workload_hours: int
    level: int                          # 1–12
    type: DisciplineType
    status: DisciplineStatus
    notes: Optional[str] = None         # observações relevantes para o sistema


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────

CURRENT_PERIOD = 4


def _status(level: int) -> DisciplineStatus:
    if level < CURRENT_PERIOD:
        return DisciplineStatus.COMPLETED
    elif level == CURRENT_PERIOD:
        return DisciplineStatus.CURRENT
    elif level >= 9:
        return DisciplineStatus.INTERNSHIP
    else:
        return DisciplineStatus.UPCOMING


def _d(code, name, hours, level, elective=False, notes=None):
    return CurriculumDiscipline(
        code=code,
        name=name,
        workload_hours=hours,
        level=level,
        type=DisciplineType.ELECTIVE if elective else DisciplineType.MANDATORY,
        status=_status(level),
        notes=notes,
    )


# ─────────────────────────────────────────────
#  GRADE CURRICULAR — UFPB MEDICINA
# ─────────────────────────────────────────────

CURRICULUM: List[CurriculumDiscipline] = [

    # ── 1º NÍVEL ──────────────────────────────
    _d("DMRF00201",  "Módulo Integrador I",                                          15,  1),
    _d("DPS005151",  "Cuidado em Saúde na Comunidade",                               60,  1),
    _d("GDBIM0107",  "Estrutura Celular, Bioquímica e Metabolismo",                 105,  1,
       notes="Bioenergética, vias metabólicas, sinalização celular, equilíbrio ácido-base."),
    _d("GDMEI0081",  "Formação Médica",                                              30,  1),
    _d("GDMRF0110",  "Organização Morfológica e Funcional dos Sistemas I",          270,  1,
       notes="Anatomia, histologia, embriologia e fisiologia: Nervoso, Sensorial, "
             "Locomotor, Cardiovascular, Respiratório, Digestório, Endócrino, "
             "Reprodutor e Urinário."),
    _d("GDPS0051",   "Saúde Coletiva I",                                             30,  1),

    # ── 2º NÍVEL ──────────────────────────────
    _d("DFPT00232",  "Organização Morfológica e Funcional dos Sistemas II",         315,  2,
       notes="Continuação de Morfologia I — mesmos sistemas em maior profundidade."),
    _d("DPOG00131",  "Módulo Integrador II",                                         15,  2),
    _d("DPS005152",  "Cuidado em Saúde na Atenção Básica",                           60,  2),
    _d("GDBIM0108",  "Genética Básica",                                              30,  2),
    _d("GDMEI0082",  "Desenvolvimento da Personalidade e Ciclo da Vida",             30,  2),
    _d("GDPOG0028",  "Metodologia do Trabalho Científico",                           30,  2),
    _d("GDPS0052",   "Saúde Coletiva II",                                            30,  2),

    # ── 3º NÍVEL ──────────────────────────────
    _d("DFPT00233",  "Bases da Terapêutica Medicamentosa e Uso de Antimicrobianos",  60,  3,
       notes="Farmacocinética (ADME), Farmacodinâmica, dosimetria, interações "
             "medicamentosas, introdução aos antibióticos."),
    _d("DFPT00234",  "Mecanismos de Agressão",                                      120,  3,
       notes="Microbiologia (bactérias, fungos, vírus) e Parasitologia "
             "(helmintos, protozoários, vetores), patogenicidade e resistência."),
    _d("DFPT00235",  "Mecanismos de Defesa",                                        120,  3,
       notes="Imunologia (inata, adquirida, autoimunidade, imunologia tumoral) e "
             "Patologia Geral (inflamação, reparo, degenerações, apoptose/necrose, "
             "neoplasias)."),
    _d("DIPI00010",  "Módulo Integrador III",                                        15,  3),
    _d("DMEI00174",  "Diversidade Étnica e Cultural na Medicina",                    30,  3),
    _d("DPS005153",  "Cuidado nas Redes de Atenção à Saúde",                         60,  3),
    _d("GDPOG0031",  "Pesquisa Aplicada à Medicina",                                 30,  3),
    _d("GDPS0044",   "Epidemiologia",                                                45,  3),
    _d("GDPS0053",   "Saúde Coletiva III",                                           30,  3),

    # ── 4º NÍVEL — CURRENT ────────────────────
    _d("DMEI00173",  "Saúde e Felicidade",                                           30,  4, elective=True),
    _d("DCRG00142",  "Bases das Técnicas dos Procedimentos Cirúrgicos",             120,  4),
    _d("DMEI00175",  "Farmacologia Clínica",                                         45,  4,
       notes="Continuação de Farmacologia Básica — aplicação clínica dos princípios "
             "de ADME e farmacodinâmica."),
    _d("DPS005154",  "Cuidado à Saúde da Família I",                                 90,  4),
    _d("GDMEI0074",  "Imaginologia Médica I",                                        30,  4),
    _d("GDMEI0079",  "Semiologia Médica",                                           120,  4,
       notes="Primeira exposição sistemática ao exame clínico. Alta densidade de "
             "conteúdo novo sem intuição clínica prévia estabelecida."),
    _d("GDMEI0084",  "Módulo Integrador IV",                                         15,  4),
    _d("GDMEI0085",  "O Estudante de Medicina e o Paciente",                         30,  4),
    _d("GDPGN0027",  "Atenção à Saúde da Criança e do Adolescente",                  30,  4),
    _d("GDPGN0028",  "Exames Complementares Laboratoriais",                          30,  4),

    # ── 5º NÍVEL ──────────────────────────────
    _d("DCRG00132",  "Doenças Prevalentes da Cabeça e Pescoço",                      30,  5, elective=True),
    _d("DCRG00140",  "Cirurgia Plástica",                                            30,  5, elective=True),
    _d("DCRG00145",  "Anestesiologia",                                               30,  5, elective=True),
    _d("DIPI00007",  "Abordagem Clínica e Cirúrgica — Sistema Respiratório e Tórax", 90,  5),
    _d("DIPI00008",  "Doenças do Sistema Tegumentar",                                75,  5),
    _d("DMEI00176",  "Doenças do Sistema Endócrino",                                 60,  5),
    _d("DPS005155",  "Cuidado à Saúde da Família II",                                90,  5),
    _d("GDCRG0032",  "Anatomia Patológica",                                          30,  5),
    _d("GDMEI0068",  "Abordagem Clínica Cirúrgica — Sistema Digestório e Abdome",   105,  5),
    _d("GDMEI0086",  "Relação Médico-Paciente I",                                    30,  5),

    # ── 6º NÍVEL ──────────────────────────────
    _d("DMEI00177",  "Abordagem Clínica e Cirúrgica — Sistema Cardiovascular",      120,  6),
    _d("DMEI00178",  "Nefrologia",                                                   60,  6),
    _d("DPOG00129",  "Ginecologia",                                                 105,  6),
    _d("DPOG00130",  "Obstetrícia",                                                 105,  6),
    _d("GDCRG0042",  "Urologia",                                                     45,  6),
    _d("GDMEI0087",  "Relação Médico-Paciente II",                                   30,  6),
    _d("GDPOG0032",  "Oncologia",                                                    30,  6),

    # ── 7º NÍVEL ──────────────────────────────
    _d("DPGN00124",  "Doenças Raras em Genética Médica e Pediatria",                 30,  7, elective=True),
    _d("DIPI00009",  "Doenças Infecciosas e Parasitárias",                           90,  7),
    _d("DMEI00179",  "Hematologia e Hemoterapia",                                    75,  7),
    _d("DPGN00125",  "Pediatria Clínica",                                           150,  7),
    _d("GDMEI0063",  "Atendimento Inicial às Urgências Clínicas",                    30,  7),
    _d("GDMEI0075",  "Imaginologia Médica II",                                       30,  7),
    _d("GDMEI0088",  "Ética e Bioética na Prática Médica",                           30,  7),
    _d("GDPGN0021",  "Cirurgia Pediátrica",                                          30,  7),
    _d("GDPGN0022",  "Iniciação à Genética Médica",                                  30,  7),
    _d("GDPGN0023",  "Neonatologia",                                                 30,  7),
    _d("GDPOG0029",  "Elaboração do Trabalho de Conclusão de Curso",                 30,  7),

    # ── 8º NÍVEL ──────────────────────────────
    _d("DCRG00143",  "Atendimento Inicial às Urgências Cirúrgicas e Traumatológicas",45,  8),
    _d("DCRG00144",  "Otorrinolaringologia",                                         45,  8),
    _d("DMEI00180",  "Geriatria",                                                    60,  8),
    _d("DMEI00181",  "Neurologia",                                                   75,  8),
    _d("GDCRG0037",  "Oftalmologia",                                                 45,  8),
    _d("GDCRG0038",  "Ortopedia e Traumatologia",                                    45,  8),
    _d("GDMEI0071",  "Elementos de Medicina Legal",                                  60,  8),
    _d("GDMEI0077",  "Reumatologia",                                                 45,  8),
    _d("GDMEI0080",  "Psiquiatria",                                                  60,  8),
    _d("GDMEI0089",  "Dilemas Éticos na Medicina Moderna e no Exercício Profissional",30, 8),

    # ── 9º NÍVEL — INTERNATO ──────────────────
    _d("DCRG00141",  "Internato I — Urgência e Emergência I",                       120,  9),
    _d("DMEI00171",  "Internato I — Clínica Médica I",                              240,  9),
    _d("DMEI00172",  "Internato I — Saúde Mental",                                  240,  9),
    _d("DPS005145",  "Internato I — Saúde Coletiva I",                               60,  9),
    _d("DPS005149",  "Internato I — Medicina de Família e Comunidade I",            300,  9),

    # ── 10º NÍVEL — INTERNATO ─────────────────
    _d("DCRG00146",  "Internato I — Urgência e Emergência II",                      165, 10),
    _d("DPGN00123",  "Internato I — Pediatria I",                                   240, 10),
    _d("DPOG00127",  "Internato I — Ginecologia e Obstetrícia I",                   240, 10),
    _d("DPS005146",  "Internato I — Saúde Coletiva II",                              60, 10),
    _d("GDCRG0035",  "Internato I — Cirurgia I",                                    240, 10),

    # ── 11º NÍVEL — INTERNATO ─────────────────
    _d("DCRG00147",  "Internato II — Urgência e Emergência III",                    135, 11),
    _d("DMEI00184",  "Internato II — Clínica Médica II",                            255, 11),
    _d("DPGN00126",  "Internato II — Pediatria II",                                 255, 11),
    _d("DPS005150",  "Internato II — Medicina de Família e Comunidade II",          315, 11),

    # ── 12º NÍVEL — INTERNATO ─────────────────
    _d("DCRG00138",  "Internato II — Urgência e Emergência IV",                     180, 12),
    _d("DCRG00148",  "Internato II — Cirurgia II",                                  255, 12),
    _d("DMEI00185",  "Internato II — Clínica Médica III",                           240, 12),
    _d("DPOG00128",  "Apresentação e Defesa do TCC",                                 15, 12),
    _d("DPOG00133",  "Internato II — Ginecologia e Obstetrícia II",                 255, 12),
]


# ─────────────────────────────────────────────
#  QUERY HELPERS
# ─────────────────────────────────────────────

def get_by_status(status: DisciplineStatus) -> List[CurriculumDiscipline]:
    return [d for d in CURRICULUM if d.status == status]

def get_by_level(level: int) -> List[CurriculumDiscipline]:
    return [d for d in CURRICULUM if d.level == level]

def get_completed() -> List[CurriculumDiscipline]:
    return get_by_status(DisciplineStatus.COMPLETED)

def get_current() -> List[CurriculumDiscipline]:
    return get_by_status(DisciplineStatus.CURRENT)

def get_upcoming() -> List[CurriculumDiscipline]:
    return get_by_status(DisciplineStatus.UPCOMING)

def knowledge_context_summary() -> str:
    """
    Returns a plain-text summary of completed disciplines for use
    in system prompts and the Hook de Ancoragem (Módulo 0).
    """
    completed = get_completed()
    lines = ["Disciplinas concluídas pelo aluno (base de conhecimento prévio):"]
    for d in completed:
        line = f"  - [{d.code}] {d.name} ({d.workload_hours}h)"
        if d.notes:
            line += f"\n      → {d.notes}"
        lines.append(line)
    return "\n".join(lines)
