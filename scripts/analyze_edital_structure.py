#!/usr/bin/env python3
"""
Análise de Estrutura de Edital - Identifica Itens e Seções

Analisa um PDF de edital para identificar automaticamente:
- Itens/equipamentos listados
- Estimativa de requisitos por item
- Páginas onde cada item é especificado
- Estrutura geral do documento

Uso:
    python3 scripts/analyze_edital_structure.py <caminho-do-edital.pdf>

Output:
    JSON com estrutura do edital (salvo no mesmo diretório do PDF)
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

try:
    import PyPDF2
except ImportError:
    print("❌ Erro: PyPDF2 não está instalado")
    print("   Instale com: pip install PyPDF2")
    sys.exit(1)


class EditalStructureAnalyzer:
    """Analisador de estrutura de editais"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.reader = None
        self.total_pages = 0
        self.items_found = []
        self.structure = {}

    def load_pdf(self):
        """Carrega o PDF"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {self.pdf_path}")

        with open(self.pdf_path, 'rb') as f:
            self.reader = PyPDF2.PdfReader(f)
            self.total_pages = len(self.reader.pages)

        print(f"📄 PDF carregado: {self.total_pages} páginas")

    def find_items_table(self) -> List[Dict[str, Any]]:
        """
        Procura pela tabela de itens do edital (geralmente no início)

        Busca padrões como:
        - ITEM | DESCRIÇÃO | UNIDADE | QUANTIDADE
        - Numeração sequencial (1, 2, 3...)
        """
        items = []

        print("\n🔍 Procurando tabela de itens...")

        # Procurar nas primeiras 15 páginas
        for i in range(min(15, self.total_pages)):
            text = self.reader.pages[i].extract_text()

            # Padrão: número + descrição + "Unidade" + quantidade + preço
            # Exemplo: "8CÂMERA DOME  INTERNA DE  BAIXO  CUSTO\n(TIPO 5)Unidade 246 R$ 3.439,53"
            # O número pode vir grudado ou com espaço
            pattern = r'(\d+)\s*([A-ZÇÃÕÁÉÍÓÚ\s\-/()]+?)\s+(Unidade|Serviço|Turma|Par|Pares|Metros)\s+(\d+)\s+R\$'

            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

            if matches:
                print(f"   ✓ Página {i+1}: Encontrados {len(matches)} itens")

                for match in matches:
                    item_num, description, unit, quantity = match

                    # Limpar descrição
                    description = description.strip()
                    description = re.sub(r'\s+', ' ', description)  # Remove espaços extras

                    # Descartar itens com descrição muito curta (provavelmente lixo)
                    if len(description) < 5:
                        continue

                    # Evitar duplicatas
                    if any(item['item_id'] == item_num for item in items):
                        continue

                    items.append({
                        'item_id': item_num,
                        'description': description,
                        'unit': unit,
                        'quantity': int(quantity),
                        'found_on_page': i + 1
                    })

        return items

    def find_specifications_sections(self, items: List[Dict]) -> List[Dict]:
        """
        Para cada item, tenta encontrar a seção de especificações técnicas
        """
        print("\n🔍 Procurando seções de especificações técnicas...")

        enhanced_items = []

        for item in items:
            item_copy = item.copy()
            item_copy['spec_pages'] = []
            item_copy['estimated_requirements'] = 0

            # Extrair palavras-chave da descrição para busca
            keywords = self._extract_keywords(item['description'])

            # Procurar em páginas posteriores (geralmente após página 20)
            for page_num in range(20, min(self.total_pages, 100)):
                text = self.reader.pages[page_num].extract_text()
                text_upper = text.upper()

                # Verificar se página menciona o item
                matches_item = any(kw in text_upper for kw in keywords)

                if matches_item:
                    # Contar possíveis requisitos nesta página
                    # Padrões comuns: "3.1.1", "a)", "•", "-"
                    req_patterns = [
                        r'\d+\.\d+\.\d+\.', # 3.1.1
                        r'^\s*[a-z]\)', # a), b), c)
                        r'^\s*•', # bullets
                        r'^\s*-\s+[A-Z]', # - Item
                    ]

                    req_count = sum(len(re.findall(p, text, re.MULTILINE)) for p in req_patterns)

                    if req_count > 3:  # Threshold: pelo menos 3 requisitos
                        item_copy['spec_pages'].append(page_num + 1)
                        item_copy['estimated_requirements'] += req_count

            # Se não encontrou nada, estimar baseado em similaridade
            if not item_copy['spec_pages']:
                item_copy['estimated_requirements'] = self._estimate_requirements(item['description'])
                item_copy['spec_pages'] = ['?']

            enhanced_items.append(item_copy)

        return enhanced_items

    def _extract_keywords(self, description: str) -> List[str]:
        """Extrai palavras-chave relevantes da descrição"""
        # Remover palavras comuns
        stop_words = ['DE', 'PARA', 'COM', 'E', 'A', 'O', 'DA', 'DO', 'EM', 'NA', 'NO']

        words = description.upper().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords[:3]  # Top 3 palavras-chave

    def _estimate_requirements(self, description: str) -> int:
        """Estima número de requisitos baseado no tipo de equipamento"""
        desc_upper = description.upper()

        # Heurísticas baseadas em complexidade típica
        if 'CÂMERA' in desc_upper or 'CAMERA' in desc_upper:
            return 35  # Câmeras geralmente têm ~30-40 requisitos
        elif 'SERVIDOR' in desc_upper or 'SERVER' in desc_upper:
            return 45  # Servidores são mais complexos
        elif 'SOFTWARE' in desc_upper:
            return 30
        elif 'SWITCH' in desc_upper:
            return 25
        elif 'SENSOR' in desc_upper:
            return 15
        elif 'INSTALAÇÃO' in desc_upper or 'SERVIÇO' in desc_upper:
            return 10
        else:
            return 20  # Padrão

    def analyze(self) -> Dict[str, Any]:
        """Executa análise completa"""
        self.load_pdf()

        # Encontrar itens
        items = self.find_items_table()

        if not items:
            print("⚠️  Nenhum item encontrado automaticamente")
            print("   O edital pode ter formato não padrão")
            return {
                'error': 'No items found',
                'message': 'Formato de edital não reconhecido automaticamente'
            }

        print(f"\n✅ Total de itens identificados: {len(items)}")

        # Encontrar especificações
        enhanced_items = self.find_specifications_sections(items)

        # Montar estrutura final
        self.structure = {
            'edital_path': str(self.pdf_path),
            'analyzed_at': datetime.now().isoformat(),
            'total_pages': self.total_pages,
            'total_items': len(enhanced_items),
            'items': enhanced_items
        }

        return self.structure

    def save_structure(self, output_path: str = None):
        """Salva estrutura em JSON"""
        if not output_path:
            output_path = self.pdf_path.parent / f"{self.pdf_path.stem}_structure.json"

        output_path = Path(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.structure, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Estrutura salva em: {output_path}")
        return output_path

    def print_summary(self):
        """Imprime resumo da análise"""
        if not self.structure or 'error' in self.structure:
            return

        print("\n" + "="*80)
        print("📋 RESUMO DA ANÁLISE")
        print("="*80)
        print(f"Total de itens: {self.structure['total_items']}")
        print(f"Total de páginas: {self.structure['total_pages']}")
        print()

        total_reqs = sum(item['estimated_requirements'] for item in self.structure['items'])
        print(f"Requisitos estimados: {total_reqs}")
        print()

        print("Amostra de itens encontrados:")
        for item in self.structure['items'][:5]:
            pages_str = ', '.join(map(str, item['spec_pages']))
            print(f"  [{item['item_id']}] {item['description'][:50]}...")
            print(f"       Quantidade: {item['quantity']} {item['unit']}")
            print(f"       Requisitos estimados: {item['estimated_requirements']}")
            print(f"       Páginas de especificação: {pages_str}")
            print()

        if len(self.structure['items']) > 5:
            print(f"  ... e mais {len(self.structure['items']) - 5} itens")

        print("="*80)


def main():
    if len(sys.argv) < 2:
        print("❌ Uso incorreto\n")
        print("Uso: python3 scripts/analyze_edital_structure.py <caminho-do-edital.pdf>\n")
        print("Exemplo:")
        print("   python3 scripts/analyze_edital_structure.py data/editais/edital_001.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("="*80)
    print("🔬 ANALISADOR DE ESTRUTURA DE EDITAIS")
    print("="*80)
    print(f"PDF: {pdf_path}")
    print()

    try:
        analyzer = EditalStructureAnalyzer(pdf_path)
        structure = analyzer.analyze()

        if 'error' not in structure:
            analyzer.print_summary()
            analyzer.save_structure(output_path)

            print("\n✅ Análise concluída com sucesso!")
        else:
            print(f"\n❌ Erro: {structure['message']}")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erro ao analisar edital: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
