# HALT Phase - Exemplos Práticos

**Versão:** 1.0

---

## Exemplo 1: HALT de Aprovação (Após STRUCTURE)

**Contexto:** Usuário solicitou análise de edital. Fase STRUCTURE concluída, plano pronto.

### HALT Apresentado ao Usuário

```markdown
🛑 HALT: Aprovação de Plano

📍 **Contexto:**
Você solicitou a análise do edital "PMSP-Videomonitoramento-2025-001.pdf".
Fase STRUCTURE concluída. Plano de execução está pronto.

📊 **O Que Precisa de Decisão:**
Aprovar o plano de execução antes de iniciar a análise.

📂 **Evidências:**
- Edital analisado: 345 páginas
- Requisitos técnicos identificados: 47
- Tempo estimado: 15-20 minutos
- Agentes necessários:
  • Document Structurer (estruturação)
  • Technical Analyst (análise técnica)
- Checkpoints HALT planejados: 3
  1. Após estruturação (CSV gerado)
  2. Após análise técnica (relatório gerado)
  3. Antes de entrega final

🤔 **Opções Disponíveis:**

**Opção A:** Aprovar e executar
→ Consequência: Iniciar análise conforme plano. Você será notificado em cada checkpoint.

**Opção B:** Ajustar plano
→ Consequência: Você fornece modificações desejadas (ex: adicionar agente, mudar ordem, etc.). Revisarei o plano e re-apresentarei.

**Opção C:** Cancelar análise
→ Consequência: Interromper workflow e descartar plano. Nenhuma análise será realizada.

⏸️ **Aguardando sua decisão: [A/B/C]**
```

### Resposta do Usuário

```
Usuário: A
```

### Código de Execução

```python
def example_1_approval_halt():
    """
    HALT after STRUCTURE phase for plan approval
    """
    # 1. STRUCTURE phase concluída
    plan = execute_structure_phase({
        "task": "Analisar edital PMSP-Videomonitoramento-2025-001.pdf",
        "edital_path": "data/uploads/PMSP-2025-001.pdf"
    })

    log_info("STRUCTURE", f"Plan created with {len(plan['steps'])} steps")
    save_yaml(plan, "data/state/plan_001.yaml")

    # 2. Preparar HALT de aprovação
    halt_message = f"""
🛑 HALT: Aprovação de Plano

📍 **Contexto:**
Você solicitou a análise do edital "{plan['task']['edital_name']}".
Fase STRUCTURE concluída. Plano de execução está pronto.

📊 **O Que Precisa de Decisão:**
Aprovar o plano de execução antes de iniciar a análise.

📂 **Evidências:**
- Edital analisado: {plan['metadata']['edital_pages']} páginas
- Requisitos técnicos identificados: {plan['metadata']['requirements_count']}
- Tempo estimado: {plan['metadata']['estimated_duration']}
- Agentes necessários: {', '.join(plan['metadata']['agents_required'])}
- Checkpoints HALT planejados: {len(plan['halt_points'])}

🤔 **Opções Disponíveis:**

**Opção A:** Aprovar e executar
→ Consequência: Iniciar análise conforme plano.

**Opção B:** Ajustar plano
→ Consequência: Você fornece modificações, revisarei e re-apresentarei.

**Opção C:** Cancelar análise
→ Consequência: Interromper workflow e descartar plano.

⏸️ **Aguardando sua decisão: [A/B/C]**
    """

    # 3. Apresentar HALT e aguardar
    log_info("HALT", "Presenting plan approval HALT")
    user_choice = present_halt_and_wait(halt_message, options=["A", "B", "C"])

    # 4. Processar resposta
    if user_choice == "A":
        log_info("HALT", "User approved plan. Proceeding to EXECUTE.")
        return execute_workflow(plan)

    elif user_choice == "B":
        log_info("HALT", "User requested adjustments.")
        adjustments = get_user_adjustments()
        revised_plan = revise_plan(plan, adjustments)

        # Re-HALT com plano revisado
        return example_1_approval_halt_revised(revised_plan)

    elif user_choice == "C":
        log_info("HALT", "User cancelled workflow.")
        return {"status": "CANCELLED", "reason": "User chose to cancel"}
```

