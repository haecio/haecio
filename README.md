# Professor Gemini

Pipeline pedagógico que transforma transcrições de aulas universitárias em sessões de ensino calibradas para o aluno — preservando o conteúdo do professor, eliminando ruído e garantindo formação de competências.

---

## O que faz

O Professor Gemini recebe a transcrição de uma aula real e:

1. **Filtra** o que não serve — perguntas de aluno sem desenvolvimento, conteúdo de nível futuro, digressões
2. **Classifica** cada seção por tipo pedagógico (mecanismo, definição, taxonomia, decisão clínica etc.)
3. **Monta um plano de aula** ordenado com estimativa de profundidade por bloco
4. **Dá a aula** — mesma sequência do professor, mas com pedagogia completa: situação concreta antes de definição, cadeia causal explícita, exemplos do professor preservados com atribuição, e teste de competência ao final de cada bloco

A aula termina quando o aluno demonstra que consegue usar o conhecimento — não quando o conteúdo foi coberto.

---

## Estrutura do repositório

```
professor-gemini/
├── main.py                       # Entry point — CLI e orquestrador
├── core/
│   ├── phase0_reception.py       # Lê o material e constrói o SessionContext
│   ├── phase1_survey.py          # Segmenta, filtra e classifica seções
│   ├── phase2_lesson_plan.py     # Monta o plano de aula em blocos ordenados
│   └── phase3_teaching.py        # Gera os payloads de instrução para o Gemini
├── modules/
│   ├── __init__.py               # Exporta todos os módulos pedagógicos
│   ├── modulo0_hook.py           # Hook de Ancoragem (background silencioso)
│   ├── modulo1_context.py        # Contexto Antes do Conteúdo
│   ├── modulo2_causal.py         # Modelo Causal Explícito
│   ├── modulo3_analogy.py        # Analogia Estrutural
│   ├── modulo4_failure.py        # O Que Muda Se Algo Falha
│   ├── modulo5_test.py           # Teste de Competência Real
│   └── modulo6_transfer.py       # Transferência para Novos Contextos
├── prompts/
│   ├── filter_rules.md           # Regras de filtragem de conteúdo
│   ├── lens_map.md               # Mapeamento tipo de seção → lenses → módulos
│   └── system_prompt.md          # System prompt completo para o Gemini
├── student_profile/
│   ├── profile.py                # Perfil do aluno (Haécio Medeiros, 4º período)
│   └── curriculum/
│       └── grade_curricular.py   # Grade curricular completa com status por disciplina
└── tests/
    └── test_pipeline.py          # Suite de 16 testes cobrindo todas as fases
```

---

## Como usar

### Modo interativo (cola a transcrição no terminal)
```bash
python main.py
```

### A partir de arquivo `.txt`
```bash
python main.py --file aula_semiologia.txt
```

### Só o plano, sem ensinar
```bash
python main.py --file aula.txt --dry-run
```

### Testar um bloco específico
```bash
python main.py --file aula.txt --block 2
```

### Com objetivo definido
```bash
python main.py --file aula.txt --discipline Semiologia --goal exam
```

**Opções de `--goal`:** `comprehensive` (padrão) · `exam` · `seminar` · `review`

---

## Como configurar no Gemini

1. Acesse [gemini.google.com](https://gemini.google.com) → **Gems** → **Create a Gem**
2. Em **Instructions**, cole o conteúdo de `prompts/system_prompt.md`
3. Salve com o nome **Professor Gemini**
4. Para usar: abra o Gem e envie a transcrição da aula diretamente no chat

O pipeline (Phase 0–3) roda internamente no Gem. O aluno não vê código — só a aula.

---

## Rodando os testes

```bash
python tests/test_pipeline.py
```

16 testes cobrindo:
- Validação de input (Phase 0)
- Filtragem e classificação de seções (Phase 1)
- Ordenação e montagem do plano (Phase 2)
- Estrutura dos payloads de ensino (Phase 3)
- Importação dos módulos pedagógicos
- Pipeline completo de ponta a ponta

---

## Pipeline interno

```
Transcrição da aula
       │
       ▼
Phase 0 — receive()
  Valida input, identifica disciplina, constrói SessionContext
       │
       ▼
Phase 1 — survey()
  Segmenta → Filtra (CORE / NOISE / AHEAD) → Classifica tipo → Atribui lenses
       │
       ▼
Phase 2 — build_plan()
  Ordena blocos pedagogicamente → Anexa exemplos do professor → Estima profundidade
  → Exibe plano → Aguarda confirmação do aluno
       │
       ▼
Phase 3 — teach()
  Para cada bloco: monta TeachingPayload com perfil do aluno,
  contexto de ancoragem, instruções por etapa e pausa obrigatória
       │
       ▼
Gemini ministra a aula bloco a bloco
```

---

## Filtros aplicados (Phase 1)

| Tag | Critério | Destino |
|-----|----------|---------|
| `CORE` | Conteúdo compatível com o nível atual | Entra na aula |
| `NOISE` | Pergunta de aluno sem desenvolvimento, trecho < 15 palavras, digressão | Descartado silenciosamente |
| `AHEAD` | Conteúdo de disciplina futura com desenvolvimento real | Registrado ao final |
| `PROFESSOR_EXAMPLE` | Flag adicional em seções CORE | Preservado com atribuição `💬` |

---

## Dependências

Python 3.10+ · Biblioteca padrão apenas · Sem dependências externas

---

## Aluno configurado

Haécio Medeiros · Medicina · UFPB · 4º período  
Perfil completo em `student_profile/profile.py`
