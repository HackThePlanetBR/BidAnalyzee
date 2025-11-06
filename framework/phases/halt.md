# HALT Phase - Guia Teórico Completo

**Versão:** 1.0
**Tipo:** Guia de implementação
**Fase SHIELD:** H - HALT (Parada para Aprovação)

---

## 🎯 O Que É a Fase HALT?

**HALT** é a fase onde o agente **pausa a execução** e **solicita aprovação/feedback do usuário** antes de prosseguir.

É um ponto de controle humano no workflow automatizado.

### Conceito Central

```
┌─────────────────┐
│  Agente IA      │
│  (Autonomia)    │
└────────┬────────┘
         │
         ↓
    ┌────┴─────┐
    │   HALT   │ ← Transfere controle para humano
    └────┬─────┘
         │
         ↓
┌────────┴────────┐
│  Usuário        │
│  (Decisão)      │
└────────┬────────┘
         │
         ↓ [Aprovado/Corrigido]
┌────────┴────────┐
│  Agente IA      │
│  (Retoma)       │
└─────────────────┘
```

**Metáfora:** É como um motorista de F1 parando no pit stop. O carro para, a equipe avalia, decide o que fazer, e o carro volta à pista.

---

## 🔍 Por Que HALT É Necessário?

### 1. **Governança Humana**

A IA é poderosa, mas **não deve tomar todas as decisões sozinha**:

- ❌ **Sem HALT:** IA executa tudo sem supervisão → Pode errar gravemente sem chance de correção
- ✅ **Com HALT:** Humano aprova cada etapa macro → Erros são detectados cedo

### 2. **Transparência**

HALT força a IA a **explicar o que fez** e **o que pretende fazer**:

```python
# Sem HALT (caixa preta)
result = magic_black_box(input)  # O que aconteceu aqui? 🤷

# Com HALT (transparente)
plan = structure(input)
HALT("Este é o plano. Aprova?")  # 👁️ Visibilidade

approved = user_reviews(plan)
if approved:
    result = execute(plan)
    HALT("Este é o resultado. Prosseguir?")  # 👁️ Controle
```

### 3. **Ambiguidade**

Quando há **múltiplas interpretações válidas**, IA não deve "adivinhar":

```python
# Situação ambígua
requirement = "Sistema deve ser 'rápido'"

# ❌ Errado: IA assume
assumed_threshold = 100  # ms (assumiu!)

# ✅ Correto: IA pergunta via HALT
HALT("""
    Requisito ambíguo: "Sistema deve ser rápido"

    Interpretações possíveis:
    A) < 100ms (tempo de resposta)
    B) < 1s (tempo de processamento completo)
    C) Outro (você define)

    Qual interpretação está correta? [A/B/C]
""")
```

---

## 📐 Quando Usar HALT?

### Obrigatório (Modo Strict)

1. **Após STRUCTURE** - Apresentar plano para aprovação
2. **Após cada etapa macro** - Mostrar resultado intermediário
3. **Quando encontrar ambiguidade** - Solicitar esclarecimento
4. **Após atingir limite de iterações (LOOP)** - Escalar problema
5. **Ao encontrar erro não recuperável** - Pedir ajuda

### Opcional (Recomendado)

6. **Antes de operações destrutivas** - Deletar, sobrescrever, etc.
7. **Ao detectar inconsistências graves** - Dados conflitantes
8. **Em decisões de negócio** - Priorizar requisito A vs B

---

## 🛠️ Como Executar HALT?

### Protocolo de 6 Passos

```
1. CONTEXTUALIZAR → O que foi feito até agora?
2. APRESENTAR → O que precisa de decisão?
3. EVIDENCIAR → Quais são os fatos relevantes?
4. PROPOR → Quais são as opções disponíveis?
5. AGUARDAR → Pausar execução (wait for user input)
6. RETOMAR → Aplicar decisão e continuar workflow
```

---

## 📋 Anatomia de um Bom HALT

### Estrutura Obrigatória

