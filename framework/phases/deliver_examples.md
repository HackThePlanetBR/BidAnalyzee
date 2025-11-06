# DELIVER Phase - Exemplos Práticos

**Versão:** 1.0

---

## Exemplo 1: DELIVER com Sucesso (Entrega Completa)

**Contexto:** VALIDATE passou (100%), usuário aprovou no HALT final. Executando DELIVER.

### Código de Execução

```python
def example_1_deliver_success():
    """
    DELIVER with full package and user approval
    """
    task_id = "analysis_pmsp_2025_001"

    log_info("DELIVER", f"Starting delivery for {task_id}")

    # 1. CONSOLIDAR artefatos
    log_info("DELIVER", "Step 1: Consolidating artifacts")

    artifacts = {
        "outputs": [
            "data/state/requirements_pmsp_2025_001.csv",
            "data/state/technical_analysis_pmsp_2025_001.json"
        ],
        "evidences": [
            "data/state/inspections/inspection_pmsp_2025_001.yaml",
            "data/state/validations/validation_pmsp_2025_001.yaml",
            "data/logs/execution_pmsp_2025_001.log"
        ],
        "metadata": [
            "data/state/plan_pmsp_2025_001.yaml"
        ],
        "sources": [
            "data/uploads/PMSP-Videomonitoramento-2025-001.pdf"
        ]
    }

    log_info("DELIVER", f"Consolidated {sum(len(v) for v in artifacts.values())} files")

    # 2. VERIFICAR completude
    log_info("DELIVER", "Step 2: Verifying completeness")

    missing = []
    for category, files in artifacts.items():
        for file_path in files:
            if not os.path.exists(file_path):
                missing.append(file_path)

    if missing:
        log_error("DELIVER", f"Missing files: {missing}")
        raise DeliveryIncompleteError(missing)

    log_info("DELIVER", "✓ All required files present")

    # 3. EMPACOTAR
    log_info("DELIVER", "Step 3: Packaging delivery")

    delivery_dir = f"data/deliveries/analysis_{task_id}"

    # Create structure
    os.makedirs(f"{delivery_dir}/outputs", exist_ok=True)
    os.makedirs(f"{delivery_dir}/evidences/inspection_results", exist_ok=True)
    os.makedirs(f"{delivery_dir}/evidences/validation_results", exist_ok=True)
    os.makedirs(f"{delivery_dir}/evidences/execution_logs", exist_ok=True)
    os.makedirs(f"{delivery_dir}/metadata", exist_ok=True)
    os.makedirs(f"{delivery_dir}/sources", exist_ok=True)

    # Copy files
    shutil.copy2(artifacts['outputs'][0], f"{delivery_dir}/outputs/requirements_structured.csv")
    shutil.copy2(artifacts['outputs'][1], f"{delivery_dir}/outputs/technical_analysis.json")
    shutil.copy2(artifacts['evidences'][0], f"{delivery_dir}/evidences/inspection_results/inspection_001.yaml")
    shutil.copy2(artifacts['evidences'][1], f"{delivery_dir}/evidences/validation_results/validation_001.yaml")
    shutil.copy2(artifacts['evidences'][2], f"{delivery_dir}/evidences/execution_logs/document_structurer_log.txt")
    shutil.copy2(artifacts['metadata'][0], f"{delivery_dir}/metadata/plan.yaml")
    shutil.copy2(artifacts['sources'][0], f"{delivery_dir}/sources/PMSP-Videomonitoramento-2025-001.pdf")

    log_info("DELIVER", f"✓ Packaged at: {delivery_dir}")

    # 4. DOCUMENTAR
    log_info("DELIVER", "Step 4: Generating executive summary")

    readme_content = f"""# Análise de Edital - PMSP-Videomonitoramento-2025-001

**Data:** 06/11/2025
**Agentes:** Document Structurer, Technical Analyst
**Status:** ✅ Concluído

---

## 📊 Resumo Executivo

Análise completa do edital PMSP-Videomonitoramento-2025-001.pdf (345 páginas).

### Resultados Principais

- **47 requisitos técnicos** identificados e estruturados
- **100% de completude** (todos os requisitos processados)
- **42 requisitos conformes** (89.4%)
- **5 requisitos com alertas** (10.6%)
- **0 requisitos não conformes**

### Métricas de Qualidade

| Métrica | Valor | Status |
|---------|-------|--------|
| Completeness | 100% | ✅ PASS |
| Integrity | 100% | ✅ PASS |
| Consistency | 100% | ✅ PASS |
| Traceability | 100% | ✅ PASS |

### Destaques

✅ **Pontos Fortes:**
- Sistema de câmeras especifica resolução 4K (alta qualidade)
- Protocolo ONVIF obrigatório (interoperabilidade garantida)
- Redundância de servidores especificada (alta disponibilidade)

⚠️ **Alertas:**
- Requisito #23: Prazo de entrega agressivo (90 dias - risco médio)
- Requisito #34: Especificação de armazenamento ambígua (verificar com cliente)
- Requisito #41: Multa elevada para SLA (0.5% por hora - risco financeiro)

### Arquivos Gerados

- `outputs/requirements_structured.csv` - 47 requisitos estruturados
- `outputs/technical_analysis.json` - Análise técnica completa

### Próximos Passos

1. Revisar requisitos com alertas (IDs: 23, 34, 41)
2. Validar estimativa de custos baseada nos requisitos
3. Preparar proposta técnica

---

## 🛡️ Certificação de Qualidade

Framework SHIELD v1.0 (Modo Strict)

- ✅ STRUCTURE: Plano aprovado
- ✅ EXECUTE: 5 etapas executadas sem erros
- ✅ INSPECT: 16 itens de checklist passaram (100%)
- ✅ VALIDATE: 4 métricas = 100%
- ✅ DELIVER: Entrega completa com evidências

**Rastreabilidade:** Todas as saídas têm fonte rastreável ao edital original.

---

**Entregue em:** 2025-11-06T17:30:00Z
**Workflow ID:** {task_id}
**Framework:** SHIELD v1.0 (Modo Strict)
"""

    with open(f"{delivery_dir}/README.md", 'w') as f:
        f.write(readme_content)

    log_info("DELIVER", "✓ README.md generated")

    # 5. APRESENTAR (HALT final)
    log_info("DELIVER", "Step 5: Presenting to user for final approval")

    halt_message = f"""
🛑 HALT: Aprovação Final de Entrega

📍 **Contexto:**
Análise completa. Todas as fases SHIELD concluídas (100%).

📦 **Pacote de Entrega:**
Localização: {delivery_dir}/

Conteúdo:
- outputs/ - 47 requisitos + análise técnica
- evidences/ - Inspection + Validation + Logs
- metadata/ - Plano original
- sources/ - Edital PDF
- README.md - Relatório executivo

📈 **Métricas:**
- Completeness: 100% ✅
- Integrity: 100% ✅
- Consistency: 100% ✅
- Traceability: 100% ✅

🤔 **Opções:**

**Opção A:** Aprovar entrega
→ Workflow marcado como concluído

**Opção B:** Solicitar ajustes
→ Retornar para LOOP

**Opção C:** Cancelar
→ Descartar resultado

⏸️ **Sua decisão: [A/B/C]**
    """

    # User chooses A
    user_choice = "A"
    log_info("DELIVER", f"User chose: {user_choice}")

    # 6. FINALIZAR
    log_info("DELIVER", "Step 6: Finalizing delivery")

    delivery_record = {
        "workflow_id": task_id,
        "status": "DELIVERED",
        "delivery_path": delivery_dir,
        "timestamp": "2025-11-06T17:30:00Z",
        "framework_version": "SHIELD v1.0",
        "mode": "Strict",
        "approved_by_user": True
    }

    with open(f"{delivery_dir}/delivery_record.yaml", 'w') as f:
        yaml.dump(delivery_record, f)

    log_info("DELIVER", f"✓ Delivery finalized: {delivery_dir}")
    log_info("DELIVER", f"✓ Workflow {task_id} marked as DELIVERED")

    return {
        "status": "DELIVERED",
        "delivery_path": delivery_dir,
        "timestamp": "2025-11-06T17:30:00Z"
    }
```

