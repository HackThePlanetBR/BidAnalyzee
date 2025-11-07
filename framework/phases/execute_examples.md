# EXECUTE Phase - Exemplos Práticos

**Versão:** 1.0

---

## Exemplo 1: Extração de Texto de PDF

**Contexto:** Etapa 2 do plano de estruturação de edital

**Input:** `edital.pdf` (47 páginas)
**Output:** Texto extraído em `extracted_text.txt`

### Código de Execução

```python
def execute_step_2_extract_pdf(analysis_id, pdf_path):
    """Execute Step 2: Extract text from PDF"""

    # 1. Validar pré-condições
    if not os.path.exists(pdf_path):
        log_error("Step-2", f"File not found: {pdf_path}")
        return {"status": "FAILED", "error": "FileNotFoundError"}

    # 2. Iniciar logging
    log_info("Step-2", "Starting: Extract text from PDF")
    log_debug("Step-2", f"Loading file: {pdf_path}")

    try:
        # 3. Executar tarefa
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            total_pages = len(pdf_reader.pages)
            log_info("Step-2", f"PDF has {total_pages} pages")

            text = ""
            for page_num in range(total_pages):
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text

                # Log progresso
                if (page_num + 1) % 10 == 0:
                    log_debug("Step-2", f"Processed {page_num+1}/{total_pages} pages")

        char_count = len(text)
        log_info("Step-2", f"Extracted {char_count} characters")

        # 4. Salvar output
        output_path = f"data/analyses/{analysis_id}/extracted_text.txt"
        with open(output_path, 'w') as f:
            f.write(text)
        log_info("Step-2", f"Saved to: {output_path}")

        # 5. Gerar resultado
        log_info("Step-2", "Completed successfully")
        return {
            "status": "SUCCESS",
            "output": {
                "text": text,
                "char_count": char_count,
                "page_count": total_pages,
                "output_file": output_path
            },
            "duration": "15s"
        }

    except Exception as e:
        # 4. Tratar erro
        log_error("Step-2", f"Error: {str(e)}")
        return {
            "status": "FAILED",
            "error": type(e).__name__,
            "message": str(e)
        }
```

### Logs Gerados

```
[2025-11-06T16:00:00Z] INFO document_structurer Step-2 Starting: Extract text from PDF
[2025-11-06T16:00:01Z] DEBUG document_structurer Step-2 Loading file: edital.pdf
[2025-11-06T16:00:02Z] INFO document_structurer Step-2 PDF has 47 pages
[2025-11-06T16:00:10Z] DEBUG document_structurer Step-2 Processed 10/47 pages
[2025-11-06T16:00:15Z] INFO document_structurer Step-2 Extracted 12,543 characters
[2025-11-06T16:00:15Z] INFO document_structurer Step-2 Saved to: extracted_text.txt
[2025-11-06T16:00:15Z] INFO document_structurer Step-2 Completed successfully
```

---

## Exemplo 2: Chamada a API Externa (com Retry)

**Contexto:** Consulta ao microsserviço n8n

```python
def execute_step_query_n8n(requirement_text, max_retries=3):
    """Execute query to n8n RAG service with retry logic"""

    log_info("Step-4", f"Querying n8n for: {requirement_text[:50]}...")

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                os.getenv("N8N_QUERY_SERVICE_URL"),
                json={"query": requirement_text, "top_k": 20},
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            log_info("Step-4", f"Received {len(result['results'])} results")
            return {"status": "SUCCESS", "output": result}

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                wait_time = 2 ** attempt
                log_warning("Step-4", f"Timeout on attempt {attempt}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                log_error("Step-4", "All retry attempts failed")
                return HALT_WITH_ERROR("n8n service timeout")

        except requests.exceptions.RequestException as e:
            log_error("Step-4", f"Request error: {e}")
            return HALT_WITH_ERROR(f"n8n service error: {e}")
```

---

## Exemplo 3: Tratamento de Ambiguidade (HALT)

```python
def execute_step_classify_requirement(requirement_text):
    """Classify requirement type, halting if ambiguous"""

    log_info("Step-3", f"Classifying: {requirement_text[:50]}...")

    # Tentativa de classificação
    if "temperatura" in requirement_text.lower():
        if "operação" in requirement_text.lower():
            type = "Técnico"
        elif any(word in requirement_text.lower() for word in ["armazenamento", "storage"]):
            type = "Operacional"
        else:
            # Ambíguo - pausar para decisão humana
            log_warning("Step-3", "Ambiguous requirement type detected")

            halt_message = f"""
            ⚠️ Classificação Ambígua - Etapa 3

            Requisito: "{requirement_text}"

            O requisito menciona "temperatura", mas não está claro se é:
            1. Técnico (temperatura de operação do equipamento)
            2. Operacional (temperatura ambiente do local)
            3. Outro

            Qual classificação você escolhe? [1-3]
            """

            return HALT(halt_message)

    # ... outras classificações ...

    log_info("Step-3", f"Classified as: {type}")
    return {"status": "SUCCESS", "output": {"type": type}}
```

---

## Resumo dos Exemplos

| Exemplo | Demonstra | Complexidade |
|---------|-----------|--------------|
| 1 | Execução básica com logging completo | Baixa |
| 2 | Retry logic para APIs externas | Média |
| 3 | HALT para ambiguidades | Média |

**Versão:** 1.0
**Criado em:** 06/11/2025
