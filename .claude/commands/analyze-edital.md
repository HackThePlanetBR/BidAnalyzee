---
description: Analyze edital requirements against knowledge base using RAG - Complete conformity analysis pipeline
---

# Analyze Edital - Conformity Analysis Pipeline

You are executing the **Technical Analyst** conformity analysis pipeline.

**Mission:** Analyze structured requirements from editais against technical knowledge base using RAG (Retrieval-Augmented Generation) to determine conformity and generate comprehensive reports.

---

## 📋 Overview

This command integrates:
1. **Document Structurer output** (structured requirements CSV)
2. **Technical Analyst RAG** (conformity analysis via Query Processor)
3. **Report Generator** (multi-format consolidated reports)

**Input:** Structured requirements CSV (from `/structure-edital` or manual creation)
**Output:** Conformity analysis report (JSON, CSV, Excel, Markdown)

---

## 🎯 Usage

```bash
/analyze-edital <csv-path> [--formats json,csv,markdown,excel] [--output-dir path]
```

### Arguments

- `<csv-path>` (required): Path to structured requirements CSV file
- `--formats` (optional): Export formats (default: json,csv,markdown)
  - Available: `json`, `csv`, `excel`, `markdown`
- `--output-dir` (optional): Output directory (default: output/analysis)

### Examples

**Basic usage:**
```bash
/analyze-edital data/deliveries/analysis_edital_001_20250108/outputs/requirements_structured.csv
```

**With custom formats:**
```bash
/analyze-edital requirements.csv --formats json,excel,markdown
```

**With custom output directory:**
```bash
/analyze-edital requirements.csv --output-dir reports/compliance
```

---

## 🔄 Workflow

### Step 1: Validate Input

1. Check if CSV file exists
2. Verify file is readable
3. Validate CSV structure (required columns)
4. Count requirements

**If validation fails:**
- HALT with clear error message
- Provide guidance on expected CSV format

### Step 2: Load Knowledge Base

1. Initialize RAG Engine with vector store
2. Verify knowledge base is ingested
3. Confirm embeddings are ready

**Status check:**
```
✅ RAG Engine initialized
✅ Vector store: FAISS (local)
✅ Knowledge base: 6 documents indexed
✅ Embeddings: all-MiniLM-L6-v2 (384 dims)
```

### Step 3: Analyze Conformity

1. Load requirements from CSV
2. For each requirement:
   - Build optimized query
   - Search knowledge base (top-k=5)
   - Extract evidence
   - Calc confidence score
   - Determine verdict (CONFORME/NAO_CONFORME/REVISAO)
   - Generate reasoning
   - Generate recommendations
3. Track statistics

**Progress indicator:**
```
🔍 Analyzing 50 requirements...
============================================================
[1/50] Analyzing REQ-001... ✅ CONFORME (92%)
[2/50] Analyzing REQ-002... ⚠️  REVISAO (68%)
[3/50] Analyzing REQ-003... ✅ CONFORME (88%)
...
[50/50] Analyzing REQ-050... ✅ CONFORME (91%)
============================================================
✅ Batch analysis complete: 50/50 successful
```

### Step 4: Generate Report

1. Create ConformityReport with all results
2. Calculate summary statistics
3. Identify critical issues (NAO_CONFORME)
4. Identify review needed (REVISAO)
5. Consolidate recommendations

### Step 5: Export Results

1. Export in requested formats:
   - **JSON**: Complete structured data
   - **CSV**: Tabular format (requirements + verdicts)
   - **Excel**: Multi-sheet workbook (Summary + Details)
   - **Markdown**: Human-readable report

**Output files:**
```
output/analysis/
├── {basename}_analysis.json       # Complete data
├── {basename}_analysis.csv        # Tabular results
├── {basename}_analysis.xlsx       # Excel workbook
└── {basename}_report.md           # Markdown report
```

### Step 6: Display Summary

Print to console:
- Total requirements analyzed
- Conformity breakdown (CONFORME/NAO_CONFORME/REVISAO)
- Overall compliance rate
- Execution times (loading, analysis, reporting)
- Critical issues (if any)
- Top recommendations

---

## 📊 Output Formats

### JSON (Complete)
```json
{
  "edital_metadata": {...},
  "summary": {
    "total_requirements": 50,
    "conforme": 35,
    "nao_conforme": 2,
    "revisao": 13,
    "overall_compliance_rate": 70.0
  },
  "requirements": [...],
  "analysis_results": [...],
  "critical_issues": [...],
  "review_needed": [...],
  "consolidated_recommendations": [...],
  "timestamp": "2025-11-08T12:00:00",
  "pipeline_stats": {...}
}
```