### Logs Gerados

```
[2025-11-06T17:25:00Z] INFO orchestrator DELIVER Starting delivery for analysis_pmsp_2025_001
[2025-11-06T17:25:00Z] INFO orchestrator DELIVER Step 1: Consolidating artifacts
[2025-11-06T17:25:01Z] INFO orchestrator DELIVER Consolidated 7 files
[2025-11-06T17:25:01Z] INFO orchestrator DELIVER Step 2: Verifying completeness
[2025-11-06T17:25:02Z] INFO orchestrator DELIVER ✓ All required files present
[2025-11-06T17:25:02Z] INFO orchestrator DELIVER Step 3: Packaging delivery
[2025-11-06T17:25:05Z] INFO orchestrator DELIVER ✓ Packaged at: data/deliveries/analysis_analysis_pmsp_2025_001
[2025-11-06T17:25:05Z] INFO orchestrator DELIVER Step 4: Generating executive summary
[2025-11-06T17:25:06Z] INFO orchestrator DELIVER ✓ README.md generated
[2025-11-06T17:25:06Z] INFO orchestrator DELIVER Step 5: Presenting to user for final approval
[2025-11-06T17:25:20Z] INFO orchestrator DELIVER User chose: A
[2025-11-06T17:25:20Z] INFO orchestrator DELIVER Step 6: Finalizing delivery
[2025-11-06T17:25:21Z] INFO orchestrator DELIVER ✓ Delivery finalized: data/deliveries/analysis_analysis_pmsp_2025_001
[2025-11-06T17:25:21Z] INFO orchestrator DELIVER ✓ Workflow analysis_pmsp_2025_001 marked as DELIVERED
```

