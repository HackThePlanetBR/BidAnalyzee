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

### Modo Assistido (`/iniciar-analise`)
Workflow completo com checkpoints de aprovação:
1. Extração de metadados do edital (Objeto, Escopo)
2. Estruturação de requisitos em CSV
3. Análise de conformidade item por item
4. Geração de relatório com evidências

**Controle total:** O usuário aprova cada etapa crítica antes de prosseguir.

### Modo FLOW (`/flow`)
Execução automatizada de ponta a ponta para usuários avançados.

**Velocidade:** Sem interrupções, notificação apenas ao final.

### Modo Consulta Rápida (`/consulta-rapida`)
Análise instantânea de uma pergunta específica contra a base de conhecimento.

**Agilidade:** Respostas em segundos, sem criar CSV.

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
| **Banco Vetorial** | Pinecone | Armazenamento de embeddings |
| **Embeddings** | `llama-text-embed-v2` | Geração de vetores semânticos |
| **Automação** | n8n | Ingestão de dados + Microsserviço de consulta |
| **Parsing** | Python (PyPDF2, python-docx) | Extração de texto de documentos |
| **Persistência** | Sistema de arquivos (JSON, CSV) | Estado e histórico |

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

### ✅ Fase 0: Fundação (Sprint 0) - **EM ANDAMENTO**
- [x] Estrutura de diretórios
- [x] Documentação do Framework SHIELD
- [x] Decisões arquiteturais documentadas
- [ ] Templates de prompts e checklists
- [ ] Configuração de ambiente

### 🔄 Fase 1: Framework SHIELD (Sprint 1-2)
Implementação dos templates e capacidades reutilizáveis do SHIELD.

### 🔄 Fase 2: Estruturação de Editais (Sprint 3-4)
Parser de documentos + @EstruturadorDeDocumentos + comando `/estruturar-edital`.

### 🔄 Fase 3: Análise de Conformidade (Sprint 5-7)
Motor RAG + @AnalistaTecnico + integração com n8n/Pinecone.

### 🔄 Fase 4: Orquestração e UX (Sprint 8-10)
@Orquestrador + Modos Assistido/FLOW/Consulta + comandos completos.

### 🔄 Fase 5: Validação e Melhorias (Sprint 11-12)
Testes com editais reais, otimizações, documentação do usuário.

📅 **Previsão de MVP completo:** 12 sprints (~3-4 meses)

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

**Versão:** 0.1.0-alpha
**Fase:** Fundação (Sprint 0)
**Último Update:** 06 de novembro de 2025

### Próximos Passos Imediatos
1. ✅ Aprovação da estratégia de implementação
2. 🔄 Criação dos templates de prompts e checklists
3. 🔄 Setup do ambiente de desenvolvimento
4. 🔄 Início do Sprint 1 (Framework SHIELD)

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
