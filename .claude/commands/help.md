---
description: Show all available commands with descriptions and usage examples
---

# Help - Command Reference

Lists all available BidAnalyzee commands with descriptions and examples.

## Usage

```
/help
```

## What to do

When this command is executed, display the complete command reference organized by category:

```
🆘 BIDANALYZEE - COMANDOS DISPONÍVEIS
======================================

## 🔄 Workflows Completos (Análise de Editais)

### /structure-edital <pdf>
Extrai e estrutura requisitos de PDF do edital em formato CSV.

Exemplo:
/structure-edital data/uploads/edital_001.pdf

Tempo: 10-30 minutos
Saída: requirements_structured.csv

---

### /analyze-edital <csv>
Analisa conformidade dos requisitos contra base de conhecimento usando RAG.

Exemplo:
/analyze-edital data/deliveries/.../requirements_structured.csv

Tempo: 15-45 minutos
Saída: analysis_conformidade.csv

---

## ⚡ Ações Rápidas

### /validate-pdf <pdf>
Valida PDF antes de processar (tamanho, formato, OCR).

Exemplo:
/validate-pdf edital.pdf

Tempo: < 5 segundos

---

### /export-pdf <csv> [output]
Gera relatório profissional em PDF.

Exemplo:
/export-pdf analysis_conformidade.csv

Tempo: < 1 minuto
Saída: relatorio.pdf

---

### /export-excel <csv> [output]
Gera planilha Excel com múltiplas abas.

Exemplo:
/export-excel analysis_conformidade.csv

Tempo: < 1 minuto
Saída: relatorio.xlsx

---

### /search "<query>"
Busca rápida na base de conhecimento (RAG).

Exemplo:
/search "prazo validade proposta Lei 8666"

Tempo: Instantâneo
Saída: Top 5 resultados com citações

---

## 📊 Navegação e Histórico

### /list-analyses [n]
Lista histórico de análises realizadas.

Exemplo:
/list-analyses 10

Tempo: Instantâneo
Saída: Últimas 10 análises

---

### /session <id>
Exibe detalhes completos de uma sessão específica.

Exemplo:
/session 20251118_143022

Tempo: Instantâneo
Saída: Estatísticas, arquivos, timeline

---

### /help
Mostra esta lista de comandos (comando atual).

---

## 🔄 Workflow Completo Típico

Passo 1: Validar
/validate-pdf edital.pdf

Passo 2: Extrair requisitos
/structure-edital edital.pdf

Passo 3: Analisar conformidade
/analyze-edital data/deliveries/.../requirements_structured.csv

Passo 4: Gerar relatórios
/export-pdf data/deliveries/.../analysis_conformidade.csv
/export-excel data/deliveries/.../analysis_conformidade.csv

Tempo total: 30-80 minutos

---

## 📚 Documentação Completa

- Referência de comandos: docs/COMMAND_REFERENCE.md
- Guia do usuário: docs/USER_GUIDE.md
- FAQ: docs/FAQ.md
- Tutorial: docs/TUTORIAL.md

---

## 💡 Dicas

- Use TAB para autocompletar caminhos de arquivo
- Caminhos podem ser absolutos ou relativos
- Use aspas em queries com espaços: /search "texto com espaços"
- Veja análises anteriores com /list-analyses antes de começar nova

---

Precisa de ajuda específica? Consulte a documentação ou pergunte diretamente!
```

## Documentation Links

After displaying the help, remind the user about the detailed documentation:

```
📖 Para documentação detalhada:

- **COMMAND_REFERENCE.md** - Sintaxe completa de todos os comandos
- **USER_GUIDE.md** - Guia do usuário com workflows
- **FAQ.md** - Perguntas frequentes
- **TUTORIAL.md** - Tutorial passo a passo

Localizados em: docs/
```

## Related Commands

- `/list-analyses` - See analysis history
- `/search "<query>"` - Quick RAG search
- All other commands listed above
