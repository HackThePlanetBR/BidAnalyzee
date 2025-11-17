# Comparação de Editais - BidAnalyzee

## 📋 Visão Geral

A funcionalidade de **Comparação de Editais** permite analisar múltiplos editais simultaneamente, identificando:

- ✅ **Requisitos idênticos** - Exatamente iguais entre editais
- ⚠️ **Requisitos similares** - Parecidos mas com diferenças (divergentes)
- 🔵 **Requisitos únicos** - Presentes em apenas um edital
- 📊 **Taxa de sobreposição** - Percentual de requisitos em comum

## 🎯 Casos de Uso

### 1. Empresa Participa de Múltiplas Licitações

**Cenário:** Sua empresa quer participar de 3 licitações diferentes de videomonitoramento.

**Problema:** Quais requisitos são comuns? Onde estão as diferenças críticas?

**Solução:**
```bash
python scripts/compare_editais.py \
  edital_prefeitura_A.csv \
  edital_prefeitura_B.csv \
  edital_prefeitura_C.csv
```

**Resultado:** Relatório mostrando:
- Requisitos comuns aos 3 editais (investimento único)
- Requisitos únicos a cada edital (investimentos específicos)
- Taxa de sobreposição (viabilidade de atender múltiplas licitações)

### 2. Análise de Viabilidade

**Cenário:** Sua empresa já venceu uma licitação e quer saber se consegue atender outra similar.

**Problema:** O edital novo é muito diferente do anterior?

**Solução:**
```bash
python scripts/compare_editais.py edital_anterior.csv edital_novo.csv
```

**Resultado:**
- Se sobreposição > 70%: Viável com poucas adaptações
- Se sobreposição 40-70%: Viável com investimentos moderados
- Se sobreposição < 40%: Requer análise detalhada de viabilidade

### 3. Benchmarking de Editais

**Cenário:** Você quer entender o que é padrão vs. específico em editais de um domínio.

**Problema:** Quais requisitos são comuns a todos os editais de TI?

**Solução:**
```bash
python scripts/compare_editais.py editais_ti/*.csv
```

**Resultado:**
- Requisitos presentes em 100% dos editais = padrão do setor
- Requisitos únicos = especificidades de cada órgão

## 🚀 Como Usar

### Instalação

Nenhuma dependência adicional necessária. O script usa apenas bibliotecas padrão do Python.

### Uso Básico

#### Comparar 2 Editais

```bash
python scripts/compare_editais.py edital_A.csv edital_B.csv
```

**Saída:**
```
================================================================================
📊 RELATÓRIO DE COMPARAÇÃO DE EDITAIS
================================================================================

📄 Editais Comparados:
   • edital_A (47 requisitos)
   • edital_B (52 requisitos)

📊 Resumo da Comparação:
   ✅ Requisitos idênticos: 32
   ⚠️  Requisitos similares: 8
   🔵 Únicos ao edital_A: 7
   🔴 Únicos ao edital_B: 12

📈 Taxa de Sobreposição:
   • edital_A: 85.1%
   • edital_B: 76.9%

⚠️  Requisitos Similares mas Divergentes (Top 5):

   1. Similaridade: 92.3%
      [edital_A] Câmeras IP com resolução mínima de 1920x1080...
      [edital_B] Câmeras com resolução mínima de 4K (3840x2160)...

   2. Similaridade: 88.7%
      [edital_A] Armazenamento de 30 dias de gravação...
      [edital_B] Armazenamento de 60 dias de gravação...
```

#### Comparar 3+ Editais

```bash
python scripts/compare_editais.py edital_A.csv edital_B.csv edital_C.csv
```

**Saída:**
```
================================================================================
📊 RELATÓRIO DE COMPARAÇÃO DE EDITAIS
================================================================================

📄 Editais Comparados (3):
   • edital_A
   • edital_B
   • edital_C

✅ Requisitos Comuns a TODOS os Editais: 25

   Exemplos (Top 5):
   1. Câmeras IP com certificação ANATEL obrigatória...
   2. Software de gestão com interface web...
   3. Garantia mínima de 36 meses...

🔍 Requisitos Únicos por Edital:
   • edital_A: 5 requisitos únicos
   • edital_B: 12 requisitos únicos
   • edital_C: 8 requisitos únicos

📊 Comparações Par a Par:
   • edital_A vs edital_B: 85.1% de sobreposição
   • edital_A vs edital_C: 78.3% de sobreposição
   • edital_B vs edital_C: 72.5% de sobreposição
```

