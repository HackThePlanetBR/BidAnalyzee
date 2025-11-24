# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**BidAnalyzee** is a production-ready AI-powered system for analyzing compliance of Brazilian public procurement documents (editais). It uses a RAG (Retrieval-Augmented Generation) architecture governed by the **SHIELD Framework** to ensure quality, traceability, and zero-tolerance for process errors.

**Key Stats:**
- Version: 1.0.0 (Production Ready)
- Framework: SHIELD v1.0 (Strict Mode)
- Tests: 116/116 passing
- Interface: Claude Code slash commands (9 commands)
- RAG Engine: FAISS + sentence-transformers (local, multilingual)

## Development Commands

### Environment Setup

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Testing

```bash
# Run all tests
pytest tests/agents/ -v

# Run specific test suite
pytest tests/agents/test_document_structurer.py -v
pytest tests/agents/test_technical_analyst.py -v
pytest tests/agents/test_orchestrator.py -v
pytest tests/agents/test_shield_framework.py -v

# Run integration tests
pytest tests/integration/ -v

# Run E2E tests
pytest tests/e2e/ -v

# Run with coverage
pytest tests/agents/ --cov --cov-report=term-missing
```

### Running Core Scripts

```bash
# Structure edital (extract requirements from PDF)
python3 scripts/analyze_edital_structure.py <path/to/edital.pdf>

# Analyze conformity (RAG-based analysis)
python3 scripts/analyze_conformity_e2e.py <path/to/requirements.csv>

# Full pipeline (structure + analyze + exports)
python3 scripts/analyze_edital_full.py <path/to/edital.pdf>

# RAG search (quick knowledge base query)
python3 scripts/rag_search.py --requirement "text" --top-k 5

# Export reports
python3 scripts/export_pdf.py <analysis.csv> [output.pdf]
python3 scripts/export_excel.py <analysis.csv> [output.xlsx]

# Validate PDF before processing
python3 scripts/validate_pdf.py <path/to/edital.pdf>

# Compare editais
python3 scripts/compare_editais.py <edital1.csv> <edital2.csv>

# Dashboard
python3 scripts/dashboard.py
```

### Knowledge Base Management

```bash
# Index knowledge base (required before first analysis)
python3 scripts/index_knowledge_base.py

# Web scrapers (populate knowledge base)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium

# Available scrapers:
# - scsaas: Security Center SaaS Help (~500 articles)
# - compliance: Genetec Compliance Portal (~100 articles)
# - techdocs: Genetec Technical Documentation (~800+ articles)
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│  Interface (Claude Code + Slash Commands)   │
│  /structure-edital | /analyze-edital | etc  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Orchestration Layer (@Orquestrador)        │
│  - SHIELD Framework governance              │
│  - State management (SessionManager)        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Specialized Agents (as structured prompts) │
│  @DocumentStructurer | @AnalistaTecnico     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Data Services                              │
│  FAISS (vectors) | Local File System        │
└─────────────────────────────────────────────┘
```

### SHIELD Framework

All agents implement the **SHIELD methodology** (Strict Mode mandatory):

- **S**TRUCTURE: Detailed planning before execution
- **H**ALT: User approval checkpoints
- **I**NSPECT: Self-inspection with checklists (8 fixed + 8 dynamic items)
- **E**XECUTE: Controlled execution
- **L**OOP: Refinement cycles (max 3 iterations)
- **L.5 VALIDATE**: Quantitative validation (100% completeness required)
- **D**DELIVER: Formal delivery with evidence

**Key principle:** Zero-tolerance for **process** errors, not model errors. The framework must correctly identify and handle AI uncertainties (< 85% confidence → marked for human review).

### Agent Architecture

Agents are implemented as **structured prompts** (YAML frontmatter + Markdown), not separate processes:

```
agents/
├── orchestrator/
│   ├── prompt.md              # Main orchestrator prompt
│   └── state/                 # SessionManager, state tracking
├── document_structurer/
│   ├── prompt.md              # Extraction/structuring logic
│   ├── validation_engine.py   # 30 validation rules
│   ├── cache_manager.py       # 105x faster with cache
│   └── extractors/            # OCR, metadata extraction
└── technical_analyst/
    ├── prompt.md              # RAG-based conformity analysis
    ├── rag_engine.py          # FAISS + sentence-transformers
    ├── vector_store.py        # Local vector storage
    └── pipeline.py            # Full RAG pipeline
```

### Data Flow

1. **Input:** PDF edital (up to 500 pages, 50MB)
2. **Structure:** @DocumentStructurer → CSV with 7 fields (ID, Item, Descrição, Categoria, Prioridade, Página, Confiança)
3. **Analyze:** @AnalistaTecnico → CSV with conformity analysis (10 fields including Veredicto, Evidências, Raciocínio)
4. **Export:** Generate professional PDF/Excel reports
5. **Storage:** `data/analyses/{session_id}/` with full audit trail

