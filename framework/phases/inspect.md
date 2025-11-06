# SHIELD Phase: INSPECT (Inspeção)

**Versão:** 1.0
**Fase:** I - INSPECT
**Responsável:** IA (auto-inspeção), depois Humano (validação no HALT)
**Modo Obrigatório:** Strict

---

## 📖 Visão Geral

A fase **INSPECT** é onde o agente valida a qualidade do trabalho executado usando checklists estruturados. É uma auto-avaliação rigorosa que acontece ANTES de qualquer resultado ser apresentado ao usuário.

**Princípio Fundamental:** "Inspecione tudo. Assuma nada. Um único item falhando = LOOP."

---

## 🎯 Objetivos da Fase INSPECT

1. **Validar** qualidade do output usando checklists
2. **Identificar** problemas antes de apresentar ao usuário
3. **Acionar** LOOP se necessário (auto-correção)
4. **Documentar** resultado da inspeção
5. **Garantir** conformidade com padrões (Modo Strict)

---

## 📋 Quando Usar

- ✅ **Obrigatório** após TODA fase EXECUTE
- ✅ Antes de qualquer VALIDATE
- ✅ Antes de qualquer HALT (apresentação ao usuário)

**Sequência Obrigatória:**
```
EXECUTE → INSPECT (você está aqui) → VALIDATE → HALT
```

---

## 🔧 Como Executar a Fase INSPECT

### Entrada (Input)

- **Output da fase EXECUTE** (arquivo, dados, resultado)
- **Checklists aplicáveis:**
  - Fixo: `framework/checklists/anti_alucinacao.yaml` (obrigatório para TODOS)
  - Dinâmico: `agents/[agent_name]/checklists/inspect.yaml` (específico do agente)

### Processo

#### 1. Carregar Checklists

**Checklists Obrigatórios em Modo Strict:**

```python
def load_checklists(agent_name):
    checklists = []

    # 1. Checklist Fixo (Anti-Alucinação) - OBRIGATÓRIO
    fixed_checklist = load_yaml("framework/checklists/anti_alucinacao.yaml")
    checklists.append({
        "type": "fixed",
        "name": "Anti-Alucinação",
        "items": fixed_checklist['checklist']['items']
    })

    # 2. Checklist Dinâmico (Específico do Agente) - OBRIGATÓRIO
    dynamic_path = f"agents/{agent_name}/checklists/inspect.yaml"
    if os.path.exists(dynamic_path):
        dynamic_checklist = load_yaml(dynamic_path)
        checklists.append({
            "type": "dynamic",
            "name": dynamic_checklist['checklist']['name'],
            "items": dynamic_checklist['checklist']['items']
        })

    return checklists
```

---

#### 2. Executar Cada Item do Checklist

**Para cada item, fazer 3 perguntas:**

1. **O que verificar?** (campo `question`)
2. **Como verificar?** (campo `how_to_check`)
3. **Passou ou falhou?** (decisão binária: `true` ou `false`)

**Estrutura de um Item:**

```yaml
- id: "AA-01"
  question: "Todas as informações foram extraídas de fontes fornecidas?"
  rationale: "O agente deve operar apenas com dados fornecidos"
  how_to_check: "Verifique se cada dado no output tem uma referência clara"
  pass_criteria: "100% dos dados têm fonte identificada"
  fail_criteria: "Qualquer dado sem fonte"
  severity: "critical"
```

**Exemplo de Execução:**

```python
def execute_checklist_item(item, output_data):
    """
    Execute a single checklist item
    Returns: (passed: bool, evidence: str)
    """
    item_id = item['id']
    question = item['question']
    how_to_check = item['how_to_check']

    log_debug("INSPECT", f"Checking {item_id}: {question}")

    # Executar a verificação específica
    # (A lógica varia por item)

    if item_id == "AA-01":  # Fontes fornecidas?
        # Verificar se cada afirmação tem referência
        missing_sources = []
        for statement in output_data['statements']:
            if 'source' not in statement or not statement['source']:
                missing_sources.append(statement['text'][:50])

        if missing_sources:
            return (
                False,
                f"Encontradas {len(missing_sources)} afirmações sem fonte"
            )
        else:
            return (
                True,
                "Todas as afirmações têm fonte identificada"
            )

    # ... outros items ...
```

---

#### 3. Registrar Resultado de Cada Item

**Formato de Registro:**