```markdown
🛑 HALT: [Tipo de Parada]

📍 Contexto:
[Onde estamos no workflow? O que foi feito?]

📊 O Que Precisa de Decisão:
[Qual é a pergunta/problema específico?]

📂 Evidências:
[Fatos relevantes para tomar a decisão]

🤔 Opções Disponíveis:

Opção A: [Descrição clara]
  → Consequência: [O que acontece se escolher A]

Opção B: [Descrição clara]
  → Consequência: [O que acontece se escolher B]

Opção C: [Descrição clara]
  → Consequência: [O que acontece se escolher C]

⏸️ Aguardando sua decisão: [A/B/C]
```

### Exemplo Completo

```markdown
🛑 HALT: Aprovação de Plano

📍 Contexto:
Você solicitou a análise do edital "PMSP-2025-001.pdf" (345 páginas).
Fase STRUCTURE concluída. Plano de execução está pronto.

📊 O Que Precisa de Decisão:
Aprovar o plano de execução antes de iniciar a análise.

📂 Evidências:
- Edital possui 47 requisitos técnicos identificados
- Estimativa de tempo: 15-20 minutos
- Recursos necessários: 2 agentes (Document Structurer, Technical Analyst)
- 3 checkpoints HALT planejados (após estruturação, após análise, antes de entrega)

🤔 Opções Disponíveis:

Opção A: Aprovar e executar
  → Consequência: Iniciar análise conforme plano

Opção B: Ajustar plano
  → Consequência: Você fornece modificações desejadas

Opção C: Cancelar análise
  → Consequência: Interromper workflow e descartar plano

⏸️ Aguardando sua decisão: [A/B/C]
```

---

## 🎯 Tipos de HALT

### 1. HALT de Aprovação (Approval HALT)

**Quando:** Após STRUCTURE, após etapas macro

**Objetivo:** Obter aprovação para prosseguir

**Estrutura:**
```markdown
🛑 HALT: Aprovação de [Etapa]

Plano/Resultado pronto para sua revisão.

Opções:
A) Aprovar e prosseguir
B) Solicitar ajustes
C) Cancelar
```

**Exemplo Real:**
```python
# Após STRUCTURE
plan = structure_phase(task)
save_yaml(plan, "plan_001.yaml")

HALT(f"""
🛑 HALT: Aprovação de Plano

Plano completo para análise do edital "{edital_name}":
- {len(plan['steps'])} etapas
- Tempo estimado: {plan['metadata']['estimated_duration']}
- Checkpoints: {len(plan['halt_points'])}

Opções:
A) Aprovar e executar
B) Ajustar plano (especifique mudanças)
C) Cancelar

Sua escolha: [A/B/C]
""")

user_choice = wait_for_user_input()

if user_choice == "A":
    proceed_to_execute(plan)
elif user_choice == "B":
    adjustments = get_user_adjustments()
    plan = revise_plan(plan, adjustments)
    HALT_again_for_approval(plan)  # Re-HALT com plano revisado
else:
    cancel_workflow()
```

---

### 2. HALT de Ambiguidade (Ambiguity HALT)

**Quando:** Encontrar informação ambígua ou faltante

**Objetivo:** Solicitar esclarecimento para evitar assumir

**Estrutura:**
```markdown
🛑 HALT: Ambiguidade Detectada

Encontrei [descrição da ambiguidade].

Não posso prosseguir sem esclarecimento (Princípio Anti-Alucinação).

Opções:
A) [Interpretação 1]
B) [Interpretação 2]
C) Você fornece a interpretação correta
```

**Exemplo Real:**
```python
# Durante EXECUTE
requirement = "Sistema deve suportar câmeras IP"

# Ambiguidade detectada: Qual protocolo?
HALT(f"""
🛑 HALT: Ambiguidade Detectada

Requisito: "{requirement}"

Ambiguidade: O edital não especifica qual protocolo de câmeras IP.

Interpretações possíveis:
A) ONVIF (protocolo padrão da indústria)
B) RTSP (protocolo de streaming)
C) Ambos os protocolos
D) Você fornece o protocolo correto

⚠️ Não posso assumir sem confirmação (Princípio Anti-Alucinação).

Qual protocolo deve ser considerado? [A/B/C/D]
""")

protocol = wait_for_user_input()
requirement_clarified = f"{requirement} - Protocolo: {protocol}"
```

