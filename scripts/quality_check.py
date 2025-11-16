#!/usr/bin/env python3
"""
Quality Check - Validação avançada de qualidade dos outputs

Verifica completude, consistência, raciocínio e evidências em análises
"""

import sys
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class QualityChecker:
    """Verifica qualidade de outputs de análise"""

    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
        self.score = 100.0

    def check_analysis_csv(self, csv_path: str) -> Dict[str, Any]:
        """
        Verifica qualidade de um CSV de análise

        Args:
            csv_path: Caminho do CSV

        Returns:
            Relatório de qualidade
        """
        self.checks = []
        self.warnings = []
        self.errors = []
        self.score = 100.0

        # Carregar CSV
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao ler CSV: {e}",
                "score": 0
            }

        if not rows:
            return {
                "status": "error",
                "message": "CSV vazio",
                "score": 0
            }

        # Executar verificações
        self._check_completeness(rows)
        self._check_consistency(rows)
        self._check_reasoning_quality(rows)
        self._check_evidence_quality(rows)
        self._check_confidence_levels(rows)
        self._check_verdict_distribution(rows)

        return {
            "status": "success",
            "score": self.score,
            "total_rows": len(rows),
            "checks_passed": len([c for c in self.checks if c["passed"]]),
            "checks_failed": len([c for c in self.checks if not c["passed"]]),
            "warnings": self.warnings,
            "errors": self.errors,
            "checks": self.checks
        }

    def _check_completeness(self, rows: List[Dict[str, Any]]):
        """Verifica se todos os campos obrigatórios estão preenchidos"""
        required_fields = [
            "item",
            "categoria",
            "descricao",
            "veredicto",
            "justificativa",
            "evidencias",
            "nivel_confianca"
        ]

        missing_counts = {field: 0 for field in required_fields}
        empty_counts = {field: 0 for field in required_fields}

        for row in rows:
            for field in required_fields:
                if field not in row:
                    missing_counts[field] += 1
                elif not row[field] or row[field].strip() == "":
                    empty_counts[field] += 1

        # Verificar missing
        for field, count in missing_counts.items():
            if count > 0:
                self.errors.append(f"Campo '{field}' ausente em {count} linhas")
                self.score -= 10

        # Verificar empty
        for field, count in empty_counts.items():
            if count > 0:
                pct = (count / len(rows)) * 100
                if pct > 10:  # > 10% vazio é erro
                    self.errors.append(f"Campo '{field}' vazio em {count} linhas ({pct:.1f}%)")
                    self.score -= 5
                elif pct > 0:
                    self.warnings.append(f"Campo '{field}' vazio em {count} linhas ({pct:.1f}%)")

        passed = len(self.errors) == 0
        self.checks.append({
            "name": "Completude de Campos",
            "passed": passed,
            "details": f"Campos obrigatórios: {', '.join(required_fields)}"
        })

    def _check_consistency(self, rows: List[Dict[str, Any]]):
        """Verifica consistência entre campos"""
        inconsistencies = []

        for i, row in enumerate(rows, 1):
            veredicto = row.get("veredicto", "").upper()
            justificativa = row.get("justificativa", "")
            evidencias = row.get("evidencias", "")

            # Veredicto CONFORME mas sem evidências
            if "CONFORME" in veredicto and "NÃO" not in veredicto and "PARCIAL" not in veredicto:
                if not evidencias or len(evidencias.strip()) < 10:
                    inconsistencies.append(f"Linha {i}: CONFORME sem evidências adequadas")

            # Veredicto NÃO CONFORME mas justificativa curta
            if "NÃO CONFORME" in veredicto:
                if len(justificativa.strip()) < 20:
                    inconsistencies.append(f"Linha {i}: NÃO CONFORME com justificativa curta")

            # REQUER ANÁLISE mas alta confiança
            if "REQUER" in veredicto:
                confianca = row.get("nivel_confianca", "").lower()
                if confianca == "alto":
                    inconsistencies.append(f"Linha {i}: REQUER ANÁLISE com confiança Alta (inconsistente)")

        if len(inconsistencies) > 0:
            pct = (len(inconsistencies) / len(rows)) * 100
            if pct > 5:
                self.errors.append(f"{len(inconsistencies)} inconsistências encontradas ({pct:.1f}%)")
                self.score -= 10
            else:
                self.warnings.append(f"{len(inconsistencies)} inconsistências encontradas ({pct:.1f}%)")
                self.score -= 2

        passed = len(inconsistencies) == 0
        self.checks.append({
            "name": "Consistência entre Campos",
            "passed": passed,
            "details": f"{len(inconsistencies)} inconsistências" if not passed else "Nenhuma inconsistência"
        })

    def _check_reasoning_quality(self, rows: List[Dict[str, Any]]):
        """Verifica qualidade do raciocínio (justificativas)"""
        short_justifications = 0
        very_short = 0
        no_reasoning = 0

        for row in rows:
            justificativa = row.get("justificativa", "").strip()

            if not justificativa:
                no_reasoning += 1
            elif len(justificativa) < 20:
                very_short += 1
            elif len(justificativa) < 50:
                short_justifications += 1

        total_problematic = no_reasoning + very_short + short_justifications

        if no_reasoning > 0:
            self.errors.append(f"{no_reasoning} linhas sem justificativa")
            self.score -= 15

        if very_short > 0:
            pct = (very_short / len(rows)) * 100
            if pct > 10:
                self.errors.append(f"{very_short} justificativas muito curtas (< 20 chars, {pct:.1f}%)")
                self.score -= 5
            else:
                self.warnings.append(f"{very_short} justificativas muito curtas")

        if short_justifications > len(rows) * 0.3:  # > 30%
            self.warnings.append(f"{short_justifications} justificativas curtas (< 50 chars)")

        passed = total_problematic == 0
        self.checks.append({
            "name": "Qualidade do Raciocínio",
            "passed": passed,
            "details": f"{total_problematic} justificativas problemáticas" if not passed else "Raciocínio adequado"
        })

    def _check_evidence_quality(self, rows: List[Dict[str, Any]]):
        """Verifica qualidade das evidências"""
        no_evidence = 0
        malformed_citations = 0
        good_citations = 0

        for row in rows:
            evidencias = row.get("evidencias", "").strip()
            veredicto = row.get("veredicto", "").upper()

            # Pular REQUER ANÁLISE (pode não ter evidência clara)
            if "REQUER" in veredicto:
                continue

            if not evidencias:
                no_evidence += 1
                continue

            # Verificar se tem citação formato "arquivo:linha"
            if ":" in evidencias and any(char.isdigit() for char in evidencias):
                good_citations += 1
            else:
                malformed_citations += 1

        if no_evidence > 0:
            pct = (no_evidence / len(rows)) * 100
            if pct > 10:
                self.errors.append(f"{no_evidence} linhas sem evidências ({pct:.1f}%)")
                self.score -= 10
            else:
                self.warnings.append(f"{no_evidence} linhas sem evidências")
                self.score -= 2

        if malformed_citations > 0:
            pct = (malformed_citations / len(rows)) * 100
            if pct > 20:
                self.warnings.append(f"{malformed_citations} evidências sem citação adequada (arquivo:linha) ({pct:.1f}%)")
                self.score -= 3

        passed = no_evidence == 0 and malformed_citations < len(rows) * 0.2
        self.checks.append({
            "name": "Qualidade das Evidências",
            "passed": passed,
            "details": f"{good_citations} citações adequadas, {malformed_citations} malformadas, {no_evidence} ausentes"
        })

    def _check_confidence_levels(self, rows: List[Dict[str, Any]]):
        """Verifica distribuição e adequação dos níveis de confiança"""
        confidence_counts = {"alto": 0, "médio": 0, "medio": 0, "baixo": 0, "": 0}

        for row in rows:
            confianca = row.get("nivel_confianca", "").lower().strip()
            if confianca in confidence_counts:
                confidence_counts[confianca] += 1
            else:
                confidence_counts[""] += 1

        # Unificar médio
        confidence_counts["médio"] += confidence_counts.get("medio", 0)
        del confidence_counts["medio"]

        total_with_confidence = len(rows) - confidence_counts[""]

        if confidence_counts[""] > 0:
            self.errors.append(f"{confidence_counts['']} linhas sem nível de confiança")
            self.score -= 10

        # Verificar distribuição (muito baixo é suspeito)
        if total_with_confidence > 0:
            baixo_pct = (confidence_counts["baixo"] / total_with_confidence) * 100
            if baixo_pct > 50:
                self.warnings.append(f"{baixo_pct:.1f}% com confiança Baixa (sistema pouco confiante?)")
                self.score -= 5

            alto_pct = (confidence_counts["alto"] / total_with_confidence) * 100
            if alto_pct < 30:
                self.warnings.append(f"Apenas {alto_pct:.1f}% com confiança Alta")

        passed = confidence_counts[""] == 0
        self.checks.append({
            "name": "Níveis de Confiança",
            "passed": passed,
            "details": f"Alto: {confidence_counts['alto']}, Médio: {confidence_counts['médio']}, Baixo: {confidence_counts['baixo']}"
        })

    def _check_verdict_distribution(self, rows: List[Dict[str, Any]]):
        """Verifica distribuição de veredictos (detectar padrões suspeitos)"""
        verdict_counts = {
            "conforme": 0,
            "nao_conforme": 0,
            "parcial": 0,
            "requer_analise": 0,
            "unknown": 0
        }

        for row in rows:
            veredicto = row.get("veredicto", "").upper()

            if "CONFORME" in veredicto and "NÃO" not in veredicto and "PARCIAL" not in veredicto:
                verdict_counts["conforme"] += 1
            elif "NÃO CONFORME" in veredicto:
                verdict_counts["nao_conforme"] += 1
            elif "PARCIAL" in veredicto:
                verdict_counts["parcial"] += 1
            elif "REQUER" in veredicto:
                verdict_counts["requer_analise"] += 1
            else:
                verdict_counts["unknown"] += 1

        if verdict_counts["unknown"] > 0:
            self.errors.append(f"{verdict_counts['unknown']} veredictos não reconhecidos")
            self.score -= 5

        # Padrões suspeitos
        conforme_pct = (verdict_counts["conforme"] / len(rows)) * 100
        if conforme_pct == 100:
            self.warnings.append("100% CONFORME - revisar se não há viés otimista")
        elif conforme_pct == 0:
            self.warnings.append("0% CONFORME - edital pode ser inadequado ou análise muito rigorosa")

        requer_pct = (verdict_counts["requer_analise"] / len(rows)) * 100
        if requer_pct > 30:
            self.warnings.append(f"{requer_pct:.1f}% REQUER ANÁLISE - sistema com muita incerteza")

        passed = verdict_counts["unknown"] == 0
        self.checks.append({
            "name": "Distribuição de Veredictos",
            "passed": passed,
            "details": f"Conforme: {conforme_pct:.1f}%, NC: {(verdict_counts['nao_conforme']/len(rows)*100):.1f}%, "
                      f"Parcial: {(verdict_counts['parcial']/len(rows)*100):.1f}%, "
                      f"Requer: {requer_pct:.1f}%"
        })


