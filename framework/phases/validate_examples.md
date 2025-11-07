# VALIDATE Phase - Exemplos Práticos

**Versão:** 1.0

---

## Exemplo 1: VALIDATE com Sucesso (100% em Todas as Métricas)

**Contexto:** CSV estruturado com 47 requisitos. INSPECT passou. Executando VALIDATE.

### Entrada (Output Data)

```python
csv_data = [
    {"ID": 1, "Descrição": "Sistema de câmeras...", "Categoria": "Hardware", "Prioridade": "Alta", "Página": 23, "Confiança": 0.95},
    {"ID": 2, "Descrição": "Software de análise...", "Categoria": "Software", "Prioridade": "Alta", "Página": 25, "Confiança": 0.92},
    # ... 45 mais ...
    {"ID": 47, "Descrição": "Treinamento de operadores...", "Categoria": "Serviço", "Prioridade": "Média", "Página": 289, "Confiança": 0.88}
]
# Total: 47 requisitos
```

### Código de Execução

```python
def example_1_validate_success():
    """
    VALIDATE with all metrics passing (100%)
    """
    log_info("VALIDATE", "Starting validation for document_structurer")

    # 1. Definir métricas esperadas
    expected_requirements = 47  # Do plano STRUCTURE

    # 2. Coletar dados reais
    csv_data = load_csv("data/state/requirements.csv")
    actual_requirements = len(csv_data)

    # 3. Calcular métricas
    metrics_results = []

    # Métrica 1: Completude
    completeness = (actual_requirements / expected_requirements) * 100
    metrics_results.append({
        "name": "completeness",
        "description": "Todos os requisitos do edital foram processados",
        "expected": 47,
        "actual": 47,
        "percentage": 100.0,
        "threshold": 100.0,
        "status": "PASS",
        "evidence": f"CSV has {actual_requirements} rows, expected {expected_requirements}"
    })
    log_info("VALIDATE", f"✓ Completeness: 100%")

    # Métrica 2: Integridade
    required_fields = ["ID", "Descrição", "Categoria", "Prioridade", "Página", "Confiança"]
    fields_required = len(csv_data) * len(required_fields)  # 47 * 6 = 282
    fields_filled = 0

    for row in csv_data:
        for field in required_fields:
            if row.get(field) and str(row[field]).strip() != "":
                fields_filled += 1

    integrity = (fields_filled / fields_required) * 100

    metrics_results.append({
        "name": "integrity",
        "description": "Todos os campos obrigatórios estão preenchidos",
        "expected": 282,
        "actual": 282,
        "percentage": 100.0,
        "threshold": 100.0,
        "status": "PASS",
        "evidence": f"All {len(required_fields)} mandatory fields filled in all {len(csv_data)} rows"
    })
    log_info("VALIDATE", f"✓ Integrity: 100%")

    # Métrica 3: Consistência
    expected_ids = list(range(1, 48))
    actual_ids = [row['ID'] for row in csv_data]
    consistency = 100.0 if actual_ids == expected_ids else 0.0

    metrics_results.append({
        "name": "consistency",
        "description": "IDs são sequenciais sem gaps",
        "expected": "1-47 sequential",
        "actual": "1-47 sequential",
        "percentage": 100.0,
        "threshold": 100.0,
        "status": "PASS",
        "evidence": f"IDs: [1, 2, 3, ..., 47] (sequential, no gaps)"
    })
    log_info("VALIDATE", f"✓ Consistency: 100%")

    # Métrica 4: Rastreabilidade
    items_with_source = sum(1 for row in csv_data if row.get('Página'))
    traceability = (items_with_source / len(csv_data)) * 100

    metrics_results.append({
        "name": "traceability",
        "description": "Todos os requisitos têm página de origem",
        "expected": 47,
        "actual": 47,
        "percentage": 100.0,
        "threshold": 100.0,
        "status": "PASS",
        "evidence": f"All {len(csv_data)} rows have 'Página' field filled"
    })
    log_info("VALIDATE", f"✓ Traceability: 100%")

    # 4. Consolidar resultado
    validation_result = {
        "id": "validation_20251106_170000_001",
        "timestamp": "2025-11-06T17:00:00Z",
        "agent": "document_structurer",
        "task_id": "analysis_pmsp_2025_001",
        "overall_status": "PASS",
        "metrics": metrics_results,
        "summary": {
            "metrics_total": 4,
            "metrics_passed": 4,
            "metrics_failed": 0,
            "overall_percentage": 100.0
        },
        "decision": {
            "next_phase": "HALT",
            "ready_for_delivery": True,
            "issues": []
        },
        "evidence_files": [
            "data/state/requirements.csv",
            "data/state/plan_001.yaml",
            "data/logs/extraction_log.txt"
        ]
    }

    # 5. Salvar resultado
    save_yaml(validation_result, "data/state/validations/validation_20251106_170000_001.yaml")
    log_info("VALIDATE", "✓ All metrics passed. Ready for delivery.")

    return validation_result
```

