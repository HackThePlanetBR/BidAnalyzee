# BidAnalyzee Documentation

Documentação completa do sistema BidAnalyzee - Análise automatizada de conformidade em licitações públicas.

## 📚 Documentação Principal

Comece aqui:

- **[USER_GUIDE.md](USER_GUIDE.md)** - Guia completo do usuário
- **[TUTORIAL.md](TUTORIAL.md)** - Tutorial passo a passo
- **[FAQ.md](FAQ.md)** - Perguntas frequentes
- **[INSTALLATION.md](INSTALLATION.md)** - Instalação e configuração

## 📂 Documentação Organizada

### [scrapers/](scrapers/)
Documentação dos web scrapers para popular a knowledge base

- Guia de uso dos scrapers
- Implementação e status
- Relatórios de testes
- Especificação de frontmatter

### [technical/](technical/)
Documentação técnica detalhada

- Pipelines de análise
- Sistema RAG
- Processamento de queries
- OCR e extração de texto

### [test-results/](test-results/)
Relatórios de testes do sistema

- Testes end-to-end
- Testes de integração
- Casos de teste complexos

### [guides/](guides/)
Guias especializados e comparações

- Comparação de abordagens
- Estratégias de implementação
- Guias de débitos técnicos

### [archived-sprints/](archived-sprints/)
Histórico de sprints anteriores

- Planejamentos e status antigos
- Documentação histórica
- Configurações obsoletas

## 🚀 Início Rápido

1. **Instalação**: [INSTALLATION.md](INSTALLATION.md)
2. **Tutorial**: [TUTORIAL.md](TUTORIAL.md)
3. **Uso**: [USER_GUIDE.md](USER_GUIDE.md)

## 🛠️ Para Desenvolvedores

- **Arquitetura**: [technical/ANALYSIS_PIPELINE.md](technical/ANALYSIS_PIPELINE.md)
- **RAG System**: [technical/TECHNICAL_ANALYST_RAG.md](technical/TECHNICAL_ANALYST_RAG.md)
- **Web Scrapers**: [scrapers/](scrapers/)
- **Comparações**: [guides/COMPARISON.md](guides/COMPARISON.md)

## 📊 Status do Projeto

Ver também na raiz do projeto:
- [../PROJECT_STATUS.md](../PROJECT_STATUS.md) - Status atual
- [../ROADMAP.md](../ROADMAP.md) - Roadmap do projeto
- [../README.md](../README.md) - README principal

## 🔍 Estrutura de Pastas

```
docs/
├── README.md                    # Este arquivo
├── USER_GUIDE.md               # Guia do usuário
├── TUTORIAL.md                 # Tutorial
├── FAQ.md                      # FAQ
├── INSTALLATION.md             # Instalação
├── scrapers/                   # Web scrapers
│   ├── WEB_SCRAPER_GUIDE.md
│   ├── WEB_SCRAPER_STATUS.md
│   └── ...
├── technical/                  # Docs técnicas
│   ├── ANALYSIS_PIPELINE.md
│   ├── TECHNICAL_ANALYST_RAG.md
│   └── ...
├── test-results/              # Relatórios de testes
│   ├── E2E_TEST_REPORT.md
│   └── ...
├── guides/                    # Guias especializados
│   ├── COMPARISON.md
│   └── ...
└── archived-sprints/         # Histórico de sprints
    ├── SPRINT_10.5_COMPLETE.md
    └── ...
```

## 📝 Contribuindo

Ao adicionar nova documentação:
- Docs de usuário → raiz de `docs/`
- Docs de web scrapers → `docs/scrapers/`
- Docs técnicas → `docs/technical/`
- Relatórios de testes → `docs/test-results/`
- Guias especializados → `docs/guides/`
- Histórico → `docs/archived-sprints/`

Sempre atualize os READMEs relevantes ao adicionar novos arquivos.
