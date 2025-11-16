# Sprint 9 - Consolidação Arquitetural: PLANO

**Data de Criação:** 08 de novembro de 2025
**Sprint:** 9 (Fase 1 + Fase 2)
**Objetivo:** Consolidar arquitetura agent-as-prompts e validar sistema com edital real

---

## 🎯 Objetivos do Sprint

Sprint 9 consolida o sistema BidAnalyzee em duas fases:

### Fase 1 - Consolidação Arquitetural
Implementar as 3 prioridades do roadmap para atingir 100% de consistência:
1. **C.1** - Refatorar Document Structurer para agent-as-prompts
2. **A** - Implementar Modo Assistido (sugestões automáticas)
3. **D.1** - Adicionar comando de busca rápida

### Fase 2 - Validação e Testes
Validar o sistema com dados reais e implementar validações robustas:
4. **C.2** - Implementar validações robustas (PDF/CSV)
5. **E.2** - Executar teste end-to-end com edital real
6. **E.3** - Criar suite de testes abrangente (opcional)

---

## 📋 Fase 1 - Consolidação Arquitetural

### C.1 - Refatorar Document Structurer

**Objetivo:** Consolidar arquitetura agent-as-prompts em todos os agentes

**Por quê:**
- Consistência arquitetural (Technical Analyst e Orchestrator já são agent-as-prompts)
- Raciocínio LLM superior a código mecânico
- Facilita manutenção e evolução

**Implementação:**
1. Criar `agents/document_structurer/prompt.md`
   - Instruções detalhadas para extração de requisitos
   - SHIELD framework (S-H-I-E-L-L.5-D)
   - Exemplos de extração
   - Tratamento de edge cases

2. Criar `agents/document_structurer/checklists/`
   - `inspect.yaml` - Validação durante extração
   - `validate.yaml` - Validação final do CSV

3. Refatorar `/structure-edital` command
   - Carregar prompt do agente
   - Claude executa extração seguindo prompt
   - Python apenas para parsing PDF (pdfplumber) e validação

4. Documentação
   - `agents/document_structurer/README.md`
   - Atualizar exemplos

**Esforço Estimado:** 3-4 horas
**Benefício:** Consistência arquitetural, melhor qualidade de extração
**Dependências:** Nenhuma

**Critérios de Aceitação:**
- [ ] Prompt completo (~750+ linhas)
- [ ] Checklists SHIELD (~48+ items)
- [ ] `/structure-edital` usa agent-as-prompts
- [ ] Documentação atualizada
- [ ] Teste com edital real passa (Fase 2 - E.2)

---

### A - Modo Assistido

**Objetivo:** Workflow mais fluido com sugestões automáticas de próximos passos

**Por quê:**
- Reduz fricção (usuário não precisa pensar no próximo comando)
- Mantém controle (usuário ainda aprova cada passo)
- Melhora UX significativamente

**Implementação:**
1. Atualizar `agents/orchestrator/prompt.md`
   - Adicionar seção "Modo Assistido"
   - Instruções para detectar estado e sugerir próximo passo
   - Templates de sugestões

2. Criar lógica de transição automática
   ```
   Após Document Structurer completar:
   "✅ Extração completa! 50 requisitos extraídos.

   📋 Próximo passo sugerido: Análise de conformidade
   Comando: /analyze-edital data/.../requirements.csv

   Deseja prosseguir? (s/n/personalizar)"
   ```

3. Atualizar checklists
   - Adicionar items para "suggestion quality"
   - Validar se sugestão é apropriada

4. Criar `/workflow-assistido` command (opcional)
   - Inicia workflow assistido
   - A cada conclusão de stage, sugere próximo

**Esforço Estimado:** 4-6 horas
**Benefício:** UX muito melhor, workflow 50% mais rápido
**Dependências:** Nenhuma (mas melhor após C.1)

**Critérios de Aceitação:**
- [ ] Orchestrator sugere próximos passos automaticamente
- [ ] Sugestões incluem comando exato a executar
- [ ] Usuário pode aceitar (s), rejeitar (n), ou personalizar
- [ ] Funciona para workflow completo (extração → análise → relatório)
- [ ] Documentação atualizada

---

### D.1 - Comando de Busca Rápida

**Objetivo:** Consulta RAG pontual sem análise completa