### CSV (Tabular)
```csv
id,descricao,tipo,categoria,prioridade,veredicto,confianca,evidencias_count,fontes,reasoning,recomendacoes
REQ-001,"Câmeras IP 4MP",Técnico,Hardware,Alta,CONFORME,0.92,3,"requisitos_tecnicos.md, doc2.md","O requisito está em conformidade...","✅ Requisito validado; 📋 Incluir evidências"
```

### Excel (Multi-sheet)
- **Sheet 1 (Resumo)**: Summary statistics
- **Sheet 2 (Análise Detalhada)**: Full requirement-by-requirement analysis

### Markdown (Human-readable)
```markdown
# Relatório de Análise de Conformidade

**Edital:** 001/2024
**Órgão:** Prefeitura Municipal
**Data da Análise:** 2025-11-08

## 📊 Resumo Executivo
| Métrica | Valor |
|---------|-------|
| Total de Requisitos | 50 |
| ✅ Conformes | 35 (70.0%) |
| ❌ Não Conformes | 2 (4.0%) |
| ⚠️ Revisão Necessária | 13 (26.0%) |

## 🚨 Questões Críticas
### ❌ REQ-042: Sistema de detecção alienígena
...

## 📋 Análise Detalhada
### ✅ REQ-001: Câmeras IP com resolução 4MP
...
```

---

## 🎯 Conformity Verdicts

| Verdict | Criteria | Meaning |
|---------|----------|---------|
| **CONFORME** | Confidence ≥ 0.85 AND Evidence ≥ 2 sources | Requirement meets documentation requirements |
| **NAO_CONFORME** | Explicitly contradicts documentation | Requirement does not meet requirements |
| **REVISAO** | Confidence < 0.85 OR Evidence < 2 sources | Requires human review (insufficient/ambiguous evidence) |

**Confidence Score:**
- Weighted: 70% average relevance + 30% max relevance
- Range: 0.0 (no match) to 1.0 (perfect match)

---

## 🚨 Error Handling

| Error | Response |
|-------|----------|
| File not found | "❌ CSV not found at: {path}. Please verify the path." |
| Invalid CSV | "❌ Invalid CSV structure. Required columns: ID, Descrição, ..." |
| Empty CSV | "⚠️ No requirements found in CSV. Please verify the file." |
| RAG not initialized | "❌ RAG Engine not ready. Run knowledge base ingestion first." |
| Export failure | "⚠️ Failed to export {format}: {error}. Other formats may succeed." |

---

## 💻 Implementation

```python
from agents.technical_analyst import AnalysisPipeline

# Initialize pipeline
pipeline = AnalysisPipeline(output_dir="output/analysis")

# Analyze from CSV
report = pipeline.analyze_from_csv(
    csv_path="requirements.csv",
    export_formats=['json', 'csv', 'markdown', 'excel']
)

# Display summary
summary = report.get_summary()
print(f"Overall Compliance: {summary['overall_compliance_rate']:.1f}%")
```

---

## ⏱️ Performance Targets

| Metric | Target |
|--------|--------|
| Small (10-20 reqs) | < 30s |
| Medium (30-50 reqs) | < 2 min |
| Large (100+ reqs) | < 5 min |
| Memory usage | < 500MB |

**Actual performance logged in report:**
- Loading time
- Analysis time (RAG queries)
- Report generation time
- Total duration

---

## 📚 Related Commands

- `/structure-edital` - Extract requirements from PDF edital
- Use `/structure-edital` first to generate the requirements CSV
- Then use `/analyze-edital` to perform conformity analysis

**Complete workflow:**
```bash
# Step 1: Extract requirements
/structure-edital data/uploads/edital_001.pdf

# Step 2: Analyze conformity (use output path from step 1)
/analyze-edital data/deliveries/analysis_edital_001_20250108/outputs/requirements_structured.csv
```

---

## 📖 References

- **Pipeline Documentation:** `docs/ANALYSIS_PIPELINE.md`
- **Query Processor:** `docs/QUERY_PROCESSOR.md`
- **RAG Engine:** `docs/TECHNICAL_ANALYST_RAG.md`
- **Agent Package:** `agents/technical_analyst/`

---

**Ready to analyze!** 🔍

Provide the CSV path to begin conformity analysis.
