# Sprint 4.5 - Document Structurer Enhancements

**Sprint Goal:** Enhance Document Structurer with advanced features for production robustness

**Duration:** 4-5 histories
**Status:** 🟡 In Progress
**Dependencies:** Sprint 4 Complete ✅

---

## 📋 Histórias (User Stories)

### História 2.7: OCR Support for Scanned PDFs
**Objetivo:** Enable Document Structurer to extract text from scanned/image-based PDFs

**Contexto:**
Currently, the agent halts when detecting scanned PDFs (< 100 chars extracted). This enhancement will automatically apply OCR to extract text from images.

**Deliverables:**
1. **OCR Integration Module** (`agents/document_structurer/extractors/ocr_handler.py`)
   - Integrate pytesseract for OCR processing
   - Support for Portuguese language optimization
   - Automatic scanned PDF detection
   - Image preprocessing (deskew, denoise, enhance)

2. **OCR Configuration** (`.env` / config)
   - Tesseract path configuration
   - Language pack settings (por + eng)
   - Quality thresholds

3. **Updated HALT Behavior**
   - Replace manual HALT with automatic OCR attempt
   - HALT only if OCR fails or confidence < threshold
   - Add OCR quality metrics to output

4. **OCR Tests** (`tests/unit/test_ocr_handler.py`)
   - Test scanned PDF detection
   - Test OCR text extraction
   - Test confidence scoring
   - Test fallback behavior

**Critérios de Aceitação:**
- ✅ Automatically detects scanned PDFs
- ✅ Applies OCR with Portuguese optimization
- ✅ Extracts text with confidence > 70%
- ✅ Preprocesses images for better quality
- ✅ Logs OCR metrics (time, confidence, pages)
- ✅ Tests pass (100%)

**Estimativa:** 6-8 hours

---

### História 2.8: Metadata Extraction - Pattern Improvements
**Objetivo:** Fix remaining 20% of metadata extraction tests and improve pattern reliability

**Contexto:**
Current metadata extractor has 80% success rate. Two tests failing:
- `test_extract_objeto_with_variations`
- `test_overall_confidence`

**Deliverables:**
1. **Enhanced Regex Patterns** (update `metadata_extractor.py`)
   - More flexible objeto patterns (handle multi-line, nested sections)
   - Better boundary detection
   - Add fallback patterns for edge cases

2. **Improved Confidence Calculation**
   - Weighted confidence by field importance
   - Separate overall vs. per-field confidence
   - Add confidence explanation metadata

3. **Additional Field Extraction**
   - `endereço_entrega` (delivery address)
   - `contato_responsável` (contact person)
   - `anexos` (list of attachments/documents required)

4. **Updated Tests** (update `test_metadata_extractor.py`)
   - Fix failing tests
   - Add tests for new fields
   - Add edge case tests (missing sections, malformed data)

**Critérios de Aceitação:**
- ✅ All 10 existing tests pass (100%)
- ✅ 3 new fields extracted successfully
- ✅ Confidence calculation improved (weighted)
- ✅ Handles edge cases gracefully
- ✅ Documentation updated with new patterns

**Estimativa:** 4-6 hours

---

### História 2.9: Performance Optimization for Large PDFs
**Objetivo:** Optimize processing speed and memory usage for large PDFs (100+ pages, 50+ MB)

**Contexto:**
Current implementation loads entire PDF into memory and processes sequentially. This is slow for large documents and may cause memory issues.

**Deliverables:**
1. **Chunked Processing** (update `pdf_processor.py`)
   - Process PDFs in page chunks (10-20 pages at a time)
   - Stream processing to reduce memory footprint
   - Progress tracking for long operations

2. **Caching Layer** (`agents/document_structurer/cache_manager.py`)
   - Cache extracted text by PDF hash
   - Cache metadata extraction results
   - Configurable TTL (time-to-live)
   - Cache invalidation on file changes

3. **Parallel Processing**
   - Parallel page extraction (multiprocessing)
   - Parallel requirement extraction from sections
   - Configurable worker count

4. **Performance Benchmarks** (`tests/performance/benchmark_large_pdfs.py`)
   - Test with PDFs: 10 pages, 50 pages, 100 pages, 500 pages
   - Measure: extraction time, memory usage, accuracy
   - Compare: before vs. after optimization

**Critérios de Aceitação:**
- ✅ 50% reduction in processing time for 100+ page PDFs
- ✅ 60% reduction in memory usage
- ✅ No accuracy loss (same output)
- ✅ Progress tracking works correctly
- ✅ Cache hit rate > 80% for repeated processing
- ✅ Benchmark results documented

