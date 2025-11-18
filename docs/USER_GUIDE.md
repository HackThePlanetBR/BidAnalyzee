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

## 🖥️ Interface do Sistema

**BidAnalyzee opera através do Claude Code** - uma interface conversacional com IA que executa comandos estruturados.

### Tipos de Comandos

**1. Slash Commands** - Para workflows complexos:
- `/structure-edital <pdf>` - Extrai requisitos de edital
- `/analyze-edital <csv>` - Analisa conformidade

**2. Comandos Rápidos (*)** - Para ações pontuais:
- `*ajuda` - Lista comandos disponíveis
- `*buscar "query"` - Busca na base de conhecimento
- `*validar <pdf>` - Valida PDF
- `*exportar-pdf <csv>` - Gera relatório PDF
- `*exportar-excel <csv>` - Gera relatório Excel
- `*listar_analises` - Histórico de análises
- `*sessao <id>` - Detalhes de sessão

**Referência Completa:** Ver [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)

### Conversação Natural

O sistema também aceita linguagem natural:
- "Valide o PDF edital.pdf"
- "Analise o edital completamente"
- "Mostre as últimas análises"

O agente Claude interpreta a intenção e executa o comando apropriado.

---

## 🔄 Workflows Disponíveis

### 1. Workflow Completo (Recomendado) ⭐

**Passo 1: Validar PDF**
```
*validar edital_001.pdf
```
**Saída:** Status de validação, tamanho, páginas, necessidade de OCR

**Passo 2: Extrair Requisitos**
```
/structure-edital edital_001.pdf
```
**Tempo:** 10-30 minutos
**Saída:** `data/deliveries/.../requirements_structured.csv`

**Passo 3: Analisar Conformidade**
```
/analyze-edital data/deliveries/.../requirements_structured.csv
```
**Tempo:** 15-45 minutos
**Saída:** `data/deliveries/.../analysis_conformidade.csv`

**Passo 4: Gerar Relatórios**
```
*exportar-pdf data/deliveries/.../analysis_conformidade.csv
*exportar-excel data/deliveries/.../analysis_conformidade.csv
```
**Tempo:** < 1 minuto
**Saída:** Arquivos PDF e Excel com análise formatada

**Tempo Total:** 30-80 minutos

---

### 2. Workflow Assistido (Passo a Passo)

**Quando usar:** Para controlar cada etapa, revisar resultados intermediários, ou customizar o processo.

**Passo 1: Enviar e Validar Edital**

Comando:
```
*validar edital_001.pdf
```

O sistema executa validações automáticas:
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

Pronto para processar.
```

#### Passo 2: Extrair Requisitos

Quando você confirmar, eu executo:

```
/structure-edital edital_001.pdf
```

**O que acontece:**
- Eu (Document Structurer Agent) extraio requisitos
- Valido cada requisito (30 regras SHIELD)
- Gero CSV estruturado
- Apresento estatísticas

**Você acompanha:**
- Progresso da extração
- Quantidade de requisitos encontrados
- Alertas de validação

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

Após a análise, peça a mim:

**Para PDF:**
```
"Gere o relatório PDF da análise"
```

**Para Excel:**
```
"Gere o relatório Excel da análise"
```

**Ou ambos:**
```
"Gere os relatórios PDF e Excel"
```

Eu vou executar os scripts de exportação e informar onde os arquivos foram salvos.

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

## 🛠️ Como Interagir com o Sistema

### Interface Principal: Claude Code

Você **não precisa executar scripts Python manualmente**. Tudo é feito através de mim (Claude).

### Slash Commands Disponíveis

| Comando | Função | Exemplo |
|---------|--------|---------|
| `/structure-edital` | Extrai requisitos de PDF | `/structure-edital edital.pdf` |
| `/analyze-edital` | Analisa conformidade | `/analyze-edital requirements.csv` |

### Conversação Natural

Você pode simplesmente conversar comigo:

**Exemplos:**

| O que você quer | Como pedir |
|----------------|------------|
| Analisar edital | "Analise o edital edital_001.pdf" |
| Buscar na base | "Busque informações sobre prazo de validade de propostas" |
| Ver estatísticas | "Mostre as estatísticas da última análise" |
| Gerar relatório | "Gere o relatório PDF da análise" |
| Validar PDF | "Valide se o PDF edital_002.pdf está ok" |
| Ver histórico | "Mostre as 10 últimas análises" |

### O que eu faço automaticamente

Quando você pede algo, **eu executo os scripts Python necessários** para você:

**Quando você pede:** "Analise o edital.pdf"

**Eu executo nos bastidores:**
1. `python scripts/validate_pdf.py edital.pdf` ← Valido o PDF
2. `/structure-edital edital.pdf` ← Extraio requisitos
3. `python scripts/rag_search.py ...` ← Busco evidências
4. `/analyze-edital requirements.csv` ← Analiso conformidade
5. `python scripts/export_pdf.py ...` ← Gero relatório

**Você só vê:**
- Progresso em tempo real
- Estatísticas
- Resultados finais
- Alertas importantes

### Comandos Rápidos via Conversação

| Comando | Função |
|---------|--------|
| `*ajuda` | Lista comandos disponíveis |
| `*buscar "query"` | Busca RAG rápida |
| `*listar_analises` | Histórico de análises |
| `*sessao <id>` | Detalhes de uma sessão |

**Nota:** Estes comandos são opcionais - você pode pedir a mesma coisa em linguagem natural.

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

   Peça a mim:
   ```
   "Valide o PDF edital.pdf antes de processar"
   ```

   Eu vou verificar:
   - Tamanho (deve ser < 500MB)
   - Formato válido
   - Texto extraível
   - OCR necessário ou não

2. **Confira tamanho** (editais > 100 páginas podem demorar)

3. **Tenha consciência do tempo** - PDFs escaneados precisam de OCR (mais lento)

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

Peça a mim:
```
"Valide o PDF edital.pdf e mostre detalhes do erro"
```

Eu vou analisar e informar:
- Se o PDF está corrompido
- Se é muito grande (> 500MB)
- Se é escaneado (precisa OCR)
- Se há texto extraível

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