### Estrutura Criada

```
data/deliveries/analysis_pmsp_2025_001/
├── outputs/
│   ├── requirements_structured.csv (47 requisitos)
│   └── technical_analysis.json (análise completa)
│
├── evidences/
│   ├── inspection_results/
│   │   └── inspection_001.yaml
│   ├── validation_results/
│   │   └── validation_001.yaml
│   └── execution_logs/
│       └── document_structurer_log.txt
│
├── metadata/
│   └── plan.yaml
│
├── sources/
│   └── PMSP-Videomonitoramento-2025-001.pdf
│
├── README.md (relatório executivo)
└── delivery_record.yaml (registro de entrega)
```

---

## Exemplo 2: DELIVER com Rejeição do Usuário (Ajustes Necessários)

**Contexto:** Pacote pronto, mas usuário solicita ajustes no HALT final.

### HALT Apresentado

```markdown
🛑 HALT: Aprovação Final de Entrega

[... mesmo conteúdo do Exemplo 1 ...]

⏸️ **Sua decisão: [A/B/C]**
```

### Resposta do Usuário

```
Usuário: B
Ajustes solicitados: "Incluir coluna 'Estimativa de Custo' no CSV"
```

### Código de Execução

```python
def example_2_deliver_rejection():
    """
    DELIVER rejected by user - adjustments needed
    """
    task_id = "analysis_pmsp_2025_001"

    # ... passos 1-4 (consolidar, verificar, empacotar, documentar) ...

    # 5. APRESENTAR
    halt_message = "[... HALT message ...]"

    user_choice = "B"  # Usuário solicita ajustes
    user_feedback = "Incluir coluna 'Estimativa de Custo' no CSV"

    log_warning("DELIVER", f"User rejected delivery: {user_feedback}")

    # Não finalizar! Retornar para LOOP
    return {
        "status": "REJECTED",
        "reason": user_feedback,
        "next_phase": "LOOP",
        "adjustments_requested": {
            "type": "add_column",
            "column_name": "Estimativa de Custo",
            "target_file": "requirements_structured.csv"
        }
    }


# Workflow retorna para LOOP
loop_result = execute_loop_phase(
    task_id,
    adjustment={
        "action": "add_column_to_csv",
        "column": "Estimativa de Custo",
        "default_value": "A estimar"
    }
)

# Re-executar fases
execute_phase("EXECUTE")  # Re-processar CSV
execute_phase("INSPECT")  # Re-inspecionar
execute_phase("VALIDATE")  # Re-validar

# Tentar DELIVER novamente
deliver_result_2 = execute_deliver_phase(task_id)
```

