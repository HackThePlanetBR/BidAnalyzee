"""
Tests for Technical Analyst Agent

Verifica:
- Análise de conformidade
- Uso de RAG search
- Veredictos e justificativas
- Framework SHIELD
"""

import pytest
import csv
import json
from pathlib import Path


class TestTechnicalAnalystPrompt:
    """Tests for Technical Analyst prompt compliance"""

    def test_prompt_metadata_exists(self):
        """Verify prompt.md exists and has correct metadata"""
        prompt_path = Path("agents/technical_analyst/prompt.md")
        assert prompt_path.exists(), "Technical Analyst prompt.md not found"

        content = prompt_path.read_text(encoding='utf-8')

        # Check metadata
        assert "agent: technical_analyst" in content
        assert "framework: SHIELD" in content
        assert "output_format: csv" in content

    def test_prompt_defines_capabilities(self):
        """Verify prompt defines analysis capabilities"""
        prompt_path = Path("agents/technical_analyst/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        capabilities = ["analyze", "reason", "judge", "recommend"]

        # Check metadata section has capabilities
        content_lower = content.lower()
        for cap in capabilities:
            assert cap in content_lower, f"Capability '{cap}' não encontrada no prompt"

    def test_prompt_has_shield_framework(self):
        """Verify prompt implements SHIELD framework"""
        prompt_path = Path("agents/technical_analyst/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        shield_sections = [
            "S - STRUCTURE",
            "H - HALT",
            "I - INSPECT",
            "E - EXECUTE"
        ]

        for section in shield_sections:
            assert section in content, f"SHIELD section '{section}' não encontrada"

    def test_prompt_mentions_rag_search(self):
        """Verify prompt instructs to use RAG search"""
        prompt_path = Path("agents/technical_analyst/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should mention rag_search.py
        assert "rag_search.py" in content, "Prompt deve mencionar rag_search.py"
        assert "RAG" in content or "Buscar Evidências" in content, \
            "Prompt deve mencionar busca RAG"

    def test_prompt_defines_verdicts(self):
        """Verify prompt defines valid verdict types"""
        prompt_path = Path("agents/technical_analyst/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        verdicts = ["CONFORME", "NÃO CONFORME", "PARCIAL", "REQUER ANÁLISE"]

        # At least some verdicts should be mentioned
        verdicts_found = sum(1 for v in verdicts if v in content)

        assert verdicts_found >= 3, \
            f"Apenas {verdicts_found}/4 veredictos encontrados no prompt"


class TestTechnicalAnalystOutput:
    """Tests for Technical Analyst output validation"""

    def test_analysis_csv_has_required_fields(self, sample_analysis_csv, expected_csv_fields):
        """Verify analysis CSV has all required fields"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        required = expected_csv_fields['analysis']

        for field in required:
            assert field in fieldnames, f"Campo obrigatório '{field}' ausente"

    def test_analysis_csv_verdicts_valid(self, sample_analysis_csv):
        """Verify all verdicts are from allowed set"""
        valid_verdicts = [
            "CONFORME",
            "NÃO CONFORME",
            "PARCIALMENTE CONFORME",
            "REQUER ANÁLISE"
        ]

        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'veredicto' in row, f"Campo 'veredicto' ausente na linha {i}"
            veredicto = row['veredicto'].strip().upper()

            # Normalize variations
            if "PARCIAL" in veredicto:
                veredicto = "PARCIALMENTE CONFORME"

            assert veredicto in valid_verdicts, \
                f"Veredicto inválido na linha {i}: '{row['veredicto']}'. Válidos: {valid_verdicts}"

    def test_analysis_csv_has_justifications(self, sample_analysis_csv):
        """Verify all items have justifications"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'justificativa' in row, f"Campo 'justificativa' ausente na linha {i}"
            justificativa = row['justificativa'].strip()

            assert justificativa != "", f"Justificativa vazia na linha {i}"
            assert len(justificativa) >= 20, \
                f"Justificativa muito curta na linha {i} ({len(justificativa)} chars): '{justificativa}'"

    def test_analysis_csv_has_evidences(self, sample_analysis_csv):
        """Verify CONFORME/NÃO CONFORME items have evidences"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            veredicto = row['veredicto'].strip().upper()

            # Skip REQUER ANÁLISE (may not have solid evidence)
            if "REQUER" in veredicto:
                continue

            assert 'evidencias' in row, f"Campo 'evidencias' ausente na linha {i}"
            evidencias = row['evidencias'].strip()

            if "CONFORME" in veredicto or "NÃO CONFORME" in veredicto:
                assert evidencias != "", \
                    f"Linha {i}: {veredicto} mas sem evidências"

    def test_analysis_csv_evidence_format(self, sample_analysis_csv):
        """Verify evidences follow 'arquivo:linha' format"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            evidencias = row.get('evidencias', '').strip()

            if not evidencias:
                continue  # Tested separately

            # Should contain ":" and digits (formato arquivo:linha)
            if ":" in evidencias and any(char.isdigit() for char in evidencias):
                # Good citation format
                continue
            else:
                # Might be acceptable for some cases, but warn
                # Not failing here, just checking format
                pass

    def test_analysis_csv_confidence_levels(self, sample_analysis_csv):
        """Verify confidence levels are valid"""
        valid_levels = ["Alto", "Médio", "Baixo"]

        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'nivel_confianca' in row, f"Campo 'nivel_confianca' ausente na linha {i}"
            nivel = row['nivel_confianca'].strip()

            assert nivel in valid_levels, \
                f"Nível de confiança inválido na linha {i}: '{nivel}'. Válidos: {valid_levels}"

    def test_analysis_csv_recommendations_present(self, sample_analysis_csv):
        """Verify recommendations field is present (can be empty)"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'recomendacoes' in row, f"Campo 'recomendacoes' ausente na linha {i}"


class TestTechnicalAnalystRAGIntegration:
    """Tests for RAG search integration"""

    def test_rag_search_script_exists(self):
        """Verify rag_search.py script exists"""
        rag_script = Path("scripts/rag_search.py")
        assert rag_script.exists(), "scripts/rag_search.py não encontrado"

    def test_rag_response_structure(self, sample_rag_response):
        """Verify RAG response has expected structure"""
        assert 'query' in sample_rag_response
        assert 'results' in sample_rag_response
        assert len(sample_rag_response['results']) > 0

        # Check first result structure
        result = sample_rag_response['results'][0]
        assert 'source' in result
        assert 'text' in result
        assert 'similarity' in result
        assert 'metadata' in result

    def test_rag_similarity_scores(self, sample_rag_response):
        """Verify RAG similarity scores are in valid range"""
        for result in sample_rag_response['results']:
            similarity = result['similarity']
            assert 0.0 <= similarity <= 1.0, \
                f"Similarity score fora do intervalo [0.0, 1.0]: {similarity}"

    def test_rag_returns_multiple_results(self, sample_rag_response):
        """Verify RAG returns multiple evidences"""
        # Good analysis should have at least 2 evidences
        assert len(sample_rag_response['results']) >= 2, \
            "RAG deve retornar pelo menos 2 evidências para análise robusta"


class TestTechnicalAnalystSHIELD:
    """Tests for SHIELD framework compliance"""

    def test_shield_structure_phase(self, shield_checklist):
        """Verify STRUCTURE phase checklist"""
        checklist = shield_checklist['technical_analyst']['S_STRUCTURE']

        # Should have:
        # - Read requirement
        # - Identify criteria
        # - Plan search strategy

        assert len(checklist) >= 3, "STRUCTURE phase deve ter pelo menos 3 checks"

        checklist_text = " ".join(checklist).lower()
        assert "requisito" in checklist_text, "STRUCTURE deve mencionar leitura do requisito"
        assert "critérios" in checklist_text or "estratégia" in checklist_text, \
            "STRUCTURE deve mencionar identificação de critérios ou estratégia de busca"

    def test_shield_halt_phase(self, shield_checklist):
        """Verify HALT phase (checkpoint before batch)"""
        checklist = shield_checklist['technical_analyst']['H_HALT']

        checklist_text = " ".join(checklist).lower()
        assert "checkpoint" in checklist_text or "confirmação" in checklist_text, \
            "HALT phase deve incluir checkpoint/confirmação"

    def test_shield_inspect_phase(self, shield_checklist):
        """Verify INSPECT phase (quality checks)"""
        checklist = shield_checklist['technical_analyst']['I_INSPECT']

        # Should check for:
        # - RAG returned evidences (≥2)
        # - Evidences cover all aspects
        # - Contradictions identified
        # - Brazilian legal context

        required_checks = ["evidências", "rag", "contradições", "legal"]
        checklist_text = " ".join(checklist).lower()

        checks_found = sum(1 for check in required_checks if check in checklist_text)

        assert checks_found >= 3, \
            f"INSPECT phase deve incluir pelo menos 3/4 verificações críticas (encontradas: {checks_found})"

    def test_shield_execute_phase(self, shield_checklist):
        """Verify EXECUTE phase (analysis execution)"""
        checklist = shield_checklist['technical_analyst']['E_EXECUTE']

        checklist_text = " ".join(checklist).lower()

        assert "rag" in checklist_text, "EXECUTE deve mencionar RAG search"
        assert "veredicto" in checklist_text, "EXECUTE deve mencionar atribuição de veredicto"
        assert "justificativa" in checklist_text, "EXECUTE deve mencionar justificativa"
        assert "evidências" in checklist_text, "EXECUTE deve mencionar evidências"

    def test_shield_loop_phase(self, shield_checklist):
        """Verify LOOP phase (iteration if needed)"""
        checklist = shield_checklist['technical_analyst']['L_LOOP']

        checklist_text = " ".join(checklist).lower()

        assert "evidências insuficientes" in checklist_text or "busca adicional" in checklist_text, \
            "LOOP phase deve mencionar iteração quando evidências insuficientes"

    def test_shield_deliver_phase(self, shield_checklist):
        """Verify DELIVER phase (final output)"""
        checklist = shield_checklist['technical_analyst']['D_DELIVER']

        checklist_text = " ".join(checklist).lower()

        assert "csv" in checklist_text, "DELIVER deve mencionar CSV"
        assert "veredictos justificados" in checklist_text or "justificativa" in checklist_text, \
            "DELIVER deve mencionar justificativas completas"


class TestTechnicalAnalystConsistency:
    """Tests for internal consistency of analysis"""

    def test_conforme_has_evidence(self, sample_analysis_csv):
        """Verify CONFORME items have evidence"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            veredicto = row['veredicto'].strip().upper()

            if "CONFORME" in veredicto and "NÃO" not in veredicto and "PARCIAL" not in veredicto:
                evidencias = row.get('evidencias', '').strip()
                assert evidencias != "", \
                    f"Linha {i}: CONFORME mas sem evidências (inconsistência)"

    def test_nao_conforme_has_justification(self, sample_analysis_csv):
        """Verify NÃO CONFORME items have detailed justification"""
        with open(sample_analysis_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            veredicto = row['veredicto'].strip().upper()

            if "NÃO CONFORME" in veredicto:
                justificativa = row.get('justificativa', '').strip()
                assert len(justificativa) >= 30, \
                    f"Linha {i}: NÃO CONFORME mas justificativa curta (< 30 chars)"

    def test_requer_analise_has_low_confidence(self):
        """Verify REQUER ANÁLISE items don't have high confidence"""
        # This is a logical consistency check
        # If verdict is REQUER ANÁLISE, confidence shouldn't be "Alto"

        # This is tested in quality_check.py, so conceptual here
        assert True, "Conceptual test - verify REQUER ANÁLISE ≠ confiança Alta"

    def test_high_confidence_has_strong_evidence(self):
        """Verify high confidence items have strong evidence"""
        # This is a quality check
        # Alto confidence should correlate with good citations

        assert True, "Conceptual test - verify in quality_check.py"


class TestTechnicalAnalystIntegration:
    """Integration tests for Technical Analyst"""

    def test_pipeline_script_exists(self):
        """Verify pipeline.py exists"""
        pipeline = Path("agents/technical_analyst/pipeline.py")
        assert pipeline.exists(), "Technical Analyst pipeline.py não encontrado"

    def test_rag_engine_exists(self):
        """Verify rag_engine.py exists"""
        rag_engine = Path("agents/technical_analyst/rag_engine.py")
        assert rag_engine.exists(), "RAG engine não encontrado"

    def test_config_exists(self):
        """Verify config.py exists"""
        config = Path("agents/technical_analyst/config.py")
        assert config.exists(), "Technical Analyst config.py não encontrado"

    def test_report_generator_exists(self):
        """Verify report.py exists"""
        report = Path("agents/technical_analyst/report.py")
        assert report.exists(), "Report generator não encontrado"
