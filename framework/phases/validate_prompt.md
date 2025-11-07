# VALIDATE Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes para validação quantitativa

---

## ✅ FASE VALIDATE: Seu Protocolo de Validação Quantitativa

Após INSPECT passar, você DEVE executar VALIDATE para verificar **quantitativamente** se **100% da tarefa foi completada**.

---

## 🎯 INSPECT vs VALIDATE

| INSPECT | VALIDATE |
|---------|----------|
| Qualitativo ("Está correto?") | Quantitativo ("Está completo?") |
| Checklist (true/false) | Métricas (números, %) |
| Qualidade dos itens | Completude do conjunto |
| `InspectionResult` | `ValidationResult` |

**Ambos são obrigatórios!**

---

## 📋 Protocolo de VALIDATE (5 Passos)

```
1. DEFINIR → Quais métricas validar?
2. COLETAR → Obter valores esperados e reais
3. CALCULAR → Computar métricas (%, razão, count)
4. VERIFICAR → Todas as métricas = 100%?
5. DOCUMENTAR → Gerar ValidationResult YAML
```

---

## 📊 Métricas Obrigatórias

### 1. Completude (Completeness)

**Pergunta:** Todos os itens esperados foram processados?

**Cálculo:**
```python
completeness = (items_processed / items_expected) * 100
```

**Exemplo:**
```python
# Edital tem 47 requisitos
items_expected = 47

# CSV gerado tem 47 linhas
items_processed = len(csv_data)  # 47

# Completude
completeness = (47 / 47) * 100  # 100% ✅
```

**Threshold:** 100% (Modo Strict - sem exceções)

---

### 2. Integridade (Integrity)

**Pergunta:** Todos os campos obrigatórios estão preenchidos?

**Cálculo:**
```python
integrity = (fields_filled / fields_required) * 100
```

**Exemplo:**
```python
# 47 requisitos * 6 campos obrigatórios
fields_required = 47 * 6  # 282

# Contar campos não vazios
fields_filled = 0
for row in csv_data:
    for field in ['ID', 'Descrição', 'Categoria', 'Prioridade', 'Página', 'Confiança']:
        if row[field] and row[field].strip() != "":
            fields_filled += 1

# Integridade
integrity = (fields_filled / 282) * 100  # 100% ✅
```

**Threshold:** 100%

---

### 3. Consistência (Consistency)

**Pergunta:** IDs/referências são consistentes?

**Cálculo:**
```python
consistency = (IDs estão sequenciais sem gaps?)  # True = 100%
```

**Exemplo:**
```python
# Esperado: [1, 2, 3, ..., 47]
expected_ids = list(range(1, 48))

# Real
actual_ids = [row['ID'] for row in csv_data]

# Consistente?
consistency = 100.0 if actual_ids == expected_ids else 0.0
```

**Threshold:** 100%

---

### 4. Rastreabilidade (Traceability)

**Pergunta:** Cada saída tem evidência rastreável à entrada?

**Cálculo:**
```python
traceability = (items_with_source / items_total) * 100
```

**Exemplo:**
```python
# Cada requisito deve ter campo "Página" preenchido
items_with_source = sum(1 for row in csv_data if row['Página'])

traceability = (items_with_source / 47) * 100  # 100% ✅
```

**Threshold:** 100% (Princípio Anti-Alucinação)

---

### 5. Cobertura (Coverage) - Opcional

**Pergunta:** Todas as páginas/seções foram analisadas?

**Cálculo:**
```python
coverage = (pages_analyzed / pages_total) * 100
```

**Threshold:** Depende do contexto (pode ser < 100% se algumas páginas são estruturais)

---

## 📄 Template de ValidationResult

