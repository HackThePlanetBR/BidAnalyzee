# VALIDATE Phase - Guia Teórico Completo

**Versão:** 1.0
**Tipo:** Guia de implementação
**Fase SHIELD:** L.5 - VALIDATE (Validação Quantitativa)

---

## 🎯 O Que É a Fase VALIDATE?

**VALIDATE** é a fase onde verificamos **quantitativamente** se **100% da tarefa foi completada** usando métricas objetivas.

É a validação final antes de entregar o resultado ao usuário.

### Conceito Central

```
INSPECT = Qualidade (Este item está correto?)
    ↓
VALIDATE = Completude (100% dos itens foram processados?)
    ↓
DELIVER = Entrega (Resultado completo e correto)
```

**Metáfora:** É como um checklist de pré-voo. INSPECT verifica se cada sistema funciona corretamente. VALIDATE verifica se TODOS os sistemas foram verificados (nenhum foi esquecido).

---

## 🔍 INSPECT vs VALIDATE

| Aspecto | INSPECT | VALIDATE |
|---------|---------|----------|
| **Tipo** | Qualitativo | Quantitativo |
| **Pergunta** | "Está correto?" | "Está completo?" |
| **Método** | Checklist (true/false) | Métricas (números) |
| **Foco** | Qualidade dos itens | Completude do conjunto |
| **Exemplo** | "Requisito #5 não tem duplicatas?" | "100% dos 47 requisitos foram processados?" |
| **Saída** | InspectionResult (pass/fail) | ValidationResult (métricas) |

### Exemplo Prático

**INSPECT:**
```yaml
# Verifica qualidade de cada requisito
- ED-01: "Cada linha do CSV representa um requisito único?" ✅
- ED-02: "Todas as colunas obrigatórias estão preenchidas?" ✅
- ED-03: "Não há requisitos duplicados?" ✅
```

**VALIDATE:**
```yaml
# Verifica completude do conjunto
- Total de requisitos no edital: 47
- Total de requisitos no CSV: 47
- Completude: 47/47 = 100% ✅

- Total de páginas no PDF: 345
- Páginas processadas: 345
- Completude: 345/345 = 100% ✅
```

---

## 📐 Quando Usar VALIDATE?

### Obrigatório (Modo Strict)

1. **Após INSPECT passar** - Antes de DELIVER ou HALT final
2. **Antes de qualquer entrega** - Garantir que nada foi esquecido
3. **Após correções (LOOP)** - Verificar que correção não criou gaps

### Opcional (Recomendado)

4. **Após etapas macro** - Checkpoint intermediário
5. **Em workflows longos** - Validação periódica

---

## 🛠️ Como Executar VALIDATE?

### Protocolo de 5 Passos

```
1. DEFINIR → Quais métricas validar?
2. COLETAR → Obter valores esperados e reais
3. CALCULAR → Computar métricas (%, razão, count)
4. VERIFICAR → Todas as métricas = 100%?
5. DOCUMENTAR → Gerar ValidationResult YAML
```

---

## 📊 Métricas de Validação

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

# CSV tem 47 linhas
items_processed = 47

# Completude
completeness = (47 / 47) * 100  # 100% ✅
```

**Threshold:** 100% obrigatório (Modo Strict)

---

### 2. Integridade (Integrity)

**Pergunta:** Todos os campos obrigatórios estão preenchidos?

**Cálculo:**
```python
integrity = (fields_filled / fields_required) * 100
```

**Exemplo:**
```python
# CSV tem 47 requisitos, cada um com 6 campos obrigatórios
fields_required = 47 * 6  # 282

# Contando campos preenchidos (não vazios)
fields_filled = count_non_empty_fields(csv_data)  # 282

# Integridade
integrity = (282 / 282) * 100  # 100% ✅
```

**Threshold:** 100% obrigatório

---

### 3. Cobertura (Coverage)

**Pergunta:** Todas as páginas/seções foram analisadas?

**Cálculo:**
```python
coverage = (pages_analyzed / pages_total) * 100
```

**Exemplo:**
```python
# Edital tem 345 páginas
pages_total = 345

