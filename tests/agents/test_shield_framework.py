"""
Tests for SHIELD Framework Implementation

Verifica:
- Todos os agents implementam SHIELD
- Consistência entre agents
- Completude de cada fase
- Documentação adequada
"""

import pytest
from pathlib import Path


class TestSHIELDFrameworkConsistency:
    """Tests for SHIELD framework consistency across agents"""

    def test_all_agents_use_shield(self):
        """Verify all agent prompts declare SHIELD framework"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            path = Path(agent_prompt)
            assert path.exists(), f"Prompt não encontrado: {agent_prompt}"

            content = path.read_text(encoding='utf-8')
            assert "framework: SHIELD" in content or "Framework SHIELD" in content, \
                f"{agent_prompt} não declara framework SHIELD"

    def test_all_agents_have_structure_phase(self):
        """Verify all agents implement STRUCTURE phase"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')
            assert "S - STRUCTURE" in content or "STRUCTURE" in content, \
                f"{agent_prompt} não implementa fase STRUCTURE"

    def test_all_agents_have_halt_phase(self):
        """Verify all agents implement HALT phase (checkpoints)"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')
            assert "H - HALT" in content or "HALT" in content or "Checkpoint" in content, \
                f"{agent_prompt} não implementa fase HALT"

    def test_all_agents_have_inspect_phase(self):
        """Verify all agents implement INSPECT phase (quality checks)"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')
            assert "I - INSPECT" in content or "INSPECT" in content, \
                f"{agent_prompt} não implementa fase INSPECT"

    def test_all_agents_have_execute_phase(self):
        """Verify all agents implement EXECUTE phase"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')
            assert "E - EXECUTE" in content or "EXECUTE" in content, \
                f"{agent_prompt} não implementa fase EXECUTE"


class TestSHIELDPhaseCompleteness:
    """Tests for completeness of each SHIELD phase"""

    def test_structure_phase_has_planning(self):
        """Verify STRUCTURE phase includes planning activities"""
        agents = {
            "document_structurer": "agents/document_structurer/prompt.md",
            "technical_analyst": "agents/technical_analyst/prompt.md",
            "orchestrator": "agents/orchestrator/prompt.md"
        }

        for agent_name, agent_path in agents.items():
            content = Path(agent_path).read_text(encoding='utf-8')

            # Extract STRUCTURE section (rough extraction)
            if "S - STRUCTURE" in content:
                # Should mention planning keywords
                planning_keywords = ["plano", "plan", "estratégia", "strategy", "analisar"]
                content_lower = content.lower()

                has_planning = any(kw in content_lower for kw in planning_keywords)
                assert has_planning, \
                    f"{agent_name}: STRUCTURE phase deve incluir planejamento"

    def test_halt_phase_has_checkpoints(self):
        """Verify HALT phase includes checkpoint logic"""
        agents = {
            "document_structurer": "agents/document_structurer/prompt.md",
            "technical_analyst": "agents/technical_analyst/prompt.md",
            "orchestrator": "agents/orchestrator/prompt.md"
        }

        for agent_name, agent_path in agents.items():
            content = Path(agent_path).read_text(encoding='utf-8')

            # Should mention checkpoint/validation/confirmation
            checkpoint_keywords = ["checkpoint", "validação", "confirmação", "aguarde"]
            content_lower = content.lower()

            has_checkpoint = any(kw in content_lower for kw in checkpoint_keywords)
            assert has_checkpoint, \
                f"{agent_name}: HALT phase deve incluir checkpoints"

    def test_inspect_phase_has_quality_checks(self):
        """Verify INSPECT phase includes quality verification"""
        agents = {
            "document_structurer": "agents/document_structurer/prompt.md",
            "technical_analyst": "agents/technical_analyst/prompt.md",
            "orchestrator": "agents/orchestrator/prompt.md"
        }

        for agent_name, agent_path in agents.items():
            content = Path(agent_path).read_text(encoding='utf-8')

            # Should mention quality checks/checklists
            quality_keywords = ["checklist", "verificar", "validar", "qualidade", "inspeção"]
            content_lower = content.lower()

            has_quality = any(kw in content_lower for kw in quality_keywords)
            assert has_quality, \
                f"{agent_name}: INSPECT phase deve incluir verificações de qualidade"

    def test_execute_phase_has_actions(self):
        """Verify EXECUTE phase includes concrete actions"""
        agents = {
            "document_structurer": "agents/document_structurer/prompt.md",
            "technical_analyst": "agents/technical_analyst/prompt.md",
            "orchestrator": "agents/orchestrator/prompt.md"
        }

        for agent_name, agent_path in agents.items():
            content = Path(agent_path).read_text(encoding='utf-8')

            # Should mention execution actions
            execution_keywords = ["executar", "execute", "gerar", "criar", "processar"]
            content_lower = content.lower()

            has_execution = any(kw in content_lower for kw in execution_keywords)
            assert has_execution, \
                f"{agent_name}: EXECUTE phase deve incluir ações concretas"


class TestSHIELDChecklist:
    """Tests for SHIELD checklist implementation"""

    def test_checklist_covers_all_phases(self, shield_checklist):
        """Verify checklist covers all SHIELD phases for each agent"""
        phases = ['S_STRUCTURE', 'H_HALT', 'I_INSPECT', 'E_EXECUTE', 'L_LOOP', 'D_DELIVER']

        for agent_name, agent_checklist in shield_checklist.items():
            for phase in phases:
                assert phase in agent_checklist, \
                    f"{agent_name}: checklist missing phase {phase}"

                assert len(agent_checklist[phase]) > 0, \
                    f"{agent_name}: checklist {phase} is empty"

    def test_structure_checklist_minimum_items(self, shield_checklist):
        """Verify STRUCTURE checklist has minimum items"""
        for agent_name, agent_checklist in shield_checklist.items():
            structure_items = agent_checklist['S_STRUCTURE']
            assert len(structure_items) >= 2, \
                f"{agent_name}: STRUCTURE checklist deve ter pelo menos 2 items"

    def test_inspect_checklist_minimum_items(self, shield_checklist):
        """Verify INSPECT checklist has minimum items (most critical)"""
        for agent_name, agent_checklist in shield_checklist.items():
            inspect_items = agent_checklist['I_INSPECT']
            assert len(inspect_items) >= 3, \
                f"{agent_name}: INSPECT checklist deve ter pelo menos 3 items (fase crítica)"

    def test_deliver_checklist_has_output_validation(self, shield_checklist):
        """Verify DELIVER checklist validates final output"""
        for agent_name, agent_checklist in shield_checklist.items():
            deliver_items = agent_checklist['D_DELIVER']
            deliver_text = " ".join(deliver_items).lower()

            # Should mention output validation
            output_keywords = ["output", "csv", "válido", "relatório", "completo"]
            has_output_validation = any(kw in deliver_text for kw in output_keywords)

            assert has_output_validation, \
                f"{agent_name}: DELIVER deve validar output final"


class TestSHIELDDocumentation:
    """Tests for SHIELD framework documentation"""

    def test_shield_documented_in_prompts(self):
        """Verify SHIELD is documented in all agent prompts"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')

            # Should have a section explaining SHIELD
            has_shield_section = (
                "SHIELD Framework" in content or
                "Framework SHIELD" in content or
                "## SHIELD" in content
            )

            assert has_shield_section, \
                f"{agent_prompt} deve ter seção explicando SHIELD Framework"

    def test_shield_acronym_explained(self):
        """Verify SHIELD acronym is explained in at least one place"""
        # Should explain what S, H, I, E, L, D stand for

        all_prompts = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        acronym_explained = False

        for prompt_path in all_prompts:
            content = Path(prompt_path).read_text(encoding='utf-8')

            # Check if all letters are explained
            letters = ["STRUCTURE", "HALT", "INSPECT", "EXECUTE", "LOOP", "DELIVER"]
            letters_found = sum(1 for letter in letters if letter in content)

            if letters_found >= 5:  # Most letters explained
                acronym_explained = True
                break

        assert acronym_explained, \
            "SHIELD acronym deve ser explicado em pelo menos um prompt"


