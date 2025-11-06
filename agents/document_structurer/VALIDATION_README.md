# Validation Rules - Complete Guide

**Version:** 1.1.0
**História:** 2.10 - Additional Validation Rules
**Created:** 2025-11-06

---

## 📋 Overview

The Document Structurer now includes **30 comprehensive validation rules** organized in three tiers:

1. **Framework-wide Rules (16 rules):**
   - 8 Anti-Alucinação (AA-01 to AA-08) - Prevents hallucination
   - 8 Estruturação (ED-01 to ED-08) - Document structure quality

2. **Domain-specific Rules (14 NEW rules):**
   - 6 Legal Compliance (LC-01 to LC-06) - Brazilian procurement law compliance
   - 4 Completeness (CP-01 to CP-04) - Essential information presence
   - 4 Consistency (CS-01 to CS-04) - Internal consistency validation

---

## 🆕 New Validation Rules (História 2.10)

### Legal Compliance Rules (LC-01 to LC-06)

#### LC-01: Lei 8.666/93 - Cláusulas Obrigatórias
**Severity:** 🔴 CRITICAL
**Category:** Legal Compliance

**Description:**
Verifies presence of mandatory clauses required by Lei 8.666/93.

**Required Clauses:**
- ✅ Objeto da licitação (Art. 40, I)
- ✅ Prazo de entrega/execução (Art. 40, III)
- ✅ Sanções administrativas (Art. 40, XVI)
- ✅ Dotação orçamentária (Art. 14)
- ✅ Critério de julgamento (Art. 40, VII)

**Pass Criteria:** All 5 mandatory clauses present
**Fail Criteria:** Any mandatory clause missing

**Example:**
```python
from agents.document_structurer.validation_engine import ValidationEngine

engine = ValidationEngine()
text = """
EDITAL Nº 001/2025

1. OBJETO DA LICITAÇÃO: Aquisição de equipamentos
2. PRAZO DE ENTREGA: 60 dias
3. SANÇÕES: Multa de 10%
4. DOTAÇÃO ORÇAMENTÁRIA: 1234
5. CRITÉRIO DE JULGAMENTO: Menor preço
"""

result = engine.validate_lc01_lei_8666_clauses(text)
print(f"Passed: {result.passed}")  # True
```

**Remediation:**
Add missing clauses according to Lei 8.666/93 requirements.

---

#### LC-02: Lei 14.133/2021 - Compatibilidade
**Severity:** 🟡 WARNING
**Category:** Legal Compliance

**Description:**
Checks if edital references Lei 14.133/2021 (new procurement law) or Lei 8.666/93 (old law).

**Pass Criteria:** References either Lei 14.133/2021 or Lei 8.666/93
**Fail Criteria:** No clear reference to procurement legislation

**Remediation:**
Verify if edital should be updated to Lei 14.133/2021.

---

#### LC-03: Prazos Legais Mínimos
**Severity:** 🔴 CRITICAL
**Category:** Legal Compliance

**Description:**
Verifies that deadlines meet legal minimums by procurement modality.

**Minimum Deadlines by Modality:**

| Modalidade | Prazo Proposta | Prazo Impugnação | Legal Basis |
|------------|----------------|------------------|-------------|
| Pregão Eletrônico | 8 dias úteis | 3 dias úteis | Lei 10.520/2002 |
| Concorrência | 30 dias corridos | 5 dias úteis | Lei 8.666/93 |
| Tomada de Preços | 15 dias corridos | 5 dias úteis | Lei 8.666/93 |

**Example:**
```python
text = """
Modalidade: Pregão Eletrônico
Prazo para propostas: 10 dias úteis  # OK (>= 8)
Prazo para impugnação: 5 dias úteis   # OK (>= 3)
"""

result = engine.validate_lc03_minimum_deadlines(text, modalidade="pregão")
# Passed: True
```

**Remediation:**
Adjust deadlines to meet minimum legal requirements.

---

#### LC-04: Garantia - Requisitos
**Severity:** 🟡 WARNING
**Category:** Legal Compliance

**Description:**
Verifies that bid bond/performance bond requirements are properly defined.

