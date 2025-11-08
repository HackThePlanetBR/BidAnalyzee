"""
Integration Tests for Analysis Pipeline

Tests the complete end-to-end pipeline:
- CSV loading
- Conformity analysis
- Report generation
- Multi-format export
"""

import pytest
from pathlib import Path
import json
import csv
import tempfile
import shutil

from agents.technical_analyst.pipeline import AnalysisPipeline
from agents.technical_analyst import RAGEngine, QueryProcessor
from agents.technical_analyst.report import ConformityReport, ReportExporter


# Mock embeddings for deterministic tests
class MockEmbeddingsManager:
    """Mock embeddings manager for testing"""

    def __init__(self, dimension=384):
        self.dimension = dimension

    def embed_documents(self, texts, show_progress=True):
        """Generate deterministic embeddings based on text hash"""
        import numpy as np

        embeddings = []
        for text in texts:
            # Create deterministic embedding from text hash
            seed = hash(text) % (2**32)
            np.random.seed(seed)
            embedding = np.random.rand(self.dimension).astype('float32')
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding.tolist())
        return embeddings

    def embed_query(self, text):
        """Generate single query embedding"""
        return self.embed_documents([text])[0]


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_knowledge_base():
    """Create temporary knowledge base with mock documents"""
    temp_dir = tempfile.mkdtemp()
    kb_dir = Path(temp_dir) / "knowledge_base"
    kb_dir.mkdir()

    # Create mock knowledge base documents
    documents = {
        "requisitos_tecnicos.md": """# Requisitos Técnicos para Câmeras

## Câmeras IP

As câmeras IP devem atender aos seguintes requisitos:
- Resolução mínima de 4MP (megapixels)
- Suporte a compressão H.265
- Visão noturna com infravermelho
- Proteção IP67

## Armazenamento

O sistema deve armazenar gravações por no mínimo 30 dias.
Redundância de dados é recomendada.
""",
        "documentacao_qualificacao.md": """# Documentação de Qualificação

## Atestados de Capacidade Técnica

As empresas devem apresentar:
- Atestado de capacidade técnica de 2 clientes
- Comprovação de execução de projetos similares
- Certificações técnicas da equipe
""",
        "criterios_pontuacao.md": """# Critérios de Pontuação

## Experiência

- 5 pontos por projeto similar executado
- 3 pontos por certificação técnica
- Máximo de 20 pontos
"""
    }

    for filename, content in documents.items():
        (kb_dir / filename).write_text(content, encoding='utf-8')

    yield kb_dir

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_rag_engine(temp_knowledge_base):
    """Create RAG engine with mocked embeddings and test knowledge base"""
    import tempfile
    from agents.technical_analyst.vector_store import FAISSVectorStore
    from agents.technical_analyst.ingestion_pipeline import IngestionPipeline
    from agents.technical_analyst.config import RAGConfig

    # Create temporary directory for vector store
    temp_index_dir = tempfile.mkdtemp()
    index_path = str(Path(temp_index_dir) / "test_index")

    # Create vector store
    vector_store = FAISSVectorStore(index_path=index_path, dimension=384)

    # Create mock embeddings
    embeddings_manager = MockEmbeddingsManager(dimension=384)

    # Create ingestion pipeline
    ingestion = IngestionPipeline(
        embeddings_manager=embeddings_manager,
        vector_store=vector_store
    )

    # Ingest knowledge base
    docs = ingestion.load_directory(temp_knowledge_base)
    chunks = ingestion.chunk_documents(docs)
    ingestion.ingest_chunks(chunks)

    # Create RAG engine
    rag = RAGEngine(
        vector_store=vector_store,
        embeddings_manager=embeddings_manager,
        ingestion_pipeline=ingestion,
        config=RAGConfig  # Pass the class, not an instance
    )

    return rag