def print_quality_report(report: Dict[str, Any]):
    """Imprime relatório de qualidade formatado"""
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO DE QUALIDADE")
    print("=" * 80)

    if report["status"] == "error":
        print(f"\n❌ ERRO: {report['message']}\n")
        return

    # Score
    score = report["score"]
    if score >= 90:
        score_emoji = "🟢"
        score_text = "EXCELENTE"
    elif score >= 75:
        score_emoji = "🟡"
        score_text = "BOM"
    elif score >= 60:
        score_emoji = "🟠"
        score_text = "ACEITÁVEL"
    else:
        score_emoji = "🔴"
        score_text = "PRECISA MELHORIAS"

    print(f"\n{score_emoji} Score de Qualidade: {score:.1f}/100 - {score_text}")
    print(f"📄 Total de linhas analisadas: {report['total_rows']}")
    print(f"✅ Verificações aprovadas: {report['checks_passed']}")
    print(f"❌ Verificações falhadas: {report['checks_failed']}")

    # Checks
    print(f"\n📋 Verificações:")
    for check in report["checks"]:
        status = "✅" if check["passed"] else "❌"
        print(f"  {status} {check['name']}")
        print(f"      {check['details']}")

    # Errors
    if report["errors"]:
        print(f"\n🔴 Erros ({len(report['errors'])}):")
        for error in report["errors"]:
            print(f"  - {error}")

    # Warnings
    if report["warnings"]:
        print(f"\n⚠️  Avisos ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"  - {warning}")

    # Recomendações
    print(f"\n💡 Recomendações:")
    if score >= 90:
        print("  ✅ Qualidade excelente! Nenhuma ação necessária.")
    elif score >= 75:
        print("  ✅ Qualidade boa. Revisar avisos se houver.")
    elif score >= 60:
        print("  ⚠️  Qualidade aceitável, mas pode melhorar.")
        print("  💡 Revisar erros e avisos antes de tomar decisões críticas.")
    else:
        print("  🔴 Qualidade precisa de melhorias significativas.")
        print("  ⚠️  NÃO USE para decisões críticas sem revisão manual completa!")
        print("  💡 Reprocesse a análise com configurações ajustadas.")

    print("\n" + "=" * 80 + "\n")


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Erro: Arquivo CSV não fornecido\n")
        print("Uso: python scripts/quality_check.py <analysis_csv>\n")
        print("Exemplo: python scripts/quality_check.py data/deliveries/.../analysis_conformidade.csv\n")
        sys.exit(1)

    csv_path = sys.argv[1]

    if not Path(csv_path).exists():
        print(f"\n❌ Erro: Arquivo não encontrado: {csv_path}\n")
        sys.exit(1)

    print(f"\n🔍 Analisando qualidade de: {csv_path}")

    checker = QualityChecker()
    report = checker.check_analysis_csv(csv_path)

    print_quality_report(report)

    # Exit code baseado em score
    if report["status"] == "error" or report["score"] < 60:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