### Logs Gerados

```
[2025-11-06T16:30:00Z] INFO orchestrator STRUCTURE Plan created with 5 steps
[2025-11-06T16:30:01Z] INFO orchestrator HALT Presenting plan approval HALT
[2025-11-06T16:30:15Z] INFO orchestrator HALT User chose: A
[2025-11-06T16:30:15Z] INFO orchestrator HALT User approved plan. Proceeding to EXECUTE.
[2025-11-06T16:30:15Z] INFO orchestrator EXECUTE Starting step 1: Extract text from PDF
```

---

## Exemplo 2: HALT de Ambiguidade (Durante EXECUTE)

**Contexto:** Durante análise técnica, encontrado requisito ambíguo que não especifica protocolo.

### HALT Apresentado ao Usuário

```markdown
🛑 HALT: Ambiguidade Detectada

📍 **Contexto:**
Análise técnica em andamento (Etapa 3/5).
Agente: Technical Analyst

📊 **O Que Precisa de Decisão:**
Requisito #8 não especifica qual protocolo de câmeras IP deve ser suportado.

📂 **Evidências:**
- Requisito original: "O sistema deve suportar câmeras IP compatíveis com a rede"
- Localização: Página 47, Seção 3.2 "Requisitos Técnicos de Hardware"
- Protocolos possíveis:
  • ONVIF (Open Network Video Interface Forum - padrão da indústria)
  • RTSP (Real Time Streaming Protocol)
  • Ambos

⚠️ **Não posso assumir qual protocolo sem confirmação** (Princípio Anti-Alucinação)

🤔 **Opções Disponíveis:**

**Opção A:** ONVIF (protocolo padrão da indústria)
→ Consequência: Marcar requisito como "Câmeras IP com suporte ONVIF obrigatório"

**Opção B:** RTSP (protocolo de streaming)
→ Consequência: Marcar requisito como "Câmeras IP com suporte RTSP obrigatório"

**Opção C:** Ambos os protocolos
→ Consequência: Marcar requisito como "Câmeras IP com suporte ONVIF E RTSP obrigatórios"

**Opção D:** Você fornece o protocolo correto
→ Consequência: Usar o protocolo específico que você indicar

⏸️ **Aguardando sua decisão: [A/B/C/D]**
```

### Resposta do Usuário

```
Usuário: C
```

### Código de Execução

