# LOOP Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes após INSPECT falhar

---

## 🎯 FASE LOOP: Seu Protocolo de Auto-Correção

Quando a inspeção (INSPECT) falhar, você DEVE entrar em LOOP para corrigir os problemas. Siga este protocolo:

### 1. ANALISAR Problemas Identificados

Você recebeu um `InspectionResult` com status `FAIL`. Carregue os itens que falharam:

```python
# Estrutura dos itens falhados:
failed_items = [
    {
        "item_id": "[ID do checklist]",
        "question": "[Pergunta que não passou]",
        "reason": "[Por que falhou]",
        "corrective_action": "[O que fazer]",
        "severity": "critical|high|medium|low"
    },
    # ... outros itens falhados
]
```

**Ações:**
- Liste TODOS os itens que falharam
- Identifique a ação corretiva sugerida para cada um
- Priorize por severidade (critical → high → medium → low)

---

### 2. PRIORIZAR Correções

**Ordem de execução:**

```
1. Critical   → Corrigir PRIMEIRO (bloqueante)
2. High       → Corrigir em seguida (importante)
3. Medium     → Corrigir depois (desejável)
4. Low        → Corrigir por último (nice-to-have)
```

**NÃO corrija em ordem aleatória.** Respeite a severidade.

---

### 3. APLICAR Correções Cirúrgicas

**Regra de Ouro:** Corrija APENAS o problema específico. NÃO refaça a etapa inteira.

#### ❌ ERRADO (Refazer Tudo):

```python
# Problema: 1 requisito duplicado
# Ação ERRADA: Reprocessar todo o PDF e refazer CSV completo

def fix_duplicate():
    text = extract_text_from_pdf(pdf_path)  # ❌ Desnecessário
    requirements = extract_all_requirements(text)  # ❌ Desnecessário
    csv_data = structure_all_requirements(requirements)  # ❌ Desnecessário
    return csv_data
```

#### ✅ CORRETO (Correção Cirúrgica):

```python
# Problema: 1 requisito duplicado (ID 23 é duplicata do ID 12)
# Ação CORRETA: Remover apenas a linha ID 23 do CSV

def fix_duplicate(csv_data, duplicate_id):
    csv_data_corrected = [
        row for row in csv_data
        if row['ID'] != duplicate_id
    ]
    log_info("LOOP", f"Removed duplicate ID {duplicate_id}")
    return csv_data_corrected
```

**Exemplos de Correções Cirúrgicas Comuns:**

```python
# 1. Remover duplicata
def remove_duplicate(csv_data, item_id):
    return [row for row in csv_data if row['ID'] != item_id]

# 2. Renumerar sequencialmente
def renumber_items(csv_data):
    for i, row in enumerate(csv_data, start=1):
        row['ID'] = i
    return csv_data

# 3. Preencher campo vazio
def fill_missing_field(csv_data, item_id, field, value):
    for row in csv_data:
        if row['ID'] == item_id:
            row[field] = value
    return csv_data

# 4. Corrigir categoria inconsistente
def fix_category(csv_data, item_id, correct_category):
    for row in csv_data:
        if row['ID'] == item_id:
            row['Categoria'] = correct_category
    return csv_data
```

---

### 4. REGISTRAR Cada Correção

**OBRIGATÓRIO:** Registre o que foi mudado:

```python
log_info("LOOP", f"=== Iteration {iteration}/{MAX_ITERATIONS} ===")

for failed_item in failed_items_sorted_by_priority:
    log_info("LOOP", f"Correcting: {failed_item['item_id']}")
    log_debug("LOOP", f"Problem: {failed_item['reason']}")
    log_debug("LOOP", f"Action: {failed_item['corrective_action']}")

    # Aplicar correção
    data = apply_correction(failed_item, data)

    log_info("LOOP", f"✓ Corrected {failed_item['item_id']}")
```

---

### 5. RE-EXECUTAR (Parcial)

**NÃO re-execute toda a etapa EXECUTE original.**

Se a correção já foi aplicada aos dados em memória:

```python
# Apenas salvar a versão corrigida
save_output(corrected_data, output_path)
log_info("LOOP", "Saved corrected output")

result = {
    "status": "SUCCESS",
    "output": corrected_data,
    "iteration": iteration
}
```

Se precisa reprocessar algo específico:

```python
# Reprocessar APENAS o necessário (não tudo)
# Ex: Se corrigiu 1 requisito, re-validar só aquele requisito
revalidate_specific_item(item_id)
```

---

### 6. RE-INSPECIONAR

**OBRIGATÓRIO:** Após corrigir, execute INSPECT novamente (completo).