**Por quê:**
- Útil para perguntas rápidas ("O que diz a Lei 8.666 sobre marcas?")
- Não requer análise completa
- Aproveita knowledge base existente

**Implementação:**
1. Criar comando `*buscar "<query>"`
   - Executa busca RAG
   - Retorna top 5 resultados
   - Formata resposta de forma clara

2. Adicionar ao Orchestrator
   ```markdown
   ### `*buscar "<query>"`

   Busca rápida na base de conhecimento

   Exemplo:
   *buscar "prazo validade proposta licitação"

   Resultado:
   📚 RESULTADOS DA BUSCA (5 encontrados)

   [1] Lei 8.666/93:120 (similaridade: 0.92)
   "O prazo de validade das propostas será de 60 dias..."

   [2] Lei 14.133/2021:89 (similaridade: 0.87)
   "A validade da proposta não poderá ser inferior a..."
   ```

3. Integrar com rag_search.py existente
   - Usar script Python já implementado
   - Apenas criar interface de comando

4. Documentação
   - Adicionar ao README do Orchestrator
   - Exemplos de uso

**Esforço Estimado:** 2-3 horas
**Benefício:** Nova funcionalidade útil, aproveita infra existente
**Dependências:** Nenhuma

**Critérios de Aceitação:**
- [ ] Comando `*buscar "<query>"` funcional
- [ ] Retorna top 5 resultados formatados
- [ ] Mostra similaridade de cada resultado
- [ ] Cita fonte (documento:linha)
- [ ] Documentação com exemplos

---

## 📋 Fase 2 - Validação e Testes

### C.2 - Validações Robustas

**Objetivo:** Garantir qualidade de inputs antes do processamento

**Por quê:**
- Prevenir erros (PDFs corrompidos, CSVs malformados)
- Feedback claro ao usuário
- Evitar desperdício de processamento

**Implementação:**
1. Criar `scripts/validate_pdf.py`
   - Verificar magic bytes (%PDF-)
   - Verificar integridade (pode abrir?)
   - Verificar tamanho razoável
   - Verificar número de páginas
   - Verificar se tem texto extraível
   - CLI: `python3 scripts/validate_pdf.py --input edital.pdf`

2. Expandir `scripts/validate_csv.py`
   - Detectar tipo automaticamente (structurer vs analyst)
   - Validar encoding (UTF-8)
   - Validar campos obrigatórios
   - Validar valores de domínio (Criticidade, Obrigatoriedade, Veredicto)
   - Validar ranges (Confiança 0.0-1.0)
   - Validar Quantidade (positivo ou N/A)

3. Integrar com checklists SHIELD
   - Adicionar validação no início de cada workflow
   - HALT se validação falhar

4. Documentação
   - Adicionar exemplos aos READMEs
   - Documentar cada tipo de validação

**Esforço Estimado:** 3-4 horas
**Benefício:** Previne 80% dos erros de processamento
**Dependências:** Nenhuma

**Critérios de Aceitação:**
- [ ] `validate_pdf.py` com 5+ checks
- [ ] `validate_csv.py` com auto-detecção de tipo
- [ ] Validação de todos os campos obrigatórios
- [ ] Mensagens de erro claras
- [ ] Integrado com workflows dos agentes

---

### E.2 - Teste End-to-End com Edital Real

**Objetivo:** Validar sistema completo com dados reais

**Por quê:**
- Descobrir edge cases não previstos
- Validar qualidade em cenário real
- Aumentar confiança no sistema
- Documentar findings para melhorias

**Implementação:**
1. Obter edital real de licitação pública
   - Baixar de portal de licitações (ex: ComprasNet, BNC)
   - Preferir edital de TI/Hardware (mais requisitos técnicos)
   - Tamanho: 20-50 páginas

2. Executar workflow completo
   - Fase 1: Validar PDF (`validate_pdf.py`)
   - Fase 2: Extrair requisitos (`/structure-edital`)
   - Fase 3: Validar CSV extração (`validate_csv.py`)
   - Fase 4: Analisar conformidade (`/analyze-edital`)
   - Fase 5: Validar CSV análise (`validate_csv.py`)

3. Revisar resultados manualmente
   - Verificar completude (todos requisitos extraídos?)
   - Verificar qualidade (análise faz sentido?)
   - Verificar fundamentação legal (evidências corretas?)
   - Identificar falsos positivos/negativos

