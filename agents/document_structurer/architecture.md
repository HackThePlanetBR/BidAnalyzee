# Document Structurer - Architecture

**Agent:** Document Structurer
**Version:** 1.0.0
**Framework:** SHIELD v1.0
**Created:** 2025-11-06

---

## 🏗️ Architectural Overview

The **Document Structurer** agent is a specialized SHIELD-compliant agent that extracts and structures requirements from Brazilian public procurement PDFs (editais) into standardized CSV format.

### Design Principles

1. **SHIELD Compliance:** All 7 phases implemented (STRUCTURE → HALT → EXECUTE → INSPECT → LOOP → VALIDATE → DELIVER)
2. **Anti-Hallucination:** Never infer requirements not explicitly present in source
3. **Modo Strict:** 100% validation required for all metrics
4. **Clean Handoff:** Structured outputs via YAML/CSV for downstream agents
5. **Traceability:** Every requirement traces back to source page in PDF

---

## 📊 System Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                     DOCUMENT STRUCTURER AGENT                      │
│                         (SHIELD v1.0)                              │
└───────────────────────────────────────────────────────────────────┘

INPUT: edital.pdf (up to 500 pages, max 50MB)
   │
   │
   ▼
┌──────────────────────────────────────────────────────────────────┐
│                        PHASE 1: STRUCTURE                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  • Analyze PDF metadata (pages, size)                      │  │
│  │  • Define extraction strategy                              │  │
│  │  • Generate Plan YAML with 5 steps                         │  │
│  │  • Estimate time (10-25 min)                               │  │
│  │  • Identify 3 HALT checkpoints                             │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────┬──────────────────────────────────────────────────────┘
            │
            ├─────→ [plan.yaml]
            │         - task_id
            │         - steps[5]
            │         - halt_checkpoints[3]
            │         - estimated_time
            │
            ▼
┌───────────────────────────────────────────────────────────────────┐
│                         PHASE 2: HALT                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  User Review:                                               │  │
│  │  • Plan preview (5 steps, 3 HALTs)                         │  │
│  │  • Estimated time                                           │  │
│  │  • Options: [A] Approve / [B] Modify / [C] Cancel         │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────┬───────────────────────────────────────────────────────┘
            │
            ├─────→ [User Decision: A/B/C]
            │
            ▼ [A: Approved]
