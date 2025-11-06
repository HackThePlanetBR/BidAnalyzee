# SHIELD Phase: LOOP (Repetição)

**Versão:** 1.0
**Fase:** L - LOOP
**Responsável:** IA (execução), acionado pela IA (falha INSPECT) ou Humano (feedback HALT)
**Modo Obrigatório:** Strict

---

## 📖 Visão Geral

A fase **LOOP** é o mecanismo de auto-correção do SHIELD. Quando a inspeção (INSPECT) identifica problemas, ou quando o usuário solicita ajustes (via HALT), o agente entra em LOOP para corrigir e tentar novamente.

**Princípio Fundamental:** "Corrija o problema específico. Não refaça tudo. Limite: 3 tentativas."

---

## 🎯 Objetivos da Fase LOOP

1. **Identificar** o problema específico a corrigir
2. **Aplicar** correção cirúrgica (não refazer tudo)
3. **Re-executar** a etapa corrigida
4. **Re-inspecionar** para verificar se o problema foi resolvido
5. **Limitar** iterações (máximo 3 tentativas)
6. **HALT** se não conseguir corrigir após limite

---

## 📋 Quando Usar

- ✅ **Automático** quando INSPECT retorna FAIL
- ✅ **Manual** quando usuário solicita ajustes via HALT
- ✅ Antes de Re-EXECUTE

**Triggers:**

```python
# Trigger 1: INSPECT falhou
if inspect_result['overall_status'] == "FAIL":
    enter_loop(inspect_result['failed_items'])

# Trigger 2: Usuário pediu ajustes
if halt_response == "solicitar_ajustes":
    enter_loop(user_feedback)
```

---

## 🔧 Como Executar a Fase LOOP

### Entrada (Input)

- **Resultado da INSPECT** (se trigger automático)
- **Feedback do usuário** (se trigger manual)
- **Iteração atual** (1, 2 ou 3)

### Processo

#### 1. Analisar Problemas Identificados

**Carregar itens que falharam:**

```python
def analyze_failures(inspect_result):
    """Analyze what failed in INSPECT"""
    failed_items = inspect_result['failed_items']

    for item in failed_items:
        log_info("LOOP", f"Problem: {item['item_id']} - {item['reason']}")
        log_info("LOOP", f"Suggested action: {item['corrective_action']}")

    return failed_items
```

**Exemplo:**
```
LOOP: Problem: ED-03 - Requisitos ID 12 e 23 duplicados
LOOP: Suggested action: Remover requisito ID 23
```

---

#### 2. Priorizar Correções

**Ordem de prioridade por severidade:**

```python
def prioritize_corrections(failed_items):
    """Sort failures by severity"""
    priority_order = {
        "critical": 1,
        "high": 2,
        "medium": 3,
        "low": 4
    }

    return sorted(
        failed_items,
        key=lambda x: priority_order.get(x.get('severity', 'medium'), 3)
    )
```

**Critical** → Corrigir primeiro
**Low** → Corrigir por último

---

#### 3. Aplicar Correções Cirúrgicas

**Regra de Ouro:** Corrija apenas o problema específico, não refaça tudo.

```python
def apply_correction(failed_item, data):
    """
    Apply surgical correction for specific failure
    DO NOT re-execute entire step, just fix the issue
    """
    item_id = failed_item['item_id']
    corrective_action = failed_item['corrective_action']

    log_info("LOOP", f"Applying correction for {item_id}")

    if item_id == "ED-03":  # Duplicatas
        # Correção específica: remover duplicatas
        data = remove_duplicates(data)
        log_info("LOOP", "Removed duplicate entries")

    elif item_id == "ED-04":  # Gaps na numeração
        # Correção específica: renumerar
        data = renumber_items(data)
        log_info("LOOP", "Renumbered items sequentially")

    # ... outras correções específicas ...

    return data
```

**Exemplos de Correções Cirúrgicas:**

```python
# Remover duplicata
def remove_duplicates(csv_data):
    seen = set()
    unique_data = []

    for row in csv_data:
        row_hash = hash(row['Descrição'])
        if row_hash not in seen:
            seen.add(row_hash)
            unique_data.append(row)
        else:
            log_debug("LOOP", f"Removed duplicate: {row['ID']}")

    return unique_data

# Renumerar IDs
def renumber_items(csv_data):
    for i, row in enumerate(csv_data, start=1):
        if row['ID'] != i:
            log_debug("LOOP", f"Renumbered: {row['ID']} → {i}")
            row['ID'] = i

    return csv_data
```

---

#### 4. Re-Executar Etapa (Parcial)

**Não re-executar tudo, apenas o necessário:**

```python
def re_execute_step(step_context, corrected_data, iteration):
    """
    Re-execute only what's needed after correction
    """
    log_info("LOOP", f"Re-executing step (iteration {iteration})")

    # Se a correção já foi aplicada aos dados, apenas salvar
    if corrected_data:
        save_output(corrected_data)
        log_info("LOOP", "Saved corrected output")
        return {"status": "SUCCESS", "output": corrected_data}

    # Se precisa re-processar algo, fazer apenas o necessário
    # (não todo o EXECUTE original)
```