### Logs Gerados

```
[2025-11-06T17:00:00Z] INFO document_structurer VALIDATE Starting validation for document_structurer
[2025-11-06T17:00:01Z] INFO document_structurer VALIDATE ✓ Completeness: 100%
[2025-11-06T17:00:01Z] INFO document_structurer VALIDATE ✓ Integrity: 100%
[2025-11-06T17:00:02Z] INFO document_structurer VALIDATE ✓ Consistency: 100%
[2025-11-06T17:00:02Z] INFO document_structurer VALIDATE ✓ Traceability: 100%
[2025-11-06T17:00:02Z] INFO document_structurer VALIDATE ✓ All metrics passed. Ready for delivery.
```

### Resultado (YAML)

```yaml
validation:
  id: "validation_20251106_170000_001"
  timestamp: "2025-11-06T17:00:00Z"
  agent: "document_structurer"
  task_id: "analysis_pmsp_2025_001"
  overall_status: "PASS"

  metrics:
    - name: "completeness"
      description: "Todos os requisitos do edital foram processados"
      expected: 47
      actual: 47
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "CSV has 47 rows, expected 47"

    - name: "integrity"
      description: "Todos os campos obrigatórios estão preenchidos"
      expected: 282
      actual: 282
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "All 6 mandatory fields filled in all 47 rows"

    - name: "consistency"
      description: "IDs são sequenciais sem gaps"
      expected: "1-47 sequential"
      actual: "1-47 sequential"
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "IDs: [1, 2, 3, ..., 47] (sequential, no gaps)"

    - name: "traceability"
      description: "Todos os requisitos têm página de origem"
      expected: 47
      actual: 47
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "All 47 rows have 'Página' field filled"

  summary:
    metrics_total: 4
    metrics_passed: 4
    metrics_failed: 0
    overall_percentage: 100.0

  decision:
    next_phase: "HALT"
    ready_for_delivery: true
    issues: []

  evidence_files:
    - "data/state/requirements.csv"
    - "data/state/plan_001.yaml"
    - "data/logs/extraction_log.txt"
```

### Próximo Passo

```python
# VALIDATE passou → HALT para apresentar resultados ao usuário
next_phase = validation_result['decision']['next_phase']  # "HALT"

return HALT_for_approval(validation_result)
```

---

## Exemplo 2: VALIDATE com Falha de Completude (95%)

**Contexto:** CSV tem apenas 45 dos 47 requisitos esperados. 2 requisitos faltando.

### Entrada (Output Data)

```python
csv_data = [
    {"ID": 1, "Descrição": "Sistema de câmeras...", ...},
    # ... 43 mais ...
    {"ID": 45, "Descrição": "Suporte técnico...", ...}
]
# Total: 45 requisitos (faltam 2!)
```

### Código de Execução