### Logs Gerados

```
[2025-11-06T17:25:20Z] INFO orchestrator DELIVER User chose: B
[2025-11-06T17:25:20Z] WARNING orchestrator DELIVER User rejected delivery: Incluir coluna 'Estimativa de Custo' no CSV
[2025-11-06T17:25:20Z] INFO orchestrator DELIVER Returning to LOOP for adjustments
[2025-11-06T17:25:21Z] INFO orchestrator LOOP Applying user feedback: add_column_to_csv
[2025-11-06T17:25:22Z] INFO orchestrator LOOP ✓ Column 'Estimativa de Custo' added to CSV
[2025-11-06T17:25:22Z] INFO orchestrator EXECUTE Re-processing CSV with new column
[... re-executa fases ...]
[2025-11-06T17:27:00Z] INFO orchestrator DELIVER Starting delivery (attempt 2)
[... delivery bem-sucedida ...]
```

---

## Exemplo 3: DELIVER com Arquivo Faltante (Erro de Verificação)

**Contexto:** Tentando entregar, mas falta um arquivo obrigatório.

### Código de Execução

```python
def example_3_deliver_missing_file():
    """
    DELIVER fails due to missing file
    """
    task_id = "analysis_pmsp_2025_001"

    # 1. CONSOLIDAR
    artifacts = {
        "outputs": [
            "data/state/requirements_pmsp_2025_001.csv",
            "data/state/technical_analysis_pmsp_2025_001.json"
        ],
        "evidences": [
            "data/state/inspections/inspection_pmsp_2025_001.yaml",
            "data/state/validations/validation_pmsp_2025_001.yaml",
            # ❌ Falta: execution log!
        ],
        # ... rest ...
    }

    # 2. VERIFICAR
    log_info("DELIVER", "Step 2: Verifying completeness")

    missing = []
    for category, files in artifacts.items():
        for file_path in files:
            if not os.path.exists(file_path):
                missing.append(file_path)

    # Verificar arquivos obrigatórios
    required_files = [
        "data/state/inspections/inspection_pmsp_2025_001.yaml",
        "data/state/validations/validation_pmsp_2025_001.yaml",
        "data/logs/execution_pmsp_2025_001.log"  # ❌ Este está faltando!
    ]

    for required_file in required_files:
        if not os.path.exists(required_file):
            missing.append(required_file)

    if missing:
        log_error("DELIVER", f"❌ Cannot deliver. Missing {len(missing)} file(s):")
        for file_path in missing:
            log_error("DELIVER", f"  - {file_path}")

        raise DeliveryIncompleteError(missing)

    # Não chega aqui!
```

### Logs Gerados

```
[2025-11-06T17:25:00Z] INFO orchestrator DELIVER Starting delivery
[2025-11-06T17:25:01Z] INFO orchestrator DELIVER Step 2: Verifying completeness
[2025-11-06T17:25:02Z] ERROR orchestrator DELIVER ❌ Cannot deliver. Missing 1 file(s):
[2025-11-06T17:25:02Z] ERROR orchestrator DELIVER   - data/logs/execution_pmsp_2025_001.log
[2025-11-06T17:25:02Z] ERROR orchestrator DELIVER Delivery aborted
```

### Ação Corretiva

```python
# Verificar por que o log não foi gerado
# Re-executar a fase que deveria ter criado o log
# Ou criar log retrospectivamente (se possível)

log_info("DELIVER", "Attempting to recover missing log")

# Se log existe em outro local, copiar
if os.path.exists("data/logs/temp_execution.log"):
    shutil.copy2(
        "data/logs/temp_execution.log",
        "data/logs/execution_pmsp_2025_001.log"
    )
    log_info("DELIVER", "✓ Log recovered from temp location")

# Re-tentar DELIVER
deliver_result = execute_deliver_phase(task_id)
```

---

## Exemplo 4: DELIVER com Múltiplos Agentes (Estrutura Complexa)

**Contexto:** Workflow usou 3 agentes (Document Structurer, Technical Analyst, Quality Assurance). DELIVER deve consolidar saídas de todos.