# Páginas com ao menos 1 requisito extraído
pages_analyzed = count_unique_pages(csv_data)  # 289

# Cobertura
coverage = (289 / 345) * 100  # 83.8%
```

**Threshold:** Depende do contexto
- 100%: Se todas as páginas devem ter requisitos
- <100%: Aceitável se algumas páginas são capa, índice, etc.

**Validação adicional:**
```python
# Se cobertura < 100%, verificar páginas faltantes
missing_pages = [p for p in range(1, 346) if p not in analyzed_pages]

# Se páginas faltantes são "estruturais" (capa, índice), OK
structural_pages = [1, 2, 3, 344, 345]  # Capa, índice, contra-capa
missing_content_pages = [p for p in missing_pages if p not in structural_pages]

if len(missing_content_pages) == 0:
    coverage_valid = True  # 100% das páginas de conteúdo
else:
    coverage_valid = False  # Páginas de conteúdo foram puladas
```

---

### 4. Consistência (Consistency)

**Pergunta:** IDs/referências são consistentes?

**Cálculo:**
```python
consistency = (references_valid / references_total) * 100
```

**Exemplo:**
```python
# CSV tem IDs de 1 a 47 sequenciais
expected_ids = list(range(1, 48))  # [1, 2, ..., 47]

# IDs reais no CSV
actual_ids = [row['ID'] for row in csv_data]

# IDs estão em ordem e sem gaps?
consistency = (actual_ids == expected_ids)  # True = 100%
```

**Threshold:** 100% obrigatório

---

### 5. Rastreabilidade (Traceability)

**Pergunta:** Cada saída tem evidência rastreável à entrada?

**Cálculo:**
```python
traceability = (items_with_source / items_total) * 100
```

**Exemplo:**
```python
# 47 requisitos no CSV
items_total = 47

# Cada requisito deve ter "Página" preenchida (fonte)
items_with_source = count_rows_with_field(csv_data, 'Página')  # 47

# Rastreabilidade
traceability = (47 / 47) * 100  # 100% ✅
```

**Threshold:** 100% obrigatório (Anti-Alucinação)

---

## 📋 Anatomia de um ValidationResult

### Estrutura Completa (YAML)

```yaml
validation:
  id: "validation_20251106_170000_001"
  timestamp: "2025-11-06T17:00:00Z"
  agent: "document_structurer"
  task_id: "analysis_pmsp_2025_001"

  overall_status: "PASS"  # PASS | FAIL

  metrics:
    - name: "completeness"
      description: "Todos os requisitos do edital foram processados"
      expected: 47
      actual: 47
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "data/state/requirements.csv (47 rows)"

    - name: "integrity"
      description: "Todos os campos obrigatórios estão preenchidos"
      expected: 282  # 47 req * 6 campos
      actual: 282
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "All 6 mandatory fields filled in all 47 rows"

    - name: "coverage"
      description: "Todas as páginas de conteúdo foram analisadas"
      expected: 289  # Páginas de conteúdo (excluindo estruturais)
      actual: 289
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "Pages 4-343 analyzed (1-3, 344-345 are structural)"

    - name: "consistency"
      description: "IDs são sequenciais sem gaps"
      expected: "1-47 sequential"
      actual: "1-47 sequential"
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "IDs: [1, 2, 3, ..., 47]"

    - name: "traceability"
      description: "Todos os requisitos têm fonte rastreável"
      expected: 47
      actual: 47
      percentage: 100.0
      threshold: 100.0
      status: "PASS"
      evidence: "All rows have 'Página' field filled"

  summary:
    metrics_total: 5
    metrics_passed: 5
    metrics_failed: 0
    overall_percentage: 100.0

  decision:
    next_phase: "HALT"  # Present results to user for approval
    ready_for_delivery: true
    issues: []

  evidence_files:
    - "data/state/requirements.csv"
    - "data/state/plan_001.yaml"
    - "data/logs/extraction_log.txt"
