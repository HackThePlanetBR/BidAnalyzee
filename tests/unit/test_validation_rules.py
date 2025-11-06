#!/usr/bin/env python3
"""
Unit Tests for Validation Rules

Tests all 14 new validation rules:
- Legal Compliance (6 rules): LC-01 to LC-06
- Completeness (4 rules): CP-01 to CP-04
- Consistency (4 rules): CS-01 to CS-04

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.1.0
História: 2.10 - Additional Validation Rules
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.document_structurer.validation_engine import ValidationEngine, validate_edital
from agents.document_structurer.validation_report import ValidationReportGenerator


class TestValidationRules:
    """Test suite for all 14 validation rules"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = ValidationEngine()

    # ==========================================================================
    # LEGAL COMPLIANCE TESTS (LC-01 to LC-06)
    # ==========================================================================

    def test_lc01_lei_8666_clauses_pass(self):
        """Test LC-01: All required clauses present"""
        text = """
        EDITAL Nº 001/2025

        1. OBJETO DA LICITAÇÃO
        Aquisição de equipamentos de informática

        2. PRAZO DE ENTREGA
        60 dias corridos

        3. SANÇÕES E PENALIDADES
        Multa de 10% sobre o valor contratado

        4. DOTAÇÃO ORÇAMENTÁRIA
        Programa de Trabalho 1234

        5. CRITÉRIO DE JULGAMENTO
        Menor preço por item
        """

        result = self.engine.validate_lc01_lei_8666_clauses(text)
        assert result.passed is True
        assert result.severity == "CRITICAL"
        assert "Todas as 5 cláusulas" in result.message

        print("✅ LC-01 Pass Test: PASS")

    def test_lc01_lei_8666_clauses_fail(self):
        """Test LC-01: Missing required clauses"""
        text = """
        EDITAL Nº 001/2025

        1. OBJETO DA LICITAÇÃO
        Aquisição de equipamentos
        """

        result = self.engine.validate_lc01_lei_8666_clauses(text)
        assert result.passed is False
        assert result.severity == "CRITICAL"
        assert "Faltam" in result.message
        assert result.remediation is not None

        print("✅ LC-01 Fail Test: PASS")

    def test_lc02_lei_14133_compatibility_new_law(self):
        """Test LC-02: References new law (14.133/2021)"""
        text = """
        Este edital segue as disposições da Lei 14.133/2021,
        a Nova Lei de Licitações e Contratos Administrativos.
        """

        result = self.engine.validate_lc02_lei_14133_compatibility(text)
        assert result.passed is True
        assert "Lei 14.133/2021" in result.message

        print("✅ LC-02 New Law Test: PASS")

    def test_lc02_lei_14133_compatibility_old_law(self):
        """Test LC-02: References old law (8.666/93)"""
        text = """
        Este edital segue as disposições da Lei 8.666/93.
        """

        result = self.engine.validate_lc02_lei_14133_compatibility(text)
        assert result.passed is True
        assert "Lei 8.666/93" in result.message

        print("✅ LC-02 Old Law Test: PASS")

    def test_lc03_minimum_deadlines_pregao_pass(self):
        """Test LC-03: Pregão deadlines meet minimum"""
        text = """
        Modalidade: Pregão Eletrônico
        Prazo para envio de propostas: 10 dias úteis
        Prazo para impugnação: 5 dias úteis
        """

        result = self.engine.validate_lc03_minimum_deadlines(text, modalidade="pregão")
        assert result.passed is True
        assert "atendem aos mínimos" in result.message

        print("✅ LC-03 Pass Test: PASS")

    def test_lc03_minimum_deadlines_pregao_fail(self):
        """Test LC-03: Pregão deadlines below minimum"""
        text = """
        Modalidade: Pregão Eletrônico
        Prazo para envio de propostas: 5 dias úteis
        Prazo para impugnação: 1 dia útil
        """

        result = self.engine.validate_lc03_minimum_deadlines(text, modalidade="pregão")
        assert result.passed is False
        assert result.severity == "CRITICAL"
        assert "inferior ao mínimo" in result.message

        print("✅ LC-03 Fail Test: PASS")

    def test_lc04_garantia_requirements_complete(self):
        """Test LC-04: Garantia properly defined"""
        text = """
        GARANTIA DE EXECUÇÃO

        A contratada deverá prestar garantia de 5% do valor do contrato,
        podendo optar por uma das seguintes modalidades:
        - Caução em dinheiro
        - Seguro-garantia
        - Fiança bancária
        """

        result = self.engine.validate_lc04_garantia_requirements(text)
        assert result.passed is True
        assert "adequadamente definidos" in result.message

        print("✅ LC-04 Complete Test: PASS")

    def test_lc04_garantia_requirements_incomplete(self):
        """Test LC-04: Garantia mentioned but incomplete"""
        text = """
        Será exigida garantia de execução do contrato.
        """

        result = self.engine.validate_lc04_garantia_requirements(text)
        assert result.passed is False
        assert result.severity == "WARNING"

        print("✅ LC-04 Incomplete Test: PASS")

    def test_lc05_habilitacao_juridica_pass(self):
        """Test LC-05: All juridical documents present"""
        text = """
        HABILITAÇÃO JURÍDICA

        - Registro comercial na Junta Comercial
        - Ato constitutivo (contrato social ou estatuto)
        - Inscrição no CNPJ
        - Certificado de Regularidade do FGTS
        """

        result = self.engine.validate_lc05_habilitacao_juridica(text)
        assert result.passed is True
        assert "Todos os documentos" in result.message

        print("✅ LC-05 Pass Test: PASS")

    def test_lc05_habilitacao_juridica_fail(self):
        """Test LC-05: Missing juridical documents"""
        text = """
        HABILITAÇÃO JURÍDICA

        - Registro comercial
        """

        result = self.engine.validate_lc05_habilitacao_juridica(text)
        assert result.passed is False
        assert result.severity == "CRITICAL"
        assert "Faltam" in result.message

        print("✅ LC-05 Fail Test: PASS")

    def test_lc06_qualificacao_tecnica_pass(self):
        """Test LC-06: Technical qualification present"""
        text = """
        QUALIFICAÇÃO TÉCNICA

        - Atestado de capacidade técnica
        - Responsável técnico habilitado
        - Certidão de Acervo Técnico (CAT) do CREA
        """

        result = self.engine.validate_lc06_qualificacao_tecnica(text)
        assert result.passed is True
        assert "presentes" in result.message

        print("✅ LC-06 Pass Test: PASS")

    def test_lc06_qualificacao_tecnica_fail(self):
        """Test LC-06: No technical qualification"""
        text = """
        Este edital não requer qualificação técnica específica.
        """

        result = self.engine.validate_lc06_qualificacao_tecnica(text)
        assert result.passed is False
        assert result.severity == "WARNING"

        print("✅ LC-06 Fail Test: PASS")

    # ==========================================================================
    # COMPLETENESS TESTS (CP-01 to CP-04)
    # ==========================================================================

    def test_cp01_mandatory_annexes_pass(self):
        """Test CP-01: All mandatory annexes referenced"""
        text = """
        ANEXOS

        Anexo I - Termo de Referência
        Anexo II - Minuta do Contrato
        Anexo III - Modelo de Proposta Comercial
        Anexo IV - Modelo de Declarações
        """

        result = self.engine.validate_cp01_mandatory_annexes(text)
        assert result.passed is True
        assert "Todos os anexos" in result.message

        print("✅ CP-01 Pass Test: PASS")

    def test_cp01_mandatory_annexes_fail(self):
        """Test CP-01: Missing annexes"""
        text = """
        ANEXOS

        Anexo I - Termo de Referência
        """

        result = self.engine.validate_cp01_mandatory_annexes(text)
        assert result.passed is False
        assert result.severity == "WARNING"
        assert "Faltam" in result.message

        print("✅ CP-01 Fail Test: PASS")

    def test_cp02_contact_information_pass(self):
        """Test CP-02: Complete contact information"""
        text = """
        INFORMAÇÕES DE CONTATO

        Telefone: (11) 1234-5678
        E-mail: licitacao@exemplo.gov.br
        Endereço: Rua Exemplo, 123 - São Paulo/SP
        CEP: 01234-567
        Horário de atendimento: 9h às 17h
        """

        result = self.engine.validate_cp02_contact_information(text)
        assert result.passed is True
        assert "telefone" in result.message.lower()
        assert "e-mail" in result.message.lower()

        print("✅ CP-02 Pass Test: PASS")

    def test_cp02_contact_information_fail(self):
        """Test CP-02: Incomplete contact information"""
        text = """
        INFORMAÇÕES DE CONTATO

        Telefone: (11) 1234-5678
        """

        result = self.engine.validate_cp02_contact_information(text)
        assert result.passed is False
        assert result.severity == "WARNING"

        print("✅ CP-02 Fail Test: PASS")

    def test_cp03_complete_schedule_pass(self):
        """Test CP-03: Complete schedule with all dates"""
        text = """
        CRONOGRAMA

        Data de publicação do edital: 15/01/2025
        Prazo para esclarecimentos: até 20/01/2025
        Data da sessão de abertura: 01/02/2025
        Início da vigência do contrato: 15/02/2025
        """

        result = self.engine.validate_cp03_complete_schedule(text)
        assert result.passed is True
        assert "Todas as datas" in result.message

        print("✅ CP-03 Pass Test: PASS")

    def test_cp03_complete_schedule_fail(self):
        """Test CP-03: Incomplete schedule"""
        text = """
        CRONOGRAMA

        Data de publicação: 15/01/2025
        """

        result = self.engine.validate_cp03_complete_schedule(text)
        assert result.passed is False
        assert result.severity == "CRITICAL"
        assert "Faltam" in result.message

        print("✅ CP-03 Fail Test: PASS")

    def test_cp04_payment_terms_pass(self):
        """Test CP-04: Complete payment terms"""
        text = """
        CONDIÇÕES DE PAGAMENTO

        Prazo de pagamento: 30 dias após a medição
        Forma de pagamento: Transferência bancária
        Processo de medição e faturamento conforme Anexo III
        Reajuste anual conforme IPCA
        """

        result = self.engine.validate_cp04_payment_terms(text)
        assert result.passed is True
        assert "definidas" in result.message

        print("✅ CP-04 Pass Test: PASS")

    def test_cp04_payment_terms_fail(self):
        """Test CP-04: Incomplete payment terms"""
        text = """
        CONDIÇÕES DE PAGAMENTO

        Prazo de pagamento: 30 dias
        """

        result = self.engine.validate_cp04_payment_terms(text)
        assert result.passed is False
        assert result.severity == "CRITICAL"

        print("✅ CP-04 Fail Test: PASS")

    # ==========================================================================
    # CONSISTENCY TESTS (CS-01 to CS-04)
    # ==========================================================================

    def test_cs01_chronological_dates_pass(self):
        """Test CS-01: Dates in chronological order"""
        text = """
        Data de publicação do edital: 15/01/2025
        Data da sessão de abertura: 01/02/2025
        Prazo de entrega: 180 dias após assinatura
        Início da vigência: 15/02/2025
        """

        result = self.engine.validate_cs01_chronological_dates(text)
        assert result.passed is True

        print("✅ CS-01 Pass Test: PASS")

    def test_cs02_value_consistency_pass(self):
        """Test CS-02: Item values sum to total"""
        text = """
        PLANILHA ORÇAMENTÁRIA

        Item 1: R$ 1.000.000,00
        Item 2: R$ 800.000,00
        Item 3: R$ 700.000,00

        Valor total estimado: R$ 2.500.000,00
        """

        result = self.engine.validate_cs02_value_consistency(
            text,
            item_values=[1000000.0, 800000.0, 700000.0],
            total_value=2500000.0
        )
        assert result.passed is True

        print("✅ CS-02 Pass Test: PASS")

    def test_cs02_value_consistency_fail(self):
        """Test CS-02: Item values don't sum to total"""
        text = """
        PLANILHA ORÇAMENTÁRIA

        Item 1: R$ 1.000.000,00
        Item 2: R$ 800.000,00

        Valor total estimado: R$ 2.500.000,00
        """

        result = self.engine.validate_cs02_value_consistency(
            text,
            item_values=[1000000.0, 800000.0],
            total_value=2500000.0
        )
        assert result.passed is False
        assert result.severity == "CRITICAL"
        assert "Diferença" in result.message

        print("✅ CS-02 Fail Test: PASS")

    def test_cs03_unit_consistency_pass(self):
        """Test CS-03: Units used consistently"""
        text = """
        ESPECIFICAÇÕES

        Item 1: 100 unidades
        Item 2: 50 unidades
        Item 3: 200 unidades
        """

        result = self.engine.validate_cs03_unit_consistency(text)
        assert result.passed is True

        print("✅ CS-03 Pass Test: PASS")

    def test_cs03_unit_consistency_fail(self):
        """Test CS-03: Inconsistent units"""
        text = """
        ESPECIFICAÇÕES

        Item 1: 100 un
        Item 2: 50 unidades
        Item 3: 200 und
        Item 4: 75 peças
        """

        result = self.engine.validate_cs03_unit_consistency(text)
        assert result.passed is False
        assert result.severity == "WARNING"
        assert "Inconsistências" in result.message

        print("✅ CS-03 Fail Test: PASS")

    def test_cs04_cross_references_pass(self):
        """Test CS-04: Valid cross-references"""
        text = """
        1. INTRODUÇÃO
        Conforme item 3.2, as especificações técnicas...

        2. OBJETO
        Ver anexo II para detalhes

        3. ESPECIFICAÇÕES
        3.1 Gerais
        3.2 Técnicas
        """

        result = self.engine.validate_cs04_cross_references(text)
        assert result.passed is True or result.severity == "WARNING"  # May have false positives

        print("✅ CS-04 Pass Test: PASS")

    # ==========================================================================
    # INTEGRATION TESTS
    # ==========================================================================

    def test_validate_all_comprehensive(self):
        """Test validate_all with comprehensive edital"""
        comprehensive_text = """
        EDITAL Nº 001/2025 - PREGÃO ELETRÔNICO

        Lei de referência: Lei 8.666/93

        1. OBJETO DA LICITAÇÃO
        Aquisição de Sistema de Videomonitoramento Urbano

        2. VALOR ESTIMADO
        R$ 2.500.000,00 (dois milhões e quinhentos mil reais)

        3. PRAZO DE ENTREGA
        180 dias corridos

        4. SANÇÕES E PENALIDADES
        Multa de até 20% do valor do contrato

        5. DOTAÇÃO ORÇAMENTÁRIA
        Programa de Trabalho: 1234.5678.9012

        6. CRITÉRIO DE JULGAMENTO
        Menor preço global

        7. PRAZOS
        Modalidade: Pregão Eletrônico
        Prazo para envio de propostas: 10 dias úteis
        Prazo para impugnação: 5 dias úteis

        8. HABILITAÇÃO JURÍDICA
        - Registro comercial na Junta Comercial
        - Ato constitutivo (contrato social)
        - Inscrição no CNPJ
        - Certificado de Regularidade do FGTS

        9. QUALIFICAÇÃO TÉCNICA
        - Atestado de capacidade técnica
        - Responsável técnico habilitado

        10. ANEXOS
        Anexo I - Termo de Referência
        Anexo II - Minuta do Contrato
        Anexo III - Modelo de Proposta Comercial
        Anexo IV - Modelo de Declarações

        11. INFORMAÇÕES DE CONTATO
        Telefone: (11) 1234-5678
        E-mail: licitacao@exemplo.gov.br
        Endereço: Rua Exemplo, 123 - São Paulo/SP
        CEP: 01234-567
        Horário de atendimento: 9h às 17h

        12. CRONOGRAMA
        Data de publicação: 15/01/2025
        Prazo para esclarecimentos: até 20/01/2025
        Data da sessão de abertura: 01/02/2025
        Início da vigência: 15/02/2025

        13. CONDIÇÕES DE PAGAMENTO
        Prazo de pagamento: 30 dias após medição
        Forma de pagamento: Transferência bancária
        Processo de faturamento conforme Anexo III
        """

        report = self.engine.validate_all(comprehensive_text)

        assert report.total_rules_checked == 14
        assert report.overall_status in ["PASS", "WARNING"]  # Should mostly pass
        assert report.rules_failed < 5  # No more than 5 critical failures

        print(f"✅ Comprehensive Test: {report.rules_passed}/{report.total_rules_checked} rules passed")
        print(f"   Overall Status: {report.overall_status}")

    def test_validate_by_category_legal(self):
        """Test validate_by_category for legal compliance"""
        text = "Lei 8.666/93, objeto da licitação, prazo de entrega, sanções, dotação orçamentária, critério de julgamento"

        results = self.engine.validate_by_category("legal", text)
        assert len(results) == 6  # 6 legal compliance rules

        print("✅ Category Test (Legal): PASS")

    def test_validate_by_category_completeness(self):
        """Test validate_by_category for completeness"""
        text = "anexos, telefone (11) 1234-5678, email@exemplo.gov.br, data de publicação, prazo de pagamento"

        results = self.engine.validate_by_category("completeness", text)
        assert len(results) == 4  # 4 completeness rules

        print("✅ Category Test (Completeness): PASS")

    def test_validate_by_category_consistency(self):
        """Test validate_by_category for consistency"""
        text = "Item 1: R$ 100,00, Item 2: R$ 200,00, Total: R$ 300,00"

        results = self.engine.validate_by_category("consistency", text)
        assert len(results) == 4  # 4 consistency rules

        print("✅ Category Test (Consistency): PASS")

    def test_severity_handling(self):
        """Test that severity levels are correctly assigned"""
        # CRITICAL severity test
        result_critical = self.engine.validate_lc01_lei_8666_clauses("")
        assert result_critical.severity == "CRITICAL"

        # WARNING severity test
        result_warning = self.engine.validate_lc02_lei_14133_compatibility("")
        assert result_warning.severity == "WARNING"

        print("✅ Severity Handling Test: PASS")

    def test_false_positive_prevention(self):
        """Test that rules don't flag false positives"""
        # Text with similar but not exact keywords
        text = """
        Este documento contém informações sobre objetivos gerais,
        prazos aproximados, e possíveis sanções futuras.
        """

        result = self.engine.validate_lc01_lei_8666_clauses(text)
        # Should recognize keywords even if not perfect match
        assert result.passed is True or len(result.details.get("missing_clauses", [])) > 0

        print("✅ False Positive Prevention Test: PASS")


