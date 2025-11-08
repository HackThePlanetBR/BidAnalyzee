# BidAnalyzee - Roadmap de Desenvolvimento

**Última Atualização:** 08 de novembro de 2025
**Status Atual:** Sprint 8 Completo - Orchestrator Base implementado
**Próximas Prioridades:** C.1 → A → D.1

---

## 📊 Estado Atual do Projeto

### ✅ Completado (100%)

**Sprint 5 - RAG & Query Processor**
- [x] História 5.1 - RAG Setup (FAISS + sentence-transformers)
- [x] História 5.2 - Query Processor (análise mecânica - posteriormente refatorado)
- [x] História 5.3 - Pipeline Integration (end-to-end)

**Sprint 7 - Technical Analyst Refactoring**
- [x] Refatorar Query Processor → Technical Analyst (agent-as-prompts)
- [x] Criar prompt completo com SHIELD framework (17KB)
- [x] Criar checklists SHIELD (inspect + validate, 68 items)
- [x] RAG search via scripts Python (`rag_search.py`)

**Sprint 8 - Orchestrator Base**
- [x] Prompt do Orchestrator (17KB, SHIELD framework)
- [x] Checklists SHIELD (68 items: 28 inspect + 40 validate)
- [x] Comandos de sistema (`*ajuda`, `*listar_analises`, `*sessao`)
- [x] Gestão de estado (design JSON)
- [x] Documentação completa (README 8KB)

### 🏗️ Arquitetura Atual

**Agentes Implementados:**
1. ✅ **@DocumentStructurer** - Extração de requisitos de PDFs (Python-based)
2. ✅ **@AnalistaTecnico** - Análise de conformidade (agent-as-prompts)
3. ✅ **@Orquestrador** - Coordenação de workflows (agent-as-prompts)

**Infraestrutura:**
- ✅ RAG Engine (FAISS + sentence-transformers)
- ✅ Knowledge Base (mock documents Lei 8.666, 14.133, requisitos técnicos)
- ✅ Python utilities (rag_search.py, validate_csv.py)
- ✅ Slash commands (/structure-edital, /analyze-edital)

---

## 🎯 Roadmap - Próximas Etapas

### 🔴 PRIORIDADE 1: Opção C.1 - Refatorar Document Structurer

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
- [ ] Prompt completo (~800+ linhas)
- [ ] Checklists SHIELD (~50+ items)
- [ ] `/structure-edital` usa agent-as-prompts
- [ ] Documentação atualizada
- [ ] Teste com edital real passa

---

### 🟠 PRIORIDADE 2: Opção A - Sprint 9 (Modo Assistido)

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

4. Criar `/workflow-assistido` command
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

### 🟡 PRIORIDADE 3: Opção D.1 - Comando de Busca Rápida

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

## 🔮 Roadmap Futuro (Após Prioridades 1-3)

### Opção B - Sprint 10 (Modo FLOW - Automação Completa)

**Objetivo:** Análise completa com um único comando, execução automática

**Descrição:**
- Comando: `/analyze-edital-full <pdf>`
- Executa automaticamente: Extração → Análise → Relatório
- HALT apenas em pontos críticos (erros, decisões importantes)
- Checkpoints de progresso (não bloqueantes)

**Implementação:**
1. Criar `/analyze-edital-full` command
2. Atualizar Orchestrator para modo FLOW
3. Definir checkpoints críticos (onde pausar)
4. Implementar recuperação automática de erros (retry)
5. Progress bar ou indicador de progresso

**Esforço Estimado:** 8-12 horas
**Benefício:** Experiência "one-click", ideal para usuários avançados
**Dependências:** Melhor após A (Modo Assistido)

**Critérios de Aceitação:**
- [ ] `/analyze-edital-full <pdf>` executa workflow completo
- [ ] Pausas apenas em erros ou decisões críticas
- [ ] Progress bar mostra andamento
- [ ] Logs detalhados de cada stage
- [ ] Recuperação automática de erros comuns
- [ ] Tempo total < 5 minutos para edital típico

---

### Opção C - Melhorias no Sistema Atual

#### C.1 - Refatorar Document Structurer ⭐ PRIORIDADE 1 (detalhado acima)