@pytest.fixture
def sample_requirements_csv(temp_output_dir):
    """Create sample requirements CSV file"""
    csv_path = Path(temp_output_dir) / "requirements.csv"

    requirements = [
        {
            'ID': '1',
            'Item': '3.1.1',
            'Descrição': 'Câmeras IP com resolução mínima 4MP e compressão H.265',
            'Categoria': 'Hardware',
            'Prioridade': 'Alta',
            'Página': '12',
            'Confiança': '0.95'
        },
        {
            'ID': '2',
            'Item': '3.1.2',
            'Descrição': 'Sistema de armazenamento com retenção de 30 dias',
            'Categoria': 'Hardware',
            'Prioridade': 'Alta',
            'Página': '13',
            'Confiança': '0.92'
        },
        {
            'ID': '3',
            'Item': '4.2.1',
            'Descrição': 'Atestado de capacidade técnica com 2 clientes',
            'Categoria': 'Qualificação',
            'Prioridade': 'Média',
            'Página': '24',
            'Confiança': '0.88'
        },
        {
            'ID': '4',
            'Item': '5.1.1',
            'Descrição': 'Experiência em projetos similares',
            'Categoria': 'Pontuação',
            'Prioridade': 'Média',
            'Página': '31',
            'Confiança': '0.85'
        },
        {
            'ID': '5',
            'Item': '999',
            'Descrição': 'Sistema de detecção de alienígenas com radar quântico',
            'Categoria': 'Hardware',
            'Prioridade': 'Baixa',
            'Página': '99',
            'Confiança': '0.10'
        }
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ID', 'Item', 'Descrição', 'Categoria', 'Prioridade', 'Página', 'Confiança']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(requirements)

    return csv_path


class TestAnalysisPipeline:
    """Tests for Analysis Pipeline"""

    def test_pipeline_initialization(self, mock_rag_engine, temp_output_dir):
        """Test pipeline initialization"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        assert pipeline.rag is not None
        assert pipeline.query_processor is not None
        assert pipeline.output_dir.exists()

    def test_load_requirements_from_csv(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test loading requirements from CSV"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        requirements, metadata = pipeline._load_requirements_from_csv(
            str(sample_requirements_csv)
        )

        assert len(requirements) == 5
        assert metadata['total_requirements'] == 5
        assert all('descricao' in req for req in requirements)
        assert all('categoria' in req for req in requirements)

    def test_analyze_from_csv(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test complete analysis from CSV"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        report = pipeline.analyze_from_csv(
            str(sample_requirements_csv),
            output_basename="test_analysis",
            export_formats=['json', 'csv']
        )

        # Verify report structure
        assert isinstance(report, ConformityReport)
        assert len(report.requirements) == 5
        assert len(report.analysis_results) == 5

        # Verify summary
        summary = report.get_summary()
        assert summary['total_requirements'] == 5
        assert summary['conforme'] + summary['nao_conforme'] + summary['revisao'] == 5

        # Verify exports were created
        json_file = Path(temp_output_dir) / "test_analysis_analysis.json"
        csv_file = Path(temp_output_dir) / "test_analysis_analysis.csv"

        assert json_file.exists()
        assert csv_file.exists()

    def test_analyze_requirements_direct(
        self,
        mock_rag_engine,
        temp_output_dir
    ):
        """Test analysis with direct requirements (no CSV file)"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        requirements = [
            {
                'id': 'REQ-001',
                'descricao': 'Câmeras IP com resolução 4MP',
                'tipo': 'Técnico',
                'categoria': 'Hardware'
            },
            {
                'id': 'REQ-002',
                'descricao': 'Armazenamento de 30 dias',
                'tipo': 'Técnico',
                'categoria': 'Hardware'
            }
        ]

        report = pipeline.analyze_requirements(
            requirements=requirements,
            metadata={'numero_edital': 'TEST-001'},
            output_basename="test_direct",
            export_formats=['json']
        )

        assert len(report.requirements) == 2
        assert len(report.analysis_results) == 2
        assert report.edital_metadata['numero_edital'] == 'TEST-001'

    def test_report_summary_statistics(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test report summary statistics"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        report = pipeline.analyze_from_csv(
            str(sample_requirements_csv),
            export_formats=[]  # No exports for this test
        )

        summary = report.get_summary()

        # Check all summary fields exist
        assert 'total_requirements' in summary
        assert 'conforme' in summary
        assert 'nao_conforme' in summary
        assert 'revisao' in summary
        assert 'conforme_pct' in summary
        assert 'overall_compliance_rate' in summary

        # Percentages should sum to ~100%
        total_pct = (
            summary['conforme_pct'] +
            summary['nao_conforme_pct'] +
            summary['revisao_pct']
        )
        assert 99.0 <= total_pct <= 101.0  # Allow for rounding

    def test_critical_issues_identification(
        self,
        mock_rag_engine,
        temp_output_dir
    ):
        """Test critical issues identification"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        # Create requirements likely to be non-conformant
        requirements = [
            {
                'id': 'REQ-999',
                'descricao': 'Sistema de teletransporte quântico intergaláctico',
                'tipo': 'Técnico'
            }
        ]

        report = pipeline.analyze_requirements(
            requirements=requirements,
            export_formats=[]
        )

        # This requirement should likely need review or be non-conformant
        assert len(report.analysis_results) == 1
        verdict = report.analysis_results[0].conformity.value
        assert verdict in ['REVISAO', 'NAO_CONFORME']

    def test_export_json(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test JSON export"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        report = pipeline.analyze_from_csv(
            str(sample_requirements_csv),
            output_basename="test_json",
            export_formats=['json']
        )

        json_file = Path(temp_output_dir) / "test_json_analysis.json"
        assert json_file.exists()

        # Verify JSON is valid and complete
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'summary' in data
        assert 'requirements' in data
        assert 'analysis_results' in data
        assert len(data['requirements']) == 5

    def test_export_csv(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test CSV export"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        report = pipeline.analyze_from_csv(
            str(sample_requirements_csv),
            output_basename="test_csv",
            export_formats=['csv']
        )

        csv_file = Path(temp_output_dir) / "test_csv_analysis.csv"
        assert csv_file.exists()

        # Verify CSV structure
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5
        assert 'id' in rows[0]
        assert 'veredicto' in rows[0]
        assert 'confianca' in rows[0]

    def test_export_markdown(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test Markdown export"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        report = pipeline.analyze_from_csv(
            str(sample_requirements_csv),
            output_basename="test_md",
            export_formats=['markdown']
        )

        md_file = Path(temp_output_dir) / "test_md_report.md"
        assert md_file.exists()

        # Verify markdown content
        content = md_file.read_text(encoding='utf-8')
        assert '# Relatório de Análise de Conformidade' in content
        assert '## 📊 Resumo Executivo' in content
        assert 'Total de Requisitos' in content

    def test_pipeline_performance_tracking(
        self,
        mock_rag_engine,
        sample_requirements_csv,
        temp_output_dir
    ):
        """Test pipeline tracks performance statistics"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        pipeline.analyze_from_csv(
            str(sample_requirements_csv),
            export_formats=[]
        )

        stats = pipeline.get_stats()

        # Verify timing stats exist
        assert 'start_time' in stats
        assert 'end_time' in stats
        assert 'total_duration' in stats
        assert 'extraction_time' in stats
        assert 'analysis_time' in stats
        assert 'report_time' in stats

        # Verify timings are reasonable
        assert stats['total_duration'] > 0
        assert stats['analysis_time'] > 0

    def test_empty_csv_handling(
        self,
        mock_rag_engine,
        temp_output_dir
    ):
        """Test handling of empty CSV file"""
        # Create empty CSV
        empty_csv = Path(temp_output_dir) / "empty.csv"
        with open(empty_csv, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ID', 'Descrição'])
            writer.writeheader()
            # No rows

        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        report = pipeline.analyze_from_csv(
            str(empty_csv),
            export_formats=[]
        )

        summary = report.get_summary()
        assert summary['total_requirements'] == 0

    def test_file_not_found_error(
        self,
        mock_rag_engine,
        temp_output_dir
    ):
        """Test error handling for non-existent CSV"""
        pipeline = AnalysisPipeline(
            rag_engine=mock_rag_engine,
            output_dir=temp_output_dir
        )

        with pytest.raises(FileNotFoundError):
            pipeline.analyze_from_csv("nonexistent.csv")
