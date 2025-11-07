# DELIVER Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes para entrega formal

---

## 📦 FASE DELIVER: Seu Protocolo de Entrega Formal

Após VALIDATE passar e usuário aprovar no HALT final, você DEVE executar DELIVER para **entregar formalmente** o resultado completo com **todas as evidências**.

Esta é a última fase do SHIELD. Faça direito!

---

## 📋 Protocolo de DELIVER (6 Passos)

```
1. CONSOLIDAR → Reunir todos os artefatos
2. VERIFICAR → Garantir que nada está faltando
3. EMPACOTAR → Organizar em estrutura padronizada
4. DOCUMENTAR → Gerar relatório executivo
5. APRESENTAR → Mostrar ao usuário (HALT final)
6. FINALIZAR → Marcar workflow como concluído
```

---

## 📦 O Que ENTREGAR?

### 1. Artefatos de Saída (Obrigatório)

```python
outputs = [
    "requirements_structured.csv",    # Requisitos extraídos
    "technical_analysis.json",        # Análise técnica
    "conformity_report.pdf"           # Relatório (se aplicável)
]
```

### 2. Evidências de Qualidade (Obrigatório)

```python
evidences = [
    "inspection_results/inspection_001.yaml",   # INSPECT passou
    "validation_results/validation_001.yaml",   # VALIDATE = 100%
    "execution_logs/agent_log.txt"              # Logs completos
]
```

### 3. Metadados (Obrigatório)

```python
metadata = [
    "plan.yaml",                      # Plano original (STRUCTURE)
    "timeline.yaml",                  # Timestamps de cada fase
    "agents_used.yaml"                # Lista de agentes
]
```

### 4. Fontes Originais (Recomendado)

```python
sources = [
    "edital_original.pdf"             # Fonte rastreável
]
```

### 5. Relatório Executivo (Obrigatório)

```python
"README.md"  # Resumo executivo em markdown
```

---

## 📂 Estrutura de Diretório Padrão

```
data/deliveries/analysis_[task_id]/
├── outputs/                          # Artefatos de saída
│   ├── requirements_structured.csv
│   ├── technical_analysis.json
│   └── conformity_report.pdf (opcional)
│
├── evidences/                        # Evidências de qualidade
│   ├── inspection_results/
│   │   └── inspection_001.yaml
│   ├── validation_results/
│   │   └── validation_001.yaml
│   └── execution_logs/
│       └── agent_log.txt
│
├── metadata/                         # Metadados
│   ├── plan.yaml
│   ├── timeline.yaml
│   └── agents_used.yaml
│
├── sources/                          # Fontes originais
│   └── edital_original.pdf
│
└── README.md                         # Relatório executivo
```

---

## ✅ Checklist Antes de DELIVER

**TODOS os itens devem estar ✅:**

### Artefatos de Saída
- [ ] CSV estruturado gerado e salvo
- [ ] Relatório de análise gerado (se aplicável)
- [ ] Todos os arquivos de output estão em `outputs/`

### Evidências de Qualidade
- [ ] InspectionResult YAML salvo (status = PASS)
- [ ] ValidationResult YAML salvo (overall_status = PASS)
- [ ] Execution logs completos salvos

### Metadados
- [ ] Plan YAML (STRUCTURE) preservado
- [ ] Timeline com timestamps criado
- [ ] Lista de agentes documentada

### Rastreabilidade
- [ ] Todas as saídas têm fonte rastreável
- [ ] Edital original copiado para `sources/`

### Relatório Executivo
- [ ] README.md gerado com métricas principais
- [ ] Alertas e riscos documentados
- [ ] Próximos passos sugeridos

### Aprovação do Usuário
- [ ] HALT final executado
- [ ] Usuário aprovou a entrega

**Se TODOS = ✅:** Prossiga com DELIVER

**Se ALGUM = ❌:** PARE! Corrija antes de entregar.

---

## 📄 Template de README.md (Relatório Executivo)

