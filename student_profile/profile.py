from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Discipline:
    code: str
    name: str
    professors: List[str]
    schedule: str


@dataclass
class StudentProfile:
    # --- Identity ---
    name: str
    current_period: int
    institution: str
    course: str

    # --- Current disciplines ---
    current_disciplines: List[Discipline] = field(default_factory=list)

    # --- Learning style ---
    learns_best_with: List[str] = field(default_factory=list)
    prior_background: List[str] = field(default_factory=list)
    anchoring_preference: str = ""
    thinking_style: str = ""

    # --- Prior knowledge bank (for Hook de Ancoragem - Módulo 0) ---
    prior_knowledge_bank: Dict[str, str] = field(default_factory=dict)

    # --- Flags ---
    needs_concrete_before_abstract: bool = True
    has_clinical_intuition: bool = False


# ─────────────────────────────────────────────
#  INSTANCE
# ─────────────────────────────────────────────

STUDENT = StudentProfile(
    name="Haecio Medeiros",
    current_period=4,
    institution="UFPB",
    course="Medicina",

    current_disciplines=[
        Discipline(
            code="GDPGN0027",
            name="Atenção à Saúde da Criança e do Adolescente",
            professors=[
                "Valderez Araujo de Lima Ramos",
                "Debora Alencar de Menezes Athayde",
                "Roxana de Almeida Roque Fontes Silva",
                "Renata de Cerqueira Paes Correa Lima",
                "Alexandre Frederico Castanheira Oliveira",
            ],
            schedule="5M45 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDCRG0034",
            name="Bases das Técnicas dos Procedimentos Cirúrgicos e Anestésicos",
            professors=[
                "Carlos Roberto Carvalho Leite",
                "Paulo Roberto da Silva Lima",
                "Sergio da Cunha Falcao",
                "Priscilla Lopes da Fonseca",
            ],
            schedule="2M2345 5T1234 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDPS0041",
            name="Cuidado à Saúde da Família I",
            professors=["Ricardo de Sousa Soares"],
            schedule="3M2345 2T23 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDPGN0028",
            name="Exames Complementares Laboratoriais",
            professors=["Joacilda da Conceicao Nunes"],
            schedule="5M23 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDMEI0072",
            name="Farmacologia Clínica",
            professors=["Maisa Freire Cartaxo Pires de Sa"],
            schedule="4T123 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDFPT0167",
            name="Fitoterapia II",
            professors=[
                "Climerio Avelino de Figueredo",
                "Danielly Albuquerque da Costa",
            ],
            schedule="6T12 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDMEI0074",
            name="Imaginologia Médica I",
            professors=["Carlos Fernando de Mello Junior"],
            schedule="4M23 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDMEI0084",
            name="Módulo Integrador IV",
            professors=["Felipe Gurgel de Araujo"],
            schedule="3T1 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDMEI0085",
            name="O Estudante de Medicina e o Paciente",
            professors=["Jose Givaldo Melquiades de Medeiros"],
            schedule="4M45 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="DPS005142",
            name="Saúde do Trabalhador",
            professors=["Denise Mota Araripe Pereira Fernandez"],
            schedule="4T45 (27/04/2026 - 13/08/2026)",
        ),
        Discipline(
            code="GDMEI0079",
            name="Semiologia Médica",
            professors=[
                "Eliauria Rosa Martins",
                "Guilherme Augusto Teodoro Athayde",
                "Marcelo Dantas Tavares de Melo",
                "Jose Luis Simoes Maroja",
                "Leina Yukari Etto",
                "Aristides Medeiros Leite",
            ],
            schedule="6M2345 3T2345 (27/04/2026 - 13/08/2026)",
        ),
    ],

    # --- Learning style ---
    learns_best_with=[
        "texto estruturado com hierarquia clara",
        "ancoragem concreta antes da abstração",
        "cadeias causais explícitas passo a passo",
        "analogias de computação, sistemas e lógica",
    ],
    prior_background=[
        "computação e sistemas",
        "pensamento algorítmico e lógica formal",
        "programação em Python",
    ],
    anchoring_preference=(
        "Prefere partir de uma situação concreta ou narrativa com desfecho inesperado "
        "antes de qualquer definição formal."
    ),
    thinking_style=(
        "Pensamento sistêmico razoável. "
        "Boa capacidade de seguir cadeias causais. "
        "Pouca intuição clínica prévia."
    ),

    # --- Prior knowledge bank ---
    # Used by Módulo 0 (Hook de Ancoragem Oportunista) to bridge new content
    # to previously studied material. Update each semester.
    prior_knowledge_bank={
        "Morfologia_I_e_II": (
            "Anatomia, histologia, embriologia e fisiologia completas dos sistemas: "
            "Nervoso, Sensorial, Locomotor, Cardiovascular, Respiratório, Digestório, "
            "Endócrino, Reprodutor e Urinário."
        ),
        "Mecanismo_de_Agressao": (
            "Microbiologia (bactérias, fungos, vírus) e Parasitologia "
            "(helmintos, protozoários, vetores clínicos), mecanismos de "
            "patogenicidade e resistência microbiana."
        ),
        "Mecanismo_de_Defesa": (
            "Imunologia (inata, adquirida, autoimunidade, imunologia tumoral) e "
            "Patologia Geral (inflamação aguda/crônica, reparo tecidual, degenerações, "
            "apoptose/necrose e neoplasias)."
        ),
        "Farmacologia_Basica": (
            "Farmacocinética (ADME), Farmacodinâmica (receptores, transdução de sinal), "
            "dosimetria, interações medicamentosas e introdução aos antibióticos."
        ),
        "Bioquimica_e_Metabolismo": (
            "Bioenergética, vias metabólicas (carboidratos, lipídios, compostos "
            "nitrogenados), sinalização/tráfego celular e regulação do equilíbrio "
            "ácido-base."
        ),
    },

    # --- Flags ---
    needs_concrete_before_abstract=True,
    has_clinical_intuition=False,
)