---

### 3. HALT de Escalação (Escalation HALT)

**Quando:** Após atingir limite de tentativas (LOOP), erro não recuperável

**Objetivo:** Escalar problema para humano resolver

**Estrutura:**
```markdown
🛑 HALT: Escalação - Problema Não Resolvido

Tentei corrigir automaticamente [N] vezes, mas o problema persiste.

Detalhes: [descrição do problema]

Opções:
A) Você fornece correção manual
B) Marcar para revisão posterior e continuar
C) Cancelar análise
```

**Exemplo Real:**
```python
# Após 3 iterações de LOOP falharem
HALT(f"""
🛑 HALT: Escalação - Limite de Iterações Atingido

Tentei corrigir o problema {MAX_ITERATIONS} vezes, mas não consegui resolver.

Problema:
- Item ED-07: "Especificações técnicas inconsistentes"
- Requisito #12: "Câmeras 4K"
- Requisito #34: "Gravação máxima 1080p"
- Conflito: Não é possível gravar 4K em sistema limitado a 1080p

Por que não posso corrigir:
Requer conhecimento do domínio para decidir qual especificação é correta.

Opções:
A) Você fornece a correção
   → Qual especificação está correta?
     1. Câmeras 4K (manter requisito #12)
     2. Gravação 1080p (manter requisito #34)
     3. Ambos estão errados (você fornece o correto)

B) Marcar como "PENDING_REVIEW" e continuar
   → Análise continua, mas este item fica pendente

C) Cancelar análise
   → Interromper workflow

Sua escolha: [A/B/C]
""")
```

---

### 4. HALT de Confirmação (Confirmation HALT)

**Quando:** Antes de operações destrutivas ou irreversíveis

**Objetivo:** Confirmar que o usuário realmente quer fazer isso

**Estrutura:**
```markdown
🛑 HALT: Confirmação Necessária

Você está prestes a [ação destrutiva].

⚠️ Esta ação é IRREVERSÍVEL.

Confirma? [S/N]
```

**Exemplo Real:**
```python
# Antes de deletar arquivo
HALT(f"""
🛑 HALT: Confirmação de Deleção

Você solicitou a exclusão de:
- {len(files)} arquivos
- Total: {total_size} MB
- Incluindo: analysis_results_2025-001.json (importante)

⚠️ Esta ação é IRREVERSÍVEL. Arquivos serão permanentemente deletados.

Confirma a exclusão? [S/N]
""")

if user_confirms():
    delete_files(files)
else:
    cancel_deletion()
```

---

## 🔄 Fluxo de HALT no Workflow

### Fluxo Normal (Approval HALT)

```
STRUCTURE → HALT (aprovar plano?) → EXECUTE → INSPECT → VALIDATE → HALT (aprovar entrega?) → DELIVER
```

### Fluxo com Ambiguidade

```
EXECUTE (passo 3) → Ambiguidade detectada → HALT (esclarecer?) → Usuário responde → Retoma EXECUTE (passo 3)
```

### Fluxo com Escalação (LOOP falhou)

```
INSPECT (falhou) → LOOP (tentativa 1) → INSPECT (falhou) → LOOP (tentativa 2) → INSPECT (falhou) → LOOP (tentativa 3) → INSPECT (falhou) → HALT (escalar problema)
```

---

## 📊 Boas Práticas de HALT

### ✅ DO (Faça)

1. **Seja claro e conciso**
   ```markdown
   🛑 HALT: Aprovação de Plano

   Plano pronto. Aprovar? [S/N]
   ```
   ✅ Direto ao ponto

