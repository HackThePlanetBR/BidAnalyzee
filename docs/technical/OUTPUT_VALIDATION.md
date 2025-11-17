# Validação de Outputs - BidAnalyzee

Sistema abrangente de validação de qualidade para outputs de análise.

## 📋 Visão Geral

A validação de outputs garante que as análises produzidas pelo BidAnalyzee atendam padrões de qualidade antes de serem usadas para decisões críticas.

## 🎯 Objetivos

- ✅ Garantir completude de todos os campos
- ✅ Verificar consistência lógica entre campos
- ✅ Avaliar qualidade do raciocínio (justificativas)
- ✅ Validar citações e evidências
- ✅ Detectar padrões suspeitos
- ✅ Gerar score de qualidade objetivo

## 🛠️ Ferramentas Disponíveis

### 1. Quality Check (`quality_check.py`)

**Script principal de validação avançada de qualidade.**

#### Uso:

```bash
python scripts/quality_check.py <analysis_csv>
```

#### Exemplo:

```bash
python scripts/quality_check.py data/deliveries/20251116_143000/analysis_conformidade.csv
```

#### O que verifica:

1. **Completude de Campos** (peso: 10-15 pontos)
   - Todos os campos obrigatórios presentes?
   - Campos vazios ou missing?
   - Campos obrigatórios: item, categoria, descrição, veredicto, justificativa, evidências, nível_confiança

2. **Consistência entre Campos** (peso: 10 pontos)
   - Veredicto CONFORME tem evidências?
   - Veredicto NÃO CONFORME tem justificativa adequada?
   - REQUER ANÁLISE com confiança Alta (inconsistente)?

3. **Qualidade do Raciocínio** (peso: 15 pontos)
   - Justificativas ausentes?
   - Justificativas muito curtas (< 20 chars)?
   - Justificativas curtas (< 50 chars)?

4. **Qualidade das Evidências** (peso: 10 pontos)
   - Evidências ausentes?
   - Citações malformadas (sem formato "arquivo:linha")?
   - Evidências adequadas com citação correta?

5. **Níveis de Confiança** (peso: 10 pontos)
   - Todas as linhas têm nível de confiança?
   - Distribuição adequada (não muitos "Baixo")?
   - Níveis válidos (Alto/Médio/Baixo)?

6. **Distribuição de Veredictos** (peso: 5 pontos)
   - Veredictos reconhecidos?
   - Padrões suspeitos (100% conforme, 0% conforme)?
   - Muitos "REQUER ANÁLISE" (> 30%)?

#### Score de Qualidade:

- **90-100**: 🟢 EXCELENTE - Pronto para uso
- **75-89**: 🟡 BOM - Revisar avisos menores
- **60-74**: 🟠 ACEITÁVEL - Revisar erros antes de usar
- **< 60**: 🔴 PRECISA MELHORIAS - NÃO usar sem revisão

#### Saída:

```
================================================================================
📊 RELATÓRIO DE QUALIDADE
================================================================================

🟢 Score de Qualidade: 92.0/100 - EXCELENTE
📄 Total de linhas analisadas: 87
✅ Verificações aprovadas: 5
❌ Verificações falhadas: 1

📋 Verificações:
  ✅ Completude de Campos
      Campos obrigatórios: item, categoria, descricao, veredicto, ...
  ✅ Consistência entre Campos
      Nenhuma inconsistência
  ⚠️  Qualidade do Raciocínio
      5 justificativas problemáticas
  ✅ Qualidade das Evidências
      82 citações adequadas, 3 malformadas, 2 ausentes
  ✅ Níveis de Confiança
      Alto: 65, Médio: 18, Baixo: 4
  ✅ Distribuição de Veredictos
      Conforme: 74.7%, NC: 9.2%, Parcial: 11.5%, Requer: 4.6%

⚠️  Avisos (1):
  - 5 justificativas muito curtas

💡 Recomendações:
  ✅ Qualidade excelente! Nenhuma ação necessária.

================================================================================
```