### Opções Avançadas

#### Saída em JSON

```bash
python scripts/compare_editais.py edital_A.csv edital_B.csv --json
```

**Uso:** Integração com outras ferramentas, processamento automatizado

**Saída:**
```json
{
  "edital1": "edital_A",
  "edital2": "edital_B",
  "total_requirements": {
    "edital_A": 47,
    "edital_B": 52
  },
  "exact_matches": {
    "count": 32,
    "items": [...]
  },
  "similar_matches": {
    "count": 8,
    "items": [...]
  },
  ...
}
```

#### Ajustar Threshold de Similaridade

```bash
python scripts/compare_editais.py edital_A.csv edital_B.csv --similarity 0.90
```

**Padrão:** 0.85 (85% de similaridade)

**Valores:**
- **0.95-1.0**: Muito rigoroso (apenas requisitos quase idênticos)
- **0.85-0.95**: Balanceado (padrão) ⭐
- **0.70-0.85**: Permissivo (captura mais variações)
- **< 0.70**: Muito permissivo (pode gerar falsos positivos)

#### Usar Wildcards

```bash
# Comparar todos os editais em um diretório
python scripts/compare_editais.py data/editais/*.csv

# Comparar editais de um padrão específico
python scripts/compare_editais.py data/editais/videomonitoramento_*.csv
```

## 📊 Interpretando os Resultados

### Taxa de Sobreposição

| Taxa | Interpretação | Ação Recomendada |
|------|---------------|------------------|
| **> 80%** | Editais muito similares | Pode atender ambos com poucas adaptações |
| **60-80%** | Editais moderadamente similares | Investimentos adicionais necessários |
| **40-60%** | Editais com diferenças significativas | Análise detalhada de viabilidade |
| **< 40%** | Editais muito diferentes | Pode não ser viável atender ambos |

### Requisitos Similares mas Divergentes

**Atenção especial!** Estes são os mais críticos para análise.

**Por quê?** Parecem iguais mas têm diferenças importantes.

**Exemplo:**
```
[Edital A] "Câmeras com resolução Full HD (1920x1080)"
[Edital B] "Câmeras com resolução 4K (3840x2160)"
```

**Impacto:** Requisitos técnicos e custos diferentes!

**Ação:** Revisar TODOS os requisitos similares manualmente.

### Requisitos Únicos de Alta Prioridade

**Foco:** Requisitos marcados como "Alta" prioridade e presentes em apenas 1 edital.

**Por quê?** Podem ser:
- Especificidades locais (legislação municipal)
- Requisitos críticos que bloqueiam participação
- Diferenciais competitivos

**Exemplo:**
```
⚡ Requisitos de Alta Prioridade Únicos ao edital_B:
   • 4.2.1: Integração com sistema de gestão municipal específico...
   • 5.1.3: Certificação específica exigida apenas nesta região...
```

**Ação:** Verificar viabilidade de atender esses requisitos únicos.

## 🔧 Algoritmo de Comparação

### 1. Carregamento de Editais

```
Para cada CSV:
   Carregar requisitos (id, item, descricao, categoria, prioridade, pagina, confianca)
   Armazenar com tag de origem (nome do edital)
```

### 2. Matching de Requisitos

#### Match Exato
```
Para cada par (req_A, req_B):
   Se descricao_A.lower() == descricao_B.lower():
      ✅ Match exato
```

#### Match Similar
```
Para cada par (req_A, req_B):
   similarity = SequenceMatcher(descricao_A, descricao_B).ratio()

   Se similarity >= threshold (padrão: 0.85):
      ⚠️ Match similar (divergente)
```

**Algoritmo de Similaridade:** [Gestalt Pattern Matching](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher)

- Baseado em subsequências comuns mais longas (LCS)
- Score de 0.0 (completamente diferente) a 1.0 (idêntico)
- Rápido e eficiente para textos

### 3. Identificação de Únicos

