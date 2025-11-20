# BidAnalyzee - Referência de Comandos

**Versão:** 1.0
**Última atualização:** 18 de novembro de 2025

---

## 📋 Índice

1. [Slash Commands](#slash-commands) - Workflows estruturados
2. [Comandos Rápidos](#comandos-rápidos) - Ações pontuais
3. [Sintaxe e Exemplos](#sintaxe-e-exemplos)
4. [Fluxos de Trabalho](#fluxos-de-trabalho)

---

## ⚡ Slash Commands

Comandos estruturados para workflows complexos. Expandem prompts completos com governança SHIELD.

### `/structure-edital`

**Função:** Extrai e estrutura requisitos de PDF do edital em formato CSV.

**Sintaxe:**
```
/structure-edital <caminho-do-pdf>
```

**Parâmetros:**
- `<caminho-do-pdf>` (obrigatório): Caminho para arquivo PDF do edital

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
/analyze-edital <caminho-do-csv>
```

**Parâmetros:**
- `<caminho-do-csv>` (obrigatório): Caminho para CSV de requisitos (gerado por `/structure-edital`)

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

## 🎯 Comandos Rápidos

Comandos simples para ações pontuais. Use prefixo `*` seguido do comando.

### `*ajuda`

**Função:** Lista todos os comandos disponíveis.

**Sintaxe:**
```
*ajuda
```

**Exemplos:**
```
*ajuda
```

**Saída:** Lista de comandos com descrições.

---

### `*buscar`

**Função:** Busca rápida na base de conhecimento usando RAG.

**Sintaxe:**
```
*buscar "<query>"
```

**Parâmetros:**
- `<query>` (obrigatório): Texto da busca (entre aspas)

**Exemplos:**
```
*buscar "prazo validade proposta"
*buscar "requisitos câmera IP 4MP"
*buscar "certificação INMETRO"
```

**Saída:**
- Top 5 resultados com score de similaridade
- Citação de fonte (documento:linha)
- Destaque de alta confiança (≥0.85)

**Tempo estimado:** Instantâneo (< 5 segundos)

---

### `*listar_analises`

**Função:** Exibe histórico de análises de editais realizadas.

**Sintaxe:**
```
*listar_analises [quantidade]
```

**Parâmetros:**
- `[quantidade]` (opcional): Número de análises a listar (padrão: 10)

**Exemplos:**
```
*listar_analises
*listar_analises 20
```

**Saída:**
- Lista com ID, data, edital, status

---

### `*sessao`

**Função:** Exibe detalhes completos de uma sessão de análise específica.

**Sintaxe:**
```
*sessao <session-id>
```

**Parâmetros:**
- `<session-id>` (obrigatório): ID da sessão (obtido via `*listar_analises`)

**Exemplos:**
```
*sessao abc123def456
*sessao 20251118_143022
```

**Saída:**
- Detalhes da sessão
- Estatísticas
- Arquivos gerados
- Log de execução

---

### `*validar`

**Função:** Valida PDF antes de processamento.

**Sintaxe:**
```
*validar <caminho-do-pdf>
```

**Parâmetros:**
- `<caminho-do-pdf>` (obrigatório): Caminho para arquivo PDF

**Exemplos:**
```
*validar edital.pdf
*validar data/uploads/edital_001.pdf
```

**Saída:**
- Status de validação (✅ aprovado / ❌ reprovado)
- Tamanho do arquivo
- Número de páginas
- Necessidade de OCR
- Texto extraível

**Tempo estimado:** Instantâneo (< 5 segundos)

---

### `*exportar-pdf`

**Função:** Gera relatório profissional em PDF a partir do CSV de análise.

**Sintaxe:**
```
*exportar-pdf <caminho-do-csv> [caminho-saida]
```

**Parâmetros:**
- `<caminho-do-csv>` (obrigatório): CSV de análise de conformidade
- `[caminho-saida]` (opcional): Caminho para salvar PDF

**Exemplos:**
```
*exportar-pdf analysis_conformidade.csv
*exportar-pdf data/deliveries/.../analysis_conformidade.csv relatorio_edital_001.pdf
```

**Saída:**
- Arquivo PDF com:
  - Capa executiva
  - Resumo estatístico
  - Tabelas formatadas por veredicto
  - Código de cores

**Tempo estimado:** < 1 minuto

---

### `*exportar-excel`

**Função:** Gera planilha Excel com múltiplas abas a partir do CSV de análise.

**Sintaxe:**
```
*exportar-excel <caminho-do-csv> [caminho-saida]
```

**Parâmetros:**
- `<caminho-do-csv>` (obrigatório): CSV de análise de conformidade
- `[caminho-saida]` (opcional): Caminho para salvar Excel

**Exemplos:**
```
*exportar-excel analysis_conformidade.csv
*exportar-excel data/deliveries/.../analysis_conformidade.csv relatorio_edital_001.xlsx
```

**Saída:**
- Arquivo Excel (.xlsx) com:
  - Aba "Resumo" com estatísticas
  - Aba "Detalhes" com análise completa
  - Abas por veredicto (Conforme, Não Conforme, etc.)
  - Formatação condicional
  - Gráficos automáticos

**Tempo estimado:** < 1 minuto

---

## 📚 Sintaxe e Exemplos

### Convenções

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

**Nome do arquivo (se estiver na raiz):**
```
/structure-edital edital.pdf
```

---

## 🔄 Fluxos de Trabalho

### Fluxo Completo (Análise de Edital)

**Passo 1:** Validar PDF
```
*validar edital_001.pdf
```

**Passo 2:** Extrair requisitos
```
/structure-edital edital_001.pdf
```
⏳ Aguardar conclusão (~10-30 min)

**Passo 3:** Analisar conformidade
```
/analyze-edital data/deliveries/20251118_143022_edital_001/outputs/requirements_structured.csv
```
⏳ Aguardar conclusão (~15-45 min)

**Passo 4:** Gerar relatórios
```
*exportar-pdf data/deliveries/20251118_143022_edital_001/outputs/analysis_conformidade.csv
*exportar-excel data/deliveries/20251118_143022_edital_001/outputs/analysis_conformidade.csv
```

**Total:** ~30-80 minutos

---

### Fluxo de Consulta Rápida

**Buscar informação específica na base:**
```
*buscar "prazo de validade de propostas Lei 8666"
```

**Resultado:** Instantâneo (< 5 segundos)

---

### Fluxo de Revisão de Análise Anterior

**Passo 1:** Listar análises
```
*listar_analises 10
```

**Passo 2:** Ver detalhes de uma
```
*sessao 20251118_143022
```

**Passo 3:** Exportar novamente (se necessário)
```
*exportar-pdf data/deliveries/20251118_143022_edital_001/outputs/analysis_conformidade.csv
```

---

## 📊 Comparação: Slash vs Asterisco

| Aspecto | Slash Commands | Comandos Asterisco |
|---------|----------------|-------------------|
| **Uso** | Workflows complexos | Ações pontuais |
| **Duração** | Minutos a horas | Segundos a minutos |
| **Governança** | Framework SHIELD completo | Execução direta |
| **Interação** | Checkpoints de aprovação | Automático |
| **Exemplos** | `/structure-edital`, `/analyze-edital` | `*buscar`, `*validar`, `*exportar-pdf` |

---

## 🆘 Precisa de Ajuda?

**Lista de comandos:**
```
*ajuda
```

**Documentação completa:**
- [USER_GUIDE.md](USER_GUIDE.md) - Guia do usuário
- [FAQ.md](FAQ.md) - Perguntas frequentes
- [TUTORIAL.md](TUTORIAL.md) - Tutorial passo a passo

---

**Versão:** 1.0
**Compatível com:** BidAnalyzee Sprint 10+
