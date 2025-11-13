# GUARDRAILS - BidAnalyzee

**Última Atualização:** 08/11/2025
**Sprint:** 9 Fase 2

---

## 🚨 GUARDRAILS CRÍTICOS

### 1. EDITAIS PÚBLICOS: COMPLETUDE 100% OBRIGATÓRIA

**Regra:** Em editais de licitação pública, **TODOS os requisitos técnicos devem ser extraídos e analisados, sem exceção**.

**Proibido:**
- ❌ Extração "representativa" ou "amostral"
- ❌ Filtrar requisitos por "criticidade"
- ❌ Decidir quais requisitos são "mais importantes"
- ❌ Pular seções ou anexos
- ❌ Assumir que alguns requisitos são "opcionais"

**Obrigatório:**
- ✅ Extrair **100% dos requisitos** de todas as páginas
- ✅ Processar **todos os anexos** técnicos
- ✅ Incluir **especificações detalhadas** completas
- ✅ Manter **rastreabilidade total** (página + contexto)
- ✅ Documentar **qualquer requisito não extraído** como falha

**Razão:** Licitações públicas são regidas por lei. Qualquer requisito não analisado pode resultar em:
- Desclassificação da proposta
- Perda de concorrência
- Prejuízo financeiro
- Problemas jurídicos

**Aplicável a:**
- Document Structurer Agent
- Technical Analyst Agent
- Orchestrator Agent
- Qualquer processo de análise de editais

---

### 2. ANTI-ALUCINAÇÃO: RASTREABILIDADE OBRIGATÓRIA

**Regra:** TODO requisito extraído DEVE ter rastreabilidade ao documento original.

**Obrigatório:**
- ✅ Número da página de origem
- ✅ Seção/item/número do edital
- ✅ Contexto (±2 sentenças)
- ✅ Transcrição literal (quando aplicável)

**Proibido:**
- ❌ Inferir requisitos não explicitamente escritos
- ❌ Parafrasear sem manter sentido original
- ❌ Adicionar interpretações pessoais
- ❌ Inventar especificações técnicas

---

### 3. CONFORMIDADE LEGAL: SEM INTERPRETAÇÃO

**Regra:** Análise de conformidade deve ser baseada em **fatos e evidências**, não em interpretações.

**Obrigatório:**
- ✅ Citar evidências literais da Knowledge Base
- ✅ Apresentar raciocínio objetivo
- ✅ Marcar como "REVISAO" quando houver dúvida
- ✅ Documentar fontes e referências

**Proibido:**
- ❌ Assumir conformidade sem evidência
- ❌ Interpretar normas sem base legal
- ❌ Inferir conformidade por similaridade
- ❌ Dar veredicto sem raciocínio completo

---

### 4. PROCESSAMENTO COMPLETO: SEM ATALHOS

**Regra:** Documentos grandes exigem processamento automatizado, não manual parcial.

**Para editais >50 páginas:**
- ✅ Usar processamento automatizado (Python + PyPDF2)
- ✅ Validar 100% de extração
- ✅ Reportar métricas quantitativas (total vs extraído)
- ✅ Documentar qualquer limitação técnica

**Proibido:**
- ❌ Processar "até onde for possível"
- ❌ Justificar incompletude por tamanho
- ❌ Usar "representatividade" como desculpa
- ❌ Omitir requisitos técnicos

---

### 5. MÉTRICAS SHIELD: 100% É O MÍNIMO

**Regra:** Todas as 4 métricas quantitativas SHIELD devem ser 100%.

**Métricas Obrigatórias:**
1. **Completeness** = 100% (items_in_csv / items_in_pdf)
2. **Integrity** = 100% (fields_filled / total_fields)
3. **Consistency** = 100% (valid_values / total_values)
4. **Traceability** = 100% (items_with_source / total_items)

**Se qualquer métrica < 100%:**
- ❌ CSV é INVÁLIDO
- ❌ Processo deve ser refeito
- ❌ HALT e reportar erro

---

### 6. VALIDAÇÃO: AUTOMÁTICA E RIGOROSA

**Regra:** Validações devem ser automáticas e rigorosas, sem exceções.

**Obrigatório:**
- ✅ `validate_pdf.py` antes de processar
- ✅ `validate_csv.py` após gerar output
- ✅ Checklists SHIELD completos
- ✅ Métricas quantitativas calculadas

**Modo Strict:**
- ✅ Warnings tratados como erros
- ✅ Zero tolerância para dados inválidos
- ✅ Falha rápida (fail-fast)

---

### 7. DOCUMENTAÇÃO: TRANSPARÊNCIA TOTAL

**Regra:** TODO processo deve ser documentado com transparência total.

**Obrigatório:**
- ✅ Documentar decisões e critérios
- ✅ Registrar limitações técnicas
- ✅ Reportar falhas e erros
- ✅ Manter auditoria completa (timestamps, versões)

**Proibido:**
- ❌ Ocultar limitações
- ❌ Justificar incompletude
- ❌ Omitir erros ou falhas

---

## 🔧 IMPLEMENTAÇÃO

### Como Aplicar Guardrails

**1. Em Prompts de Agentes:**
```markdown
🚨 GUARDRAIL CRÍTICO:
Em editais públicos, você DEVE extrair 100% dos requisitos técnicos.
Extração parcial ou "representativa" é PROIBIDA.
Se o documento for muito grande, solicite processamento automatizado.
```

**2. Em Checklists SHIELD:**
```yaml
- id: "GUARD-01"
  check: "100% dos requisitos do PDF foram extraídos?"
  critical: true
  guardrail: true
  failure_action: "HALT e reportar falha"
```

**3. Em Scripts de Validação:**
```python
# validate_csv.py
if completeness < 1.0:
    errors.append(f"GUARDRAIL VIOLATION: Only {completeness*100}% completeness. 100% required for public procurement.")
    return False, errors
```

**4. Em Documentação:**
```markdown
⚠️ IMPORTANTE: Este é um edital público. 100% dos requisitos devem ser analisados conforme GUARDRAILS.md
```

---

## 📊 COMPLIANCE CHECK

Antes de finalizar qualquer análise, verificar:

- [ ] Completude = 100%?
- [ ] Todos os anexos processados?
- [ ] Rastreabilidade total mantida?
- [ ] Validações automáticas passaram?
- [ ] Métricas SHIELD = 100%?
- [ ] Documentação completa?
- [ ] Sem interpretações ou inferências?

**Se qualquer item = NÃO → HALT e reportar**

---

## 🎯 CONSEQUÊNCIAS DE VIOLAÇÃO

**Violação de Guardrails resulta em:**
1. ❌ Output marcado como INVÁLIDO
2. ❌ Processo deve ser reiniciado
3. ❌ Documentação de falha obrigatória
4. ❌ Escalação para revisão humana

**Zero tolerância para:**
- Incompletude em editais públicos
- Alucinação de requisitos
- Interpretação sem base legal
- Omissão de falhas ou limitações

---

**Status:** ✅ ATIVO
**Aplicável a:** Todos os agentes e processos
**Última Revisão:** 08/11/2025
**Mantido por:** Equipe + Claude

---

**⚠️ ESTES GUARDRAILS SÃO INVIOLÁVEIS E DEVEM SER APLICADOS EM 100% DOS CASOS**
