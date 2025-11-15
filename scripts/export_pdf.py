#!/usr/bin/env python3
"""
Export to PDF - Gerador de Relatórios PDF Profissionais

Gera relatório PDF formatado a partir do CSV de análise.
"""

import sys
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, PageBreak, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFReportGenerator:
    """Gerador de relatórios PDF"""

    def __init__(self, csv_path: str, output_path: str):
        self.csv_path = Path(csv_path)
        self.output_path = Path(output_path)
        self.data = []
        self.summary_stats = {}

    def load_csv(self):
        """Carrega dados do CSV"""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)

        # Calcular estatísticas
        self.calculate_summary()

    def calculate_summary(self):
        """Calcula estatísticas do relatório"""
        if not self.data:
            return

        total = len(self.data)
        conforme = sum(1 for row in self.data if row.get('veredicto', '').upper() == 'CONFORME')
        nao_conforme = sum(1 for row in self.data if row.get('veredicto', '').upper() == 'NAO_CONFORME')
        revisao = sum(1 for row in self.data if row.get('veredicto', '').upper() == 'REVISAO')

        self.summary_stats = {
            'total': total,
            'conforme': conforme,
            'nao_conforme': nao_conforme,
            'revisao': revisao,
            'conforme_pct': (conforme / total * 100) if total > 0 else 0,
            'nao_conforme_pct': (nao_conforme / total * 100) if total > 0 else 0,
            'revisao_pct': (revisao / total * 100) if total > 0 else 0,
        }

    def create_cover_page(self, elements: List, styles: Dict):
        """Cria página de capa"""
        # Título principal
        title = Paragraph(
            "<b>RELATÓRIO DE ANÁLISE DE EDITAL</b>",
            styles['title_style']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))

        # Informações do edital
        edital_name = self.csv_path.parent.name
        info_text = f"""
        <b>Edital:</b> {edital_name}<br/>
        <b>Data de Análise:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
        <b>Sistema:</b> BidAnalyzee v2.0<br/>
        """
        info = Paragraph(info_text, styles['normal'])
        elements.append(info)
        elements.append(Spacer(1, 1*inch))

        # Resumo executivo
        summary_title = Paragraph("<b>RESUMO EXECUTIVO</b>", styles['heading'])
        elements.append(summary_title)
        elements.append(Spacer(1, 0.3*inch))

        # Tabela de estatísticas
        summary_data = [
            ['Métrica', 'Quantidade', 'Percentual'],
            ['Total de Requisitos', str(self.summary_stats['total']), '100%'],
            ['✅ Conforme', str(self.summary_stats['conforme']),
             f"{self.summary_stats['conforme_pct']:.1f}%"],
            ['❌ Não Conforme', str(self.summary_stats['nao_conforme']),
             f"{self.summary_stats['nao_conforme_pct']:.1f}%"],
            ['⚠️  Requer Revisão', str(self.summary_stats['revisao']),
             f"{self.summary_stats['revisao_pct']:.1f}%"],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(summary_table)
        elements.append(PageBreak())

    def create_details_section(self, elements: List, styles: Dict):
        """Cria seção de detalhes"""
        details_title = Paragraph("<b>ANÁLISE DETALHADA</b>", styles['heading'])
        elements.append(details_title)
        elements.append(Spacer(1, 0.3*inch))

        # Agrupar por veredicto
        for veredicto in ['NAO_CONFORME', 'REVISAO', 'CONFORME']:
            items = [row for row in self.data if row.get('veredicto', '').upper() == veredicto]

            if not items:
                continue

            # Título da seção
            veredicto_names = {
                'CONFORME': '✅ REQUISITOS CONFORMES',
                'NAO_CONFORME': '❌ REQUISITOS NÃO CONFORMES',
                'REVISAO': '⚠️  REQUISITOS QUE REQUEREM REVISÃO'
            }

            section_title = Paragraph(
                f"<b>{veredicto_names.get(veredicto, veredicto)}</b>",
                styles['subheading']
            )
            elements.append(section_title)
            elements.append(Spacer(1, 0.2*inch))

            # Tabela de requisitos
            table_data = [['ID', 'Descrição', 'Confiança', 'Justificativa']]

            for item in items:
                req_id = item.get('id', 'N/A')
                descricao = item.get('descricao', 'N/A')[:100] + '...' if len(item.get('descricao', '')) > 100 else item.get('descricao', 'N/A')
                confianca = item.get('confianca', 'N/A')
                justificativa = item.get('justificativa', 'N/A')[:150] + '...' if len(item.get('justificativa', '')) > 150 else item.get('justificativa', 'N/A')

                table_data.append([
                    req_id,
                    Paragraph(descricao, styles['small']),
                    confianca,
                    Paragraph(justificativa, styles['small'])
                ])

            req_table = Table(
                table_data,
                colWidths=[0.5*inch, 2.5*inch, 0.8*inch, 2.7*inch]
            )

            # Cores por veredicto
            bg_colors = {
                'CONFORME': colors.lightgreen,
                'NAO_CONFORME': colors.lightcoral,
                'REVISAO': colors.lightyellow
            }

            req_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), bg_colors.get(veredicto, colors.white)),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            elements.append(req_table)
            elements.append(Spacer(1, 0.5*inch))

            # Page break para seções longas
            if len(items) > 10:
                elements.append(PageBreak())

    def generate(self) -> bool:
        """Gera o PDF"""
        if not REPORTLAB_AVAILABLE:
            print("❌ ReportLab não está instalado")
            print("   Instale com: pip install reportlab")
            return False

        try:
            # Carregar dados
            self.load_csv()

            # Criar documento
            doc = SimpleDocTemplate(
                str(self.output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Estilos
            styles_obj = getSampleStyleSheet()
            styles = {
                'title_style': ParagraphStyle(
                    'CustomTitle',
                    parent=styles_obj['Title'],
                    fontSize=24,
                    textColor=colors.HexColor('#1f4788'),
                    spaceAfter=30,
                    alignment=TA_CENTER,
                ),
                'heading': ParagraphStyle(
                    'CustomHeading',
                    parent=styles_obj['Heading1'],
                    fontSize=16,
                    textColor=colors.HexColor('#1f4788'),
                    spaceAfter=12,
                    spaceBefore=12,
                ),
                'subheading': ParagraphStyle(
                    'CustomSubHeading',
                    parent=styles_obj['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#2c5aa0'),
                    spaceAfter=10,
                ),
                'normal': styles_obj['Normal'],
                'small': ParagraphStyle(
                    'Small',
                    parent=styles_obj['Normal'],
                    fontSize=8,
                ),
            }

            # Elementos do documento
            elements = []

            # Página de capa
            self.create_cover_page(elements, styles)

            # Detalhes
            self.create_details_section(elements, styles)

            # Construir PDF
            doc.build(elements)

            return True

        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Uso incorreto\n")
        print("Uso: python3 scripts/export_pdf.py <csv_path> [output_path]")
        print("\nExemplo:")
        print("   python3 scripts/export_pdf.py data/.../analysis_results.csv")
        print("   python3 scripts/export_pdf.py data/.../analysis_results.csv report.pdf")
        print()
        sys.exit(1)

    csv_path = sys.argv[1]

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Gerar nome automático
        csv_p = Path(csv_path)
        output_path = csv_p.parent / f"{csv_p.stem}_report.pdf"

    print(f"\n📄 Gerando relatório PDF...")
    print(f"   CSV: {csv_path}")
    print(f"   Output: {output_path}")

    generator = PDFReportGenerator(csv_path, output_path)
    success = generator.generate()

    if success:
        print(f"\n✅ Relatório PDF gerado com sucesso!")
        print(f"   📁 {output_path}")
    else:
        print(f"\n❌ Falha ao gerar relatório PDF")
        sys.exit(1)


if __name__ == "__main__":
    main()
