# Scripts Utilitários

Esta pasta contém scripts auxiliares para setup, validação e manutenção do projeto BidAnalyzee.

## Scripts Disponíveis

### `validate_structure.py`

**Propósito:** Valida que a estrutura completa do projeto está correta.

**Uso:**
```bash
python3 scripts/validate_structure.py
```

**O que verifica:**
- ✅ Todos os diretórios necessários existem
- ✅ Arquivos de documentação estão presentes
- ✅ Templates SHIELD estão criados
- ✅ Checklists dos agentes existem
- ⚠️ Arquivo .env está configurado (aviso)

**Output:**
- Exit code 0: Tudo OK
- Exit code 1: Estrutura incompleta

---

### `scrapers/` - Web Scrapers para Knowledge Base

**Propósito:** Extrai documentação técnica de sites da Genetec e converte para Markdown com frontmatter YAML para popular a knowledge base do RAG.

**Scrapers Disponíveis:**
- **SCSaaS** - Security Center SaaS Help (sitemap.xml)
- **Compliance** - Genetec Compliance Portal (seção-based + Selenium)
- **TechDocs** - Genetec Technical Documentation (sitemap.xml + Selenium)

**Uso Rápido:**
```bash
# Ver configuração atual
python -m scripts.scrapers.scraper_orchestrator --print-config

# Testar com limite de 5 URLs
python -m scripts.scrapers.scraper_orchestrator --sites scsaas --limit 5

# Rodar todos os scrapers (produção)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium
```

**Configuração (.env):**
```bash
SCRAPERS_USE_SELENIUM=true           # Selenium para Compliance/TechDocs
SCRAPERS_HEADLESS=true              # Browser headless
SCRAPERS_USE_PROXY=false            # Habilita proxy
SCRAPERS_PROXY_URL=                 # URL do proxy (auto-detect de HTTP_PROXY)
SCRAPERS_DELAY_BETWEEN_REQUESTS=1.5 # Rate limiting
```

**Documentação Completa:**
- [Guia de Uso](../docs/WEB_SCRAPER_GUIDE.md)
- [Status de Implementação](../docs/WEB_SCRAPER_STATUS.md)
- [Relatório de Testes](../docs/WEB_SCRAPER_TEST_REPORT.md)
- [README dos Scrapers](scrapers/README.md)

---

## Scripts Futuros (Próximos Sprints)

### `test_pinecone_connection.py` (Sprint 1)
Testa conexão com o Pinecone e valida credenciais.

### `test_n8n_connection.py` (Sprint 5)
Testa conexão com o n8n e lista workflows disponíveis.

### `setup_database.py` (Sprint 5)
Inicializa o index do Pinecone com schema correto.

### `import_workflows.py` (Sprint 5)
Importa os workflows n8n (ingestão + consulta) para a instância.

### `validate_config.py` (Sprint 1)
Valida que todas as variáveis do .env estão preenchidas corretamente.

---

## Convenções

- Todos os scripts devem ser executáveis: `chmod +x script.py`
- Todos os scripts devem ter shebang: `#!/usr/bin/env python3`
- Usar Python 3.9+ para compatibilidade
- Incluir docstring no topo do arquivo
- Retornar exit codes apropriados (0 = sucesso, 1 = erro)

---

**Última atualização:** Sprint 0