```

---

## ✅ Critérios de Sucesso (Modo Strict)

Para VALIDATE passar em **Modo Strict**, **TODAS** as condições devem ser verdadeiras:

1. ✅ **Completude = 100%** - Todos os itens esperados foram processados
2. ✅ **Integridade = 100%** - Todos os campos obrigatórios preenchidos
3. ✅ **Consistência = 100%** - IDs/referências válidas
4. ✅ **Rastreabilidade = 100%** - Todas as saídas têm fonte
5. ✅ **Cobertura ≥ Threshold** - Páginas/seções cobertas conforme esperado

**Se QUALQUER métrica < threshold:**
```yaml
overall_status: "FAIL"
decision:
  next_phase: "LOOP"  # Or HALT for user intervention
  ready_for_delivery: false
  issues:
    - metric: "completeness"
      expected: 47
      actual: 45
      gap: 2
      corrective_action: "Identify and process missing 2 requirements"
```

---

## 🔄 Fluxo de VALIDATE

### Fluxo Normal (Tudo 100%)

```
INSPECT (PASS) → VALIDATE (100%) → HALT (apresentar resultados) → DELIVER
```

### Fluxo com Falha de Validação

```
INSPECT (PASS) → VALIDATE (95%) → LOOP (corrigir gaps) → EXECUTE (reprocessar) → INSPECT → VALIDATE
```

### Fluxo com Escala para Usuário

```
INSPECT (PASS) → VALIDATE (FAIL - gap não corrigível) → HALT (escalar problema) → User decision
```

---

## 🧪 Implementação Técnica

### Código: Executar VALIDATE

```python
def execute_validate_phase(agent_name, task_id, output_data):
    """
    Execute VALIDATE phase with quantitative metrics
    """
    log_info("VALIDATE", f"Starting validation for {agent_name} / {task_id}")

    # 1. Definir métricas
    metrics_to_validate = define_metrics(agent_name, task_id)

    # 2. Coletar valores
    validation_result = {
        "id": f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "task_id": task_id,
        "metrics": []
    }

    # 3. Calcular e verificar cada métrica
    all_passed = True

    for metric_def in metrics_to_validate:
        metric_result = calculate_metric(metric_def, output_data)

        validation_result['metrics'].append(metric_result)

        if metric_result['status'] == "FAIL":
            all_passed = False
            log_warning("VALIDATE", f"Metric {metric_def['name']} failed: {metric_result['percentage']}% (threshold: {metric_def['threshold']}%)")
        else:
            log_info("VALIDATE", f"Metric {metric_def['name']} passed: {metric_result['percentage']}%")

    # 4. Decisão geral
    validation_result['overall_status'] = "PASS" if all_passed else "FAIL"
    validation_result['summary'] = {
        "metrics_total": len(metrics_to_validate),
        "metrics_passed": sum(1 for m in validation_result['metrics'] if m['status'] == "PASS"),
        "metrics_failed": sum(1 for m in validation_result['metrics'] if m['status'] == "FAIL"),
        "overall_percentage": (sum(m['percentage'] for m in validation_result['metrics']) / len(metrics_to_validate))
    }

    # 5. Documentar
    save_validation_result(validation_result)

    # 6. Decidir próximo passo
    if validation_result['overall_status'] == "PASS":
        log_info("VALIDATE", "✓ All metrics passed. Ready for delivery.")
        validation_result['decision'] = {
            "next_phase": "HALT",
            "ready_for_delivery": True,
            "issues": []
        }
    else:
        log_error("VALIDATE", "✗ Some metrics failed. Corrective action needed.")
        validation_result['decision'] = {
            "next_phase": "LOOP",
            "ready_for_delivery": False,
            "issues": [m for m in validation_result['metrics'] if m['status'] == "FAIL"]
        }

    return validation_result


