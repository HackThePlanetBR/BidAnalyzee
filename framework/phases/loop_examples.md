# LOOP Phase - Exemplos Práticos

**Versão:** 1.0

---

## Exemplo 1: Correção Simples (1 Iteração)

**Contexto:** CSV estruturado com 1 requisito duplicado

**Inspect Result (Entrada):**

```yaml
inspection:
  overall_status: "FAIL"
  overall:
    items_total: 16
    items_passed: 15
    items_failed: 1

  failed_items:
    - item_id: "ED-03"
      question: "Não há requisitos duplicados?"
      reason: "Requisitos ID 12 e ID 23 têm descrições idênticas"
      corrective_action: "Remover requisito ID 23 (duplicata)"
      severity: "high"
```

### Código de Execução

```python
def execute_loop_iteration_1(csv_data, inspect_result):
    """
    LOOP Iteration 1: Remove duplicate requirement
    """
    log_info("LOOP", "=== Iteration 1/3 ===")

    # 1. Analisar problema
    failed_item = inspect_result['failed_items'][0]
    log_info("LOOP", f"Correcting: {failed_item['item_id']}")
    log_debug("LOOP", f"Problem: {failed_item['reason']}")
    log_debug("LOOP", f"Action: {failed_item['corrective_action']}")

    # 2. Aplicar correção cirúrgica
    csv_data_before = len(csv_data)
    csv_data_corrected = [row for row in csv_data if row['ID'] != 23]
    csv_data_after = len(csv_data_corrected)

    log_info("LOOP", f"Removed 1 duplicate (ID 23)")
    log_debug("LOOP", f"Rows: {csv_data_before} → {csv_data_after}")

    # 3. Re-executar (salvar)
    save_csv(csv_data_corrected, "requirements_corrected.csv")
    log_info("LOOP", "Saved corrected CSV")

    # 4. Re-inspecionar
    log_info("LOOP", "Re-inspecting...")
    inspect_result_2 = run_inspect_phase(csv_data_corrected, "document_structurer")

    # 5. Resultado
    if inspect_result_2['overall_status'] == "PASS":
        log_info("LOOP", "✓ Correction successful after 1 iteration")
        return {
            "status": "SUCCESS",
            "iterations_used": 1,
            "next_phase": "VALIDATE",
            "corrected_data": csv_data_corrected
        }
```

### Logs Gerados

```
[2025-11-06T16:05:00Z] INFO document_structurer LOOP === Iteration 1/3 ===
[2025-11-06T16:05:00Z] INFO document_structurer LOOP Correcting: ED-03
[2025-11-06T16:05:00Z] DEBUG document_structurer LOOP Problem: Requisitos ID 12 e ID 23 têm descrições idênticas
[2025-11-06T16:05:00Z] DEBUG document_structurer LOOP Action: Remover requisito ID 23 (duplicata)
[2025-11-06T16:05:01Z] INFO document_structurer LOOP Removed 1 duplicate (ID 23)
[2025-11-06T16:05:01Z] DEBUG document_structurer LOOP Rows: 47 → 46
[2025-11-06T16:05:01Z] INFO document_structurer LOOP Saved corrected CSV
[2025-11-06T16:05:01Z] INFO document_structurer LOOP Re-inspecting...
[2025-11-06T16:05:02Z] INFO document_structurer INSPECT Executing fixed checklist
[2025-11-06T16:05:03Z] INFO document_structurer INSPECT Executing dynamic checklist
[2025-11-06T16:05:04Z] INFO document_structurer INSPECT ✓ All 16 items passed
[2025-11-06T16:05:04Z] INFO document_structurer LOOP ✓ Correction successful after 1 iteration
```

### Resultado

```yaml
loop_result:
  status: "SUCCESS"
  iterations_used: 1
  next_phase: "VALIDATE"
  corrections_applied:
    - iteration: 1
      item_id: "ED-03"
      action: "Removed duplicate ID 23"
      result: "SUCCESS"
```

---

## Exemplo 2: Correção Múltipla (2 Iterações)

**Contexto:** CSV com duplicata + gap na numeração

**Inspect Result (Entrada - Iteração 1):**

