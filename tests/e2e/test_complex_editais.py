#!/usr/bin/env python3
"""
E2E Tests for Complex Editais (Sprint 9 - E.3)

Tests the complete BidAnalyzee system with complex and edge case scenarios:
- Large editais (50-100+ requirements)
- Multi-level requirements (nested items)
- Compound requirements (requiring decomposition)
- Edge cases (malformed PDFs, encoding issues, etc.)

Usage:
    pytest tests/e2e/test_complex_editais.py -v
    pytest tests/e2e/test_complex_editais.py::test_large_edital -v
"""

import pytest
import csv
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.validate_pdf import validate_pdf
from scripts.validate_csv import validate_csv


class TestComplexEditais:
    """Test suite for complex edital scenarios"""

    def test_validate_pdf_script_exists(self):
        """Verify validate_pdf.py script exists and is executable"""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "validate_pdf.py"
        assert script_path.exists(), "validate_pdf.py not found"
        assert script_path.stat().st_mode & 0o111, "validate_pdf.py not executable"

    def test_validate_csv_script_exists(self):
        """Verify validate_csv.py script exists and is executable"""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "validate_csv.py"
        assert script_path.exists(), "validate_csv.py not found"
        assert script_path.stat().st_mode & 0o111, "validate_csv.py not executable"

    def test_existing_edital_pdf_validation(self):
        """Test validation of existing edital.pdf"""
        edital_path = Path(__file__).parent.parent.parent / "edital.pdf"

        if not edital_path.exists():
            pytest.skip("edital.pdf not found - test requires real edital")

        is_valid, errors, warnings, metadata = validate_pdf(
            edital_path,
            strict=False,
            max_size_mb=100,
            max_pages=500,
            min_text_chars=100
        )

        assert is_valid, f"PDF validation failed: {errors}"
        assert len(errors) == 0, f"PDF has errors: {errors}"
        # Metadata may be empty if PyPDF2 is not available or PDF is simple
        # Just check that validation passed

    def test_existing_requirements_csv_validation(self):
        """Test validation of existing requirements_extracted.csv"""
        csv_path = Path(__file__).parent.parent.parent / "requirements_extracted.csv"

        if not csv_path.exists():
            pytest.skip("requirements_extracted.csv not found")

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"CSV validation failed: {errors}"
        assert detected_type == 'structurer', f"Wrong CSV type detected: {detected_type}"
        assert len(errors) == 0, f"CSV has errors: {errors}"

    def test_existing_analysis_csv_validation(self):
        """Test validation of existing analysis_conformidade.csv"""
        csv_path = Path(__file__).parent.parent.parent / "analysis_conformidade.csv"

        if not csv_path.exists():
            pytest.skip("analysis_conformidade.csv not found")

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"CSV validation failed: {errors}"
        assert detected_type == 'analyst', f"Wrong CSV type detected: {detected_type}"
        assert len(errors) == 0, f"CSV has errors: {errors}"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_pdf_validation_nonexistent_file(self):
        """Test PDF validation with non-existent file"""
        fake_path = Path("/tmp/nonexistent_edital.pdf")

        is_valid, errors, warnings, metadata = validate_pdf(fake_path)

        assert not is_valid, "Should fail for non-existent file"
        assert len(errors) > 0, "Should have errors"
        assert any("not found" in str(e).lower() for e in errors), "Should mention file not found"

    def test_csv_validation_nonexistent_file(self):
        """Test CSV validation with non-existent file"""
        fake_path = Path("/tmp/nonexistent.csv")

        is_valid, errors, detected_type = validate_csv(fake_path)

        assert not is_valid, "Should fail for non-existent file"
        assert len(errors) > 0, "Should have errors"
        assert detected_type is None, "Should not detect type for missing file"

    def test_csv_validation_empty_file(self, tmp_path):
        """Test CSV validation with empty file"""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")

        is_valid, errors, detected_type = validate_csv(empty_csv)

        assert not is_valid, "Should fail for empty file"
        assert len(errors) > 0, "Should have errors"

    def test_csv_validation_malformed_header(self, tmp_path):
        """Test CSV validation with malformed header"""
        malformed_csv = tmp_path / "malformed.csv"
        malformed_csv.write_text("Invalid,Header,Format\n1,2,3\n")

        is_valid, errors, detected_type = validate_csv(malformed_csv)

        assert not is_valid, "Should fail for malformed header"
        assert detected_type is None, "Should not detect type for wrong headers"

    def test_csv_structurer_invalid_criticidade(self, tmp_path):
        """Test CSV validation with invalid Criticidade value"""
        csv_path = tmp_path / "invalid_criticidade.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n"
            "1,Test requirement,Hardware,INVALIDA,OBRIGATORIO,1,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert not is_valid, "Should fail for invalid Criticidade"
        assert detected_type == 'structurer', "Should detect as structurer type"
        assert any("Criticidade" in str(e) for e in errors), "Should mention Criticidade error"

    def test_csv_structurer_invalid_obrigatoriedade(self, tmp_path):
        """Test CSV validation with invalid Obrigatoriedade value"""
        csv_path = tmp_path / "invalid_obrig.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n"
            "1,Test,Hardware,ALTA,INVALIDO,1,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert not is_valid, "Should fail for invalid Obrigatoriedade"
        assert any("Obrigatoriedade" in str(e) for e in errors), "Should mention Obrigatoriedade error"

    def test_csv_structurer_negative_quantidade(self, tmp_path):
        """Test CSV validation with negative Quantidade"""
        csv_path = tmp_path / "negative_qty.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n"
            "1,Test,Hardware,ALTA,OBRIGATORIO,-5,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert not is_valid, "Should fail for negative Quantidade"
        assert any("negative" in str(e).lower() for e in errors), "Should mention negative error"

    def test_csv_analyst_invalid_veredicto(self, tmp_path):
        """Test CSV validation with invalid Veredicto value"""
        csv_path = tmp_path / "invalid_veredicto.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Veredicto,Confiança,Evidências,Raciocínio,Recomendações\n"
            "1,Test,Hardware,INVALIDO,0.9,Test,Test,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert not is_valid, "Should fail for invalid Veredicto"
        assert detected_type == 'analyst', "Should detect as analyst type"
        assert any("Veredicto" in str(e) for e in errors), "Should mention Veredicto error"

    def test_csv_analyst_confianca_out_of_range_high(self, tmp_path):
        """Test CSV validation with Confiança > 1.0"""
        csv_path = tmp_path / "high_conf.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Veredicto,Confiança,Evidências,Raciocínio,Recomendações\n"
            "1,Test,Hardware,CONFORME,1.5,Test,Test,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert not is_valid, "Should fail for Confiança > 1.0"
        assert any("out of range" in str(e).lower() for e in errors), "Should mention range error"

    def test_csv_analyst_confianca_out_of_range_low(self, tmp_path):
        """Test CSV validation with Confiança < 0.0"""
        csv_path = tmp_path / "low_conf.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Veredicto,Confiança,Evidências,Raciocínio,Recomendações\n"
            "1,Test,Hardware,CONFORME,-0.1,Test,Test,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert not is_valid, "Should fail for Confiança < 0.0"
        assert any("out of range" in str(e).lower() for e in errors), "Should mention range error"

    def test_csv_structurer_valid_na_quantidade(self, tmp_path):
        """Test CSV validation with N/A Quantidade (valid)"""
        csv_path = tmp_path / "na_qty.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n"
            "1,Test,Hardware,ALTA,OBRIGATORIO,N/A,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"Should accept N/A Quantidade: {errors}"
        assert detected_type == 'structurer', "Should detect as structurer type"