```
Para cada requisito em Edital A:
   unique = True

   Para cada outro edital:
      Se existe match (exato ou similar) neste outro edital:
         unique = False
         break

   Se unique:
      🔵 Adicionar a "Únicos do Edital A"
```

### 4. Requisitos Comuns a Todos

```
Para cada requisito no primeiro edital:
   Verificar se tem match em TODOS os outros editais

   Se sim:
      ✅ Requisito comum a todos
```

## 📈 Casos de Uso Avançados

### 1. Pipeline Automatizado de Comparação

```bash
#!/bin/bash
# Script para comparar todos os editais novos com baseline

BASELINE="data/baseline/edital_padrao.csv"

for edital in data/novos_editais/*.csv; do
    echo "Comparando: $(basename $edital)"

    python scripts/compare_editais.py \
        "$BASELINE" \
        "$edital" \
        --json > "data/comparacoes/$(basename $edital .csv)_comparison.json"
done

echo "✅ Comparações completas em data/comparacoes/"
```

### 2. Identificar Tendências de Mercado

```bash
# Comparar todos os editais de 2024 para identificar requisitos emergentes
python scripts/compare_editais.py data/editais_2024/*.csv
```

**Análise:** Requisitos únicos que aparecem em < 30% dos editais podem ser tendências emergentes.

### 3. Validação de Conformidade

```bash
# Comparar edital do cliente com checklist de conformidade padrão
python scripts/compare_editais.py \
    data/checklist/requisitos_minimos_ANATEL.csv \
    data/editais/edital_cliente.csv
```

**Resultado:** Requisitos mínimos ausentes no edital do cliente.

### 4. Análise de Competitividade

```bash
# Comparar editais onde empresa ganhou vs. perdeu
python scripts/compare_editais.py \
    data/vencidos/*.csv \
    data/perdidos/*.csv
```

**Insight:** Identificar padrões de requisitos em licitações vencidas vs. perdidas.

## 🐛 Troubleshooting

### "CSV não encontrado"

**Causa:** Caminho inválido ou arquivo não existe

**Solução:**
```bash
# Verificar se arquivo existe
ls -lh edital_A.csv

# Usar caminho absoluto
python scripts/compare_editais.py /caminho/completo/edital_A.csv edital_B.csv
```

### "Erro ao carregar CSV"

**Causa:** CSV malformado ou encoding incorreto

**Solução:**
```bash
# Validar CSV primeiro
python scripts/validate_csv.py edital_A.csv --type requirements

# Verificar encoding
file edital_A.csv
# Deve ser: UTF-8 Unicode text
```

### Muitos "Requisitos Similares" Falsos

**Causa:** Threshold de similaridade muito baixo

**Solução:**
```bash
# Aumentar threshold
python scripts/compare_editais.py edital_A.csv edital_B.csv --similarity 0.92
```

### Poucos Matches

**Causa:**
- Threshold muito alto
- Editais realmente muito diferentes
- Descrições dos requisitos formatadas de forma muito diferente

**Solução:**
```bash
# Tentar threshold mais permissivo
python scripts/compare_editais.py edital_A.csv edital_B.csv --similarity 0.75

# Se ainda poucos matches: editais são realmente muito diferentes
```

## 🔗 Integração com Workflow

### Workflow Completo de Análise

```bash
# 1. Estruturar requisitos de múltiplos editais
python scripts/analyze_edital_full.py edital_A.pdf
python scripts/analyze_edital_full.py edital_B.pdf

# 2. Comparar requisitos estruturados
python scripts/compare_editais.py \
    data/deliveries/edital_A_*/outputs/requirements_structured.csv \
    data/deliveries/edital_B_*/outputs/requirements_structured.csv

# 3. Usar comparação para priorizar análise
# (Focar em requisitos únicos e divergentes de alta prioridade)
```

### Automação com Make

```makefile
# Makefile
compare-editais:
	@python scripts/compare_editais.py data/editais/*.csv

compare-json:
	@python scripts/compare_editais.py data/editais/*.csv --json > comparison.json

.PHONY: compare-editais compare-json
```

Uso:
```bash
make compare-editais
make compare-json
```

## 📚 Exemplos Práticos

### Exemplo 1: Dois Editais de Videomonitoramento