```markdown
# Análise de Edital - [Nome do Edital]

**Data:** [DD/MM/YYYY]
**Agentes:** [Lista de agentes utilizados]
**Status:** ✅ Concluído

---

## 📊 Resumo Executivo

Análise completa do edital [Nome] ([X] páginas).

### Resultados Principais

- **[N] requisitos técnicos** identificados e estruturados
- **100% de completude** (todos os requisitos processados)
- **[N] requisitos conformes** ([X]%)
- **[N] requisitos com alertas** ([X]%)
- **[N] requisitos não conformes** ([X]%)

### Métricas de Qualidade

| Métrica | Valor | Status |
|---------|-------|--------|
| Completeness | 100% | ✅ PASS |
| Integrity | 100% | ✅ PASS |
| Consistency | 100% | ✅ PASS |
| Traceability | 100% | ✅ PASS |

### Destaques

✅ **Pontos Fortes:**
- [Ponto forte 1]
- [Ponto forte 2]

⚠️ **Alertas:**
- Requisito #[ID]: [Descrição do alerta]
- Requisito #[ID]: [Descrição do alerta]

❌ **Não Conformidades:**
- [Se houver, listar aqui]

### Arquivos Gerados

- `outputs/requirements_structured.csv` - [N] requisitos estruturados
- `outputs/technical_analysis.json` - Análise técnica completa
- `outputs/conformity_report.pdf` - Relatório de conformidade

### Próximos Passos

1. [Próximo passo 1]
2. [Próximo passo 2]
3. [Próximo passo 3]

---

## 🛡️ Certificação de Qualidade

Este resultado foi processado seguindo o **Framework SHIELD** em **Modo Strict**:

- ✅ STRUCTURE: Plano aprovado
- ✅ EXECUTE: [N] etapas executadas sem erros
- ✅ INSPECT: [N] itens de checklist passaram (100%)
- ✅ VALIDATE: [N] métricas = 100%
- ✅ DELIVER: Entrega completa com evidências

**Rastreabilidade:** Todas as saídas têm fonte rastreável ao edital original.

---

## 📂 Evidências

Todas as evidências de qualidade estão em `evidences/`:

- `inspection_results/` - Resultados de auto-inspeção
- `validation_results/` - Métricas quantitativas
- `execution_logs/` - Logs completos de execução

---

**Entregue em:** [ISO8601 Timestamp]
**Workflow ID:** [task_id]
**Framework:** SHIELD v1.0 (Modo Strict)
```

---

## 🔄 Passo a Passo de Execução

### Passo 1: CONSOLIDAR Artefatos

```python
def consolidate_artifacts(task_id):
    """
    Consolidate all files for delivery
    """
    log_info("DELIVER", "Step 1: Consolidating artifacts")

    artifacts = {
        "outputs": [
            f"data/state/requirements_{task_id}.csv",
            f"data/state/technical_analysis_{task_id}.json"
        ],
        "evidences": [
            f"data/state/inspections/inspection_{task_id}.yaml",
            f"data/state/validations/validation_{task_id}.yaml",
            f"data/logs/execution_{task_id}.log"
        ],
        "metadata": [
            f"data/state/plan_{task_id}.yaml"
        ],
        "sources": [
            f"data/uploads/edital_{task_id}.pdf"
        ]
    }

    return artifacts
```

---

### Passo 2: VERIFICAR Completude

```python
def verify_completeness(artifacts):
    """
    Verify all required files exist
    """
    log_info("DELIVER", "Step 2: Verifying completeness")

    missing = []

    for category, files in artifacts.items():
        for file_path in files:
            if not os.path.exists(file_path):
                missing.append(file_path)
                log_error("DELIVER", f"Missing file: {file_path}")

    if missing:
        log_error("DELIVER", f"❌ Delivery incomplete. Missing {len(missing)} file(s).")
        raise DeliveryIncompleteError(missing)

    log_info("DELIVER", "✓ All required files present")
    return True
```

---

### Passo 3: EMPACOTAR