```python
def example_2_ambiguity_halt():
    """
    HALT during EXECUTE when ambiguity is detected
    """
    # Durante análise de requisito
    requirement = {
        "id": 8,
        "description": "O sistema deve suportar câmeras IP compatíveis com a rede",
        "page": 47,
        "section": "3.2 Requisitos Técnicos de Hardware"
    }

    # Detectar ambiguidade
    if "câmeras IP" in requirement['description'] and "protocolo" not in requirement['description']:
        log_warning("EXECUTE", f"Ambiguity detected in requirement #{requirement['id']}")

        # Preparar HALT de ambiguidade
        halt_message = f"""
🛑 HALT: Ambiguidade Detectada

📍 **Contexto:**
Análise técnica em andamento (Etapa 3/5).
Agente: Technical Analyst

📊 **O Que Precisa de Decisão:**
Requisito #{requirement['id']} não especifica qual protocolo de câmeras IP deve ser suportado.

📂 **Evidências:**
- Requisito original: "{requirement['description']}"
- Localização: Página {requirement['page']}, Seção {requirement['section']}
- Protocolos possíveis:
  • ONVIF (Open Network Video Interface Forum - padrão da indústria)
  • RTSP (Real Time Streaming Protocol)
  • Ambos

⚠️ **Não posso assumir qual protocolo sem confirmação** (Princípio Anti-Alucinação)

🤔 **Opções Disponíveis:**

**Opção A:** ONVIF (protocolo padrão da indústria)
→ Consequência: Marcar requisito como "Câmeras IP com suporte ONVIF obrigatório"

**Opção B:** RTSP (protocolo de streaming)
→ Consequência: Marcar requisito como "Câmeras IP com suporte RTSP obrigatório"

**Opção C:** Ambos os protocolos
→ Consequência: Marcar requisito como "Câmeras IP com suporte ONVIF E RTSP obrigatórios"

**Opção D:** Você fornece o protocolo correto
→ Consequência: Usar o protocolo específico que você indicar

⏸️ **Aguardando sua decisão: [A/B/C/D]**
        """

        # Apresentar HALT
        log_info("HALT", f"Presenting ambiguity HALT for requirement #{requirement['id']}")
        user_choice = present_halt_and_wait(halt_message, options=["A", "B", "C", "D"])

        # Processar resposta
        if user_choice == "A":
            requirement['protocol'] = "ONVIF"
            requirement['description_clarified'] = f"{requirement['description']} (Protocolo ONVIF)"
            log_info("HALT", "User clarified: ONVIF")

        elif user_choice == "B":
            requirement['protocol'] = "RTSP"
            requirement['description_clarified'] = f"{requirement['description']} (Protocolo RTSP)"
            log_info("HALT", "User clarified: RTSP")

        elif user_choice == "C":
            requirement['protocol'] = "ONVIF+RTSP"
            requirement['description_clarified'] = f"{requirement['description']} (Protocolos ONVIF e RTSP)"
            log_info("HALT", "User clarified: Both ONVIF and RTSP")

        elif user_choice == "D":
            custom_protocol = get_user_custom_input("Digite o protocolo correto:")
            requirement['protocol'] = custom_protocol
            requirement['description_clarified'] = f"{requirement['description']} (Protocolo {custom_protocol})"
            log_info("HALT", f"User provided custom protocol: {custom_protocol}")

        # Retomar análise com requisito esclarecido
        log_info("EXECUTE", f"Resuming analysis with clarified requirement #{requirement['id']}")
        return continue_analysis(requirement)
```

### Logs Gerados

```
[2025-11-06T16:35:00Z] INFO technical_analyst EXECUTE Analyzing requirement #8
[2025-11-06T16:35:01Z] WARNING technical_analyst EXECUTE Ambiguity detected in requirement #8
[2025-11-06T16:35:01Z] INFO technical_analyst HALT Presenting ambiguity HALT for requirement #8
[2025-11-06T16:35:23Z] INFO technical_analyst HALT User chose: C
[2025-11-06T16:35:23Z] INFO technical_analyst HALT User clarified: Both ONVIF and RTSP
[2025-11-06T16:35:23Z] INFO technical_analyst EXECUTE Resuming analysis with clarified requirement #8
[2025-11-06T16:35:24Z] INFO technical_analyst EXECUTE Requirement #8 updated: "Câmeras IP com suporte ONVIF e RTSP obrigatórios"
```

---

## Exemplo 3: HALT de Escalação (Após LOOP Falhar)

**Contexto:** LOOP tentou corrigir 3 vezes, mas inconsistência técnica persiste. Precisa de intervenção humana.

### HALT Apresentado ao Usuário

