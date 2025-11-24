---
description: View detailed information about a specific analysis session
---

# Session Details

Shows complete details about a specific analysis session including statistics, files generated, and execution log.

## Usage

```
/session <session-id>
```

## Parameters

- `<session-id>` (required): Session identifier (get from `/list-analyses`)

## What to do

When this command is executed:

1. **Execute the session script:**
   ```bash
   python scripts/orchestrator_session.py <session-id>
   ```

2. **Parse and format results comprehensively:**
   - Session metadata (ID, date, duration)
   - Edital information (name, size, pages)
   - Extraction statistics (requirements found)
   - Analysis statistics (verdicts breakdown)
   - Files generated (paths and sizes)
   - Execution timeline
   - Critical items flagged

3. **Provide actionable next steps:**
   - Links to generated files
   - Suggestions for reports
   - Navigation to related sessions

## Example Output

```
📊 DETALHES DA SESSÃO
=====================

SESSION ID: 20251118_143022_edital_pmsp_001

📋 Informações Gerais
---------------------
Data/Hora: 18/11/2025 14:30:22
Duração total: 42 minutos
Status: ✅ Completo
Workflow: Extraction → Analysis → Reports

📄 Edital Analisado
-------------------
Arquivo: edital_pmsp_001.pdf
Tamanho: 2.3 MB
Páginas: 45
OCR utilizado: Não
Texto extraível: Sim

📊 Estatísticas de Extração
----------------------------
Requisitos extraídos: 50
Categorias encontradas:
  - Hardware: 20 requisitos (40%)
  - Software: 15 requisitos (30%)
  - Serviços: 10 requisitos (20%)
  - Legal: 5 requisitos (10%)
Confiança média: 0.89 (Alta)

📈 Estatísticas de Análise
---------------------------
Total analisado: 50 requisitos
Tempo de análise: 28 minutos

Veredictos:
  ✅ CONFORME: 35 requisitos (70%)
  ❌ NÃO CONFORME: 2 requisitos (4%)
  ⚠️  REVISÃO: 13 requisitos (26%)

Confiança média: 0.82 (Alta)

🚨 Itens Críticos (NÃO CONFORME)
---------------------------------
1. REQ-042: "Marca específica exigida"
   Problema: Viola Lei 8.666/93 Art. 7º (direcionamento)
   Ação: Questionar no edital ou não participar

2. REQ-067: "Prazo de execução 30 dias"
   Problema: Incompatível com legislação (mínimo 60 dias)
   Ação: Solicitar retificação do edital

📂 Arquivos Gerados
-------------------
1. Requirements CSV
   Caminho: data/deliveries/20251118_143022_edital_pmsp_001/outputs/requirements_structured.csv
   Tamanho: 45 KB

2. Analysis CSV
   Caminho: data/deliveries/20251118_143022_edital_pmsp_001/outputs/analysis_conformidade.csv
   Tamanho: 78 KB

3. PDF Report
   Caminho: data/deliveries/20251118_143022_edital_pmsp_001/outputs/relatorio_edital_pmsp_001.pdf
   Tamanho: 2.1 MB

4. Excel Report
   Caminho: data/deliveries/20251118_143022_edital_pmsp_001/outputs/relatorio_edital_pmsp_001.xlsx
   Tamanho: 156 KB

⏱️ Timeline de Execução
------------------------
14:30:22 - Início da sessão
14:31:05 - Validação PDF concluída
14:32:18 - Extração iniciada
14:45:33 - Extração completa (50 requisitos)
14:46:01 - Análise iniciada
15:14:22 - Análise completa
15:15:08 - Relatório PDF gerado
15:15:42 - Relatório Excel gerado
15:15:42 - Sessão finalizada

Total: 42 minutos

---

💡 Próximas Ações Sugeridas:

1. Revisar itens NÃO CONFORMES (2 itens críticos)
2. Analisar itens em REVISÃO (13 itens precisam atenção)
3. Gerar novo relatório se fez ajustes:
   /export-pdf data/deliveries/20251118_143022_edital_pmsp_001/outputs/analysis_conformidade.csv
   /export-excel data/deliveries/20251118_143022_edital_pmsp_001/outputs/analysis_conformidade.csv

Ver todas as análises:
/list-analyses
```

## Session Not Found

```
❌ SESSÃO NÃO ENCONTRADA

Session ID: abc123xyz (não encontrado)

Possíveis causas:
1. ID digitado incorretamente
2. Sessão foi deletada
3. Sessão ainda não foi criada

Ver sessões disponíveis:
/list-analyses
```

## Incomplete Session

```
⚠️ SESSÃO INCOMPLETA

Session ID: 20251114_103501_edital_obras_publicas

Status: Parcialmente completo
Progresso: Extração ✅ | Análise ❌ | Relatórios ❌

📊 O que foi feito:
- ✅ PDF validado
- ✅ Requisitos extraídos (45 itens)
- ❌ Análise de conformidade não executada

💡 Para completar a análise:
/analyze-edital data/deliveries/20251114_103501_edital_obras_publicas/outputs/requirements_structured.csv
```

## Related Commands

- `/list-analyses` - See all analysis sessions
- `/export-pdf <csv>` - Generate new PDF report
- `/export-excel <csv>` - Generate new Excel report
- `/help` - List all commands
