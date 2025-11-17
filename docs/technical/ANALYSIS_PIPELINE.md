# Analysis Pipeline - End-to-End Integration

**Status:** ✅ COMPLETO (Sprint 5.3)
**Versão:** 0.3.0
**Data:** 08 de novembro de 2025

---

## 📋 Visão Geral

O **Analysis Pipeline** integra o Document Structurer com o Technical Analyst Query Processor para fornecer análise completa de conformidade end-to-end.

### Pipeline Completo

```
PDF Edital → Document Structurer → Requirements CSV
                                          ↓
                                    Query Processor
                                          ↓
                                    RAG Analysis
                                          ↓
                                 Conformity Report
                                          ↓
                            Export (JSON/CSV/Excel/Markdown)
```

---

## 🚀 Uso Rápido

### Comando CLI

```bash
# Passo 1: Estruturar edital (extrai requisitos)
/structure-edital data/uploads/edital_001.pdf

# Passo 2: Analisar conformidade
/analyze-edital data/deliveries/analysis_edital_001_20250108/outputs/requirements_structured.csv
```

### API Python

```python
from agents.technical_analyst import AnalysisPipeline

# Criar pipeline
pipeline = AnalysisPipeline(output_dir="output/analysis")

# Analisar requirements CSV
report = pipeline.analyze_from_csv(
    "requirements.csv",
    export_formats=['json', 'csv', 'markdown', 'excel']
)

# Ver resumo
summary = report.get_summary()
print(f"Taxa de Conformidade: {summary['overall_compliance_rate']:.1f}%")
print(f"Conformes: {summary['conforme']}")
print(f"Revisão Necessária: {summary['revisao']}")
```

---

## 📦 Componentes

### 1. AnalysisPipeline

Orquestra todo o fluxo end-to-end:

```python
from agents.technical_analyst.pipeline import AnalysisPipeline

pipeline = AnalysisPipeline(
    rag_engine=None,  # Usa default (FAISS local)
    output_dir="output/analysis"
)
```

**Métodos principais:**
- `analyze_from_csv()` - Analisa a partir de CSV do Document Structurer
- `analyze_requirements()` - Analisa lista de requisitos diretamente
- `get_stats()` - Retorna estatísticas de performance

### 2. ConformityReport

Estrutura consolidada do relatório de análise:

```python
from agents.technical_analyst.report import ConformityReport

# Acessar dados do relatório
summary = report.get_summary()
critical_issues = report.get_critical_issues()
review_needed = report.get_review_needed()
recommendations = report.get_recommendations()

# Exportar
json_data = report.to_json()
dict_data = report.to_dict()
```

### 3. ReportExporter

Exporta relatórios em múltiplos formatos:

```python
from agents.technical_analyst.report import ReportExporter

exporter = ReportExporter(report, output_dir="output")

# Exportar em formato específico
json_file = exporter.to_json("analysis")
csv_file = exporter.to_csv("analysis")
excel_file = exporter.to_excel("analysis")  # Requer openpyxl
md_file = exporter.to_markdown("analysis")
```

---

## 📊 Formatos de Export

### JSON (Completo)

Dados estruturados completos incluindo:
- Metadados do edital
- Requisitos extraídos
- Resultados de análise por requisito
- Evidências e fontes
- Estatísticas e recomendações

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
  "timestamp": "2025-11-08T12:00:00"
}
```

### CSV (Tabular)

Formato planilha com uma linha por requisito:

| id | descricao | tipo | categoria | veredicto | confianca | evidencias_count | fontes | reasoning |
|----|-----------|------|-----------|-----------|-----------|------------------|--------|-----------|
| REQ-001 | Câmeras IP 4MP | Técnico | Hardware | CONFORME | 0.92 | 3 | requisitos_tecnicos.md | Requisito em conformidade... |

### Excel (Multi-sheet)

Planilha Excel com 2 abas:
- **Resumo**: Estatísticas gerais
- **Análise Detalhada**: Todos os requisitos com análise

### Markdown (Human-readable)

Relatório formatado para leitura:
- Resumo executivo
- Questões críticas destacadas
- Requisitos necessitando revisão
- Análise detalhada por requisito

---

## 🎯 Veredictos de Conformidade

| Veredicto | Critério | Significado |
|-----------|----------|-------------|
| **CONFORME** | Confiança ≥ 0.85 E Evidências ≥ 2 | Requisito atende documentação |
| **NAO_CONFORME** | Contradiz explicitamente documentação | Requisito não atende |
| **REVISAO** | Confiança < 0.85 OU Evidências < 2 | Requer revisão manual |

**Score de Confiança:**
- Weighted: 70% relevância média + 30% relevância máxima
- Range: 0.0 (sem match) a 1.0 (match perfeito)

---

## ⏱️ Performance

### Métricas Típicas

| Cenário | Requisitos | Tempo Esperado |
|---------|------------|----------------|
| Pequeno | 10-20 | < 30s |
| Médio | 30-50 | < 2 min |
| Grande | 100+ | < 5 min |

### Rastreamento

O pipeline rastreia automaticamente:
- Tempo de carregamento do CSV
- Tempo de análise RAG
- Tempo de geração de relatório
- Tempo total

```python
stats = pipeline.get_stats()
print(f"Tempo total: {stats['total_duration']:.1f}s")
print(f"  Carregamento: {stats['extraction_time']:.1f}s")
print(f"  Análise: {stats['analysis_time']:.1f}s")
print(f"  Relatório: {stats['report_time']:.1f}s")
```

---

## 📖 Exemplos

### Exemplo 1: Análise Básica

```python
from agents.technical_analyst import AnalysisPipeline

