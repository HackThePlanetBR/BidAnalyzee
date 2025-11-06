# Metadata Extractor - Document Structurer

**Module:** `metadata_extractor.py`
**Version:** 1.0.0
**Purpose:** Extract key metadata from Brazilian public procurement documents (editais)

---

## 📋 Overview

The Metadata Extractor complements the Document Structurer agent by extracting administrative and contextual information from editais beyond technical requirements.

**What it extracts:**

| Field | Description | Example |
|-------|-------------|---------|
| **objeto** | Procurement object/purpose | "Aquisição de Sistema de Videomonitoramento" |
| **orgao** | Contracting agency | "Prefeitura Municipal De São Paulo" |
| **valor_estimado** | Estimated value | "R$ 2.500.000,00" |
| **prazo_entrega** | Delivery deadline | "180 dias" |
| **modalidade** | Procurement modality | "Pregão Eletrônico" |
| **numero_edital** | Edital number | "001/2025" |
| **data_publicacao** | Publication date | "15/01/2025" |

---

## 🚀 Usage

### Basic Usage

```python
from agents.document_structurer.extractors.metadata_extractor import extract_metadata

# Extract from text
text = """
PREFEITURA MUNICIPAL DE SÃO PAULO
EDITAL Nº 001/2025
PREGÃO ELETRÔNICO
...
"""

result = extract_metadata(text)

print(result["metadata"]["objeto"])
# "Aquisição de Sistema de Videomonitoramento"

print(result["overall_confidence"])
# 0.92
```

### Advanced Usage with Pages

```python
from agents.document_structurer.extractors.metadata_extractor import MetadataExtractor

# If you have page-by-page extraction
pages = [
    {"page": 1, "text": "..."},
    {"page": 2, "text": "..."},
    ...
]

extractor = MetadataExtractor()
metadata = extractor.extract(text, pages=pages)

# Access metadata
print(metadata.objeto)
print(metadata.orgao)
print(metadata.valor_estimado)

# Check confidence
print(metadata.confidence_scores)
# {"objeto": 0.95, "orgao": 0.98, ...}

# Validate
validation = extractor.validate_metadata(metadata)
print(validation["objeto_confident"])  # True if confidence >= 0.70
```

---

## 🧠 How It Works

### 1. Pattern Matching

Uses regex patterns optimized for Brazilian Portuguese administrative documents:

```python
PATTERNS = {
    "objeto": [
        r'(?:OBJETO|Objeto)[:\s]*(.{10,500}?)(?:\n\n|\d+\.)',
        r'(?:DO OBJETO|Do Objeto)[:\s]*(.{10,500}?)(?:\n\n|\d+\.)',
        ...
    ],
    "valor_estimado": [
        r'(?:VALOR ESTIMADO|Valor Estimado)[:\s]*R?\$?\s*([\d\.,]+)',
        ...
    ],
    ...
}
```

**Pattern Strategy:**
- Multiple patterns per field (fallbacks)
- Case-insensitive matching
- Context-aware extraction (stops at section boundaries)

### 2. Confidence Scoring

Each extracted field gets a confidence score (0.0-1.0) based on:

- **Pattern strength:** Which pattern matched (primary = high, fallback = lower)
- **Value format:** Does it match expected format? (e.g., R$ XXX,XX for valor)
- **Length:** Appropriate length for field type
- **Keywords:** Contains expected keywords (e.g., "aquisição" in objeto)

**Confidence Thresholds:**
- **High (≥ 0.90):** Very reliable, use as-is
- **Medium (0.70-0.89):** Reliable, minor review recommended
- **Low (< 0.70):** Needs manual verification

### 3. Value Cleaning

Extracted values are cleaned:

```python
# Before: "  Sistema de videomonitoramento  ;"
# After: "Sistema de videomonitoramento"

# Before: "2500000"
# After: "R$ 2.500.000,00"
```

---

## 📊 Confidence Calculation

### Field-Specific Scoring

**Objeto:**
```python
confidence = 0.7 + (length_score * 0.2) + keyword_bonus
```