┌───────────────────────────────────────────────────────────────────┐
│                        PHASE 3: EXECUTE                            │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  STEP 1: Extract Text from PDF                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  • Input: edital.pdf                                    │ │ │
│  │  │  • Tool: PyPDF2.PdfReader                               │ │ │
│  │  │  • Process: page-by-page text extraction               │ │ │
│  │  │  • Output: text_extracted.txt (1-2MB)                   │ │ │
│  │  │  • Time: ~0.5s per page (2-5 min total)                │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └──────────────────┬───────────────────────────────────────────┘ │
│                     │                                              │
│                     ├─────→ [text_extracted.txt]                  │
│                     │                                              │
│                     ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  STEP 2: Identify Requirements                              │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  • Input: text_extracted.txt                           │ │ │
│  │  │  • Method: Linguistic pattern matching                 │ │ │
│  │  │  • Patterns:                                            │ │ │
│  │  │    - "deve [verb]"                                      │ │ │
│  │  │    - "deverá [verb]"                                    │ │ │
│  │  │    - "é obrigatório"                                    │ │ │
│  │  │    - "requisito técnico"                                │ │ │
│  │  │  • Output: requirements_raw.json (N items)              │ │ │
│  │  │  • Time: ~3 min                                         │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └──────────────────┬───────────────────────────────────────────┘ │
│                     │                                              │
│                     ├─────→ [requirements_raw.json]               │
│                     │                                              │
│                     ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  STEP 3: Categorize Requirements                            │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  • Input: requirements_raw.json                         │ │ │
│  │  │  • Method: Keyword matching                             │ │ │
│  │  │  • Categories:                                          │ │ │
│  │  │    - Hardware: câmera, servidor, equipamento...        │ │ │
│  │  │    - Software: sistema, aplicação, licença...          │ │ │
│  │  │    - Serviço: treinamento, manutenção, suporte...      │ │ │
│  │  │    - Integração: API, protocolo, interface...          │ │ │
│  │  │  • Output: requirements_categorized.json                │ │ │
│  │  │  • Time: ~30s                                           │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └──────────────────┬───────────────────────────────────────────┘ │
│                     │                                              │
│                     ├─────→ [requirements_categorized.json]       │
│                     │                                              │
│                     ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  STEP 4: Assign Priority                                    │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  • Input: requirements_categorized.json                 │ │ │
│  │  │  • Method: Keyword-based rules                          │ │ │
│  │  │  • Rules:                                               │ │ │
│  │  │    - Alta: obrigatório, essencial, crítico...          │ │ │
│  │  │    - Média: importante, necessário, recomendado...     │ │ │
│  │  │    - Baixa: desejável, opcional, diferencial...        │ │ │
│  │  │  • Output: requirements_prioritized.json                │ │ │
│  │  │  • Time: ~30s                                           │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └──────────────────┬───────────────────────────────────────────┘ │
│                     │                                              │
│                     ├─────→ [requirements_prioritized.json]       │
│                     │                                              │
│                     ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  STEP 5: Structure as CSV                                   │ │
│  │  ┌────────────────────────────────────────────────────────┐ │ │
│  │  │  • Input: requirements_prioritized.json                 │ │ │
│  │  │  • Method: pandas DataFrame transformation              │ │ │
│  │  │  • CSV Fields (7):                                      │ │ │
│  │  │    1. ID (int): Sequential 1-N                          │ │ │
│  │  │    2. Item (string): Original edital item (e.g., 3.2.1) │ │ │
│  │  │    3. Descrição (string): Full requirement text         │ │ │
│  │  │    4. Categoria (enum): HW/SW/Service/Integration       │ │ │
│  │  │    5. Prioridade (enum): Alta/Média/Baixa              │ │ │
│  │  │    6. Página (int): Source page number                  │ │ │
│  │  │    7. Confiança (float): 0.0-1.0                        │ │ │
│  │  │  • Output: requirements_structured.csv (N rows)         │ │ │
│  │  │  • Time: ~1 min                                         │ │ │
│  │  └────────────────────────────────────────────────────────┘ │ │
│  └──────────────────┬───────────────────────────────────────────┘ │
└────────────────────┬──────────────────────────────────────────────┘
                     │
                     ├─────→ [requirements_structured.csv]
                     │
                     ▼
┌───────────────────────────────────────────────────────────────────┐
│                        PHASE 4: INSPECT                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Dual Checklist System:                                     │  │
│  │                                                              │  │
│  │  1. Fixed Checklist (Anti-Alucinação) - 8 items:           │  │
│  │     [ ] All requirements traced to source page              │  │
│  │     [ ] No assumptions made                                 │  │
│  │     [ ] No external knowledge added                         │  │
│  │     [ ] Citations format correct                            │  │
│  │     [ ] Source availability verified                        │  │
│  │     [ ] Confidence scores calculated                        │  │
│  │     [ ] Low confidence flagged (< 0.85)                     │  │
│  │     [ ] Ambiguities documented                              │  │
│  │                                                              │  │
│  │  2. Dynamic Checklist (Estruturação Edital) - 8 items:     │  │
│  │     [ ] All fields present (7 columns)                      │  │
│  │     [ ] ID sequential without gaps                          │  │
│  │     [ ] Item references valid                               │  │
│  │     [ ] Categories valid (4 enums)                          │  │
│  │     [ ] Priorities valid (3 enums)                          │  │
│  │     [ ] Page numbers > 0                                    │  │
│  │     [ ] Confidence in range 0.0-1.0                         │  │
│  │     [ ] No duplicates present                               │  │
│  │                                                              │  │
│  │  Mode: Strict (100% required)                               │  │
│  │  Output: InspectionResult YAML                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────┬───────────────────────────────────────────────────────┘
            │
            ├─────→ [inspection_result.yaml]
            │         - overall_status: PASS/FAIL
            │         - fixed_checklist: 8/8
            │         - dynamic_checklist: 8/8
            │         - failed_items: []
            │
            ▼
       ┌────────────┐
       │  PASSED?   │
       └────┬───┬───┘
            │   │
      [YES] │   │ [NO]
            │   │
            │   └──────────────────────────────────────────────┐
            │                                                   │
            ▼                                                   ▼
