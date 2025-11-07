#!/usr/bin/env python3
"""
Validation Report Generator

Generates comprehensive validation reports with:
- Severity-based grouping
- Remediation suggestions
- Compliance checklist export
- Multiple output formats (YAML, JSON, Markdown, HTML)

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.1.0
História: 2.10 - Additional Validation Rules
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import validation engine classes
try:
    from .validation_engine import ValidationReport, ValidationResult
except ImportError:
    from validation_engine import ValidationReport, ValidationResult


class ValidationReportGenerator:
    """
    Generates formatted validation reports with multiple output options.
    """

    def __init__(self):
        """Initialize report generator"""
        self.severity_symbols = {
            "CRITICAL": "🔴",
            "WARNING": "🟡",
            "INFO": "🔵"
        }

        self.severity_colors = {
            "CRITICAL": "red",
            "WARNING": "yellow",
            "INFO": "blue"
        }

    def group_by_severity(self, report: ValidationReport) -> Dict[str, List[ValidationResult]]:
        """
        Group validation results by severity level.

        Args:
            report: ValidationReport to group

        Returns:
            Dictionary mapping severity to list of results
        """
        grouped = {
            "CRITICAL": [],
            "WARNING": [],
            "INFO": []
        }

        for result in report.results:
            severity = result.severity
            if severity in grouped:
                grouped[severity].append(result)

        return grouped

    def group_by_category(self, report: ValidationReport) -> Dict[str, List[ValidationResult]]:
        """
        Group validation results by category.

        Args:
            report: ValidationReport to group

        Returns:
            Dictionary mapping category to list of results
        """
        grouped = {}

        for result in report.results:
            category = result.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(result)

        return grouped

    def generate_summary(self, report: ValidationReport) -> str:
        """
        Generate text summary of validation report.

        Args:
            report: ValidationReport to summarize

        Returns:
            Formatted text summary
        """
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION SUMMARY")
        lines.append("=" * 70)
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Total Rules Checked: {report.total_rules_checked}")
        lines.append(f"✅ Passed: {report.rules_passed}")
        lines.append(f"🔴 Failed (CRITICAL): {report.rules_failed}")
        lines.append(f"🟡 Warned (WARNING): {report.rules_warned}")
        lines.append(f"\nOverall Status: {report.overall_status}")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_detailed_text(self, report: ValidationReport, group_by: str = "severity") -> str:
        """
        Generate detailed text report.

        Args:
            report: ValidationReport to format
            group_by: 'severity' or 'category'

        Returns:
            Formatted detailed report
        """
        lines = []

        # Summary
        lines.append(self.generate_summary(report))
        lines.append("")

        # Group results
        if group_by == "severity":
            grouped = self.group_by_severity(report)
            order = ["CRITICAL", "WARNING", "INFO"]
        else:  # category
            grouped = self.group_by_category(report)
            order = sorted(grouped.keys())

        # Print each group
        for group_name in order:
            if group_name not in grouped or not grouped[group_name]:
                continue

            results = grouped[group_name]
            symbol = self.severity_symbols.get(group_name, "•")

            lines.append("-" * 70)
            lines.append(f"{symbol} {group_name.upper()} ({len(results)} rules)")
            lines.append("-" * 70)

            for result in results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                lines.append(f"\n{status} | {result.rule_id}: {result.rule_name}")
                lines.append(f"Category: {result.category}")
                lines.append(f"Message: {result.message}")

                if result.details:
                    lines.append(f"Details: {json.dumps(result.details, indent=2, ensure_ascii=False)}")

                if result.remediation:
                    lines.append(f"📋 Remediation: {result.remediation}")

            lines.append("")

        return "\n".join(lines)

    def generate_compliance_checklist(self, report: ValidationReport) -> str:
        """
        Generate compliance checklist in Markdown format.

        Args:
            report: ValidationReport to convert

        Returns:
            Markdown checklist
        """
        lines = []
        lines.append("# Compliance Checklist")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Overall Status:** {report.overall_status}")
        lines.append("")

        # Group by category
        grouped = self.group_by_category(report)

        for category, results in sorted(grouped.items()):
            lines.append(f"## {category}")
            lines.append("")

            for result in results:
                checkbox = "[x]" if result.passed else "[ ]"
                severity_symbol = self.severity_symbols.get(result.severity, "•")
                lines.append(f"- {checkbox} {severity_symbol} **{result.rule_id}**: {result.rule_name}")
                lines.append(f"  - {result.message}")

                if not result.passed and result.remediation:
                    lines.append(f"  - **Action Required:** {result.remediation}")

                lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append(f"- Total Checks: {report.total_rules_checked}")
        lines.append(f"- Passed: {report.rules_passed}")
        lines.append(f"- Failed (Critical): {report.rules_failed}")
        lines.append(f"- Warnings: {report.rules_warned}")

        return "\n".join(lines)

    def generate_yaml_report(self, report: ValidationReport) -> str:
        """
        Generate YAML format report.

        Args:
            report: ValidationReport to export

        Returns:
            YAML string
        """
        return yaml.dump(report.to_dict(), allow_unicode=True, sort_keys=False, default_flow_style=False)

    def generate_json_report(self, report: ValidationReport, pretty: bool = True) -> str:
        """
        Generate JSON format report.

        Args:
            report: ValidationReport to export
            pretty: Whether to pretty-print JSON

        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        return json.dumps(report.to_dict(), ensure_ascii=False)

    def generate_html_report(self, report: ValidationReport) -> str:
        """
        Generate HTML format report.

        Args:
            report: ValidationReport to export

        Returns:
            HTML string
        """
        html_parts = []

        # HTML header
        html_parts.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .summary {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status-pass { color: #27ae60; font-weight: bold; }
        .status-fail { color: #e74c3c; font-weight: bold; }
        .status-warning { color: #f39c12; font-weight: bold; }
        .category-group {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .result-item {
            border-left: 4px solid #bdc3c7;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        }
        .result-item.critical { border-left-color: #e74c3c; }
        .result-item.warning { border-left-color: #f39c12; }
        .result-item.info { border-left-color: #3498db; }
        .result-item.pass { border-left-color: #27ae60; }
        .remediation {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
        }
        .details {
            background-color: #ecf0f1;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #34495e;
            color: white;
        }
    </style>
</head>
<body>
""")

        # Header
        html_parts.append(f"""
    <div class="header">
        <h1>📋 Validation Report</h1>
        <p><strong>Timestamp:</strong> {report.timestamp}</p>
        <p><strong>Overall Status:</strong> <span class="status-{report.overall_status.lower()}">{report.overall_status}</span></p>
    </div>
""")

        # Summary
        html_parts.append(f"""
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Rules Checked</td>
                <td>{report.total_rules_checked}</td>
            </tr>
            <tr>
                <td>✅ Passed</td>
                <td class="status-pass">{report.rules_passed}</td>
            </tr>
            <tr>
                <td>❌ Failed (CRITICAL)</td>
                <td class="status-fail">{report.rules_failed}</td>
            </tr>
            <tr>
                <td>⚠️ Warnings</td>
                <td class="status-warning">{report.rules_warned}</td>
            </tr>
        </table>
    </div>
""")

        # Group by category
        grouped = self.group_by_category(report)

        for category, results in sorted(grouped.items()):
            html_parts.append(f"""
    <div class="category-group">
        <h2>{category}</h2>
""")

            for result in results:
                status_class = "pass" if result.passed else result.severity.lower()
                status_text = "✅ PASS" if result.passed else "❌ FAIL"

                html_parts.append(f"""
        <div class="result-item {status_class}">
            <h3>{result.rule_id}: {result.rule_name}</h3>
            <p><strong>Status:</strong> {status_text}</p>
            <p><strong>Severity:</strong> {self.severity_symbols.get(result.severity, '•')} {result.severity}</p>
            <p><strong>Message:</strong> {result.message}</p>
""")

                if result.details:
                    html_parts.append(f"""
            <div class="details">
                <strong>Details:</strong><br>
                <pre>{json.dumps(result.details, indent=2, ensure_ascii=False)}</pre>
            </div>
""")

                if result.remediation:
                    html_parts.append(f"""
            <div class="remediation">
                <strong>📋 Remediation:</strong> {result.remediation}
            </div>
""")

                html_parts.append("        </div>")

            html_parts.append("    </div>")

        # HTML footer
        html_parts.append("""
</body>
</html>
""")

        return "\n".join(html_parts)

    def save_report(
        self,
        report: ValidationReport,
        output_path: str,
        format: str = "yaml",
        **kwargs
    ):
        """
        Save validation report to file.

        Args:
            report: ValidationReport to save
            output_path: Path to save file
            format: Output format ('yaml', 'json', 'text', 'markdown', 'html')
            **kwargs: Additional format-specific options
        """
        output_file = Path(output_path)

        if format == "yaml":
            content = self.generate_yaml_report(report)
        elif format == "json":
            content = self.generate_json_report(report, kwargs.get('pretty', True))
        elif format == "text":
            group_by = kwargs.get('group_by', 'severity')
            content = self.generate_detailed_text(report, group_by)
        elif format == "markdown":
            content = self.generate_compliance_checklist(report)
        elif format == "html":
            content = self.generate_html_report(report)
        else:
            raise ValueError(f"Unknown format: {format}")

        output_file.write_text(content, encoding='utf-8')
        return output_file


# Convenience functions

def generate_report(
    report: ValidationReport,
    format: str = "text",
    group_by: str = "severity"
) -> str:
    """
    Generate validation report in specified format.

    Args:
        report: ValidationReport to format
        format: Output format ('text', 'yaml', 'json', 'markdown', 'html')
        group_by: Grouping method ('severity' or 'category') for text format

    Returns:
        Formatted report string
    """
    generator = ValidationReportGenerator()

    if format == "text":
        return generator.generate_detailed_text(report, group_by)
    elif format == "yaml":
        return generator.generate_yaml_report(report)
    elif format == "json":
        return generator.generate_json_report(report)
    elif format == "markdown":
        return generator.generate_compliance_checklist(report)
    elif format == "html":
        return generator.generate_html_report(report)
    else:
        raise ValueError(f"Unknown format: {format}")


def save_report(
    report: ValidationReport,
    output_path: str,
    format: str = "yaml"
):
    """
    Save validation report to file.

    Args:
        report: ValidationReport to save
        output_path: Path to save file
        format: Output format
    """
    generator = ValidationReportGenerator()
    return generator.save_report(report, output_path, format)


if __name__ == "__main__":
    # Demo with sample data
    from validation_engine import ValidationEngine

    print("=" * 70)
    print("Validation Report Generator - Demo")
    print("=" * 70)

    # Sample edital text
    sample_text = """
    EDITAL Nº 001/2025 - PREGÃO ELETRÔNICO

    1. OBJETO DA LICITAÇÃO
    Aquisição de Sistema de Videomonitoramento Urbano

    2. VALOR ESTIMADO
    R$ 2.500.000,00

    3. PRAZO DE ENTREGA
    180 dias corridos

    4. SANÇÕES E PENALIDADES
    Multa de até 20% do valor do contrato

    Lei 8.666/93
    Modalidade: Pregão Eletrônico
    Prazo de propostas: 10 dias úteis
    Contato: (11) 1234-5678 | licitacao@exemplo.gov.br
    """

    # Run validation
    engine = ValidationEngine()
    report = engine.validate_all(sample_text)

    # Generate reports in different formats
    generator = ValidationReportGenerator()

    print("\n" + "=" * 70)
    print("TEXT FORMAT (grouped by severity)")
    print("=" * 70)
    print(generator.generate_detailed_text(report, group_by="severity"))

    print("\n" + "=" * 70)
    print("COMPLIANCE CHECKLIST (Markdown)")
    print("=" * 70)
    print(generator.generate_compliance_checklist(report))

    # Save to files
    output_dir = Path("/tmp/validation_reports")
    output_dir.mkdir(exist_ok=True)

    generator.save_report(report, output_dir / "report.yaml", format="yaml")
    generator.save_report(report, output_dir / "report.json", format="json")
    generator.save_report(report, output_dir / "report.txt", format="text")
    generator.save_report(report, output_dir / "checklist.md", format="markdown")
    generator.save_report(report, output_dir / "report.html", format="html")

    print(f"\n✅ Reports saved to {output_dir}")
    print("   - report.yaml")
    print("   - report.json")
    print("   - report.txt")
    print("   - checklist.md")
    print("   - report.html")

    print("\n" + "=" * 70)
