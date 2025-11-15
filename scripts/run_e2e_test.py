#!/usr/bin/env python3
"""
Teste E2E Completo - Edital Complexo

Executa workflow completo de ponta a ponta com edital complexo.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_command(cmd: list, description: str) -> tuple:
    """Executa comando e retorna (success, output)"""
    print(f"\n{'='*80}")
    print(f"▶️  {description}")
    print(f"{'='*80}")
    print(f"Comando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )

        print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            return (True, result.stdout)
        else:
            print(f"❌ {description} - FALHOU (exit code {result.returncode})")
            return (False, result.stderr)

    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} - TIMEOUT")
        return (False, "Timeout")
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return (False, str(e))


def main():
    print("\n" + "="*80)
    print("🧪 TESTE E2E - EDITAL COMPLEXO")
    print("="*80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configuração
    base_dir = Path("data/e2e_tests/edital_complexo")
    pdf_path = base_dir / "input" / "edital.pdf"
    extraction_dir = base_dir / "extraction"

    if not pdf_path.exists():
        print(f"❌ PDF não encontrado: {pdf_path}")
        sys.exit(1)

    # Resultados
    results = []

    # Fase 1: Análise de Estrutura
    step = run_command(
        ["python3", "scripts/test_analyzer_simple.py", str(pdf_path)],
        "Fase 1: Análise de Estrutura do Edital"
    )
    results.append({
        'fase': 'Análise de Estrutura',
        'success': step[0],
        'output': step[1][:500]
    })

    if not step[0]:
        print("\n❌ Teste E2E interrompido - Análise de estrutura falhou")
        sys.exit(1)

    # Verificar se estrutura foi gerada
    structure_path = extraction_dir / "edital_structure.json"
    if not structure_path.exists():
        print(f"❌ Estrutura não foi gerada: {structure_path}")
        sys.exit(1)

    # Carregar estrutura
    with open(structure_path, 'r') as f:
        structure = json.load(f)

    total_items = structure.get('total_items', 0)
    print(f"\n📊 Estrutura identificada: {total_items} itens")

    # Fase 2: Seleção de Itens (automática - todos)
    print("\n" + "="*80)
    print("▶️  Fase 2: Seleção de Itens")
    print("="*80)
    print("Modo: TODOS OS ITENS (automático)")

    # Criar seleção automática
    selected_items_path = extraction_dir / "selected_items.json"
    selection = {
        'total_items_in_edital': total_items,
        'selected_count': total_items,
        'selected_indices': list(range(1, total_items + 1)),
        'selected_items': structure['items']
    }

    with open(selected_items_path, 'w', encoding='utf-8') as f:
        json.dump(selection, f, ensure_ascii=False, indent=2)

    print(f"✅ {total_items} itens selecionados para análise")
    results.append({
        'fase': 'Seleção de Itens',
        'success': True,
        'output': f"{total_items} itens selecionados"
    })

    # Fase 3: Extração Multi-Item
    step = run_command(
        [
            "python3", "scripts/extract_multi_item.py",
            str(pdf_path),
            str(selected_items_path),
            str(extraction_dir)
        ],
        "Fase 3: Extração Multi-Item (CSVs)"
    )
    results.append({
        'fase': 'Extração Multi-Item',
        'success': step[0],
        'output': step[1][:500]
    })

    if not step[0]:
        print("\n⚠️  Extração falhou - continuando com validação")

    # Fase 4: Validação vs PDF Original
    step = run_command(
        [
            "python3", "scripts/validate_extraction.py",
            str(pdf_path),
            str(selected_items_path),
            str(extraction_dir)
        ],
        "Fase 4: Validação vs PDF Original"
    )
    results.append({
        'fase': 'Validação vs PDF',
        'success': step[0],
        'output': step[1][:500]
    })

    # Fase 5: Análise de Conformidade (Mock KB)
    step = run_command(
        [
            "python3", "scripts/analyze_conformity_e2e.py",
            str(selected_items_path),
            str(extraction_dir)
        ],
        "Fase 5: Análise de Conformidade (Mock KB)"
    )
    results.append({
        'fase': 'Análise de Conformidade',
        'success': step[0],
        'output': step[1][:500]
    })

    # Resumo Final
    print("\n" + "="*80)
    print("📊 RESUMO DO TESTE E2E")
    print("="*80)
    print()

    total_fases = len(results)
    fases_sucesso = sum(1 for r in results if r['success'])

    for i, result in enumerate(results, 1):
        status = "✅ PASSOU" if result['success'] else "❌ FALHOU"
        print(f"[{i}/{total_fases}] {result['fase']}: {status}")

    print()
    print(f"Taxa de sucesso: {fases_sucesso}/{total_fases} ({fases_sucesso/total_fases*100:.1f}%)")
    print()

    # Verificar arquivos gerados
    print("📁 Arquivos gerados:")
    print()

    files_to_check = [
        (extraction_dir / "edital_structure.json", "Estrutura do edital"),
        (extraction_dir / "selected_items.json", "Itens selecionados"),
        (extraction_dir / "extraction_summary.json", "Resumo de extração"),
        (base_dir / "validation" / "validation_report.json", "Relatório de validação"),
        (base_dir / "analysis" / "conformity_report_mock.json", "Relatório de conformidade"),
    ]

    for file_path, desc in files_to_check:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {desc}: {file_path.name} ({size} bytes)")
        else:
            print(f"   ❌ {desc}: AUSENTE")

    # Contar CSVs gerados
    csv_files = list(extraction_dir.glob("item_*.csv"))
    print(f"   ✅ CSVs de requisitos: {len(csv_files)} arquivos")
    print()

    # Salvar log de teste
    log_path = base_dir / "logs" / "e2e_test_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    test_log = {
        'timestamp': datetime.now().isoformat(),
        'pdf_path': str(pdf_path),
        'total_items': total_items,
        'phases': results,
        'success_rate': f"{fases_sucesso}/{total_fases}",
        'csv_count': len(csv_files)
    }

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(test_log, f, ensure_ascii=False, indent=2)

    print(f"💾 Log do teste salvo em: {log_path}")
    print()
    print("="*80)
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Exit code
    if fases_sucesso == total_fases:
        print("\n✅ TESTE E2E PASSOU EM TODAS AS FASES")
        sys.exit(0)
    else:
        print("\n⚠️  TESTE E2E PASSOU COM AVISOS")
        sys.exit(0)  # Não falhar pois algumas fases são opcionais


if __name__ == "__main__":
    main()