pipeline = AnalysisPipeline()

report = pipeline.analyze_from_csv(
    "data/deliveries/analysis_edital_001/outputs/requirements.csv"
)

print(f"Total: {len(report.requirements)} requisitos")
print(f"Conformes: {report.get_summary()['conforme']}")
```

### Exemplo 2: Requisitos Diretos (Sem CSV)

```python
requirements = [
    {'id': 'REQ-001', 'descricao': 'Câmeras 4MP', 'tipo': 'Técnico'},
    {'id': 'REQ-002', 'descricao': 'Armazenamento 30 dias', 'tipo': 'Técnico'}
]

report = pipeline.analyze_requirements(
    requirements=requirements,
    metadata={'numero_edital': '001/2024'},
    export_formats=['json', 'markdown']
)
```

### Exemplo 3: Questões Críticas

```python
# Identificar requisitos não conformes
critical = report.get_critical_issues()

for issue in critical:
    req = issue['requirement']
    analysis = issue['analysis']
    print(f"❌ {req['id']}: {req['descricao']}")
    print(f"   Confiança: {analysis['confidence']:.0%}")
    print(f"   Razão: {analysis['reasoning']}\n")
```

### Exemplo 4: Exportação Customizada

```python
from agents.technical_analyst.report import ReportExporter

exporter = ReportExporter(report, output_dir="reports/custom")

# Exportar apenas formatos específicos
exporter.to_json("edital_001")
exporter.to_markdown("edital_001")

# Excel requer openpyxl
try:
    exporter.to_excel("edital_001")
except ImportError:
    print("Install openpyxl for Excel export")
```

---

## 🔧 Configuração

### RAG Engine

Por padrão usa FAISS local. Para customizar:

```python
from agents.technical_analyst import RAGEngine, AnalysisPipeline

# Criar RAG engine customizado
rag = RAGEngine.from_config()
rag.ingest_knowledge_base("data/knowledge_base/custom")

# Usar no pipeline
pipeline = AnalysisPipeline(rag_engine=rag)
```

### Diretório de Output

```python
pipeline = AnalysisPipeline(output_dir="custom/output/path")
```

---

## 🚨 Tratamento de Erros

### CSV não encontrado

```python
try:
    report = pipeline.analyze_from_csv("nonexistent.csv")
except FileNotFoundError as e:
    print(f"❌ Arquivo não encontrado: {e}")
```

### CSV vazio

```python
report = pipeline.analyze_from_csv("empty.csv")
summary = report.get_summary()

if summary['total_requirements'] == 0:
    print("⚠️ Nenhum requisito encontrado no CSV")
```

### Falha em Export

```python
try:
    pipeline.analyze_from_csv("requirements.csv", export_formats=['excel'])
except ImportError:
    print("⚠️ openpyxl não instalado. Use: pip install openpyxl")
```

---

## 📚 Integração com Document Structurer

### Workflow Completo

```bash
# 1. Estruturar edital
/structure-edital editais/edital_pmsp_001.pdf

# Output: data/deliveries/analysis_edital_pmsp_001_20250108/outputs/requirements_structured.csv

# 2. Analisar conformidade
/analyze-edital data/deliveries/analysis_edital_pmsp_001_20250108/outputs/requirements_structured.csv --formats json,csv,markdown,excel

# Outputs em output/analysis/:
# - edital_pmsp_001_analysis.json
# - edital_pmsp_001_analysis.csv
# - edital_pmsp_001_analysis.xlsx
# - edital_pmsp_001_report.md
```

### Formatos CSV Suportados

O pipeline aceita CSVs do Document Structurer com os seguintes campos:

**Obrigatórios:**
- `ID` ou `id`: Identificador do requisito
- `Descrição` ou `descricao`: Texto do requisito

**Opcionais:**
- `Item`: Número do item no edital
- `Categoria` ou `categoria`: Hardware/Software/etc
- `Prioridade` ou `prioridade`: Alta/Média/Baixa
- `Página` ou `pagina`: Página de origem
- `Confiança` ou `confianca`: Score de confiança

---

## ✅ Sprint 5.3 - Definition of Done

- [x] AnalysisPipeline implementado
- [x] ConformityReport e ReportExporter funcionais
- [x] Integração com Document Structurer CSV
- [x] 4 formatos de export (JSON, CSV, Excel, Markdown)
- [x] Comando `/analyze-edital` implementado
- [x] Testes de integração criados
- [x] Documentação completa
- [x] Performance tracking
- [x] Error handling robusto

---

## 🎯 Próximos Passos

**Sprint 5.4 (Futuro):**
- Dashboard web para visualização de resultados
- Integração com banco de dados para histórico
- APIs REST para análise remota
- Análise comparativa entre múltiplos editais

---

**Última atualização:** 08 de novembro de 2025
**Versão:** 0.3.0
**Status:** ✅ Production Ready
