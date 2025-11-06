# SHIELD Phase: EXECUTE (Execução)

**Versão:** 1.0
**Fase:** E - EXECUTE
**Responsável:** 100% IA (mas decisão de iniciar é do Humano via HALT)
**Modo Obrigatório:** Strict

---

## 📖 Visão Geral

A fase **EXECUTE** é onde o trabalho real acontece. Após o planeamento (STRUCTURE) e aprovação (HALT), o agente executa cada etapa do plano de forma controlada, com logging completo e tratamento de erros.

**Princípio Fundamental:** "Execute apenas o que foi planejado e aprovado. Registre tudo. Nunca assuma."

---

## 🎯 Objetivos da Fase EXECUTE

1. **Executar** a etapa conforme definido no plano
2. **Registrar** logs de todas as ações significativas
3. **Tratar** erros de forma apropriada
4. **Reportar** resultado (sucesso, falha, saída)
5. **Preservar** evidências para auditoria
6. **Garantir** execução determinística (mesmos inputs → mesmos outputs)

---

## 📋 Quando Usar

- ✅ Após aprovação do plano (STRUCTURE → HALT → aprovado)
- ✅ Para executar CADA etapa do plano sequencialmente
- ✅ Antes de qualquer fase [INSPECT](inspect.md) (Execute → Inspect)

---

## 🔧 Como Executar a Fase EXECUTE

### Entrada (Input)

- **Plano aprovado** (de STRUCTURE, salvo em `data/state/plan_[id].yaml`)
- **Etapa específica** a executar (ex: Step 2 de 6)
- **Contexto da etapa** (inputs, dependências)

### Processo

#### 1. Carregar Contexto da Etapa

**Antes de iniciar, valide:**

```yaml
pre_execution_checklist:
  - [ ] Plano foi carregado corretamente
  - [ ] Etapa a executar está identificada (Step ID)
  - [ ] Todas as dependências da etapa foram concluídas
  - [ ] Inputs necessários estão disponíveis
  - [ ] Aprovação do usuário foi obtida (se necessário)
```

**Exemplo:**
```python
def load_step_context(plan_id, step_id):
    # Carregar plano
    plan = load_yaml(f"data/state/plan_{plan_id}.yaml")

    # Encontrar etapa
    step = plan['steps'][step_id - 1]  # IDs começam em 1

    # Validar dependências
    for dep_id in step['dependencies']:
        if not is_step_completed(plan_id, dep_id):
            raise DependencyNotMetError(f"Step {dep_id} not completed")

    return step
```

---

#### 2. Iniciar Logging

**Todo EXECUTE deve logar:**

```python
log_entry = {
    "timestamp": "2025-11-06T16:00:00Z",
    "analysis_id": "ANA-20251106-001",
    "step_id": 2,
    "step_name": "Extrair texto do PDF",
    "status": "STARTED",
    "agent": "document_structurer"
}

append_to_log(log_entry)
```

**Localização do log:**
```
data/analyses/[analysis_id]/logs.txt
```

**Formato de log:**
```
[ISO8601 timestamp] [LEVEL] [Agent] [Step ID] Message
```

**Exemplo:**
```
[2025-11-06T16:00:00Z] INFO document_structurer Step-2 Starting: Extrair texto do PDF
[2025-11-06T16:00:01Z] DEBUG document_structurer Step-2 Loading file: edital.pdf
[2025-11-06T16:00:15Z] INFO document_structurer Step-2 Extracted 12,543 characters
[2025-11-06T16:00:15Z] INFO document_structurer Step-2 Completed successfully
```

---

#### 3. Executar a Tarefa

**Regras de Execução:**

1. **Nunca assumir informações não fornecidas**
   - ❌ "Provavelmente o requisito quer dizer X"
   - ✅ "Requisito explicitamente menciona X"

2. **Se encontrar ambiguidade, pausar (HALT)**
   - Não adivinhar
   - Não "interpretar criativamente"
   - Solicitar esclarecimento ao usuário

3. **Registrar cada ação significativa**
   - Abertura de arquivos
   - Chamadas a APIs externas
   - Decisões tomadas
   - Resultados intermediários

4. **Manter evidências**
   - Salvar outputs intermediários se útil para debug
   - Preservar dados originais (não sobrescrever)
   - Calcular checksums quando apropriado

**Exemplo de Execução (Estruturação de PDF):**