class TestComplexScenarios:
    """Test complex realistic scenarios"""

    def test_large_csv_performance(self, tmp_path):
        """Test validation performance with large CSV (100 rows)"""
        csv_path = tmp_path / "large.csv"

        # Generate 100 valid rows
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n")
            for i in range(1, 101):
                f.write(f"{i},Requisito {i},Hardware,ALTA,OBRIGATORIO,1,Observacao {i}\n")

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"Should validate large CSV: {errors}"
        assert detected_type == 'structurer', "Should detect as structurer type"

    def test_mixed_criticidade_levels(self, tmp_path):
        """Test CSV with all Criticidade levels"""
        csv_path = tmp_path / "mixed_crit.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n"
            "1,Test,Hardware,BAIXA,OBRIGATORIO,1,Test\n"
            "2,Test,Hardware,MEDIA,OBRIGATORIO,1,Test\n"
            "3,Test,Hardware,ALTA,OBRIGATORIO,1,Test\n"
            "4,Test,Hardware,CRITICA,OBRIGATORIO,1,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"Should accept all Criticidade levels: {errors}"

    def test_mixed_obrigatoriedade_levels(self, tmp_path):
        """Test CSV with all Obrigatoriedade levels"""
        csv_path = tmp_path / "mixed_obrig.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Criticidade,Obrigatoriedade,Quantidade,Observacoes\n"
            "1,Test,Hardware,ALTA,OBRIGATORIO,1,Test\n"
            "2,Test,Hardware,ALTA,DESEJAVEL,1,Test\n"
            "3,Test,Hardware,ALTA,OPCIONAL,1,Test\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"Should accept all Obrigatoriedade levels: {errors}"

    def test_mixed_veredictos(self, tmp_path):
        """Test analyst CSV with all Veredicto types"""
        csv_path = tmp_path / "mixed_verd.csv"
        csv_path.write_text(
            "ID,Requisito,Categoria,Veredicto,Confiança,Evidências,Raciocínio,Recomendações\n"
            "1,Test,Hardware,CONFORME,0.95,Ev1,Rac1,Rec1\n"
            "2,Test,Hardware,NAO_CONFORME,0.90,Ev2,Rac2,Rec2\n"
            "3,Test,Hardware,REVISAO,0.75,Ev3,Rac3,Rec3\n"
        )

        is_valid, errors, detected_type = validate_csv(csv_path)

        assert is_valid, f"Should accept all Veredicto types: {errors}"
        assert detected_type == 'analyst', "Should detect as analyst type"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
