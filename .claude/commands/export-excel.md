---
description: Generate Excel spreadsheet with multiple tabs from conformity analysis CSV
---

# Export Excel

Generates a professional Excel spreadsheet with multiple tabs from conformity analysis results.

## Usage

```
/export-excel <analysis-csv> [output-path]
```

## Parameters

- `<analysis-csv>` (required): Path to analysis CSV file (output from `/analyze-edital`)
- `[output-path]` (optional): Path to save Excel file. If not provided, saves in same directory as CSV

## What to do

When this command is executed:

1. **Execute the export script:**
   ```bash
   python scripts/export_excel.py <analysis-csv> [output-path]
   ```

2. **Monitor and report progress:**
   - Show generation progress
   - Indicate tabs being created
   - Report when complete

3. **Present results:**
   - Show path to generated Excel file
   - Show file size
   - List tabs included
   - Provide summary of features

## Example Output

```
📊 GERANDO PLANILHA EXCEL
=========================

Processando análise...
- Total de requisitos: 50
- Criando aba "Resumo"...
- Criando aba "Detalhes"...
- Criando aba "Conformes" (35 itens)...
- Criando aba "Não Conformes" (2 itens)...
- Criando aba "Em Revisão" (13 itens)...
- Aplicando formatação condicional...
- Gerando gráficos...
- Ajustando colunas...

✅ PLANILHA EXCEL GERADA

Arquivo: data/deliveries/20251118_143022_edital_001/outputs/relatorio_edital_001.xlsx
Tamanho: 156 KB

Abas incluídas:
✅ Resumo - Estatísticas e gráficos
✅ Detalhes - Análise completa de todos os requisitos
✅ Conformes - Filtro dos 35 requisitos CONFORMES
✅ Não Conformes - Filtro dos 2 requisitos NÃO CONFORMES
✅ Em Revisão - Filtro dos 13 requisitos que precisam revisão

Recursos:
✅ Formatação condicional por veredicto
✅ Gráficos de pizza e barras
✅ Colunas auto-ajustadas
✅ Cabeçalhos fixos para rolagem
✅ Filtros automáticos

A planilha está pronta para análise no Excel.
```

## Excel Contents

The generated Excel file includes:
- **Aba "Resumo"**: Statistics with charts
- **Aba "Detalhes"**: Complete analysis of all requirements
- **Abas filtradas**: Separate tabs by verdict
- **Conditional formatting**: Color-coded verdicts
- **Auto-sized columns**: Readable layout
- **Frozen headers**: Easy scrolling
- **Auto filters**: Interactive filtering

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

O arquivo não contém as colunas necessárias para export Excel.

Colunas necessárias:
- ID, Requisito, Categoria, Veredicto, Confiança, Evidências, Raciocínio, Recomendações

Este CSV foi gerado por /analyze-edital?
```

## Related Commands

- `/export-pdf <csv>` - Generate PDF report
- `/analyze-edital <csv>` - Run conformity analysis first
- `/list-analyses` - See available analyses