#### C.2 - Adicionar Validações Robustas

**Descrição:**
- Validar PDFs antes de processar (não corrompido, tem texto)
- Validar CSVs com mais rigor (encoding, duplicatas, campos vazios)
- Validar knowledge base (documentos completos, índice consistente)

**Implementação:**
- Criar `scripts/validate_pdf.py`
- Expandir `scripts/validate_csv.py`
- Criar `scripts/validate_knowledge_base.py`
- Adicionar validações nos checklists SHIELD

**Esforço:** 3-4 horas

#### C.3 - Criar Utilitários para Gestão de Estado

**Descrição:**
- Scripts Python para criar/ler/atualizar sessões JSON
- Utilitário para limpar sessões antigas
- Backup/restore de estado

**Implementação:**
- `src/orchestrator/state_manager.py`
- `src/orchestrator/session.py`
- CLI para operações (`python -m src.orchestrator.cli session list`)

**Esforço:** 4-6 horas

#### C.4 - Melhorar Documentação de Uso

**Descrição:**
- Criar USER_GUIDE.md (guia completo para usuários)
- Criar FAQ.md (perguntas frequentes)
- Tutorial passo-a-passo com screenshots/exemplos

**Implementação:**
- `docs/USER_GUIDE.md`
- `docs/FAQ.md`
- `docs/TUTORIAL.md`
- Adicionar diagramas (mermaid)

**Esforço:** 4-6 horas

#### C.5 - Adicionar Mais Exemplos na Knowledge Base

**Descrição:**
- Adicionar mais documentos mock
- Cobrir mais cenários (licitações de TI, obras, serviços)
- Adicionar jurisprudência TCU/TCE

**Implementação:**
- Expandir `data/knowledge_base/mock_documents/`
- Criar `jurisprudencia_tcu.md`
- Criar `requisitos_ti_avancados.md`
- Re-indexar knowledge base

**Esforço:** 3-5 horas

---

### Opção D - Funcionalidades Novas

#### D.1 - Comando de Busca Rápida ⭐ PRIORIDADE 3 (detalhado acima)

#### D.2 - Exportar para PDF/Excel

**Descrição:**
- Gerar relatório PDF profissional (além do CSV)
- Exportar para Excel com formatação
- Templates customizáveis

**Implementação:**
- Usar `reportlab` ou `weasyprint` para PDF
- Usar `openpyxl` para Excel
- Criar templates em `templates/`
- Adicionar ao workflow final do Orchestrator

**Esforço:** 6-8 horas
**Benefício:** Outputs mais profissionais

#### D.3 - Dashboard de Métricas

**Descrição:**
- Painel consolidado de estatísticas
- Métricas de múltiplas análises
- Visualizações (gráficos de conformidade, tendências)

**Implementação:**
- Criar `scripts/dashboard.py`
- Web UI (Streamlit ou Dash) ou terminal (Rich)
- Agregar dados de `data/state/sessions/`
- Gráficos: taxa de conformidade, categorias mais problemáticas, etc.

**Esforço:** 8-12 horas
**Benefício:** Insights valiosos, análise de tendências

#### D.4 - Comparação de Editais

**Descrição:**
- Analisar 2+ editais e comparar requisitos
- Identificar diferenças críticas
- Gerar relatório de comparação

**Implementação:**
- Criar `agents/comparator/` (novo agente)
- Lógica de diff entre CSVs de requisitos
- Identificar requisitos únicos, divergentes, comuns
- Relatório de comparação

**Esforço:** 10-16 horas
**Benefício:** Útil para empresas que participam de múltiplas licitações

#### D.5 - Sistema de Templates

**Descrição:**
- Salvar configurações de análise (quais validações, threshold RAG, etc.)
- Reutilizar templates em análises futuras
- Templates pré-definidos (TI, Obras, Serviços)

**Implementação:**
- Criar `data/templates/`
- Schema de template (YAML/JSON)
- Comando `*carregar_template <nome>`
- Templates default incluídos

**Esforço:** 5-8 horas
**Benefício:** Padronização, eficiência

---

### Opção E - Testes e Qualidade

#### E.1 - Testes Automatizados para Agents

**Descrição:**
- Testes de prompts (verificar se agentes seguem instruções)
- Testes de checklists (garantir cobertura)
- Mocking de interações