```yaml
inspection_result:
  item_id: "AA-01"
  question: "Todas as informações foram extraídas de fontes fornecidas?"
  status: true  # ou false
  evidence: "Todas as 47 linhas do CSV têm campo 'fonte' preenchido"
  timestamp: "2025-11-06T16:05:00Z"
```

**Se passou (true):**
- Registrar evidência do sucesso
- Continuar para próximo item

**Se falhou (false):**
- Registrar razão da falha
- Registrar ação corretiva sugerida
- Marcar checklist como FAILED
- Preparar para LOOP

---

#### 4. Consolidar Resultados

**Após executar TODOS os itens:**

```python
def consolidate_inspection_results(fixed_results, dynamic_results):
    """
    Consolidate results from all checklists
    """
    total_items = len(fixed_results) + len(dynamic_results)
    passed_items = sum(1 for r in fixed_results + dynamic_results if r['status'])
    failed_items = total_items - passed_items

    overall_status = "PASS" if failed_items == 0 else "FAIL"

    return {
        "timestamp": datetime.now().isoformat(),
        "fixed_checklist": {
            "items_total": len(fixed_results),
            "items_passed": sum(1 for r in fixed_results if r['status']),
            "items_failed": sum(1 for r in fixed_results if not r['status'])
        },
        "dynamic_checklist": {
            "items_total": len(dynamic_results),
            "items_passed": sum(1 for r in dynamic_results if r['status']),
            "items_failed": sum(1 for r in dynamic_results if not r['status'])
        },
        "overall": {
            "items_total": total_items,
            "items_passed": passed_items,
            "items_failed": failed_items,
            "pass_rate": f"{(passed_items/total_items)*100:.1f}%",
            "overall_status": overall_status
        },
        "failed_items": [r for r in fixed_results + dynamic_results if not r['status']],
        "next_action": "LOOP" if overall_status == "FAIL" else "VALIDATE"
    }
```

---

#### 5. Decidir Próxima Ação

**Regra Simples em Modo Strict:**

```python
if overall_status == "PASS":
    # Todos os itens passaram
    next_phase = "VALIDATE"
    log_info("INSPECT", "All checklist items passed ✓")

elif overall_status == "FAIL":
    # Pelo menos 1 item falhou
    next_phase = "LOOP"
    log_warning("INSPECT", f"{failed_items} items failed. Entering LOOP...")

    # Apresentar itens falhados
    for failed in failed_items_list:
        log_error("INSPECT", f"Failed: {failed['item_id']} - {failed['reason']}")
```

**Modo Strict = "All or Nothing":**
- ✅ Todos os itens passam → VALIDATE
- ❌ 1 ou mais itens falham → LOOP

---

#### 6. Salvar Resultado da Inspeção

**Usando template:**

Localização: `data/analyses/[id]/inspection_[step_id].yaml`

```yaml
inspection:
  timestamp: "2025-11-06T16:05:00Z"
  agent: "document_structurer"
  phase: "Estruturação de CSV"
  task_id: "ANA-20251106-001"

  checklist_used:
    fixed: "framework/checklists/anti_alucinacao.yaml"
    dynamic: "agents/document_structurer/checklists/inspect.yaml"

  fixed_checklist_results:
    - item: "Todas as informações foram extraídas de fontes fornecidas?"
      status: true
      evidence: "Todas as 47 linhas têm fonte (edital.pdf)"

    - item: "Não há invenção ou suposição de dados?"
      status: true
      evidence: "Todos os requisitos copiados textualmente do PDF"

    # ... (8 itens do fixo)

  dynamic_checklist_results:
    - item: "Cada linha do CSV representa um requisito único?"
      status: true
      evidence: "Validação manual de amostra: todos únicos"

    - item: "Não há requisitos duplicados?"
      status: false
      reason: "Requisitos ID 12 e 23 têm descrições idênticas"
      corrective_action: "Remover requisito ID 23 (duplicata)"

    # ... (8 itens do dinâmico)

  summary:
    fixed_checklist:
      items_total: 8
      items_passed: 8
      items_failed: 0

    dynamic_checklist:
      items_total: 8
      items_passed: 7
      items_failed: 1

    overall:
      items_total: 16
      items_passed: 15
      items_failed: 1
      pass_rate: "93.8%"
      overall_status: "FAIL"  # 1 item falhou

  failed_items:
    - checklist: "dynamic"
      item: "Não há requisitos duplicados?"
      reason: "Requisitos ID 12 e 23 têm descrições idênticas"
      corrective_action: "Remover requisito ID 23"
      priority: "high"

  next_action: "LOOP"
  loop_iteration: 1
```

---