**Required Elements (if garantia is mentioned):**
- ✅ Percentage (typically up to 10% per Lei 8.666/93)
- ✅ Accepted modalities (caução, seguro-garantia, fiança bancária)

**Pass Criteria:** If garantia required, both percentage and modalities defined
**Fail Criteria:** Garantia mentioned without clear criteria

**Remediation:**
Define modalities and percentages per Art. 56 of Lei 8.666/93.

---

#### LC-05: Habilitação Jurídica
**Severity:** 🔴 CRITICAL
**Category:** Legal Compliance

**Description:**
Verifies that juridical qualification requirements are listed.

**Required Documents:**
- ✅ Registro comercial (Commercial registration)
- ✅ Ato constitutivo (Articles of incorporation)
- ✅ Inscrição no CNPJ (Tax ID)
- ✅ Regularidade com FGTS (FGTS compliance)

**Remediation:**
Include all documents required by Lei 8.666/93 (Art. 28-29).

---

#### LC-06: Qualificação Técnica
**Severity:** 🟡 WARNING
**Category:** Legal Compliance

**Description:**
Verifies that technical qualification requirements are present.

**Common Requirements:**
- ✅ Atestado de capacidade técnica (Technical capacity certificate)
- ✅ Responsável técnico habilitado (Qualified technical manager)
- ✅ Certidão de Acervo Técnico - CAT (Technical portfolio certificate)

**Pass Criteria:** At least one technical requirement present
**Fail Criteria:** No technical qualification requirements identified

**Remediation:**
Adjust technical requirements to match procurement object.

---

### Completeness Rules (CP-01 to CP-04)

#### CP-01: Anexos Obrigatórios Referenciados
**Severity:** 🟡 WARNING
**Category:** Completeness

**Description:**
Verifies that all mandatory annexes are referenced.

**Mandatory Annexes:**
- ✅ Termo de Referência / Projeto Básico
- ✅ Minuta do Contrato
- ✅ Modelo de Proposta Comercial
- ✅ Modelo de Declarações

**Remediation:**
List all mandatory annexes with clear identification.

---

#### CP-02: Informações de Contato Completas
**Severity:** 🟡 WARNING
**Category:** Completeness

**Description:**
Verifies presence of contact information for the contracting agency.

**Required Information:**
- ✅ **Telefone** (Phone - REQUIRED)
- ✅ **E-mail** (Email - REQUIRED)
- ⚪ Endereço (Address - Recommended)
- ⚪ Horário de atendimento (Office hours - Recommended)

**Pass Criteria:** At minimum phone AND email present
**Fail Criteria:** Missing phone or email

**Example:**
```python
text = """
CONTATO
Telefone: (11) 1234-5678
E-mail: licitacao@exemplo.gov.br
Endereço: Rua Exemplo, 123
Horário: 9h às 17h
"""

result = engine.validate_cp02_contact_information(text)
# Passed: True
```

---

#### CP-03: Cronograma/Calendário Completo
**Severity:** 🔴 CRITICAL
**Category:** Completeness

**Description:**
Verifies that schedule includes all critical dates.

**Critical Dates:**
- ✅ Data de publicação (Publication date)
- ✅ Prazo para esclarecimentos (Deadline for questions)
- ✅ Data da sessão/abertura (Opening session date)
- ✅ Início da vigência (Contract start date)

**Remediation:**
Include complete schedule with all relevant dates.

---

#### CP-04: Condições de Pagamento Definidas
**Severity:** 🔴 CRITICAL
**Category:** Completeness

**Description:**
Verifies that payment terms and conditions are clearly defined.

**Required Elements:**
- ✅ **Prazo de pagamento** (Payment deadline - REQUIRED)
- ✅ **Forma de pagamento** (Payment method - REQUIRED)
- ⚪ Processo de medição/faturamento (Measurement/billing process)
- ⚪ Critérios de reajuste (Adjustment criteria)

**Pass Criteria:** At minimum prazo AND forma defined
**Fail Criteria:** Missing deadline or payment method

**Example:**
```python
text = """
PAGAMENTO
Prazo: 30 dias após medição
Forma: Transferência bancária
Medição: Conforme Anexo III
Reajuste: IPCA anual
"""

result = engine.validate_cp04_payment_terms(text)
# Passed: True
```

---