4. Documentar findings
   - Criar `E2_TEST_RESULTS.md`
   - Métricas quantitativas
   - Problemas identificados
   - Recomendações de melhoria

**Esforço Estimado:** 4-6 horas
**Benefício:** Validação real, descobrir edge cases
**Dependências:** Fase 1 completa (especialmente C.1 e C.2)

**Critérios de Aceitação:**
- [ ] Edital real obtido e processado
- [ ] Workflow completo executado sem erros críticos
- [ ] Resultados revisados manualmente
- [ ] Métricas documentadas (completude, precisão, qualidade)
- [ ] Findings documentados em `E2_TEST_RESULTS.md`

---

### E.3 - Suite de Testes Abrangente (Opcional)

**Objetivo:** Criar testes automatizados para validações e edge cases

**Por quê:**
- Prevenir regressões
- Validar edge cases automaticamente
- Aumentar confiança em mudanças futuras

**Implementação:**
1. Criar `tests/e2e/test_complex_editais.py`
   - Testar validações de PDF (arquivo inexistente, corrompido, etc.)
   - Testar validações de CSV (malformado, valores inválidos, etc.)
   - Testar edge cases (requisitos muito longos, caracteres especiais, etc.)

2. Casos de teste
   - **PDF:** válido, inválido, corrompido, vazio, muito grande
   - **CSV Structurer:** válido, Criticidade inválida, Quantidade negativa, campos vazios
   - **CSV Analyst:** válido, Veredicto inválido, Confiança fora do range
   - **Integração:** validar se arquivo real passa validações

3. Usar pytest
   - Fixtures para arquivos de teste
   - Parametrização para múltiplos casos
   - Assertions claras

4. CI/CD (futuro)
   - Executar testes em PRs
   - Badge de status no README

**Esforço Estimado:** 4-6 horas
**Benefício:** Qualidade garantida, previne regressões
**Dependências:** C.2 (validações) implementado

**Critérios de Aceitação:**
- [ ] 15+ testes automatizados
- [ ] Edge cases cobertos
- [ ] Todos os testes passando
- [ ] Documentação de como executar
- [ ] Integrado com pytest

---

## 📊 Resumo de Esforço

### Fase 1 - Consolidação

| Item | Esforço | Prioridade |
|------|---------|------------|
| C.1 - Document Structurer | 3-4h | ⭐⭐⭐ |
| A - Modo Assistido | 4-6h | ⭐⭐⭐ |
| D.1 - Busca Rápida | 2-3h | ⭐⭐⭐ |
| **Total Fase 1** | **9-13h** | - |

### Fase 2 - Validação

| Item | Esforço | Prioridade |
|------|---------|------------|
| C.2 - Validações | 3-4h | ⭐⭐ |
| E.2 - Teste Real | 4-6h | ⭐⭐ |
| E.3 - Suite Testes | 4-6h | ⭐ (opcional) |
| **Total Fase 2** | **11-16h** | - |

**Total Sprint 9:** 20-29 horas

---

## 🎯 Objetivos de Sucesso

### Fase 1 é bem-sucedida quando:
- [x] Todos os 3 agentes usam agent-as-prompts (100% consistência)
- [x] Modo Assistido reduz fricção em workflows
- [x] Comando *buscar funciona para consultas rápidas
- [x] Documentação completa e atualizada

### Fase 2 é bem-sucedida quando:
- [x] Validações previnem inputs inválidos
- [x] Edital real processado com sucesso
- [x] Qualidade da análise é alta (>80% precisão)
- [x] Findings documentados para melhorias

### Sprint 9 completo é bem-sucedido quando:
- [x] **Arquitetura 100% consolidada**
- [x] **Sistema validado com dados reais**
- [x] **Qualidade garantida por validações**
- [x] **UX significativamente melhorado**
- [x] **Zero bugs críticos conhecidos**

---

## 📈 Métricas de Sucesso

### Quantitativas