```python
def package_delivery(task_id, artifacts):
    """
    Package all files into delivery directory
    """
    log_info("DELIVER", "Step 3: Packaging delivery")

    delivery_dir = f"data/deliveries/analysis_{task_id}"

    # Create directory structure
    os.makedirs(f"{delivery_dir}/outputs", exist_ok=True)
    os.makedirs(f"{delivery_dir}/evidences/inspection_results", exist_ok=True)
    os.makedirs(f"{delivery_dir}/evidences/validation_results", exist_ok=True)
    os.makedirs(f"{delivery_dir}/evidences/execution_logs", exist_ok=True)
    os.makedirs(f"{delivery_dir}/metadata", exist_ok=True)
    os.makedirs(f"{delivery_dir}/sources", exist_ok=True)

    # Copy files
    for file_path in artifacts['outputs']:
        dest = f"{delivery_dir}/outputs/{os.path.basename(file_path)}"
        shutil.copy2(file_path, dest)
        log_debug("DELIVER", f"Copied: {file_path} → {dest}")

    # ... copy other categories similarly ...

    log_info("DELIVER", f"✓ Packaged at: {delivery_dir}")
    return delivery_dir
```

---

### Passo 4: DOCUMENTAR

```python
def generate_readme(task_id, validation_result, edital_name, requirements_count):
    """
    Generate executive summary README.md
    """
    log_info("DELIVER", "Step 4: Generating executive summary")

    readme_content = f"""# Análise de Edital - {edital_name}

**Data:** {datetime.now().strftime('%d/%m/%Y')}
**Status:** ✅ Concluído

## 📊 Resumo Executivo

Análise completa com {requirements_count} requisitos técnicos.

### Métricas de Qualidade

| Métrica | Valor | Status |
|---------|-------|--------|
"""

    for metric in validation_result['metrics']:
        status_icon = "✅" if metric['status'] == "PASS" else "❌"
        readme_content += f"| {metric['name']} | {metric['percentage']}% | {status_icon} {metric['status']} |\n"

    readme_content += f"""

## 🛡️ Certificação de Qualidade

Framework SHIELD v1.0 (Modo Strict)

**Entregue em:** {datetime.now().isoformat()}
**Workflow ID:** {task_id}
"""

    return readme_content
```

---

### Passo 5: APRESENTAR (HALT Final)

```python
def present_final_halt(delivery_dir, readme_content):
    """
    Present final HALT to user for approval
    """
    log_info("DELIVER", "Step 5: Presenting to user for final approval")

    halt_message = f"""
🛑 HALT: Aprovação Final de Entrega

📍 **Contexto:**
Análise completa. Todas as fases SHIELD concluídas.

📦 **Pacote de Entrega:**
Localização: {delivery_dir}/

Conteúdo:
- outputs/ - Requisitos estruturados + análise técnica
- evidences/ - Inspection + Validation + Logs
- metadata/ - Plano + Timeline
- sources/ - Edital original
- README.md - Relatório executivo

🤔 **Opções Disponíveis:**

**Opção A:** Aprovar entrega
→ Consequência: Marcar workflow como concluído

**Opção B:** Solicitar ajustes
→ Consequência: Retornar para LOOP

**Opção C:** Cancelar entrega
→ Consequência: Descartar resultado

⏸️ **Aguardando sua decisão: [A/B/C]**
    """

    user_choice = present_halt_and_wait(halt_message, options=["A", "B", "C"])

    if user_choice == "A":
        log_info("DELIVER", "User approved delivery")
        return {"approved": True}

    elif user_choice == "B":
        adjustments = get_user_adjustments()
        log_info("DELIVER", f"User requested adjustments: {adjustments}")
        return {"approved": False, "reason": "User requested adjustments", "adjustments": adjustments}

    else:
        log_info("DELIVER", "User cancelled delivery")
        return {"approved": False, "reason": "User cancelled"}
```

---

### Passo 6: FINALIZAR