### Consistency Rules (CS-01 to CS-04)

#### CS-01: Ordem Cronológica de Datas
**Severity:** 🟡 WARNING
**Category:** Consistency

**Description:**
Verifies that all dates appear in logical chronological order.

**Expected Order:**
1. Data de publicação →
2. Prazo esclarecimentos →
3. Data de abertura →
4. Prazo de entrega →
5. Início de vigência

**Remediation:**
Correct date sequence to proper chronological order.

---

#### CS-02: Soma de Valores (Itens vs. Total)
**Severity:** 🔴 CRITICAL
**Category:** Consistency

**Description:**
Verifies that sum of item values equals declared total value.

**Validation:**
- Sums all individual item values
- Compares with declared total
- Allows 1% tolerance for rounding

**Pass Criteria:** Difference ≤ 1%
**Fail Criteria:** Difference > 1%

**Example:**
```python
result = engine.validate_cs02_value_consistency(
    text,
    item_values=[1000000.0, 800000.0, 700000.0],
    total_value=2500000.0
)
# Sum: 2,500,000 = Total: 2,500,000 → Passed: True
```

**Remediation:**
Correct item values or total value for consistency.

---

#### CS-03: Unidades de Medida Consistentes
**Severity:** 🟡 WARNING
**Category:** Consistency

**Description:**
Verifies that units of measurement are used consistently.

**Common Unit Groups:**
- unidade/un/und/peça
- metro/m/metros
- quilograma/kg/kilo
- litro/l/lt
- hora/h/hrs

**Pass Criteria:** Same measurement type uses same unit
**Fail Criteria:** Same measurement with different units without conversion

**Remediation:**
Standardize units per INMETRO or include conversions.

---

#### CS-04: Referências Cruzadas Válidas
**Severity:** 🟡 WARNING
**Category:** Consistency

**Description:**
Verifies that all cross-references point to existing sections/annexes.

**Validation:**
- Extracts references like "conforme item 3.2", "ver anexo II"
- Checks if referenced sections/annexes exist
- Validates internal links

**Pass Criteria:** All references point to existing sections
**Fail Criteria:** Any broken or invalid reference

**Remediation:**
Correct broken references or add missing sections.

---

## 🔧 Usage

### Basic Usage

```python
from agents.document_structurer.validation_engine import ValidationEngine

# Initialize engine
engine = ValidationEngine()

# Load edital text
with open("edital.txt", "r") as f:
    text = f.read()

# Run all 14 new rules
report = engine.validate_all(text)

# Check results
print(f"Overall Status: {report.overall_status}")
print(f"Passed: {report.rules_passed}/{report.total_rules_checked}")
print(f"Failed (CRITICAL): {report.rules_failed}")
print(f"Warnings: {report.rules_warned}")
```

### Validate by Category

```python
# Validate only legal compliance rules
legal_results = engine.validate_by_category("legal", text)

# Validate only completeness rules
completeness_results = engine.validate_by_category("completeness", text)

# Validate only consistency rules
consistency_results = engine.validate_by_category("consistency", text)
```

### Validate Individual Rules

```python
# Validate specific rule
result = engine.validate_lc01_lei_8666_clauses(text)

if not result.passed:
    print(f"❌ {result.message}")
    print(f"Remediation: {result.remediation}")
else:
    print(f"✅ {result.message}")
```

### Generate Reports

```python
from agents.document_structurer.validation_report import ValidationReportGenerator

generator = ValidationReportGenerator()

# Generate text report (grouped by severity)
text_report = generator.generate_detailed_text(report, group_by="severity")
print(text_report)

# Generate compliance checklist (Markdown)
checklist = generator.generate_compliance_checklist(report)
print(checklist)

# Save reports to files
generator.save_report(report, "validation_report.yaml", format="yaml")
generator.save_report(report, "validation_report.json", format="json")
generator.save_report(report, "compliance_checklist.md", format="markdown")
generator.save_report(report, "validation_report.html", format="html")
```

---

## 📊 Severity Levels

### 🔴 CRITICAL
- **Description:** Violation blocks delivery - requires immediate correction
- **Action:** LOOP (return for correction)
- **Examples:** Missing mandatory clauses, incorrect values