---

#### 5. Re-Inspecionar

**Executar INSPECT novamente:**

```python
def re_inspect_after_loop(corrected_output, iteration):
    """
    Run INSPECT again after corrections
    """
    log_info("LOOP", f"Re-inspecting (iteration {iteration})")

    # Executar INSPECT completo novamente
    inspect_result = run_inspect_phase(corrected_output)

    if inspect_result['overall_status'] == "PASS":
        log_info("LOOP", f"✓ Correction successful (iteration {iteration})")
        return "VALIDATE"  # Sair do loop

    else:
        # Ainda há problemas
        remaining_failures = inspect_result['overall']['items_failed']
        log_warning("LOOP", f"✗ Still {remaining_failures} failures after iteration {iteration}")

        if iteration < MAX_LOOP_ITERATIONS:
            # Tentar novamente
            return "LOOP_AGAIN"
        else:
            # Atingiu limite
            log_error("LOOP", "Max iterations reached. Escalating to HALT")
            return "HALT"
```

---

#### 6. Gerenciar Limite de Iterações

**Máximo: 3 tentativas (configurável via .env)**

```python
MAX_LOOP_ITERATIONS = int(os.getenv("MAX_LOOP_ITERATIONS", 3))

def loop_with_limit(inspect_result, max_iterations=3):
    """
    Loop with maximum iteration limit
    """
    for iteration in range(1, max_iterations + 1):
        log_info("LOOP", f"=== Iteration {iteration}/{max_iterations} ===")

        # 1. Analisar problemas
        failed_items = analyze_failures(inspect_result)

        # 2. Aplicar correções
        corrected_data = apply_corrections(failed_items, data)

        # 3. Re-executar (parcial)
        execute_result = re_execute_step(step_context, corrected_data, iteration)

        # 4. Re-inspecionar
        inspect_result = run_inspect_phase(execute_result['output'])

        # 5. Decidir
        if inspect_result['overall_status'] == "PASS":
            log_info("LOOP", f"✓ Successfully corrected after {iteration} iteration(s)")
            return "VALIDATE"

    # Após 3 tentativas, ainda falhou
    log_error("LOOP", f"Failed to correct after {max_iterations} iterations")

    halt_message = f"""
    ❌ Não Foi Possível Corrigir Automaticamente

    Tentativas: {max_iterations}
    Problemas restantes: {inspect_result['overall']['items_failed']}

    Detalhes:
    {format_failures(inspect_result['failed_items'])}

    Opções:
    1. Você corrige manualmente e fornece novo input
    2. Marcar esta etapa para revisão humana posterior
    3. Cancelar análise

    Sua escolha [1-3]:
    """

    return HALT(halt_message)
```

---

### Saída (Output)

1. **Dados corrigidos** (versão atualizada)
2. **Número de iterações** usadas
3. **Status** (sucesso após N tentativas, ou HALT após limite)
4. **Log** de cada correção aplicada

---

## 📊 Fluxo Completo do LOOP

```
INSPECT falhou
    ↓
┌───LOOP (iteração 1)───┐
│                       │
│ 1. Analisar problemas │
│ 2. Aplicar correções  │
│ 3. Re-executar        │
│ 4. Re-inspecionar     │
│                       │
└───────┬───────────────┘
        │
    ┌───┴───┐
    │Passou?│
    └───┬───┘
        │
   ❌ Não│  Sim ✅
        │    │
        ↓    ↓
  (iteração < 3?)  → VALIDATE
        │
    Sim │  Não
        │    │
        ↓    ↓
     LOOP   HALT
 (iteração 2)
```

---

## ✅ Boas Práticas

### DO ✅

- **Correções cirúrgicas:** Apenas o problema específico
- **Re-inspecionar sempre:** Após cada correção
- **Respeitar limite:** Máximo 3 iterações
- **Logar cada correção:** O que foi mudado
- **Escalate quando necessário:** HALT se não resolver

### DON'T ❌

- **Não refazer tudo:** Apenas corrija o problema
- **Não ignorar limite:** Loops infinitos são perigosos
- **Não assumir sucesso:** Sempre re-inspecionar
- **Não aplicar correções não solicitadas:** Só o que falhou

---

## 🛡️ Modo Strict: Garantias

1. **✅ Limite obrigatório:** Máximo 3 iterações
2. **✅ Re-inspeção obrigatória:** Após cada correção
3. **✅ Logging completo:** Cada correção documentada
4. **✅ HALT se falhar:** Não continuar sem resolver
5. **✅ Correções específicas:** Não refazer etapa inteira

---

## 📚 Referências

- **Princípios SHIELD:** `../../OPERATING_PRINCIPLES.md`
- **Fase anterior:** `inspect.md`
- **Próxima fase:** Re-EXECUTE ou HALT
- **Config:** `MAX_LOOP_ITERATIONS` em `.env`

---

**Versão:** 1.0
**Criado em:** 06/11/2025
**Última atualização:** 06/11/2025