```yaml
inspection:
  overall_status: "FAIL"
  overall:
    items_total: 16
    items_passed: 14
    items_failed: 2

  failed_items:
    - item_id: "ED-03"
      question: "Não há requisitos duplicados?"
      reason: "Requisitos ID 12 e ID 23 têm descrições idênticas"
      corrective_action: "Remover requisito ID 23"
      severity: "high"

    - item_id: "ED-04"
      question: "Numeração sequencial sem gaps?"
      reason: "Após remover ID 23, haverá gap: 22 → 24"
      corrective_action: "Renumerar todos os IDs sequencialmente"
      severity: "medium"
```

### Código de Execução

```python
def execute_loop_multiple_iterations(csv_data, inspect_result):
    """
    LOOP with multiple iterations
    """
    MAX_ITERATIONS = 3
    corrected_data = csv_data.copy()

    for iteration in range(1, MAX_ITERATIONS + 1):
        log_info("LOOP", f"=== Iteration {iteration}/3 ===")

        failed_items = inspect_result['failed_items']
        log_info("LOOP", f"Found {len(failed_items)} items to correct")

        # Priorizar por severidade
        priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        failed_items_sorted = sorted(
            failed_items,
            key=lambda x: priority_order.get(x.get('severity', 'medium'), 3)
        )

        # Aplicar correções
        for failed_item in failed_items_sorted:
            log_info("LOOP", f"Correcting: {failed_item['item_id']}")

            if failed_item['item_id'] == "ED-03":
                # Remover duplicata
                corrected_data = [row for row in corrected_data if row['ID'] != 23]
                log_info("LOOP", "✓ Removed duplicate ID 23")

            elif failed_item['item_id'] == "ED-04":
                # Renumerar
                for i, row in enumerate(corrected_data, start=1):
                    if row['ID'] != i:
                        log_debug("LOOP", f"Renumbering: {row['ID']} → {i}")
                        row['ID'] = i
                log_info("LOOP", "✓ Renumbered all items sequentially")

        # Re-executar
        save_csv(corrected_data, "requirements_corrected.csv")
        log_info("LOOP", "Saved corrected CSV")

        # Re-inspecionar
        log_info("LOOP", f"Re-inspecting (iteration {iteration})...")
        inspect_result = run_inspect_phase(corrected_data, "document_structurer")

        # Decidir
        if inspect_result['overall_status'] == "PASS":
            log_info("LOOP", f"✓ Correction successful after {iteration} iteration(s)")
            return {
                "status": "SUCCESS",
                "iterations_used": iteration,
                "next_phase": "VALIDATE",
                "corrected_data": corrected_data
            }
        else:
            failures = inspect_result['overall']['items_failed']
            log_warning("LOOP", f"✗ Still {failures} failures after iteration {iteration}")

    # Não deveria chegar aqui neste exemplo, mas...
    log_error("LOOP", "Failed to correct after 3 iterations")
    return {"status": "FAILED", "next_phase": "HALT"}
```

### Logs Gerados

```
[2025-11-06T16:10:00Z] INFO document_structurer LOOP === Iteration 1/3 ===
[2025-11-06T16:10:00Z] INFO document_structurer LOOP Found 2 items to correct
[2025-11-06T16:10:00Z] INFO document_structurer LOOP Correcting: ED-03
[2025-11-06T16:10:01Z] INFO document_structurer LOOP ✓ Removed duplicate ID 23
[2025-11-06T16:10:01Z] INFO document_structurer LOOP Correcting: ED-04
[2025-11-06T16:10:02Z] DEBUG document_structurer LOOP Renumbering: 24 → 23
[2025-11-06T16:10:02Z] DEBUG document_structurer LOOP Renumbering: 25 → 24
[... 22 more renumbering logs ...]
[2025-11-06T16:10:03Z] INFO document_structurer LOOP ✓ Renumbered all items sequentially
[2025-11-06T16:10:03Z] INFO document_structurer LOOP Saved corrected CSV
[2025-11-06T16:10:03Z] INFO document_structurer LOOP Re-inspecting (iteration 1)...
[2025-11-06T16:10:05Z] INFO document_structurer INSPECT ✓ All 16 items passed
[2025-11-06T16:10:05Z] INFO document_structurer LOOP ✓ Correction successful after 1 iteration
```

**Observação:** Neste caso, ambas correções foram aplicadas na iteração 1, então passou na primeira re-inspeção.