### Código de Execução

```python
def example_4_deliver_multiple_agents():
    """
    DELIVER with multiple agents
    """
    task_id = "analysis_pmsp_2025_001"

    # Consolidar outputs de 3 agentes
    artifacts = {
        "outputs": [
            # Agent 1: Document Structurer
            "data/state/document_structurer/requirements.csv",

            # Agent 2: Technical Analyst
            "data/state/technical_analyst/analysis.json",
            "data/state/technical_analyst/conformity_report.json",

            # Agent 3: Quality Assurance
            "data/state/quality_assurance/qa_report.json"
        ],
        "evidences": [
            # Inspection results (1 per agent)
            "data/state/inspections/inspection_document_structurer.yaml",
            "data/state/inspections/inspection_technical_analyst.yaml",
            "data/state/inspections/inspection_quality_assurance.yaml",

            # Validation results (1 per agent)
            "data/state/validations/validation_document_structurer.yaml",
            "data/state/validations/validation_technical_analyst.yaml",
            "data/state/validations/validation_quality_assurance.yaml",

            # Execution logs (1 per agent)
            "data/logs/document_structurer_log.txt",
            "data/logs/technical_analyst_log.txt",
            "data/logs/quality_assurance_log.txt"
        ],
        "metadata": [
            "data/state/plan.yaml",
            "data/state/timeline.yaml",
            "data/state/agents_used.yaml"  # Lista de agentes
        ],
        "sources": [
            "data/uploads/edital.pdf"
        ]
    }

    # Package com estrutura por agente
    delivery_dir = f"data/deliveries/analysis_{task_id}"

    os.makedirs(f"{delivery_dir}/outputs/document_structurer", exist_ok=True)
    os.makedirs(f"{delivery_dir}/outputs/technical_analyst", exist_ok=True)
    os.makedirs(f"{delivery_dir}/outputs/quality_assurance", exist_ok=True)

    # Copy outputs por agente
    shutil.copy2(
        artifacts['outputs'][0],
        f"{delivery_dir}/outputs/document_structurer/requirements.csv"
    )

    shutil.copy2(
        artifacts['outputs'][1],
        f"{delivery_dir}/outputs/technical_analyst/analysis.json"
    )

    # ... rest ...

    log_info("DELIVER", f"Packaged outputs from 3 agents")

    # README.md menciona todos os agentes
    readme_content = f"""# Análise de Edital - PMSP-2025-001

**Agentes Utilizados:**
1. **Document Structurer** - Extração de requisitos
2. **Technical Analyst** - Análise técnica e conformidade
3. **Quality Assurance** - Validação final de qualidade

**Arquivos por Agente:**
- Document Structurer: `outputs/document_structurer/requirements.csv`
- Technical Analyst: `outputs/technical_analyst/analysis.json`
- Quality Assurance: `outputs/quality_assurance/qa_report.json`

[... resto do README ...]
"""

    # ... rest of delivery ...
```

---

## Comparação dos Exemplos

| Exemplo | Situação | Resultado |
|---------|----------|-----------|
| 1 | Tudo OK, usuário aprova | ✅ DELIVERED |
| 2 | Usuário solicita ajustes | ⏮️ LOOP (ajustes) → Re-DELIVER |
| 3 | Arquivo faltante | ❌ DeliveryIncompleteError |
| 4 | Múltiplos agentes | ✅ DELIVERED (estrutura complexa) |

---

## Lições dos Exemplos

### ✅ Boas Práticas

1. **Sempre verificar completude** antes de empacotar
2. **Gerar README.md com métricas** para transparência
3. **HALT final obrigatório** para aprovação do usuário
4. **Estrutura padronizada** facilita auditoria
5. **Documentar todos os agentes** em workflows complexos

### 🔄 Padrões de Correção

**Arquivo faltante:**
```
DELIVER (fail) → Identificar causa → Re-gerar arquivo → DELIVER (retry)
```

**Usuário rejeita:**
```
DELIVER (rejected) → LOOP (ajustes) → EXECUTE → INSPECT → VALIDATE → DELIVER (retry)
```

---

**Versão:** 1.0
**Criado em:** 06/11/2025
