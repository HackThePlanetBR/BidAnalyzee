# BidAnalyzee - Perguntas Frequentes (FAQ)

**Versão:** 1.0
**Data:** 16 de novembro de 2025

---

## 📋 Índice

- [Geral](#geral)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso do Sistema](#uso-do-sistema)
- [Resultados e Interpretação](#resultados-e-interpretação)
- [Performance e Limites](#performance-e-limites)
- [Troubleshooting](#troubleshooting)
- [Base de Conhecimento](#base-de-conhecimento)

---

## 🎯 Geral

### O que é BidAnalyzee?

BidAnalyzee é um sistema inteligente que automatiza a análise de conformidade de editais públicos usando IA (RAG + LLM) governada pelo Framework SHIELD.

### Quanto custa usar?

O sistema é open-source (MIT License) e gratuito. Você precisa apenas de:
- Infraestrutura para rodar (Python + dependências)
- API keys se usar LLMs externos (Claude, OpenAI) - opcional para alguns módulos

### Quem desenvolveu?

Desenvolvido como sistema experimental para empresas que participam de licitações públicas no Brasil.

### Qual a precisão do sistema?

- **> 85% de precisão** em requisitos técnicos padrão
- **90% em testes reais** (ver PROJECT_STATUS.md)
- **Sempre requer validação humana** para decisões críticas

### O sistema substitui análise humana?

**Não.** O sistema é assistido por IA e:
- ✅ Acelera análise (dias → minutos)
- ✅ Reduz erros mecânicos
- ❌ **NÃO** substitui julgamento especialista
- ❌ **NÃO** toma decisões finais

**Veredictos "REQUER ANÁLISE" sempre precisam de revisão humana.**

---

## 🔧 Instalação e Configuração

### Quais são os requisitos mínimos?

**Sistema:**
- Python 3.11+
- 4GB RAM (recomendado: 8GB+)
- 2GB espaço em disco
- Linux, macOS ou Windows (WSL recomendado)

**Software:**
- Tesseract OCR (`apt install tesseract-ocr tesseract-ocr-por`)
- Git

### Como instalo o Tesseract OCR?

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
- Baixe: https://github.com/UB-Mannheim/tesseract/wiki
- Adicione ao PATH

### Preciso de API keys?

**Não para uso básico.** A versão atual usa:
- FAISS (local, sem API)
- sentence-transformers (local, sem API)

APIs externas são opcionais para recursos avançados.

### Como configuro o .env?

```bash
# 1. Copie o exemplo
cp .env.example .env

# 2. Edite conforme necessário
# Valores padrão geralmente funcionam para uso local
```

**Principais variáveis:**
- `PINECONE_API_KEY` - Opcional (apenas se usar Pinecone)
- `RAG_TOP_K` - Quantos resultados buscar (padrão: 5)
- `CHUNK_SIZE` - Tamanho de chunks (padrão: 1000)

### Como indexo a base de conhecimento?

```bash
python scripts/index_knowledge_base.py
```

Isso cria `data/knowledge_base/faiss_index/` com embeddings.

**Re-indexar apenas se:**
- Adicionar/remover documentos
- Atualizar documentos existentes
- Mudar configuração de chunks

---

## 💻 Uso do Sistema

### Qual modo devo usar: FLOW ou Assistido?

| Cenário | Modo Recomendado |
|---------|------------------|
| Análise completa, rapidez | **FLOW** ⭐ |
| Revisar cada etapa | **Assistido** |
| Aprendendo o sistema | **Assistido** |
| Customizar processo | **Assistido** |
| Produção, em escala | **FLOW** |

### Como uso o Modo FLOW?

**Via Claude Code** (conversação comigo):

```
"Analise o edital edital.pdf completamente"
```

Ou use o slash command:
```
/structure-edital edital.pdf
```

Eu vou executar todo o fluxo automaticamente. Aguarde 15-45 minutos (depende do edital).

### Como acompanho o progresso?

**Modo FLOW mostra:**
```
[1/4] ✅ Validando PDF...
[2/4] 🔄 Extraindo requisitos...
[3/4] ⏳ Analisando conformidade...
[4/4] 📊 Gerando relatórios...
```

**Logs detalhados:**
```bash
tail -f logs/analysis.log  # Se configurado
```

### Posso pausar e retomar?

**Não nativamente.** O Modo FLOW roda de ponta a ponta.

**Workaround:** Use Modo Assistido e execute etapas separadamente.

### Como cancelo um processamento?

`Ctrl+C` para interromper.

**Atenção:** Estado intermediário pode ficar inconsistente. Recomenda-se recomeçar do zero.

### Onde ficam os resultados?

```
data/deliveries/YYYYMMDD_HHMMSS_<edital>/
├── requirements.csv          # Requisitos extraídos
├── analysis_conformidade.csv # Análise
├── relatorio.pdf             # PDF
└── relatorio.xlsx            # Excel
```

---

## 📊 Resultados e Interpretação

### O que significa cada veredicto?

- **CONFORME:** ✅ Atende completamente, OK para participar
- **NÃO CONFORME:** ❌ Não atende, risco de desqualificação
- **PARCIALMENTE CONFORME:** ⚠️ Atende parcial, verificar se aceitável
- **REQUER ANÁLISE:** 🔍 Complexo, análise humana obrigatória

### Devo confiar nos veredictos?

**Com ressalvas:**
- ✅ Veredictos com **nível de confiança "Alto"** são geralmente corretos
- ⚠️ Veredictos "Médio" precisam de revisão
- ❌ Veredictos "Baixo" **sempre** revisem manualmente

**Regra de ouro:** Sempre valide evidências antes de decisões críticas.

### Como valido evidências?

Evidências citam `arquivo:linha`:

```
Lei 8.666/93:120 - "prazo será de 60 dias"
```

**Validação:**
1. Abra `data/knowledge_base/Lei_8666.md`
2. Vá até linha 120
3. Leia contexto completo (linhas ~115-125)
4. Confirme se citação está correta e contexto é aplicável

### Por que alguns itens são "REQUER ANÁLISE"?

**Motivos comuns:**
- Requisito ambíguo ou mal escrito no edital
- Base de conhecimento não cobre o tópico
- Múltiplas interpretações possíveis
- Nível de confiança baixo (< 0.70)

**Ação:** Sempre escale para especialista humano.

### Posso editar o CSV de análise?

**Sim**, mas:
- ✅ Edite `analysis_conformidade.csv` se necessário
- ✅ Adicione colunas customizadas
- ⚠️ Não altere colunas principais (estrutura pode quebrar exports)
- ⚠️ Mantenha encoding UTF-8

### Como exporto para outros formatos?

**Via Claude Code** - simplesmente peça:

**Para PDF:**
```
"Gere o relatório PDF da análise"
```

**Para Excel:**
```
"Gere o relatório Excel da análise"
```

**Ambos:**
```
"Gere os relatórios PDF e Excel"
```

Eu vou executar os scripts de exportação e informar onde foram salvos os arquivos.

---

## ⚡ Performance e Limites

### Quanto tempo demora uma análise?

**Depende de:**
- Tamanho do edital (páginas)
- Quantidade de requisitos
- OCR necessário ou não
- Hardware

**Estimativas:**
| Edital | Páginas | Requisitos | Tempo (sem OCR) | Tempo (com OCR) |
|--------|---------|------------|-----------------|-----------------|
| Pequeno | 10-30 | 20-50 | 5-10 min | 15-25 min |
| Médio | 30-100 | 50-150 | 15-30 min | 30-60 min |
| Grande | 100-300 | 150-500 | 30-60 min | 1-3 horas |

### Qual o tamanho máximo de PDF?

**Limite atual:** 500MB

**Recomendado:** < 100MB para melhor performance

**Se PDF > 500MB:**
1. Divida em partes menores
2. Processe separadamente
3. Consolide resultados

### Quantos editais posso processar simultaneamente?

**Recomendado:** 1 por vez.

**Motivo:** Cada análise usa bastante CPU/RAM.

**Se precisar de paralelismo:**
- Use múltiplas máquinas/containers
- Cada instância processa 1 edital

### Como acelero o processamento?

**Otimizações:**
1. **Use SSD** (não HDD)
2. **Mais RAM** (8GB+ recomendado)
3. **PDFs já com texto** (evite OCR se possível)
4. **Reduza RAG_TOP_K** no .env (ex: de 5 para 3)

**Não recomendado:**
- ❌ Pular validações (pode gerar resultados ruins)
- ❌ Reduzir chunk_size demais (perde contexto)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named..."

**Causa:** Dependências não instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

### "FAISS index not found"

**Causa:** Base de conhecimento não indexada.

**Solução:**
```bash
python scripts/index_knowledge_base.py
```

### "PDF validation failed: File too large"

**Causa:** PDF > 500MB.

**Solução:**
- Comprima o PDF (ferramentas online)
- Divida em partes menores

### "PDF validation failed: No text extractable"

**Causa:** PDF escaneado, sem camada de texto.

**Solução:**
- OCR será usado automaticamente (mais lento)
- Ou faça OCR prévio com Adobe/Abby

### "No requirements extracted"

**Causas comuns:**
1. PDF não tem requisitos claros (tabelas/listas)
2. Formato não reconhecido
3. OCR falhou

**Soluções:**
1. Verifique se PDF realmente tem requisitos estruturados
2. Teste com outro edital (confirme que sistema funciona)
3. Considere extração manual para este edital

### "Analysis took too long / timeout"

**Causa:** Edital muito grande ou hardware lento.

**Soluções:**
- Aumente timeout no código (se souber Python)
- Use hardware mais potente
- Divida edital em partes

### Resultados inconsistentes / baixa qualidade

**Possíveis causas:**
1. Base de conhecimento inadequada para o domínio
2. Edital mal escrito (ambíguo)
3. OCR de baixa qualidade

**Soluções:**
1. Adicione documentos relevantes à KB
2. Re-indexe após adicionar
3. Para OCR: use PDFs de melhor qualidade

---

## 📚 Base de Conhecimento

### O que é a "base de conhecimento mock"?

**Mock = Simulada.** A versão base usa documentos de exemplo para demonstração:
- Lei 8.666/93 (mock)
- Lei 14.133/2021 (mock)
- Requisitos técnicos genéricos

**Para produção:** Use os **web scrapers automatizados** ou adicione documentos manualmente.

### Como populo a base com documentação real? ⭐ **NOVO**

**Opção 1: Web Scrapers Automatizados (Recomendado)**

O BidAnalyzee possui scrapers prontos para documentação da Genetec:

```bash
# Scrape toda documentação Genetec (SCSaaS, Compliance, TechDocs)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium

# Ou apenas um site específico
python -m scripts.scrapers.scraper_orchestrator --sites scsaas --limit 10
```

**Sites suportados:**
- ✅ **SCSaaS** - Security Center SaaS Help (100% funcional)
- ✅ **Compliance** - Genetec Compliance Portal (requer Selenium)
- ✅ **TechDocs** - Genetec Technical Documentation (requer Selenium)

**Documentação completa:** Ver [docs/scrapers/WEB_SCRAPER_GUIDE.md](scrapers/WEB_SCRAPER_GUIDE.md)

**Opção 2: Adicionar Manualmente**

Para documentos que não têm scraper:

```bash
# Passo 1: Adicione arquivo Markdown
cp meu_documento.md data/knowledge_base/

# Passo 2: Re-indexe
python scripts/index_knowledge_base.py
```

**Formatos suportados:** Apenas Markdown (.md).

### Como configuro os web scrapers?

**1. Configure no .env:**

```bash
# Selenium (necessário para Compliance e TechDocs)
SCRAPERS_USE_SELENIUM=true
SCRAPERS_HEADLESS=true

# Proxy (opcional)
SCRAPERS_USE_PROXY=false
SCRAPERS_PROXY_URL=

# Rate limiting (seja educado!)
SCRAPERS_DELAY_BETWEEN_REQUESTS=1.5
```

**2. Execute:**

```bash
# Teste primeiro (apenas 5 URLs)
python -m scripts.scrapers.scraper_orchestrator --sites scsaas --limit 5

# Produção (scrape tudo)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium
```

**Requisitos:**
- Chrome/Chromium instalado (para Selenium)
- Conexão com internet
- ~30-60 min para scraping completo

### Preciso de Selenium para os scrapers?

**Depende do site:**

| Scraper | Selenium? | Motivo |
|---------|-----------|--------|
| SCSaaS | ❌ Não | Site estático, requests funciona |
| Compliance | ✅ Sim | Cloudflare bot protection |
| TechDocs | ✅ Sim | SPA com JavaScript |

**Instalação Selenium:**
```bash
pip install selenium
pip install undetected-chromedriver  # Opcional, melhora bypass Cloudflare
```

### Qual o formato ideal de documentos?

**Markdown bem estruturado:**

```markdown
# Título do Documento

## Seção 1

Texto relevante aqui.

## Seção 2

Mais informações técnicas.

- Item 1
- Item 2
```

**Boas práticas:**
- Use headers (##, ###) para estrutura
- Parágrafos curtos (mais fácil chunking)
- Listas quando aplicável
- Evite tabelas complexas (pode perder estrutura)

### Como atualizo a base de conhecimento?

**Atualizar documentos existentes:**
1. Edite arquivo em `data/knowledge_base/`
2. Re-indexe: `python scripts/index_knowledge_base.py`

**Remover documentos:**
1. Delete arquivo de `data/knowledge_base/`
2. Re-indexe

**Adicionar novos:**
1. Adicione em `data/knowledge_base/`
2. Re-indexe

### Com que frequência devo re-indexar?

**Apenas quando:**
- Adicionar novos documentos
- Atualizar documentos existentes
- Remover documentos

**Não precisa** re-indexar se apenas processar editais.

### Posso usar PDFs na base de conhecimento?

**Não diretamente.** Apenas Markdown (.md).

**Workaround:**
1. Converta PDF → Markdown (ferramentas: pandoc, online converters)
2. Adicione .md à base
3. Re-indexe

### Os scrapers funcionam com proxy?

**Sim!** Configure no .env:

```bash
SCRAPERS_USE_PROXY=true
SCRAPERS_PROXY_URL=http://proxy.example.com:8080
```

Ou use a variável de ambiente `HTTP_PROXY` (auto-detectada).

### Com que frequência devo atualizar a documentação scraped?

**Recomendação:** Mensal ou trimestral.

**Documentação técnica da Genetec** é relativamente estável, mas pode ter:
- Novos produtos/features
- Atualizações de versão
- Novos artigos de suporte

**Para re-scrape:**
```bash
# Limpe pasta antiga
rm -rf data/knowledge_base/genetec/*

# Re-scrape
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium

# Re-indexe
python scripts/index_knowledge_base.py --force
```

### Posso criar scrapers para outros sites?

**Sim!** O sistema é extensível.

**Passo 1:** Crie novo scraper herdando de `BaseScraper`

```python
from scripts.scrapers.base_scraper import BaseScraper

class MeuScraper(BaseScraper):
    def discover_urls(self):
        # Implementar descoberta de URLs
        pass

    def extract_content(self, url):
        # Implementar extração
        pass
```

**Passo 2:** Registre no orchestrator

**Documentação:** Ver [docs/scrapers/WEB_SCRAPER_IMPLEMENTATION.md](scrapers/WEB_SCRAPER_IMPLEMENTATION.md)

---

## 🎓 Dicas Avançadas

### Como customizo os prompts dos agentes?

Edite:
- `agents/document_structurer/prompt.md`
- `agents/technical_analyst/prompt.md`
- `agents/orchestrator/prompt.md`

**Atenção:** Mudanças podem afetar qualidade. Teste bem!

### Posso integrar com outros sistemas?

**Sim, via:**
- CSV outputs (import em qualquer sistema)
- Scripts Python (chame via API/subprocess)
- n8n workflows (integração planejada)

### Como contribuo com melhorias?

1. Fork o repositório
2. Crie branch para feature
3. Implemente + testes
4. Abra Pull Request

Ver [CONTRIBUTING.md](../CONTRIBUTING.md) (se existir).

---

## 📞 Ainda tem dúvidas?

- **Não encontrou resposta aqui?** Consulte [USER_GUIDE.md](USER_GUIDE.md)
- **Tutorial passo a passo:** [TUTORIAL.md](TUTORIAL.md)
- **Problemas técnicos:** Abra issue no GitHub
- **Documentação técnica:** Ver `/docs` e README.md

---

**Última atualização:** 16/11/2025
**Versão:** Sprint 10