┌───────────────────────────────────────────┐   ┌──────────────────────────────────┐
│         PHASE 5: LOOP                     │   │   SKIP LOOP                      │
│  (Only if INSPECT failed)                 │   │   (Inspection passed)            │
│                                           │   └──────────────┬───────────────────┘
│  ┌─────────────────────────────────────┐ │                  │
│  │  • Input: inspection_result.yaml   │ │                  │
│  │  • Identify failed items            │ │                  │
│  │  • Apply surgical corrections:      │ │                  │
│  │    - Remove duplicates              │ │                  │
│  │    - Renumber IDs                   │ │                  │
│  │    - Fix invalid enums              │ │                  │
│  │    - Validate page numbers          │ │                  │
│  │  • Re-run INSPECT                   │ │                  │
│  │  • Max iterations: 3                │ │                  │
│  │  • If max reached → HALT            │ │                  │
│  └─────────────────────────────────────┘ │                  │
└───────────┬───────────────────────────────┘                  │
            │                                                   │
            └───────────────────────────┬───────────────────────┘
                                        │
                                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                       PHASE 6: VALIDATE                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Quantitative Metrics (All must = 100%):                    │  │
│  │                                                              │  │
│  │  1. Completeness:                                           │  │
│  │     • Formula: (items_processed / items_expected) × 100     │  │
│  │     • Check: All identified requirements present            │  │
│  │                                                              │  │
│  │  2. Integrity:                                              │  │
│  │     • Formula: (fields_filled / fields_required) × 100      │  │
│  │     • Check: All 7 fields present in all rows               │  │
│  │                                                              │  │
│  │  3. Consistency:                                            │  │
│  │     • Check: IDs sequential 1-N without gaps                │  │
│  │     • Check: No duplicate IDs                               │  │
│  │     • Check: Enums match specification                      │  │
│  │                                                              │  │
│  │  4. Traceability:                                           │  │
│  │     • Check: All requirements have source page              │  │
│  │     • Check: All pages valid (1 to max_pages)               │  │
│  │                                                              │  │
│  │  Mode: Strict (100% required for all metrics)               │  │
│  │  Output: ValidationResult YAML                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────┬───────────────────────────────────────────────────────┘
            │
            ├─────→ [validation_result.yaml]
            │         - completeness: 100.0%
            │         - integrity: 100.0%
            │         - consistency: 100.0%
            │         - traceability: 100.0%
            │         - overall_status: PASS
            │
            ▼
┌───────────────────────────────────────────────────────────────────┐
│                         PHASE 7: HALT                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Delivery Preview:                                          │  │
│  │  • CSV: requirements_structured.csv (N requirements)        │  │
│  │  • Quality: 16/16 checklist passed                          │  │
│  │  • Metrics: 4/4 validation = 100%                           │  │
│  │  • Options: [A] Approve / [B] Review / [C] Cancel          │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────┬───────────────────────────────────────────────────────┘
            │
            ├─────→ [User Decision: A/B/C]
            │
            ▼ [A: Approved]
