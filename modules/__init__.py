"""
modules/__init__.py
-------------------
Exports all pedagogical modules as a unified interface.
Each module is the authoritative source for its teaching instructions.
phase3_teaching.py imports from here — never hardcodes instructions directly.
"""

from modules.modulo0_hook    import MODIFICADOR_PASSIVO
from modules.modulo1_context import MODULO_1
from modules.modulo2_causal  import MODULO_2
from modules.modulo3_analogy import MODULO_3
from modules.modulo4_failure import MODULO_4
from modules.modulo5_test    import MODULO_5
from modules.modulo6_transfer import MODULO_6

__all__ = [
    "MODIFICADOR_PASSIVO",
    "MODULO_1",
    "MODULO_2",
    "MODULO_3",
    "MODULO_4",
    "MODULO_5",
    "MODULO_6",
]
