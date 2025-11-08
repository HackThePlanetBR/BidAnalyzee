"""
Unit Tests for Query Processor

Tests the Query Processor component in isolation using mocked RAG Engine.
"""

import pytest
from unittest.mock import Mock, MagicMock
from agents.technical_analyst.query_processor import (
    QueryProcessor,
    ConformityVerdict,
    ConformityAnalysis,
    Evidence
)


class TestEvidence:
    """Tests for Evidence dataclass"""

    def test_evidence_creation(self):
        """Test Evidence object creation"""
        evidence = Evidence(
            source="test.md",
            text="Sample text",
            relevance=0.85,
            chunk_index=0
        )

        assert evidence.source == "test.md"
        assert evidence.text == "Sample text"
        assert evidence.relevance == 0.85
        assert evidence.chunk_index == 0

    def test_evidence_to_dict(self):
        """Test Evidence conversion to dictionary"""
        evidence = Evidence(
            source="test.md",
            text="Sample",
            relevance=0.90,
            chunk_index=1
        )

        result = evidence.to_dict()

        assert isinstance(result, dict)
        assert result['source'] == "test.md"
        assert result['relevance'] == 0.90


class TestConformityAnalysis:
    """Tests for ConformityAnalysis dataclass"""

    def test_analysis_creation(self):
        """Test ConformityAnalysis object creation"""
        evidence = [Evidence("test.md", "text", 0.85, 0)]

        analysis = ConformityAnalysis(
            requirement_id="REQ-001",
            conformity=ConformityVerdict.CONFORME,
            confidence=0.85,
            evidence=evidence,
            reasoning="Test reasoning",
            recommendations=["Test recommendation"],
            sources=["test.md"],
            metadata={"test": "data"}
        )

        assert analysis.requirement_id == "REQ-001"
        assert analysis.conformity == ConformityVerdict.CONFORME
        assert analysis.confidence == 0.85
        assert len(analysis.evidence) == 1

    def test_analysis_to_dict(self):
        """Test ConformityAnalysis conversion to dictionary"""
        evidence = [Evidence("test.md", "text", 0.85, 0)]

        analysis = ConformityAnalysis(
            requirement_id="REQ-001",
            conformity=ConformityVerdict.CONFORME,
            confidence=0.85,
            evidence=evidence,
            reasoning="Test",
            recommendations=[],
            sources=["test.md"],
            metadata={}
        )

        result = analysis.to_dict()

        assert isinstance(result, dict)
        assert result['requirement_id'] == "REQ-001"
        assert result['conformity'] == "CONFORME"
        assert result['confidence'] == 0.85

    def test_analysis_to_json(self):
        """Test ConformityAnalysis JSON serialization"""
        import json

        evidence = [Evidence("test.md", "text", 0.85, 0)]

        analysis = ConformityAnalysis(
            requirement_id="REQ-001",
            conformity=ConformityVerdict.REVISAO,
            confidence=0.65,
            evidence=evidence,
            reasoning="Needs review",
            recommendations=["Review manually"],
            sources=["test.md"],
            metadata={}
        )

        json_str = analysis.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed['requirement_id'] == "REQ-001"
        assert parsed['conformity'] == "REVISAO"


