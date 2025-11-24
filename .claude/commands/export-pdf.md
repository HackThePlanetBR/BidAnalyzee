---
description: Generate professional PDF report from conformity analysis CSV
---

# Export PDF

Generates a professional PDF report from conformity analysis results.

## Usage

```
/export-pdf <analysis-csv> [output-path]
```

## Parameters

- `<analysis-csv>` (required): Path to analysis CSV file (output from `/analyze-edital`)
- `[output-path]` (optional): Path to save PDF. If not provided, saves in same directory as CSV

## What to do

When this command is executed:

1. **Execute the export script:**
   ```bash
   python scripts/export_pdf.py <analysis-csv> [output-path]
   ```

2. **Monitor and report progress:**
   - Show generation progress
   - Indicate number of requirements being processed
   - Report when complete

3. **Present results:**
   - Show path to generated PDF
   - Show file size
   - Provide summary of what's included

## Example Output

```
📄 GERANDO RELATÓRIO PDF
========================

Processando análise...
- Total de requisitos: 50
- Gerando capa executiva...
- Criando tabelas por veredicto...
- Aplicando formatação...

✅ RELATÓRIO PDF GERADO

Arquivo: data/deliveries/20251118_143022_edital_001/outputs/relatorio_edital_001.pdf
Tamanho: 2.1 MB
Páginas: 15

Conteúdo incluído:
✅ Capa executiva com resumo
✅ Estatísticas gerais
✅ Tabela de requisitos CONFORMES (35 itens)
✅ Tabela de requisitos NÃO CONFORMES (2 itens)
✅ Tabela de requisitos em REVISÃO (13 itens)
✅ Código de cores por veredicto
✅ Layout profissional

O relatório está pronto para apresentação.
```

## PDF Contents

The generated PDF includes:
- Executive cover page with summary
- Overall statistics table
- Detailed requirements table
- Color-coded verdicts (green/red/yellow)
- Professional formatting (ReportLab)

## Error Handling

**CSV not found:**
```
❌ ERRO: Arquivo não encontrado

Arquivo: analysis_conformidade.csv
Caminho procurado: data/deliveries/.../analysis_conformidade.csv

Verifique:
1. O caminho está correto?
2. A análise foi concluída?
3. Use /list-analyses para ver análises disponíveis
```

**Invalid CSV format:**
```
❌ ERRO: CSV inválido

O arquivo não contém as colunas necessárias para export PDF.

Colunas necessárias:
- ID, Requisito, Categoria, Veredicto, Confiança, Evidências, Raciocínio, Recomendações

Este CSV foi gerado por /analyze-edital?
```

## Related Commands

- `/export-excel <csv>` - Generate Excel report
- `/analyze-edital <csv>` - Run conformity analysis first
- `/list-analyses` - See available analyses
