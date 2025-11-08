"""
Analysis Pipeline - End-to-End Integration

Integrates Document Structurer output with Technical Analyst Query Processor
to provide complete edital conformity analysis.

This module provides:
- AnalysisPipeline: Orchestrates extraction → analysis → reporting
- Integration with Document Structurer CSV outputs
- Batch conformity analysis
- Multi-format report generation
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import csv
from datetime import datetime
import time

from agents.technical_analyst import QueryProcessor, RAGEngine
from agents.technical_analyst.report import ConformityReport, ReportExporter


class AnalysisPipeline:
    """
    End-to-end pipeline for edital analysis

    Integrates Document Structurer (requirement extraction) with
    Technical Analyst (conformity analysis) to provide complete
    analysis from structured requirements to conformity report.

    Example:
        >>> pipeline = AnalysisPipeline()
        >>> report = pipeline.analyze_from_csv("requirements.csv")
        >>> print(f"Conformity: {report.get_summary()['overall_compliance_rate']:.1f}%")
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

    def analyze_from_csv(
        self,
        csv_path: str,
        output_basename: Optional[str] = None,
        export_formats: List[str] = ['json', 'csv', 'markdown']
    ) -> ConformityReport:
        """
        Analyze requirements from Document Structurer CSV output

        Args:
            csv_path: Path to structured requirements CSV
            output_basename: Base name for output files (default: CSV filename)
            export_formats: List of export formats ('json', 'csv', 'excel', 'markdown')

        Returns:
            ConformityReport with complete analysis

        Example:
            >>> pipeline = AnalysisPipeline()
            >>> report = pipeline.analyze_from_csv("output/requirements.csv")
        """
        self.stats['start_time'] = time.time()

        print(f"\n{'='*70}")
        print(f"🔍 ANÁLISE DE CONFORMIDADE - PIPELINE COMPLETO")
        print(f"{'='*70}")
        print(f"📄 CSV de Requisitos: {csv_path}")
        print(f"{'='*70}\n")

        # Stage 1: Load requirements from CSV
        print("📋 ETAPA 1/3: Carregamento de Requisitos")
        load_start = time.time()
        requirements, metadata = self._load_requirements_from_csv(csv_path)
        self.stats['extraction_time'] = time.time() - load_start

        print(f"✅ Carregados: {len(requirements)} requisitos")
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
            output_basename = Path(csv_path).stem

        self._export(report, output_basename, export_formats)

        # Print summary
        self._print_summary(report)

        return report

    def analyze_requirements(
        self,
        requirements: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        output_basename: str = "analysis",
        export_formats: List[str] = ['json', 'csv', 'markdown']
    ) -> ConformityReport:
        """
        Analyze requirements directly (without CSV file)

        Useful for:
        - Testing with mock data
        - Integration with other systems
        - Custom requirement sources

        Args:
            requirements: List of requirement dictionaries
            metadata: Optional edital metadata
            output_basename: Base name for output files
            export_formats: List of export formats

        Returns:
            ConformityReport with complete analysis

        Example:
            >>> requirements = [
            ...     {'id': 'REQ-001', 'descricao': 'Câmeras IP 4MP', 'tipo': 'Técnico'},
            ...     {'id': 'REQ-002', 'descricao': 'Armazenamento 30 dias', 'tipo': 'Técnico'}
            ... ]
            >>> report = pipeline.analyze_requirements(requirements)
        """
        self.stats['start_time'] = time.time()

        print(f"\n{'='*70}")
        print(f"🔍 ANÁLISE DE CONFORMIDADE - REQUISITOS DIRETOS")
        print(f"{'='*70}")
        print(f"📋 Total de Requisitos: {len(requirements)}")
        print(f"{'='*70}\n")

        # Analyze conformity
        print("🔍 Análise de Conformidade (RAG)")
        analysis_start = time.time()
        analysis_results = self._analyze_conformity(requirements)
        self.stats['analysis_time'] = time.time() - analysis_start

        print(f"✅ Analisados: {len(analysis_results)} requisitos")
        print(f"⏱️  Tempo: {self.stats['analysis_time']:.1f}s\n")

        # Generate report
        print("📊 Geração de Relatório")
        report_start = time.time()
        report = self._generate_report(metadata or {}, requirements, analysis_results)
        self.stats['report_time'] = time.time() - report_start

        self.stats['end_time'] = time.time()
        self.stats['total_duration'] = self.stats['end_time'] - self.stats['start_time']

        print(f"✅ Relatório gerado")
        print(f"⏱️  Tempo: {self.stats['report_time']:.1f}s\n")

        # Export
        self._export(report, output_basename, export_formats)

        # Print summary
        self._print_summary(report)

        return report

    def _load_requirements_from_csv(
        self,
        csv_path: str
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Load requirements from Document Structurer CSV output

        Expected CSV format (from Document Structurer):
        - ID: Sequential ID
        - Item: Original edital item number
        - Descrição: Requirement text
        - Categoria: Hardware/Software/Serviço/Integração
        - Prioridade: Alta/Média/Baixa
        - Página: Source page
        - Confiança: Confidence score (0.0-1.0)

        Args:
            csv_path: Path to CSV file

        Returns:
            Tuple of (requirements_list, metadata_dict)
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        requirements = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Normalize field names (handle variations)
                requirement = {
                    'id': row.get('ID') or row.get('id') or '',
                    'descricao': row.get('Descrição') or row.get('descricao') or row.get('Descricao') or '',
                    'tipo': 'Técnico',  # Default type
                    'categoria': row.get('Categoria') or row.get('categoria') or '',
                    'prioridade': row.get('Prioridade') or row.get('prioridade') or '',
                    'item': row.get('Item') or row.get('item') or '',
                    'pagina': row.get('Página') or row.get('Pagina') or row.get('pagina') or '',
                    'confianca': row.get('Confiança') or row.get('Confianca') or row.get('confianca') or ''
                }

                requirements.append(requirement)

        # Extract metadata from CSV path (if from Document Structurer delivery)
        metadata = {
            'source_file': csv_file.name,
            'source_path': str(csv_file),
            'total_requirements': len(requirements)
        }

        # Try to extract edital info from path (if structured delivery)
        # Example: data/deliveries/analysis_edital_001_20250108/outputs/requirements.csv
        path_parts = csv_file.parts
        if 'deliveries' in path_parts:
            try:
                delivery_folder_idx = path_parts.index('deliveries') + 1
                if delivery_folder_idx < len(path_parts):
                    delivery_folder = path_parts[delivery_folder_idx]
                    # Extract from folder name: analysis_{edital_name}_{timestamp}
                    if delivery_folder.startswith('analysis_'):
                        parts = delivery_folder.split('_')
                        if len(parts) >= 2:
                            metadata['numero_edital'] = '_'.join(parts[1:-1])
                            metadata['timestamp'] = parts[-1]
            except (ValueError, IndexError):
                pass

        return requirements, metadata

    def _analyze_conformity(self, requirements: List[Dict]) -> List[Any]:
        """
        Analyze conformity using Query Processor

        Args:
            requirements: List of requirement dictionaries

        Returns:
            List of ConformityAnalysis objects
        """
        return self.query_processor.analyze_batch(
            requirements,
            show_progress=True
        )

    def _generate_report(
        self,
        metadata: Dict,
        requirements: List[Dict],
        analysis_results: List[Any]
    ) -> ConformityReport:
        """
        Generate consolidated report

        Args:
            metadata: Edital metadata
            requirements: List of requirements
            analysis_results: List of ConformityAnalysis objects

        Returns:
            ConformityReport object
        """
        return ConformityReport(
            edital_metadata=metadata,
            requirements=requirements,
            analysis_results=analysis_results,
            timestamp=datetime.now().isoformat(),
            pipeline_stats=self.stats
        )

    def _export(
        self,
        report: ConformityReport,
        basename: str,
        formats: List[str]
    ):
        """
        Export report in multiple formats

        Args:
            report: ConformityReport to export
            basename: Base filename
            formats: List of export formats
        """
        exporter = ReportExporter(report, self.output_dir)

        print(f"💾 EXPORTANDO RESULTADOS")
        print(f"{'='*70}")

        for fmt in formats:
            try:
                filepath = exporter.export(basename, fmt)
                print(f"  ✅ {fmt.upper()}: {filepath}")
            except Exception as e:
                print(f"  ❌ {fmt.upper()}: Error - {e}")

        print(f"{'='*70}\n")

    def _print_summary(self, report: ConformityReport):
        """
        Print analysis summary to console

        Args:
            report: ConformityReport to summarize
        """
        summary = report.get_summary()

        print(f"{'='*70}")
        print(f"📊 RESUMO DA ANÁLISE DE CONFORMIDADE")
        print(f"{'='*70}")
        print(f"📋 Total de Requisitos: {summary['total_requirements']}")
        print(f"✅ Conformes: {summary['conforme']} ({summary['conforme_pct']:.1f}%)")
        print(f"❌ Não Conformes: {summary['nao_conforme']} ({summary['nao_conforme_pct']:.1f}%)")
        print(f"⚠️  Revisão Necessária: {summary['revisao']} ({summary['revisao_pct']:.1f}%)")
        print(f"")
        print(f"📈 Taxa de Conformidade Geral: {summary['overall_compliance_rate']:.1f}%")
        print(f"{'='*70}")
        print(f"⏱️  Tempo Total: {self.stats['total_duration']:.1f}s")
        print(f"   ├─ Carregamento: {self.stats.get('extraction_time', 0):.1f}s")
        print(f"   ├─ Análise: {self.stats.get('analysis_time', 0):.1f}s")
        print(f"   └─ Relatório: {self.stats.get('report_time', 0):.1f}s")
        print(f"{'='*70}\n")

        # Show critical issues if any
        critical = report.get_critical_issues()
        if critical:
            print(f"🚨 QUESTÕES CRÍTICAS ({len(critical)}):")
            for item in critical[:5]:  # Show first 5
                req = item['requirement']
                print(f"  ❌ {req.get('id', 'N/A')}: {req.get('descricao', 'N/A')[:60]}...")
            if len(critical) > 5:
                print(f"  ... e mais {len(critical) - 5} requisitos não conformes")
            print()

        # Show recommendations
        recommendations = report.get_recommendations()
        if recommendations:
            print(f"💡 RECOMENDAÇÕES PRINCIPAIS:")
            for rec in list(set(recommendations))[:5]:  # Show first 5 unique
                print(f"  • {rec}")
            print()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline execution statistics

        Returns:
            Dictionary with timing and performance statistics
        """
        return {
            **self.stats,
            'query_processor_stats': self.query_processor.get_stats()
        }