┌───────────────────────────────────────────────────────────────────┐
│                        PHASE 8: DELIVER                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Package Structure:                                         │  │
│  │                                                              │  │
│  │  data/deliveries/analysis_{edital_name}_{timestamp}/        │  │
│  │  │                                                           │  │
│  │  ├── outputs/                                               │  │
│  │  │   └── requirements_structured.csv   (Primary output)    │  │
│  │  │                                                           │  │
│  │  ├── evidences/                                             │  │
│  │  │   ├── inspection_results/                                │  │
│  │  │   │   └── inspection_001.yaml       (16/16 passed)      │  │
│  │  │   ├── validation_results/                                │  │
│  │  │   │   └── validation_001.yaml       (4 metrics = 100%)  │  │
│  │  │   └── execution_logs/                                    │  │
│  │  │       └── document_structurer.log   (Full trace)        │  │
│  │  │                                                           │  │
│  │  ├── metadata/                                              │  │
│  │  │   ├── plan.yaml                     (Original plan)     │  │
│  │  │   └── timeline.yaml                 (Phase timestamps)  │  │
│  │  │                                                           │  │
│  │  ├── sources/                                               │  │
│  │  │   └── edital_original.pdf           (Input preserved)   │  │
│  │  │                                                           │  │
│  │  └── README.md                          (Executive summary) │  │
│  │                                                              │  │
│  │  Time: ~30s                                                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────┬───────────────────────────────────────────────────────┘
            │
            ▼

     OUTPUT: Complete delivery package
```

---

## 🧩 Component Breakdown

### 1. PDF Processor

**Responsibility:** Extract text from PDF documents

**Technology:**
- Primary: `PyPDF2.PdfReader`
- Fallback: `pdfplumber` (for complex layouts)

**Input:**
- PDF file (max 500 pages, max 50MB)
- Text-extractable (no OCR)

**Output:**
- Plain text (UTF-8 encoded)
- Page boundaries preserved

**Performance:**
- ~0.5 seconds per page
- ~2-5 minutes for 345-page document

**Error Handling:**
- Encrypted PDFs: HALT with error
- Corrupted PDFs: HALT with error
- Scanned PDFs: HALT with warning (no OCR support)

---

### 2. Requirement Identifier

**Responsibility:** Identify technical requirements using linguistic patterns

**Method:** Regex-based pattern matching

**Brazilian Portuguese Patterns:**
```python
REQUIREMENT_PATTERNS = [
    r'deve\s+\w+',           # "deve fornecer"
    r'deverá\s+\w+',         # "deverá suportar"
    r'é\s+obrigatório',      # "é obrigatório"
    r'requisito\s+técnico',  # "requisito técnico"
    r'especificação',        # "especificação"
    r'obrigatoriamente',     # "obrigatoriamente"
]
```

**Context Detection:**
- Identifies technical sections (e.g., "Especificações Técnicas", "Requisitos")
- Filters administrative requirements
- Preserves requirement context (surrounding text)

**Confidence Calculation:**
```python
confidence = (
    pattern_match_strength * 0.4 +
    technical_section_bonus * 0.3 +
    clarity_score * 0.2 +
    context_relevance * 0.1
)
```

**Thresholds:**
- High: ≥ 0.90 (explicit requirement)
- Medium: 0.85-0.89 (implicit requirement)
- Low: < 0.85 (flagged for manual review)

---

### 3. Requirement Categorizer

**Responsibility:** Classify requirements into 4 categories

**Method:** Keyword-based classification

**Categories and Keywords:**

| Category | Keywords |
|----------|----------|
| **Hardware** | câmera, servidor, equipamento, dispositivo, CPU, memória, disco, rack, switch, roteador |
| **Software** | sistema, aplicação, licença, software, programa, plataforma, banco de dados, middleware |
| **Serviço** | treinamento, manutenção, suporte, instalação, configuração, implantação, garantia |
| **Integração** | integração, API, protocolo, interface, WebService, REST, SOAP, middleware |

**Fallback:** If no keywords match, default to "Software" and flag with lower confidence

**Accuracy Target:** >90%

---

### 4. Priority Assigner

**Responsibility:** Assign priority levels based on urgency keywords

**Method:** Rule-based classification

**Priority Rules:**

| Priority | Keywords |
|----------|----------|
| **Alta** | obrigatório, essencial, crítico, fundamental, mandatório, imprescindível, bloqueante |
| **Média** | importante, necessário, recomendado, relevante, significativo |
| **Baixa** | desejável, opcional, diferencial, nice-to-have, preferencial |

**Default:** If no keywords match, default to "Média"

**Accuracy Target:** >85%

---

### 5. CSV Structurer

**Responsibility:** Transform JSON data into structured CSV

**Technology:** `pandas.DataFrame`

**CSV Specification:**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| **ID** | int | Yes | Sequential 1-N, no gaps |
| **Item** | string | Yes | Max 50 chars, edital format |
| **Descrição** | string | Yes | Max 2000 chars |
| **Categoria** | enum | Yes | One of: Hardware, Software, Serviço, Integração |
| **Prioridade** | enum | Yes | One of: Alta, Média, Baixa |
| **Página** | int | Yes | Range: 1 to max_pages |
| **Confiança** | float | Yes | Range: 0.0 to 1.0 |

**Encoding:** UTF-8 with BOM (for Excel compatibility)

**Delimiter:** Comma (`,`)

**Quoting:** All string fields quoted

---

### 6. Quality Inspector

**Responsibility:** Run dual checklist validation (16 items total)

**Fixed Checklist (8 items):** Anti-Hallucination principles
**Dynamic Checklist (8 items):** Agent-specific validation

**Mode:** Strict (100% pass required)

**Output Format:**
```yaml
inspection_result:
  overall_status: "PASS"  # or "FAIL"
  timestamp: "2025-11-06T14:32:15Z"

  fixed_checklist:
    total_items: 8
    passed_items: 8
    failed_items: []

  dynamic_checklist:
    total_items: 8
    passed_items: 8
    failed_items: []
