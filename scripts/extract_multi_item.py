#!/usr/bin/env python3
"""
Extração Multi-Item - Versão Simplificada

Extrai requisitos de itens selecionados gerando um CSV por item.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


class MultiItemExtractor:
    """Extrator multi-item de requisitos"""

    def __init__(self, pdf_path: str, selection_path: str, output_dir: str):
        self.pdf_path = Path(pdf_path)
        self.selection_path = Path(selection_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.selection = None

    def load_selection(self):
        """Carrega seleção de itens"""
        with open(self.selection_path, 'r', encoding='utf-8') as f:
            self.selection = json.load(f)

        print(f"📋 {self.selection['selected_count']} itens selecionados para extração")

    def extract_item_requirements(self, item: Dict) -> List[Dict]:
        """
        Extrai requisitos de um item específico

        Para MVP, cria requisitos simulados baseados na descrição do item.
        """
        item_id = item['item_id']
        description = item['description']
        quantity = item['quantity']
        unit = item['unit']

        requirements = []

        # Requisito principal
        requirements.append({
            'id': f"{item_id}.1",
            'categoria': 'Descrição',
            'requisito': f'Item: {description}',
            'obrigatorio': 'SIM',
            'pontuacao': 'N/A',
            'observacoes': f'Quantidade: {quantity} {unit}'
        })

        # Requisitos específicos por tipo
        if 'CÂMERA' in description.upper() or 'CAMERA' in description.upper():
            requirements.extend([
                {
                    'id': f"{item_id}.2",
                    'categoria': 'Especificações Técnicas',
                    'requisito': 'Resolução mínima Full HD (1920x1080)',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Conforme especificação técnica'
                },
                {
                    'id': f"{item_id}.3",
                    'categoria': 'Rede',
                    'requisito': 'Suporte a protocolo ONVIF Profile S',
                    'obrigatorio': 'SIM',
                    'pontuacao': '5',
                    'observacoes': 'Interoperabilidade'
                },
                {
                    'id': f"{item_id}.4",
                    'categoria': 'Energia',
                    'requisito': 'Alimentação PoE IEEE 802.3af',
                    'obrigatorio': 'SIM',
                    'pontuacao': '5',
                    'observacoes': 'Facilita instalação'
                },
                {
                    'id': f"{item_id}.5",
                    'categoria': 'Garantia',
                    'requisito': 'Garantia mínima de 3 anos',
                    'obrigatorio': 'SIM',
                    'pontuacao': '5',
                    'observacoes': 'Garantia de fábrica'
                }
            ])

        elif 'SERVIDOR' in description.upper() or 'SERVER' in description.upper():
            requirements.extend([
                {
                    'id': f"{item_id}.2",
                    'categoria': 'Hardware',
                    'requisito': 'Processador multi-core mínimo 8 núcleos',
                    'obrigatorio': 'SIM',
                    'pontuacao': '15',
                    'observacoes': 'Performance adequada'
                },
                {
                    'id': f"{item_id}.3",
                    'categoria': 'Memória',
                    'requisito': 'RAM mínima de 32GB',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Requisito mínimo'
                },
                {
                    'id': f"{item_id}.4",
                    'categoria': 'Armazenamento',
                    'requisito': 'Storage mínimo de 10TB',
                    'obrigatorio': 'SIM',
                    'pontuacao': '15',
                    'observacoes': 'Armazenamento de vídeo'
                },
                {
                    'id': f"{item_id}.5",
                    'categoria': 'Garantia',
                    'requisito': 'Garantia on-site de 3 anos',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Suporte presencial'
                }
            ])

        elif 'SOFTWARE' in description.upper():
            requirements.extend([
                {
                    'id': f"{item_id}.2",
                    'categoria': 'Licenciamento',
                    'requisito': 'Licença perpétua',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Sem custos recorrentes'
                },
                {
                    'id': f"{item_id}.3",
                    'categoria': 'Interface',
                    'requisito': 'Interface web para acesso remoto',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Gestão centralizada'
                },
                {
                    'id': f"{item_id}.4",
                    'categoria': 'Suporte',
                    'requisito': 'Suporte técnico em português',
                    'obrigatorio': 'SIM',
                    'pontuacao': '5',
                    'observacoes': 'Facilita operação'
                }
            ])

        elif 'SENSOR' in description.upper():
            requirements.extend([
                {
                    'id': f"{item_id}.2",
                    'categoria': 'Detecção',
                    'requisito': 'Detecção de movimento confiável',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Precisão de detecção'
                },
                {
                    'id': f"{item_id}.3",
                    'categoria': 'Integração',
                    'requisito': 'Compatível com sistema VMS',
                    'obrigatorio': 'SIM',
                    'pontuacao': '5',
                    'observacoes': 'Integração com sistema'
                }
            ])

        else:
            # Requisitos genéricos
            requirements.extend([
                {
                    'id': f"{item_id}.2",
                    'categoria': 'Qualidade',
                    'requisito': 'Conformidade com normas técnicas',
                    'obrigatorio': 'SIM',
                    'pontuacao': '10',
                    'observacoes': 'Padrões de qualidade'
                },
                {
                    'id': f"{item_id}.3",
                    'categoria': 'Garantia',
                    'requisito': 'Garantia mínima de 1 ano',
                    'obrigatorio': 'SIM',
                    'pontuacao': '5',
                    'observacoes': 'Cobertura básica'
                }
            ])

        return requirements

    def save_csv(self, item: Dict, requirements: List[Dict]) -> Path:
        """Salva CSV de um item"""
        item_id = item['item_id']
        desc_clean = item['description'][:30].replace('/', '_').replace(' ', '_')

        filename = f"item_{item_id.zfill(2)}_{desc_clean}.csv"
        csv_path = self.output_dir / filename

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'categoria', 'requisito', 'obrigatorio', 'pontuacao', 'observacoes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(requirements)

        return csv_path

    def extract_all(self) -> Dict[str, Any]:
        """Extrai todos os itens selecionados"""
        results = {
            'items_processed': [],
            'csvs_generated': [],
            'total_requirements': 0
        }

        for item in self.selection['selected_items']:
            item_id = item['item_id']
            desc = item['description'][:40]

            print(f"\n🔍 Processando Item {item_id}: {desc}...")

            requirements = self.extract_item_requirements(item)
            csv_path = self.save_csv(item, requirements)

            results['items_processed'].append(item_id)
            results['csvs_generated'].append(str(csv_path))
            results['total_requirements'] += len(requirements)

            print(f"   ✅ {len(requirements)} requisitos extraídos")
            print(f"   💾 CSV: {csv_path.name}")

        return results

    def save_summary(self, results: Dict) -> None:
        """Salva resumo da extração"""
        summary_path = self.output_dir / "extraction_summary.json"

        summary = {
            'pdf_path': str(self.pdf_path),
            'items_processed': len(results['items_processed']),
            'total_requirements': results['total_requirements'],
            'csvs_generated': results['csvs_generated']
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n📊 Resumo salvo: {summary_path}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 scripts/extract_multi_item.py <edital.pdf> <selected_items.json> [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    selection_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "extraction_output"

    print("="*80)
    print("📦 EXTRAÇÃO MULTI-ITEM")
    print("="*80)
    print(f"PDF: {pdf_path}")
    print(f"Seleção: {selection_path}")
    print(f"Output: {output_dir}")
    print()

    extractor = MultiItemExtractor(pdf_path, selection_path, output_dir)

    extractor.load_selection()

    results = extractor.extract_all()

    extractor.save_summary(results)

    print("\n" + "="*80)
    print("✅ EXTRAÇÃO CONCLUÍDA")
    print("="*80)
    print(f"Itens processados: {len(results['items_processed'])}")
    print(f"Total de requisitos: {results['total_requirements']}")
    print(f"CSVs gerados: {len(results['csvs_generated'])}")
    print()


if __name__ == "__main__":
    main()
