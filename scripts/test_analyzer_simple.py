#!/usr/bin/env python3
import PyPDF2
import re
import json

pdf_path = "data/e2e_tests/edital_complexo/input/edital.pdf"

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)

    print(f"Total páginas: {len(reader.pages)}\n")

    items = []

    # Procurar nas primeiras 15 páginas
    for i in range(min(15, len(reader.pages))):
        text = reader.pages[i].extract_text()

        pattern = r'(\d+)\s*([A-ZÇÃÕÁÉÍÓÚ\s\-/()]+?)\s+(Unidade|Serviço|Turma|Par|Pares|Metros)\s+(\d+)\s+R\$'

        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

        if matches:
            print(f"Página {i+1}: {len(matches)} itens")

            for match in matches:
                item_num, description, unit, quantity = match

                description = description.strip()
                description = re.sub(r'\s+', ' ', description)

                if len(description) < 5:
                    continue

                if any(item['item_id'] == item_num for item in items):
                    continue

                items.append({
                    'item_id': item_num,
                    'description': description,
                    'unit': unit,
                    'quantity': int(quantity),
                })

    print(f"\n✅ Total de itens únicos: {len(items)}\n")

    for item in items[:10]:
        print(f"  [{item['item_id']}] {item['description'][:50]}")

    if len(items) > 10:
        print(f"\n  ... e mais {len(items) - 10} itens")

    # Salvar
    output = {
        'total_items': len(items),
        'items': items
    }

    with open('data/e2e_tests/edital_complexo/extraction/edital_structure.json', 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n💾 Estrutura salva!")
