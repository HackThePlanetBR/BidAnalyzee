"""
Testes para comandos do Orchestrator
"""

import pytest
import subprocess
from pathlib import Path


class TestOrchestratorCommands:
    """Testes para comandos do Orchestrator"""

    def test_help_command_exists(self):
        """Testa se comando *ajuda existe"""
        script = Path("scripts/orchestrator_help.py")
        assert script.exists()
        assert script.stat().st_mode & 0o111  # Executável

    def test_help_command_runs(self):
        """Testa se comando *ajuda executa"""
        result = subprocess.run(
            ["python3", "scripts/orchestrator_help.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "BIDANALYZEE" in result.stdout
        assert "*ajuda" in result.stdout

    def test_list_command_exists(self):
        """Testa se comando *listar_analises existe"""
        script = Path("scripts/orchestrator_list.py")
        assert script.exists()

    def test_list_command_runs(self):
        """Testa se comando *listar_analises executa"""
        result = subprocess.run(
            ["python3", "scripts/orchestrator_list.py", "5"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_session_command_exists(self):
        """Testa se comando *sessao existe"""
        script = Path("scripts/orchestrator_session.py")
        assert script.exists()

    def test_session_command_requires_id(self):
        """Testa se comando *sessao requer ID"""
        result = subprocess.run(
            ["python3", "scripts/orchestrator_session.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "ID da sessão não fornecido" in result.stdout

    def test_search_command_exists(self):
        """Testa se comando *buscar existe"""
        script = Path("scripts/orchestrator_search.py")
        assert script.exists()

    def test_search_command_requires_query(self):
        """Testa se comando *buscar requer query"""
        result = subprocess.run(
            ["python3", "scripts/orchestrator_search.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "Query de busca não fornecida" in result.stdout
