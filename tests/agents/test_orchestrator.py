"""
Tests for Orchestrator Agent

Verifica:
- Coordenação de agentes
- Gestão de estado/sessões
- Roteamento de comandos
- Workflows (Manual, Assistido, FLOW)
"""

import pytest
import json
from pathlib import Path


class TestOrchestratorPrompt:
    """Tests for Orchestrator prompt compliance"""

    def test_prompt_metadata_exists(self):
        """Verify prompt.md exists and has correct metadata"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        assert prompt_path.exists(), "Orchestrator prompt.md not found"

        content = prompt_path.read_text(encoding='utf-8')

        # Check metadata
        assert "agent: orchestrator" in content
        assert "framework: SHIELD" in content
        assert "manages:" in content or "coordinate" in content

    def test_prompt_defines_responsibilities(self):
        """Verify prompt defines all responsibilities"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        responsibilities = [
            "Coordenação de Agentes",
            "Gestão de Estado",
            "Roteamento de Comandos",
            "Orquestração de Workflows"
        ]

        for resp in responsibilities:
            assert resp in content, f"Responsabilidade '{resp}' não encontrada no prompt"

    def test_prompt_defines_modes(self):
        """Verify prompt defines workflow modes"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        modes = ["manual", "assistido", "flow"]

        content_lower = content.lower()
        for mode in modes:
            assert mode in content_lower, f"Modo '{mode}' não encontrado no prompt"

    def test_prompt_defines_commands(self):
        """Verify prompt defines user commands"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should mention some commands
        commands = ["*ajuda", "*listar", "*sessao"]

        commands_found = sum(1 for cmd in commands if cmd in content)

        assert commands_found >= 2, \
            f"Apenas {commands_found}/3 comandos encontrados no prompt"

    def test_prompt_has_shield_framework(self):
        """Verify prompt implements SHIELD framework"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # At least some SHIELD sections should be present
        shield_keywords = ["STRUCTURE", "HALT", "INSPECT", "EXECUTE"]

        shield_found = sum(1 for kw in shield_keywords if kw in content)

        assert shield_found >= 3, \
            f"SHIELD framework insuficiente no prompt (apenas {shield_found}/4 seções)"


class TestOrchestratorState:
    """Tests for state management"""

    def test_state_manager_exists(self):
        """Verify StateManager class exists"""
        state_manager_path = Path("agents/orchestrator/state/state_manager.py")
        assert state_manager_path.exists(), "StateManager não encontrado"

    def test_session_schema_exists(self):
        """Verify session schema is defined"""
        session_schema_path = Path("agents/orchestrator/state/session_schema.py")
        assert session_schema_path.exists(), "Session schema não encontrado"

    def test_session_state_structure(self, sample_session_state):
        """Verify session state has required fields"""
        required_fields = [
            "session_id",
            "edital_name",
            "created_at",
            "stage",
            "status",
            "metadata",
            "outputs"
        ]

        for field in required_fields:
            assert field in sample_session_state, \
                f"Campo obrigatório '{field}' ausente no estado da sessão"

    def test_session_state_stage_valid(self, sample_session_state):
        """Verify session stage is valid"""
        valid_stages = [
            "created",
            "extraction",
            "analysis",
            "export",
            "completed",
            "failed"
        ]

        stage = sample_session_state['stage']
        assert stage in valid_stages, \
            f"Stage '{stage}' inválido. Válidos: {valid_stages}"

    def test_session_state_status_valid(self, sample_session_state):
        """Verify session status is valid"""
        valid_statuses = [
            "pending",
            "in_progress",
            "completed",
            "failed",
            "cancelled"
        ]

        status = sample_session_state['status']
        assert status in valid_statuses, \
            f"Status '{status}' inválido. Válidos: {valid_statuses}"

    def test_session_state_persistence(self, temp_dir, sample_session_state):
        """Verify session state can be persisted to JSON"""
        session_file = temp_dir / "session.json"

        # Write
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(sample_session_state, f, ensure_ascii=False, indent=2)

        # Read back
        with open(session_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        assert loaded['session_id'] == sample_session_state['session_id']
        assert loaded['stage'] == sample_session_state['stage']


class TestOrchestratorCommands:
    """Tests for command routing"""

    def test_readme_documents_commands(self):
        """Verify README documents available commands"""
        readme_path = Path("agents/orchestrator/README.md")
        assert readme_path.exists(), "Orchestrator README.md não encontrado"

        content = readme_path.read_text(encoding='utf-8')

        # Should document some commands
        commands = ["ajuda", "listar", "sessao"]

        commands_found = sum(1 for cmd in commands if cmd in content.lower())

        assert commands_found >= 2, \
            f"Apenas {commands_found}/3 comandos documentados no README"

    def test_command_help_available(self):
        """Verify help command is documented"""
        readme_path = Path("agents/orchestrator/README.md")
        content = readme_path.read_text(encoding='utf-8')

        assert "ajuda" in content.lower() or "help" in content.lower(), \
            "Comando de ajuda deve estar documentado"

    def test_command_list_sessions_available(self):
        """Verify list sessions command is documented"""
        readme_path = Path("agents/orchestrator/README.md")
        content = readme_path.read_text(encoding='utf-8')

        assert "listar" in content.lower() or "list" in content.lower(), \
            "Comando de listar sessões deve estar documentado"


class TestOrchestratorWorkflows:
    """Tests for workflow orchestration"""

    def test_manual_mode_documented(self):
        """Verify manual mode is documented"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        assert "Manual" in content or "manual" in content, \
            "Modo Manual deve estar documentado"

    def test_assisted_mode_documented(self):
        """Verify assisted mode is documented"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        assert "Assistido" in content or "assistido" in content, \
            "Modo Assistido deve estar documentado"

    def test_flow_mode_documented(self):
        """Verify FLOW mode is documented"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        assert "FLOW" in content or "flow" in content, \
            "Modo FLOW deve estar documentado"

    def test_workflow_stages_defined(self):
        """Verify workflow stages are defined"""
        # Typical workflow: extraction → analysis → export

        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        stages = ["extraction", "análise", "export"]

        content_lower = content.lower()
        stages_found = sum(1 for stage in stages if stage.lower() in content_lower)

        assert stages_found >= 2, \
            f"Apenas {stages_found}/3 stages de workflow documentados"