**Implementação:**
- Criar `tests/agents/test_technical_analyst.py`
- Criar `tests/agents/test_orchestrator.py`
- Criar `tests/agents/test_document_structurer.py`
- Usar pytest + fixtures

**Esforço:** 8-12 horas
**Benefício:** Confiança, detectar regressões

#### E.2 - Teste End-to-End com Edital Real

**Descrição:**
- Obter edital real de licitação pública
- Executar workflow completo
- Validar resultados manualmente
- Documentar findings

**Implementação:**
- Baixar edital de portal de licitações
- Executar `/structure-edital` → `/analyze-edital`
- Revisar análise manualmente (especialista)
- Documentar em `tests/e2e/EDITAL_REAL_TEST.md`

**Esforço:** 4-6 horas
**Benefício:** Validação real, descobrir edge cases

#### E.3 - Validação de Outputs

**Descrição:**
- Scripts robustos de validação
- Verificação automática de qualidade
- Alertas para outputs suspeitos

**Implementação:**
- Expandir `scripts/validate_csv.py`
- Criar `scripts/quality_check.py`
- Métricas: completude, consistência, raciocínio adequado
- Integrar com checklists VALIDATE

**Esforço:** 4-6 horas
**Benefício:** Qualidade garantida

#### E.4 - CI/CD Setup

**Descrição:**
- GitHub Actions para testes automáticos
- Linting (ruff, black)
- Type checking (mypy)
- Coverage reports

**Implementação:**
- Criar `.github/workflows/ci.yml`
- Setup de linters e formatters
- Executar testes em PRs
- Badge de status no README

**Esforço:** 3-5 horas
**Benefício:** Qualidade contínua, evitar bugs

---

## 📅 Timeline Proposta

### Fase 1 - Consolidação Arquitetural (Sprint 9)
**Duração:** 1-2 semanas

1. **Semana 1:**
   - ✅ C.1 - Refatorar Document Structurer (3-4h)
   - ✅ A - Modo Assistido (4-6h)
   - ✅ D.1 - Busca Rápida (2-3h)
   - **Total:** ~10-13 horas

2. **Semana 2 (se necessário):**
   - C.2 - Validações Robustas (3-4h)
   - E.2 - Teste End-to-End Real (4-6h)
   - **Total:** ~7-10 horas

**Entregável:** Sistema consolidado, testado, pronto para uso real

---

### Fase 2 - Automação e UX (Sprint 10)
**Duração:** 1-2 semanas

1. **Semana 1:**
   - B - Modo FLOW (8-12h)
   - D.2 - Export PDF/Excel (6-8h)

2. **Semana 2:**
   - C.3 - Utilitários de Estado (4-6h)
   - C.4 - Documentação de Uso (4-6h)

**Entregável:** Sistema automático, outputs profissionais, bem documentado

---

### Fase 3 - Funcionalidades Avançadas (Sprint 11+)
**Duração:** 2-4 semanas

1. **Sprint 11:**
   - D.3 - Dashboard de Métricas (8-12h)
   - E.1 - Testes Automatizados (8-12h)

2. **Sprint 12:**
   - D.4 - Comparação de Editais (10-16h)
   - E.4 - CI/CD Setup (3-5h)

3. **Sprint 13:**
   - D.5 - Sistema de Templates (5-8h)
   - E.3 - Validação de Outputs (4-6h)
   - C.5 - Expandir Knowledge Base (3-5h)

**Entregável:** Sistema completo, enterprise-ready

---

## 🎯 Ordem de Execução Recomendada

### Imediato (Próximas 2 semanas):
1. ⭐⭐⭐ **C.1** - Refatorar Document Structurer
2. ⭐⭐⭐ **A** - Sprint 9 (Modo Assistido)
3. ⭐⭐⭐ **D.1** - Busca Rápida

### Curto Prazo (3-4 semanas):
4. ⭐⭐ **E.2** - Teste End-to-End Real
5. ⭐⭐ **C.2** - Validações Robustas
6. ⭐⭐ **B** - Sprint 10 (Modo FLOW)

