# BidAnalyzee - Guia do Usuário

**Versão:** 1.0
**Data:** 16 de novembro de 2025
**Audiência:** Analistas de Propostas, Engenheiros de Vendas, Gerentes Comerciais

---

## 📋 Índice

1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Populando a Base de Conhecimento](#populando-a-base-de-conhecimento)
4. [Workflows Disponíveis](#workflows-disponíveis)
5. [Comandos e Ferramentas](#comandos-e-ferramentas)
6. [Interpretando Resultados](#interpretando-resultados)
7. [Boas Práticas](#boas-práticas)
8. [Troubleshooting](#troubleshooting)
9. [Referências](#referências)

---

## 🎯 Introdução

### O que é BidAnalyzee?

BidAnalyzee é um sistema inteligente assistido por IA que automatiza a análise de conformidade de editais públicos. Utilizando RAG (Retrieval-Augmented Generation) e o Framework SHIELD, o sistema:

- ✅ **Extrai requisitos** de PDFs de editais automaticamente
- ✅ **Analisa conformidade** contra base de conhecimento técnica
- ✅ **Gera relatórios** profissionais em CSV, PDF e Excel
- ✅ **Garante rastreabilidade** completa de cada decisão

### Para quem é este sistema?

- **Analistas de Propostas:** Gere matrizes de conformidade em minutos
- **Engenheiros de Vendas:** Identifique requisitos técnicos críticos rapidamente
- **Gerentes Comerciais:** Tome decisões Go/No-Go baseadas em análises precisas

### Benefícios

| Antes | Depois |
|-------|--------|
| 2-5 dias de análise manual | < 1 hora automatizado |
| Alto risco de erros humanos | > 85% precisão com validação |
| Sem rastreabilidade | Evidências completas com citações |
| Processo não padronizado | Framework SHIELD governado |

---

## 🚀 Primeiros Passos

### Pré-requisitos

**Sistema:**
- Python 3.11+
- Tesseract OCR instalado
- 4GB+ RAM disponível

**Arquivos necessários:**
- PDF do edital (máx 500MB)
- Base de conhecimento indexada (automático)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/HackThePlanetBR/BidAnalyzee.git
cd BidAnalyzee

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure variáveis de ambiente
cp .env.example .env
# Edite .env conforme necessário

# 4. Indexe a base de conhecimento
python scripts/index_knowledge_base.py

# 5. Verifique instalação
python scripts/validate_pdf.py --help
```

### Verificação Rápida

```bash
# Teste se tudo está funcionando
python -c "from agents.orchestrator.state import StateManager; print('✅ OK')"
```

---

## 📚 Populando a Base de Conhecimento

### Opção 1: Web Scrapers Automatizados ⭐ (Recomendado)

O BidAnalyzee possui scrapers prontos para documentação técnica da Genetec:

```bash
# 1. Configure no .env (se necessário)
# Ver seção de configuração abaixo

# 2. Execute scraping completo (primeira vez)
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium

# Isso irá scrape:
# - Security Center SaaS Help (~500 artigos)
# - Genetec Compliance Portal (~100 artigos)
# - Genetec Technical Documentation (~800+ artigos)

# 3. Indexe na base vetorial
python scripts/index_knowledge_base.py --force
```

**Tempo estimado:** 30-60 minutos (scraping) + 5-10 min (indexação)

**Sites suportados:**
- ✅ **SCSaaS** - Security Center SaaS Help
- ✅ **Compliance** - Compliance Portal (certificações, normas)
- ✅ **TechDocs** - Documentação técnica de produtos

### Configuração dos Scrapers (.env)

```bash
# Selenium (necessário para Compliance e TechDocs)
SCRAPERS_USE_SELENIUM=true
SCRAPERS_HEADLESS=true

# Proxy (opcional)
SCRAPERS_USE_PROXY=false
SCRAPERS_PROXY_URL=

# Rate limiting (seja educado com os servidores!)
SCRAPERS_DELAY_BETWEEN_REQUESTS=1.5

# Output
SCRAPERS_OUTPUT_DIR=data/knowledge_base/genetec
```

### Teste Antes de Rodar Tudo

```bash
# Teste com apenas 5 URLs de cada site
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium --limit 5

# Se funcionar, rode completo
python -m scripts.scrapers.scraper_orchestrator --sites all --selenium
```

### Opção 2: Adicionar Documentos Manualmente

Para documentos que não têm scraper:

```bash
# 1. Adicione arquivos .md em data/knowledge_base/
cp meus_documentos/*.md data/knowledge_base/

# 2. Re-indexe
python scripts/index_knowledge_base.py --force
```

**Formato:** Apenas Markdown (.md) com frontmatter YAML opcional.

**Ver também:** [Web Scraper Guide](scrapers/WEB_SCRAPER_GUIDE.md) para detalhes completos.

---

## 🔄 Workflows Disponíveis

### 1. Modo FLOW (Automação Completa) - RECOMENDADO ⭐

**Quando usar:** Análise completa de edital, do início ao fim, sem intervenção.

```bash
python scripts/analyze_edital_full.py edital.pdf
```

**O que faz:**
1. ✅ Valida PDF (tamanho, formato, OCR)
2. ✅ Extrai requisitos (usando Document Structurer)
3. ✅ Analisa conformidade (usando Technical Analyst)
4. ✅ Gera relatórios (CSV, PDF, Excel)
5. ✅ Salva estado da sessão

**Duração típica:** 15-45 minutos (depende do tamanho do edital)

**Saída:**
```
data/deliveries/YYYYMMDD_HHMMSS_<nome-edital>/
├── requirements.csv          # Requisitos extraídos
├── analysis_conformidade.csv # Análise completa
├── relatorio.pdf             # Relatório PDF profissional
└── relatorio.xlsx            # Planilha Excel com abas
```

---

### 2. Modo Assistido (Passo a Passo)

**Quando usar:** Quando você quer controlar cada etapa, revisar intermediários, ou customizar processo.

#### Passo 1: Validar PDF

```bash
python scripts/validate_pdf.py edital.pdf
```

**Verifica:**
- ✅ Arquivo existe e está acessível
- ✅ Tamanho dentro do limite (500MB)
- ✅ Formato PDF válido
- ✅ Contém texto extraível (não só imagens)
- ✅ Não está corrompido
- ✅ Possui metadados básicos

**Saída exemplo:**
```
✅ VALIDAÇÃO COMPLETA - PDF APROVADO

Detalhes:
- Arquivo: edital_12345.pdf
- Tamanho: 2.3 MB
- Páginas: 45
- Texto extraível: Sim
- OCR necessário: Não
```

#### Passo 2: Extrair Requisitos

Use o slash command `/structure-edital`:

```
/structure-edital edital.pdf
```

**O que faz:**
- Extrai requisitos usando Document Structurer Agent
- Valida cada requisito (30 regras)
- Gera CSV estruturado

**Saída:** `data/deliveries/.../requirements.csv`

**Campos do CSV:**
- `item`: Número do item
- `categoria`: Categoria do requisito
- `descricao`: Descrição completa
- `subcategoria`: Subcategoria (se aplicável)
- `especificacao_tecnica`: Detalhes técnicos
- `referencia_edital`: Página/seção do edital
- `obrigatorio`: Sim/Não/Desejável
- `observacoes`: Notas adicionais

#### Passo 3: Analisar Conformidade

Use o slash command `/analyze-edital`:

```
/analyze-edital data/deliveries/.../requirements.csv
```

**O que faz:**
- Carrega requisitos do CSV
- Para cada requisito:
  - Busca na base de conhecimento (RAG)
  - Analisa conformidade
  - Gera veredicto + evidências
- Valida completude (100% obrigatório)

**Saída:** `data/deliveries/.../analysis_conformidade.csv`

**Campos adicionados:**
- `veredicto`: CONFORME / NÃO CONFORME / PARCIAL / REQUER ANÁLISE
- `justificativa`: Explicação do veredicto
- `evidencias`: Citações da base de conhecimento
- `recomendacoes`: Ações sugeridas
- `nivel_confianca`: Alto / Médio / Baixo

#### Passo 4: Gerar Relatórios

**PDF:**
```bash
python scripts/export_pdf.py data/deliveries/.../analysis_conformidade.csv
```

**Excel:**
```bash
python scripts/export_excel.py data/deliveries/.../analysis_conformidade.csv
```

---

### 3. Busca Rápida na Base de Conhecimento

**Quando usar:** Consulta pontual sem análise completa.

```
*buscar "prazo validade proposta licitação"
```

**Saída:**
```
📚 RESULTADOS DA BUSCA (5 encontrados)

[1] Lei 8.666/93:120 (similaridade: 0.92) ⭐
"O prazo de validade das propostas será de 60 dias..."

[2] Lei 14.133/2021:89 (similaridade: 0.87) ⭐
"A validade da proposta não poderá ser inferior a..."

[3] requisitos_tecnicos.md:45 (similaridade: 0.78)
"Propostas técnicas devem manter validade mínima..."
```

---

## 🛠️ Comandos e Ferramentas

### Comandos do Orchestrator

Execute via Claude Code ou diretamente:

| Comando | Função | Exemplo |
|---------|--------|---------|
| `*ajuda` | Lista comandos disponíveis | `*ajuda` |
| `*buscar "<query>"` | Busca RAG rápida | `*buscar "prazo recurso"` |
| `*listar_analises` | Histórico de análises | `*listar_analises` |
| `*sessao <id>` | Detalhes de uma sessão | `*sessao abc123` |

### Scripts Python Utilitários

**Validação:**
```bash
# Validar PDF antes de processar
python scripts/validate_pdf.py edital.pdf

# Validar CSV de requisitos
python scripts/validate_csv.py requirements.csv

# Validar CSV de análise
python scripts/validate_csv.py analysis_conformidade.csv --type analysis
```

**Busca RAG:**
```bash
# Buscar na base de conhecimento
python scripts/rag_search.py "prazo validade proposta"

# Top 10 resultados
python scripts/rag_search.py "marca especificada" --top-k 10
```

**State Management:**
```bash
# Listar sessões recentes
python scripts/orchestrator_list.py 10

# Ver detalhes de sessão
python scripts/orchestrator_session.py <session-id>
```

---

## 📊 Interpretando Resultados

### Veredictos de Conformidade

| Veredicto | Significado | Ação Recomendada |
|-----------|-------------|------------------|
| **CONFORME** | Requisito atendido completamente | ✅ Nenhuma ação necessária |
| **NÃO CONFORME** | Requisito não atendido | ⚠️ Avaliar impacto, considerar não participar |
| **PARCIALMENTE CONFORME** | Atendimento parcial | ⚠️ Verificar se parcial é aceitável |
| **REQUER ANÁLISE** | Complexo, precisa análise humana | 🔍 Revisar manualmente com especialista |

### Nível de Confiança

- **Alto (0.85-1.0):** IA muito confiante, evidências claras
- **Médio (0.70-0.84):** Razoável, mas revisar evidências
- **Baixo (<0.70):** Incerteza, análise humana obrigatória

### Lendo Evidências

Evidências sempre citam **fonte:linha**:

```
Evidências:
- Lei 8.666/93:120 - "prazo de validade será de 60 dias"
- requisitos_tecnicos.md:45 - "certificação INMETRO obrigatória"
```

**Como validar:**
1. Abra o arquivo fonte (`data/knowledge_base/...`)
2. Vá até a linha citada
3. Verifique contexto completo

---

## ✅ Boas Práticas

### Antes de Processar

1. **Valide o PDF primeiro**
   ```bash
   python scripts/validate_pdf.py edital.pdf
   ```

2. **Confira tamanho** (editais > 100 páginas podem demorar)

3. **Verifique OCR** - PDFs escaneados precisam de OCR (mais lento)

### Durante o Processamento

1. **Não interrompa** - Deixe o processo completar

2. **Monitore logs** - Verifique se há erros

3. **Modo FLOW é mais rápido** - Use assistido apenas se necessário

### Após Análise

1. **Revise itens "REQUER ANÁLISE"** - Sempre valide com especialista

2. **Confira evidências** - Não confie cegamente, valide citações

3. **Salve resultados** - Backup de `data/deliveries/`

### Atualização da Base de Conhecimento

**Importante:** Esta versão usa base mock. Para produção:

1. Substitua arquivos em `data/knowledge_base/`
2. Re-indexe com:
   ```bash
   python scripts/index_knowledge_base.py
   ```

---

## ⚠️ Troubleshooting

### Erros Comuns

#### 1. "PDF validation failed"

**Causa:** PDF corrompido, muito grande, ou sem texto.

**Solução:**
```bash
# Verifique detalhes
python scripts/validate_pdf.py edital.pdf --verbose

# Se PDF for escaneado, use OCR
# (mais lento, mas funciona)
```

#### 2. "No requirements extracted"

**Causa:** PDF sem requisitos claros, ou formato não reconhecido.

**Solução:**
- Verifique se PDF tem tabelas/listas de requisitos
- Teste com outro edital primeiro
- Revise manualmente se necessário

#### 3. "FAISS index not found"

**Causa:** Base de conhecimento não indexada.

**Solução:**
```bash
python scripts/index_knowledge_base.py
```

#### 4. "Low confidence in all verdicts"

**Causa:** Base de conhecimento não cobre o domínio do edital.

**Solução:**
- Adicione documentos relevantes em `data/knowledge_base/`
- Re-indexe a base
- Considere análise manual

### Logs e Debug

**Ativar logs verbosos:**
```bash
export LOG_LEVEL=DEBUG
python scripts/analyze_edital_full.py edital.pdf
```

**Ver logs de sessão:**
```bash
cat data/state/sessions/<session-id>.json
```

---

## 📚 Referências

### Documentação Técnica

- [README.md](../README.md) - Overview do projeto
- [ROADMAP.md](../ROADMAP.md) - Plano de desenvolvimento
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Status atual
- [OPERATING_PRINCIPLES.md](../OPERATING_PRINCIPLES.md) - Framework SHIELD
- [ARCHITECTURE_DECISIONS.md](../ARCHITECTURE_DECISIONS.md) - Decisões técnicas

### Agentes

- [Document Structurer](../agents/document_structurer/README.md)
- [Technical Analyst](../agents/technical_analyst/README.md)
- [Orchestrator](../agents/orchestrator/README.md)

### Tutoriais

- [TUTORIAL.md](TUTORIAL.md) - Tutorial passo a passo com exemplos reais
- [FAQ.md](FAQ.md) - Perguntas frequentes

### Scripts

- [scripts/README.md](../scripts/README.md) - Documentação de todos os scripts

---

## 📞 Suporte

**Problemas técnicos:** Abra uma issue no GitHub
**Dúvidas de uso:** Consulte [FAQ.md](FAQ.md)
**Tutoriais:** Veja [TUTORIAL.md](TUTORIAL.md)

---

**Última atualização:** 16/11/2025
**Versão do sistema:** Sprint 10 (Modo FLOW + Exports + CI/CD)