```python
def example_2_validate_fail_completeness():
    """
    VALIDATE fails due to completeness < 100%
    """
    log_info("VALIDATE", "Starting validation")

    expected_requirements = 47
    csv_data = load_csv("data/state/requirements.csv")
    actual_requirements = len(csv_data)  # 45

    # Métrica 1: Completude
    completeness = (actual_requirements / expected_requirements) * 100  # 95.74%

    completeness_result = {
        "name": "completeness",
        "description": "Todos os requisitos do edital foram processados",
        "expected": 47,
        "actual": 45,
        "percentage": 95.74,
        "threshold": 100.0,
        "status": "FAIL",  # ❌
        "evidence": f"CSV has {actual_requirements} rows, expected {expected_requirements}. Missing 2 requirements."
    }
    log_error("VALIDATE", f"✗ Completeness: 95.74% (threshold: 100%)")

    # ... outras métricas (assumindo que todas passaram)
    integrity_result = {"name": "integrity", "status": "PASS", "percentage": 100.0, ...}
    consistency_result = {"name": "consistency", "status": "PASS", "percentage": 100.0, ...}
    traceability_result = {"name": "traceability", "status": "PASS", "percentage": 100.0, ...}

    # Consolidar
    validation_result = {
        "id": "validation_20251106_170100_002",
        "timestamp": "2025-11-06T17:01:00Z",
        "agent": "document_structurer",
        "task_id": "analysis_pmsp_2025_001",
        "overall_status": "FAIL",  # ❌ Uma métrica falhou
        "metrics": [completeness_result, integrity_result, consistency_result, traceability_result],
        "summary": {
            "metrics_total": 4,
            "metrics_passed": 3,
            "metrics_failed": 1,
            "overall_percentage": 98.935  # (95.74 + 100 + 100 + 100) / 4
        },
        "decision": {
            "next_phase": "LOOP",  # Tentar corrigir
            "ready_for_delivery": False,
            "issues": [completeness_result]
        }
    }

    save_yaml(validation_result, "data/state/validations/validation_20251106_170100_002.yaml")
    log_error("VALIDATE", "✗ Validation failed. Missing 2 requirements. Entering LOOP.")

    return validation_result
```

### Logs Gerados

```
[2025-11-06T17:01:00Z] INFO document_structurer VALIDATE Starting validation
[2025-11-06T17:01:01Z] ERROR document_structurer VALIDATE ✗ Completeness: 95.74% (threshold: 100%)
[2025-11-06T17:01:01Z] INFO document_structurer VALIDATE ✓ Integrity: 100%
[2025-11-06T17:01:02Z] INFO document_structurer VALIDATE ✓ Consistency: 100%
[2025-11-06T17:01:02Z] INFO document_structurer VALIDATE ✓ Traceability: 100%
[2025-11-06T17:01:02Z] ERROR document_structurer VALIDATE ✗ Validation failed. Missing 2 requirements. Entering LOOP.
```

### Ação Corretiva (LOOP)

```python
# VALIDATE falhou → LOOP para corrigir
if validation_result['overall_status'] == "FAIL":
    failed_metric = validation_result['decision']['issues'][0]

    log_info("LOOP", f"Correcting issue: {failed_metric['name']}")

    # Identificar quais requisitos estão faltando
    all_pages = set(range(1, 346))  # Páginas 1-345
    analyzed_pages = set(row['Página'] for row in csv_data)
    missing_pages = all_pages - analyzed_pages

    log_info("LOOP", f"Missing pages: {missing_pages}")

    # Re-extrair requisitos das páginas faltantes
    for page in missing_pages:
        log_info("LOOP", f"Re-extracting from page {page}")
        new_requirements = extract_requirements_from_page(pdf_path, page)
        csv_data.extend(new_requirements)

    # Re-validar
    validation_result_2 = execute_validate_phase("document_structurer", task_id, csv_data)

    if validation_result_2['overall_status'] == "PASS":
        log_info("LOOP", "✓ Issue corrected. Completeness now 100%")
```

---

## Exemplo 3: VALIDATE com Falha de Integridade (Campos Vazios)