```yaml
validation:
  id: "validation_[timestamp]_[number]"
  timestamp: "[ISO8601]"
  agent: "[agent_name]"
  task_id: "[task_id]"

  overall_status: "[PASS|FAIL]"

  metrics:
    - name: "completeness"
      description: "Todos os requisitos foram processados"
      expected: [number]
      actual: [number]
      percentage: [0-100]
      threshold: 100.0
      status: "[PASS|FAIL]"
      evidence: "[description of evidence]"

    - name: "integrity"
      description: "Todos os campos obrigatórios preenchidos"
      expected: [number]
      actual: [number]
      percentage: [0-100]
      threshold: 100.0
      status: "[PASS|FAIL]"
      evidence: "[description]"

    - name: "consistency"
      description: "IDs sequenciais sem gaps"
      expected: "[description]"
      actual: "[description]"
      percentage: [0-100]
      threshold: 100.0
      status: "[PASS|FAIL]"
      evidence: "[description]"

    - name: "traceability"
      description: "Todos os itens têm fonte rastreável"
      expected: [number]
      actual: [number]
      percentage: [0-100]
      threshold: 100.0
      status: "[PASS|FAIL]"
      evidence: "[description]"

  summary:
    metrics_total: [number]
    metrics_passed: [number]
    metrics_failed: [number]
    overall_percentage: [0-100]

  decision:
    next_phase: "[HALT|LOOP]"
    ready_for_delivery: [true|false]
    issues: []  # Or list of failed metrics

  evidence_files:
    - "[file_path_1]"
    - "[file_path_2]"
```

---

## ✅ Execução Passo a Passo

### Passo 1: DEFINIR Métricas

```python
def define_metrics(agent_name, expected_count):
    """
    Define which metrics to validate
    """
    if agent_name == "document_structurer":
        return [
            {
                "name": "completeness",
                "description": "Todos os requisitos do edital foram extraídos",
                "expected": expected_count,
                "threshold": 100.0
            },
            {
                "name": "integrity",
                "description": "Todos os campos obrigatórios preenchidos",
                "required_fields": ["ID", "Descrição", "Categoria", "Prioridade", "Página", "Confiança"],
                "threshold": 100.0
            },
            {
                "name": "consistency",
                "description": "IDs sequenciais sem gaps",
                "threshold": 100.0
            },
            {
                "name": "traceability",
                "description": "Todos os requisitos têm página de origem",
                "threshold": 100.0
            }
        ]

    # ... outros agentes
```

---

### Passo 2: COLETAR Valores

```python
def collect_values(output_data, metric_def):
    """
    Collect expected and actual values
    """
    if metric_def['name'] == "completeness":
        expected = metric_def['expected']  # Do plano
        actual = len(output_data)  # Do output

    elif metric_def['name'] == "integrity":
        required_fields = metric_def['required_fields']
        expected = len(output_data) * len(required_fields)
        actual = count_filled_fields(output_data, required_fields)

    # ... outras métricas

    return expected, actual
```

---

### Passo 3: CALCULAR Métricas

```python
def calculate_metric(metric_def, output_data):
    """
    Calculate metric percentage
    """
    expected, actual = collect_values(output_data, metric_def)

    if metric_def['name'] in ["completeness", "integrity", "traceability"]:
        percentage = (actual / expected) * 100

    elif metric_def['name'] == "consistency":
        expected_ids = list(range(1, len(output_data) + 1))
        actual_ids = [row['ID'] for row in output_data]
        percentage = 100.0 if actual_ids == expected_ids else 0.0

    return {
        "name": metric_def['name'],
        "description": metric_def['description'],
        "expected": expected,
        "actual": actual,
        "percentage": round(percentage, 2),
        "threshold": metric_def['threshold'],
        "status": "PASS" if percentage >= metric_def['threshold'] else "FAIL",
        "evidence": generate_evidence(metric_def['name'], output_data)
    }
```

---

### Passo 4: VERIFICAR Threshold

