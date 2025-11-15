#!/usr/bin/env python3
"""
Seleção Interativa de Itens do Edital

Permite ao usuário escolher quais itens do edital deseja analisar.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any


def load_structure(json_path: str) -> Dict[str, Any]:
    """Carrega estrutura do edital"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def display_items(items: List[Dict]) -> None:
    """Exibe lista de itens"""
    print("\n" + "="*80)
    print("📋 ITENS ENCONTRADOS NO EDITAL")
    print("="*80)
    print()

    for idx, item in enumerate(items, 1):
        desc = item['description']
        if len(desc) > 60:
            desc = desc[:57] + "..."

        qty = item['quantity']
        unit = item['unit']

        print(f"[{idx:2d}] {desc:60s} ({qty:5d} {unit})")

    print()
    print("="*80)


def get_user_selection(total_items: int) -> List[int]:
    """Obtém seleção do usuário"""
    while True:
        print("\nEscolha uma opção:")
        print("[T] Analisar TODOS os itens")
        print("[S] Selecionar itens específicos")
        print("[Q] Cancelar")
        print()

        choice = input("> ").strip().upper()

        if choice == 'Q':
            print("\n❌ Operação cancelada pelo usuário")
            sys.exit(0)

        elif choice == 'T':
            return list(range(1, total_items + 1))

        elif choice == 'S':
            print(f"\nDigite os números dos itens separados por vírgula (ex: 1,3,5-7,10):")
            print("(Use 'X-Y' para selecionar intervalo)")

            selection_input = input("> ").strip()

            try:
                selected = parse_selection(selection_input, total_items)

                if not selected:
                    print("⚠️  Nenhum item selecionado. Tente novamente.")
                    continue

                return selected

            except ValueError as e:
                print(f"⚠️  Erro: {e}")
                print("   Tente novamente.")
                continue

        else:
            print("⚠️  Opção inválida. Escolha T, S ou Q.")


def parse_selection(selection_str: str, max_items: int) -> List[int]:
    """
    Parse seleção do usuário

    Exemplos:
    - "1,2,3" -> [1,2,3]
    - "1-5" -> [1,2,3,4,5]
    - "1,3-5,7" -> [1,3,4,5,7]
    """
    selected = set()

    parts = selection_str.split(',')

    for part in parts:
        part = part.strip()

        if '-' in part:
            # Intervalo
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())

                if start < 1 or end > max_items or start > end:
                    raise ValueError(f"Intervalo inválido: {part}")

                selected.update(range(start, end + 1))
            except ValueError:
                raise ValueError(f"Intervalo mal formatado: {part}")
        else:
            # Número individual
            try:
                num = int(part)

                if num < 1 or num > max_items:
                    raise ValueError(f"Número fora do intervalo (1-{max_items}): {num}")

                selected.add(num)
            except ValueError:
                raise ValueError(f"Número inválido: {part}")

    return sorted(list(selected))


def confirm_selection(items: List[Dict], selected_indices: List[int]) -> bool:
    """Confirma seleção com usuário"""
    print("\n✅ Itens selecionados:")
    print()

    for idx in selected_indices:
        item = items[idx - 1]
        desc = item['description']
        if len(desc) > 50:
            desc = desc[:47] + "..."
        print(f"  [{idx:2d}] {desc}")

    print()
    print(f"Total: {len(selected_indices)} itens")
    print()

    confirm = input("Confirma seleção? [S/n]: ").strip().lower()

    return confirm in ['', 's', 'sim', 'y', 'yes']


def save_selection(structure: Dict, selected_indices: List[int], output_path: str) -> None:
    """Salva seleção em JSON"""
    selected_items = [structure['items'][idx - 1] for idx in selected_indices]

    selection = {
        'total_items_in_edital': structure['total_items'],
        'selected_count': len(selected_items),
        'selected_indices': selected_indices,
        'selected_items': selected_items
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(selection, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Seleção salva em: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/select_items.py <edital_structure.json> [output.json]")
        sys.exit(1)

    structure_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "selected_items.json"

    # Carregar estrutura
    structure = load_structure(structure_path)
    items = structure['items']

    if not items:
        print("❌ Erro: Nenhum item encontrado na estrutura")
        sys.exit(1)

    # Exibir itens
    display_items(items)

    # Obter seleção
    selected_indices = get_user_selection(len(items))

    # Confirmar
    if not confirm_selection(items, selected_indices):
        print("\n❌ Seleção cancelada")
        sys.exit(0)

    # Salvar
    save_selection(structure, selected_indices, output_path)

    print("\n✅ Pronto! Use o arquivo de seleção para prosseguir com a análise.")


if __name__ == "__main__":
    main()
