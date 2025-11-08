# Sprint 5.3 Plan - Integration Pipeline (Document Structurer + Technical Analyst)

**Data de Início:** 08 de novembro de 2025
**Duração Estimada:** 10-12 horas
**Objetivo:** Criar pipeline end-to-end integrando Document Structurer com Query Processor

---

## 🎯 Objetivo da História

Implementar a **História 5.3 - Integration Pipeline**, que:
1. Integra Document Structurer (extração de requisitos) com Query Processor (análise)
2. Cria pipeline completo: PDF → Extração → Análise RAG → Relatório
3. Implementa análise de conformidade batch para todos os requisitos
4. Gera relatórios consolidados com veredictos e evidências
5. Fornece comando `/analyze-edital` para análise completa

---

## 📋 Critérios de Aceitação

- [ ] Classe `AnalysisPipeline` implementada
- [ ] Integração Document Structurer → Query Processor funcional
- [ ] Análise batch de requisitos contra knowledge base
- [ ] Relatório consolidado com estrutura + análise
- [ ] Exportação em múltiplos formatos (CSV, JSON, Excel, Markdown)
- [ ] Comando `/analyze-edital` funcional
- [ ] Testes de integração end-to-end
- [ ] Documentação completa do pipeline
- [ ] Performance aceitável (< 5min para edital típico)

---

## 🏗️ Arquitetura

### Pipeline End-to-End

```
┌────────────────────────────────────────────────────────┐
│                  ANALYZE EDITAL                        │
│                                                        │
│  1️⃣ Document Structurer                               │
│     PDF Input → Text Extraction → Requirements        │
│     ├── OCR (if needed)                               │
│     ├── Metadata Extraction                           │
│     └── Structured CSV Output                         │
│                    │                                   │
│                    ▼                                   │
│  2️⃣ Technical Analyst (Query Processor)               │
│     Requirements → RAG Search → Conformity Analysis   │
│     ├── Batch Processing                              │
│     ├── Evidence Extraction                           │
│     └── Verdict Generation                            │
│                    │                                   │
│                    ▼                                   │
│  3️⃣ Report Generator                                  │
│     Analysis Results → Consolidated Report            │
│     ├── CSV (requirements + verdicts)                 │
│     ├── JSON (full analysis)                          │
│     ├── Excel (multi-sheet)                           │
│     └── Markdown (human-readable)                     │
└────────────────────────────────────────────────────────┘
```

### Componentes

```python
# New components for Sprint 5.3

AnalysisPipeline
├── analyze_edital()           # Main entry point
├── _extract_requirements()    # Document Structurer integration
├── _analyze_conformity()      # Query Processor integration
├── _generate_report()         # Report generation
└── _export()                  # Multi-format export

ConformityReport
├── summary                    # High-level stats
├── requirements               # Structured requirements
├── analysis_results           # Conformity analysis per requirement
├── evidence                   # All evidence collected
└── recommendations            # Consolidated recommendations

ReportExporter
├── to_csv()                   # Enhanced CSV with analysis
├── to_json()                  # Complete JSON export
├── to_excel()                 # Multi-sheet Excel
└── to_markdown()              # Human-readable report
```

---

## 📊 Estrutura de Dados

### Input (PDF Edital)
```
edital_123.pdf (50 pages, 2MB)
```

### Stage 1 Output (Document Structurer)
```python
{
    "metadata": {
        "numero_edital": "001/2024",
        "orgao": "Prefeitura Municipal",
        "modalidade": "Pregão Eletrônico",
        ...
    },
    "requirements": [
        {
            "id": "REQ-001",
            "descricao": "Câmeras IP com resolução mínima 4MP",
            "tipo": "Técnico",
            "categoria": "Hardware",
            "prioridade": "Alta",
            "fonte": "Item 3.1.2",
            "pagina": 12
        },
        # ... 50 requirements
    ]
}
```

