# INSPECT Phase - Exemplos Práticos

**Versão:** 1.0

---

## Exemplo 1: Inspeção de CSV Estruturado (PASS)

**Contexto:** @EstruturadorDeDocumentos acabou de gerar CSV com 47 requisitos

**Output a Inspecionar:** `requisitos_estruturados.csv`

### Checklist Fixo (Anti-Alucinação): 8 itens

```python
# Item AA-01: "Todas as informações foram extraídas de fontes fornecidas?"
verificar: Cada linha tem referência ao edital.pdf
resultado: ✓ PASS - Todas as 47 linhas extraídas do PDF fornecido

# Item AA-02: "Não há invenção ou suposição de dados?"
verificar: Requisitos são cópia textual (não parafraseados)
resultado: ✓ PASS - Todos os requisitos copiados literalmente

# Item AA-03: "Cada afirmação tem evidência rastreável?"
verificar: Fonte está documentada (edital.pdf, páginas X-Y)
resultado: ✓ PASS - Campo 'fonte' preenchido em todas as linhas

# ... (mais 5 itens) ...
# Todos passaram ✓
```

### Checklist Dinâmico (Estruturação): 8 itens

```python
# Item ED-01: "Cada linha do CSV representa um requisito único?"
verificar: Não há múltiplos requisitos numa linha
resultado: ✓ PASS - Todos os 47 requisitos são únicos

# Item ED-02: "Todas as colunas obrigatórias estão preenchidas?"
verificar: Colunas ID, Descrição, Tipo, Categoria
resultado: ✓ PASS - Todas as colunas preenchidas

# Item ED-03: "Não há requisitos duplicados?"
verificar: Comparar descrições (hash de conteúdo)
resultado: ✓ PASS - Zero duplicatas encontradas

# ... (mais 5 itens) ...
# Todos passaram ✓
```

### Resultado Final

```
✅ INSPEÇÃO PASSOU

Checklist Fixo: 8/8 ✓
Checklist Dinâmico: 8/8 ✓

Total: 16/16 (100%)

Próxima ação: VALIDATE
```

---

## Exemplo 2: Inspeção com Falha (FAIL → LOOP)

**Contexto:** Mesmo cenário, mas CSV tem problemas

### Checklist Fixo: PASSOU

```
Todos os 8 itens passaram ✓
```

### Checklist Dinâmico: FALHOU

```python
# Itens 1-2: ✓ PASS
# ...

# Item ED-03: "Não há requisitos duplicados?"
verificar: Comparar descrições
resultado: ✗ FAIL - Requisitos ID 12 e 23 têm descrição idêntica:
           "Sistema deve suportar resolução Full HD"
ação_corretiva: "Remover requisito ID 23 (duplicata)"

# Itens 4-7: ✓ PASS

# Item ED-08: "Referências cruzadas foram preservadas?"
verificar: Menções a "conforme item X" mantidas
resultado: ✗ FAIL - Requisito ID 34 menciona "conforme item 5.2"
           mas essa referência não foi preservada no CSV
ação_corretiva: "Adicionar nota na coluna 'Obs': 'Ver item 5.2'"
```

### Resultado Final

```
❌ INSPEÇÃO FALHOU

Checklist Fixo: 8/8 ✓
Checklist Dinâmico: 6/8 ✗

Total: 14/16 (87.5%)

Itens que falharam:

1. [ED-03] "Não há requisitos duplicados?"
   Problema: IDs 12 e 23 duplicados
   Ação: Remover ID 23

2. [ED-08] "Referências cruzadas preservadas?"
   Problema: Requisito 34 perdeu referência a item 5.2
   Ação: Adicionar nota na coluna 'Obs'

Próxima ação: LOOP (corrigir 2 problemas)
```

---

## Exemplo 3: Item Crítico Falha → HALT Imediato

**Contexto:** Inspeção detecta problema crítico (severity: critical)

```python
# Item AA-02: "Não há invenção ou suposição de dados?"
# (severity: critical)

verificar: Dados foram inventados/supostos?
resultado: ✗ FAIL - Requisito ID 15 contém:
           "Sistema provavelmente precisa de câmeras IP"

           A palavra "provavelmente" indica SUPOSIÇÃO, não fato do edital.

ação: HALT IMEDIATO (não continuar checklist)

halt_message: """
❌ PROBLEMA CRÍTICO Detectado (Item AA-02)

Requisito ID 15 contém suposição:
"Sistema provavelmente precisa de câmeras IP"

Isso viola o princípio fundamental: nunca assumir dados.

Opções:
1. Remover palavra "provavelmente" e confirmar que está no edital
2. Marcar requisito para revisão humana
3. Cancelar estruturação e revisar edital original

Sua escolha [1-3]:
"""
```

---

## Resumo dos Exemplos

| Exemplo | Cenário | Resultado | Próxima Ação |
|---------|---------|-----------|--------------|
| 1 | Todos os itens passaram | PASS (16/16) | VALIDATE |
| 2 | 2 itens falharam | FAIL (14/16) | LOOP |
| 3 | Item crítico falhou | FAIL + HALT | Decisão do usuário |

---

## Código de Verificação (Exemplo Item ED-03)

```python
def check_duplicates(csv_data):
    """
    Verifica se há requisitos duplicados no CSV

    Returns: (passed: bool, evidence: str)
    """
    descriptions = [row['Descrição'] for row in csv_data]

    # Procurar duplicatas
    seen = {}
    duplicates = []

    for i, desc in enumerate(descriptions, start=1):
        desc_hash = hashlib.md5(desc.encode()).hexdigest()

        if desc_hash in seen:
            duplicates.append({
                "id1": seen[desc_hash],
                "id2": i,
                "text": desc[:50]
            })
        else:
            seen[desc_hash] = i

    if duplicates:
        # Falhou
        dup_list = ", ".join([f"IDs {d['id1']} e {d['id2']}" for d in duplicates])
        return (
            False,
            f"Encontradas {len(duplicates)} duplicatas: {dup_list}"
        )
    else:
        # Passou
        return (
            True,
            f"Zero duplicatas em {len(descriptions)} requisitos"
        )
```

---

**Versão:** 1.0
**Criado em:** 06/11/2025
