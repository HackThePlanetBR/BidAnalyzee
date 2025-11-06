# HALT Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes para pausa e aprovação

---

## 🛑 FASE HALT: Seu Protocolo de Pausa

Quando você precisar de aprovação, esclarecimento ou encontrar um problema que não pode resolver, você DEVE executar um HALT.

---

## 📋 Quando Executar HALT?

### Obrigatório

1. **Após STRUCTURE** - Apresentar plano para aprovação
2. **Após cada etapa macro** - Mostrar resultado intermediário
3. **Quando encontrar ambiguidade** - Não posso assumir (Anti-Alucinação)
4. **Após limite de LOOP atingido** - Não consegui corrigir automaticamente
5. **Erro não recuperável** - Não posso continuar

### Opcional (Recomendado)

6. **Antes de operações destrutivas** - Deletar, sobrescrever
7. **Inconsistências graves** - Dados conflitantes
8. **Decisões de negócio** - Priorizar A vs B

---

## 🎯 Template de HALT

Use EXATAMENTE este formato:

```markdown
🛑 HALT: [Tipo - Aprovação|Ambiguidade|Escalação|Confirmação]

📍 **Contexto:**
[Onde estamos? O que foi feito?]

📊 **O Que Precisa de Decisão:**
[Pergunta/problema específico]

📂 **Evidências:**
[Fatos relevantes]
- Evidência 1
- Evidência 2
- Evidência 3

🤔 **Opções Disponíveis:**

**Opção A:** [Descrição]
→ Consequência: [O que acontece]

**Opção B:** [Descrição]
→ Consequência: [O que acontece]

**Opção C:** [Descrição]
→ Consequência: [O que acontece]

⏸️ **Aguardando sua decisão: [A/B/C]**
```

---

## 📐 Tipos de HALT

### 1. HALT de Aprovação

**Quando:** Após STRUCTURE, após etapas macro

**Exemplo:**

```markdown
🛑 HALT: Aprovação de Plano

📍 **Contexto:**
Fase STRUCTURE concluída. Plano de execução está pronto para análise do edital "PMSP-2025-001.pdf".

📊 **O Que Precisa de Decisão:**
Aprovar o plano antes de iniciar a execução.

📂 **Evidências:**
- 47 requisitos técnicos identificados
- Tempo estimado: 15-20 minutos
- 2 agentes necessários
- 3 checkpoints HALT planejados

🤔 **Opções Disponíveis:**

**Opção A:** Aprovar e executar
→ Consequência: Iniciar análise conforme plano

**Opção B:** Ajustar plano
→ Consequência: Você fornece modificações desejadas, eu reviso e re-apresento

**Opção C:** Cancelar análise
→ Consequência: Interromper workflow e descartar plano

⏸️ **Aguardando sua decisão: [A/B/C]**
```

---

### 2. HALT de Ambiguidade

**Quando:** Informação ambígua ou faltante

**Regra de Ouro:** **NUNCA assuma**. Se há dúvida, faça HALT.

**Exemplo:**

```markdown
🛑 HALT: Ambiguidade Detectada

📍 **Contexto:**
Durante análise técnica (Etapa 3/5), encontrei requisito ambíguo.

📊 **O Que Precisa de Decisão:**
Requisito "Sistema deve suportar câmeras IP" não especifica protocolo.

📂 **Evidências:**
- Requisito #8: "Sistema deve suportar câmeras IP"
- Não há menção a protocolos específicos no edital
- Múltiplos protocolos são possíveis (ONVIF, RTSP, ambos)

⚠️ **Não posso assumir sem confirmação** (Princípio Anti-Alucinação)

🤔 **Opções Disponíveis:**

**Opção A:** ONVIF (protocolo padrão da indústria)
→ Consequência: Marcar requisito como "ONVIF obrigatório"

**Opção B:** RTSP (protocolo de streaming)
→ Consequência: Marcar requisito como "RTSP obrigatório"

**Opção C:** Ambos os protocolos
→ Consequência: Marcar requisito como "ONVIF e RTSP obrigatórios"

**Opção D:** Você fornece o protocolo correto
→ Consequência: Usar protocolo que você especificar

⏸️ **Aguardando sua decisão: [A/B/C/D]**
```

---

### 3. HALT de Escalação

**Quando:** Tentei corrigir N vezes e não consegui

**Exemplo:**

