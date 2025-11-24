# BidAnalyzee - Referência de Comandos

**Versão:** 2.0
**Última atualização:** 24 de novembro de 2025

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Workflows Completos](#workflows-completos)
3. [Ações Rápidas](#ações-rápidas)
4. [Navegação e Histórico](#navegação-e-histórico)
5. [Sintaxe e Convenções](#sintaxe-e-convenções)
6. [Fluxos de Trabalho](#fluxos-de-trabalho)

---

## 🎯 Visão Geral

BidAnalyzee utiliza **slash commands** executados através do Claude Code. Todos os comandos seguem a sintaxe `/comando <obrigatorio> [opcional]`.

**Características:**
- ✅ Executados diretamente no Claude Code
- ✅ Autocompletar com TAB
- ✅ Documentação integrada
- ✅ Governança SHIELD quando aplicável

---

## 🔄 Workflows Completos

Comandos para workflows de análise de editais que envolvem processamento extenso.

### `/structure-edital`

**Função:** Extrai e estrutura requisitos de PDF do edital em formato CSV.

**Sintaxe:**
```
/structure-edital <pdf>
```

**Parâmetros:**
- `<pdf>` (obrigatório): Caminho para arquivo PDF do edital

**Exemplos:**
```
/structure-edital data/uploads/edital_001.pdf
/structure-edital edital_pmsp_2025.pdf
```

**Saída:**
- `data/deliveries/YYYYMMDD_HHMMSS_<edital>/outputs/requirements_structured.csv`

**Tempo estimado:** 10-30 minutos (depende do tamanho do edital)

**Agente responsável:** @EstruturadorDeDocumentos

---

### `/analyze-edital`

**Função:** Analisa conformidade dos requisitos contra base de conhecimento usando RAG.

**Sintaxe:**
```
/analyze-edital <csv>
```

**Parâmetros:**
- `<csv>` (obrigatório): Caminho para CSV de requisitos (gerado por `/structure-edital`)

**Exemplos:**
```
/analyze-edital data/deliveries/20251118_143022_edital_001/outputs/requirements_structured.csv
/analyze-edital requirements.csv
```

**Saída:**
- `data/deliveries/<sessao>/outputs/analysis_conformidade.csv`

**Tempo estimado:** 15-45 minutos (depende da quantidade de requisitos)

**Agente responsável:** @AnalistaTecnico

---

## ⚡ Ações Rápidas

Comandos para validação, exportação e consultas rápidas.

### `/validate-pdf`

**Função:** Valida PDF antes de processar (tamanho, formato, OCR).

**Sintaxe:**
```
/validate-pdf <pdf>
```

**Parâmetros:**
- `<pdf>` (obrigatório): Caminho para arquivo PDF

**Exemplos:**
```
/validate-pdf edital.pdf
/validate-pdf data/uploads/edital_001.pdf
```

**Saída:**
- Status de validação (✅ aprovado / ❌ reprovado)
- Tamanho do arquivo
- Número de páginas
- Necessidade de OCR
- Texto extraível

**Tempo estimado:** < 5 segundos

---

### `/export-pdf`

**Função:** Gera relatório profissional em PDF.

**Sintaxe:**
```
/export-pdf <csv> [output]
```

**Parâmetros:**
- `<csv>` (obrigatório): CSV de análise de conformidade
- `[output]` (opcional): Caminho para salvar PDF

**Exemplos:**
```
/export-pdf analysis_conformidade.csv
/export-pdf data/deliveries/.../analysis_conformidade.csv relatorio.pdf
```

**Saída:**
- Arquivo PDF com:
  - Capa executiva
  - Resumo estatístico
  - Tabelas formatadas por veredicto
  - Código de cores

**Tempo estimado:** < 1 minuto

---

### `/export-excel`

**Função:** Gera planilha Excel com múltiplas abas.

**Sintaxe:**
```
/export-excel <csv> [output]
```

**Parâmetros:**
- `<csv>` (obrigatório): CSV de análise de conformidade
- `[output]` (opcional): Caminho para salvar Excel

**Exemplos:**
```
/export-excel analysis_conformidade.csv
/export-excel data/deliveries/.../analysis_conformidade.csv relatorio.xlsx
```

**Saída:**
- Arquivo Excel (.xlsx) com:
  - Aba "Resumo" com estatísticas
  - Aba "Detalhes" com análise completa
  - Abas por veredicto (Conforme, Não Conforme, Revisão)
  - Formatação condicional
  - Gráficos automáticos

**Tempo estimado:** < 1 minuto

---

### `/search`

**Função:** Busca rápida na base de conhecimento (RAG).

**Sintaxe:**
```
/search "<query>"
```

**Parâmetros:**
- `<query>` (obrigatório): Texto da busca (entre aspas se contiver espaços)

**Exemplos:**
```
/search "prazo validade proposta Lei 8666"
/search "requisitos câmera IP 4MP"
/search "certificação INMETRO"
```

**Saída:**
- Top 5 resultados com score de similaridade
- Citação de fonte (documento:linha)
- Destaque de alta confiança (≥0.85)

**Tempo estimado:** Instantâneo

---

## 📊 Navegação e Histórico

Comandos para gerenciar e revisar análises anteriores.

### `/list-analyses`

**Função:** Lista histórico de análises realizadas.

**Sintaxe:**
```
/list-analyses [n]
```

**Parâmetros:**
- `[n]` (opcional): Número de análises a listar (padrão: 10, máx: 50)

**Exemplos:**
```
/list-analyses
/list-analyses 20
```

**Saída:**
- Lista em ordem cronológica reversa (mais recentes primeiro)
- ID, data, edital, status
- Resumo estatístico de cada análise

**Tempo estimado:** Instantâneo

---

### `/session`

**Função:** Exibe detalhes completos de uma sessão específica.

**Sintaxe:**
```
/session <id>
```

**Parâmetros:**
- `<id>` (obrigatório): Session ID (obtido via `/list-analyses`)

**Exemplos:**
```
/session 20251118_143022
/session 20251114_103501_edital_obras_publicas
```

**Saída:**
- Metadados da sessão (ID, data, duração)
- Informações do edital (nome, tamanho, páginas)
- Estatísticas de extração
- Estatísticas de análise
- Arquivos gerados
- Timeline de execução
- Itens críticos flagados

**Tempo estimado:** Instantâneo

---

### `/help`

**Função:** Mostra lista de comandos disponíveis.

**Sintaxe:**
```
/help
```

**Exemplos:**
```
/help
```

**Saída:**
- Lista de todos os comandos organizados por categoria
- Exemplos de uso
- Workflow típico completo
- Links para documentação

**Tempo estimado:** Instantâneo

---

## 📚 Sintaxe e Convenções

### Notação de Parâmetros

- **`<parametro>`** = Obrigatório
- **`[parametro]`** = Opcional
- **`"texto"`** = Usar aspas quando houver espaços

### Caminhos de Arquivo

**Absolutos:**
```
/structure-edital /home/user/editais/edital_001.pdf
```

**Relativos (a partir da raiz do projeto):**
```
/structure-edital data/uploads/edital_001.pdf
```

**Nome do arquivo (se estiver na pasta atual):**
```
/structure-edital edital.pdf
```

### Autocompletar

Use **TAB** para autocompletar caminhos de arquivo ao digitar comandos.

---

## 🔄 Fluxos de Trabalho

### Workflow Completo (Análise de Edital)

**Passo 1: Validar PDF**
```
/validate-pdf edital_001.pdf
```
⏱️ < 5 segundos

**Passo 2: Extrair requisitos**
```
/structure-edital edital_001.pdf
```
⏳ Aguardar conclusão (~10-30 min)

**Passo 3: Analisar conformidade**
```
/analyze-edital data/deliveries/20251118_143022_edital_001/outputs/requirements_structured.csv
```
⏳ Aguardar conclusão (~15-45 min)

**Passo 4: Gerar relatórios**
```
/export-pdf data/deliveries/20251118_143022_edital_001/outputs/analysis_conformidade.csv
/export-excel data/deliveries/20251118_143022_edital_001/outputs/analysis_conformidade.csv
```
⏱️ < 1 minuto cada

**Tempo total:** 30-80 minutos

---

### Workflow de Consulta Rápida

**Buscar informação específica na base:**
```
/search "prazo de validade de propostas Lei 8666"
```
⏱️ Instantâneo

**Caso de uso:**
- Verificar requisitos legais
- Consultar especificações técnicas
- Validar interpretações

---

### Workflow de Revisão de Análise Anterior

**Passo 1: Listar análises**
```
/list-analyses 10
```

**Passo 2: Ver detalhes de uma**
```
/session 20251118_143022
```

**Passo 3: Exportar novamente (se necessário)**
```
/export-pdf data/deliveries/20251118_143022_edital_001/outputs/analysis_conformidade.csv
```

---

## 🆘 Suporte

**Ver todos os comandos:**
```
/help
```

**Documentação adicional:**
- [USER_GUIDE.md](USER_GUIDE.md) - Guia do usuário completo
- [FAQ.md](FAQ.md) - Perguntas frequentes
- [TUTORIAL.md](TUTORIAL.md) - Tutorial passo a passo

---

## 📌 Resumo Rápido

| Comando | Função | Tempo |
|---------|--------|-------|
| `/validate-pdf <pdf>` | Valida PDF | < 5s |
| `/structure-edital <pdf>` | Extrai requisitos | 10-30 min |
| `/analyze-edital <csv>` | Analisa conformidade | 15-45 min |
| `/export-pdf <csv>` | Gera relatório PDF | < 1 min |
| `/export-excel <csv>` | Gera planilha Excel | < 1 min |
| `/search "<query>"` | Busca RAG | Instantâneo |
| `/list-analyses [n]` | Lista histórico | Instantâneo |
| `/session <id>` | Detalhes da sessão | Instantâneo |
| `/help` | Lista comandos | Instantâneo |

---

**Versão:** 2.0
**Compatível com:** BidAnalyzee Sprint 10+
**Interface:** Claude Code (slash commands)