class TestOrchestratorSHIELD:
    """Tests for SHIELD framework compliance"""

    def test_shield_structure_phase(self, shield_checklist):
        """Verify STRUCTURE phase checklist"""
        checklist = shield_checklist['orchestrator']['S_STRUCTURE']

        # Should have:
        # - Session creation
        # - State persistence
        # - Workflow planning

        assert len(checklist) >= 3, "STRUCTURE phase deve ter pelo menos 3 checks"

        checklist_text = " ".join(checklist).lower()
        assert "sessão" in checklist_text, "STRUCTURE deve mencionar criação de sessão"
        assert "estado" in checklist_text, "STRUCTURE deve mencionar estado"

    def test_shield_halt_phase(self, shield_checklist):
        """Verify HALT phase (checkpoint between agents)"""
        checklist = shield_checklist['orchestrator']['H_HALT']

        checklist_text = " ".join(checklist).lower()
        assert "checkpoint" in checklist_text or "agentes" in checklist_text, \
            "HALT phase deve mencionar checkpoints entre agentes"

    def test_shield_inspect_phase(self, shield_checklist):
        """Verify INSPECT phase (validate outputs)"""
        checklist = shield_checklist['orchestrator']['I_INSPECT']

        checklist_text = " ".join(checklist).lower()
        assert "output" in checklist_text or "válido" in checklist_text, \
            "INSPECT deve mencionar validação de outputs"

    def test_shield_execute_phase(self, shield_checklist):
        """Verify EXECUTE phase (route commands)"""
        checklist = shield_checklist['orchestrator']['E_EXECUTE']

        checklist_text = " ".join(checklist).lower()
        assert "comando" in checklist_text or "agente" in checklist_text, \
            "EXECUTE deve mencionar roteamento de comandos ou invocação de agentes"

    def test_shield_loop_phase(self, shield_checklist):
        """Verify LOOP phase (retry on failure)"""
        checklist = shield_checklist['orchestrator']['L_LOOP']

        checklist_text = " ".join(checklist).lower()
        assert "retry" in checklist_text or "falha" in checklist_text or "rollback" in checklist_text, \
            "LOOP deve mencionar retry/rollback em caso de falha"

    def test_shield_deliver_phase(self, shield_checklist):
        """Verify DELIVER phase (complete workflow)"""
        checklist = shield_checklist['orchestrator']['D_DELIVER']

        checklist_text = " ".join(checklist).lower()
        assert "workflow" in checklist_text or "completo" in checklist_text, \
            "DELIVER deve mencionar conclusão de workflow"