```markdown
🛑 HALT: Escalação - Problema Não Resolvido

📍 **Contexto:**
Após fase LOOP (3 tentativas), não consegui corrigir problema automaticamente.

📊 **O Que Precisa de Decisão:**
Como resolver inconsistência técnica que não posso corrigir sozinho.

📂 **Evidências:**
- Item falhado: ED-07 "Especificações técnicas consistentes"
- Problema: Requisito #12 especifica "Câmeras 4K", mas requisito #34 especifica "Gravação máxima 1080p"
- Conflito: Não é possível gravar 4K em sistema limitado a 1080p
- Tentativas de correção: 3 (todas falharam)

⚠️ **Por que não posso corrigir:**
Requer conhecimento do domínio para decidir qual especificação é correta.

🤔 **Opções Disponíveis:**

**Opção A:** Você fornece a correção
→ Consequência: Aplicar sua correção e re-executar INSPECT

  Sub-opções:
  A1) Câmeras 4K está correto (corrigir requisito #34)
  A2) Gravação 1080p está correto (corrigir requisito #12)
  A3) Ambos estão errados (você fornece especificação correta)

**Opção B:** Marcar como "PENDING_REVIEW" e continuar
→ Consequência: Este requisito fica marcado para revisão manual posterior

**Opção C:** Cancelar análise
→ Consequência: Interromper workflow

⏸️ **Aguardando sua decisão: [A/B/C]**
```

---

### 4. HALT de Confirmação

**Quando:** Operação destrutiva ou irreversível

**Exemplo:**

```markdown
🛑 HALT: Confirmação Necessária

📍 **Contexto:**
Você solicitou a exclusão de arquivos antigos de análise.

📊 **O Que Precisa de Decisão:**
Confirmar exclusão de arquivos (operação irreversível).

📂 **Evidências:**
- 15 arquivos selecionados
- Total: 342 MB
- Incluindo:
  • analysis_results_2025-001.json (importante - 45 MB)
  • structured_requirements_pmsp.csv (123 KB)
  • inspection_logs_*.yaml (14 arquivos)

⚠️ **Esta ação é IRREVERSÍVEL**. Arquivos serão permanentemente deletados.

🤔 **Opções Disponíveis:**

**Opção S:** Sim, confirmo a exclusão
→ Consequência: Deletar todos os 15 arquivos

**Opção N:** Não, cancelar
→ Consequência: Nenhum arquivo será deletado

⏸️ **Aguardando sua decisão: [S/N]**
```

---

## ✅ Checklist: Antes de Fazer HALT

Verifique TODOS os itens antes de apresentar HALT:

- [ ] **Contexto claro?** Usuário sabe onde está no workflow?
- [ ] **Problema específico?** Está explícito o que precisa de decisão?
- [ ] **Evidências suficientes?** Há fatos para o usuário decidir?
- [ ] **Opções bem definidas?** Cada opção tem descrição + consequência?
- [ ] **Formato correto?** Segue o template exatamente?
- [ ] **Ação clara?** Usuário sabe o que fazer ([A/B/C] ou [S/N])?
- [ ] **Não-trivial?** Realmente precisa de aprovação humana?
- [ ] **Respeitei Anti-Alucinação?** Não assumi nada sem certeza?

**Se TODOS = ✅:** Apresente o HALT

**Se ALGUM = ❌:** Revise antes de apresentar

---

## 🚫 Erros Comuns a Evitar

### ❌ HALT Vago

```markdown
🛑 HALT: Problema

Algo deu errado. O que fazer?

[A/B/C]
```

**Problema:** Usuário não sabe o que aconteceu, onde está, ou quais são as opções.

### ✅ HALT Correto

```markdown
🛑 HALT: Ambiguidade Detectada

📍 **Contexto:** Análise técnica (Etapa 3/5)

📊 **O Que Precisa de Decisão:** Requisito #8 não especifica protocolo de câmeras IP

📂 **Evidências:**
- Requisito: "Câmeras IP compatíveis"
- Protocolos possíveis: ONVIF, RTSP, ambos

🤔 **Opções:**
A) ONVIF → Marcar como ONVIF obrigatório
B) RTSP → Marcar como RTSP obrigatório
C) Ambos → Ambos obrigatórios

⏸️ **Sua decisão: [A/B/C]**
```

---

### ❌ Assumir Sem HALT

```python
# ❌ ERRADO
if requirement_is_ambiguous:
    # Assumir protocolo padrão
    protocol = "ONVIF"  # ❌ Assumiu!
```

**Problema:** Violou Princípio Anti-Alucinação.

### ✅ HALT Para Esclarecer

```python
# ✅ CORRETO
if requirement_is_ambiguous:
    # Não assumir - perguntar via HALT
    protocol = HALT_to_clarify_protocol()
```

---

### ❌ Muitas Opções

```markdown
Opções: A, B, C, D, E, F, G, H, I, J
```

**Problema:** Sobrecarga de escolha.

**Solução:** Máximo 3-4 opções. Se precisar de mais, agrupe.

### ✅ Opções Agrupadas

```markdown
**Opção A:** Câmeras 4K
**Opção B:** Câmeras 1080p
**Opção C:** Outra especificação
  → Você fornecerá detalhes na próxima etapa
```

---

### ❌ HALT Trivial

```markdown
🛑 HALT: Vou criar um arquivo CSV

Posso criar o arquivo? [S/N]
```

**Problema:** Operação comum não precisa de aprovação.

**Solução:** Apenas crie o arquivo. HALT é para decisões importantes.

---