**Contexto:** CSV tem 47 requisitos, mas 3 deles têm o campo "Categoria" vazio.

### Entrada (Output Data)

```python
csv_data = [
    {"ID": 1, "Descrição": "Sistema...", "Categoria": "Hardware", "Prioridade": "Alta", "Página": 23, "Confiança": 0.95},
    {"ID": 2, "Descrição": "Software...", "Categoria": "", "Prioridade": "Alta", "Página": 25, "Confiança": 0.92},  # ❌ Vazio
    {"ID": 3, "Descrição": "Rede...", "Categoria": "", "Prioridade": "Média", "Página": 27, "Confiança": 0.89},  # ❌ Vazio
    # ... 42 mais ...
    {"ID": 46, "Descrição": "Manutenção...", "Categoria": "", "Prioridade": "Baixa", "Página": 287, "Confiança": 0.86},  # ❌ Vazio
    {"ID": 47, "Descrição": "Treinamento...", "Categoria": "Serviço", "Prioridade": "Média", "Página": 289, "Confiança": 0.88}
]
# Total: 47 requisitos, mas 3 com campo "Categoria" vazio
```

### Código de Execução

```python
def example_3_validate_fail_integrity():
    """
    VALIDATE fails due to integrity < 100% (empty fields)
    """
    log_info("VALIDATE", "Starting validation")

    csv_data = load_csv("data/state/requirements.csv")
    required_fields = ["ID", "Descrição", "Categoria", "Prioridade", "Página", "Confiança"]

    # Métrica 2: Integridade
    fields_required = len(csv_data) * len(required_fields)  # 47 * 6 = 282
    fields_filled = 0
    empty_fields_list = []

    for row in csv_data:
        for field in required_fields:
            value = row.get(field)
            if value and str(value).strip() != "":
                fields_filled += 1
            else:
                empty_fields_list.append({
                    "ID": row['ID'],
                    "field": field
                })

    integrity = (fields_filled / fields_required) * 100  # 279/282 = 98.94%

    integrity_result = {
        "name": "integrity",
        "description": "Todos os campos obrigatórios estão preenchidos",
        "expected": 282,
        "actual": 279,
        "percentage": 98.94,
        "threshold": 100.0,
        "status": "FAIL",  # ❌
        "evidence": f"3 fields are empty: {empty_fields_list}"
    }
    log_error("VALIDATE", f"✗ Integrity: 98.94% (threshold: 100%)")
    log_error("VALIDATE", f"Empty fields: {empty_fields_list}")

    # ... outras métricas (assumindo que todas passaram)

    validation_result = {
        "overall_status": "FAIL",
        "decision": {
            "next_phase": "LOOP",
            "ready_for_delivery": False,
            "issues": [integrity_result]
        }
    }

    return validation_result
```

### Logs Gerados

```
[2025-11-06T17:05:00Z] INFO document_structurer VALIDATE Starting validation
[2025-11-06T17:05:01Z] INFO document_structurer VALIDATE ✓ Completeness: 100%
[2025-11-06T17:05:01Z] ERROR document_structurer VALIDATE ✗ Integrity: 98.94% (threshold: 100%)
[2025-11-06T17:05:01Z] ERROR document_structurer VALIDATE Empty fields: [{'ID': 2, 'field': 'Categoria'}, {'ID': 3, 'field': 'Categoria'}, {'ID': 46, 'field': 'Categoria'}]
```

### Ação Corretiva (LOOP)

```python
# LOOP para preencher campos vazios
empty_fields = [{"ID": 2, "field": "Categoria"}, {"ID": 3, "field": "Categoria"}, {"ID": 46, "field": "Categoria"}]

for empty_field in empty_fields:
    row_id = empty_field['ID']
    field_name = empty_field['field']

    log_info("LOOP", f"Filling empty field: ID {row_id}, field '{field_name}'")

    # Re-analisar requisito para inferir categoria
    row = next(r for r in csv_data if r['ID'] == row_id)
    inferred_category = infer_category_from_description(row['Descrição'])

    row[field_name] = inferred_category
    log_info("LOOP", f"✓ ID {row_id}, '{field_name}' filled with: {inferred_category}")

# Re-validar
validation_result_2 = execute_validate_phase("document_structurer", task_id, csv_data)
```