### 🟡 WARNING
- **Description:** Serious issue that should be reviewed before proceeding
- **Action:** Flag for human review
- **Examples:** Missing recommended information, potential compliance issues

### 🔵 INFO
- **Description:** Suggestion for improvement - does not block delivery
- **Action:** Log in report
- **Examples:** Style suggestions, optional enhancements

---

## 🧪 Testing

### Run All Tests

```bash
python tests/unit/test_validation_rules.py
```

**Expected Output:**
```
======================================================================
Validation Rules - Unit Tests
======================================================================

✅ LC-01 Pass Test: PASS
✅ LC-01 Fail Test: PASS
... (30 more tests)

======================================================================
TEST SUMMARY
======================================================================
✅ Passed: 32
❌ Failed: 0
Total: 32
Success Rate: 100.0%
======================================================================
```

### Test Coverage

- **14 rules × 2 tests** (pass/fail) = 28 tests
- **4 integration tests** (comprehensive, categories, severity, false positives)
- **Total: 32 tests** with 100% pass rate

---

## 📂 Files

| File | Purpose | LOC |
|------|---------|-----|
| `validation_rules.yaml` | Rule configuration | ~450 |
| `validation_engine.py` | Rule implementation | ~950 |
| `validation_report.py` | Report generation | ~550 |
| `test_validation_rules.py` | Unit tests | ~650 |
| `VALIDATION_README.md` | This documentation | ~600 |

**Total:** ~3,200 lines of code + documentation

---

## 🎯 Success Metrics

### Performance
- ✅ All 14 rules implemented
- ✅ Total 30 rules (16 existing + 14 new)
- ✅ 100% test coverage (32/32 tests passing)

### Quality
- ✅ Comprehensive pattern matching
- ✅ False positive prevention
- ✅ Clear remediation suggestions
- ✅ Multiple severity levels

### Usability
- ✅ Simple API (3 methods: validate_all, validate_by_category, individual validators)
- ✅ Multiple report formats (YAML, JSON, Text, Markdown, HTML)
- ✅ Detailed error messages
- ✅ Complete documentation

---

## 🔄 Integration with SHIELD Framework

The validation rules integrate seamlessly with the existing SHIELD framework:

```
┌─────────────────────────────────────────┐
│         SHIELD FRAMEWORK                │
├─────────────────────────────────────────┤
│  1. STRUCTURE → Plan extraction         │
│  2. HALT → User approval                │
│  3. EXECUTE → Extract & structure       │
│  4. INSPECT →                           │
│     ├─ AA-01 to AA-08 (Framework)      │
│     ├─ ED-01 to ED-08 (Structure)      │
│     └─ LC/CP/CS-01 to 14 (NEW!)        │ ← História 2.10
│  5. LOOP → Fix issues if any            │
│  6. VALIDATE → Final check              │
│  7. DELIVER → CSV output                │
└─────────────────────────────────────────┘
```

The new rules are applied during the **INSPECT** phase, after basic structure validation (ED-01 to ED-08) and hallucination prevention (AA-01 to AA-08).

---

## 📚 References

- **Lei 8.666/93:** Lei de Licitações e Contratos (old law)
- **Lei 14.133/2021:** Nova Lei de Licitações e Contratos (new law)
- **Lei 10.520/2002:** Lei do Pregão
- **INMETRO:** Instituto Nacional de Metrologia, Qualidade e Tecnologia

---

## 📝 Changelog

### Version 1.1.0 (2025-11-06) - História 2.10
- ✅ Added 6 Legal Compliance rules (LC-01 to LC-06)
- ✅ Added 4 Completeness rules (CP-01 to CP-04)
- ✅ Added 4 Consistency rules (CS-01 to CS-04)
- ✅ Created validation_engine.py with 14 rule implementations
- ✅ Created validation_report.py with 5 output formats
- ✅ Created 32 comprehensive tests (100% passing)
- ✅ Total rules: 16 → 30 (+87.5%)

### Version 1.0.0 (2025-11-06) - Sprint 4
- Initial implementation with 16 rules (AA + ED)

---

**Author:** BidAnalyzee Team
**Contact:** [Project Repository](https://github.com/HackThePlanetBR/BidAnalyzee)
**License:** [License Information]
