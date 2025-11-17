# Web Scrapers Documentation

Documentação completa dos web scrapers para popular a knowledge base com documentação da Genetec.

## Documentos

- **[WEB_SCRAPER_GUIDE.md](WEB_SCRAPER_GUIDE.md)** - Guia de uso dos scrapers implementados
- **[WEB_SCRAPER_IMPLEMENTATION.md](WEB_SCRAPER_IMPLEMENTATION.md)** - Plano de implementação detalhado
- **[WEB_SCRAPER_STATUS.md](WEB_SCRAPER_STATUS.md)** - Status e progresso da implementação
- **[WEB_SCRAPER_TEST_REPORT.md](WEB_SCRAPER_TEST_REPORT.md)** - Relatório de testes
- **[FRONTMATTER_SPEC.md](FRONTMATTER_SPEC.md)** - Especificação do frontmatter YAML

## Sites Cobertos

1. **SCSaaS** - Security Center SaaS Help (✅ 100% Funcional)
2. **Compliance** - Genetec Compliance Portal (✅ Implementado, requer Selenium)
3. **TechDocs** - Genetec Technical Documentation (✅ Implementado, requer Selenium)

## Uso Rápido

```bash
# Ver configuração
python -m scripts.scrapers.scraper_orchestrator --print-config

# Testar
python -m scripts.scrapers.scraper_orchestrator --sites scsaas --limit 5

# Produção
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium
```

Ver também: [scripts/scrapers/README.md](../../scripts/scrapers/README.md)