```

---

### 7. Quantitative Validator

**Responsibility:** Validate 4 quantitative metrics (all must = 100%)

**Metrics:**

1. **Completeness:** `(items_processed / items_expected) × 100`
2. **Integrity:** `(fields_filled / fields_required) × 100`
3. **Consistency:** IDs sequential, no duplicates, valid enums
4. **Traceability:** All items have source page

**Output Format:**
```yaml
validation_result:
  overall_status: "PASS"  # or "FAIL"
  timestamp: "2025-11-06T14:35:42Z"

  metrics:
    completeness:
      value: 100.0
      formula: "(47 / 47) × 100"
      status: "PASS"

    integrity:
      value: 100.0
      formula: "(329 / 329) × 100"
      status: "PASS"

    consistency:
      value: 100.0
      checks: ["ids_sequential", "no_duplicates", "valid_enums"]
      status: "PASS"

    traceability:
      value: 100.0
      checks: ["all_have_pages", "valid_page_range"]
      status: "PASS"
```

---

### 8. Delivery Packager

**Responsibility:** Organize final delivery package

**Structure:**
```
data/deliveries/analysis_{edital_name}_{timestamp}/
├── outputs/
│   └── requirements_structured.csv
├── evidences/
│   ├── inspection_results/
│   │   └── inspection_001.yaml
│   ├── validation_results/
│   │   └── validation_001.yaml
│   └── execution_logs/
│       └── document_structurer.log
├── metadata/
│   ├── plan.yaml
│   └── timeline.yaml
├── sources/
│   └── edital_original.pdf
└── README.md
```

**README.md Contents:**
- Executive summary (1-2 paragraphs)
- Key metrics (47 requirements, 100% validation)
- Timestamp and version info
- Usage instructions

---

## 🔄 Data Flow

```
PDF Bytes
   │
   ▼ [PyPDF2]
Raw Text (string)
   │
   ▼ [Pattern Matching]
Requirements List (JSON)
[
  {
    "text": "Sistema de câmeras...",
    "page": 23,
    "confidence": 0.95
  },
  ...
]
   │
   ▼ [Categorizer]
