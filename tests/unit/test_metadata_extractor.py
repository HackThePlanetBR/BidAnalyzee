#!/usr/bin/env python3
"""
Unit Tests for Metadata Extractor

Tests extraction, confidence scoring, and validation logic.

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.document_structurer.extractors.metadata_extractor import (
    MetadataExtractor,
    EditalMetadata,
    extract_metadata
)


class TestMetadataExtractor:
    """Test suite for MetadataExtractor"""

    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = MetadataExtractor()

        # Sample edital text (complete)
        self.sample_text_complete = """
        PREFEITURA MUNICIPAL DE SÃO PAULO

        EDITAL Nº 001/2025
        PREGÃO ELETRÔNICO

        DATA DE PUBLICAÇÃO: 15/01/2025

        1. OBJETO

        Aquisição de Sistema de Videomonitoramento Urbano com câmeras IP,
        servidores de armazenamento e software de gerenciamento, conforme
        especificações técnicas anexas.

        2. VALOR ESTIMADO

        R$ 2.500.000,00 (dois milhões e quinhentos mil reais)

        3. PRAZO DE ENTREGA

        180 dias corridos a partir da assinatura do contrato.
        """

        # Sample edital text (partial - missing some fields)
        self.sample_text_partial = """
        GOVERNO DO ESTADO DE RIO DE JANEIRO

        CONCORRÊNCIA PÚBLICA Nº RJ-042/2025

        DO OBJETO: Contratação de empresa especializada para fornecimento
        de equipamentos de segurança eletrônica.

        Prazo: 90 dias
        """

        # Sample edital text (minimal - only critical fields)
        self.sample_text_minimal = """
        Edital nº 123/2025

        Objeto: Aquisição de câmeras
        """

    def test_extract_complete_metadata(self):
        """Test extraction from complete edital"""
        metadata = self.extractor.extract(self.sample_text_complete)

        # Check all fields extracted
        assert metadata.objeto is not None, "Objeto should be extracted"
        assert metadata.orgao is not None, "Órgão should be extracted"
        assert metadata.valor_estimado is not None, "Valor should be extracted"
        assert metadata.prazo_entrega is not None, "Prazo should be extracted"
        assert metadata.modalidade is not None, "Modalidade should be extracted"
        assert metadata.numero_edital is not None, "Número should be extracted"
        assert metadata.data_publicacao is not None, "Data should be extracted"

        # Check values
        assert "videomonitoramento" in metadata.objeto.lower()
        assert "são paulo" in metadata.orgao.lower()
        assert "2.500.000" in metadata.valor_estimado or "2500000" in metadata.valor_estimado
        assert "180" in metadata.prazo_entrega
        assert "pregão" in metadata.modalidade.lower()
        assert "001/2025" in metadata.numero_edital
        assert "15/01/2025" in metadata.data_publicacao

        print("✅ Complete metadata extraction: PASS")

    def test_extract_partial_metadata(self):
        """Test extraction from partial edital"""
        metadata = self.extractor.extract(self.sample_text_partial)

        # Check some fields extracted
        assert metadata.objeto is not None, "Objeto should be extracted"
        assert metadata.orgao is not None, "Órgão should be extracted"
        assert metadata.modalidade is not None, "Modalidade should be extracted"
        assert metadata.prazo_entrega is not None, "Prazo should be extracted"

        # Check some fields missing (expected)
        assert metadata.valor_estimado is None, "Valor should be None (not in text)"
        assert metadata.data_publicacao is None, "Data should be None (not in text)"

        print("✅ Partial metadata extraction: PASS")

    def test_extract_minimal_metadata(self):
        """Test extraction from minimal edital"""
        metadata = self.extractor.extract(self.sample_text_minimal)

        # Check critical fields
        assert metadata.numero_edital is not None, "Número should be extracted"
        assert metadata.objeto is not None, "Objeto should be extracted"

        # Most fields missing
        assert metadata.orgao is None
        assert metadata.valor_estimado is None

        print("✅ Minimal metadata extraction: PASS")

    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        metadata = self.extractor.extract(self.sample_text_complete)

        # Check confidence scores exist
        assert len(metadata.confidence_scores) > 0, "Confidence scores should exist"

        # Check reasonable confidence values
        for field, score in metadata.confidence_scores.items():
            assert 0.0 <= score <= 1.0, f"{field} confidence should be in [0, 1]"

        # Fields with data should have higher confidence
        assert metadata.confidence_scores.get("objeto", 0) > 0.7, "Objeto confidence should be high"
        assert metadata.confidence_scores.get("modalidade", 0) > 0.9, "Modalidade confidence should be very high"

        print("✅ Confidence scoring: PASS")

    def test_overall_confidence(self):
        """Test overall confidence calculation"""
        # Complete metadata
        metadata_complete = self.extractor.extract(self.sample_text_complete)
        overall_complete = self.extractor.get_overall_confidence(metadata_complete)

        assert 0.0 <= overall_complete <= 1.0, "Overall confidence should be in [0, 1]"
        assert overall_complete > 0.8, "Complete metadata should have high overall confidence"

        # Minimal metadata
        metadata_minimal = self.extractor.extract(self.sample_text_minimal)
        overall_minimal = self.extractor.get_overall_confidence(metadata_minimal)

        assert 0.0 <= overall_minimal <= 1.0, "Overall confidence should be in [0, 1]"
        # Minimal should have lower overall confidence than complete
        assert overall_minimal < overall_complete

        print("✅ Overall confidence calculation: PASS")

    def test_validation(self):
        """Test metadata validation"""
        # Complete metadata
        metadata_complete = self.extractor.extract(self.sample_text_complete)
        validation_complete = self.extractor.validate_metadata(metadata_complete)

        # Critical fields should pass
        assert validation_complete["objeto_present"] is True
        assert validation_complete["numero_edital_present"] is True
        assert validation_complete["overall_confident"] is True

        # Minimal metadata
        metadata_minimal = self.extractor.extract(self.sample_text_minimal)
        validation_minimal = self.extractor.validate_metadata(metadata_minimal)

        # Critical fields should pass
        assert validation_minimal["objeto_present"] is True
        assert validation_minimal["numero_edital_present"] is True

        # But some optional checks may fail
        assert validation_minimal["orgao_present"] is False
        assert validation_minimal["modalidade_present"] is False

        print("✅ Metadata validation: PASS")

    def test_value_cleaning(self):
        """Test value cleaning functionality"""
        # Test objeto cleaning
        raw_objeto = "  Sistema de videomonitoramento  ;"
        clean_objeto = self.extractor._clean_value(raw_objeto, "objeto")
        assert clean_objeto == "Sistema de videomonitoramento"

        # Test valor cleaning
        raw_valor = "2500000"
        clean_valor = self.extractor._clean_value(raw_valor, "valor_estimado")
        assert clean_valor.startswith("R$")

        # Test orgao cleaning
        raw_orgao = "prefeitura municipal de são paulo"
        clean_orgao = self.extractor._clean_value(raw_orgao, "orgao")
        assert "Prefeitura" in clean_orgao  # Title case

        print("✅ Value cleaning: PASS")

    def test_convenience_function(self):
        """Test the extract_metadata convenience function"""
        result = extract_metadata(self.sample_text_complete)

        # Check structure
        assert "metadata" in result
        assert "overall_confidence" in result
        assert "validation" in result

        # Check metadata content
        metadata = result["metadata"]
        assert metadata["objeto"] is not None
        assert metadata["orgao"] is not None

        # Check confidence
        assert isinstance(result["overall_confidence"], float)
        assert 0.0 <= result["overall_confidence"] <= 1.0

        # Check validation
        validation = result["validation"]
        assert validation["objeto_present"] is True

        print("✅ Convenience function: PASS")

    def test_edge_cases(self):
        """Test edge cases"""
        # Empty text
        metadata_empty = self.extractor.extract("")
        assert metadata_empty.objeto is None
        assert len(metadata_empty.confidence_scores) == 0 or all(s == 0 for s in metadata_empty.confidence_scores.values())

        # Very short text
        metadata_short = self.extractor.extract("test")
        assert self.extractor.get_overall_confidence(metadata_short) == 0.0

        # Text with no metadata
        text_no_metadata = "Lorem ipsum dolor sit amet " * 100
        metadata_none = self.extractor.extract(text_no_metadata)
        assert self.extractor.get_overall_confidence(metadata_none) == 0.0

        print("✅ Edge cases: PASS")

    def test_to_dict(self):
        """Test EditalMetadata.to_dict() method"""
        metadata = self.extractor.extract(self.sample_text_complete)
        metadata_dict = metadata.to_dict()

        # Check structure
        assert isinstance(metadata_dict, dict)
        assert "objeto" in metadata_dict
        assert "orgao" in metadata_dict
        assert "confidence_scores" in metadata_dict

        # Check values
        assert metadata_dict["objeto"] == metadata.objeto
        assert metadata_dict["confidence_scores"] == metadata.confidence_scores

        print("✅ to_dict() method: PASS")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Metadata Extractor - Unit Tests")
    print("=" * 60 + "\n")

    test_suite = TestMetadataExtractor()
    test_suite.setup_method()

    # Run tests
    tests = [
        test_suite.test_extract_complete_metadata,
        test_suite.test_extract_partial_metadata,
        test_suite.test_extract_minimal_metadata,
        test_suite.test_confidence_scoring,
        test_suite.test_overall_confidence,
        test_suite.test_validation,
        test_suite.test_value_cleaning,
        test_suite.test_convenience_function,
        test_suite.test_edge_cases,
        test_suite.test_to_dict,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: FAILED")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: ERROR")
            print(f"   Error: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