2. **Ofereça opções claras**
   ```markdown
   Opções:
   A) Continuar
   B) Ajustar
   C) Cancelar
   ```
   ✅ Fácil de escolher

3. **Forneça contexto suficiente**
   ```markdown
   📍 Contexto: Etapa 2/5 concluída (Estruturação)
   ```
   ✅ Usuário sabe onde está

4. **Explique consequências**
   ```markdown
   Opção A: Aprovar
   → Consequência: Iniciar análise (15-20 min)
   ```
   ✅ Usuário sabe o que vai acontecer

### ❌ DON'T (Não Faça)

1. **Não seja vago**
   ```markdown
   Algo deu errado. O que fazer?
   ```
   ❌ Usuário não sabe o que aconteceu

2. **Não ofereça muitas opções**
   ```markdown
   Opções: A, B, C, D, E, F, G, H, I, J
   ```
   ❌ Sobrecarga de escolha

3. **Não assuma sem HALT**
   ```python
   # ❌ Assumir sem perguntar
   if ambiguous:
       value = guess_value()  # Errado!

   # ✅ HALT para esclarecer
   if ambiguous:
       value = HALT_to_clarify()  # Correto!
   ```

4. **Não faça HALT trivial**
   ```markdown
   HALT: Vou criar um arquivo. Ok?
   ```
   ❌ Desnecessário (operação comum)

---

## 🧪 Checklist de Qualidade do HALT

Antes de apresentar um HALT ao usuário, verifique:

- [ ] **Contexto claro:** Usuário sabe onde está no workflow?
- [ ] **Problema específico:** O que precisa de decisão está explícito?
- [ ] **Evidências fornecidas:** Há fatos suficientes para decidir?
- [ ] **Opções bem definidas:** Cada opção tem descrição e consequência?
- [ ] **Formato consistente:** Segue o template padrão?
- [ ] **Ação clara:** Usuário sabe o que fazer (A/B/C, S/N)?
- [ ] **Não-trivial:** Realmente precisa de aprovação humana?

**Se TODOS = ✅:** Apresente o HALT

**Se ALGUM = ❌:** Revise antes de apresentar

---

## 🔧 Implementação Técnica

### Estrutura de Dados (HALT Request)

```yaml
halt_request:
  id: "halt_20251106_160523_001"
  timestamp: "2025-11-06T16:05:23Z"
  agent: "document_structurer"
  type: "approval"  # approval | ambiguity | escalation | confirmation

  context:
    workflow_step: "After STRUCTURE phase"
    completed_steps: ["structure"]
    current_phase: "HALT"
    next_phase: "EXECUTE"

  message: |
    🛑 HALT: Aprovação de Plano

    Plano completo para análise do edital "PMSP-2025-001.pdf":
    - 5 etapas
    - Tempo estimado: 15-20 minutos
    - 3 checkpoints

    Opções:
    A) Aprovar e executar
    B) Ajustar plano
    C) Cancelar

    Sua escolha: [A/B/C]

  options:
    - id: "A"
      label: "Aprovar e executar"
      consequence: "Iniciar análise conforme plano"
      next_action: "EXECUTE"

    - id: "B"
      label: "Ajustar plano"
      consequence: "Solicitar modificações ao plano"
      next_action: "ADJUST_PLAN_THEN_HALT_AGAIN"

    - id: "C"
      label: "Cancelar"
      consequence: "Interromper workflow"
      next_action: "CANCEL_WORKFLOW"

  evidence:
    - key: "edital_pages"
      value: 345
    - key: "requirements_identified"
      value: 47
    - key: "agents_required"
      value: ["document_structurer", "technical_analyst"]
```

### Salvar HALT Request

```python
def save_halt_request(halt_request):
    """
    Save HALT request to data/state/halts/
    """
    halt_id = halt_request['id']
    file_path = f"data/state/halts/halt_{halt_id}.yaml"

    with open(file_path, 'w') as f:
        yaml.dump(halt_request, f)

    log_info("HALT", f"Saved HALT request: {halt_id}")
    return file_path
```