```markdown
🛑 HALT: Escalação - Problema Não Resolvido

📍 **Contexto:**
Fase LOOP concluída após 3 tentativas de correção.
Problema técnico persiste e não pode ser resolvido automaticamente.

📊 **O Que Precisa de Decisão:**
Como resolver inconsistência técnica entre dois requisitos conflitantes.

📂 **Evidências:**

**Problema detectado:**
- Item falhado: AT-07 "Especificações técnicas são consistentes entre si"
- Conflito identificado:
  • Requisito #12 (Página 23): "Sistema deve suportar câmeras com resolução 4K (3840x2160)"
  • Requisito #34 (Página 67): "Gravação máxima suportada: 1080p (1920x1080)"
  • Incompatibilidade: Não é possível gravar vídeo 4K em sistema limitado a 1080p

**Tentativas de correção automática:**
- Iteração 1: Tentei marcar requisito #34 como "erro de digitação" → INSPECT falhou (sem evidência de erro)
- Iteração 2: Tentei interpretar #12 como "visualização 4K" vs #34 como "gravação 1080p" → INSPECT falhou (requisito #12 específica "gravação 4K")
- Iteração 3: Tentei marcar ambos como "revisão necessária" → INSPECT falhou (modo Strict não permite itens pendentes)

⚠️ **Por que não posso corrigir automaticamente:**
Este conflito requer conhecimento do contexto do edital e do projeto para decidir qual especificação é a correta. Não posso assumir ou "adivinhar" (Princípio Anti-Alucinação).

🤔 **Opções Disponíveis:**

**Opção A:** Você fornece a correção
→ Consequência: Aplicar sua correção e re-executar INSPECT

  **Sub-opções:**
  **A1)** Câmeras 4K está correto
       → Corrigir requisito #34 para "Gravação máxima: 4K"

  **A2)** Gravação 1080p está correto
       → Corrigir requisito #12 para "Câmeras com resolução 1080p"

  **A3)** Ambos estão errados
       → Você fornece a especificação técnica correta

**Opção B:** Marcar como "PENDING_REVIEW" e continuar
→ Consequência: Ambos os requisitos (#12 e #34) serão marcados como "PENDING_HUMAN_REVIEW". Análise continuará com outros requisitos. Relatório final incluirá seção "Inconsistências Detectadas".

**Opção C:** Cancelar análise
→ Consequência: Interromper workflow. Você poderá revisar o edital e reiniciar a análise posteriormente.

⏸️ **Aguardando sua decisão: [A/B/C]**

(Se escolher A, especifique: [A1/A2/A3])
```

### Resposta do Usuário

```
Usuário: A1
```

### Código de Execução

