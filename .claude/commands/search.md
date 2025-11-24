---
description: Quick RAG search in knowledge base - instant lookup without full analysis
---

# Search Knowledge Base

Performs a quick RAG (Retrieval-Augmented Generation) search in the knowledge base without running a full analysis.

## Usage

```
/search "<query>"
```

## Parameters

- `<query>` (required): Search query in natural language (use quotes)

## What to do

When this command is executed:

1. **Execute the RAG search script:**
   ```bash
   python scripts/rag_search.py --requirement "<query>" --top-k 5
   ```

2. **Parse and present results:**
   - Show top 5 most relevant results
   - Display similarity scores
   - Show source citations (document:line)
   - Highlight high-confidence results (≥0.85)

3. **Format output clearly:**
   - Rank results by relevance
   - Show document excerpts
   - Provide actionable information

## Example Output

```
🔍 BUSCA RAG: "prazo de validade de propostas"
===============================================

Top 5 resultados encontrados:

1. ⭐ Lei 8.666/93:120 (Similaridade: 0.92) ← Alta confiança
   "O prazo de validade da proposta não será inferior a 60 dias
   contados da data de sua entrega."

   Contexto: Art. 64, §3º da Lei 8.666/93

2. Lei 14.133/2021:87 (Similaridade: 0.88) ← Alta confiança
   "A validade da proposta será de no mínimo 60 dias, prorrogável
   até o máximo de 180 dias mediante acordo."

   Contexto: Art. 65, §2º da Lei 14.133/2021

3. requisitos_tecnicos.md:45 (Similaridade: 0.76)
   "Propostas técnicas devem especificar prazo de validade dos
   equipamentos oferecidos, mínimo 12 meses de garantia."

   Contexto: Requisitos técnicos comuns - Garantias

4. documentacao_qualificacao.md:23 (Similaridade: 0.71)
   "Documentos de qualificação têm validade de 90 dias."

   Contexto: Documentação para licitações

5. prazos_cronogramas.md:12 (Similaridade: 0.68)
   "Prazo de execução não pode exceder prazo de validade da proposta."

   Contexto: Gestão de prazos em editais

---

💡 Dica: Resultados com ⭐ (≥0.85) têm alta confiança
📖 Para análise completa de edital, use /structure-edital e /analyze-edital
```

## Query Tips

**Good queries:**
- "prazo de validade de propostas Lei 8666"
- "requisitos câmera IP 4MP"
- "certificação INMETRO obrigatória"
- "garantia mínima equipamentos"

**Bad queries:**
- "prazo" (muito genérico)
- "8666" (apenas número)
- Single words without context

## Use Cases

- ✅ Quick lookup of specific information
- ✅ Verify legal requirements
- ✅ Check technical specifications
- ✅ Validate interpretations
- ❌ Not for full edital analysis (use `/structure-edital` + `/analyze-edital` for that)

## No Results Found

```
🔍 BUSCA RAG: "quantum flux capacitor"
==========================================

❌ Nenhum resultado relevante encontrado

A busca não retornou resultados com similaridade suficiente (>0.60).

Possíveis causas:
1. Termo não existe na base de conhecimento
2. Query muito específica ou técnica
3. Base de conhecimento precisa ser expandida

Sugestões:
- Tente termos mais genéricos
- Verifique se escreveu corretamente
- Use /help para ver o que a base contém
```

## Related Commands

- `/structure-edital <pdf>` - Extract requirements from edital
- `/analyze-edital <csv>` - Full conformity analysis with RAG
- `/help` - List all commands
