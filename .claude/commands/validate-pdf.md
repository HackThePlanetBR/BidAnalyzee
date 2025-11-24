---
description: Validate PDF file before processing - checks size, format, text extraction, and OCR requirements
---

# Validate PDF

Validates a PDF file to ensure it can be processed by the BidAnalyzee system.

## Usage

```
/validate-pdf <pdf-path>
```

## Parameters

- `<pdf-path>` (required): Path to PDF file to validate

## What to do

When this command is executed:

1. **Execute the validation script:**
   ```bash
   python scripts/validate_pdf.py <pdf-path>
   ```

2. **Parse and present the results:**
   - Display validation status (✅ approved / ❌ rejected)
   - Show file details (size, pages, format)
   - Indicate if OCR is needed
   - Show if text is extractable
   - List any issues found

3. **Provide guidance:**
   - If approved: "PDF ready for processing. Use `/structure-edital <pdf-path>` to extract requirements."
   - If rejected: Explain issues and how to fix them

## Example Output

```
✅ VALIDAÇÃO COMPLETA - PDF APROVADO

Detalhes:
- Arquivo: edital_12345.pdf
- Tamanho: 2.3 MB (dentro do limite de 500MB)
- Páginas: 45
- Formato: PDF válido
- Texto extraível: Sim
- OCR necessário: Não
- Metadados: Presentes

Status: ✅ Pronto para processar

Próximo passo:
/structure-edital edital_12345.pdf
```

## Error Handling

If validation fails, show specific error and solution:

**File too large:**
```
❌ VALIDAÇÃO FALHOU

Erro: Arquivo muito grande (520 MB)
Limite: 500 MB

Soluções:
1. Comprimir PDF (ferramentas online)
2. Dividir em partes menores
3. Remover páginas desnecessárias
```

**No text extractable:**
```
⚠️ VALIDAÇÃO - OCR NECESSÁRIO

Aviso: PDF escaneado (sem texto extraível)
OCR: Será aplicado automaticamente (mais lento)

Tempo estimado com OCR: +50-100% do normal

Status: ✅ Pode processar (com OCR)

Próximo passo:
/structure-edital edital_12345.pdf
```

## Related Commands

- `/structure-edital <pdf>` - Extract requirements after validation
- `/help` - List all commands