### Aguardar Resposta do Usuário

```python
def wait_for_user_response(halt_request):
    """
    Present HALT to user and wait for response
    """
    halt_id = halt_request['id']

    # Apresentar mensagem ao usuário
    print(halt_request['message'])

    # Aguardar input
    user_input = input(">>> ")

    # Validar input
    valid_options = [opt['id'] for opt in halt_request['options']]

    while user_input not in valid_options:
        print(f"Opção inválida. Escolha uma das opções: {valid_options}")
        user_input = input(">>> ")

    # Registrar resposta
    response = {
        "halt_id": halt_id,
        "timestamp": datetime.now().isoformat(),
        "user_choice": user_input,
        "chosen_option": next(opt for opt in halt_request['options'] if opt['id'] == user_input),
    }

    # Salvar resposta
    response_path = f"data/state/halts/response_{halt_id}.yaml"
    with open(response_path, 'w') as f:
        yaml.dump(response, f)

    log_info("HALT", f"User chose: {user_input}")

    return response
```

### Retomar Workflow

```python
def resume_after_halt(response):
    """
    Resume workflow based on user response
    """
    next_action = response['chosen_option']['next_action']

    log_info("HALT", f"Resuming with action: {next_action}")

    if next_action == "EXECUTE":
        return execute_phase()

    elif next_action == "ADJUST_PLAN_THEN_HALT_AGAIN":
        adjustments = get_user_adjustments()
        plan = revise_plan(adjustments)
        return HALT_for_approval(plan)  # Re-HALT

    elif next_action == "CANCEL_WORKFLOW":
        log_info("HALT", "Workflow cancelled by user")
        return {"status": "CANCELLED"}

    else:
        log_error("HALT", f"Unknown action: {next_action}")
        raise ValueError(f"Unknown next_action: {next_action}")
```

---

## 🎓 Exemplos Avançados

### Exemplo 1: HALT com Múltiplos Níveis

```python
def multi_level_halt():
    # Nível 1: Aprovação do plano geral
    plan = structure_phase()
    response_1 = HALT_approval(plan, level=1)

    if response_1['user_choice'] == "A":
        # Nível 2: Aprovação de etapa específica (dados sensíveis)
        sensitive_step = plan['steps'][3]

        if sensitive_step['involves_sensitive_data']:
            response_2 = HALT_confirmation(
                message="Etapa 4 envolve processamento de dados sensíveis. Confirma?",
                level=2
            )

            if response_2['user_choice'] == "N":
                # Nível 3: Alternativas
                response_3 = HALT_alternatives(
                    message="Como prosseguir sem processar dados sensíveis?",
                    options=["Skip etapa 4", "Anonimizar dados", "Cancelar"],
                    level=3
                )
```

### Exemplo 2: HALT com Timeout

```python
def halt_with_timeout(halt_request, timeout_seconds=300):
    """
    HALT with auto-default after timeout
    """
    import threading
    import time

    result = {"user_responded": False, "choice": None}

    def get_user_input():
        choice = wait_for_user_response(halt_request)
        result["user_responded"] = True
        result["choice"] = choice

    # Start input thread
    input_thread = threading.Thread(target=get_user_input)
    input_thread.daemon = True
    input_thread.start()

    # Wait for timeout
    input_thread.join(timeout=timeout_seconds)

    if not result["user_responded"]:
        # Timeout reached - use default option
        default_option = halt_request.get('default_option', 'A')
        log_warning("HALT", f"Timeout reached. Using default option: {default_option}")

        return {
            "user_choice": default_option,
            "timeout_triggered": True
        }

    return result["choice"]
```

---

## 📚 Referências

- **Framework SHIELD completo:** `../OPERATING_PRINCIPLES.md`
- **Outras fases:** `structure.md`, `execute.md`, `inspect.md`, `loop.md`
- **PRD:** História 1.5 (Épico 1)

---

**Versão:** 1.0
**Criado em:** 06/11/2025
**Última atualização:** 06/11/2025
