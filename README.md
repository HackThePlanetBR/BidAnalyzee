# BidAnalyzee 🔍

**Sistema Inteligente de Análise de Conformidade de Editais com IA**

[![Status](https://img.shields.io/badge/status-MVP%20em%20desenvolvimento-yellow)]()
[![Framework](https://img.shields.io/badge/framework-SHIELD%201.0-blue)]()
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
| **Banco Vetorial** | Pinecone (planejado) | Armazenamento de embeddings |
| **Embeddings** | `llama-text-embed-v2` (planejado) | Geração de vetores semânticos |
| **Automação** | n8n (planejado) | Ingestão de dados + Microsserviço de consulta |
| **Parsing** | Python (PyPDF2) | Extração de texto de documentos |
| **OCR** | Tesseract OCR + pytesseract | Texto de PDFs escaneados |
| **Imagens** | Pillow (PIL), pdf2image | Processamento de imagens |
| **Cache** | Disk-based cache (SHA256) | Performance optimization |
| **Persistência** | Sistema de arquivos (JSON, CSV, YAML) | Estado e histórico |
| **Testes** | pytest | Testes unitários e integração |

---

## 📖 Documentação

### Para Desenvolvedores
- 📋 [Estratégia de Implementação](IMPLEMENTATION_STRATEGY.md) - Roadmap completo do projeto
- 🏛️ [Decisões Arquiteturais (ADRs)](ARCHITECTURE_DECISIONS.md) - Registros de decisões técnicas
- 🛡️ [Framework SHIELD](OPERATING_PRINCIPLES.md) - Metodologia de governança

### Para Usuários (em desenvolvimento)
- 📘 **User Guide** - Guia de uso dos comandos
- 🎓 **Tutorial** - Primeira análise passo a passo
- ❓ **FAQ** - Perguntas frequentes

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

### 🔄 Fase 5: Teste E2E e Refinamentos (Sprint 10.5) - **EM PROGRESSO**
- [ ] Teste E2E com edital real complexo
- [ ] Suporte para múltiplos itens/seções
- [ ] Seleção interativa de itens para análise
- [ ] Validação agente vs documento original
- [ ] Refinamentos baseados em casos reais

### 🔄 Fase 6: Documentação e Qualidade (Sprint 11-12)
Utilitários de estado, documentação do usuário, testes avançados, dashboard.

📅 **Progresso:** 10 de 13 sprints completos (~77%)
📅 **Próximo marco:** Sprint 10.5 - Teste E2E Complexo e Multi-Item Support

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

**Versão:** 0.10.0-beta
**Fase:** Teste E2E e Refinamentos (Sprint 10.5) - **EM PROGRESSO**
**Último Update:** 15 de novembro de 2025

### ✅ Sprints Completados
- Sprint 0: Fundação ✅
- Sprint 1-2: Framework SHIELD ✅
- Sprint 3-4: Document Structurer + Testes ✅
- Sprint 4.5: Melhorias (OCR, Metadata, Cache, Validation) ✅
- Sprint 5-7: RAG Engine + Technical Analyst ✅
- Sprint 8: Orchestrator Base ✅
- Sprint 9: Modo Assistido + Consulta Rápida ✅
- Sprint 10: Modo FLOW + Exports Profissionais ✅

### 📊 Estatísticas do Projeto
- **Total de código:** ~15,000+ linhas (production)
- **Agentes implementados:** 3 (@DocumentStructurer, @AnalistaTecnico, @Orquestrador)
- **Scripts:** 6 (analyze_edital_full, export_pdf, export_excel, rag_search, validate_csv, validate_pdf)
- **Regras de validação:** 48+ itens (SHIELD checklists)
- **Test coverage:** 85%+ (148 tests implementados)
- **Documentação:** 10,000+ linhas

### 🎯 Próximos Passos (Sprint 10.5)
1. ✅ Atualizar documentação para refletir Sprint 10
2. 🔄 Criar plano de teste E2E com edital real complexo
3. 🔄 Implementar suporte para múltiplos itens/seções
4. 🔄 Adicionar seleção interativa de itens
5. 🔄 Validação agente vs documento original
6. Ver [docs/E2E_EDITAL_COMPLEXO.md](docs/E2E_EDITAL_COMPLEXO.md) para plano completo

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
