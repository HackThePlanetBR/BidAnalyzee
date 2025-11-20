# BidAnalyzee 🔍

**Sistema Inteligente de Análise de Conformidade de Editais com IA**

[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![Framework](https://img.shields.io/badge/framework-SHIELD%201.0-blue)]()
[![Tests](https://img.shields.io/badge/tests-116%2F116%20passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 📋 Visão Geral

BidAnalyzee é um sistema assistido por IA projetado para automatizar a análise de conformidade de editais públicos. Utilizando uma arquitetura avançada de **RAG (Retrieval-Augmented Generation)** governada pelo **Framework SHIELD**, o sistema valida cada requisito do edital contra uma base de conhecimento técnica, garantindo precisão, velocidade e confiabilidade.

### Problema Resolvido

Empresas que participam de licitações públicas enfrentam um processo manual, lento e sujeito a erros:
- ⏱️ **Horas de análise** por especialistas para cada edital
- ⚠️ **Alto risco de erros** que podem causar desqualificação
- 💰 **Custo elevado** de equipe técnica dedicada
- 📊 **Falta de auditabilidade** nas análises manuais

### Solução Proposta

Um sistema inteligente que:
- ✅ Reduz tempo de análise de dias para **< 1 hora**
- ✅ Garante **> 85% de precisão** com validação automática
- ✅ Oferece **rastreabilidade completa** de cada decisão
- ✅ Opera com **governança rigorosa** (Framework SHIELD)

---

## 🎯 Público-Alvo (MVP)

- **Analistas de Propostas / Engenheiros de Vendas:** Profissionais que precisam gerar matrizes de conformidade rapidamente
- **Gerentes Comerciais:** Líderes que tomam decisões estratégicas de Go/No-Go baseadas nas análises

**Setor Inicial:** Empresas de segurança eletrônica e videomonitoramento

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────┐
│  Interface (Claude Code + Slash Commands)       │
│  /iniciar-analise | /flow | /consulta-rapida   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Camada de Orquestração (@Orquestrador)         │
│  - Governança via Framework SHIELD              │
│  - Gestão de estado e workflows                 │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Agentes Especializados                         │
│  @EstruturadorDeDocumentos | @AnalistaTecnico   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Serviços de Dados                              │
│  n8n (Ingestão + Consulta) | Pinecone (Vetores)│
└─────────────────────────────────────────────────┘
```

### Framework SHIELD

Metodologia proprietária de governança que garante qualidade e confiabilidade:

- **S**TRUCTURE: Planejamento detalhado antes da execução
- **H**ALT: Pausas para aprovação do usuário
- **I**NSPECT: Auto-inspeção rigorosa com checklists
- **E**XECUTE: Execução controlada
- **L**OOP: Ciclos de refinamento
- **L.5** VALIDATE: Validação quantitativa (100% de completude)
- **D**ELIVER: Entrega formal com evidências

📖 **Documentação completa:** [OPERATING_PRINCIPLES.md](OPERATING_PRINCIPLES.md)

---

## 🚀 Funcionalidades

### ✅ Document Structurer (Implementado)
Agente especializado em extração e estruturação de requisitos de editais públicos:

**Funcionalidades Core:**
- 📄 **Extração de texto** de PDFs (até 500 páginas, 50MB)
- 🔍 **Identificação automática** de requisitos técnicos
- 📊 **Estruturação em CSV** com 7 campos padronizados
- ✅ **30 regras de validação** para conformidade legal

**Recursos Avançados (Sprint 4.5):**
- 🖼️ **OCR automático** para PDFs escaneados (Tesseract + português)
- 📋 **Extração de metadados** (10 campos) com confiança ponderada
- ⚡ **Cache inteligente** (105x mais rápido em cache hits)
- 🔄 **Processamento paralelo** (3.9x mais rápido)
- ⚖️ **Validação legal** (Lei 8.666/93, Lei 14.133/2021)

**Validação Rigorosa:**
- 8 regras Anti-Alucinação (AA-01 a AA-08)
- 8 regras de Estruturação (ED-01 a ED-08)
- 6 regras de Legal Compliance (LC-01 a LC-06)
- 4 regras de Completeness (CP-01 a CP-04)
- 4 regras de Consistency (CS-01 a CS-04)

**Comando:** `/structure-edital <caminho-do-pdf>`

### ✅ Modo Assistido (Implementado - Sprint 9)
Workflow completo com sugestões automáticas de próximos passos e checkpoints de aprovação.

**Funcionalidades:**
- 🔄 Sugestão automática do próximo passo após cada etapa
- ✅ Usuário mantém controle total (aprovar/rejeitar/personalizar)
- 📋 Detecção inteligente do estado do workflow
- 🎯 Reduz fricção - workflow 50% mais rápido

**Comando:** Integrado ao `@Orquestrador`

### ✅ Modo FLOW (Implementado - Sprint 10)
Execução automatizada de ponta a ponta com checkpoints críticos para usuários avançados.

**Funcionalidades:**
- 🚀 Workflow completo com um único comando
- ⚡ Automação de todas as fases (extração → análise → relatórios)
- 📊 Progress tracking em tempo real
- 💾 Gestão de estado integrada (SessionManager)
- ⏸️ Pausas apenas em erros ou decisões críticas

**Script:** `python3 scripts/analyze_edital_full.py <edital.pdf>`

### ✅ Modo Consulta Rápida (Implementado - Sprint 9)
Busca instantânea na base de conhecimento técnica sem análise completa.

**Funcionalidades:**
- 🔍 Busca RAG pontual com query em linguagem natural
- 📚 Top 5 resultados com score de similaridade
- 📖 Citação de fonte (documento:linha)
- ⭐ Destaque de resultados com alta confiança (≥0.85)

**Comando:** `*buscar "<query>"` via `@Orquestrador`

### ✅ Web Scrapers para Knowledge Base (Implementado - Nov 2025)
Scrapers automatizados para popular a base de conhecimento com documentação técnica da Genetec.

**Funcionalidades:**
- 🕷️ **3 scrapers prontos**: SCSaaS, Compliance Portal, TechDocs
- 🔄 **Automação completa**: Descoberta de URLs + extração + conversão Markdown
- 📝 **Frontmatter YAML**: Metadados estruturados (title, url, category, etc.)
- ⚙️ **Configurável via .env**: Proxy, headless mode, rate limiting
- 🌐 **Selenium integrado**: Bypass Cloudflare + renderização JavaScript
- 📊 **Estatísticas**: Tracking de URLs descobertas/processadas/extraídas

**Sites suportados:**
- ✅ Security Center SaaS Help (~500 artigos)
- ✅ Genetec Compliance Portal (~100 artigos)
- ✅ Genetec Technical Documentation (~800+ artigos)

**Script:** `python -m scripts.scrapers.scraper_orchestrator --sites all --selenium`

**Documentação:** [docs/scrapers/](docs/scrapers/)

### ✅ Exports Profissionais (Implementado - Sprint 10)
Geração automática de relatórios profissionais em múltiplos formatos.

**Funcionalidades PDF:**
- 📄 Capa executiva com resumo
- 📊 Tabelas formatadas de estatísticas
- 🎨 Seções por veredicto com código de cores
- 📐 Layout profissional (ReportLab)

**Funcionalidades Excel:**
- 📊 Múltiplas abas organizadas (Resumo, Detalhes, Filtrados)
- 🎨 Formatação condicional por veredicto
- 📈 Gráficos e visualizações automáticas
- 📏 Colunas auto-ajustadas e cabeçalhos fixos

**Scripts:**
- `python3 scripts/export_pdf.py <csv_path> [output_path]`
- `python3 scripts/export_excel.py <csv_path> [output_path]`

### ✅ Sistema de Templates (Implementado - Sprint 11)
Templates YAML reutilizáveis para configurações comuns de análise.

**Funcionalidades:**
- 📋 Templates pré-configurados por domínio (CFTV, TI, Obras)
- 🎯 Parâmetros customizáveis (threshold, top_k, veredictos)
- ⚡ Reutilização de configurações testadas
- 📦 Fácil compartilhamento entre equipes

**Localização:** `data/templates/*.yaml`

### ✅ Dashboard Interativo (Implementado - Sprint 11)
Dashboard CLI rico e interativo para visualização de análises.

**Funcionalidades:**
- 📊 Estatísticas visuais coloridas (Rich library)
- 🎨 Código de cores por veredicto
- 📈 Progress bars e tabelas formatadas
- 💾 Histórico de sessões
- 🔍 Navegação interativa entre análises

**Script:** `python3 scripts/dashboard.py`

### ✅ Validação de Outputs (Implementado - Sprint 11)
Sistema de scoring 0-100 para qualidade de análises.

**Funcionalidades:**
- 📊 6 dimensões de qualidade (Completude, Evidências, Consistência, etc.)
- 🎯 Score agregado ponderado (0-100 pontos)
- ⚠️ Alertas de qualidade (Excelente/Boa/Aceitável/Ruim)
- 📋 Recomendações automáticas de melhoria
- 📊 Relatórios detalhados de validação

**Script:** `python3 scripts/validate_output.py <csv_path>`
**Documentação:** [OUTPUT_VALIDATION.md](docs/OUTPUT_VALIDATION.md)

### ✅ Comparação de Editais (Implementado - Sprint 12)
Ferramenta para comparar múltiplos editais e identificar padrões.

**Funcionalidades:**
- 🔄 Comparação 1:1 ou N:N editais
- 🎯 Identificação de requisitos comuns/únicos
- 📊 Cálculo de % de overlap entre editais
- 🔍 Matching exato e similar (SequenceMatcher)
- 📄 Output em texto ou JSON

**Script:** `python3 scripts/compare_editais.py <edital1.csv> <edital2.csv> [...]`
**Documentação:** [COMPARISON.md](docs/COMPARISON.md)

### ✅ Testes Automatizados (Implementado - Sprint 12)
Suite completa de 116 testes cobrindo todos os agentes.

**Funcionalidades:**
- 🧪 116 tests (100% passing)
- 📦 Fixtures reutilizáveis (conftest.py)
- 🎯 Cobertura: Document Structurer (24), Technical Analyst (30), Orchestrator (35), SHIELD (27)
- ✅ Validação de prompts, SHIELD compliance, workflows
- 📊 Testes de integração E2E

**Execução:** `pytest tests/agents/ -v`
**Documentação:** [tests/agents/README.md](tests/agents/README.md)

---

## 📂 Estrutura do Projeto

```
BidAnalyzee/
├── .claude/                    # Claude Code configuration
│   └── commands/               # Slash commands (/iniciar-analise, etc.)
├── agents/                     # Agentes como prompts estruturados
│   ├── orchestrator/
│   ├── document_structurer/
│   └── technical_analyst/
├── framework/                  # SHIELD Framework
│   ├── SHIELD_PRINCIPLES.md
│   ├── phases/
│   ├── checklists/
│   └── templates/
├── workflows/                  # Definições de fluxos de trabalho
├── services/                   # Integrações (n8n, Pinecone)
├── data/                       # Dados e histórico
│   ├── analyses/               # Uma pasta por análise
│   ├── state/                  # Estado do sistema
│   └── templates/
├── scripts/                    # Scripts utilitários
├── tests/                      # Testes automatizados
├── docs/                       # Documentação técnica
├── IMPLEMENTATION_STRATEGY.md  # Estratégia de desenvolvimento
├── ARCHITECTURE_DECISIONS.md   # Decisões arquiteturais (ADRs)
├── OPERATING_PRINCIPLES.md     # Framework SHIELD
└── README.md                   # Este arquivo
```

---

## 📊 Métricas de Sucesso (MVP)

### KPIs Técnicos
- ⏱️ **Tempo de Análise:** < 1 hora (NFR1)
- 🎯 **Precisão:** > 85% sem revisão humana (NFR2)
- ⚠️ **Taxa de Revisão:** < 15% dos itens

### KPIs de Qualidade
- ✅ 100% das histórias implementadas com SHIELD completo
- 📝 Cobertura de testes > 80%
- 🔍 Zero erros críticos em produção (primeira semana)

### KPIs de Negócio
- 📄 Validação com 3 editais reais
- 👍 Feedback positivo do usuário piloto
- 💰 ROI demonstrável (tempo economizado)

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia | Propósito |
|------------|------------|-----------|
| **Interface** | Claude Code | Ambiente de desenvolvimento integrado |
| **Orquestração** | Prompts estruturados (YAML + Markdown) | Sistema de agentes |
| **Banco Vetorial** | FAISS (faiss-cpu) | Busca vetorial local ultra-rápida |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) | Embeddings multilíngue local (384d) |
| **RAG Framework** | LangChain | Orquestração de RAG pipeline |
| **Parsing** | Python (PyPDF2) | Extração de texto de documentos |
| **OCR** | Tesseract OCR + pytesseract | Texto de PDFs escaneados |
| **Imagens** | Pillow (PIL), pdf2image | Processamento de imagens |
| **Cache** | Disk-based cache (SHA256) | Performance optimization |
| **Persistência** | Sistema de arquivos (JSON, CSV, YAML) | Estado e histórico |
| **Reports** | ReportLab (PDF) + OpenPyXL (Excel) | Geração de relatórios profissionais |
| **Testes** | pytest (116 tests) | Testes unitários e integração |
| **Dashboard** | Rich library | Interface CLI interativa |

---

## 📖 Documentação

### Para Usuários
- 🚀 [Guia de Instalação](docs/INSTALLATION.md) - Setup rápido em 10-15 minutos
- 📘 [Guia do Usuário](docs/USER_GUIDE.md) - Guia completo de uso do sistema
- 🎓 [Tutorial Passo a Passo](docs/TUTORIAL.md) - Sua primeira análise de edital
- ❓ [FAQ - Perguntas Frequentes](docs/FAQ.md) - Dúvidas comuns e soluções
- ✅ [Validação de Outputs](docs/OUTPUT_VALIDATION.md) - Sistema de qualidade 0-100 pontos
- 🔄 [Comparação de Editais](docs/COMPARISON.md) - Guia de uso da ferramenta de comparação

### Para Desenvolvedores
- 📋 [Estratégia de Implementação](IMPLEMENTATION_STRATEGY.md) - Roadmap completo do projeto
- 🏛️ [Decisões Arquiteturais (ADRs)](ARCHITECTURE_DECISIONS.md) - Registros de decisões técnicas
- 🛡️ [Framework SHIELD](OPERATING_PRINCIPLES.md) - Metodologia de governança
- 🧪 [Documentação de Testes](tests/agents/README.md) - 116 testes automatizados

---

## 🗺️ Roadmap

### ✅ Fase 0: Fundação (Sprint 0) - **COMPLETO**
- [x] Estrutura de diretórios
- [x] Documentação do Framework SHIELD
- [x] Decisões arquiteturais documentadas
- [x] Templates de prompts e checklists
- [x] Configuração de ambiente

### ✅ Fase 1: Framework SHIELD (Sprint 1-2) - **COMPLETO**
- [x] Implementação das 7 fases do SHIELD
- [x] Templates reutilizáveis
- [x] Checklists de validação
- [x] Sistema de LOOP para refinamento

### ✅ Fase 2: Estruturação de Editais (Sprint 3-4) - **COMPLETO**
- [x] Parser de PDFs com PyPDF2
- [x] @EstruturadorDeDocumentos completo
- [x] Comando `/structure-edital`
- [x] Testes E2E e integração

### ✅ Fase 2.5: Melhorias Document Structurer (Sprint 4.5) - **COMPLETO**
- [x] OCR para PDFs escaneados (História 2.7)
- [x] Extração de metadados - 10 campos (História 2.8)
- [x] Cache e performance optimization (História 2.9)
- [x] 30 regras de validação legal (História 2.10)

### ✅ Fase 3: Análise de Conformidade (Sprint 5-7) - **COMPLETO**
- [x] Motor RAG (FAISS + sentence-transformers)
- [x] @AnalistaTecnico (agent-as-prompts)
- [x] Knowledge Base (Lei 8.666, 14.133, requisitos técnicos)
- [x] Scripts Python para RAG search

### ✅ Fase 4: Orquestração e UX (Sprint 8-10) - **COMPLETO**
- [x] @Orquestrador com Framework SHIELD (Sprint 8)
- [x] Modo Assistido com sugestões automáticas (Sprint 9)
- [x] Modo FLOW com automação completa (Sprint 10)
- [x] Modo Consulta Rápida (*buscar) (Sprint 9)
- [x] Exports Profissionais (PDF + Excel) (Sprint 10)
- [x] Comandos de sistema completos
- [x] Gestão de estado (SessionManager)

### ✅ Fase 5: Teste E2E e Refinamentos (Sprint 10.5) - **COMPLETO**
- [x] Teste E2E com edital real complexo
- [x] Suporte para múltiplos itens/seções
- [x] Seleção interativa de itens para análise
- [x] Validação agente vs documento original
- [x] Refinamentos baseados em casos reais

### ✅ Fase 6: Documentação e Qualidade (Sprint 11-12) - **COMPLETO**
**Sprint 11 - Utilitários e Documentação:**
- [x] C.4 - Documentação completa de usuário (USER_GUIDE, TUTORIAL, FAQ)
- [x] C.3 - Utilitários de estado (estado.py CLI)
- [x] D.5 - Sistema de templates YAML reutilizáveis
- [x] D.3 - Dashboard interativo (Rich library)
- [x] E.3 - Sistema de validação de outputs (0-100 pontos)

**Sprint 12 - Testes e Comparação:**
- [x] E.1 - Testes automatizados completos (116 tests, 100% passing)
- [x] D.4 - Ferramenta de comparação de editais

📅 **Progresso:** 16 de 16 itens completos (100%)
✅ **Status:** Sistema production-ready!

---

## 🎓 Princípios de Design

### 1. Transparência Total
Cada decisão do sistema é justificada e rastreável.

### 2. Controle do Usuário
No Modo Assistido, o usuário aprova cada etapa crítica.

### 3. Tolerância Zero a Erros (de Processo)
O processo SHIELD identifica e gerencia corretamente as incertezas do modelo de IA.

### 4. Evidências Obrigatórias
Toda afirmação tem um link ou trecho de fonte como evidência.

### 5. Auditabilidade Completa
Logs estruturados de cada ação significativa.

---

## 🔒 Segurança e Privacidade

- 🔑 **Credenciais:** Gerenciadas via variáveis de ambiente (`.env`)
- 📁 **Dados Locais:** Editais e análises ficam no ambiente do usuário
- 🚫 **Sem Telemetria:** Nenhum dado é enviado para servidores externos (exceto APIs necessárias: Pinecone, n8n)
- 🔐 **Escopo Restrito:** Cada agente tem permissões limitadas à sua função

---

## 🤝 Contribuindo

Este é um projeto em desenvolvimento ativo. Contribuições são bem-vindas após a conclusão do MVP.

### Processo de Contribuição (futuro)
1. Fork do repositório
2. Crie uma branch (`feature/nova-funcionalidade`)
3. Commit com mensagens descritivas
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 🙋 Suporte e Contato

- **Issues:** Para bugs e sugestões, abra uma [issue](../../issues)
- **Discussões:** Para perguntas e ideias, use as [discussions](../../discussions)
- **Documentação:** Consulte a pasta [docs/](docs/)

---

## 🎯 Status Atual

**Versão:** 1.0.0
**Fase:** Production-Ready - Sistema 100% implementado
**Último Update:** 16 de novembro de 2025

### ✅ Todos os Sprints Completados
- Sprint 0: Fundação ✅
- Sprint 1-2: Framework SHIELD ✅
- Sprint 3-4: Document Structurer + Testes ✅
- Sprint 4.5: Melhorias (OCR, Metadata, Cache, Validation) ✅
- Sprint 5-7: RAG Engine + Technical Analyst ✅
- Sprint 8: Orchestrator Base ✅
- Sprint 9: Modo Assistido + Consulta Rápida ✅
- Sprint 10: Modo FLOW + Exports Profissionais ✅
- Sprint 10.5: Teste E2E + Multi-Item Support ✅
- Sprint 11: Documentação + Utilitários + Dashboard ✅
- Sprint 12: Testes Automatizados + Comparação ✅

### 📊 Estatísticas do Projeto
- **Total de código:** ~20,000+ linhas (production)
- **Agentes implementados:** 3 (@DocumentStructurer, @AnalistaTecnico, @Orquestrador)
- **Scripts:** 12 (structure, analyze, export_pdf, export_excel, compare, validate, dashboard, rag_search, etc.)
- **Regras de validação:** 48+ itens (SHIELD checklists)
- **Testes:** 116 tests (100% passing)
- **Documentação:** 15,000+ linhas (dev + usuário)
- **Templates:** Sistema YAML configurável
- **Knowledge Base:** 6 documentos mock (~153KB) para validação

### 🎉 Sistema Production-Ready!
✅ Todas as 16 features do roadmap implementadas
✅ Documentação completa de usuário e desenvolvedor
✅ Suite de testes abrangente (116 tests passing)
✅ Sistema de qualidade (validação 0-100 pontos)
✅ Ferramentas auxiliares (dashboard, comparação, templates)
✅ RAG totalmente funcional (FAISS + sentence-transformers)

---

## 🌟 Visão de Longo Prazo

Evoluir o BidAnalyzee para uma suíte completa de assistência a licitações:

- 🧠 **Agentes Avançados:** Jurídico, Comercial, Gerador de Questionamentos
- 🌐 **SaaS Multi-tenant:** Plataforma cloud com planos de assinatura
- 🖥️ **Interface Gráfica (GUI):** Dashboard web para equipes
- 🏛️ **B2G:** Ferramentas para órgãos públicos avaliarem propostas
- 🛒 **Marketplace:** Conectar distribuidores com fabricantes

---

## 📚 Referências

- **PRD (Product Requirements Document):** Documento base fornecido pelo Product Owner
- **BMad-Method:** Metodologia de arquitetura de sistemas de IA (inspiração interna)
- **Claude Code:** [Documentação oficial](https://docs.claude.com)
- **Pinecone:** [Documentação da API](https://docs.pinecone.io)
- **n8n:** [Documentação de workflows](https://docs.n8n.io)

---

<div align="center">

**Construído com ❤️ e governado pelo Framework SHIELD**

[Documentação](docs/) · [Estratégia](IMPLEMENTATION_STRATEGY.md) · [Arquitetura](ARCHITECTURE_DECISIONS.md) · [SHIELD](OPERATING_PRINCIPLES.md)

</div>