def calculate_metric(metric_def, output_data):
    """
    Calculate a single metric
    """
    name = metric_def['name']

    if name == "completeness":
        expected = metric_def['expected_value']
        actual = len(output_data)
        percentage = (actual / expected) * 100

    elif name == "integrity":
        expected = len(output_data) * metric_def['required_fields_count']
        actual = count_filled_fields(output_data, metric_def['required_fields'])
        percentage = (actual / expected) * 100

    elif name == "consistency":
        expected_ids = list(range(1, len(output_data) + 1))
        actual_ids = [row['ID'] for row in output_data]
        percentage = 100.0 if actual_ids == expected_ids else 0.0
        expected = "Sequential 1-N"
        actual = "Sequential" if actual_ids == expected_ids else "Gaps/Duplicates"

    elif name == "traceability":
        expected = len(output_data)
        actual = count_rows_with_field(output_data, 'Página')
        percentage = (actual / expected) * 100

    else:
        raise ValueError(f"Unknown metric: {name}")

    status = "PASS" if percentage >= metric_def['threshold'] else "FAIL"

    return {
        "name": name,
        "description": metric_def['description'],
        "expected": expected,
        "actual": actual,
        "percentage": round(percentage, 2),
        "threshold": metric_def['threshold'],
        "status": status,
        "evidence": generate_evidence(name, output_data)
    }
```

---

## 📊 Métricas por Tipo de Agente

### Document Structurer

```python
metrics = [
    {
        "name": "completeness",
        "description": "Todos os requisitos do edital foram extraídos",
        "expected_value": requirements_count_from_edital,
        "threshold": 100.0
    },
    {
        "name": "integrity",
        "description": "Todos os campos obrigatórios preenchidos",
        "required_fields": ["ID", "Descrição", "Categoria", "Prioridade", "Página", "Confiança"],
        "required_fields_count": 6,
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
```

### Technical Analyst

```python
metrics = [
    {
        "name": "completeness",
        "description": "Todos os requisitos foram analisados",
        "expected_value": requirements_count_from_csv,
        "threshold": 100.0
    },
    {
        "name": "integrity",
        "description": "Todos os campos de análise preenchidos",
        "required_fields": ["Análise Técnica", "Complexidade", "Riscos", "Conformidade"],
        "required_fields_count": 4,
        "threshold": 100.0
    },
    {
        "name": "confidence_threshold",
        "description": "Análises com confiança ≥ 85%",
        "threshold": 85.0  # % dos requisitos com conf ≥ 85%
    }
]
```

---

## 🚫 Erros Comuns a Evitar

### ❌ Confundir INSPECT com VALIDATE

```python
# ❌ ERRADO: Usar VALIDATE para checar qualidade
validate_metric = {
    "name": "no_duplicates",
    "description": "Não há duplicatas"  # Isso é INSPECT, não VALIDATE!
}
```

**VALIDATE é para completude, não qualidade.**

### ✅ CORRETO

```python
# ✅ INSPECT: Qualidade
inspect_item = {
    "id": "ED-03",
    "question": "Não há requisitos duplicados?"  # Qualidade
}

# ✅ VALIDATE: Completude
validate_metric = {
    "name": "completeness",
    "description": "100% dos requisitos foram processados"  # Quantitativo
}
```

---

### ❌ Aceitar < 100% em Modo Strict

```python
# ❌ ERRADO
if completeness >= 95:  # 95% é "bom o suficiente"
    return "PASS"
```

**Modo Strict exige 100%. Sem exceções.**

### ✅ CORRETO

```python
# ✅ CORRETO
if completeness == 100:
    return "PASS"
else:
    return "FAIL"  # Mesmo 99% = FAIL
```

---

## 🛡️ Modo Strict: Garantias Obrigatórias

1. **✅ Completude 100%:** Todos os itens esperados foram processados
2. **✅ Integridade 100%:** Todos os campos obrigatórios preenchidos
3. **✅ Consistência 100%:** IDs/referências válidas
4. **✅ Rastreabilidade 100%:** Todas as saídas têm fonte
5. **✅ Documentação completa:** ValidationResult YAML salvo
6. **✅ Evidências preservadas:** Arquivos de prova linkados

---

## 📚 Referências

- **Framework SHIELD completo:** `../OPERATING_PRINCIPLES.md`
- **Template YAML:** `../templates/validation_result.yaml`
- **Outras fases:** `inspect.md`, `loop.md`, `halt.md`, `deliver.md`
- **PRD:** História 1.6 (Épico 1)

---

**Versão:** 1.0
**Criado em:** 06/11/2025
**Última atualização:** 06/11/2025
