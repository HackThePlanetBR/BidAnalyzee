---
description: List recent edital analyses with status and summary
---

# List Analyses

Shows history of edital analyses performed by the system.

## Usage

```
/list-analyses [quantity]
```

## Parameters

- `[quantity]` (optional): Number of analyses to list (default: 10, max: 50)

## What to do

When this command is executed:

1. **Execute the list script:**
   ```bash
   python scripts/orchestrator_list.py [quantity]
   ```

2. **Parse and format results:**
   - Show analyses in reverse chronological order (newest first)
   - Display session ID, date, edital name, status
   - Include summary statistics for each
   - Highlight recent analyses (< 24h)

3. **Provide navigation:**
   - Show how to get details of specific analysis
   - Indicate if there are more analyses available

## Example Output

```
📋 HISTÓRICO DE ANÁLISES
========================

Total de análises encontradas: 15
Mostrando: 10 mais recentes

1. 🆕 20251118_143022_edital_pmsp_001 [HÁ 2 HORAS]
   📅 Data: 18/11/2025 14:30
   📄 Edital: edital_pmsp_001.pdf
   📊 Status: ✅ Completo
   📈 Resumo: 50 requisitos | 35 Conformes | 2 Não Conformes | 13 Revisão
   📂 Sessão: 20251118_143022

2. 20251117_091533_edital_pmrj_045 [ONTEM]
   📅 Data: 17/11/2025 09:15
   📄 Edital: edital_pmrj_045.pdf
   📊 Status: ✅ Completo
   📈 Resumo: 32 requisitos | 28 Conformes | 1 Não Conforme | 3 Revisão
   📂 Sessão: 20251117_091533

3. 20251115_160244_edital_prefeitura_sp
   📅 Data: 15/11/2025 16:02
   📄 Edital: edital_prefeitura_sp_2025.pdf
   📊 Status: ✅ Completo
   📈 Resumo: 78 requisitos | 65 Conformes | 5 Não Conformes | 8 Revisão
   📂 Sessão: 20251115_160244

4. 20251114_103501_edital_obras_publicas
   📅 Data: 14/11/2025 10:35
   📄 Edital: edital_obras_publicas.pdf
   📊 Status: ⚠️ Incompleto (extração OK, análise pendente)
   📈 Resumo: 45 requisitos extraídos | Análise não realizada
   📂 Sessão: 20251114_103501

5. 20251113_144520_edital_ti_equipamentos
   📅 Data: 13/11/2025 14:45
   📄 Edital: edital_ti_equipamentos.pdf
   📊 Status: ✅ Completo
   📈 Resumo: 120 requisitos | 98 Conformes | 12 Não Conformes | 10 Revisão
   📂 Sessão: 20251113_144520

... (mais 5 análises)

---

Ver detalhes de uma análise específica:
/session <session-id>

Exemplo:
/session 20251118_143022
```

## Status Indicators

- ✅ **Completo** - Extraction + Analysis + Reports generated
- ⚠️ **Incompleto** - Partial (only extraction, or analysis without reports)
- ❌ **Erro** - Failed during processing
- 🔄 **Em andamento** - Currently processing

## Empty List

```
📋 HISTÓRICO DE ANÁLISES
========================

Nenhuma análise encontrada.

Ainda não há análises realizadas no sistema.

Para começar:
/validate-pdf <edital.pdf>
/structure-edital <edital.pdf>
/analyze-edital <requirements.csv>
```

## Related Commands

- `/session <id>` - View detailed information about specific analysis
- `/structure-edital <pdf>` - Start new analysis
- `/help` - List all commands