### Médio Prazo (1-2 meses):
7. ⭐⭐ **D.2** - Export PDF/Excel
8. ⭐ **C.3** - Utilitários de Estado
9. ⭐ **C.4** - Documentação de Uso

### Longo Prazo (2-3 meses):
10. ⭐ **D.3** - Dashboard
11. ⭐ **E.1** - Testes Automatizados
12. **D.4** - Comparação de Editais
13. **D.5** - Templates
14. **E.3** - Validação Outputs
15. **E.4** - CI/CD

---

## 📊 Matriz de Priorização

| Item | Valor | Esforço | Prioridade | ROI |
|------|-------|---------|------------|-----|
| C.1 - Refactor Doc Structurer | Alto | Baixo | ⭐⭐⭐ | ★★★★★ |
| A - Modo Assistido | Alto | Médio | ⭐⭐⭐ | ★★★★☆ |
| D.1 - Busca Rápida | Médio | Baixo | ⭐⭐⭐ | ★★★★☆ |
| E.2 - Teste Real | Alto | Médio | ⭐⭐ | ★★★★☆ |
| C.2 - Validações | Médio | Médio | ⭐⭐ | ★★★☆☆ |
| B - Modo FLOW | Alto | Alto | ⭐⭐ | ★★★☆☆ |
| D.2 - PDF/Excel | Médio | Alto | ⭐⭐ | ★★★☆☆ |
| C.3 - Utilitários | Baixo | Médio | ⭐ | ★★☆☆☆ |
| C.4 - Docs | Médio | Médio | ⭐ | ★★★☆☆ |
| D.3 - Dashboard | Médio | Alto | ⭐ | ★★☆☆☆ |
| E.1 - Testes Auto | Alto | Alto | ⭐ | ★★★☆☆ |
| D.4 - Comparação | Baixo | Alto | - | ★☆☆☆☆ |
| D.5 - Templates | Baixo | Médio | - | ★★☆☆☆ |
| E.3 - Valid Outputs | Médio | Médio | - | ★★☆☆☆ |
| E.4 - CI/CD | Médio | Baixo | - | ★★★☆☆ |

---

## 🏆 Objetivos de Cada Fase

### Fase 1 - Consolidação (Sprint 9)
**Objetivo:** Sistema consistente, arquitetura agent-as-prompts completa, testado com edital real

**Sucesso medido por:**
- [x] Todos os 3 agentes usando agent-as-prompts
- [x] Workflow assistido funcional
- [x] Teste real com edital público passou
- [x] Zero bugs críticos conhecidos

---

### Fase 2 - Automação (Sprint 10)
**Objetivo:** UX excepcional, automação completa, outputs profissionais

**Sucesso medido por:**
- [x] Análise completa em < 5 minutos (one-command)
- [x] PDF report gerado automaticamente
- [x] 90%+ dos usuários conseguem usar sem ajuda

---

### Fase 3 - Enterprise (Sprint 11+)
**Objetivo:** Sistema production-ready, escalável, confiável

**Sucesso medido por:**
- [x] CI/CD configurado (testes passando)
- [x] Dashboard com insights valiosos
- [x] 10+ análises reais completadas com sucesso
- [x] < 5% taxa de erro

---

## 📝 Notas de Implementação

### Princípios a Manter:
1. **SHIELD Framework** em todos os agentes
2. **Agent-as-prompts** como padrão (Python só para infra)
3. **Documentação completa** (README + prompts + checklists)
4. **Governança via checklists** (não confiar só em código)
5. **User-centric** (HALT, feedback claro, transparência)

### Tecnologias:
- **Agents:** Markdown prompts + YAML checklists
- **Infrastructure:** Python 3.11+, FAISS, sentence-transformers
- **PDF:** pdfplumber
- **Validation:** Custom scripts
- **Testing:** pytest
- **CI/CD:** GitHub Actions

---

## 🔄 Processo de Atualização

Este roadmap deve ser revisado:
- **Mensalmente:** Verificar progresso, ajustar prioridades
- **Após cada Sprint:** Atualizar status, adicionar learnings
- **Quando novos requisitos surgirem:** Re-priorizar

**Última revisão:** 08/11/2025
**Próxima revisão:** 15/11/2025 (após Sprint 9)

---

**Mantido por:** Claude + Equipe
**Versão:** 1.0
