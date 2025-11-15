#!/usr/bin/env python3
"""
Análise de Conformidade E2E com Knowledge Base Mock

Executa análise de conformidade usando CSVs reais e knowledge base mock.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


# Mock Knowledge Base - Produtos simulados para teste
MOCK_KNOWLEDGE_BASE = {
    "cameras": [
        {
            "fabricante": "Hikvision",
            "modelo": "DS-2CD2143G0-I",
            "tipo": "Câmera IP Dome",
            "especificacoes": {
                "resolucao": "4MP (2688x1520)",
                "fps": "30fps",
                "sensor": "1/3\" Progressive Scan CMOS",
                "iluminacao": "IR até 30m",
                "lente": "2.8mm fixa",
                "compressao": "H.265+/H.265/H.264+/H.264",
                "poe": "IEEE 802.3af",
                "wdr": "120dB WDR",
                "analytics": "Line crossing, intrusion detection",
                "protecao": "IP67",
                "temperatura": "-30°C a +60°C",
                "garantia": "3 anos"
            },
            "conformidade_geral": 95
        },
        {
            "fabricante": "Intelbras",
            "modelo": "VIP 3430 D",
            "tipo": "Câmera IP Dome",
            "especificacoes": {
                "resolucao": "4MP (2560x1440)",
                "fps": "30fps",
                "sensor": "1/2.7\" Progressive Scan CMOS",
                "iluminacao": "IR até 30m",
                "lente": "2.8mm fixa",
                "compressao": "H.265/H.264",
                "poe": "IEEE 802.3af",
                "wdr": "120dB WDR",
                "analytics": "Detecção de movimento",
                "protecao": "IP66",
                "temperatura": "-10°C a +50°C",
                "garantia": "2 anos"
            },
            "conformidade_geral": 88
        }
    ],
    "software": [
        {
            "fabricante": "Milestone",
            "modelo": "XProtect Corporate",
            "tipo": "VMS (Video Management System)",
            "especificacoes": {
                "licenciamento": "Perpétuo",
                "usuarios": "Ilimitado",
                "interface": "Web + Desktop",
                "idiomas": "Português, Inglês, Espanhol",
                "gravacao": "Contínua e por eventos",
                "busca": "Por data/hora, eventos, analytics",
                "exportacao": "AVI, MP4, MKV",
                "api": "REST API documentada",
                "seguranca": "HTTPS, autenticação multi-fator",
                "suporte": "24x7 em português",
                "garantia": "3 anos de atualizações"
            },
            "conformidade_geral": 92
        },
        {
            "fabricante": "Genetec",
            "modelo": "Security Center",
            "tipo": "VMS + PSIM",
            "especificacoes": {
                "licenciamento": "Perpétuo",
                "usuarios": "Ilimitado",
                "interface": "Web + Desktop (Windows)",
                "idiomas": "Português, Inglês",
                "gravacao": "Contínua, eventos, motion",
                "busca": "Avançada por múltiplos critérios",
                "exportacao": "Múltiplos formatos",
                "api": "SDK + REST API",
                "seguranca": "Criptografia end-to-end",
                "suporte": "Português",
                "garantia": "3 anos"
            },
            "conformidade_geral": 90
        }
    ],
    "sensores": [
        {
            "fabricante": "Bosch",
            "modelo": "ISC-BDL2-W12G",
            "tipo": "Sensor IVA (PIR)",
            "especificacoes": {
                "deteccao": "Movimento PIR",
                "alcance": "12m",
                "angulo": "90 graus",
                "tensao": "12VDC",
                "temperatura": "-10°C a +50°C",
                "protecao": "IP54",
                "garantia": "2 anos"
            },
            "conformidade_geral": 85
        }
    ],
    "acessorios": [
        {
            "fabricante": "Furukawa",
            "modelo": "U/UTP Cat6",
            "tipo": "Cabo de Rede",
            "especificacoes": {
                "categoria": "Cat6",
                "tipo": "U/UTP",
                "velocidade": "1Gbps",
                "certificacao": "ANATEL, ANSI/TIA",
                "uso": "Interno/Externo",
                "temperatura": "-20°C a +60°C",
                "garantia": "25 anos"
            },
            "conformidade_geral": 95
        }
    ]
}


def load_csv_requirements(csv_path: str) -> List[Dict[str, str]]:
    """Carrega requisitos de um CSV"""
    requirements = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            requirements.append(row)

    return requirements


def determine_product_category(item_description: str) -> str:
    """Determina categoria do produto baseado na descrição"""
    desc_upper = item_description.upper()

    if 'CÂMERA' in desc_upper or 'CAMERA' in desc_upper:
        return 'cameras'
    elif 'SOFTWARE' in desc_upper or 'VMS' in desc_upper:
        return 'software'
    elif 'SENSOR' in desc_upper:
        return 'sensores'
    elif 'CABO' in desc_upper or 'U/UTP' in desc_upper or 'UTP' in desc_upper:
        return 'acessorios'
    else:
        return 'outros'


def analyze_conformity_mock(
    item_id: str,
    item_description: str,
    requirements: List[Dict],
    category: str
) -> Dict[str, Any]:
    """
    Analisa conformidade usando knowledge base mock.

    Simula análise de produtos candidatos.
    """

    # Buscar produtos da categoria
    products = MOCK_KNOWLEDGE_BASE.get(category, [])

    if not products:
        return {
            'item_id': item_id,
            'item_description': item_description,
            'category': category,
            'status': '⚠️  SEM PRODUTOS NA KB',
            'total_requirements': len(requirements),
            'mandatory_requirements': len([r for r in requirements if r.get('obrigatorio', '').upper() == 'SIM']),
            'products_analyzed': 0,
            'best_match': None,
            'notes': ['Categoria não possui produtos na knowledge base mock']
        }

    # Analisar cada produto
    product_results = []

    for product in products:
        # Análise simulada de conformidade
        mandatory_reqs = [r for r in requirements if r.get('obrigatorio', '').upper() == 'SIM']
        optional_reqs = [r for r in requirements if r.get('obrigatorio', '').upper() != 'SIM']

        # Simular atendimento baseado na conformidade geral do produto
        conformidade_base = product.get('conformidade_geral', 70)

        # Adicionar aleatoriedade baseada em tipo de requisito
        import random
        random.seed(hash(product['modelo']))  # Seed determinístico

        mandatory_met = int(len(mandatory_reqs) * (conformidade_base / 100))
        optional_met = int(len(optional_reqs) * ((conformidade_base + 10) / 100))

        total_score = 0
        max_score = 0

        # Calcular pontuação
        for req in requirements:
            try:
                pontuacao = float(req.get('pontuacao', '0').replace('N/A', '0'))
            except:
                pontuacao = 0

            max_score += pontuacao

            # Simular atendimento
            is_mandatory = req.get('obrigatorio', '').upper() == 'SIM'

            if is_mandatory:
                meets = random.random() < (conformidade_base / 100)
            else:
                meets = random.random() < ((conformidade_base + 10) / 100)

            if meets:
                total_score += pontuacao

        score_percent = (total_score / max_score * 100) if max_score > 0 else 0

        product_results.append({
            'fabricante': product['fabricante'],
            'modelo': product['modelo'],
            'tipo': product['tipo'],
            'mandatory_met': mandatory_met,
            'mandatory_total': len(mandatory_reqs),
            'optional_met': optional_met,
            'optional_total': len(optional_reqs),
            'score': round(total_score, 1),
            'max_score': round(max_score, 1),
            'score_percent': round(score_percent, 1),
            'conformidade_geral': conformidade_base
        })

    # Ordenar por pontuação
    product_results.sort(key=lambda x: x['score_percent'], reverse=True)

    best_match = product_results[0] if product_results else None

    # Determinar status
    if best_match:
        if best_match['score_percent'] >= 90:
            status = "✅ CONFORME"
        elif best_match['score_percent'] >= 70:
            status = "⚠️  PARCIALMENTE CONFORME"
        else:
            status = "❌ NÃO CONFORME"
    else:
        status = "⚠️  SEM ANÁLISE"

    return {
        'item_id': item_id,
        'item_description': item_description,
        'category': category,
        'status': status,
        'total_requirements': len(requirements),
        'mandatory_requirements': len([r for r in requirements if r.get('obrigatorio', '').upper() == 'SIM']),
        'products_analyzed': len(product_results),
        'best_match': best_match,
        'all_products': product_results,
        'notes': []
    }


def generate_conformity_report(analyses: List[Dict], output_path: str) -> None:
    """Gera relatório de conformidade"""

    report = {
        'total_items': len(analyses),
        'conforme_items': sum(1 for a in analyses if '✅' in a['status']),
        'partial_items': sum(1 for a in analyses if '⚠️' in a['status']),
        'nao_conforme_items': sum(1 for a in analyses if '❌' in a['status']),
        'total_products_analyzed': sum(a['products_analyzed'] for a in analyses),
        'analyses': analyses
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE CONFORMIDADE (MOCK KB)")
    print("="*80)
    print()
    print(f"Total de itens analisados: {report['total_items']}")
    print(f"Total de produtos avaliados: {report['total_products_analyzed']}")
    print()
    print(f"✅ Conformes: {report['conforme_items']}")
    print(f"⚠️  Parcialmente conformes: {report['partial_items']}")
    print(f"❌ Não conformes: {report['nao_conforme_items']}")
    print()

    # Detalhes por item
    for analysis in analyses:
        print(f"{analysis['status']} Item {analysis['item_id']}: {analysis['item_description'][:50]}")
        print(f"   Categoria: {analysis['category']}")
        print(f"   Requisitos: {analysis['total_requirements']} total ({analysis['mandatory_requirements']} obrigatórios)")

        if analysis['best_match']:
            best = analysis['best_match']
            print(f"   🏆 Melhor match: {best['fabricante']} {best['modelo']}")
            print(f"      Pontuação: {best['score_percent']}% ({best['score']}/{best['max_score']} pontos)")
            print(f"      Obrigatórios: {best['mandatory_met']}/{best['mandatory_total']}")
            print(f"      Opcionais: {best['optional_met']}/{best['optional_total']}")

        print()

    print("="*80)
    print(f"💾 Relatório salvo em: {output_path}")
    print("="*80)


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 scripts/analyze_conformity_e2e.py <selected_items.json> <extraction_dir>")
        sys.exit(1)

    selection_path = sys.argv[1]
    extraction_dir = sys.argv[2]

    # Carregar seleção
    with open(selection_path, 'r', encoding='utf-8') as f:
        selection = json.load(f)

    selected_items = selection['selected_items']

    print("\n" + "="*80)
    print("🔍 ANÁLISE DE CONFORMIDADE E2E")
    print("="*80)
    print(f"Itens selecionados: {len(selected_items)}")
    print(f"Knowledge Base: MOCK (para testes)")
    print()

    analyses = []

    for item in selected_items:
        item_id = item['item_id']
        description = item['description']

        print(f"📋 Analisando Item {item_id}: {description[:50]}...")

        # Encontrar CSV correspondente
        csv_pattern = f"item_{int(item_id):02d}_*.csv"
        csv_files = list(Path(extraction_dir).glob(csv_pattern))

        if not csv_files:
            print(f"   ⚠️  CSV não encontrado: {csv_pattern}")
            continue

        csv_path = csv_files[0]

        # Carregar requisitos
        requirements = load_csv_requirements(str(csv_path))

        # Determinar categoria
        category = determine_product_category(description)

        # Analisar conformidade
        analysis = analyze_conformity_mock(
            item_id,
            description,
            requirements,
            category
        )

        analyses.append(analysis)
        print(f"   {analysis['status']} - {analysis['products_analyzed']} produtos analisados")

    # Gerar relatório
    report_path = Path(extraction_dir).parent / 'analysis' / 'conformity_report_mock.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    generate_conformity_report(analyses, str(report_path))


if __name__ == "__main__":
    main()