| Métrica | Target | Como Medir |
|---------|--------|------------|
| Consistência Arquitetural | 100% (3/3 agentes) | Todos usam agent-as-prompts |
| Qualidade Documentação | >15KB prompts | wc -l agents/*/prompt.md |
| Cobertura Checklists | >100 items | Total de checklists SHIELD |
| Validações Implementadas | >10 checks | validate_pdf + validate_csv |
| Testes Automatizados | >15 testes | pytest --collect-only |
| Taxa de Sucesso E.2 | >80% | Requisitos corretos / Total |

### Qualitativas

- [ ] Código é mais fácil de manter (agent-as-prompts > Python)
- [ ] UX é mais fluida (Modo Assistido)
- [ ] Usuário tem confiança no sistema (teste real + validações)
- [ ] Documentação é compreensível por novo desenvolvedor
- [ ] Sistema está pronto para uso real

---

## 🚀 Próximos Passos Após Sprint 9

Após Sprint 9 completo, próximas prioridades são:

### Imediato (Sprint 10)
- **B - Modo FLOW:** Automação completa (one-command analysis)
- **D.2 - Export PDF/Excel:** Outputs profissionais

### Curto Prazo (1 mês)
- **C.3 - State Management:** Persistência de sessões
- **C.4 - Documentação de Uso:** USER_GUIDE completo

### Médio Prazo (2-3 meses)
- **D.3 - Dashboard:** Métricas consolidadas
- **E.1 - Testes Automatizados:** Coverage >80%
- **E.4 - CI/CD:** GitHub Actions

---

## 📋 Checklist de Início

Antes de iniciar Sprint 9, verificar:

- [x] Sprint 8 está completo (Orchestrator Base)
- [x] Technical Analyst funcional (Sprint 7)
- [x] RAG Engine funcional (Sprint 5)
- [x] Knowledge Base indexada
- [x] ROADMAP atualizado
- [x] Ambiente de desenvolvimento pronto

---

## 📋 Checklist de Conclusão

Sprint 9 está completo quando:

### Fase 1
- [ ] C.1 - Document Structurer refatorado e testado
- [ ] A - Modo Assistido implementado e documentado
- [ ] D.1 - Comando *buscar funcional
- [ ] Todos os 3 agentes usam agent-as-prompts
- [ ] Documentação atualizada

### Fase 2
- [ ] C.2 - Validações implementadas e testadas
- [ ] E.2 - Edital real processado com sucesso
- [ ] E.3 - Suite de testes criada (opcional)
- [ ] Findings documentados
- [ ] SPRINT_9_STATUS.md criado

### Finalização
- [ ] Testes passando
- [ ] Commits organizados
- [ ] PR criada e revisada
- [ ] ROADMAP atualizado
- [ ] PROJECT_STATUS.md atualizado

---

## 🔄 Processo de Execução

### Dia 1 - Consolidação (C.1)
1. Criar estrutura `agents/document_structurer/`
2. Escrever prompt.md com SHIELD framework
3. Criar checklists (inspect.yaml + validate.yaml)
4. Escrever README.md
5. Testar extração básica

### Dia 2 - UX (A + D.1)
1. Atualizar Orchestrator prompt (Modo Assistido)
2. Criar templates de sugestões
3. Adicionar comando *buscar
4. Testar workflows assistidos
5. Atualizar documentação

### Dia 3 - Validações (C.2)
1. Criar validate_pdf.py (6 checks)
2. Expandir validate_csv.py (auto-detect)
3. Testar com arquivos válidos e inválidos
4. Integrar com workflows
5. Documentar uso

### Dia 4 - Teste Real (E.2)
1. Obter edital real
2. Executar workflow completo
3. Revisar resultados manualmente
4. Documentar findings
5. Criar E2_TEST_RESULTS.md

### Dia 5 - Testes Automatizados (E.3 - Opcional)
1. Criar test_complex_editais.py
2. Implementar casos de teste
3. Executar pytest
4. Corrigir falhas
5. Documentar coverage

---

## 📝 Notas de Implementação

### Princípios a Seguir:
1. **SHIELD Framework** em todos os agentes
2. **Agent-as-prompts** como padrão (Python só para infra)
3. **Documentação completa** antes de código
4. **Testes com dados reais** sempre que possível
5. **Validações primeiro** (fail fast)

### Armadilhas a Evitar:
- ❌ Voltar para Python mecânico (manter agent-as-prompts)
- ❌ Testes superficiais (usar edital real complexo)
- ❌ Validações fracas (cobrir edge cases)
- ❌ Documentação insuficiente (exemplos reais)
- ❌ Otimização prematura (funcionalidade > performance)

---

**Criado por:** Claude
**Data:** 08 de novembro de 2025
**Versão:** 1.0
**Status:** Plano aprovado, execução iniciada

**Ver:** `SPRINT_9_STATUS.md` para status de implementação