class TestOrchestratorIntegration:
    """Integration tests for Orchestrator"""

    def test_state_directory_structure(self):
        """Verify state directory exists"""
        state_dir = Path("agents/orchestrator/state")
        assert state_dir.exists(), "State directory não encontrado"
        assert state_dir.is_dir(), "State path não é diretório"

    def test_state_init_exists(self):
        """Verify state module __init__.py exists"""
        init_file = Path("agents/orchestrator/state/__init__.py")
        assert init_file.exists(), "State __init__.py não encontrado"

    def test_orchestrator_cli_scripts_exist(self):
        """Verify CLI scripts for orchestrator exist"""
        # Check for state management scripts
        scripts_dir = Path("scripts")

        # At least some orchestrator-related scripts should exist
        orchestrator_scripts = [
            "orchestrator_cli.py",
            "orchestrator_stats.py",
            "orchestrator_backup.py"
        ]

        scripts_found = sum(1 for script in orchestrator_scripts
                          if (scripts_dir / script).exists())

        assert scripts_found >= 2, \
            f"Apenas {scripts_found}/3 scripts de orchestrator encontrados"


class TestOrchestratorAgentCoordination:
    """Tests for agent coordination"""

    def test_manages_document_structurer(self):
        """Verify Orchestrator manages Document Structurer"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        assert "document_structurer" in content.lower() or "estruturador" in content.lower(), \
            "Orchestrator deve gerenciar Document Structurer"

    def test_manages_technical_analyst(self):
        """Verify Orchestrator manages Technical Analyst"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        assert "technical_analyst" in content.lower() or "analista" in content.lower(), \
            "Orchestrator deve gerenciar Technical Analyst"

    def test_workflow_extraction_to_analysis(self):
        """Verify workflow chains extraction → analysis"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should describe the flow from Document Structurer to Technical Analyst
        content_lower = content.lower()

        has_extraction = "extração" in content_lower or "extraction" in content_lower
        has_analysis = "análise" in content_lower or "analysis" in content_lower
        has_workflow = "workflow" in content_lower or "fluxo" in content_lower

        assert has_extraction and has_analysis, \
            "Orchestrator deve documentar workflow de extração → análise"

    def test_error_handling_documented(self):
        """Verify error handling is documented"""
        prompt_path = Path("agents/orchestrator/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        content_lower = content.lower()

        has_error_handling = ("erro" in content_lower or
                            "falha" in content_lower or
                            "retry" in content_lower or
                            "rollback" in content_lower)

        assert has_error_handling, \
            "Orchestrator deve documentar tratamento de erros"


class TestOrchestratorStateBackupRestore:
    """Tests for state backup/restore utilities (Sprint 11 - C.3)"""

    def test_backup_method_exists(self):
        """Verify backup_all_sessions method exists in StateManager"""
        state_manager_path = Path("agents/orchestrator/state/state_manager.py")
        content = state_manager_path.read_text(encoding='utf-8')

        assert "backup_all_sessions" in content, \
            "StateManager deve ter método backup_all_sessions"

    def test_restore_method_exists(self):
        """Verify restore_from_backup method exists in StateManager"""
        state_manager_path = Path("agents/orchestrator/state/state_manager.py")
        content = state_manager_path.read_text(encoding='utf-8')

        assert "restore_from_backup" in content, \
            "StateManager deve ter método restore_from_backup"

    def test_cleanup_method_exists(self):
        """Verify cleanup_old_sessions method exists in StateManager"""
        state_manager_path = Path("agents/orchestrator/state/state_manager.py")
        content = state_manager_path.read_text(encoding='utf-8')

        assert "cleanup_old_sessions" in content, \
            "StateManager deve ter método cleanup_old_sessions"

    def test_stats_method_exists(self):
        """Verify get_sessions_stats method exists in StateManager"""
        state_manager_path = Path("agents/orchestrator/state/state_manager.py")
        content = state_manager_path.read_text(encoding='utf-8')

        assert "get_sessions_stats" in content, \
            "StateManager deve ter método get_sessions_stats"