**Órgão:**
```python
if "Prefeitura" or "Governo" in value:
    confidence = 0.95
else:
    confidence = 0.75
```

**Valor Estimado:**
```python
if matches_format("R$ X.XXX,XX"):
    confidence = 0.90
else:
    confidence = 0.70
```

### Overall Confidence

```python
overall = average([conf for conf in field_confidences if conf > 0])
```

---

## ✅ Validation

The `validate_metadata()` method checks:

| Check | Description | Critical? |
|-------|-------------|-----------|
| **objeto_present** | Objeto was extracted | ✅ Yes |
| **numero_edital_present** | Edital number was extracted | ✅ Yes |
| **orgao_present** | Agency was extracted | ⚠️ Important |
| **modalidade_present** | Modality was extracted | ⚠️ Important |
| **objeto_confident** | Objeto confidence ≥ 0.70 | ✅ Yes |
| **overall_confident** | Overall confidence ≥ 0.70 | ✅ Yes |

**Example:**
```python
validation = extractor.validate_metadata(metadata)

if not validation["objeto_present"]:
    print("❌ CRITICAL: No objeto found")

if not validation["overall_confident"]:
    print("⚠️ WARNING: Low overall confidence")
```

---

## 🔧 Integration with Document Structurer

### EXECUTE Phase - Step 0 (New)

The metadata extractor runs **before** requirement extraction:

```
EXECUTE Phase:
  Step 0: Extract Metadata (NEW) ← metadata_extractor.py
  Step 1: Extract Text from PDF
  Step 2: Identify Requirements
  Step 3: Categorize Requirements
  Step 4: Assign Priorities
  Step 5: Structure as CSV
```

### Delivery Package

Metadata is saved in the delivery package:

```
data/deliveries/analysis_{edital}_{timestamp}/
├── metadata/
│   ├── plan.yaml
│   ├── edital_metadata.yaml  ← NEW (from metadata_extractor)
│   └── timeline.yaml
```

**edital_metadata.yaml Example:**
```yaml
objeto: "Aquisição de Sistema de Videomonitoramento Urbano"
orgao: "Prefeitura Municipal De São Paulo"
valor_estimado: "R$ 2.500.000,00"
prazo_entrega: "180 dias"
modalidade: "Pregão Eletrônico"
numero_edital: "001/2025"
data_publicacao: "15/01/2025"

confidence_scores:
  objeto: 0.95
  orgao: 0.98
  valor_estimado: 0.90
  prazo_entrega: 0.90
  modalidade: 0.98
  numero_edital: 0.95
  data_publicacao: 0.95

overall_confidence: 0.94
```

---

## 🧪 Testing

### Unit Tests

```bash
python tests/unit/test_metadata_extractor.py
```

**Test Coverage:**
- Pattern matching for each field
- Confidence scoring
- Value cleaning
- Validation logic
- Edge cases (missing fields, malformed values)

### Integration Tests

Metadata extraction is integrated into the main Document Structurer integration tests.

---

## 🚨 Known Limitations

1. **Scanned PDFs:** Requires text-extractable PDFs (no OCR support)
2. **Non-standard formats:** Works best with standard Brazilian edital formats
3. **Multiple values:** If multiple values found (e.g., 2 valores), takes the first
4. **Language:** Optimized for Brazilian Portuguese only

---

## 🔮 Future Enhancements

- [ ] Support for multiple languages (Spanish, English)
- [ ] ML-based extraction (vs pure regex)
- [ ] Table extraction for structured metadata
- [ ] OCR support for scanned documents
- [ ] Auto-correction for common typos

---

## 📚 References

- **Main Agent:** `agents/document_structurer/README.md`
- **Prompt Integration:** `agents/document_structurer/prompt.md`
- **Brazilian Edital Standards:** [Comprasnet Guidelines](https://www.gov.br/compras)

---

**Created:** 2025-11-06
**Version:** 1.0.0
**Status:** ✅ Production Ready