```python
def execute_pdf_extraction(step_context, analysis_id):
    """
    Execute Step 2: Extract text from PDF
    """
    # Log início
    log_info(f"Step-2", "Starting: Extract text from PDF")

    try:
        # 1. Validar arquivo existe
        pdf_path = step_context['input_file']
        if not os.path.exists(pdf_path):
            log_error(f"Step-2", f"File not found: {pdf_path}")
            return ExecutionResult(
                status="FAILED",
                error="FileNotFoundError",
                message=f"Input file not found: {pdf_path}"
            )

        log_debug(f"Step-2", f"Loading file: {pdf_path}")

        # 2. Extrair texto
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            log_info(f"Step-2", f"PDF has {total_pages} pages")

            text = ""
            for page_num in range(total_pages):
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text

                # Log progresso a cada 10 páginas
                if (page_num + 1) % 10 == 0:
                    log_debug(f"Step-2", f"Processed {page_num + 1}/{total_pages} pages")

        # 3. Validar extração
        char_count = len(text)
        log_info(f"Step-2", f"Extracted {char_count} characters")

        if char_count < 100:
            log_warning(f"Step-2", "Extracted text is very short (< 100 chars)")

        # 4. Salvar resultado intermediário
        output_path = f"data/analyses/{analysis_id}/extracted_text.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        log_info(f"Step-2", f"Saved extracted text to: {output_path}")

        # 5. Retornar resultado
        return ExecutionResult(
            status="SUCCESS",
            output={
                "text": text,
                "char_count": char_count,
                "page_count": total_pages,
                "output_file": output_path
            },
            duration="15s"
        )

    except PyPDF2.errors.PdfReadError as e:
        log_error(f"Step-2", f"PDF parsing error: {str(e)}")
        return ExecutionResult(
            status="FAILED",
            error="PdfReadError",
            message=str(e)
        )

    except Exception as e:
        log_error(f"Step-2", f"Unexpected error: {str(e)}")
        return ExecutionResult(
            status="FAILED",
            error=type(e).__name__,
            message=str(e)
        )
```

---

#### 4. Tratar Erros

**Estratégia de Error Handling:**

**Erros Recuperáveis (Retry):**
- Timeout de rede
- API temporariamente indisponível
- Arquivo temporariamente locked

**Protocolo de Retry:**
```python
def execute_with_retry(func, max_attempts=3, backoff_seconds=2):
    for attempt in range(1, max_attempts + 1):
        try:
            result = func()
            return result
        except RecoverableError as e:
            if attempt < max_attempts:
                log_warning(f"Attempt {attempt} failed: {e}. Retrying in {backoff_seconds}s...")
                time.sleep(backoff_seconds)
                backoff_seconds *= 2  # Exponential backoff
            else:
                log_error(f"All {max_attempts} attempts failed")
                raise
```

**Erros Não-Recuperáveis (Halt):**
- Arquivo corrompido
- Credenciais inválidas
- Input em formato incorreto

**Ação:** HALT e solicitar intervenção do usuário

```python
def handle_unrecoverable_error(error, step_id):
    log_error(f"Step-{step_id}", f"Unrecoverable error: {error}")

    # Pausar execução
    halt_message = f"""
    ❌ Erro Irrecuperável na Etapa {step_id}

    Tipo: {type(error).__name__}
    Mensagem: {error}

    Opções:
    1. Fornecer input alternativo
    2. Pular esta etapa (marcar para revisão manual)
    3. Cancelar análise

    Sua escolha [1-3]:
    """

    return halt_and_wait_for_user(halt_message)
```

---

#### 5. Gerar Resultado Estruturado

**Todo EXECUTE deve retornar um resultado estruturado:**

```python
class ExecutionResult:
    status: str  # "SUCCESS", "FAILED", "PARTIAL"
    output: dict  # Dados de saída da etapa
    error: str = None  # Tipo de erro (se FAILED)
    message: str = None  # Mensagem descritiva
    duration: str = None  # Tempo de execução
    warnings: list = []  # Avisos não-críticos
    evidence: dict = {}  # Evidências para auditoria
```

**Exemplo de Resultado de Sucesso:**
```yaml
execution_result:
  status: "SUCCESS"
  output:
    text: "[Texto extraído...]"
    char_count: 12543
    page_count: 47
    output_file: "data/analyses/ANA-001/extracted_text.txt"
  duration: "15s"
  warnings:
    - "Página 23 tem formatação não-padrão"
  evidence:
    checksum: "a3f5b8c..."
    extraction_method: "PyPDF2"
```

**Exemplo de Resultado de Falha:**
```yaml
execution_result:
  status: "FAILED"
  error: "PdfReadError"
  message: "PDF está protegido por senha"
  duration: "2s"
  evidence:
    attempted_file: "edital.pdf"
    error_timestamp: "2025-11-06T16:00:02Z"
```

---

#### 6. Atualizar Estado do Plano

**Após execução, marcar etapa como concluída:**