### 2. CSV Validation (`validate_csv.py`)

**Validação básica de estrutura de CSV.**

#### Uso:

```bash
python scripts/validate_csv.py <csv_file> [--type requirements|analysis]
```

#### O que verifica:

- Encoding válido (UTF-8)
- Estrutura CSV bem formada
- Colunas obrigatórias presentes
- Tipos de dados básicos
- Duplicatas (por campo `item`)
- Campos vazios críticos

### 3. PDF Validation (`validate_pdf.py`)

**Validação de PDFs antes de processar.**

#### Uso:

```bash
python scripts/validate_pdf.py <pdf_file>
```

#### O que verifica:

- Arquivo existe e é acessível
- Tamanho dentro do limite (500MB)
- Formato PDF válido
- Não está corrompido
- Contém texto extraível
- Metadados básicos

## 📊 Métricas de Qualidade

### Completude (0-15 pontos)

**Critérios:**
- **-10 pontos**: Campo obrigatório ausente
- **-5 pontos**: > 10% das linhas com campo vazio
- **-1 ponto**: Qualquer linha com campo vazio

**Exemplo:**
```
❌ Campo 'evidencias' vazio em 12 linhas (13.8%)
✅ Campo 'justificativa' completo em todas as linhas
```

### Consistência (0-10 pontos)

**Critérios:**
- **-10 pontos**: > 5% de inconsistências
- **-2 pontos**: < 5% de inconsistências

**Inconsistências detectadas:**
- CONFORME sem evidências
- NÃO CONFORME com justificativa curta (< 20 chars)
- REQUER ANÁLISE com confiança Alta

**Exemplo:**
```
❌ Linha 45: CONFORME sem evidências adequadas
❌ Linha 67: NÃO CONFORME com justificativa curta
```

### Raciocínio (0-15 pontos)

**Critérios:**
- **-15 pontos**: Linhas sem justificativa
- **-5 pontos**: > 10% justificativas muito curtas (< 20 chars)
- **-1 ponto**: > 30% justificativas curtas (< 50 chars)

**Exemplo:**
```
❌ 3 linhas sem justificativa
⚠️  8 justificativas muito curtas (< 20 chars, 9.2%)
```

### Evidências (0-10 pontos)

**Critérios:**
- **-10 pontos**: > 10% sem evidências
- **-2 pontos**: < 10% sem evidências
- **-3 pontos**: > 20% citações malformadas

**Formato esperado:** `arquivo.md:123`

**Exemplo:**
```
✅ 82 citações adequadas (Lei_8666.md:120, requisitos.md:45)
⚠️  3 malformadas ("conforme legislação")
❌ 2 ausentes
```

### Confiança (0-10 pontos)

**Critérios:**
- **-10 pontos**: Linhas sem nível de confiança
- **-5 pontos**: > 50% com confiança Baixa (sistema incerto)

**Exemplo:**
```
✅ Todas as linhas com nível de confiança
⚠️  60% com confiança Baixa (sistema pouco confiante?)
```

### Veredictos (0-5 pontos)

**Critérios:**
- **-5 pontos**: Veredictos não reconhecidos

**Padrões suspeitos (avisos):**
- 100% CONFORME → viés otimista?
- 0% CONFORME → edital inadequado?
- > 30% REQUER ANÁLISE → muita incerteza

**Exemplo:**
```
✅ Todos os veredictos reconhecidos
⚠️  35% REQUER ANÁLISE - sistema com muita incerteza
```

## 🔄 Workflow Recomendado

### 1. Validação Durante Análise

```bash
# Após estruturação
python scripts/validate_csv.py requirements.csv --type requirements

# Após análise
python scripts/validate_csv.py analysis.csv --type analysis
```

### 2. Verificação de Qualidade

```bash
# Validação avançada
python scripts/quality_check.py analysis.csv

# Se score < 60: revisar e reprocessar
# Se score >= 75: aprovado para uso
```

