#!/usr/bin/env python3
"""
Validation Engine for Document Structurer

Implements 14 domain-specific validation rules for Brazilian public procurement
editais, covering Legal Compliance, Completeness, and Consistency.

Total Rules: 30
- 8 Anti-Alucinação (AA-01 to AA-08) - Framework-wide
- 8 Estruturação (ED-01 to ED-08) - Document structure
- 6 Legal Compliance (LC-01 to LC-06) - NEW
- 4 Completeness (CP-01 to CP-04) - NEW
- 4 Consistency (CS-01 to CS-04) - NEW

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.1.0
História: 2.10 - Additional Validation Rules
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml


@dataclass
class ValidationResult:
    """Result of a single validation rule check"""
    rule_id: str
    rule_name: str
    category: str
    severity: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationReport:
    """Complete validation report"""
    total_rules_checked: int
    rules_passed: int
    rules_failed: int
    rules_warned: int
    overall_status: str  # PASS, FAIL, WARNING
    results: List[ValidationResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "summary": {
                "total_rules_checked": self.total_rules_checked,
                "rules_passed": self.rules_passed,
                "rules_failed": self.rules_failed,
                "rules_warned": self.rules_warned,
                "overall_status": self.overall_status,
                "timestamp": self.timestamp
            },
            "results": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "category": r.category,
                    "severity": r.severity,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "remediation": r.remediation
                }
                for r in self.results
            ]
        }


class ValidationEngine:
    """
    Validation engine implementing 14 new domain-specific rules
    for Brazilian public procurement editais.
    """

    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize validation engine.

        Args:
            rules_file: Path to validation_rules.yaml (optional)
        """
        if rules_file is None:
            # Default to validation_rules.yaml in same directory
            rules_file = Path(__file__).parent / "validation_rules.yaml"

        self.rules_file = Path(rules_file)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Load validation rules from YAML file"""
        if not self.rules_file.exists():
            # Return empty rules if file doesn't exist
            return {"validation_rules": {}}

        with open(self.rules_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # ==========================================================================
    # LEGAL COMPLIANCE RULES (LC-01 to LC-06)
    # ==========================================================================

    def validate_lc01_lei_8666_clauses(self, text: str) -> ValidationResult:
        """
        LC-01: Lei 8.666/93 - Cláusulas Obrigatórias
        Verifica presença de cláusulas obrigatórias da Lei 8.666/93
        """
        rule_id = "LC-01"
        rule_name = "Lei 8.666/93 - Cláusulas Obrigatórias"
        category = "Legal Compliance"
        severity = "CRITICAL"

        required_clauses = {
            "objeto": r"objeto.*licitação|objeto.*edital",
            "prazo": r"prazo.*entrega|prazo.*execução",
            "sancoes": r"sanções|penalidades|multa",
            "dotacao": r"dotação.*orçamentária|previsão.*orçamentária",
            "criterio": r"critério.*julgamento|tipo.*licitação"
        }

        found_clauses = {}
        missing_clauses = []

        for clause_name, pattern in required_clauses.items():
            match = re.search(pattern, text, re.IGNORECASE)
            found_clauses[clause_name] = bool(match)
            if not match:
                missing_clauses.append(clause_name)

        passed = len(missing_clauses) == 0

        message = (
            f"Todas as 5 cláusulas obrigatórias encontradas" if passed else
            f"Faltam {len(missing_clauses)} cláusula(s): {', '.join(missing_clauses)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "found_clauses": found_clauses,
                "missing_clauses": missing_clauses,
                "total_required": len(required_clauses)
            },
            remediation="Adicionar cláusulas faltantes conforme Lei 8.666/93" if not passed else None
        )

    def validate_lc02_lei_14133_compatibility(self, text: str) -> ValidationResult:
        """
        LC-02: Lei 14.133/2021 - Compatibilidade
        Verifica se edital é compatível com nova Lei de Licitações
        """
        rule_id = "LC-02"
        rule_name = "Lei 14.133/2021 - Compatibilidade"
        category = "Legal Compliance"
        severity = "WARNING"

        # Check for references to new law
        lei_14133_match = re.search(r"lei.*14\.?133|nova.*lei.*licitações", text, re.IGNORECASE)
        lei_8666_match = re.search(r"lei.*8\.?666", text, re.IGNORECASE)

        references_new_law = bool(lei_14133_match)
        references_old_law = bool(lei_8666_match)

        # Determine compatibility
        if references_new_law:
            passed = True
            message = "Edital referencia Lei 14.133/2021 (nova lei)"
        elif references_old_law:
            passed = True  # Still valid during transition period
            message = "Edital referencia Lei 8.666/93 (antiga lei - ainda válida)"
        else:
            passed = False
            message = "Nenhuma referência clara à legislação de licitações"

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "references_lei_14133": references_new_law,
                "references_lei_8666": references_old_law
            },
            remediation="Verificar se edital deve ser atualizado para Lei 14.133/2021" if not passed else None
        )

    def validate_lc03_minimum_deadlines(self, text: str, modalidade: Optional[str] = None) -> ValidationResult:
        """
        LC-03: Prazos Legais Mínimos
        Verifica se prazos atendem aos mínimos legais por modalidade
        """
        rule_id = "LC-03"
        rule_name = "Prazos Legais Mínimos"
        category = "Legal Compliance"
        severity = "CRITICAL"

        # Extract modalidade if not provided
        if not modalidade:
            modalidade_match = re.search(
                r"modalidade.*(?:pregão|concorrência|tomada.*preços)",
                text,
                re.IGNORECASE
            )
            modalidade = modalidade_match.group(0).lower() if modalidade_match else "desconhecida"

        # Define minimum deadlines by modalidade
        minimum_deadlines = {
            "pregão": {"proposta": 8, "impugnacao": 3},
            "concorrência": {"proposta": 30, "impugnacao": 5},
            "tomada de preços": {"proposta": 15, "impugnacao": 5}
        }

        # Extract prazo de proposta
        prazo_proposta_match = re.search(r"prazo.*(?:proposta|envio).*?(\d+).*dias?", text, re.IGNORECASE)
        prazo_proposta = int(prazo_proposta_match.group(1)) if prazo_proposta_match else None

        # Extract prazo de impugnação
        prazo_impugnacao_match = re.search(r"impugnação.*?(\d+).*dias?", text, re.IGNORECASE)
        prazo_impugnacao = int(prazo_impugnacao_match.group(1)) if prazo_impugnacao_match else None

        # Validate deadlines
        issues = []
        for mod_key, min_deadlines in minimum_deadlines.items():
            if mod_key in modalidade.lower():
                if prazo_proposta and prazo_proposta < min_deadlines["proposta"]:
                    issues.append(
                        f"Prazo de proposta ({prazo_proposta} dias) inferior ao mínimo ({min_deadlines['proposta']} dias)"
                    )
                if prazo_impugnacao and prazo_impugnacao < min_deadlines["impugnacao"]:
                    issues.append(
                        f"Prazo de impugnação ({prazo_impugnacao} dias) inferior ao mínimo ({min_deadlines['impugnacao']} dias)"
                    )

        passed = len(issues) == 0

        message = (
            "Todos os prazos atendem aos mínimos legais" if passed else
            f"Problemas encontrados: {'; '.join(issues)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "modalidade": modalidade,
                "prazo_proposta_dias": prazo_proposta,
                "prazo_impugnacao_dias": prazo_impugnacao,
                "issues": issues
            },
            remediation="Ajustar prazos para atender requisitos legais mínimos" if not passed else None
        )

    def validate_lc04_garantia_requirements(self, text: str) -> ValidationResult:
        """
        LC-04: Garantia - Requisitos
        Verifica se requisitos de garantia (caução) estão presentes
        """
        rule_id = "LC-04"
        rule_name = "Garantia - Requisitos"
        category = "Legal Compliance"
        severity = "WARNING"

        # Check for garantia mention
        garantia_match = re.search(r"garantia.*execução|caução", text, re.IGNORECASE)

        # Check for percentage
        percentage_match = re.search(r"(\d+)%.*valor.*contrato|valor.*contrato.*(\d+)%", text, re.IGNORECASE)

        # Check for modalities
        modalidades_match = re.search(
            r"caução|seguro.*garantia|fiança.*bancária",
            text,
            re.IGNORECASE
        )

        garantia_mentioned = bool(garantia_match)
        percentage_defined = bool(percentage_match)
        modalidades_defined = bool(modalidades_match)

        # If garantia is required, check if properly defined
        if garantia_mentioned:
            passed = percentage_defined and modalidades_defined
            if not passed:
                missing = []
                if not percentage_defined:
                    missing.append("percentual")
                if not modalidades_defined:
                    missing.append("modalidades")
                message = f"Garantia mencionada mas faltam: {', '.join(missing)}"
            else:
                message = "Requisitos de garantia adequadamente definidos"
        else:
            # No garantia required - pass
            passed = True
            message = "Garantia não exigida no edital"

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "garantia_mentioned": garantia_mentioned,
                "percentage_defined": percentage_defined,
                "modalidades_defined": modalidades_defined
            },
            remediation="Definir modalidades e percentuais conforme Art. 56 da Lei 8.666/93" if not passed else None
        )

    def validate_lc05_habilitacao_juridica(self, text: str) -> ValidationResult:
        """
        LC-05: Habilitação Jurídica
        Verifica se exigências de habilitação jurídica estão presentes
        """
        rule_id = "LC-05"
        rule_name = "Habilitação Jurídica"
        category = "Legal Compliance"
        severity = "CRITICAL"

        required_docs = {
            "registro_comercial": r"registro.*comercial|junta.*comercial",
            "ato_constitutivo": r"ato.*constitutivo|contrato.*social|estatuto",
            "cnpj": r"inscrição.*cnpj|cadastro.*nacional",
            "fgts": r"regularidade.*fgts|certificado.*fgts"
        }

        found_docs = {}
        missing_docs = []

        for doc_name, pattern in required_docs.items():
            match = re.search(pattern, text, re.IGNORECASE)
            found_docs[doc_name] = bool(match)
            if not match:
                missing_docs.append(doc_name)

        passed = len(missing_docs) == 0

        message = (
            "Todos os documentos de habilitação jurídica listados" if passed else
            f"Faltam {len(missing_docs)} documento(s): {', '.join(missing_docs)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "found_docs": found_docs,
                "missing_docs": missing_docs,
                "total_required": len(required_docs)
            },
            remediation="Incluir todos os documentos exigidos por Lei (Art. 28-29)" if not passed else None
        )

    def validate_lc06_qualificacao_tecnica(self, text: str) -> ValidationResult:
        """
        LC-06: Qualificação Técnica
        Verifica se exigências de qualificação técnica estão presentes
        """
        rule_id = "LC-06"
        rule_name = "Qualificação Técnica"
        category = "Legal Compliance"
        severity = "WARNING"

        qualificacao_items = {
            "atestado": r"atestado.*capacidade.*técnica|comprovação.*técnica",
            "responsavel_tecnico": r"responsável.*técnico|profissional.*habilitado",
            "certidao_acervo": r"certidão.*acervo.*técnico|registro.*crea|registro.*cau"
        }

        found_items = {}
        for item_name, pattern in qualificacao_items.items():
            match = re.search(pattern, text, re.IGNORECASE)
            found_items[item_name] = bool(match)

        # At least one item should be present for technical qualification
        any_found = any(found_items.values())
        passed = any_found

        message = (
            f"Requisitos de qualificação técnica presentes ({sum(found_items.values())}/{len(found_items)} itens)" if passed else
            "Nenhum requisito de qualificação técnica identificado"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={"found_items": found_items},
            remediation="Adequar exigências técnicas ao objeto da licitação" if not passed else None
        )

    # ==========================================================================
    # COMPLETENESS RULES (CP-01 to CP-04)
    # ==========================================================================

    def validate_cp01_mandatory_annexes(self, text: str) -> ValidationResult:
        """
        CP-01: Anexos Obrigatórios Referenciados
        Verifica se todos os anexos obrigatórios estão referenciados
        """
        rule_id = "CP-01"
        rule_name = "Anexos Obrigatórios Referenciados"
        category = "Completeness"
        severity = "WARNING"

        mandatory_annexes = {
            "termo_referencia": r"termo.*referência|projeto.*básico",
            "minuta_contrato": r"minuta.*contrato",
            "modelo_proposta": r"modelo.*proposta",
            "modelo_declaracoes": r"modelo.*declarações|modelo.*declaracao"
        }

        found_annexes = {}
        missing_annexes = []

        for annex_name, pattern in mandatory_annexes.items():
            match = re.search(pattern, text, re.IGNORECASE)
            found_annexes[annex_name] = bool(match)
            if not match:
                missing_annexes.append(annex_name)

        passed = len(missing_annexes) == 0

        message = (
            "Todos os anexos obrigatórios referenciados" if passed else
            f"Faltam {len(missing_annexes)} anexo(s): {', '.join(missing_annexes)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "found_annexes": found_annexes,
                "missing_annexes": missing_annexes
            },
            remediation="Listar todos os anexos obrigatórios com identificação clara" if not passed else None
        )

    def validate_cp02_contact_information(self, text: str) -> ValidationResult:
        """
        CP-02: Informações de Contato Completas
        Verifica presença de informações de contato do órgão
        """
        rule_id = "CP-02"
        rule_name = "Informações de Contato Completas"
        category = "Completeness"
        severity = "WARNING"

        # Check for phone
        phone_match = re.search(r"\(\d{2}\).*\d{4,5}-?\d{4}|telefone.*\d+", text, re.IGNORECASE)

        # Check for email
        email_match = re.search(r"[\w\.]+@[\w\.]+\.[a-zA-Z]{2,}", text)

        # Check for address
        address_match = re.search(
            r"endereço|rua|avenida.*\d+|cep.*\d{5}-?\d{3}",
            text,
            re.IGNORECASE
        )

        # Check for office hours
        hours_match = re.search(r"horário.*atendimento|expediente", text, re.IGNORECASE)

        has_phone = bool(phone_match)
        has_email = bool(email_match)
        has_address = bool(address_match)
        has_hours = bool(hours_match)

        # At least phone and email required
        passed = has_phone and has_email

        contact_info = []
        if has_phone:
            contact_info.append("telefone")
        if has_email:
            contact_info.append("e-mail")
        if has_address:
            contact_info.append("endereço")
        if has_hours:
            contact_info.append("horário")

        message = (
            f"Informações de contato presentes: {', '.join(contact_info)}" if passed else
            "Informações de contato insuficientes (mínimo: telefone e e-mail)"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "has_phone": has_phone,
                "has_email": has_email,
                "has_address": has_address,
                "has_hours": has_hours
            },
            remediation="Incluir telefone, e-mail e endereço do órgão licitante" if not passed else None
        )

    def validate_cp03_complete_schedule(self, text: str) -> ValidationResult:
        """
        CP-03: Cronograma/Calendário Completo
        Verifica se cronograma com datas importantes está presente
        """
        rule_id = "CP-03"
        rule_name = "Cronograma/Calendário Completo"
        category = "Completeness"
        severity = "CRITICAL"

        critical_dates = {
            "publicacao": r"publicação.*edital|data.*publicação",
            "esclarecimento": r"prazo.*esclarecimento|esclarecimento.*até",
            "abertura": r"data.*sessão|abertura.*proposta|data.*pregão",
            "vigencia": r"início.*vigência|assinatura.*contrato"
        }

        found_dates = {}
        missing_dates = []

        for date_name, pattern in critical_dates.items():
            match = re.search(pattern, text, re.IGNORECASE)
            found_dates[date_name] = bool(match)
            if not match:
                missing_dates.append(date_name)

        passed = len(missing_dates) == 0

        message = (
            "Todas as datas críticas presentes" if passed else
            f"Faltam {len(missing_dates)} data(s): {', '.join(missing_dates)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "found_dates": found_dates,
                "missing_dates": missing_dates
            },
            remediation="Incluir cronograma completo com todas as datas relevantes" if not passed else None
        )

    def validate_cp04_payment_terms(self, text: str) -> ValidationResult:
        """
        CP-04: Condições de Pagamento Definidas
        Verifica se condições e prazos de pagamento estão claros
        """
        rule_id = "CP-04"
        rule_name = "Condições de Pagamento Definidas"
        category = "Completeness"
        severity = "CRITICAL"

        payment_elements = {
            "prazo": r"prazo.*pagamento|pagamento.*\d+.*dias",
            "forma": r"forma.*pagamento(?!.*prazo)|condições.*pagamento(?!.*prazo)",  # Not if it mentions prazo
            "medicao": r"medição|faturamento|nota.*fiscal",
            "reajuste": r"reajuste|correção.*monetária|índice"
        }

        found_elements = {}
        for element_name, pattern in payment_elements.items():
            match = re.search(pattern, text, re.IGNORECASE)
            found_elements[element_name] = bool(match)

        # Special check for "forma" - needs explicit mention separate from prazo
        # If only "prazo de pagamento" is mentioned, forma should be False
        if found_elements.get("forma", False):
            # Verify forma is mentioned separately
            forma_explicit = re.search(
                r"(?:forma|modalidade|tipo).*(?:pagamento|transferência|depósito|cheque|boleto)",
                text,
                re.IGNORECASE
            )
            found_elements["forma"] = bool(forma_explicit)

        # At least prazo and forma required
        passed = found_elements.get("prazo", False) and found_elements.get("forma", False)

        message = (
            f"Condições de pagamento definidas ({sum(found_elements.values())}/{len(found_elements)} elementos)" if passed else
            "Informações de pagamento incompletas (mínimo: prazo e forma)"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={"found_elements": found_elements},
            remediation="Definir prazo, forma e processo de pagamento detalhadamente" if not passed else None
        )

    # ==========================================================================
    # CONSISTENCY RULES (CS-01 to CS-04)
    # ==========================================================================

    def validate_cs01_chronological_dates(self, text: str, extracted_dates: Optional[Dict[str, str]] = None) -> ValidationResult:
        """
        CS-01: Ordem Cronológica de Datas
        Verifica se todas as datas estão em ordem cronológica lógica
        """
        rule_id = "CS-01"
        rule_name = "Ordem Cronológica de Datas"
        category = "Consistency"
        severity = "WARNING"

        # This is a simplified check - in production, would parse actual dates
        # For now, just check if date-related terms appear in logical order

        # Extract date mentions in order of appearance
        date_patterns = [
            ("publicacao", r"(?:data|em)\s+(?:de\s+)?publicação"),
            ("abertura", r"data.*(?:sessão|abertura|pregão)"),
            ("entrega", r"prazo.*entrega"),
            ("vigencia", r"início.*vigência")
        ]

        date_positions = {}
        for date_name, pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_positions[date_name] = match.start()

        # Check if dates appear in expected order
        expected_order = ["publicacao", "abertura", "entrega", "vigencia"]
        found_order = sorted(date_positions.keys(), key=lambda x: date_positions[x])

        # Filter to only dates that exist in both
        common_dates = [d for d in expected_order if d in found_order]
        actual_order = [d for d in found_order if d in expected_order]

        passed = common_dates == actual_order

        message = (
            "Datas aparecem em ordem cronológica lógica" if passed else
            f"Ordem esperada: {' → '.join(common_dates)}, encontrada: {' → '.join(actual_order)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "expected_order": common_dates,
                "actual_order": actual_order,
                "date_positions": date_positions
            },
            remediation="Corrigir sequência de datas para ordem cronológica correta" if not passed else None
        )

    def validate_cs02_value_consistency(self, text: str, item_values: Optional[List[float]] = None, total_value: Optional[float] = None) -> ValidationResult:
        """
        CS-02: Soma de Valores (Itens vs. Total)
        Verifica se soma dos itens corresponde ao valor total estimado
        """
        rule_id = "CS-02"
        rule_name = "Soma de Valores (Itens vs. Total)"
        category = "Consistency"
        severity = "CRITICAL"

        # Extract total value if not provided
        if total_value is None:
            total_match = re.search(r"valor.*total.*(?:estimado|global).*R?\$\s*([\d\.,]+)", text, re.IGNORECASE)
            if total_match:
                total_str = total_match.group(1).replace('.', '').replace(',', '.')
                total_value = float(total_str)

        # Extract item values if not provided
        if item_values is None:
            item_matches = re.findall(r"(?:item|lote).*\d+.*R?\$\s*([\d\.,]+)", text, re.IGNORECASE)
            item_values = []
            for match in item_matches:
                value_str = match.replace('.', '').replace(',', '.')
                try:
                    item_values.append(float(value_str))
                except ValueError:
                    pass

        # Validate if we have enough data
        if not total_value or not item_values:
            passed = True  # Cannot validate without data
            message = "Valores insuficientes para validar consistência"
            details = {
                "total_value": total_value,
                "item_count": len(item_values) if item_values else 0,
                "validation": "skipped"
            }
        else:
            sum_items = sum(item_values)
            tolerance = 0.01  # 1%
            difference = abs(sum_items - total_value)
            difference_percent = (difference / total_value) * 100 if total_value > 0 else 0

            passed = difference_percent <= tolerance

            message = (
                f"Soma dos itens (R$ {sum_items:,.2f}) = valor total (R$ {total_value:,.2f})" if passed else
                f"Diferença de {difference_percent:.2f}% entre soma (R$ {sum_items:,.2f}) e total (R$ {total_value:,.2f})"
            )

            details = {
                "total_value": total_value,
                "sum_of_items": sum_items,
                "item_count": len(item_values),
                "difference": difference,
                "difference_percent": difference_percent,
                "tolerance_percent": tolerance
            }

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details=details,
            remediation="Corrigir valores dos itens ou valor total para consistência" if not passed else None
        )

    def validate_cs03_unit_consistency(self, text: str) -> ValidationResult:
        """
        CS-03: Unidades de Medida Consistentes
        Verifica se unidades de medida são usadas consistentemente
        """
        rule_id = "CS-03"
        rule_name = "Unidades de Medida Consistentes"
        category = "Consistency"
        severity = "WARNING"

        # Extract units of measurement
        unit_patterns = {
            "unidade": r"\b(?:unidade|un|und|peça|pç)\b",
            "metro": r"\b(?:metro|m|metros)\b",
            "quilograma": r"\b(?:quilograma|kg|kilo)\b",
            "litro": r"\b(?:litro|l|lt)\b",
            "hora": r"\b(?:hora|h|hrs)\b"
        }

        found_units = {}
        for unit_type, pattern in unit_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_units[unit_type] = {
                    "count": len(matches),
                    "variants": list(set(m.lower() for m in matches))
                }

        # Check for inconsistent usage (same unit type, different variants)
        inconsistencies = []
        for unit_type, data in found_units.items():
            if len(data["variants"]) > 1:
                inconsistencies.append(f"{unit_type}: {', '.join(data['variants'])}")

        passed = len(inconsistencies) == 0

        message = (
            "Unidades de medida usadas consistentemente" if passed else
            f"Inconsistências em {len(inconsistencies)} tipo(s): {'; '.join(inconsistencies)}"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "found_units": found_units,
                "inconsistencies": inconsistencies
            },
            remediation="Padronizar unidades conforme INMETRO ou incluir conversões" if not passed else None
        )

    def validate_cs04_cross_references(self, text: str) -> ValidationResult:
        """
        CS-04: Referências Cruzadas Válidas
        Verifica se todas as referências a seções/itens existem
        """
        rule_id = "CS-04"
        rule_name = "Referências Cruzadas Válidas"
        category = "Consistency"
        severity = "WARNING"

        # Extract references
        references = re.findall(
            r"(?:conforme|vide|ver).*(?:item|seção|anexo|capítulo).*?([\d\.]+|[IiVvXx]+)",
            text,
            re.IGNORECASE
        )

        # Extract existing sections
        existing_sections = re.findall(r"^\d+\.?\d*\.?\d*\s", text, re.MULTILINE)

        # Simplified check: ensure references are found in document
        broken_references = []
        for ref in references:
            # Simple check: see if reference number appears as section
            if not re.search(rf"^{re.escape(ref)}\s", text, re.MULTILINE):
                broken_references.append(ref)

        passed = len(broken_references) == 0

        message = (
            f"Todas as {len(references)} referências verificadas" if passed else
            f"{len(broken_references)} referência(s) possivelmente quebrada(s)"
        )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            passed=passed,
            message=message,
            details={
                "total_references": len(references),
                "broken_references": broken_references,
                "existing_sections_count": len(existing_sections)
            },
            remediation="Corrigir referências quebradas ou adicionar seções faltantes" if not passed else None
        )

    # ==========================================================================
    # VALIDATION ORCHESTRATION
    # ==========================================================================

    def validate_all(self, text: str, **kwargs) -> ValidationReport:
        """
        Run all 14 validation rules.

        Args:
            text: Edital text to validate
            **kwargs: Additional parameters for specific rules

        Returns:
            ValidationReport with all results
        """
        results = []

        # Legal Compliance (6 rules)
        results.append(self.validate_lc01_lei_8666_clauses(text))
        results.append(self.validate_lc02_lei_14133_compatibility(text))
        results.append(self.validate_lc03_minimum_deadlines(text, kwargs.get('modalidade')))
        results.append(self.validate_lc04_garantia_requirements(text))
        results.append(self.validate_lc05_habilitacao_juridica(text))
        results.append(self.validate_lc06_qualificacao_tecnica(text))

        # Completeness (4 rules)
        results.append(self.validate_cp01_mandatory_annexes(text))
        results.append(self.validate_cp02_contact_information(text))
        results.append(self.validate_cp03_complete_schedule(text))
        results.append(self.validate_cp04_payment_terms(text))

        # Consistency (4 rules)
        results.append(self.validate_cs01_chronological_dates(text, kwargs.get('extracted_dates')))
        results.append(self.validate_cs02_value_consistency(
            text,
            kwargs.get('item_values'),
            kwargs.get('total_value')
        ))
        results.append(self.validate_cs03_unit_consistency(text))
        results.append(self.validate_cs04_cross_references(text))

        # Calculate statistics
        total_rules = len(results)
        rules_passed = sum(1 for r in results if r.passed)
        rules_failed = sum(1 for r in results if not r.passed and r.severity == "CRITICAL")
        rules_warned = sum(1 for r in results if not r.passed and r.severity == "WARNING")

        # Determine overall status
        if rules_failed > 0:
            overall_status = "FAIL"
        elif rules_warned > 0:
            overall_status = "WARNING"
        else:
            overall_status = "PASS"

        return ValidationReport(
            total_rules_checked=total_rules,
            rules_passed=rules_passed,
            rules_failed=rules_failed,
            rules_warned=rules_warned,
            overall_status=overall_status,
            results=results
        )

    def validate_by_category(self, category: str, text: str, **kwargs) -> List[ValidationResult]:
        """
        Run validation rules for a specific category.

        Args:
            category: 'legal', 'completeness', or 'consistency'
            text: Edital text to validate
            **kwargs: Additional parameters

        Returns:
            List of ValidationResults for that category
        """
        if category.lower() == "legal":
            return [
                self.validate_lc01_lei_8666_clauses(text),
                self.validate_lc02_lei_14133_compatibility(text),
                self.validate_lc03_minimum_deadlines(text, kwargs.get('modalidade')),
                self.validate_lc04_garantia_requirements(text),
                self.validate_lc05_habilitacao_juridica(text),
                self.validate_lc06_qualificacao_tecnica(text)
            ]
        elif category.lower() == "completeness":
            return [
                self.validate_cp01_mandatory_annexes(text),
                self.validate_cp02_contact_information(text),
                self.validate_cp03_complete_schedule(text),
                self.validate_cp04_payment_terms(text)
            ]
        elif category.lower() == "consistency":
            return [
                self.validate_cs01_chronological_dates(text, kwargs.get('extracted_dates')),
                self.validate_cs02_value_consistency(text, kwargs.get('item_values'), kwargs.get('total_value')),
                self.validate_cs03_unit_consistency(text),
                self.validate_cs04_cross_references(text)
            ]
        else:
            raise ValueError(f"Unknown category: {category}")


# Convenience functions
def validate_edital(text: str, **kwargs) -> ValidationReport:
    """
    Validate edital text against all 14 new rules.

    Args:
        text: Edital text to validate
        **kwargs: Additional parameters for specific rules

    Returns:
        ValidationReport with all results
    """
    engine = ValidationEngine()
    return engine.validate_all(text, **kwargs)


def validate_edital_category(category: str, text: str, **kwargs) -> List[ValidationResult]:
    """
    Validate edital against rules in a specific category.

    Args:
        category: 'legal', 'completeness', or 'consistency'
        text: Edital text to validate
        **kwargs: Additional parameters

    Returns:
        List of ValidationResults
    """
    engine = ValidationEngine()
    return engine.validate_by_category(category, text, **kwargs)


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("Validation Engine - Demo")
    print("=" * 60)

    # Sample edital text (simplified)
    sample_text = """
    EDITAL Nº 001/2025 - PREGÃO ELETRÔNICO

    1. OBJETO DA LICITAÇÃO
    Aquisição de Sistema de Videomonitoramento Urbano

    2. VALOR ESTIMADO
    R$ 2.500.000,00 (dois milhões e quinhentos mil reais)

    3. PRAZO DE ENTREGA
    180 dias corridos

    4. SANÇÕES E PENALIDADES
    Multa de até 20% do valor do contrato

    5. DOTAÇÃO ORÇAMENTÁRIA
    Projeto Atividade 1234.5678

    6. CRITÉRIO DE JULGAMENTO
    Menor preço global

    Lei de referência: Lei 8.666/93
    Modalidade: Pregão Eletrônico
    Prazo para envio de propostas: 10 dias úteis
    Prazo para impugnação: 5 dias úteis

    Contato: (11) 1234-5678 | licitacao@exemplo.gov.br
    Endereço: Rua Exemplo, 123 - São Paulo/SP

    Data de publicação: 15/01/2025
    Data da sessão de abertura: 01/02/2025
    """

    engine = ValidationEngine()
    report = engine.validate_all(sample_text)

    print(f"\nTotal Rules Checked: {report.total_rules_checked}")
    print(f"Passed: {report.rules_passed}")
    print(f"Failed (CRITICAL): {report.rules_failed}")
    print(f"Warned (WARNING): {report.rules_warned}")
    print(f"Overall Status: {report.overall_status}")

    print("\nDetailed Results:")
    print("-" * 60)
    for result in report.results:
        status_symbol = "✅" if result.passed else ("❌" if result.severity == "CRITICAL" else "⚠️")
        print(f"{status_symbol} {result.rule_id}: {result.rule_name}")
        print(f"   {result.message}")
        if result.remediation:
            print(f"   → {result.remediation}")
        print()

    print("=" * 60)