### Saída (Output)

1. **Resultado consolidado** (InspectionResult YAML)
2. **Decisão** (VALIDATE ou LOOP)
3. **Lista de problemas** (se houver)
4. **Ações corretivas** sugeridas

---

## ✅ Scoring: "All or Nothing"

Em **Modo Strict**, o scoring é binário:

```
PASS = 100% dos itens passaram
FAIL = < 100% (mesmo que 99.9%)
```

**Por quê tão rigoroso?**
- Qualidade > Velocidade
- Prevenir erros que causariam desqualificação
- Conformidade com NFR12 (Modo Strict obrigatório)

---

## 📊 Exemplo Completo: Inspeção de CSV Estruturado

**Contexto:** Após executar Step 5 (estruturação em CSV)

**Output a Inspecionar:**
- CSV com 47 linhas
- Colunas: ID, Descrição, Tipo, Categoria

**Checklists Aplicáveis:**
1. Fixo: Anti-Alucinação (8 itens)
2. Dinâmico: Estruturação de Documentos (8 itens)

**Execução:**

```python
# 1. Carregar checklists
checklists = load_checklists("document_structurer")

# 2. Executar checklist fixo
fixed_results = []
for item in checklists[0]['items']:
    passed, evidence = execute_checklist_item(item, csv_data)
    fixed_results.append({
        "item_id": item['id'],
        "question": item['question'],
        "status": passed,
        "evidence": evidence
    })

# 3. Executar checklist dinâmico
dynamic_results = []
for item in checklists[1]['items']:
    passed, evidence = execute_checklist_item(item, csv_data)
    dynamic_results.append({
        "item_id": item['id'],
        "question": item['question'],
        "status": passed,
        "evidence": evidence if passed else "Falhou",
        "reason": None if passed else evidence
    })

# 4. Consolidar
results = consolidate_inspection_results(fixed_results, dynamic_results)

# 5. Decidir
if results['overall']['overall_status'] == "PASS":
    log_info("INSPECT", "✓ All 16 items passed. Proceeding to VALIDATE")
    next_phase = "VALIDATE"
else:
    failed_count = results['overall']['items_failed']
    log_warning("INSPECT", f"✗ {failed_count} items failed. Entering LOOP")
    next_phase = "LOOP"

# 6. Salvar
save_yaml(f"data/analyses/{analysis_id}/inspection_step5.yaml", results)

return next_phase
```

---

## 🎓 Boas Práticas

### DO ✅

- **Execute TODOS os itens:** Não pule nenhum, mesmo após uma falha
- **Documente evidências:** Para cada PASS, explique por quê
- **Seja objetivo:** Critérios mensuráveis, não subjetivos
- **Registre tudo:** Salve resultado completo em YAML
- **Acione LOOP imediatamente:** Não continue com problemas

### DON'T ❌

- **Não "arredonde":** 99% ≠ 100%, é FAIL
- **Não pule itens:** "Provavelmente está OK" não é válido
- **Não invente evidências:** Se não verificou, marque como FAIL
- **Não ignore severidade:** Itens "critical" que falham = HALT imediato
- **Não continue após FAIL:** Sempre LOOP antes de prosseguir

---

## 🔄 Integração com Outras Fases

```
EXECUTE → INSPECT (você está aqui)
             ↓
        [Executar checklists]
             ↓
         ┌───┴───┐
    PASS│       │FAIL
         │       │
         ↓       ↓
    VALIDATE   LOOP
                 ↓
            [Corrigir]
                 ↓
            Re-EXECUTE
                 ↓
            INSPECT (novamente)
```

---

## 🛡️ Modo Strict: Garantias Obrigatórias

1. **✅ Ambos os checklists executados:** Fixo + Dinâmico
2. **✅ Todos os itens validados:** Não pular nenhum
3. **✅ Scoring All-or-Nothing:** 100% ou FAIL
4. **✅ Evidências documentadas:** Para PASS e FAIL
5. **✅ Resultado salvo:** YAML completo gerado
6. **✅ LOOP automático:** Se falhar, não continua

---

## 📚 Referências

- **Checklists:** `../checklists/` (fixo e dinâmicos)
- **Template:** `../templates/inspection_result.yaml`
- **Princípios SHIELD:** `../../OPERATING_PRINCIPLES.md`
- **Fase anterior:** `execute.md`
- **Próximas fases:** `validate.md`, `loop.md`

---

**Versão:** 1.0
**Criado em:** 06/11/2025
**Última atualização:** 06/11/2025
