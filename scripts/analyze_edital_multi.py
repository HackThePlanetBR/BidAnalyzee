#!/usr/bin/env python3
"""
Workflow Completo de Análise Multi-Item

Executa análise completa de edital com suporte a seleção de itens.

Fluxo:
1. Analisa estrutura do edital
2. Permite seleção de itens
3. Extrai requisitos (múltiplos CSVs)
4. Gera relatórios consolidados

Uso:
    python3 scripts/analyze_edital_multi.py <edital.pdf> <output_dir>
"""

import sys
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("❌ Uso incorreto\n")
        print("Uso: python3 scripts/analyze_edital_multi.py <edital.pdf> [output_dir]\n")
        print("Exemplo:")
        print("   python3 scripts/analyze_edital_multi.py data/editais/edital.pdf")
        sys.exit(1)

    edital_pdf = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f"analysis_{edital_pdf.stem}")

    if not edital_pdf.exists():
        print(f"❌ Erro: PDF não encontrado: {edital_pdf}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("🚀 ANÁLISE MULTI-ITEM DE EDITAL")
    print("="*80)
    print(f"PDF: {edital_pdf}")
    print(f"Output: {output_dir}")
    print()

    # Passo 1: Analisar estrutura
    print("📋 Passo 1: Analisando estrutura do edital...")
    structure_path = output_dir / "edital_structure.json"

    result = subprocess.run([
        "python3", "scripts/test_analyzer_simple.py"
    ], env={"PDF_PATH": str(edital_pdf), "OUTPUT_PATH": str(structure_path)})

    if result.returncode != 0:
        print("❌ Erro na análise de estrutura")
        sys.exit(1)

    print(f"✅ Estrutura identificada: {structure_path}\n")

    # Passo 2: Seleção interativa
    print("📋 Passo 2: Seleção de itens")
    print("(Usando seleção automática para demo - em produção seria interativa)\n")

    selection_path = output_dir / "selected_items.json"

    # Para demo, criar seleção programática
    import json

    with open(structure_path) as f:
        structure = json.load(f)

    # Selecionar primeiros 3 itens
    selected_indices = list(range(1, min(4, len(structure['items']) + 1)))
    selected_items = [structure['items'][idx-1] for idx in selected_indices]

    selection = {
        'total_items_in_edital': structure['total_items'],
        'selected_count': len(selected_items),
        'selected_indices': selected_indices,
        'selected_items': selected_items
    }

    with open(selection_path, 'w') as f:
        json.dump(selection, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(selected_items)} itens selecionados\n")

    # Passo 3: Extração multi-item
    print("📋 Passo 3: Extraindo requisitos...")

    extraction_dir = output_dir / "extraction"

    result = subprocess.run([
        "python3", "scripts/extract_multi_item.py",
        str(edital_pdf),
        str(selection_path),
        str(extraction_dir)
    ])

    if result.returncode != 0:
        print("❌ Erro na extração")
        sys.exit(1)

    print("\n✅ Extração concluída\n")

    # Resumo final
    print("="*80)
    print("✅ ANÁLISE COMPLETA")
    print("="*80)
    print(f"Resultados em: {output_dir}")
    print(f"  - Estrutura: {structure_path.name}")
    print(f"  - Seleção: {selection_path.name}")
    print(f"  - CSVs: {extraction_dir}/")
    print()
    print("📝 Próximos passos:")
    print("  - Analisar CSVs gerados")
    print("  - Gerar relatórios consolidados")
    print()


if __name__ == "__main__":
    main()