Categorized Requirements (JSON)
[
  {
    "text": "Sistema de câmeras...",
    "category": "Hardware",
    "page": 23,
    "confidence": 0.95
  },
  ...
]
   │
   ▼ [Priority Assigner]
Prioritized Requirements (JSON)
[
  {
    "text": "Sistema de câmeras...",
    "category": "Hardware",
    "priority": "Alta",
    "page": 23,
    "confidence": 0.95
  },
  ...
]
   │
   ▼ [CSV Structurer]
Structured CSV (DataFrame)
ID,Item,Descrição,Categoria,Prioridade,Página,Confiança
1,"3.2.1","Sistema de câmeras...",Hardware,Alta,23,0.95
...
   │
   ▼ [Quality Gates]
Validated CSV (Final Output)
```

---

## 🛡️ SHIELD Integration

### Phase Mapping

| SHIELD Phase | Document Structurer Activity | Time |
|--------------|------------------------------|------|
| **STRUCTURE** | Analyze PDF, create 5-step plan | ~1 min |
| **HALT** | User approves plan | User input |
| **EXECUTE** | 5 steps (extract, identify, categorize, prioritize, structure) | ~6 min |
| **INSPECT** | Run 16-item checklist (Anti-Alucinação + Estruturação) | ~30s |
| **LOOP** | Fix issues if INSPECT fails (max 3 iterations) | 1-3 min |
| **VALIDATE** | Calculate 4 metrics (all = 100%) | ~30s |
| **HALT** | User approves delivery | User input |
| **DELIVER** | Package outputs + evidences + metadata | ~30s |

**Total Time:** ~10 minutes (excluding user input)

---

## 📊 Performance Characteristics

### Time Complexity

| Component | Complexity | Time (345 pages) |
|-----------|-----------|------------------|
| PDF Extraction | O(n) | 2-3 min |
| Requirement Identification | O(n×m) | 3-5 min |
| Categorization | O(n) | 30s |
| Prioritization | O(n) | 30s |
| CSV Structuring | O(n) | 1 min |
| Inspection | O(1) | 30s |
| Validation | O(n) | 30s |
| Delivery | O(n) | 30s |
| **Total** | **O(n×m)** | **~10 min** |

*where n = number of pages, m = average patterns per page*

### Memory Usage

| Phase | Memory |
|-------|--------|
| PDF in memory | ~50 MB |
| Extracted text | ~2 MB |
| JSON intermediate | ~500 KB |
| DataFrame | ~200 KB |
| **Peak Total** | **~53 MB** |

### Scalability

| PDF Size | Pages | Estimated Time |
|----------|-------|----------------|
| Small | 20-50 | 2-3 min |
| Medium | 100-200 | 5-8 min |
| Large | 300-500 | 10-15 min |
| **Max Supported** | **500** | **~15 min** |

---

## 🔌 Integration Points

### Upstream (Input)

**Slash Command:**
```bash
/structure-edital data/uploads/PMSP-2025-001.pdf
```

**Python API:**
```python
from agents.document_structurer import DocumentStructurer

agent = DocumentStructurer()
result = agent.run(
    input_pdf="data/uploads/PMSP-2025-001.pdf",
    mode="strict"
)
```

### Downstream (Output)

**For Next Agent (Compliance Analyzer):**
```python
import pandas as pd

# Read structured requirements
df = pd.read_csv("data/deliveries/.../outputs/requirements_structured.csv")

# Access metadata
with open("data/deliveries/.../metadata/plan.yaml") as f:
    plan = yaml.safe_load(f)