```python
def finalize_delivery(task_id, delivery_dir):
    """
    Finalize delivery and mark workflow as complete
    """
    log_info("DELIVER", "Step 6: Finalizing delivery")

    # Create delivery record
    delivery_record = {
        "workflow_id": task_id,
        "status": "DELIVERED",
        "delivery_path": delivery_dir,
        "timestamp": datetime.now().isoformat(),
        "framework_version": "SHIELD v1.0",
        "mode": "Strict"
    }

    # Save record
    record_path = f"{delivery_dir}/delivery_record.yaml"
    save_yaml(delivery_record, record_path)

    log_info("DELIVER", f"✓ Delivery finalized: {delivery_dir}")
    log_info("DELIVER", f"✓ Workflow {task_id} marked as DELIVERED")

    return delivery_record
```

---

## ⚠️ Erros Comuns a Evitar

### ❌ Entregar Sem VALIDATE Passar

```python
# ❌ ERRADO
if validation_result['overall_status'] == "FAIL":
    deliver_anyway()  # NUNCA faça isso!
```

**NUNCA entregue se VALIDATE falhou. Corrija via LOOP primeiro.**

---

### ❌ Esquecer de Copiar Evidências

```python
# ❌ ERRADO
delivery_package = {
    "outputs": [...],
    # ❌ Faltou evidences!
}
```

**Evidências são obrigatórias para auditoria.**

---

### ❌ Não Gerar README.md

```python
# ❌ ERRADO
package_delivery(task_id, artifacts)
# ❌ Esqueceu de criar README.md!
```

**README.md é obrigatório. Usuário precisa entender o resultado.**

---

### ❌ Entregar Sem Aprovação do Usuário

```python
# ❌ ERRADO
def deliver():
    package_delivery()
    finalize_delivery()
    # ❌ Não perguntou ao usuário!
```

**Sempre fazer HALT final antes de finalizar.**

---

## 🛡️ Modo Strict: Garantias

1. **✅ Todas as evidências preservadas**
2. **✅ Rastreabilidade completa**
3. **✅ Relatório executivo gerado**
4. **✅ Aprovação do usuário obtida**
5. **✅ Estrutura padronizada seguida**
6. **✅ Workflow marcado como DELIVERED**

---

## 🔗 Integração com Outras Fases

```python
# Fluxo completo
validation_result = execute_validate_phase(...)

if validation_result['overall_status'] == "PASS":
    # VALIDATE passou → HALT para apresentar resultados
    halt_response = HALT_present_results(validation_result)

    if halt_response['user_choice'] == "A":  # Usuário aprovou
        # DELIVER
        delivery_result = execute_deliver_phase(
            task_id,
            validation_result,
            user_approval=True
        )

        if delivery_result['status'] == "DELIVERED":
            log_info("DELIVER", "✓ Workflow completed successfully")
            return {"status": "SUCCESS", "delivery_path": delivery_result['delivery_path']}
```

---

## 📚 Template Copy-Paste (Completo)

```python
def execute_deliver_phase(task_id, validation_result, user_approval):
    """
    Execute DELIVER phase - Full workflow
    """
    log_info("DELIVER", f"Starting delivery for {task_id}")

    # 1. CONSOLIDAR
    artifacts = consolidate_artifacts(task_id)

    # 2. VERIFICAR
    verify_completeness(artifacts)

    # 3. EMPACOTAR
    delivery_dir = package_delivery(task_id, artifacts)

    # 4. DOCUMENTAR
    readme_content = generate_readme(task_id, validation_result)
    save_file(f"{delivery_dir}/README.md", readme_content)

    # 5. APRESENTAR
    final_halt_response = present_final_halt(delivery_dir, readme_content)

    if final_halt_response['approved']:
        # 6. FINALIZAR
        delivery_record = finalize_delivery(task_id, delivery_dir)
        log_info("DELIVER", f"✓ Delivery completed: {delivery_dir}")

        return {
            "status": "DELIVERED",
            "delivery_path": delivery_dir,
            "timestamp": datetime.now().isoformat()
        }
    else:
        log_warning("DELIVER", "User rejected delivery")
        return {
            "status": "REJECTED",
            "reason": final_halt_response['reason'],
            "next_phase": "LOOP"
        }
```

---

**Este é um componente reutilizável. Use este prompt para todas as entregas.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
