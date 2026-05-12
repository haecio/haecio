# lens_map.md
> **Localização no repositório:** `prompts/lens_map.md`

Mapeamento entre o tipo de seção diagnosticado no survey e as lenses pedagógicas
que a `phase3_teaching.py` deve aplicar ao ministrar aquele bloco.

Uma lens não é um formato de resposta — é uma **instrução de foco** que diz ao
sistema qual aspecto do conteúdo precisa ser trabalhado primeiro e com mais
profundidade para aquele tipo de seção.

---

## Tipos de seção (`section_type`)

Herdados e expandidos da lógica de `diagnose_topic()` em `flowchart2.py`.

| Código | Tipo | Descrição |
|--------|------|-----------|
| `definition` | Definição conceitual | Conceito, termo, princípio ou classificação introdutória |
| `mechanism` | Mecanismo | Via causal, cascata, processo fisiológico ou patológico |
| `taxonomy` | Taxonomia | Tipos, subtipos, fases, estágios, classificações |
| `quant_process` | Processo quantitativo | Curvas, compartimentos, modelos, doses, cinética |
| `clinical_decision` | Decisão clínica | Diagnóstico diferencial, conduta, prognóstico, caso clínico |
| `procedure` | Procedimento | Técnica cirúrgica, anestésica, laboratorial ou de imagem |
| `mixed` | Misto | Seção que combina dois ou mais tipos acima |

---

## Lenses disponíveis

| Lens | O que instrui o sistema a fazer |
|------|--------------------------------|
| `boundary` | Definir o objeto com precisão — o que é e o que não é |
| `mechanism` | Construir a cadeia causal completa passo a passo (Módulo 2) |
| `discrimination` | Identificar o vizinho mais próximo e o discriminador principal |
| `taxonomy_contrast` | Comparar tipos entre si — o que muda de um para o outro e por quê |
| `quant_representation` | Traduzir o processo para diagrama, gráfico ou timeline descritiva |
| `constraints` | Mostrar sob quais condições a regra geral deixa de valer |
| `exceptions` | Trazer o caso especial ou população que inverte a expectativa padrão |
| `clinical_trigger` | Formular a regra If→Then que guia a decisão clínica |
| `failure_mode` | Mostrar o que acontece quando uma peça falha, é bloqueada ou exagerada (Módulo 4) |
| `procedure_rationale` | Explicar o porquê de cada etapa do procedimento, não apenas a sequência |
| `examples_counterexamples` | Dar exemplo concreto + contraexemplo próximo que parece igual mas não é |
| `anchoring` | Conectar o conteúdo novo a disciplina já concluída (Hook — Módulo 0) |

---

## Mapeamento `section_type` → lenses

### `definition`
**Lenses obrigatórias:** `boundary`, `discrimination`, `examples_counterexamples`
**Lens opcional:** `anchoring` (se houver conexão direta com `completed`)

Instrução: comece pelo limite do conceito antes de qualquer propriedade interna.
O aluno precisa saber o que o conceito exclui tanto quanto o que ele inclui.
Definições sem contraexemplo geram falsa familiaridade.

---

### `mechanism`
**Lenses obrigatórias:** `mechanism`, `failure_mode`, `anchoring`
**Lens opcional:** `constraints`

Instrução: siga rigorosamente o pipeline do Módulo 2 —
estado inicial → gatilho → etapas intermediárias → consequência local →
consequência sistêmica → efeito observável.
Nunca pule elos causais.
O `failure_mode` deve aparecer logo após o mecanismo normal, não separado.
O `anchoring` é quase sempre aplicável aqui: mecanismos fisiológicos e
patológicos têm raízes em Morfologia, Bioquímica ou Imunologia (disciplinas `completed`).

---

### `taxonomy`
**Lenses obrigatórias:** `taxonomy_contrast`, `boundary`, `discrimination`
**Lens opcional:** `exceptions`

Instrução: nunca liste os tipos em sequência sem compará-los entre si.
A pergunta central é: o que muda estruturalmente de um tipo para o outro?
Taxonomias são aprendidas por fronteiras e contrastes, não por listas.
Se houver tipo atípico ou exceção clínica relevante, inclua com `exceptions`.

---

### `quant_process`
**Lenses obrigatórias:** `quant_representation`, `boundary`, `constraints`
**Lens opcional:** `anchoring`

Instrução: processos quantitativos (cinética, curvas, modelos de compartimento)
precisam de representação visual descritiva antes de qualquer equação ou número.
Descreva os eixos, o que cada região da curva significa e o que acontece nos extremos.
`constraints` é crítico aqui: o aluno precisa saber quando o modelo não se aplica.

---

### `clinical_decision`
**Lenses obrigatórias:** `clinical_trigger`, `discrimination`, `exceptions`
**Lens opcional:** `failure_mode`

Instrução: o foco é a lógica de decisão, não a lista de achados.
Formule explicitamente a regra If→Then:
"Se [dado clínico X] + [dado Y], então [conduta Z] — porque [mecanismo]."
`discrimination` é central: diagnósticos diferenciais são ganhos por um ou dois
discriminadores, não por memorização de listas.

---

### `procedure`
**Lenses obrigatórias:** `procedure_rationale`, `failure_mode`, `boundary`
**Lens opcional:** `constraints`

Instrução: procedimentos ensinados sem o porquê de cada etapa são memorizados
mas não transferidos.
Para cada passo relevante, explicar: o que essa etapa previne ou garante?
O que acontece se for omitida ou feita errada? (`failure_mode`)
`boundary` define o escopo de indicação — quando o procedimento é adequado
e quando não é.

---

### `mixed`
**Lenses:** selecionar as lenses dos tipos constituintes, priorizando
o tipo dominante da seção.

Instrução: identificar qual `section_type` tem maior peso na seção
e aplicar suas lenses como primárias. As lenses dos tipos secundários
entram como suporte, sem expandir o bloco além do necessário.

---

## Relação entre lenses e módulos pedagógicos

| Lens | Módulo principal acionado |
|------|--------------------------|
| `boundary` | Módulo 1 (contexto) + Módulo 2 (mecanismo inicial) |
| `mechanism` | Módulo 2 |
| `failure_mode` | Módulo 4 |
| `discrimination` | Módulo 5 (teste de compreensão) |
| `taxonomy_contrast` | Módulo 3 (analogia estrutural) + Módulo 5 |
| `quant_representation` | Módulo 3 |
| `constraints` | Módulo 4 |
| `exceptions` | Módulo 4 |
| `clinical_trigger` | Módulo 6 (transferência) |
| `procedure_rationale` | Módulo 2 + Módulo 4 |
| `examples_counterexamples` | Módulo 1 + Módulo 5 |
| `anchoring` | Módulo 0 (background) |

---

## Output esperado do diagnóstico de seção

A `phase1_survey.py` produz, para cada seção identificada no material:

```json
{
  "section_id": "int",
  "title": "string",
  "section_type": "definition | mechanism | taxonomy | quant_process | clinical_decision | procedure | mixed",
  "dominant_type": "string (se mixed)",
  "lenses_selected": ["lens1", "lens2", "lens3"],
  "lenses_optional": ["lens4"],
  "module_chain": ["Módulo 0", "Módulo 2", "Módulo 4"],
  "notes": "string (observações sobre a seção)"
}
```