```

**For User Interface:**
- CSV downloadable for Excel/spreadsheet tools
- README.md provides executive summary
- Evidences available for audit trail

---

## 🚨 Error Handling

### Known Failure Modes

| Error | Detection | Recovery |
|-------|-----------|----------|
| **Encrypted PDF** | PyPDF2 raises EncryptionError | HALT with error message |
| **Scanned PDF (no text)** | Extracted text < 100 chars | HALT with OCR warning |
| **Corrupted PDF** | PyPDF2 raises PdfReadError | HALT with error message |
| **No requirements found** | 0 requirements after Step 2 | HALT asking for clarification |
| **Low confidence items** | Any item with confidence < 0.85 | Flag in CSV, continue |
| **INSPECT fails** | INSPECT returns FAIL | Enter LOOP (max 3 iterations) |
| **VALIDATE fails** | Any metric < 100% | HALT with metric details |
| **Timeout** | Execution > 10 min | HALT with progress report |

### Escalation Path

```
Error Detected
    │
    ▼
Try LOOP (if applicable)
    │
    ├─ Success → Continue
    │
    └─ Failed after 3 iterations
        │
        ▼
    HALT (User Decision)
        │
        ├─ [A] Manual Fix → Resume
        ├─ [B] Adjust Plan → Restart
        └─ [C] Cancel → End
```

---

## 🧪 Testing Strategy

### Unit Tests

| Test | Target | Coverage |
|------|--------|----------|
| `test_extract.py` | PDF text extraction | PDF Processor |
| `test_identify.py` | Pattern matching | Requirement Identifier |
| `test_categorize.py` | Category assignment | Categorizer |
| `test_prioritize.py` | Priority rules | Priority Assigner |
| `test_structure.py` | CSV generation | CSV Structurer |

**Target Coverage:** 80%+

### Integration Tests

| Test | Fixture | Expected Output |
|------|---------|-----------------|
| `test_document_structurer.py` | `edital_sample.pdf` (120 pages) | 47 requirements, 100% validation |

### Manual Tests

```bash
# Simple edital (20 pages)
/structure-edital tests/fixtures/edital_simple.pdf

# Medium edital (100 pages)
/structure-edital tests/fixtures/edital_medium.pdf

# Complex edital (345 pages)
/structure-edital tests/fixtures/edital_complex.pdf
```

---

## 📦 Dependencies

### Required Libraries

```toml
[dependencies]
PyPDF2 = "3.0.1"      # PDF text extraction
pandas = "2.1.3"      # CSV manipulation
pyyaml = "6.0.1"      # YAML templates
structlog = "23.2.0"  # Structured logging
```

### Optional Libraries

```toml
[optional]
pdfplumber = "0.10.3"  # Fallback for complex PDFs
```

### Python Version

- **Minimum:** 3.9
- **Recommended:** 3.11+

---

## 🔐 Security Considerations

1. **PDF Uploads:**
   - Max size: 50MB (prevents DoS)
   - File type validation (only PDF allowed)
   - Virus scanning recommended (external tool)

2. **Data Privacy:**
   - PDFs may contain sensitive procurement data
   - Store in secure directory with restricted permissions
   - Consider encryption at rest

3. **Output Safety:**
   - CSV properly escaped (prevents CSV injection)
   - File paths validated (prevents directory traversal)
   - Logs sanitized (no PII exposure)

---

## 📈 Future Enhancements

### Planned (Next Sprints)

1. **OCR Support** - Process scanned PDFs via Tesseract
2. **Multi-language** - Support English editais
3. **Table Extraction** - Parse complex requirement tables
4. **Image Analysis** - Extract specs from diagrams (via GPT-4V)

### Under Consideration

1. **Batch Processing** - Handle multiple PDFs in one run
2. **Incremental Updates** - Re-process only changed sections
3. **Active Learning** - Improve patterns based on user corrections
4. **API Mode** - REST API for external integrations

---

## 📚 References

- **Framework SHIELD:** `framework/phases/README.md`
- **Agent Capabilities:** `agents/document_structurer/capabilities.yaml`
- **Checklist Definition:** `agents/document_structurer/checklists/inspect.yaml`
- **PRD:** Épico 2, História 2.1
- **Sprint Plan:** `SPRINT_3_PLAN.md`

---

**Architecture Version:** 1.0.0
**Last Updated:** 2025-11-06
**Status:** ✅ Ready for Implementation