```python
log_info("LOOP", f"Re-inspecting (iteration {iteration})...")

# Carregar checklists
fixed_checklist = load_yaml("framework/checklists/anti_alucinacao.yaml")
dynamic_checklist = load_yaml(f"agents/{agent_name}/checklists/inspect.yaml")

# Executar inspeção completa
inspect_result = run_inspect_phase(
    corrected_output,
    fixed_checklist,
    dynamic_checklist
)

# Decidir próximo passo
if inspect_result['overall_status'] == "PASS":
    log_info("LOOP", f"✓ Correction successful after {iteration} iteration(s)")
    return "VALIDATE"  # Sair do loop
else:
    remaining_failures = inspect_result['overall']['items_failed']
    log_warning("LOOP", f"✗ Still {remaining_failures} failures after iteration {iteration}")

    if iteration < MAX_LOOP_ITERATIONS:
        return "LOOP_AGAIN"  # Tentar novamente
    else:
        return "HALT"  # Atingiu limite
```

---

### 7. DECIDIR Próxima Ação

**Após Re-INSPECT:**

```
┌─────────────────────┐
│ Re-INSPECT resultado│
└──────────┬──────────┘
           │
      ┌────┴────┐
      │ PASSOU? │
      └────┬────┘
           │
    ┌──────┴──────┐
    │             │
  SIM ✅         NÃO ❌
    │             │
    ↓             ↓
VALIDATE    (iteração < 3?)
                  │
            ┌─────┴─────┐
            │           │
          SIM         NÃO
            │           │
            ↓           ↓
      LOOP_AGAIN      HALT
    (iteração N+1)
```

**Pseudo-código:**

```python
MAX_LOOP_ITERATIONS = int(os.getenv("MAX_LOOP_ITERATIONS", 3))

for iteration in range(1, MAX_LOOP_ITERATIONS + 1):
    # 1-5: Analisar, priorizar, corrigir, registrar, re-executar
    corrected_data = apply_all_corrections(failed_items)

    # 6: Re-inspecionar
    inspect_result = run_inspect_phase(corrected_data)

    # 7: Decidir
    if inspect_result['overall_status'] == "PASS":
        log_info("LOOP", f"✓ Success after {iteration} iteration(s)")
        return "VALIDATE"

    # Ainda há falhas
    log_warning("LOOP", f"Iteration {iteration} failed. Failures: {inspect_result['overall']['items_failed']}")

# Após MAX_ITERATIONS, ainda falhou
log_error("LOOP", f"Failed to correct after {MAX_LOOP_ITERATIONS} iterations")
return HALT_FOR_USER_INTERVENTION()
```

---

## 🛑 HALT por Limite de Iterações

Se atingir o limite de tentativas sem sucesso:

```python
def halt_after_max_iterations(inspect_result, max_iterations):
    halt_message = f"""
    ❌ Não Foi Possível Corrigir Automaticamente

    Tentativas realizadas: {max_iterations}
    Problemas restantes: {inspect_result['overall']['items_failed']}

    Detalhes dos itens que ainda falham:
    """

    for failed_item in inspect_result['failed_items']:
        halt_message += f"""
        • [{failed_item['item_id']}] {failed_item['question']}
          Problema: {failed_item['reason']}
          Ação sugerida: {failed_item['corrective_action']}
        """

    halt_message += """

    🤔 O Que Fazer Agora?

    Opção A: Você fornece correção manual
             → Carregue arquivo corrigido
             → Retomaremos a partir da inspeção

    Opção B: Marcar para revisão humana posterior
             → Documentar problema
             → Continuar com outras etapas

    Opção C: Cancelar esta análise
             → Interromper workflow

    Sua escolha [A/B/C]:
    """

    return HALT(halt_message)
```

---

## ✅ Checklist de Auto-Verificação do LOOP

Antes de sair desta fase, confirme:

- [ ] Analisei TODOS os itens que falharam (não apenas o primeiro)?
- [ ] Priorizei por severidade (critical primeiro)?
- [ ] Apliquei correções CIRÚRGICAS (não refiz tudo)?
- [ ] Registrei CADA correção aplicada em log?
- [ ] Re-executei apenas o necessário (não toda a etapa)?
- [ ] Re-inspecionei COMPLETAMENTE após correções?
- [ ] Tomei a decisão correta (VALIDATE, LOOP_AGAIN ou HALT)?
- [ ] Respeitei o limite de iterações (MAX_LOOP_ITERATIONS)?

**Se TODOS = ✅:** Prossiga conforme decisão