### Stage 2 Output (Query Processor)
```python
{
    "requirement_id": "REQ-001",
    "conformity": "CONFORME",
    "confidence": 0.92,
    "evidence": [
        {
            "source": "requisitos_tecnicos.md",
            "text": "Câmeras IP devem ter resolução mínima de 4MP...",
            "relevance": 0.94
        }
    ],
    "reasoning": "O requisito está em conformidade...",
    "recommendations": ["✅ Requisito validado"]
}
```

### Final Output (Consolidated Report)
```python
{
    "edital_info": {...},
    "summary": {
        "total_requirements": 50,
        "conforme": 35,
        "nao_conforme": 2,
        "revisao": 13,
        "overall_compliance": "70%"
    },
    "detailed_analysis": [
        {
            "requirement": {...},
            "analysis": {...},
            "verdict": "CONFORME",
            "confidence": 0.92
        }
    ],
    "recommendations": [
        "13 requisitos necessitam revisão manual",
        "2 requisitos identificados como não conformes"
    ]
}
```

---

## 🔧 Implementação

### 1. AnalysisPipeline (agents/technical_analyst/pipeline.py)

```python
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from agents.document_structurer.document_structurer import DocumentStructurer
from agents.technical_analyst import QueryProcessor, RAGEngine
from agents.technical_analyst.report import ConformityReport, ReportExporter


class AnalysisPipeline:
    """
    End-to-end pipeline for edital analysis

    Integrates Document Structurer and Technical Analyst to provide
    complete analysis from PDF to conformity report.
    """

    def __init__(
        self,
        rag_engine: Optional[RAGEngine] = None,
        output_dir: str = "output/analysis"
    ):
        """
        Initialize analysis pipeline

        Args:
            rag_engine: RAG engine (will create default if not provided)
            output_dir: Directory for output files
        """
        # Initialize components
        self.structurer = DocumentStructurer()
        self.rag = rag_engine or RAGEngine.from_config()
        self.query_processor = QueryProcessor(self.rag)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_duration': None,
            'extraction_time': None,
            'analysis_time': None,
            'report_time': None
        }

    def analyze_edital(
        self,
        pdf_path: str,
        output_basename: Optional[str] = None,
        export_formats: List[str] = ['json', 'csv', 'markdown']
    ) -> ConformityReport:
        """
        Analyze edital PDF end-to-end

        Args:
            pdf_path: Path to edital PDF
            output_basename: Base name for output files (default: PDF filename)
            export_formats: List of export formats ('json', 'csv', 'excel', 'markdown')

        Returns:
            ConformityReport with complete analysis
        """
        import time
        self.stats['start_time'] = time.time()

        print(f"\n{'='*70}")
        print(f"🔍 ANÁLISE COMPLETA DE EDITAL")
        print(f"{'='*70}")
        print(f"📄 Arquivo: {pdf_path}")
        print(f"{'='*70}\n")

        # Stage 1: Extract requirements
        print("📋 ETAPA 1/3: Extração de Requisitos")
        extraction_start = time.time()
        structured_data = self._extract_requirements(pdf_path)
        self.stats['extraction_time'] = time.time() - extraction_start

        requirements = structured_data.get('requirements', [])
        metadata = structured_data.get('metadata', {})

        print(f"✅ Extraídos: {len(requirements)} requisitos")
        print(f"⏱️  Tempo: {self.stats['extraction_time']:.1f}s\n")

        # Stage 2: Analyze conformity
        print("🔍 ETAPA 2/3: Análise de Conformidade (RAG)")
        analysis_start = time.time()
        analysis_results = self._analyze_conformity(requirements)
        self.stats['analysis_time'] = time.time() - analysis_start

        print(f"✅ Analisados: {len(analysis_results)} requisitos")
        print(f"⏱️  Tempo: {self.stats['analysis_time']:.1f}s\n")

        # Stage 3: Generate report
        print("📊 ETAPA 3/3: Geração de Relatório")
        report_start = time.time()
        report = self._generate_report(metadata, requirements, analysis_results)
        self.stats['report_time'] = time.time() - report_start

        self.stats['end_time'] = time.time()
        self.stats['total_duration'] = self.stats['end_time'] - self.stats['start_time']

        print(f"✅ Relatório gerado")
        print(f"⏱️  Tempo: {self.stats['report_time']:.1f}s\n")

        # Export
        if output_basename is None:
            output_basename = Path(pdf_path).stem

        self._export(report, output_basename, export_formats)

        # Print summary
        self._print_summary(report)

        return report

    def _extract_requirements(self, pdf_path: str) -> Dict[str, Any]:
        """Extract requirements using Document Structurer"""
        # Use Document Structurer to extract
        result = self.structurer.structure_document(pdf_path)
        return result

    def _analyze_conformity(self, requirements: List[Dict]) -> List[Any]:
        """Analyze conformity using Query Processor"""
        # Batch analyze all requirements
        return self.query_processor.analyze_batch(
            requirements,
            show_progress=True
        )

    def _generate_report(
        self,
        metadata: Dict,
        requirements: List[Dict],
        analysis_results: List[Any]
    ) -> 'ConformityReport':
        """Generate consolidated report"""
        return ConformityReport(
            edital_metadata=metadata,
            requirements=requirements,
            analysis_results=analysis_results,
            timestamp=datetime.now().isoformat(),
            pipeline_stats=self.stats
        )

    def _export(
        self,
        report: 'ConformityReport',
        basename: str,
        formats: List[str]
    ):
        """Export report in multiple formats"""
        exporter = ReportExporter(report, self.output_dir)

        print(f"💾 EXPORTANDO RESULTADOS")
        print(f"{'='*70}")

        for fmt in formats:
            filepath = exporter.export(basename, fmt)
            print(f"  ✅ {fmt.upper()}: {filepath}")

        print(f"{'='*70}\n")

    def _print_summary(self, report: 'ConformityReport'):
        """Print analysis summary"""
        summary = report.get_summary()

        print(f"{'='*70}")
        print(f"📊 RESUMO DA ANÁLISE")
        print(f"{'='*70}")
        print(f"📋 Total de Requisitos: {summary['total_requirements']}")
        print(f"✅ Conformes: {summary['conforme']} ({summary['conforme_pct']:.1f}%)")
        print(f"❌ Não Conformes: {summary['nao_conforme']} ({summary['nao_conforme_pct']:.1f}%)")
        print(f"⚠️  Revisão Necessária: {summary['revisao']} ({summary['revisao_pct']:.1f}%)")
        print(f"{'='*70}")
        print(f"⏱️  Tempo Total: {self.stats['total_duration']:.1f}s")
        print(f"{'='*70}\n")
```

