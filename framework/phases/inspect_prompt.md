# INSPECT Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes após EXECUTE

---

## 🎯 FASE INSPECT: Seu Protocolo de Auto-Inspeção

Após executar uma etapa, você DEVE auto-inspecionar usando checklists. Siga este protocolo:

### 1. CARREGAR Checklists

Você tem **2 checklists obrigatórios:**

**A) Checklist Fixo (Anti-Alucinação):**
- Localização: `framework/checklists/anti_alucinacao.yaml`
- Aplicável a: TODOS os agentes, SEMPRE
- Itens: 8 verificações de qualidade geral

**B) Checklist Dinâmico (Específico do Agente):**
- Localização: `agents/[seu_nome]/checklists/inspect.yaml`
- Aplicável a: Apenas você
- Itens: 8-10 verificações específicas da sua tarefa

---

### 2. EXECUTAR Cada Item do Checklist

**Para CADA item, faça:**

#### a) LER o Item

Estrutura do item:
```yaml
- id: "AA-01"
  question: "[Pergunta a responder]"
  how_to_check: "[Como verificar]"
  pass_criteria: "[Quando passa]"
  fail_criteria: "[Quando falha]"
```

#### b) VERIFICAR o Output

Siga as instruções em `how_to_check` literalmente.

**Exemplo:**
```
Item: "Não há requisitos duplicados?"
How to check: "Compare o texto da coluna 'Descrição' de todas as linhas"

Ação:
1. Ler todas as descrições
2. Comparar cada uma com as outras
3. Se encontrar 2 idênticas → status = false
4. Se todas únicas → status = true
```

#### c) DECIDIR: Passou ou Falhou?

**Decisão Binária:**
- `true` = Passou (atende `pass_criteria`)
- `false` = Falhou (atende `fail_criteria`)

**NÃO há meio-termo.** Não existe "quase passou" ou "95% OK".

---

### 3. REGISTRAR Resultado

**Para cada item, registre:**

```yaml
- item_id: "[ID do item]"
  question: "[Pergunta]"
  status: true/false
  evidence: "[Se passou: evidência. Se falhou: razão]"
```

**Se PASSOU (true):**
```yaml
  status: true
  evidence: "Todas as 47 linhas do CSV têm campo 'fonte' preenchido"
```

**Se FALHOU (false):**
```yaml
  status: false
  reason: "Requisitos ID 12 e 23 têm descrições idênticas"
  corrective_action: "Remover requisito ID 23 (duplicata)"
```

---

### 4. CONSOLIDAR Resultados

Após verificar **TODOS** os itens (não pare no primeiro erro):

```python
# Contar
total_items = len(fixo) + len(dinâmico)
passed_items = count(status == true)
failed_items = count(status == false)

# Decisão
if failed_items == 0:
    overall_status = "PASS"
    next_action = "VALIDATE"
else:
    overall_status = "FAIL"
    next_action = "LOOP"
```

---

### 5. APRESENTAR Sumário

**Se TODOS passaram:**

```markdown
✅ INSPEÇÃO PASSOU

Checklist Fixo: 8/8 ✓
Checklist Dinâmico: 8/8 ✓

Total: 16/16 (100%)

Próxima ação: VALIDATE
```

**Se ALGUM falhou:**

```markdown
❌ INSPEÇÃO FALHOU

Checklist Fixo: 8/8 ✓
Checklist Dinâmico: 7/8 ✗

Total: 15/16 (93.8%)

Itens que falharam:

1. [ED-03] "Não há requisitos duplicados?"
   Problema: Requisitos ID 12 e 23 têm descrições idênticas
   Ação corretiva: Remover requisito ID 23

Próxima ação: LOOP (corrigir problemas)
```

---

### 6. SALVAR Resultado

**OBRIGATÓRIO:** Salve o resultado completo em YAML:

```
Localização: data/analyses/[id]/inspection_step[N].yaml
Template: framework/templates/inspection_result.yaml
```

---

### 7. DECIDIR Próxima Ação

**Regra Simples (Modo Strict):**

```
SE todos os itens passaram (100%):
    → Prosseguir para VALIDATE

SE pelo menos 1 item falhou (< 100%):
    → Entrar em LOOP para corrigir
```

**NÃO continue se falhou.** Mesmo que seja "só 1 item" ou "coisa pequena". LOOP é obrigatório.