```python
def update_plan_status(plan_id, step_id, result):
    plan = load_yaml(f"data/state/plan_{plan_id}.yaml")

    # Adicionar resultado ao plano
    if 'execution_results' not in plan:
        plan['execution_results'] = {}

    plan['execution_results'][step_id] = {
        "status": result.status,
        "completed_at": datetime.now().isoformat(),
        "duration": result.duration,
        "output_summary": summarize(result.output)
    }

    save_yaml(f"data/state/plan_{plan_id}.yaml", plan)
```

---

### Saída (Output)

1. **Resultado estruturado** (ExecutionResult)
2. **Logs completos** em `data/analyses/[id]/logs.txt`
3. **Plano atualizado** em `data/state/plan_[id].yaml`
4. **Artefatos gerados** (arquivos, CSVs, etc.)

---

## ✅ Checklist de Qualidade da Execução

Antes de prosseguir para INSPECT, valide:

- [ ] **Completude:** A etapa foi totalmente executada (não parcial)?
- [ ] **Logging:** Todas as ações significativas foram registradas?
- [ ] **Evidências:** Artefatos gerados estão salvos?
- [ ] **Error Handling:** Erros foram tratados apropriadamente?
- [ ] **Determinismo:** A execução foi determinística (reproduzível)?
- [ ] **Plano Atualizado:** Status da etapa foi atualizado no plano?

---

## 📊 Exemplo Completo: Extração de Texto

**Contexto:**
- Etapa 2 do plano de "Estruturação de Edital"
- Input: `edital_prefeitura_sp.pdf`
- Output esperado: Texto extraído em arquivo `.txt`

**Fluxo de Execução:**

```
1. CARREGAR CONTEXTO
   ✅ Plano carregado
   ✅ Step 2 identificado
   ✅ Dependências (Step 1) concluídas
   ✅ Input file disponível

2. INICIAR LOGGING
   [2025-11-06T16:00:00Z] INFO Step-2 Starting: Extract text from PDF

3. EXECUTAR TAREFA
   [2025-11-06T16:00:01Z] DEBUG Loading file: edital_prefeitura_sp.pdf
   [2025-11-06T16:00:02Z] INFO PDF has 47 pages
   [2025-11-06T16:00:10Z] DEBUG Processed 10/47 pages
   [2025-11-06T16:00:15Z] INFO Extracted 12,543 characters
   [2025-11-06T16:00:15Z] INFO Saved to: extracted_text.txt

4. GERAR RESULTADO
   status: SUCCESS
   output:
     char_count: 12543
     page_count: 47
     output_file: "extracted_text.txt"

5. ATUALIZAR PLANO
   plan.execution_results[2].status = "SUCCESS"
   plan.execution_results[2].completed_at = "2025-11-06T16:00:15Z"

6. RETORNAR RESULTADO → Próxima fase: INSPECT
```

---

## 🎓 Boas Práticas

### DO ✅

- **Log tudo:** Início, progresso, fim, erros
- **Seja determinístico:** Mesmos inputs → mesmos outputs
- **Preserve dados:** Não sobrescreva inputs originais
- **Trate erros:** Try-catch apropriado
- **Valide inputs:** Antes de processar
- **Use checksums:** Para garantir integridade

### DON'T ❌

- **Assumir dados:** Se não está explícito, não existe
- **Silenciar erros:** Todo erro deve ser registrado
- **Pular validações:** Sempre valide antes de processar
- **Modificar inputs:** Preservar dados originais
- **Continuar após erro crítico:** HALT se não for recuperável
- **Logs verbosos demais:** Balance informação e ruído

---

## 🔄 Integração com Outras Fases

```
STRUCTURE → HALT (aprovação) → EXECUTE (você está aqui)
                                    ↓
                               [Execução completa]
                                    ↓
                                 INSPECT
                                    ↓
                            [Checklist passou?]
                                 ↓    ↓
                            Não ← LOOP
                                 ↓
                               Sim → VALIDATE
```

---

## 🛡️ Modo Strict: Garantias Obrigatórias

Em **Modo Strict** (NFR12), EXECUTE deve garantir:

1. **✅ Logging Completo:** Obrigatório, não opcional
2. **✅ Error Handling:** Todo error path tem tratamento
3. **✅ Determinismo:** Execução reproduzível
4. **✅ Evidências:** Todos os outputs salvos com checksums
5. **✅ Validação de Pré-condições:** Antes de executar
6. **✅ Validação de Pós-condições:** Após executar

---

## 📚 Referências

- **Princípios SHIELD:** `../OPERATING_PRINCIPLES.md`
- **Fase anterior:** `structure.md` (planeamento)
- **Próxima fase:** `inspect.md` (validação)
- **ADR-002:** Execução controlada e auditável

---

**Versão:** 1.0
**Criado em:** 06/11/2025
**Última atualização:** 06/11/2025