```python
def verify_all_metrics(validation_result):
    """
    Check if ALL metrics passed
    """
    all_passed = all(
        metric['status'] == "PASS"
        for metric in validation_result['metrics']
    )

    if all_passed:
        log_info("VALIDATE", "✓ All metrics passed (100%)")
        validation_result['overall_status'] = "PASS"
        validation_result['decision'] = {
            "next_phase": "HALT",
            "ready_for_delivery": True,
            "issues": []
        }
    else:
        failed = [m for m in validation_result['metrics'] if m['status'] == "FAIL"]
        log_error("VALIDATE", f"✗ {len(failed)} metric(s) failed")

        validation_result['overall_status'] = "FAIL"
        validation_result['decision'] = {
            "next_phase": "LOOP",
            "ready_for_delivery": False,
            "issues": failed
        }

    return validation_result
```

---

### Passo 5: DOCUMENTAR Resultado

```python
def save_validation_result(validation_result):
    """
    Save ValidationResult to YAML
    """
    validation_id = validation_result['id']
    file_path = f"data/state/validations/validation_{validation_id}.yaml"

    with open(file_path, 'w') as f:
        yaml.dump(validation_result, f)

    log_info("VALIDATE", f"Saved validation result: {file_path}")

    return file_path
```

---

## 🚦 Decisão Após VALIDATE

```python
if validation_result['overall_status'] == "PASS":
    # Todas as métricas = 100%
    log_info("VALIDATE", "Ready for delivery")
    return "HALT"  # Present results to user

else:
    # Alguma métrica < 100%
    log_error("VALIDATE", "Completeness/integrity issues detected")

    # Tentar corrigir via LOOP?
    if can_auto_correct(validation_result['issues']):
        return "LOOP"
    else:
        return "HALT"  # Escalar para usuário
```

---

## ⚠️ Erros Comuns a Evitar

### ❌ Confundir INSPECT com VALIDATE

```python
# ❌ ERRADO: Isso é INSPECT, não VALIDATE
validate_metric = {
    "name": "no_duplicates",
    "description": "Não há duplicatas"  # Qualidade, não completude
}
```

**VALIDATE = Quantitativo (100% processados?)**
**INSPECT = Qualitativo (Está correto?)**

---

### ❌ Aceitar < 100% em Modo Strict

```python
# ❌ ERRADO
if completeness >= 95:  # "95% é bom o suficiente"
    return "PASS"
```

**Modo Strict exige 100%. Sem exceções.**

---

### ❌ Não Documentar Evidências

```python
# ❌ ERRADO
metric_result = {
    "percentage": 100.0,
    "status": "PASS",
    # ❌ Faltou evidence!
}
```

**Sempre inclua `evidence` para auditoria.**

---

## ✅ Checklist de VALIDATE

Antes de finalizar VALIDATE, verifique:

- [ ] **Todas as 4 métricas obrigatórias calculadas?** (completeness, integrity, consistency, traceability)
- [ ] **Todas as métricas ≥ threshold?** (100% em Modo Strict)
- [ ] **Evidências documentadas?** Cada métrica tem `evidence` field
- [ ] **ValidationResult salvo?** YAML em `data/state/validations/`
- [ ] **Decisão tomada?** `next_phase` definido (HALT ou LOOP)
- [ ] **Logging completo?** Cada métrica logada (INFO ou ERROR)

**Se TODOS = ✅:** Prossiga para próxima fase

**Se ALGUM = ❌:** Corrija antes de prosseguir

---

## 🔄 Integração com Outras Fases

### Após INSPECT Passar

```python
# INSPECT passou
inspect_result = run_inspect_phase(output_data, agent_name)

if inspect_result['overall_status'] == "PASS":
    log_info("INSPECT", "✓ All checklist items passed")

    # VALIDATE obrigatório após INSPECT
    log_info("VALIDATE", "Starting quantitative validation")
    validation_result = execute_validate_phase(agent_name, task_id, output_data)

    if validation_result['overall_status'] == "PASS":
        # Tudo 100% - pronto para entregar
        return "HALT"
    else:
        # Alguma métrica falhou - corrigir
        return "LOOP"
```

---

### Se VALIDATE Falhar