**Se ALGUM = ❌:** Corrija antes de prosseguir

---

## 🔄 Gerenciamento de Iterações

**Configuração via .env:**

```bash
MAX_LOOP_ITERATIONS=3  # Padrão recomendado
```

**Tracking de iteração:**

```python
# Estrutura de tracking
loop_state = {
    "current_iteration": 1,
    "max_iterations": 3,
    "corrections_applied": [],
    "history": [
        {
            "iteration": 1,
            "failures_before": 3,
            "corrections": ["Removed duplicate ID 23", "Renumbered items"],
            "failures_after": 1,
            "status": "IMPROVED_BUT_NOT_PASSED"
        },
        # ... outras iterações
    ]
}
```

---

## 🛡️ Modo Strict: Garantias Obrigatórias

1. **✅ Limite respeitado:** Nunca exceder MAX_LOOP_ITERATIONS
2. **✅ Correções cirúrgicas:** Nunca refazer etapa inteira
3. **✅ Re-inspeção obrigatória:** Após cada correção
4. **✅ Logging completo:** Cada correção documentada
5. **✅ HALT se falhar:** Não continuar workflow sem resolver

---

## ⚠️ Avisos Críticos

1. **NUNCA refaça tudo** - Apenas corrija o problema específico
2. **NUNCA pule re-inspeção** - Você pode ter criado novos problemas
3. **NUNCA ignore o limite** - Loops infinitos são perigosos
4. **NUNCA assuma sucesso** - Sempre verifique com INSPECT
5. **SEMPRE documente** - Cada correção deve estar no log

---

## 📋 Template de Execução (Copy-Paste)

```python
MAX_LOOP_ITERATIONS = int(os.getenv("MAX_LOOP_ITERATIONS", 3))

def execute_loop_phase(inspect_result, original_data, agent_name):
    """
    Execute LOOP phase with iteration limit
    """
    for iteration in range(1, MAX_LOOP_ITERATIONS + 1):
        log_info("LOOP", f"=== Iteration {iteration}/{MAX_LOOP_ITERATIONS} ===")

        # 1. Analisar problemas
        failed_items = inspect_result['failed_items']
        log_info("LOOP", f"Found {len(failed_items)} items to correct")

        # 2. Priorizar por severidade
        priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        failed_items_sorted = sorted(
            failed_items,
            key=lambda x: priority_order.get(x.get('severity', 'medium'), 3)
        )

        # 3. Aplicar correções cirúrgicas
        corrected_data = original_data.copy()
        for failed_item in failed_items_sorted:
            log_info("LOOP", f"Correcting: {failed_item['item_id']}")
            log_debug("LOOP", f"Action: {failed_item['corrective_action']}")

            corrected_data = apply_correction(failed_item, corrected_data)

            log_info("LOOP", f"✓ Applied correction for {failed_item['item_id']}")

        # 4. Re-executar (apenas salvar)
        save_output(corrected_data)
        log_info("LOOP", "Saved corrected output")

        # 5. Re-inspecionar
        log_info("LOOP", f"Re-inspecting (iteration {iteration})...")
        inspect_result = run_inspect_phase(
            corrected_data,
            agent_name
        )

        # 6. Decidir
        if inspect_result['overall_status'] == "PASS":
            log_info("LOOP", f"✓ Successfully corrected after {iteration} iteration(s)")
            return {
                "status": "SUCCESS",
                "iterations_used": iteration,
                "next_phase": "VALIDATE",
                "corrected_data": corrected_data
            }
        else:
            failures = inspect_result['overall']['items_failed']
            log_warning("LOOP", f"✗ Still {failures} failures after iteration {iteration}")

    # Atingiu limite sem sucesso
    log_error("LOOP", f"Failed to correct after {MAX_LOOP_ITERATIONS} iterations")
    return {
        "status": "FAILED",
        "iterations_used": MAX_LOOP_ITERATIONS,
        "next_phase": "HALT",
        "remaining_failures": inspect_result['failed_items']
    }


def apply_correction(failed_item, data):
    """
    Apply surgical correction based on item_id
    """
    item_id = failed_item['item_id']

    if item_id == "ED-03":  # Duplicatas
        data = remove_duplicates(data)
    elif item_id == "ED-04":  # Gaps na numeração
        data = renumber_items(data)
    elif item_id == "ED-05":  # Campo vazio
        data = fill_missing_fields(data)
    elif item_id == "AT-04":  # Confiança < 85%
        data = mark_low_confidence_items(data)
    # ... outros casos específicos

    return data
```

---

**Este é um componente reutilizável. Adapte conforme necessário para seu agente específico.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
