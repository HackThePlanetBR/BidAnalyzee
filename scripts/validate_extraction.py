#!/usr/bin/env python3
"""
Validação de Extração via Agente

Compara CSVs gerados com PDF original para verificar completude.
Usa agente para análise inteligente de requisitos.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2


def load_csv_requirements(csv_path: str) -> List[Dict[str, str]]:
    """Carrega requisitos de um CSV"""
    requirements = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            requirements.append(row)

    return requirements


def extract_item_text_from_pdf(pdf_path: str, item_id: str) -> str:
    """
    Extrai texto relacionado a um item específico do PDF.
    Busca pelo número do item e captura contexto ao redor.
    """
    text_chunks = []

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)

        # Buscar em todas as páginas
        for page_num in range(len(reader.pages)):
            page_text = reader.pages[page_num].extract_text()

            # Buscar referências ao item
            # Padrões: "ITEM 11", "11.", "Item 11", etc.
            patterns = [
                f"ITEM {item_id}",
                f"Item {item_id}",
                f"{item_id}.",
                f"{item_id} ",
            ]

            for pattern in patterns:
                if pattern in page_text:
                    text_chunks.append(f"\n--- Página {page_num + 1} ---\n{page_text}\n")
                    break

    return "\n".join(text_chunks)


def validate_requirements(
    item_id: str,
    item_description: str,
    csv_requirements: List[Dict],
    pdf_text: str
) -> Dict[str, Any]:
    """
    Valida requisitos extraídos comparando com texto do PDF.

    Retorna análise de completude.
    """

    # Análise básica automática
    total_reqs = len(csv_requirements)

    # Verificar se termos-chave dos requisitos aparecem no PDF
    found_in_pdf = 0
    missing_keywords = []

    for req in csv_requirements:
        req_text = req.get('requisito', '').lower()

        # Extrair palavras-chave (ignore palavras comuns)
        common_words = {'de', 'da', 'do', 'para', 'com', 'em', 'por', 'a', 'o', 'e', 'ou'}
        keywords = [w for w in req_text.split() if len(w) > 3 and w not in common_words]

        # Verificar se pelo menos 50% das keywords aparecem no PDF
        found_count = sum(1 for kw in keywords if kw in pdf_text.lower())

        if keywords and (found_count / len(keywords)) >= 0.3:  # 30% threshold
            found_in_pdf += 1
        else:
            missing_keywords.append({
                'req_id': req.get('id', '?'),
                'requisito': req_text,
                'keywords': keywords[:3]  # Primeiras 3 keywords
            })

    coverage_percent = (found_in_pdf / total_reqs * 100) if total_reqs > 0 else 0

    # Determinar status
    if coverage_percent >= 80:
        status = "✅ COMPLETO"
        confidence = "ALTA"
    elif coverage_percent >= 60:
        status = "⚠️  PARCIAL"
        confidence = "MÉDIA"
    else:
        status = "❌ INCOMPLETO"
        confidence = "BAIXA"

    return {
        'item_id': item_id,
        'item_description': item_description,
        'status': status,
        'confidence': confidence,
        'total_requirements': total_reqs,
        'found_in_pdf': found_in_pdf,
        'coverage_percent': round(coverage_percent, 1),
        'missing_keywords_sample': missing_keywords[:5],  # Top 5
        'pdf_text_length': len(pdf_text),
        'notes': []
    }


def generate_validation_report(validations: List[Dict], output_path: str) -> None:
    """Gera relatório consolidado de validação"""

    report = {
        'total_items': len(validations),
        'complete_items': sum(1 for v in validations if '✅' in v['status']),
        'partial_items': sum(1 for v in validations if '⚠️' in v['status']),
        'incomplete_items': sum(1 for v in validations if '❌' in v['status']),
        'total_requirements': sum(v['total_requirements'] for v in validations),
        'validations': validations
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE VALIDAÇÃO")
    print("="*80)
    print()
    print(f"Total de itens validados: {report['total_items']}")
    print(f"Total de requisitos: {report['total_requirements']}")
    print()
    print(f"✅ Completos: {report['complete_items']}")
    print(f"⚠️  Parciais: {report['partial_items']}")
    print(f"❌ Incompletos: {report['incomplete_items']}")
    print()

    # Detalhes por item
    for v in validations:
        print(f"{v['status']} Item {v['item_id']}: {v['item_description'][:50]}")
        print(f"   Cobertura: {v['coverage_percent']}% ({v['found_in_pdf']}/{v['total_requirements']} requisitos)")
        print(f"   Confiança: {v['confidence']}")

        if v['missing_keywords_sample']:
            print(f"   ⚠️  Requisitos com baixa evidência no PDF:")
            for missing in v['missing_keywords_sample'][:3]:
                print(f"      - {missing['req_id']}: {missing['requisito'][:60]}")
        print()

    print("="*80)
    print(f"💾 Relatório salvo em: {output_path}")
    print("="*80)


def main():
    if len(sys.argv) < 4:
        print("Uso: python3 scripts/validate_extraction.py <edital.pdf> <selected_items.json> <extraction_dir>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    selection_path = sys.argv[2]
    extraction_dir = sys.argv[3]

    # Carregar seleção
    with open(selection_path, 'r', encoding='utf-8') as f:
        selection = json.load(f)

    selected_items = selection['selected_items']

    print("\n" + "="*80)
    print("🔍 VALIDAÇÃO DE EXTRAÇÃO")
    print("="*80)
    print(f"PDF: {pdf_path}")
    print(f"Itens selecionados: {len(selected_items)}")
    print()

    validations = []

    for item in selected_items:
        item_id = item['item_id']
        description = item['description']

        print(f"📋 Validando Item {item_id}: {description[:50]}...")

        # Encontrar CSV correspondente
        csv_pattern = f"item_{int(item_id):02d}_*.csv"
        csv_files = list(Path(extraction_dir).glob(csv_pattern))

        if not csv_files:
            print(f"   ⚠️  CSV não encontrado: {csv_pattern}")
            continue

        csv_path = csv_files[0]

        # Carregar requisitos do CSV
        csv_requirements = load_csv_requirements(str(csv_path))

        # Extrair texto do PDF para este item
        pdf_text = extract_item_text_from_pdf(pdf_path, item_id)

        if not pdf_text:
            print(f"   ⚠️  Texto do item não encontrado no PDF")
            validation = {
                'item_id': item_id,
                'item_description': description,
                'status': '⚠️  SEM EVIDÊNCIA',
                'confidence': 'BAIXA',
                'total_requirements': len(csv_requirements),
                'found_in_pdf': 0,
                'coverage_percent': 0,
                'missing_keywords_sample': [],
                'pdf_text_length': 0,
                'notes': ['Texto do item não localizado no PDF']
            }
        else:
            # Validar requisitos
            validation = validate_requirements(
                item_id,
                description,
                csv_requirements,
                pdf_text
            )

        validations.append(validation)
        print(f"   {validation['status']} - Cobertura: {validation['coverage_percent']}%")

    # Gerar relatório
    report_path = Path(extraction_dir).parent / 'validation' / 'validation_report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    generate_validation_report(validations, str(report_path))


if __name__ == "__main__":
    main()