class TestQueryProcessor:
    """Tests for QueryProcessor class"""

    @pytest.fixture
    def mock_rag_engine(self):
        """Create mock RAG engine"""
        mock = Mock()
        mock.search = Mock(return_value=[])
        return mock

    @pytest.fixture
    def query_processor(self, mock_rag_engine):
        """Create QueryProcessor with mocked RAG"""
        return QueryProcessor(mock_rag_engine)

    @pytest.fixture
    def sample_requirement(self):
        """Sample requirement for testing"""
        return {
            'id': 'REQ-001',
            'descricao': 'Câmeras IP com resolução mínima 4MP',
            'tipo': 'Técnico',
            'categoria': 'Hardware'
        }

    def test_initialization(self, mock_rag_engine):
        """Test QueryProcessor initialization"""
        processor = QueryProcessor(mock_rag_engine)

        assert processor.rag == mock_rag_engine
        assert processor.high_confidence_threshold == 0.85
        assert processor.low_confidence_threshold == 0.60
        assert processor.min_evidence_count == 2

    def test_initialization_with_config(self, mock_rag_engine):
        """Test QueryProcessor with custom config"""
        config = {
            'high_confidence': 0.90,
            'low_confidence': 0.50,
            'min_evidence': 3
        }

        processor = QueryProcessor(mock_rag_engine, config=config)

        assert processor.high_confidence_threshold == 0.90
        assert processor.low_confidence_threshold == 0.50
        assert processor.min_evidence_count == 3

    def test_build_query_basic(self, query_processor, sample_requirement):
        """Test query building from requirement"""
        query = query_processor._build_query(sample_requirement)

        assert 'Câmeras IP com resolução mínima 4MP' in query
        assert 'Hardware' in query
        assert 'Técnico' in query

    def test_build_query_minimal(self, query_processor):
        """Test query building with minimal requirement"""
        req = {'descricao': 'Test requirement'}

        query = query_processor._build_query(req)

        assert 'Test requirement' in query

    def test_extract_evidence_empty(self, query_processor):
        """Test evidence extraction from empty results"""
        results = []

        evidence = query_processor._extract_evidence(results)

        assert evidence == []

    def test_extract_evidence_single(self, query_processor):
        """Test evidence extraction from single result"""
        results = [
            {
                'text': 'Sample text about cameras',
                'similarity_score': 0.85,
                'metadata': {
                    'filename': 'requisitos_tecnicos.md',
                    'chunk_index': 0
                }
            }
        ]

        evidence = query_processor._extract_evidence(results)

        assert len(evidence) == 1
        assert evidence[0].source == 'requisitos_tecnicos.md'
        assert evidence[0].text == 'Sample text about cameras'
        assert evidence[0].relevance == 0.85
        assert evidence[0].chunk_index == 0

    def test_extract_evidence_multiple(self, query_processor):
        """Test evidence extraction from multiple results"""
        results = [
            {
                'text': 'Text 1',
                'similarity_score': 0.90,
                'metadata': {'filename': 'doc1.md', 'chunk_index': 0}
            },
            {
                'text': 'Text 2',
                'similarity_score': 0.80,
                'metadata': {'filename': 'doc2.md', 'chunk_index': 1}
            }
        ]

        evidence = query_processor._extract_evidence(results)

        assert len(evidence) == 2
        assert evidence[0].relevance == 0.90
        assert evidence[1].relevance == 0.80

    def test_analyze_conformity_no_evidence(self, query_processor):
        """Test conformity analysis with no evidence"""
        verdict, confidence = query_processor._analyze_conformity(
            {},
            []
        )

        assert verdict == ConformityVerdict.REVISAO
        assert confidence == 0.0

    def test_analyze_conformity_high_confidence(self, query_processor):
        """Test conformity analysis with high confidence"""
        evidence = [
            Evidence("doc1.md", "text1", 0.90, 0),
            Evidence("doc2.md", "text2", 0.88, 0)
        ]

        verdict, confidence = query_processor._analyze_conformity(
            {},
            evidence
        )

        assert verdict == ConformityVerdict.CONFORME
        assert confidence >= 0.85

    def test_analyze_conformity_low_confidence(self, query_processor):
        """Test conformity analysis with low confidence"""
        evidence = [
            Evidence("doc1.md", "text1", 0.50, 0),
            Evidence("doc2.md", "text2", 0.45, 0)
        ]

        verdict, confidence = query_processor._analyze_conformity(
            {},
            evidence
        )

        assert verdict == ConformityVerdict.REVISAO
        assert confidence < 0.60

    def test_analyze_conformity_medium_confidence(self, query_processor):
        """Test conformity analysis with medium confidence (needs review)"""
        evidence = [
            Evidence("doc1.md", "text1", 0.75, 0),
            Evidence("doc2.md", "text2", 0.70, 0)
        ]

        verdict, confidence = query_processor._analyze_conformity(
            {},
            evidence
        )

        assert verdict == ConformityVerdict.REVISAO
        assert 0.60 <= confidence < 0.85

    def test_analyze_conformity_insufficient_evidence(self, query_processor):
        """Test conformity analysis with insufficient evidence count"""
        # High relevance but only 1 evidence (min is 2)
        evidence = [
            Evidence("doc1.md", "text1", 0.95, 0)
        ]

        verdict, confidence = query_processor._analyze_conformity(
            {},
            evidence
        )

        # Should be REVISAO due to insufficient evidence count
        assert verdict == ConformityVerdict.REVISAO

    def test_generate_reasoning_conforme(self, query_processor, sample_requirement):
        """Test reasoning generation for CONFORME verdict"""
        evidence = [
            Evidence("doc1.md", "text1", 0.90, 0),
            Evidence("doc2.md", "text2", 0.85, 0)
        ]

        reasoning = query_processor._generate_reasoning(
            sample_requirement,
            evidence,
            ConformityVerdict.CONFORME
        )

        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
        assert 'conformidade' in reasoning.lower()
        assert '2 evidências' in reasoning

    def test_generate_reasoning_revisao_no_evidence(self, query_processor, sample_requirement):
        """Test reasoning generation for REVISAO with no evidence"""
        reasoning = query_processor._generate_reasoning(
            sample_requirement,
            [],
            ConformityVerdict.REVISAO
        )

        assert 'Nenhuma evidência' in reasoning or 'nenhuma evidência' in reasoning.lower()

    def test_generate_recommendations_conforme(self, query_processor, sample_requirement):
        """Test recommendation generation for CONFORME verdict"""
        evidence = [
            Evidence("doc1.md", "text1", 0.90, 0),
            Evidence("doc2.md", "text2", 0.88, 0)
        ]

        recommendations = query_processor._generate_recommendations(
            sample_requirement,
            evidence,
            ConformityVerdict.CONFORME
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any('validado' in r.lower() for r in recommendations)

    def test_generate_recommendations_revisao(self, query_processor, sample_requirement):
        """Test recommendation generation for REVISAO verdict"""
        evidence = [Evidence("doc1.md", "text1", 0.70, 0)]

        recommendations = query_processor._generate_recommendations(
            sample_requirement,
            evidence,
            ConformityVerdict.REVISAO
        )

        assert isinstance(recommendations, list)
        assert any('revisar' in r.lower() for r in recommendations)

    def test_generate_recommendations_insufficient_evidence(self, query_processor, sample_requirement):
        """Test recommendations when evidence count is low"""
        evidence = [Evidence("doc1.md", "text1", 0.85, 0)]  # Only 1, min is 2

        recommendations = query_processor._generate_recommendations(
            sample_requirement,
            evidence,
            ConformityVerdict.REVISAO
        )

        assert any('incompleta' in r.lower() for r in recommendations)

    def test_analyze_requirement_integration(self, mock_rag_engine, sample_requirement):
        """Test full analyze_requirement method"""
        # Mock RAG search to return high-quality results
        mock_rag_engine.search.return_value = [
            {
                'text': 'Câmeras devem ter resolução mínima de 4MP',
                'similarity_score': 0.92,
                'metadata': {'filename': 'requisitos_tecnicos.md', 'chunk_index': 0}
            },
            {
                'text': 'Especificações de câmeras IP para segurança',
                'similarity_score': 0.88,
                'metadata': {'filename': 'doc2.md', 'chunk_index': 1}
            }
        ]

        processor = QueryProcessor(mock_rag_engine)
        result = processor.analyze_requirement(sample_requirement)

        assert isinstance(result, ConformityAnalysis)
        assert result.requirement_id == 'REQ-001'
        assert result.conformity == ConformityVerdict.CONFORME
        assert result.confidence >= 0.85
        assert len(result.evidence) == 2
        assert len(result.sources) > 0

    def test_get_stats_initial(self, query_processor):
        """Test statistics retrieval initially"""
        stats = query_processor.get_stats()

        assert stats['total_analyzed'] == 0
        assert stats['verdicts']['conforme'] == 0
        assert stats['verdicts']['revisao'] == 0

    def test_update_stats(self, query_processor):
        """Test statistics update"""
        # Update stats manually
        query_processor._update_stats(ConformityVerdict.CONFORME)
        query_processor._update_stats(ConformityVerdict.REVISAO)
        query_processor._update_stats(ConformityVerdict.CONFORME)

        stats = query_processor.get_stats()

        assert stats['total_analyzed'] == 3
        assert stats['verdicts']['conforme'] == 2
        assert stats['verdicts']['revisao'] == 1
        assert stats['percentages']['conforme'] == pytest.approx(66.67, rel=0.1)

    def test_reset_stats(self, query_processor):
        """Test statistics reset"""
        # Add some stats
        query_processor._update_stats(ConformityVerdict.CONFORME)
        query_processor._update_stats(ConformityVerdict.REVISAO)

        # Reset
        query_processor.reset_stats()

        stats = query_processor.get_stats()
        assert stats['total_analyzed'] == 0
        assert stats['verdicts']['conforme'] == 0

    def test_analyze_batch(self, mock_rag_engine):
        """Test batch analysis"""
        # Mock RAG to return consistent results
        mock_rag_engine.search.return_value = [
            {
                'text': 'Test',
                'similarity_score': 0.90,
                'metadata': {'filename': 'test.md', 'chunk_index': 0}
            },
            {
                'text': 'Test 2',
                'similarity_score': 0.85,
                'metadata': {'filename': 'test2.md', 'chunk_index': 0}
            }
        ]

        processor = QueryProcessor(mock_rag_engine)

        requirements = [
            {'id': 'REQ-001', 'descricao': 'Test 1'},
            {'id': 'REQ-002', 'descricao': 'Test 2'},
            {'id': 'REQ-003', 'descricao': 'Test 3'}
        ]

        results = processor.analyze_batch(requirements, show_progress=False)

        assert len(results) == 3
        assert all(isinstance(r, ConformityAnalysis) for r in results)
        assert results[0].requirement_id == 'REQ-001'
        assert results[1].requirement_id == 'REQ-002'

    def test_analyze_batch_with_errors(self, mock_rag_engine, capsys):
        """Test batch analysis with errors"""
        # Mock to raise error on second call
        call_count = [0]

        def search_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise ValueError("Test error")
            return [
                {
                    'text': 'Test',
                    'similarity_score': 0.90,
                    'metadata': {'filename': 'test.md', 'chunk_index': 0}
                }
            ]

        mock_rag_engine.search.side_effect = search_side_effect

        processor = QueryProcessor(mock_rag_engine)

        requirements = [
            {'id': 'REQ-001', 'descricao': 'Test 1'},
            {'id': 'REQ-002', 'descricao': 'Test 2'},  # Will error
            {'id': 'REQ-003', 'descricao': 'Test 3'}
        ]

        results = processor.analyze_batch(requirements, show_progress=False)

        # Should have 2 results (skipped the error)
        assert len(results) == 2