---

## ✅ Checklist de Auto-Verificação da Inspeção

Antes de sair desta fase, confirme:

- [ ] Carreguei e executei o checklist FIXO (anti-alucinação)?
- [ ] Carreguei e executei o checklist DINÂMICO (do meu agente)?
- [ ] Verifiquei TODOS os itens (não parei no primeiro erro)?
- [ ] Registrei evidência para cada item (PASS ou FAIL)?
- [ ] Consolidei os resultados corretamente?
- [ ] Salvei o resultado completo em YAML?
- [ ] Decidi corretamente a próxima ação (VALIDATE ou LOOP)?

**Se TODOS = ✅:** Prossiga conforme decisão (VALIDATE ou LOOP)

**Se ALGUM = ❌:** Corrija antes de prosseguir

---

## 📋 Template de Execução (Copy-Paste)

```python
# 1. Carregar checklists
fixed_checklist = load_yaml("framework/checklists/anti_alucinacao.yaml")
dynamic_checklist = load_yaml(f"agents/{agent_name}/checklists/inspect.yaml")

# 2. Executar checklist fixo
log_info("INSPECT", "Executing fixed checklist (Anti-Alucinação)")
fixed_results = []
for item in fixed_checklist['checklist']['items']:
    log_debug("INSPECT", f"Checking {item['id']}: {item['question']}")

    # Verificar item (lógica específica de cada item)
    passed, evidence = check_item(item, output_data)

    fixed_results.append({
        "item_id": item['id'],
        "question": item['question'],
        "status": passed,
        "evidence": evidence
    })

    if not passed:
        log_warning("INSPECT", f"✗ {item['id']} failed: {evidence}")

# 3. Executar checklist dinâmico
log_info("INSPECT", f"Executing dynamic checklist ({agent_name})")
dynamic_results = []
for item in dynamic_checklist['checklist']['items']:
    log_debug("INSPECT", f"Checking {item['id']}: {item['question']}")

    passed, evidence = check_item(item, output_data)

    dynamic_results.append({
        "item_id": item['id'],
        "question": item['question'],
        "status": passed,
        "evidence": evidence
    })

    if not passed:
        log_warning("INSPECT", f"✗ {item['id']} failed: {evidence}")

# 4. Consolidar
total = len(fixed_results) + len(dynamic_results)
passed = sum(1 for r in fixed_results + dynamic_results if r['status'])
failed = total - passed

overall_status = "PASS" if failed == 0 else "FAIL"

# 5. Apresentar sumário
if overall_status == "PASS":
    log_info("INSPECT", f"✓ All {total} items passed. Proceeding to VALIDATE")
else:
    log_warning("INSPECT", f"✗ {failed}/{total} items failed. Entering LOOP")

# 6. Salvar
inspection_result = {
    "timestamp": datetime.now().isoformat(),
    "fixed_checklist_results": fixed_results,
    "dynamic_checklist_results": dynamic_results,
    "summary": {
        "overall_status": overall_status,
        "items_total": total,
        "items_passed": passed,
        "items_failed": failed
    },
    "next_action": "LOOP" if overall_status == "FAIL" else "VALIDATE"
}

save_yaml(f"data/analyses/{analysis_id}/inspection_step{step_id}.yaml", inspection_result)

# 7. Retornar decisão
return inspection_result['next_action']
```

---

## ⚠️ Avisos Críticos

1. **NUNCA pule itens:** Mesmo que já tenha falhado um, execute TODOS
2. **NUNCA "arredonde":** 99.9% ≠ 100%, é FAIL
3. **NUNCA invente evidências:** Se não verificou de verdade, marque como FAIL
4. **SEMPRE salve o resultado:** YAML completo é obrigatório
5. **SEMPRE entre em LOOP se falhar:** Não há exceções em Modo Strict

---

## 🛡️ Modo Strict: Garantias Obrigatórias

- ✅ **Ambos os checklists:** Fixo E Dinâmico executados
- ✅ **Todos os itens:** Nenhum pulado
- ✅ **Scoring All-or-Nothing:** 100% = PASS, < 100% = FAIL
- ✅ **Evidências documentadas:** Para cada item
- ✅ **Resultado salvo:** YAML gerado
- ✅ **LOOP automático:** Se falhar

---

**Este é um componente reutilizável. Adapte conforme necessário para seu agente específico.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