```python
def example_3_escalation_halt():
    """
    HALT after LOOP reaches max iterations without resolving issue
    """
    MAX_ITERATIONS = 3

    # Após 3 iterações de LOOP
    loop_result = {
        "status": "FAILED",
        "iterations_used": MAX_ITERATIONS,
        "remaining_failures": [
            {
                "item_id": "AT-07",
                "question": "Especificações técnicas são consistentes entre si?",
                "reason": "Requisitos #12 e #34 conflitantes (4K vs 1080p)",
                "requires_human_input": True
            }
        ]
    }

    log_error("LOOP", f"Failed to correct after {MAX_ITERATIONS} iterations")
    log_info("LOOP", "Escalating to user via HALT")

    # Preparar HALT de escalação
    halt_message = """
🛑 HALT: Escalação - Problema Não Resolvido

📍 **Contexto:**
Fase LOOP concluída após 3 tentativas de correção.
Problema técnico persiste e não pode ser resolvido automaticamente.

📊 **O Que Precisa de Decisão:**
Como resolver inconsistência técnica entre dois requisitos conflitantes.

📂 **Evidências:**

**Problema detectado:**
- Item falhado: AT-07 "Especificações técnicas são consistentes entre si"
- Conflito identificado:
  • Requisito #12 (Página 23): "Sistema deve suportar câmeras com resolução 4K"
  • Requisito #34 (Página 67): "Gravação máxima suportada: 1080p"
  • Incompatibilidade: Não é possível gravar vídeo 4K em sistema limitado a 1080p

**Tentativas de correção automática:**
- Iteração 1: Marcado como erro de digitação → INSPECT falhou
- Iteração 2: Interpretado como visualização vs gravação → INSPECT falhou
- Iteração 3: Marcado para revisão → INSPECT falhou (Modo Strict)

⚠️ **Por que não posso corrigir:**
Requer conhecimento do contexto para decidir qual especificação é correta.

🤔 **Opções Disponíveis:**

**Opção A:** Você fornece a correção
  A1) Câmeras 4K está correto → Corrigir requisito #34 para "4K"
  A2) Gravação 1080p está correto → Corrigir requisito #12 para "1080p"
  A3) Ambos estão errados → Você fornece especificação correta

**Opção B:** Marcar como "PENDING_REVIEW" e continuar

**Opção C:** Cancelar análise

⏸️ **Aguardando sua decisão: [A/B/C]**
    """

    # Apresentar HALT
    log_info("HALT", "Presenting escalation HALT")
    user_choice = present_halt_and_wait(halt_message, options=["A", "B", "C", "A1", "A2", "A3"])

    # Processar resposta
    if user_choice in ["A", "A1"]:
        log_info("HALT", "User chose A1: Cameras 4K is correct")

        # Aplicar correção
        csv_data = load_csv("data/state/requirements_corrected.csv")

        # Corrigir requisito #34
        for row in csv_data:
            if row['ID'] == 34:
                row['Descrição'] = "Gravação máxima suportada: 4K (3840x2160)"
                log_info("HALT", f"Corrected requirement #34: {row['Descrição']}")

        save_csv(csv_data, "data/state/requirements_corrected.csv")

        # Re-executar INSPECT
        log_info("HALT", "Re-running INSPECT with user correction")
        inspect_result = run_inspect_phase(csv_data, "technical_analyst")

        if inspect_result['overall_status'] == "PASS":
            log_info("HALT", "✓ INSPECT passed after user correction")
            return {"status": "SUCCESS_WITH_USER_INTERVENTION", "next_phase": "VALIDATE"}
        else:
            log_error("HALT", "✗ INSPECT still failing after user correction")
            return {"status": "FAILED", "reason": "Correction did not resolve issue"}

    elif user_choice in ["A2"]:
        log_info("HALT", "User chose A2: Recording 1080p is correct")
        # Similar logic for A2...

    elif user_choice in ["A3"]:
        log_info("HALT", "User chose A3: Both are wrong")
        custom_spec = get_user_custom_input("Forneça a especificação técnica correta:")
        # Apply custom specification...

    elif user_choice == "B":
        log_info("HALT", "User chose B: Mark as PENDING_REVIEW")

        # Marcar requisitos como pendentes
        csv_data = load_csv("data/state/requirements_corrected.csv")
        for row in csv_data:
            if row['ID'] in [12, 34]:
                row['Status'] = "PENDING_HUMAN_REVIEW"
                row['Observação'] = "Inconsistência técnica detectada - Requer revisão manual"

        save_csv(csv_data, "data/state/requirements_pending_review.csv")

        log_info("HALT", "Requirements #12 and #34 marked as PENDING_REVIEW")
        return {"status": "SUCCESS_WITH_PENDING_ITEMS", "next_phase": "VALIDATE"}

    elif user_choice == "C":
        log_info("HALT", "User chose C: Cancel analysis")
        return {"status": "CANCELLED", "reason": "User cancelled due to unresolved conflict"}
```

### Logs Gerados

```
[2025-11-06T16:40:00Z] ERROR technical_analyst LOOP Failed to correct after 3 iterations
[2025-11-06T16:40:00Z] INFO technical_analyst LOOP Escalating to user via HALT
[2025-11-06T16:40:01Z] INFO technical_analyst HALT Presenting escalation HALT
[2025-11-06T16:40:45Z] INFO technical_analyst HALT User chose: A1
[2025-11-06T16:40:45Z] INFO technical_analyst HALT User chose A1: Cameras 4K is correct
[2025-11-06T16:40:46Z] INFO technical_analyst HALT Corrected requirement #34: Gravação máxima suportada: 4K (3840x2160)
[2025-11-06T16:40:46Z] INFO technical_analyst HALT Re-running INSPECT with user correction
[2025-11-06T16:40:48Z] INFO technical_analyst INSPECT ✓ All 16 items passed
[2025-11-06T16:40:48Z] INFO technical_analyst HALT ✓ INSPECT passed after user correction
[2025-11-06T16:40:48Z] INFO technical_analyst HALT Proceeding to VALIDATE phase
```

---

## Comparação dos Exemplos

