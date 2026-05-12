[filter_rules.md](https://github.com/user-attachments/files/27651363/filter_rules.md)
# filter_rules.md
> **Localização no repositório:** `prompts/filter_rules.md`

Critérios operacionais que a `phase1_survey.py` aplica ao ler o material bruto.
O objetivo é separar o conteúdo em três categorias antes de montar o plano de aula.

---

## Categorias de classificação

| Categoria | Rótulo interno | O que acontece |
|-----------|---------------|----------------|
| Conteúdo-núcleo | `CORE` | Entra no plano de aula normalmente |
| Ruído pedagógico | `NOISE` | Descartado silenciosamente, sem menção ao aluno |
| Avançado útil | `AHEAD` | Sinalizado no plano, não ensinado agora; registrado para referência futura |

---

## Regra 1 — Ruído pedagógico (`NOISE`)

Descartar silenciosamente qualquer trecho que se enquadre em ao menos um dos critérios abaixo.

### 1.1 Expert blind-spot
O professor usa conceito, sigla ou mecanismo sem definir, assumindo que o aluno já sabe.
Critério operacional: o conceito pressuposto não aparece em nenhuma disciplina com
status `completed` ou `current` na grade curricular do aluno.
Ação: descartar o trecho. Se o conceito for central para entender o tema da aula,
reclassificar como `AHEAD` e sinalizar.

### 1.2 Pergunta de aluno exibicionista
Pergunta feita por aluno durante a aula que:
- introduz nomenclatura ou subtema não coberto no nível atual;
- cita referência avançada (artigo, guideline, protocolo) sem contexto didático;
- desvia o fluxo da aula para um caso-limite ou exceção rara.
Critério operacional: a resposta do professor ao trecho não avança o conceito
principal da aula — ela apenas satisfaz a pergunta pontual.
Ação: descartar pergunta e resposta.

### 1.3 Exemplo descuidado do professor
O professor usa um exemplo que:
- pressupõe cenário clínico não visto até o período atual (status `upcoming`);
- introduz patologia, fármaco ou procedimento fora do escopo do 4º período;
- é mencionado de passagem, sem desenvolvimento didático.
Critério operacional: o exemplo não pode ser explicado com o conhecimento
das disciplinas `completed` + `current`.
Ação: descartar o exemplo. Se o princípio que ele ilustra for importante,
substituir por exemplo compatível com o nível atual.

### 1.4 Digressão sem retorno
Trecho em que o professor sai do tema principal e não retorna explicitamente a ele.
Critério operacional: o trecho não contém conceito, mecanismo ou dado
referenciado em qualquer outra parte da aula.
Ação: descartar.

---

## Regra 2 — Conteúdo avançado útil (`AHEAD`)

Não descartar. Registrar com flag `AHEAD` e incluir nota no plano de aula.

### 2.1 Critério de classificação como `AHEAD`
O conteúdo:
- pertence a disciplina com status `upcoming` na grade;
- mas tem conexão estrutural direta com o tema da aula atual;
- e o professor o menciona com desenvolvimento mínimo (não apenas citação).

Ação: registrar no plano de aula com a nota:
> "⚠️ Conteúdo de nível futuro ({nome_da_disciplina}, {nível}º período).
> Não será ensinado agora. Registrado para referência quando o aluno chegar nesse nível."

### 2.2 O que NÃO é `AHEAD`
- Conteúdo sem conexão com o tema atual → `NOISE`
- Pergunta de aluno sem desenvolvimento do professor → `NOISE`
- Nomenclatura avançada jogada sem explicação → `NOISE`

---

## Regra 3 — Exemplos do professor (`PROFESSOR_EXAMPLE`)

Todo exemplo dado explicitamente pelo professor em aula recebe flag especial.

### 3.1 Critério de identificação
O trecho é um exemplo do professor se:
- o professor narra um caso, situação ou analogia para ilustrar um conceito;
- usa linguagem narrativa ou descritiva, não apenas definição técnica;
- o exemplo tem personagem, cenário ou sequência de eventos.

### 3.2 Comportamento do sistema
- O exemplo é preservado integralmente no plano de aula com flag `PROFESSOR_EXAMPLE`.
- Ao ministrar o bloco correspondente, o sistema o reusa e sinaliza explicitamente:
  > "💬 *Este exemplo foi dado pelo professor em aula.*"
- O sistema NÃO parafraseará nem substituirá o exemplo sem necessidade.
- Se o exemplo for `NOISE` por outro critério (ex: pressupõe nível futuro),
  o sistema extrai o princípio que o exemplo ilustrava e constrói exemplo equivalente
  compatível com o nível atual — sem a flag `PROFESSOR_EXAMPLE`.

---

## Regra 4 — Calibração pelo período atual

O filtro usa a grade curricular (`grade_curricular.py`) como referência fixa.

| Status da disciplina | Conhecimento pode ser pressuposto? | Pode aparecer como `CORE`? |
|---------------------|-----------------------------------|---------------------------|
| `completed` | ✅ Sim | ✅ Sim |
| `current` | ✅ Sim (com cuidado) | ✅ Sim |
| `upcoming` | ❌ Não | ❌ → `AHEAD` ou `NOISE` |
| `internship` | ❌ Não | ❌ → `AHEAD` ou `NOISE` |

**Exceção:** se o aluno explicitamente indicar familiaridade com conteúdo de nível
futuro (ex: estudou por conta própria), o perfil em `profile.py` pode ser atualizado
para refletir isso. O filtro respeita `prior_knowledge_bank` do perfil.

---

## Regra 5 — O que nunca filtrar

Independente de qualquer critério acima, os itens abaixo são sempre `CORE`:

- Definições centrais do tema da aula
- Mecanismos causais principais
- Critérios diagnósticos básicos compatíveis com o nível
- Dados quantitativos relevantes (valores de referência, doses, limiares)
- Qualquer conteúdo que o professor retoma mais de uma vez na aula
  (repetição = sinal de importância pedagógica intencional)

---

## Output esperado do filtro

Para cada trecho do material, a `phase1_survey.py` deve produzir:

```json
{
  "trecho_id": "int",
  "conteudo_resumido": "string",
  "classificacao": "CORE | NOISE | AHEAD | PROFESSOR_EXAMPLE",
  "justificativa": "string",
  "disciplina_referencia": "nome da disciplina + nível, se AHEAD",
  "flag_professor_example": true | false
}
```