### Resultado

```yaml
loop_result:
  status: "SUCCESS"
  iterations_used: 1
  next_phase: "VALIDATE"
  corrections_applied:
    - iteration: 1
      corrections:
        - item_id: "ED-03"
          action: "Removed duplicate ID 23"
        - item_id: "ED-04"
          action: "Renumbered 22 items"
      result: "SUCCESS"
```

---

## Exemplo 3: Limite de Iterações Atingido (HALT)

**Contexto:** Problema complexo que não pode ser resolvido automaticamente

**Inspect Result (Entrada - Iteração 1):**

```yaml
inspection:
  overall_status: "FAIL"
  failed_items:
    - item_id: "AT-07"
      question: "Especificações técnicas são consistentes entre si?"
      reason: "Requisito #12 especifica 'câmeras 4K', mas requisito #34 especifica 'gravação 1080p máximo' - Incompatível"
      corrective_action: "Requer decisão humana: qual especificação é correta?"
      severity: "critical"
```

### Código de Execução

```python
def execute_loop_with_halt(csv_data, inspect_result):
    """
    LOOP that reaches max iterations and HALTs
    """
    MAX_ITERATIONS = 3
    corrected_data = csv_data.copy()

    for iteration in range(1, MAX_ITERATIONS + 1):
        log_info("LOOP", f"=== Iteration {iteration}/3 ===")

        failed_item = inspect_result['failed_items'][0]
        log_info("LOOP", f"Analyzing: {failed_item['item_id']}")
        log_warning("LOOP", f"Problem: {failed_item['reason']}")

        # Tentativa de correção automática
        if failed_item['item_id'] == "AT-07":
            # Problema: Inconsistência entre 2 requisitos
            # Não há como decidir qual está correto sem input humano

            log_warning("LOOP", "Cannot auto-correct: Requires human decision")
            log_info("LOOP", f"Attempted iteration {iteration}, no automatic fix available")

            # Re-inspecionar (vai continuar falhando)
            inspect_result = run_inspect_phase(corrected_data, "technical_analyst")

            if inspect_result['overall_status'] == "FAIL":
                log_warning("LOOP", f"✗ Still failed after iteration {iteration}")

                if iteration >= MAX_ITERATIONS:
                    # Atingiu limite
                    log_error("LOOP", f"Max iterations ({MAX_ITERATIONS}) reached")
                    log_error("LOOP", "Escalating to user via HALT")

                    return halt_after_max_iterations(inspect_result, MAX_ITERATIONS)

    # Nunca deveria chegar aqui (return dentro do loop)


def halt_after_max_iterations(inspect_result, max_iterations):
    """
    HALT for user intervention after max iterations
    """
    failed_item = inspect_result['failed_items'][0]

    halt_message = f"""
    ❌ Não Foi Possível Corrigir Automaticamente

    Tentativas realizadas: {max_iterations}
    Problemas restantes: {len(inspect_result['failed_items'])}

    Detalhes do problema:

    [{failed_item['item_id']}] {failed_item['question']}

    Problema detectado:
    {failed_item['reason']}

    Por que não posso corrigir automaticamente:
    Este problema envolve uma inconsistência técnica que requer conhecimento
    do domínio para decidir qual especificação é a correta. Não posso assumir
    ou "adivinhar" a resposta correta (Princípio Anti-Alucinação).

    🤔 O Que Fazer Agora?

    Opção A: Você fornece a correção
             → Qual especificação está correta?
               1. Câmeras 4K (requisito #12)
               2. Gravação 1080p (requisito #34)
               3. Ambos estão errados (você fornecerá o correto)

    Opção B: Marcar para revisão posterior
             → Documentar inconsistência
             → Continuar análise (marcar requisitos como "PENDING_REVIEW")

    Opção C: Cancelar análise
             → Interromper workflow

    Sua escolha [A/B/C]:
    """

    log_info("LOOP", "Presenting HALT to user")

    return {
        "status": "HALTED",
        "iterations_used": max_iterations,
        "next_phase": "HALT",
        "halt_type": "MAX_ITERATIONS_REACHED",
        "halt_message": halt_message,
        "remaining_failures": inspect_result['failed_items']
    }
```

### Logs Gerados