### State Management

```python
# SessionManager tracks analysis state
data/
├── analyses/              # One folder per analysis
│   ├── {session_id}/
│   │   ├── metadata.json      # Session metadata
│   │   ├── outputs/           # Generated CSVs
│   │   ├── evidences/         # Validation results
│   │   └── logs/              # Execution logs
└── state/
    ├── sessions_index.json    # Master index
    └── current_session.json   # Active session
```

## Key Implementation Details

### RAG Engine Configuration

- **Vector Store:** FAISS (faiss-cpu) - local, ultra-fast
- **Embeddings:** sentence-transformers `all-MiniLM-L6-v2` (384d, multilingual)
- **Similarity:** Cosine similarity
- **Top-K:** 20 results, re-ranked to top 3-5
- **Threshold:** 0.85 confidence for CONFORME verdict

### Document Structurer Specifics

**What it does:**
- Extracts text from PDF (PyPDF2)
- OCR support for scanned PDFs (Tesseract + pytesseract)
- Extracts metadata (10 fields with weighted confidence)
- Applies 30 validation rules (Anti-Alucinação + Legal Compliance)
- Cache optimization (SHA256-based, 105x faster on hits)

**What it does NOT do:**
- Process images/diagrams
- Invent requirements (Anti-Alucinação principle)
- Handle non-PDF formats (must convert first)

### Technical Analyst Specifics

**Analysis logic:**
- **CONFORME:** Requirement fully supported by knowledge base + high confidence (≥0.75)
- **NAO_CONFORME:** Requirement contradicts knowledge base or legislation (≥0.70 confidence)
- **REVISAO:** Insufficient evidence, ambiguous, or low confidence (<0.70)
- **PARCIAL:** Partially meets requirements (use sparingly)

**Evidence format:** `document.md:line_number` with semantic similarity score

**Critical rule:** When in doubt → REVISAO (conservative approach for legal safety)

## Important Files and Locations

### Core Documentation
- `OPERATING_PRINCIPLES.md` - SHIELD Framework complete spec
- `ARCHITECTURE_DECISIONS.md` - ADRs (Architecture Decision Records)
- `README.md` - User-facing documentation
- `PROJECT_STATUS.md` - Current project status
- `ROADMAP.md` - Development roadmap

### Agent Definitions
- `agents/orchestrator/prompt.md` - Main orchestration logic
- `agents/document_structurer/prompt.md` - Extraction/structuring
- `agents/technical_analyst/prompt.md` - Conformity analysis

### Validation Rules
- `framework/checklists/anti_alucinacao.yaml` - Fixed anti-hallucination checklist
- `agents/document_structurer/checklists/inspect.yaml` - Structuring validation
- `agents/technical_analyst/checklists/inspect.yaml` - Analysis validation

### Configuration
- `.env` - Environment variables (copy from `.env.example`)
- `requirements.txt` - Python dependencies
- `data/templates/*.yaml` - Analysis templates (reusable configs)

### Slash Commands
- `.claude/commands/*.md` - 9 slash command definitions
- Use `/help` to see all available commands

## Common Development Workflows

### Adding a New Validation Rule

1. Add rule to relevant checklist: `agents/{agent}/checklists/inspect.yaml`
2. Update validation engine: `agents/{agent}/validation_engine.py`
3. Add test case: `tests/agents/test_{agent}.py`
4. Update agent prompt: `agents/{agent}/prompt.md` (INSPECT phase)
5. Run tests: `pytest tests/agents/test_{agent}.py -v`

### Extending the Knowledge Base

1. Add markdown files to: `data/knowledge_base/mock/`
2. Include YAML frontmatter with metadata:
   ```yaml
   ---
   title: Document Title
   url: https://source.url
   category: Hardware|Software|Legislação
   ---
   ```
3. Re-index: `python3 scripts/index_knowledge_base.py`
4. Test search: `python3 scripts/rag_search.py --requirement "test query"`

### Adding a New Slash Command

1. Create file: `.claude/commands/{command-name}.md`
2. Add YAML frontmatter: `description: Command description`
3. Write prompt with clear instructions
4. Test: `/{command-name}` in Claude Code
5. Document in `docs/COMMAND_REFERENCE.md`

### Debugging Failed Analyses

1. Check logs: `data/analyses/{session_id}/logs/execution_log.txt`
2. Validate input: `python3 scripts/validate_pdf.py <file>` or `scripts/validate_csv.py <file>`
3. Check validation results: `data/analyses/{session_id}/evidences/inspection_results/`
4. Review session: `/session {session_id}`
5. Check FAISS index: Ensure `data/knowledge_base/mock/.faiss_index/` exists