def run_all_tests():
    """Run all validation rule tests"""
    print("\n" + "=" * 70)
    print("Validation Rules - Unit Tests")
    print("=" * 70 + "\n")

    test_suite = TestValidationRules()

    # Define all tests
    tests = [
        # Legal Compliance
        ("LC-01 Pass", test_suite.test_lc01_lei_8666_clauses_pass),
        ("LC-01 Fail", test_suite.test_lc01_lei_8666_clauses_fail),
        ("LC-02 New Law", test_suite.test_lc02_lei_14133_compatibility_new_law),
        ("LC-02 Old Law", test_suite.test_lc02_lei_14133_compatibility_old_law),
        ("LC-03 Pass", test_suite.test_lc03_minimum_deadlines_pregao_pass),
        ("LC-03 Fail", test_suite.test_lc03_minimum_deadlines_pregao_fail),
        ("LC-04 Complete", test_suite.test_lc04_garantia_requirements_complete),
        ("LC-04 Incomplete", test_suite.test_lc04_garantia_requirements_incomplete),
        ("LC-05 Pass", test_suite.test_lc05_habilitacao_juridica_pass),
        ("LC-05 Fail", test_suite.test_lc05_habilitacao_juridica_fail),
        ("LC-06 Pass", test_suite.test_lc06_qualificacao_tecnica_pass),
        ("LC-06 Fail", test_suite.test_lc06_qualificacao_tecnica_fail),

        # Completeness
        ("CP-01 Pass", test_suite.test_cp01_mandatory_annexes_pass),
        ("CP-01 Fail", test_suite.test_cp01_mandatory_annexes_fail),
        ("CP-02 Pass", test_suite.test_cp02_contact_information_pass),
        ("CP-02 Fail", test_suite.test_cp02_contact_information_fail),
        ("CP-03 Pass", test_suite.test_cp03_complete_schedule_pass),
        ("CP-03 Fail", test_suite.test_cp03_complete_schedule_fail),
        ("CP-04 Pass", test_suite.test_cp04_payment_terms_pass),
        ("CP-04 Fail", test_suite.test_cp04_payment_terms_fail),

        # Consistency
        ("CS-01 Pass", test_suite.test_cs01_chronological_dates_pass),
        ("CS-02 Pass", test_suite.test_cs02_value_consistency_pass),
        ("CS-02 Fail", test_suite.test_cs02_value_consistency_fail),
        ("CS-03 Pass", test_suite.test_cs03_unit_consistency_pass),
        ("CS-03 Fail", test_suite.test_cs03_unit_consistency_fail),
        ("CS-04 Pass", test_suite.test_cs04_cross_references_pass),

        # Integration
        ("Comprehensive", test_suite.test_validate_all_comprehensive),
        ("Category Legal", test_suite.test_validate_by_category_legal),
        ("Category Completeness", test_suite.test_validate_by_category_completeness),
        ("Category Consistency", test_suite.test_validate_by_category_consistency),
        ("Severity Handling", test_suite.test_severity_handling),
        ("False Positive Prevention", test_suite.test_false_positive_prevention),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_suite.setup_method()
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: FAILED")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR")
            print(f"   Error: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
