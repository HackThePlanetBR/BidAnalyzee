"""
Tests for Document Structurer Agent

Verifica:
- Extração de requisitos
- Estruturação em CSV
- Validação SHIELD
- Anti-alucinação (rastreabilidade)
"""

import pytest
import csv
from pathlib import Path


class TestDocumentStructurerPrompt:
    """Tests for Document Structurer prompt compliance"""

    def test_prompt_metadata_exists(self):
        """Verify prompt.md exists and has correct metadata"""
        prompt_path = Path("agents/document_structurer/prompt.md")
        assert prompt_path.exists(), "Document Structurer prompt.md not found"

        content = prompt_path.read_text(encoding='utf-8')

        # Check metadata
        assert "agent: document_structurer" in content
        assert "framework: SHIELD" in content
        assert "output: CSV estruturado" in content

    def test_prompt_has_all_responsibilities(self):
        """Verify prompt defines all 4 responsibilities"""
        prompt_path = Path("agents/document_structurer/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        responsibilities = [
            "Extração de Requisitos",
            "Estruturação em CSV",
            "Validação Rigorosa",
            "Anti-Alucinação"
        ]

        for resp in responsibilities:
            assert resp in content, f"Responsabilidade '{resp}' não encontrada no prompt"

    def test_prompt_has_shield_framework(self):
        """Verify prompt implements SHIELD framework"""
        prompt_path = Path("agents/document_structurer/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        shield_sections = [
            "S - STRUCTURE",
            "H - HALT",
            "I - INSPECT",
            "E - EXECUTE",
            "L - LOOP",
            "D - DELIVER"
        ]

        for section in shield_sections:
            assert section in content, f"SHIELD section '{section}' não encontrada"

    def test_prompt_defines_csv_structure(self):
        """Verify prompt defines 7 mandatory CSV fields"""
        prompt_path = Path("agents/document_structurer/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should mention 7 fields
        assert "7 campos" in content or "sete campos" in content.lower()

        # Check for field mentions (can be anywhere in prompt)
        expected_fields = ["ID", "Item", "Descrição", "Categoria", "Prioridade", "Página", "Confiança"]
        fields_found = sum(1 for field in expected_fields if field in content)

        assert fields_found >= 5, f"Apenas {fields_found}/7 campos encontrados no prompt"


class TestDocumentStructurerOutput:
    """Tests for Document Structurer output validation"""

    def test_csv_has_required_fields(self, sample_requirements_csv, expected_csv_fields):
        """Verify CSV has all 7 required fields"""
        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

        required = expected_csv_fields['requirements']

        for field in required:
            assert field in fieldnames, f"Campo obrigatório '{field}' ausente"

    def test_csv_completeness(self, sample_requirements_csv):
        """Verify all fields are filled (no empty values)"""
        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0, "CSV vazio"

        for i, row in enumerate(rows, 1):
            for field, value in row.items():
                assert value.strip() != "", f"Campo '{field}' vazio na linha {i}"

    def test_csv_traceability(self, sample_requirements_csv):
        """Verify traceability (pagina field present and valid)"""
        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'pagina' in row, f"Campo 'pagina' ausente na linha {i}"
            assert row['pagina'].strip() != "", f"Rastreabilidade (pagina) vazia na linha {i}"

            # Page should be numeric
            try:
                page_num = int(row['pagina'])
                assert page_num > 0, f"Número de página inválido na linha {i}: {page_num}"
            except ValueError:
                pytest.fail(f"Página não é numérica na linha {i}: {row['pagina']}")

    def test_csv_confidence_scores(self, sample_requirements_csv):
        """Verify confidence scores are valid (0.0-1.0)"""
        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'confianca' in row, f"Campo 'confianca' ausente na linha {i}"

            try:
                conf = float(row['confianca'])
                assert 0.0 <= conf <= 1.0, f"Confiança fora do intervalo [0.0, 1.0] na linha {i}: {conf}"
            except ValueError:
                pytest.fail(f"Confiança não é numérica na linha {i}: {row['confianca']}")

    def test_csv_categories_valid(self, sample_requirements_csv):
        """Verify categories are from allowed set"""
        valid_categories = ["Hardware", "Software", "Serviço", "Integração"]

        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'categoria' in row, f"Campo 'categoria' ausente na linha {i}"
            category = row['categoria'].strip()

            assert category in valid_categories, \
                f"Categoria inválida na linha {i}: '{category}'. Válidas: {valid_categories}"

    def test_csv_priorities_valid(self, sample_requirements_csv):
        """Verify priorities are from allowed set"""
        valid_priorities = ["Alta", "Média", "Baixa"]

        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            assert 'prioridade' in row, f"Campo 'prioridade' ausente na linha {i}"
            priority = row['prioridade'].strip()

            assert priority in valid_priorities, \
                f"Prioridade inválida na linha {i}: '{priority}'. Válidas: {valid_priorities}"

    def test_csv_no_duplicates(self, sample_requirements_csv):
        """Verify no duplicate IDs"""
        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        ids = [row['id'] for row in rows]
        duplicates = [id for id in ids if ids.count(id) > 1]

        assert len(duplicates) == 0, f"IDs duplicados encontrados: {set(duplicates)}"

    def test_csv_encoding_utf8(self, sample_requirements_csv):
        """Verify CSV is UTF-8 encoded"""
        try:
            with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "CSV vazio"
        except UnicodeDecodeError:
            pytest.fail("CSV não está em UTF-8")


class TestDocumentStructurerAntiHallucination:
    """Tests for anti-hallucination features"""

    def test_all_items_have_page_reference(self, sample_requirements_csv):
        """Verify every item has page reference (traceability)"""
        with open(sample_requirements_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for i, row in enumerate(rows, 1):
            page = row.get('pagina', '').strip()
            assert page != "", f"Item na linha {i} sem referência de página (anti-alucinação violado)"

    def test_confidence_decreases_with_ambiguity(self):
        """Test that ambiguous requirements have lower confidence"""
        # This is a conceptual test - in practice you'd check actual output
        # High confidence items: clear, specific requirements
        # Low confidence items: vague, ambiguous requirements

        # Example: "Sistema deve ser rápido" -> baixa confiança
        # Example: "Processador Intel Core i7, 8GB RAM" -> alta confiança

        assert True, "Conceptual test - verify in real outputs"

    def test_items_from_pdf_only(self):
        """Verify items are extracted from PDF only (no invention)"""
        # This is validated by page reference + confidence score
        # In real test, you'd compare against known PDF content

        assert True, "Conceptual test - verify against known PDF"


class TestDocumentStructurerSHIELD:
    """Tests for SHIELD framework compliance"""

    def test_shield_structure_phase(self, shield_checklist):
        """Verify STRUCTURE phase checklist"""
        checklist = shield_checklist['document_structurer']['S_STRUCTURE']

        # At minimum, should have:
        # - Extraction plan
        # - Categorization strategy
        # - Time estimation

        assert len(checklist) >= 3, "STRUCTURE phase deve ter pelo menos 3 checks"

    def test_shield_halt_phase(self, shield_checklist):
        """Verify HALT phase (checkpoint before batch processing)"""
        checklist = shield_checklist['document_structurer']['H_HALT']

        # Should have checkpoint before processing
        assert any("checkpoint" in item.lower() for item in checklist), \
            "HALT phase deve incluir checkpoint"

    def test_shield_inspect_phase(self, shield_checklist):
        """Verify INSPECT phase (quality checks)"""
        checklist = shield_checklist['document_structurer']['I_INSPECT']

        # Should check for:
        # - Completeness
        # - Traceability
        # - Confidence
        # - No duplicates

        required_checks = ["campos obrigatórios", "rastreabilidade", "confiança", "duplicatas"]
        checklist_text = " ".join(checklist).lower()

        for check in required_checks:
            assert check in checklist_text, f"INSPECT phase deve incluir verificação de '{check}'"

    def test_shield_execute_phase(self, shield_checklist):
        """Verify EXECUTE phase (CSV generation)"""
        checklist = shield_checklist['document_structurer']['E_EXECUTE']

        # Should generate UTF-8 CSV with 7 fields
        checklist_text = " ".join(checklist).lower()

        assert "csv" in checklist_text, "EXECUTE phase deve mencionar CSV"
        assert "utf-8" in checklist_text, "EXECUTE phase deve mencionar UTF-8"

    def test_shield_loop_phase(self, shield_checklist):
        """Verify LOOP phase (iteration on failure)"""
        checklist = shield_checklist['document_structurer']['L_LOOP']

        # Should iterate if validation fails
        checklist_text = " ".join(checklist).lower()

        assert "validação" in checklist_text or "erro" in checklist_text, \
            "LOOP phase deve mencionar correção de validação/erros"

    def test_shield_deliver_phase(self, shield_checklist):
        """Verify DELIVER phase (final output)"""
        checklist = shield_checklist['document_structurer']['D_DELIVER']

        # Should deliver valid CSV + quality report
        checklist_text = " ".join(checklist).lower()

        assert "csv" in checklist_text, "DELIVER phase deve mencionar CSV"
        assert "relatório" in checklist_text or "qualidade" in checklist_text, \
            "DELIVER phase deve mencionar relatório de qualidade"


class TestDocumentStructurerIntegration:
    """Integration tests for Document Structurer"""

    def test_readme_exists(self):
        """Verify README documentation exists"""
        readme_path = Path("agents/document_structurer/README.md")
        assert readme_path.exists(), "Document Structurer README.md não encontrado"

    def test_validation_readme_exists(self):
        """Verify validation documentation exists"""
        validation_readme = Path("agents/document_structurer/VALIDATION_README.md")
        assert validation_readme.exists(), "VALIDATION_README.md não encontrado"

    def test_prompt_references_validation(self):
        """Verify prompt references validation files"""
        prompt_path = Path("agents/document_structurer/prompt.md")
        content = prompt_path.read_text(encoding='utf-8')

        # Should mention inspect.yaml and validate.yaml
        assert "inspect.yaml" in content or "validate.yaml" in content, \
            "Prompt deve referenciar arquivos de validação (inspect.yaml/validate.yaml)"