```python
# VALIDATE falhou (alguma métrica < 100%)
if validation_result['overall_status'] == "FAIL":
    failed_metrics = [m for m in validation_result['metrics'] if m['status'] == "FAIL"]

    log_error("VALIDATE", f"{len(failed_metrics)} metric(s) failed")

    for metric in failed_metrics:
        log_error("VALIDATE", f"  - {metric['name']}: {metric['actual']}/{metric['expected']} ({metric['percentage']}%)")

    # Decisão: LOOP ou HALT?
    if can_auto_correct(failed_metrics):
        log_info("VALIDATE", "Attempting auto-correction via LOOP")
        return "LOOP"
    else:
        log_warning("VALIDATE", "Cannot auto-correct. Escalating to user via HALT")
        return "HALT"
```

---

## 📊 Exemplo Completo (Copy-Paste)

```python
def execute_validate_phase(agent_name, task_id, output_data):
    """
    Execute VALIDATE phase - Quantitative validation
    """
    log_info("VALIDATE", f"Starting validation for {agent_name}")

    # 1. DEFINIR métricas
    metrics_to_validate = [
        {
            "name": "completeness",
            "description": "Todos os requisitos foram processados",
            "expected": 47,  # Do plano
            "threshold": 100.0
        },
        {
            "name": "integrity",
            "description": "Todos os campos obrigatórios preenchidos",
            "required_fields": ["ID", "Descrição", "Categoria", "Prioridade", "Página", "Confiança"],
            "threshold": 100.0
        },
        {
            "name": "consistency",
            "description": "IDs sequenciais sem gaps",
            "threshold": 100.0
        },
        {
            "name": "traceability",
            "description": "Todos os requisitos têm página de origem",
            "threshold": 100.0
        }
    ]

    # 2. Inicializar resultado
    validation_result = {
        "id": f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "task_id": task_id,
        "metrics": []
    }

    # 3. CALCULAR cada métrica
    for metric_def in metrics_to_validate:
        metric_result = calculate_metric(metric_def, output_data)
        validation_result['metrics'].append(metric_result)

        if metric_result['status'] == "PASS":
            log_info("VALIDATE", f"✓ {metric_result['name']}: {metric_result['percentage']}%")
        else:
            log_error("VALIDATE", f"✗ {metric_result['name']}: {metric_result['percentage']}% (threshold: {metric_result['threshold']}%)")

    # 4. VERIFICAR tudo
    all_passed = all(m['status'] == "PASS" for m in validation_result['metrics'])

    validation_result['overall_status'] = "PASS" if all_passed else "FAIL"
    validation_result['summary'] = {
        "metrics_total": len(validation_result['metrics']),
        "metrics_passed": sum(1 for m in validation_result['metrics'] if m['status'] == "PASS"),
        "metrics_failed": sum(1 for m in validation_result['metrics'] if m['status'] == "FAIL"),
        "overall_percentage": sum(m['percentage'] for m in validation_result['metrics']) / len(validation_result['metrics'])
    }

    # 5. DOCUMENTAR
    save_validation_result(validation_result)

    # 6. DECIDIR
    if validation_result['overall_status'] == "PASS":
        log_info("VALIDATE", "✓ All metrics passed. Ready for delivery.")
        validation_result['decision'] = {
            "next_phase": "HALT",
            "ready_for_delivery": True,
            "issues": []
        }
    else:
        log_error("VALIDATE", "✗ Some metrics failed.")
        validation_result['decision'] = {
            "next_phase": "LOOP",
            "ready_for_delivery": False,
            "issues": [m for m in validation_result['metrics'] if m['status'] == "FAIL"]
        }

    return validation_result
```

---

## 🛡️ Modo Strict: Garantias

1. **✅ Completude 100%:** Todos os itens foram processados
2. **✅ Integridade 100%:** Todos os campos preenchidos
3. **✅ Consistência 100%:** IDs válidos
4. **✅ Rastreabilidade 100%:** Todas as saídas têm fonte
5. **✅ Documentação completa:** ValidationResult YAML salvo

---

**Este é um componente reutilizável. Use este prompt em todos os seus agentes.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
