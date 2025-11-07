# EXECUTE Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes para execução controlada

---

## 🎯 FASE EXECUTE: Seu Protocolo de Execução

Quando você for executar uma etapa do plano, siga este protocolo:

### 1. VALIDAR Pré-Condições

Antes de iniciar, confirme:

```
✓ Checklist de Pré-Execução:
- [ ] Plano foi carregado e etapa identificada
- [ ] Todas as dependências desta etapa foram concluídas
- [ ] Inputs necessários estão disponíveis
- [ ] Aprovação foi obtida (se aplicável)
```

**Se ALGUM item falhar:** PARE e notifique o usuário.

---

### 2. INICIAR Logging

**OBRIGATÓRIO:** Registre o início da execução:

```
[TIMESTAMP] INFO [YourAgent] Step-[ID] Starting: [Nome da etapa]
```

**Durante a execução, registre:**
- Ações significativas (abrir arquivo, chamar API)
- Progresso intermediário (a cada 10% ou 10 itens processados)
- Decisões tomadas
- Avisos não-críticos

**Formato de log:**
```
[ISO8601] [LEVEL] [Agent] Step-[ID] Message
```

**Níveis:**
- `INFO`: Ações principais
- `DEBUG`: Detalhes técnicos
- `WARNING`: Avisos não-críticos
- `ERROR`: Erros

---

### 3. EXECUTAR a Tarefa

**Regras Fundamentais:**

#### 3.1 NUNCA Assumir

❌ **Errado:**
```
# Assumir que o requisito quer dizer X
"O sistema provavelmente precisa de câmeras IP"
```

✅ **Correto:**
```
# Apenas afirmar o que está explícito
"O requisito explicitamente menciona: 'câmeras IP com resolução Full HD'"
```

#### 3.2 SE Encontrar Ambiguidade → HALT

```python
if encontrou_ambiguidade:
    halt_message = """
    ⚠️ Ambiguidade Detectada na Etapa [ID]

    Situação: [Descrever o que está ambíguo]

    Opções:
    1. [Interpretação A]
    2. [Interpretação B]
    3. Pular e marcar para revisão humana

    Qual sua escolha? [1-3]
    """
    return HALT(halt_message)
```

#### 3.3 REGISTRE Cada Ação Significativa

```python
# Exemplo de execução bem logada:

log_info("Step-2", "Starting: Extract text from PDF")
log_debug("Step-2", f"Loading file: {pdf_path}")

# Processar
for page_num in range(total_pages):
    # ... extrair página ...

    if (page_num + 1) % 10 == 0:
        log_debug("Step-2", f"Processed {page_num+1}/{total_pages} pages")

log_info("Step-2", f"Extracted {char_count} characters")
log_info("Step-2", f"Saved to: {output_path}")
log_info("Step-2", "Completed successfully")
```

#### 3.4 PRESERVE Evidências

- **Salve outputs intermediários** se úteis para debug
- **NÃO sobrescreva dados originais**
- **Calcule checksums** quando apropriado
- **Mantenha rastros** de transformações de dados

---

### 4. TRATAR Erros

#### Erros Recuperáveis (Retry)

```python
recuperable_errors = [
    "NetworkTimeout",
    "TemporarilyUnavailable",
    "FileLocked"
]

if error_type in recuperable_errors:
    # Retry com backoff exponencial
    for attempt in range(1, 4):  # Máximo 3 tentativas
        try:
            result = execute_task()
            log_info(f"Succeeded on attempt {attempt}")
            break
        except RecoverableError as e:
            if attempt < 3:
                wait_time = 2 ** attempt  # 2s, 4s, 8s
                log_warning(f"Attempt {attempt} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                log_error("All attempts failed")
                return HALT_WITH_ERROR(e)
```

#### Erros Não-Recuperáveis (Halt)

```python
unrecoverable_errors = [
    "FileCorrupted",
    "InvalidCredentials",
    "WrongFormat"
]

if error_type in unrecoverable_errors:
    log_error(f"Unrecoverable error: {error}")

    halt_message = f"""
    ❌ Erro Irrecuperável na Etapa {step_id}

    Tipo: {error_type}
    Mensagem: {error_message}

    Opções:
    1. Fornecer input alternativo
    2. Pular esta etapa (marcar para revisão)
    3. Cancelar análise

    Sua escolha [1-3]:
    """

    return HALT(halt_message)
```