```
[2025-11-06T16:15:00Z] INFO technical_analyst LOOP === Iteration 1/3 ===
[2025-11-06T16:15:00Z] INFO technical_analyst LOOP Analyzing: AT-07
[2025-11-06T16:15:00Z] WARNING technical_analyst LOOP Problem: Requisito #12 especifica 'câmeras 4K', mas requisito #34 especifica 'gravação 1080p máximo' - Incompatível
[2025-11-06T16:15:01Z] WARNING technical_analyst LOOP Cannot auto-correct: Requires human decision
[2025-11-06T16:15:01Z] INFO technical_analyst LOOP Attempted iteration 1, no automatic fix available
[2025-11-06T16:15:01Z] INFO technical_analyst LOOP Re-inspecting (iteration 1)...
[2025-11-06T16:15:03Z] WARNING technical_analyst LOOP ✗ Still failed after iteration 1

[2025-11-06T16:15:03Z] INFO technical_analyst LOOP === Iteration 2/3 ===
[... same process ...]
[2025-11-06T16:15:06Z] WARNING technical_analyst LOOP ✗ Still failed after iteration 2

[2025-11-06T16:15:06Z] INFO technical_analyst LOOP === Iteration 3/3 ===
[... same process ...]
[2025-11-06T16:15:09Z] WARNING technical_analyst LOOP ✗ Still failed after iteration 3
[2025-11-06T16:15:09Z] ERROR technical_analyst LOOP Max iterations (3) reached
[2025-11-06T16:15:09Z] ERROR technical_analyst LOOP Escalating to user via HALT
[2025-11-06T16:15:09Z] INFO technical_analyst LOOP Presenting HALT to user
```

### Resultado

```yaml
loop_result:
  status: "HALTED"
  iterations_used: 3
  next_phase: "HALT"
  halt_type: "MAX_ITERATIONS_REACHED"

  remaining_failures:
    - item_id: "AT-07"
      question: "Especificações técnicas são consistentes entre si?"
      reason: "Requisito #12 vs #34 - Inconsistência de resolução"
      requires_human_input: true

  user_options:
    - id: "A"
      label: "Fornecer correção manual"
    - id: "B"
      label: "Marcar para revisão posterior"
    - id: "C"
      label: "Cancelar análise"
```

### Resposta do Usuário (Simulada)

```
Usuário escolheu: A1
Correção fornecida: "Requisito #34 está errado. O correto é gravação 4K."
```

### Re-execução Após Feedback Humano

```python
# Aplicar correção do usuário
csv_data_corrected = csv_data.copy()
csv_data_corrected[33]['Descrição'] = "Sistema de gravação com suporte a 4K"

# Re-inspecionar
inspect_result = run_inspect_phase(csv_data_corrected, "technical_analyst")

# Agora passa
if inspect_result['overall_status'] == "PASS":
    log_info("LOOP", "✓ Corrected after user intervention")
    return {
        "status": "SUCCESS_WITH_USER_INPUT",
        "iterations_used": 3,
        "user_intervention": True,
        "next_phase": "VALIDATE"
    }
```

---

## Comparação dos Exemplos

| Exemplo | Iterações | Tipo de Problema | Resultado |
|---------|-----------|------------------|-----------|
| 1 | 1 | Duplicata simples | ✅ Sucesso automático |
| 2 | 1 (2 correções) | Duplicata + Renumeração | ✅ Sucesso automático |
| 3 | 3 (max) | Inconsistência técnica | ⚠️ HALT (requer humano) |

---

## Lições dos Exemplos

### Quando LOOP Funciona Bem (Automático)

✅ **Problemas estruturais:**
- Duplicatas
- Gaps na numeração
- Campos vazios
- Formatação inconsistente

✅ **Problemas de integridade:**
- Referências quebradas
- IDs inconsistentes
- Checksums inválidos

### Quando LOOP Precisa de HALT (Humano)

⚠️ **Ambiguidades semânticas:**
- Requisitos contraditórios
- Especificações técnicas inconsistentes
- Múltiplas interpretações válidas

⚠️ **Decisões de negócio:**
- Qual requisito priorizar
- Como resolver conflitos
- O que considerar "correto"

---

**Versão:** 1.0
**Criado em:** 06/11/2025