## Critical Principles

### 1. SHIELD Compliance is Mandatory
Every workflow must implement all SHIELD phases. No shortcuts or "quick modes" allowed.

### 2. Anti-Alucinação (Anti-Hallucination)
Never invent information. All assertions must have documented evidence with source citations.

### 3. Conservative Verdicts
When analyzing requirements:
- High certainty + clear evidence → CONFORME
- Clear contradiction → NAO_CONFORME
- Any doubt or ambiguity → REVISAO

Better to flag for human review than risk legal issues in public procurement.

### 4. Auditability
Every decision must be traceable:
- Evidence citations: `document.md:line_number`
- Confidence scores: 0.0-1.0 with justification
- Logs: Structured execution logs for debugging

### 5. Legal Context
This system operates in Brazilian public procurement context:
- Lei 8.666/1993 (old procurement law)
- Lei 14.133/2021 (new procurement law)
- Regulations prohibit brand-specific requirements unless justified
- Documentation must support legal defensibility

## Testing Strategy

### Test Coverage
- **Unit tests:** Individual functions (cache, metadata, OCR, vector store)
- **Agent tests:** Prompt validation, SHIELD compliance (116 tests)
- **Integration tests:** Full pipelines (structure → analyze → export)
- **E2E tests:** Real editais (complex multi-item support)

### Fixtures
Reusable test fixtures in `tests/agents/conftest.py`:
- Sample PDFs, CSVs, validation results
- Mock RAG responses
- Session state examples

### Running Specific Tests
```bash
# Test a specific component
pytest tests/unit/test_cache_manager.py -v

# Test SHIELD compliance
pytest tests/agents/test_shield_framework.py -v

# Test with specific markers
pytest -m "slow" -v  # Run slow tests
pytest -m "not slow" -v  # Skip slow tests
```

## Performance Considerations

### Document Structurer
- **Cold run:** 10-30 minutes (depends on PDF size)
- **Cache hit:** 105x faster (~6 seconds)
- **Cache key:** SHA256 of (PDF content + metadata + config)
- **Parallel processing:** 3.9x speedup on multi-page PDFs

### RAG Engine
- **Index time:** ~5 seconds for ~150KB knowledge base
- **Query time:** < 1 second (FAISS is ultra-fast)
- **Memory:** ~100MB for loaded index + embeddings model

### Optimization Tips
- Pre-index knowledge base before batch analyses
- Use cache aggressively (document structurer)
- Batch multiple requirements in single RAG query when possible
- Use FLOW mode for automated end-to-end (skips HALTs except on errors)

## Troubleshooting

### "No module named 'X'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "FAISS index not found"
```bash
python3 scripts/index_knowledge_base.py
```

### OCR not working
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

### Tests failing
```bash
# Clean test cache
pytest --cache-clear

# Reinstall test dependencies
pip install -r requirements.txt --upgrade
```

### Session state corrupted
```bash
# Backup and reset state
python3 scripts/orchestrator_backup.py
python3 scripts/orchestrator_cleanup.py
```

## Additional Resources

- **User Guide:** `docs/USER_GUIDE.md` - End-user documentation
- **Tutorial:** `docs/TUTORIAL.md` - Step-by-step first analysis
- **FAQ:** `docs/FAQ.md` - Common questions
- **Web Scraper Guide:** `docs/scrapers/WEB_SCRAPER_GUIDE.md` - Scraping documentation
- **Test Documentation:** `tests/agents/README.md` - Testing guidelines

## Notes on Architecture Decisions

See `ARCHITECTURE_DECISIONS.md` for full ADRs. Key decisions:

- **ADR-001:** Agents as prompts (not isolated processes) - simpler, more maintainable
- **ADR-004:** Local FAISS instead of Pinecone - zero external dependencies, ultra-fast
- **ADR-006:** Strict Mode mandatory - maximum quality, no shortcuts
- **ADR-007:** Tolerance Zero for process, not model - framework catches AI uncertainties

## Working with This Codebase

When making changes:

1. **Read the SHIELD principles** (`OPERATING_PRINCIPLES.md`) first
2. **Check existing ADRs** (`ARCHITECTURE_DECISIONS.md`) before major decisions
3. **Write tests** for new functionality (maintain 100% pass rate)
4. **Update agent prompts** if changing workflow logic
5. **Document in CLAUDE.md** if adding common commands or patterns
6. **Test end-to-end** with real edital PDFs before considering complete

The system is production-ready but designed for continuous improvement. When in doubt, prioritize:
1. Legal safety (conservative verdicts)
2. Auditability (complete evidence trail)
3. User control (HALT checkpoints)
4. Process correctness (SHIELD compliance)