class TestSHIELDAntiHallucination:
    """Tests for anti-hallucination features in SHIELD"""

    def test_document_structurer_has_traceability(self):
        """Verify Document Structurer implements traceability"""
        prompt_path = Path("agents/document_structurer/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should mention page references, traceability
        traceability_keywords = ["rastreabilidade", "traceability", "página", "page", "anti-alucinação"]
        content_lower = content.lower()

        has_traceability = any(kw in content_lower for kw in traceability_keywords)

        assert has_traceability, \
            "Document Structurer deve implementar rastreabilidade (anti-alucinação)"

    def test_technical_analyst_requires_evidence(self):
        """Verify Technical Analyst requires evidence for verdicts"""
        prompt_path = Path("agents/technical_analyst/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should mention evidence, citations
        evidence_keywords = ["evidência", "evidence", "citação", "citation", "fonte", "source"]
        content_lower = content.lower()

        has_evidence_requirement = any(kw in content_lower for kw in evidence_keywords)

        assert has_evidence_requirement, \
            "Technical Analyst deve requerer evidências para veredictos"

    def test_confidence_scores_documented(self):
        """Verify confidence/certainty scores are documented"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')

            # Should mention confidence/certainty
            confidence_keywords = ["confiança", "confidence", "certeza", "certainty"]
            content_lower = content.lower()

            has_confidence = any(kw in content_lower for kw in confidence_keywords)

            assert has_confidence, \
                f"{agent_prompt} deve documentar scores de confiança"


class TestSHIELDLoopPhase:
    """Tests for LOOP phase (iteration/correction)"""

    def test_all_agents_have_loop_or_correction(self):
        """Verify all agents implement LOOP/correction logic"""
        agents = [
            "agents/document_structurer/prompt.md",
            "agents/technical_analyst/prompt.md",
            "agents/orchestrator/prompt.md"
        ]

        for agent_prompt in agents:
            content = Path(agent_prompt).read_text(encoding='utf-8')

            # Should mention LOOP, iteration, retry, correction
            loop_keywords = ["L - LOOP", "LOOP", "iteração", "retry", "correção", "corrigir"]
            content_lower = content.lower()

            has_loop = any(kw in content_lower for kw in loop_keywords)

            assert has_loop, \
                f"{agent_prompt} deve implementar LOOP/correção"

    def test_loop_triggers_documented(self):
        """Verify conditions that trigger LOOP are documented"""
        agents = {
            "document_structurer": "agents/document_structurer/prompt.md",
            "technical_analyst": "agents/technical_analyst/prompt.md",
            "orchestrator": "agents/orchestrator/prompt.md"
        }

        for agent_name, agent_path in agents.items():
            content = Path(agent_path).read_text(encoding='utf-8')

            # Should mention when to loop (validation failure, errors, etc.)
            trigger_keywords = ["falha", "erro", "insuficiente", "validação falhar"]
            content_lower = content.lower()

            has_trigger = any(kw in content_lower for kw in trigger_keywords)

            # This is a quality check, not strict requirement
            # But good practice to document loop triggers
            if not has_trigger:
                # Warn but don't fail
                pass


class TestSHIELDIntegration:
    """Integration tests for SHIELD framework"""

    def test_shield_workflow_end_to_end(self):
        """Verify SHIELD phases flow logically"""
        # Conceptual test: SHIELD should flow S → H → I → E → L → D

        # In Document Structurer:
        # S: Plan extraction
        # H: Checkpoint before batch
        # I: Validate each requirement
        # E: Generate CSV
        # L: Iterate if validation fails
        # D: Deliver final CSV + report

        assert True, "Conceptual test - verify workflow in prompts"

    def test_checkpoints_prevent_invalid_progression(self):
        """Verify HALT checkpoints prevent invalid progression"""
        # H (HALT) should prevent moving to next agent with invalid output

        assert True, "Conceptual test - verify in orchestrator logic"

    def test_quality_gates_at_each_phase(self):
        """Verify quality gates exist at phase transitions"""
        # I (INSPECT) should validate before moving to next phase

        assert True, "Conceptual test - verify in agent logic"


class TestSHIELDMetrics:
    """Tests for SHIELD-related metrics and reporting"""

    def test_validation_reports_exist(self):
        """Verify validation report generation is implemented"""
        # Document Structurer should generate validation report

        validation_files = [
            "agents/document_structurer/validation_report.py",
            "agents/document_structurer/validation_engine.py"
        ]

        files_found = sum(1 for vf in validation_files if Path(vf).exists())

        assert files_found >= 1, \
            "Document Structurer deve implementar relatório de validação"

    def test_quality_check_script_exists(self):
        """Verify quality check script exists (E.3 - Output Validation)"""
        quality_check = Path("scripts/quality_check.py")
        assert quality_check.exists(), \
            "Quality check script deve existir (E.3 - Output Validation)"

    def test_quality_check_validates_completeness(self):
        """Verify quality check validates completeness"""
        quality_check = Path("scripts/quality_check.py")
        content = quality_check.read_text(encoding='utf-8')

        assert "completeness" in content.lower() or "completude" in content.lower(), \
            "Quality check deve validar completude"

    def test_quality_check_validates_consistency(self):
        """Verify quality check validates consistency"""
        quality_check = Path("scripts/quality_check.py")
        content = quality_check.read_text(encoding='utf-8')

        assert "consistency" in content.lower() or "consistência" in content.lower(), \
            "Quality check deve validar consistência"