---

## Exemplo 4: VALIDATE com Falha de Consistência (IDs com Gaps)

**Contexto:** IDs não são sequenciais: [1, 2, 3, 5, 6, ...] (falta ID 4)

### Entrada

```python
csv_data = [
    {"ID": 1, ...},
    {"ID": 2, ...},
    {"ID": 3, ...},
    # ID 4 está faltando! ❌
    {"ID": 5, ...},
    {"ID": 6, ...},
    # ... até ...
    {"ID": 48, ...}
]
# Total: 47 requisitos, mas IDs com gap (falta 4)
```

### Código

```python
def example_4_validate_fail_consistency():
    """
    VALIDATE fails due to consistency (ID gaps)
    """
    csv_data = load_csv("data/state/requirements.csv")

    expected_ids = list(range(1, 48))  # [1, 2, ..., 47]
    actual_ids = [row['ID'] for row in csv_data]  # [1, 2, 3, 5, 6, ..., 48]

    # Gaps?
    consistency = 100.0 if actual_ids == expected_ids else 0.0  # 0.0 (tem gap)

    # Identificar gaps
    missing_ids = set(expected_ids) - set(actual_ids)  # {4}
    extra_ids = set(actual_ids) - set(expected_ids)  # {48}

    consistency_result = {
        "name": "consistency",
        "description": "IDs são sequenciais sem gaps",
        "expected": "1-47 sequential",
        "actual": f"1-48 with gaps (missing: {missing_ids}, extra: {extra_ids})",
        "percentage": 0.0,
        "threshold": 100.0,
        "status": "FAIL",
        "evidence": f"IDs: {actual_ids[:10]}... (47 items, but not sequential)"
    }

    log_error("VALIDATE", "✗ Consistency: 0% (IDs have gaps)")

    return {"overall_status": "FAIL", "decision": {"next_phase": "LOOP", "issues": [consistency_result]}}
```

### Ação Corretiva (LOOP)

```python
# LOOP para renumerar IDs
log_info("LOOP", "Renumbering IDs to fix gaps")

for i, row in enumerate(csv_data, start=1):
    old_id = row['ID']
    row['ID'] = i
    if old_id != i:
        log_debug("LOOP", f"Renumbered: {old_id} → {i}")

log_info("LOOP", "✓ All IDs renumbered sequentially")

# Re-validar
validation_result_2 = execute_validate_phase("document_structurer", task_id, csv_data)
```

---

## Comparação dos Exemplos

| Exemplo | Métrica Falha | Percentual | Ação Corretiva |
|---------|---------------|------------|----------------|
| 1 | Nenhuma | 100% | HALT (apresentar resultados) |
| 2 | Completude | 95.74% | LOOP (re-extrair 2 requisitos faltantes) |
| 3 | Integridade | 98.94% | LOOP (preencher 3 campos vazios) |
| 4 | Consistência | 0% | LOOP (renumerar IDs) |

---

## Lições dos Exemplos

### ✅ Quando VALIDATE Passa

- **Todas as métricas = 100%**
- **Decisão:** `next_phase = "HALT"`, `ready_for_delivery = true`
- **Próximo passo:** Apresentar resultados ao usuário para aprovação

### ❌ Quando VALIDATE Falha

- **Qualquer métrica < threshold**
- **Decisão:** `next_phase = "LOOP"` (se corrigível) ou `"HALT"` (se não corrigível)
- **Próximo passo:** Corrigir via LOOP ou escalar para usuário

### 📐 Padrão de Correção

```
VALIDATE (FAIL) → LOOP (corrigir) → EXECUTE (re-processar) → VALIDATE (re-validar)
```

---

**Versão:** 1.0
**Criado em:** 06/11/2025