| Exemplo | Tipo HALT | Trigger | User Choice | Resultado |
|---------|-----------|---------|-------------|-----------|
| 1 | Aprovação | Após STRUCTURE | A (Aprovar) | Workflow continua |
| 2 | Ambiguidade | Durante EXECUTE | C (Ambos protocolos) | Requisito esclarecido |
| 3 | Escalação | Após 3 LOOPs | A1 (4K correto) | Correção aplicada, INSPECT passa |

---

## Lições dos Exemplos

### ✅ Boas Práticas Demonstradas

1. **Contexto claro:** Todos os exemplos explicam onde está no workflow
2. **Evidências suficientes:** Usuário tem informação para decidir
3. **Opções bem definidas:** Cada opção tem consequência clara
4. **Formato consistente:** Todos seguem o mesmo template
5. **Logging completo:** Cada decisão é registrada

### 📐 Padrões de Uso

**HALT de Aprovação:**
- Use após etapas macro (STRUCTURE, grandes operações)
- Sempre inclua: o que foi feito, o que será feito, tempo estimado

**HALT de Ambiguidade:**
- Use quando há múltiplas interpretações válidas
- NUNCA assuma - sempre pergunte
- Ofereça interpretações comuns + opção "outro"

**HALT de Escalação:**
- Use após N tentativas falhadas (geralmente 3)
- Explique o que tentou e por que falhou
- Ofereça alternativas (correção, pular, cancelar)

---

## Exemplo 4: HALT Aninhado (Múltiplos Níveis)

**Situação:** Usuário escolhe "Ajustar plano" (Opção B) no primeiro HALT, gerando um segundo HALT com plano revisado.

### HALT 1 (Inicial)

```markdown
🛑 HALT: Aprovação de Plano

[Mesmo conteúdo do Exemplo 1]

⏸️ **Aguardando sua decisão: [A/B/C]**
```

**Usuário:** B

### HALT 2 (Plano Revisado)

```markdown
🛑 HALT: Aprovação de Plano Revisado

📍 **Contexto:**
Você solicitou ajustes ao plano original.
Suas modificações foram aplicadas. Plano revisado está pronto.

📊 **Modificações Aplicadas:**
✓ Adicionado agente "Quality Assurance" (validação extra)
✓ Tempo estimado atualizado: 20-25 minutos (era 15-20)
✓ Checkpoint adicional: Após validação de qualidade

📂 **Plano Revisado:**
- Edital: PMSP-2025-001.pdf (345 páginas)
- Requisitos: 47
- Tempo estimado: 20-25 minutos
- Agentes: Document Structurer, Technical Analyst, Quality Assurance
- Checkpoints: 4 (era 3)

🤔 **Opções Disponíveis:**

**Opção A:** Aprovar plano revisado
→ Consequência: Iniciar análise com as modificações aplicadas

**Opção B:** Ajustar novamente
→ Consequência: Fornecer novos ajustes

**Opção C:** Cancelar análise
→ Consequência: Descartar plano e interromper

⏸️ **Aguardando sua decisão: [A/B/C]**
```

**Usuário:** A

### Código

```python
def example_4_nested_halt():
    """
    HALT with revision cycle (user requests adjustments)
    """
    # HALT 1
    plan = create_initial_plan()
    user_choice = HALT_approval(plan)

    if user_choice == "B":
        log_info("HALT", "User requested plan adjustments")

        # Obter ajustes
        adjustments = get_user_adjustments()
        # Ex: {"add_agent": "Quality Assurance", "add_checkpoint": "After QA validation"}

        # Revisar plano
        revised_plan = apply_adjustments(plan, adjustments)

        # HALT 2 (plano revisado)
        user_choice_2 = HALT_approval_revised(revised_plan, adjustments)

        if user_choice_2 == "A":
            return execute_workflow(revised_plan)
        elif user_choice_2 == "B":
            # Pode continuar em loop de revisões
            return example_4_nested_halt_level_3()
```

---

**Versão:** 1.0
**Criado em:** 06/11/2025