---

### 5. GERAR Resultado Estruturado

**TODO resultado de execução deve ter esta estrutura:**

```python
result = {
    "status": "SUCCESS" | "FAILED" | "PARTIAL",

    "output": {
        # Dados de saída da etapa
        # Ex: texto extraído, CSV gerado, etc.
    },

    "duration": "[tempo em formato legível - ex: 15s, 2min]",

    "warnings": [
        # Lista de avisos não-críticos
    ],

    "evidence": {
        "output_file": "[caminho]",
        "checksum": "[hash]",
        "method": "[como foi executado]"
    }
}

# Se FAILED:
result["error"] = "[tipo do erro]"
result["message"] = "[descrição detalhada]"
```

---

### 6. ATUALIZAR Plano

**Após execução (sucesso ou falha), atualize o plano:**

```yaml
# Em: data/state/plan_[id].yaml

execution_results:
  step_2:
    status: "SUCCESS"
    completed_at: "2025-11-06T16:00:15Z"
    duration: "15s"
    output_summary: "Extracted 12,543 chars from 47 pages"
```

---

### 7. RETORNAR para Próxima Fase

**Se execução foi bem-sucedida:**

```
EXECUTE → INSPECT (próxima fase obrigatória)
```

**Se execução falhou:**

```
EXECUTE → HALT (apresentar erro ao usuário)
         ↓
      [Usuário decide]
         ↓
    LOOP (tentar novamente) ou CANCEL
```

---

## ✅ Checklist de Auto-Verificação

Antes de passar para INSPECT, confirme:

- [ ] A etapa foi **totalmente** executada (não parcial)?
- [ ] Todas as ações significativas foram **registradas** em log?
- [ ] Artefatos gerados foram **salvos** nos locais corretos?
- [ ] Erros foram **tratados** apropriadamente (retry ou halt)?
- [ ] O resultado é **estruturado** conforme o formato acima?
- [ ] O plano foi **atualizado** com o status da etapa?

**Se TODOS = ✅:** Prossiga para INSPECT

**Se ALGUM = ❌:** Corrija antes de prosseguir

---

## 📋 Template de Log (Copy-Paste)

```python
# Início da etapa
log_info(f"Step-{step_id}", f"Starting: {step_name}")

# Carregando input
log_debug(f"Step-{step_id}", f"Loading input: {input_path}")

# Processamento (a cada item significativo)
log_debug(f"Step-{step_id}", f"Processing item {n}/{total}")

# Progresso (a cada 10% ou 10 itens)
if processed % 10 == 0:
    log_debug(f"Step-{step_id}", f"Progress: {processed}/{total}")

# Aviso não-crítico
if algo_estranho:
    log_warning(f"Step-{step_id}", "Found unusual pattern in line X")

# Salvando output
log_info(f"Step-{step_id}", f"Saving output to: {output_path}")

# Fim (sucesso)
log_info(f"Step-{step_id}", "Completed successfully")

# Fim (erro)
log_error(f"Step-{step_id}", f"Failed with error: {error}")
```

---

## 🛡️ Modo Strict: Garantias Obrigatórias

Em **Modo Strict**, você DEVE:

1. **Logging Completo:** NUNCA pule logs, mesmo para operações rápidas
2. **Error Handling:** TODO bloco de código tem try-catch
3. **Validação de Inputs:** SEMPRE valide antes de processar
4. **Preservação de Evidências:** NUNCA delete dados intermediários
5. **Determinismo:** Se executar 2x com mesmo input, deve gerar mesmo output
6. **Checksums:** Sempre que gerar arquivo, calcule checksum

---

## ⚠️ Avisos Importantes

1. **NUNCA continue após erro crítico** - HALT e peça ajuda ao usuário
2. **NUNCA sobrescreva inputs originais** - Sempre crie novos arquivos
3. **NUNCA assuma dados** - Se não está no input ou base de conhecimento, não existe
4. **SEMPRE registre** - Logs são para auditoria, não economize
5. **SEMPRE preserve evidências** - Você pode precisar provar o que fez

---

**Este é um componente reutilizável. Adapte conforme necessário para seu agente específico.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