**Estimativa:** 8-10 hours

---

### História 2.10: Additional Validation Rules
**Objetivo:** Expand validation checklist with domain-specific rules for edital compliance

**Contexto:**
Current validation has 16 checks (8 Anti-Alucinação + 8 Estruturação). We need more specific rules for Brazilian public procurement compliance.

**Deliverables:**
1. **New Validation Categories** (update `validation_engine.py`)
   - **Legal Compliance** (6 rules)
     - Lei 8.666/93 mandatory clauses detection
     - Lei 14.133/2021 compatibility check
     - Prazo legal verification (minimum deadlines)
     - Garantia requirements (bid bond, performance bond)
     - Habilitação jurídica requirements
     - Qualificação técnica requirements

   - **Completeness** (4 rules)
     - All mandatory annexes referenced
     - Contact information present
     - Timeline/calendar complete
     - Payment terms defined

   - **Consistency** (4 rules)
     - Dates in chronological order
     - Values sum correctly (items vs. total)
     - Units of measurement consistent
     - References to sections exist

2. **Configurable Rule Severity** (`validation_rules.yaml`)
   - CRITICAL: blocks delivery
   - WARNING: flags for review
   - INFO: suggestions only

3. **Validation Report Enhancement** (update `validation_report.py`)
   - Grouped by severity
   - Links to specific sections
   - Remediation suggestions
   - Compliance checklist export

4. **Rule Tests** (`tests/unit/test_validation_rules.py`)
   - Test each rule individually
   - Test rule combinations
   - Test severity handling
   - Test false positive prevention

**Critérios de Aceitação:**
- ✅ 14 new validation rules implemented
- ✅ Total 30 validation rules (16 existing + 14 new)
- ✅ Rule severity system working
- ✅ Validation report enhanced with grouping
- ✅ All rules tested (100% coverage)
- ✅ Documentation for each rule

**Estimativa:** 8-10 hours

---

## 📊 Sprint 4.5 Summary

| História | Focus | Estimativa | Status |
|----------|-------|------------|--------|
| História 2.7 | OCR Support | 6-8h | 🟡 Pending |
| História 2.8 | Metadata Improvements | 4-6h | 🟡 Pending |
| História 2.9 | Performance Optimization | 8-10h | 🟡 Pending |
| História 2.10 | Additional Validation Rules | 8-10h | 🟡 Pending |

**Total Estimativa:** 26-34 hours (3-4 days)

---

## 🎯 Success Metrics

**Performance:**
- ✅ 50% faster processing for large PDFs
- ✅ 60% reduction in memory usage
- ✅ OCR success rate > 70% for scanned PDFs

**Quality:**
- ✅ Metadata extraction: 100% test pass rate (up from 80%)
- ✅ Validation rules: 30 total rules (up from 16)
- ✅ Test coverage: 95%+ maintained

**Usability:**
- ✅ Automatic OCR (no manual intervention needed)
- ✅ Progress tracking for long operations
- ✅ Cache reduces repeat processing time by 80%

---

## 🔧 Technical Stack Additions

**New Dependencies:**
- `pytesseract` - OCR engine wrapper
- `Pillow` (PIL) - Image preprocessing
- `diskcache` - Simple disk-based caching
- `multiprocessing` - Parallel processing (built-in)

**System Requirements:**
- Tesseract-OCR installed (`apt-get install tesseract-ocr`)
- Portuguese language pack (`apt-get install tesseract-ocr-por`)
- Recommended: 4GB+ RAM for large PDFs

---

## 📝 Implementation Order

**Recommended sequence:**

1. **História 2.8 (Metadata)** - Fix existing issues first
2. **História 2.7 (OCR)** - Add critical missing feature
3. **História 2.9 (Performance)** - Optimize before scaling
4. **História 2.10 (Validation)** - Enhance quality checks last

**Rationale:** Fix bugs → Add features → Optimize → Enhance quality

---

## 🚀 Next Steps

Ready to begin História 2.8 (Metadata Improvements)?

**[A] Sim - Começar História 2.8 (Metadata)**
Fix the 2 failing tests and improve pattern reliability

**[B] Não - Começar História 2.7 (OCR)**
Start with OCR support for scanned PDFs

**[C] Não - Mudar ordem**
Suggest different implementation order

**[D] Revisar plano**
Review and adjust the Sprint 4.5 plan
