"""
Testes para ferramentas de export (PDF e Excel)
"""

import pytest
import subprocess
from pathlib import Path


class TestExportTools:
    """Testes para export_pdf.py e export_excel.py"""

    def test_pdf_script_exists(self):
        """Testa se export_pdf.py existe"""
        script = Path("scripts/export_pdf.py")
        assert script.exists()
        assert script.stat().st_mode & 0o111  # Executável

    def test_excel_script_exists(self):
        """Testa se export_excel.py existe"""
        script = Path("scripts/export_excel.py")
        assert script.exists()
        assert script.stat().st_mode & 0o111  # Executável

    def test_pdf_script_help(self):
        """Testa se export_pdf.py mostra ajuda"""
        result = subprocess.run(
            ["python3", "scripts/export_pdf.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0  # Deve falhar sem argumentos
        assert "Uso:" in result.stdout or "uso" in result.stdout.lower()

    def test_excel_script_help(self):
        """Testa se export_excel.py mostra ajuda"""
        result = subprocess.run(
            ["python3", "scripts/export_excel.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0  # Deve falhar sem argumentos
        assert "Uso:" in result.stdout or "uso" in result.stdout.lower()


class TestFlowMode:
    """Testes para modo FLOW"""

    def test_flow_script_exists(self):
        """Testa se analyze_edital_full.py existe"""
        script = Path("scripts/analyze_edital_full.py")
        assert script.exists()
        assert script.stat().st_mode & 0o111  # Executável

    def test_flow_script_help(self):
        """Testa se FLOW mode mostra ajuda"""
        result = subprocess.run(
            ["python3", "scripts/analyze_edital_full.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0  # Deve falhar sem argumentos
        assert "Uso:" in result.stdout or "uso" in result.stdout.lower()
        assert "FLOW" in result.stdout or "flow" in result.stdout.lower()