### 2. ConformityReport (agents/technical_analyst/report.py)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime
import json


@dataclass
class ConformityReport:
    """Consolidated conformity report"""

    edital_metadata: Dict[str, Any]
    requirements: List[Dict[str, Any]]
    analysis_results: List[Any]  # List[ConformityAnalysis]
    timestamp: str
    pipeline_stats: Dict[str, Any] = field(default_factory=dict)

    def get_summary(self) -> Dict[str, Any]:
        """Get high-level summary statistics"""
        total = len(self.analysis_results)
        conforme = sum(1 for r in self.analysis_results if r.conformity.value == 'CONFORME')
        nao_conforme = sum(1 for r in self.analysis_results if r.conformity.value == 'NAO_CONFORME')
        revisao = sum(1 for r in self.analysis_results if r.conformity.value == 'REVISAO')

        return {
            'total_requirements': total,
            'conforme': conforme,
            'nao_conforme': nao_conforme,
            'revisao': revisao,
            'conforme_pct': (conforme / total * 100) if total > 0 else 0,
            'nao_conforme_pct': (nao_conforme / total * 100) if total > 0 else 0,
            'revisao_pct': (revisao / total * 100) if total > 0 else 0
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'edital_metadata': self.edital_metadata,
            'summary': self.get_summary(),
            'requirements': self.requirements,
            'analysis_results': [r.to_dict() for r in self.analysis_results],
            'timestamp': self.timestamp,
            'pipeline_stats': self.pipeline_stats
        }

    def to_json(self, indent=2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
```

### 3. ReportExporter (agents/technical_analyst/report.py)

```python
import csv
from pathlib import Path
from typing import List, Dict, Any


class ReportExporter:
    """Export conformity reports in multiple formats"""

    def __init__(self, report: ConformityReport, output_dir: Path):
        self.report = report
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, basename: str, format: str) -> Path:
        """
        Export report in specified format

        Args:
            basename: Base filename (without extension)
            format: Export format ('json', 'csv', 'excel', 'markdown')

        Returns:
            Path to exported file
        """
        if format == 'json':
            return self.to_json(basename)
        elif format == 'csv':
            return self.to_csv(basename)
        elif format == 'excel':
            return self.to_excel(basename)
        elif format == 'markdown':
            return self.to_markdown(basename)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_json(self, basename: str) -> Path:
        """Export as JSON"""
        filepath = self.output_dir / f"{basename}_analysis.json"
        filepath.write_text(self.report.to_json(), encoding='utf-8')
        return filepath

    def to_csv(self, basename: str) -> Path:
        """Export as CSV (requirements + analysis)"""
        filepath = self.output_dir / f"{basename}_analysis.csv"

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'id', 'descricao', 'tipo', 'categoria', 'prioridade',
                'veredicto', 'confianca', 'evidencias_count', 'reasoning'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for req, analysis in zip(self.report.requirements, self.report.analysis_results):
                writer.writerow({
                    'id': req.get('id', ''),
                    'descricao': req.get('descricao', ''),
                    'tipo': req.get('tipo', ''),
                    'categoria': req.get('categoria', ''),
                    'prioridade': req.get('prioridade', ''),
                    'veredicto': analysis.conformity.value,
                    'confianca': f"{analysis.confidence:.2f}",
                    'evidencias_count': len(analysis.evidence),
                    'reasoning': analysis.reasoning
                })

        return filepath

    def to_markdown(self, basename: str) -> Path:
        """Export as Markdown report"""
        filepath = self.output_dir / f"{basename}_report.md"

        summary = self.report.get_summary()

        md = f"""# Relatório de Análise de Conformidade

**Edital:** {self.report.edital_metadata.get('numero_edital', 'N/A')}
**Órgão:** {self.report.edital_metadata.get('orgao', 'N/A')}
**Data da Análise:** {self.report.timestamp}

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| Total de Requisitos | {summary['total_requirements']} |
| ✅ Conformes | {summary['conforme']} ({summary['conforme_pct']:.1f}%) |
| ❌ Não Conformes | {summary['nao_conforme']} ({summary['nao_conforme_pct']:.1f}%) |
| ⚠️ Revisão Necessária | {summary['revisao']} ({summary['revisao_pct']:.1f}%) |

---

## 📋 Análise Detalhada

"""

        for req, analysis in zip(self.report.requirements, self.report.analysis_results):
            verdict_emoji = {
                'CONFORME': '✅',
                'NAO_CONFORME': '❌',
                'REVISAO': '⚠️'
            }.get(analysis.conformity.value, '❓')

            md += f"""
### {verdict_emoji} {req.get('id', 'N/A')}: {req.get('descricao', 'N/A')}

- **Tipo:** {req.get('tipo', 'N/A')}
- **Categoria:** {req.get('categoria', 'N/A')}
- **Veredicto:** {analysis.conformity.value}
- **Confiança:** {analysis.confidence:.0%}
- **Evidências:** {len(analysis.evidence)} fonte(s)

**Raciocínio:** {analysis.reasoning}

**Recomendações:**
{chr(10).join(f"- {rec}" for rec in analysis.recommendations)}

---

"""

        filepath.write_text(md, encoding='utf-8')
        return filepath

    def to_excel(self, basename: str) -> Path:
        """Export as Excel (requires openpyxl)"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            raise ImportError("openpyxl required for Excel export. Install with: pip install openpyxl")

        filepath = self.output_dir / f"{basename}_analysis.xlsx"
        wb = openpyxl.Workbook()

        # Sheet 1: Summary
        ws_summary = wb.active
        ws_summary.title = "Resumo"
        summary = self.report.get_summary()

        ws_summary['A1'] = "Métrica"
        ws_summary['B1'] = "Valor"
        ws_summary['A1'].font = Font(bold=True)
        ws_summary['B1'].font = Font(bold=True)

        ws_summary['A2'] = "Total de Requisitos"
        ws_summary['B2'] = summary['total_requirements']
        ws_summary['A3'] = "Conformes"
        ws_summary['B3'] = summary['conforme']
        ws_summary['A4'] = "Não Conformes"
        ws_summary['B4'] = summary['nao_conforme']
        ws_summary['A5'] = "Revisão Necessária"
        ws_summary['B5'] = summary['revisao']

        # Sheet 2: Detailed Analysis
        ws_detail = wb.create_sheet("Análise Detalhada")
        headers = ['ID', 'Descrição', 'Tipo', 'Categoria', 'Veredicto', 'Confiança', 'Evidências', 'Raciocínio']
        ws_detail.append(headers)

        for cell in ws_detail[1]:
            cell.font = Font(bold=True)

        for req, analysis in zip(self.report.requirements, self.report.analysis_results):
            ws_detail.append([
                req.get('id', ''),
                req.get('descricao', ''),
                req.get('tipo', ''),
                req.get('categoria', ''),
                analysis.conformity.value,
                analysis.confidence,
                len(analysis.evidence),
                analysis.reasoning
            ])

        wb.save(filepath)
        return filepath
```

---

## 📦 Comando /analyze-edital

```python
# .claude/commands/analyze-edital.md

You are helping analyze a public procurement edital (PDF) using the BidAnalyzee system.

The analysis pipeline performs:
1. Document Structurer: Extract requirements from PDF
2. Technical Analyst: Analyze conformity against knowledge base using RAG
3. Report Generator: Create consolidated reports

Usage:
```
/analyze-edital <path-to-pdf> [options]
```

Options:
- `--formats csv,json,markdown,excel` - Export formats (default: json,csv,markdown)
- `--output-dir <path>` - Output directory (default: output/analysis)

Example:
```
/analyze-edital editais/edital_001.pdf --formats json,csv,markdown
```

Implementation:
1. Use AnalysisPipeline.analyze_edital() to process the PDF
2. Display progress and summary
3. Report output file locations
```

---

## 🧪 Testes

### Integration Test (tests/integration/test_analysis_pipeline.py)

```python
import pytest
from pathlib import Path
from agents.technical_analyst.pipeline import AnalysisPipeline


class TestAnalysisPipeline:
    """Integration tests for analysis pipeline"""

    @pytest.fixture
    def pipeline(self, mock_rag_engine):
        """Create pipeline with mocked RAG"""
        return AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir="output/test"
        )

    def test_full_pipeline_mock_pdf(self, pipeline, sample_pdf):
        """Test complete pipeline with mock PDF"""
        report = pipeline.analyze_edital(
            sample_pdf,
            export_formats=['json', 'csv']
        )

        assert report is not None
        assert len(report.requirements) > 0
        assert len(report.analysis_results) == len(report.requirements)

        summary = report.get_summary()
        assert summary['total_requirements'] > 0
        assert summary['conforme'] + summary['nao_conforme'] + summary['revisao'] == summary['total_requirements']
```

---

## 📊 Métricas de Sucesso

| Métrica | Target |
|---------|--------|
| Tempo total (50 reqs) | < 5 minutos |
| Taxa de sucesso | 100% (sem crashes) |
| Cobertura de testes | > 85% |
| Formatos de export | 4 (JSON, CSV, Excel, Markdown) |
| Integração | Document Structurer + Query Processor |

---

## ✅ Definition of Done

- [ ] `AnalysisPipeline` implementado e testado
- [ ] `ConformityReport` e `ReportExporter` funcionais
- [ ] Integração end-to-end funcional
- [ ] 4 formatos de export (JSON, CSV, Excel, Markdown)
- [ ] Comando `/analyze-edital` implementado
- [ ] Testes de integração passando
- [ ] Documentação completa
- [ ] Performance < 5min para edital típico
- [ ] Código commitado e pushed

---

**Status:** 🚀 Ready to Start
**Próximo Passo:** Implementar AnalysisPipeline
**Data:** 08 de novembro de 2025