### 3. Automatização

```python
from scripts.quality_check import QualityChecker

checker = QualityChecker()
report = checker.check_analysis_csv("analysis.csv")

if report["score"] < 75:
    print("⚠️  Qualidade insuficiente, reprocessar")
    # Ajustar configs, reprocessar
else:
    print("✅ Qualidade aprovada")
    # Prosseguir com exports
```

## ⚙️ Integração com CI/CD

### GitHub Actions (exemplo)

```yaml
- name: Validate Analysis Quality
  run: |
    python scripts/quality_check.py data/test_analysis.csv
    if [ $? -ne 0 ]; then
      echo "Quality check failed"
      exit 1
    fi
```

### Pre-commit Hook (exemplo)

```bash
#!/bin/bash
# .git/hooks/pre-commit

for csv in $(git diff --cached --name-only --diff-filter=ACM | grep analysis.*\.csv); do
    python scripts/quality_check.py "$csv"
    if [ $? -ne 0 ]; then
        echo "Quality check failed for $csv"
        exit 1
    fi
done
```

## 📈 Melhorando o Score

### Se Score < 60:

**Ações imediatas:**
1. Revisar erros listados
2. Verificar se base de conhecimento é adequada
3. Ajustar threshold RAG (aumentar se muitos "REQUER ANÁLISE")
4. Reprocessar análise

### Se Score 60-75:

**Ações recomendadas:**
1. Revisar avisos
2. Melhorar evidências com citações corretas
3. Expandir justificativas curtas
4. Validar manualmente itens críticos

### Se Score 75-90:

**Ações opcionais:**
1. Revisar avisos menores
2. Melhorar formatação de evidências
3. Expandir justificativas quando relevante

### Se Score > 90:

**Aprovado!** ✅
- Nenhuma ação necessária
- Qualidade excelente para decisões

## 🎯 Casos de Uso

### Caso 1: Análise para Go/No-Go

```bash
# Validar qualidade antes de decidir
python scripts/quality_check.py analysis.csv

# Se score >= 75: confiar na análise
# Se score < 75: revisar manualmente itens críticos
```

### Caso 2: Auditoria de Qualidade

```bash
# Verificar qualidade de múltiplas análises
for analysis in data/deliveries/*/analysis_conformidade.csv; do
    echo "Analisando $analysis"
    python scripts/quality_check.py "$analysis"
done
```

### Caso 3: Continuous Integration

```bash
# CI pipeline
python scripts/quality_check.py test_analysis.csv
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Quality check failed"
    exit 1
fi
```

## 🐛 Troubleshooting

### "Score muito baixo (< 40)"

**Possíveis causas:**
- Base de conhecimento inadequada
- Edital fora do domínio esperado
- Configurações RAG inadequadas (threshold muito alto)

**Soluções:**
1. Adicionar documentos relevantes à KB
2. Re-indexar KB
3. Ajustar threshold RAG (reduzir de 0.70 para 0.60)
4. Usar template apropriado

### "Muitas evidências malformadas"

**Causa:** Sistema não está citando fontes corretamente

**Solução:**
1. Verificar se KB está indexada
2. Verificar se scripts RAG estão funcionando
3. Revisar prompts do Technical Analyst

### "Muitos REQUER ANÁLISE"

**Causa:** Sistema com baixa confiança

**Possíveis motivos:**
- KB não cobre o domínio
- Requisitos muito específicos/técnicos
- Threshold RAG muito alto

**Solução:**
1. Expandir KB com docs relevantes
2. Reduzir threshold RAG
3. Aceitar que análise manual será necessária

## 📚 Referências

- [quality_check.py](../scripts/quality_check.py) - Script principal
- [validate_csv.py](../scripts/validate_csv.py) - Validação CSV
- [validate_pdf.py](../scripts/validate_pdf.py) - Validação PDF

---

**Última atualização:** 16/11/2025
**Versão:** 1.0