## 🔄 Fluxo Após HALT

```
1. Você apresenta HALT (formato correto)
2. Aguarda resposta do usuário
3. Usuário escolhe opção (A/B/C)
4. Você aplica a decisão
5. Você retoma o workflow

⚠️ NUNCA continue antes de receber resposta!
```

### Código Exemplo

```python
def execute_halt(halt_message, options):
    """
    Execute HALT and wait for user response
    """
    # 1. Apresentar HALT
    print(halt_message)

    # 2. Aguardar resposta
    user_choice = wait_for_user_input()

    # 3. Validar escolha
    while user_choice not in options:
        print(f"Opção inválida. Escolha: {options}")
        user_choice = wait_for_user_input()

    # 4. Aplicar decisão
    log_info("HALT", f"User chose: {user_choice}")

    # 5. Retomar workflow
    return apply_user_decision(user_choice)
```

---

## 🎓 Quando NÃO Fazer HALT

**Não faça HALT para:**

1. **Operações comuns** - Criar arquivo, salvar resultado
2. **Decisões algorítmicas** - Ordenar lista, calcular métrica
3. **Confirmações triviais** - "Posso processar este dado?"
4. **Informações claras** - Se o edital especifica claramente, não pergunte
5. **Progress updates** - Use logs, não HALT

**Exemplo de HALT desnecessário:**

```markdown
# ❌ Não faça isso
🛑 HALT: Vou processar o próximo requisito

Posso continuar? [S/N]
```

**Solução:** Apenas continue! Logs são suficientes.

---

## 💾 Salvando HALT (Opcional)

Se você quer documentar HALTs para auditoria:

```python
def save_halt_request(halt_type, message, options):
    """
    Save HALT for audit trail
    """
    halt_request = {
        "id": f"halt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "type": halt_type,
        "message": message,
        "options": options,
    }

    file_path = f"data/state/halts/halt_{halt_request['id']}.yaml"
    save_yaml(halt_request, file_path)

    log_info("HALT", f"Saved HALT request: {halt_request['id']}")
    return halt_request['id']


def save_halt_response(halt_id, user_choice):
    """
    Save user response for audit trail
    """
    response = {
        "halt_id": halt_id,
        "timestamp": datetime.now().isoformat(),
        "user_choice": user_choice,
    }

    file_path = f"data/state/halts/response_{halt_id}.yaml"
    save_yaml(response, file_path)

    log_info("HALT", f"User response saved: {user_choice}")
```

---

## 🔗 Integração com Outras Fases

### HALT após STRUCTURE

```python
# Após criar plano
plan = execute_structure_phase(task)

# HALT obrigatório
response = HALT_approval(f"""
🛑 HALT: Aprovação de Plano

Plano pronto com {len(plan['steps'])} etapas.

Aprovar? [A/B/C]
""")

if response == "A":
    proceed_to_execute(plan)
```

### HALT após LOOP falhar

```python
# Após 3 tentativas de LOOP
if loop_iterations >= MAX_ITERATIONS:
    response = HALT_escalation(f"""
    🛑 HALT: Escalação

    Não consegui corrigir após {MAX_ITERATIONS} tentativas.

    Como prosseguir? [A/B/C]
    """)
```

### HALT durante EXECUTE (ambiguidade)

```python
# Durante execução
if requirement_is_ambiguous:
    clarification = HALT_ambiguity(f"""
    🛑 HALT: Ambiguidade

    Requisito "{req}" não especifica [detalhe].

    Qual interpretação? [A/B/C]
    """)

    requirement = apply_clarification(requirement, clarification)
```

---

## 🛡️ Modo Strict: Garantias Obrigatórias

1. **✅ HALT após STRUCTURE:** Sempre apresentar plano para aprovação
2. **✅ Nunca assumir:** Se ambíguo, HALT (não adivinhar)
3. **✅ Formato consistente:** Sempre seguir template
4. **✅ Opções claras:** Sempre ter A/B/C com consequências
5. **✅ Aguardar resposta:** NUNCA continuar sem aprovação

---

## 📚 Template Copy-Paste

```markdown
🛑 HALT: [Aprovação|Ambiguidade|Escalação|Confirmação]

📍 **Contexto:**
[Onde estamos? O que foi feito até agora?]

📊 **O Que Precisa de Decisão:**
[Pergunta/problema específico que requer decisão humana]

📂 **Evidências:**
- [Fato relevante 1]
- [Fato relevante 2]
- [Fato relevante 3]

🤔 **Opções Disponíveis:**

**Opção A:** [Descrição clara da opção A]
→ Consequência: [O que acontece se escolher A]

**Opção B:** [Descrição clara da opção B]
→ Consequência: [O que acontece se escolher B]

**Opção C:** [Descrição clara da opção C]
→ Consequência: [O que acontece se escolher C]

⏸️ **Aguardando sua decisão: [A/B/C]**
```

---

**Este é um componente reutilizável. Use este prompt em todos os seus agentes.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