**Input:**
```bash
python scripts/compare_editais.py \
    data/exemplos/edital_videomonitoramento_A.csv \
    data/exemplos/edital_videomonitoramento_B.csv
```

**Output:**
```
📊 Resumo da Comparação:
   ✅ Requisitos idênticos: 38
   ⚠️  Requisitos similares: 6
   🔵 Únicos ao edital_A: 3
   🔴 Únicos ao edital_B: 8

📈 Taxa de Sobreposição:
   • edital_A: 92.9% (alta viabilidade!)
   • edital_B: 88.5%
```

**Análise:** Editais muito similares (> 88%), viável atender ambos com pequenas adaptações.

### Exemplo 2: Três Editais de TI

**Input:**
```bash
python scripts/compare_editais.py \
    edital_ti_A.csv \
    edital_ti_B.csv \
    edital_ti_C.csv
```

**Output:**
```
✅ Requisitos Comuns a TODOS os Editais: 22

🔍 Requisitos Únicos por Edital:
   • edital_ti_A: 5 requisitos únicos
   • edital_ti_B: 12 requisitos únicos
   • edital_ti_C: 8 requisitos únicos

📊 Comparações Par a Par:
   • edital_ti_A vs edital_ti_B: 78.2% de sobreposição
   • edital_ti_A vs edital_ti_C: 82.1% de sobreposição
   • edital_ti_B vs edital_ti_C: 71.4% de sobreposição
```

**Análise:**
- 22 requisitos comuns = "pacote base" para TI
- Edital B tem mais requisitos únicos (12) = mais específico
- Maior sobreposição: A-C (82%) = editais mais similares

## 💡 Dicas e Boas Práticas

### 1. Sempre Compare Requisitos Estruturados

✅ **Correto:** Comparar CSVs gerados pelo `analyze_edital_full.py`

❌ **Errado:** Comparar PDFs ou textos brutos

**Por quê?** Requisitos estruturados têm formato padronizado, facilitando comparação precisa.

### 2. Use Threshold Apropriado

- **Editais do mesmo domínio:** 0.85 (padrão)
- **Editais muito padronizados:** 0.90
- **Editais com variação de redação:** 0.80

### 3. Revise Manualmente Requisitos Similares

**Nunca confie cegamente!** Requisitos similares (85-95% match) podem ter diferenças críticas.

**Exemplo:**
```
Similaridade: 89%
[A] "Garantia de 24 meses"
[B] "Garantia de 36 meses"
```

Diferença de 1 ano = impacto significativo!

### 4. Priorize Requisitos de Alta Prioridade Únicos

Foque em:
1. Únicos + Alta prioridade
2. Divergentes + Alta prioridade
3. Comuns + Alta prioridade

**Por quê?** Maior impacto na viabilidade e custos.

### 5. Use JSON para Análises Programáticas

```bash
# Gerar JSON
python scripts/compare_editais.py A.csv B.csv --json > comparison.json

# Processar com jq (ferramenta CLI JSON)
cat comparison.json | jq '.unique_to_edital1.count'

# Ou com Python
python -c "import json; print(json.load(open('comparison.json'))['overlap_percentage'])"
```

## 📋 Checklist de Análise

Após executar a comparação, verifique:

- [ ] Taxa de sobreposição > 70%? (viabilidade geral)
- [ ] Quantos requisitos únicos de alta prioridade em cada edital?
- [ ] Todos os requisitos similares foram revisados manualmente?
- [ ] Diferenças críticas foram identificadas (valores numéricos, prazos, certificações)?
- [ ] Requisitos únicos são viáveis de atender?

## 🔄 Próximos Passos

Após comparação, você pode:

1. **Gerar relatórios customizados** (exportar para Excel, PDF)
2. **Integrar com análise de conformidade** (focar em requisitos divergentes)
3. **Criar baseline de requisitos comuns** (para futuros editais)
4. **Automatizar comparação contínua** (pipeline CI/CD)

## 📚 Referências

- [SequenceMatcher (difflib)](https://docs.python.org/3/library/difflib.html)
- [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [CSV Validation](./CSV_VALIDATION.md)

---

**Última atualização:** 16/11/2025
**Versão:** 1.0
