"""
Testes para State Management
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from agents.orchestrator.state import StateManager, Session


@pytest.fixture
def temp_state_dir():
    """Cria diretório temporário para testes"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestStateManager:
    """Testes para StateManager"""

    def test_create_session(self, temp_state_dir):
        """Testa criação de sessão"""
        manager = StateManager(temp_state_dir)
        session = manager.create_session("test_session_001")

        assert session.session_id == "test_session_001"
        assert session.data.metadata.status == "in_progress"
        assert session.data.metadata.workflow_stage == "idle"

    def test_save_and_load_session(self, temp_state_dir):
        """Testa salvar e carregar sessão"""
        manager = StateManager(temp_state_dir)

        # Criar e modificar sessão
        session = manager.create_session("test_session_002")
        session.update_stage("extracting")
        session.set_edital_info("/path/to/edital.pdf", "Edital 001")
        manager.save_session(session)

        # Carregar sessão
        loaded = manager.load_session("test_session_002")

        assert loaded is not None
        assert loaded.session_id == "test_session_002"
        assert loaded.data.metadata.workflow_stage == "extracting"
        assert loaded.data.edital_info["name"] == "Edital 001"

    def test_list_sessions(self, temp_state_dir):
        """Testa listagem de sessões"""
        manager = StateManager(temp_state_dir)

        # Criar várias sessões
        manager.create_session("session_001")
        manager.create_session("session_002")
        manager.create_session("session_003")

        # Listar
        sessions = manager.list_sessions()

        assert len(sessions) == 3
        assert all("session_id" in s for s in sessions)

    def test_delete_session(self, temp_state_dir):
        """Testa deleção de sessão"""
        manager = StateManager(temp_state_dir)

        # Criar sessão
        manager.create_session("session_to_delete")

        # Deletar
        result = manager.delete_session("session_to_delete")
        assert result is True

        # Verificar que foi deletada
        loaded = manager.load_session("session_to_delete")
        assert loaded is None

    def test_get_latest_session(self, temp_state_dir):
        """Testa obter sessão mais recente"""
        manager = StateManager(temp_state_dir)

        # Criar sessões
        manager.create_session("session_old")
        import time
        time.sleep(0.1)  # Garantir timestamp diferente
        manager.create_session("session_new")

        # Obter mais recente
        latest = manager.get_latest_session()

        assert latest is not None
        assert latest.session_id == "session_new"


class TestSession:
    """Testes para Session"""

    def test_session_creation(self):
        """Testa criação de sessão"""
        session = Session("test_id")

        assert session.session_id == "test_id"
        assert session.data.metadata.status == "in_progress"

    def test_update_stage(self):
        """Testa atualização de estágio"""
        session = Session("test_id")
        session.update_stage("analyzing")

        assert session.data.metadata.workflow_stage == "analyzing"

    def test_add_error(self):
        """Testa adicionar erro"""
        session = Session("test_id")
        session.add_error("Test error message")

        assert len(session.data.errors) == 1
        assert session.data.errors[0]["message"] == "Test error message"

    def test_set_extraction_result(self):
        """Testa definir resultado de extração"""
        session = Session("test_id")
        session.set_extraction_result("/path/to/output.csv", 50)

        assert session.data.extraction_result["csv_path"] == "/path/to/output.csv"
        assert session.data.extraction_result["num_requirements"] == 50
