# STRUCTURE Phase - Exemplos Práticos

**Versão:** 1.0
**Propósito:** Demonstrar como diferentes agentes usam a capacidade STRUCTURE

---

## 📚 Índice de Exemplos

1. [Exemplo 1: Estruturação de Edital](#exemplo-1-estruturação-de-edital) (@EstruturadorDeDocumentos)
2. [Exemplo 2: Análise de Conformidade](#exemplo-2-análise-de-conformidade) (@AnalistaTecnico)
3. [Exemplo 3: Workflow Completo](#exemplo-3-workflow-completo) (@Orquestrador)

---

## Exemplo 1: Estruturação de Edital

**Agente:** @EstruturadorDeDocumentos
**Objetivo:** Transformar um PDF de edital em CSV estruturado
**Complexidade:** Média

### Entrada do Usuário

```
Usuário: Estruture o arquivo "edital_prefeitura_sp_2025.pdf" em CSV
```

### Fase STRUCTURE (Passo a Passo)

#### 1. INTERPRETAÇÃO

**Agente apresenta:**

```markdown
📋 Meu Entendimento da Tarefa

Objetivo: Extrair requisitos técnicos do edital e estruturá-los em formato CSV

Inputs:
- Arquivo: edital_prefeitura_sp_2025.pdf
- Localização: (assumindo que está em ./edital_prefeitura_sp_2025.pdf)

Outputs esperados:
- CSV com colunas: ID, Descrição, Tipo, Categoria
- Localização: data/analyses/[novo_ID]/requisitos_estruturados.csv
- Log de execução: data/analyses/[novo_ID]/logs.txt

Critérios de Sucesso:
- Todos os requisitos extraídos (100%)
- Cada requisito é uma linha única
- Zero duplicatas
- CSV válido e abre em Excel

Confirme se meu entendimento está correto antes de eu prosseguir com o plano.
```

**Usuário confirma:** ✅ "Correto, prossiga"

---

#### 2. DECOMPOSIÇÃO

**Agente planeja 6 etapas:**

```yaml
steps:
  - id: 1
    name: "Validar arquivo de entrada"
    estimated_time: "10s"

  - id: 2
    name: "Extrair texto completo do PDF"
    estimated_time: "1min 30s"

  - id: 3
    name: "Identificar seção de especificações técnicas"
    estimated_time: "30s"

  - id: 4
    name: "Extrair requisitos individuais"
    estimated_time: "2min"

  - id: 5
    name: "Estruturar requisitos em CSV"
    estimated_time: "1min"

  - id: 6
    name: "Salvar arquivos e gerar logs"
    estimated_time: "20s"
```

---

#### 3. CHECKPOINTS

```yaml
checkpoints_por_etapa:
  etapa_1:
    - INSPECT: "Arquivo existe e é válido"

  etapa_2:
    - INSPECT: "Texto extraído sem erros"
    - VALIDATE: "Texto tem > 1000 caracteres"

  etapa_4:
    - INSPECT: "Requisitos estão individualizados"
    - VALIDATE: "Número de requisitos > 0"

  etapa_5:
    - INSPECT: "CSV formatado corretamente"
    - VALIDATE: "100% dos requisitos incluídos"
    - HALT: "Apresentar CSV para aprovação do usuário"

  etapa_6:
    - VALIDATE: "Arquivos salvos com sucesso"
```

---

#### 4. ESTIMATIVAS

```yaml
resources:
  estimated_duration:
    optimistic: "3min"
    realistic: "5min 30s"
    pessimistic: "10min"

  estimated_tokens: 8000

  estimated_disk_space: "500KB"
```

---

#### 5. RISCOS

```yaml
risks:
  - risk: "PDF está protegido por senha ou corrompido"
    probability: "low"
    impact: "high"
    mitigation: "Validar integridade na etapa 1 antes de processar"
    contingency: "HALT e solicitar ao usuário um arquivo válido"

  - risk: "Documento não tem estrutura padrão (requisitos em formato não esperado)"
    probability: "medium"
    impact: "medium"
    mitigation: "Usar múltiplas estratégias de parsing (regex, NLP)"
    contingency: "Marcar seções problemáticas para revisão humana"

  - risk: "Número de requisitos excede estimativa (>200 itens)"
    probability: "low"
    impact: "medium"
    mitigation: "Processar em lotes de 50 requisitos"
    contingency: "Informar usuário sobre tempo adicional necessário"
```

---

#### 6. CRITÉRIOS DE SUCESSO

```yaml
success_criteria:
  - "100% dos requisitos do documento foram extraídos"
  - "CSV gerado tem todas as colunas obrigatórias [ID, Descrição, Tipo, Categoria]"
  - "Zero requisitos duplicados (validado por hash de conteúdo)"
  - "IDs são sequenciais de 1 a N sem gaps"
  - "Arquivo CSV é válido e abre sem erros em Excel/LibreOffice"
  - "Log completo foi gerado para auditoria"
```

---

#### 7. APRESENTAÇÃO DO PLANO

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PLANO DE EXECUÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Tarefa:** Estruturação de Edital em CSV
**Duração Estimada:** 5min 30s (realista)
**Modo:** Assistido

## Etapas

1. Validar arquivo de entrada (~10s)
   → Verificar existência, formato e integridade
   ✓ Checkpoint: INSPECT

2. Extrair texto completo do PDF (~1min 30s)
   → Usar PyPDF2 para extração
   ✓ Checkpoints: INSPECT, VALIDATE

3. Identificar seção de especificações técnicas (~30s)
   → Localizar seção com requisitos
   ✓ Checkpoint: INSPECT

4. Extrair requisitos individuais (~2min)
   → Parsear cada requisito como item único
   ✓ Checkpoints: INSPECT, VALIDATE

5. Estruturar requisitos em CSV (~1min)
   → Criar CSV com colunas [ID, Descrição, Tipo, Categoria]
   ✓ Checkpoints: INSPECT, VALIDATE
   ⏸️  Checkpoint: HALT (Aprovação do usuário)

6. Salvar arquivos e gerar logs (~20s)
   → Persistir CSV e logs
   ✓ Checkpoint: VALIDATE

## Pontos de Parada (HALTs)

- Após etapa 5: Usuário valida se requisitos foram extraídos corretamente

## Recursos Estimados

- ⏱️  Duração: 3min - 5min 30s - 10min
- 🔢 Tokens: ~8,000
- 💾 Espaço: ~500KB

## Riscos Identificados

⚠️  PDF protegido ou corrompido (Probabilidade: Baixa, Impacto: Alto)
   → Mitigação: Validar integridade antes de processar

⚠️  Estrutura não-padrão (Probabilidade: Média, Impacto: Médio)
   → Mitigação: Parser robusto com múltiplas estratégias

⚠️  Volume maior que estimado (Probabilidade: Baixa, Impacto: Médio)
   → Mitigação: Processar em lotes

## Critérios de Sucesso

✅ 100% dos requisitos extraídos
✅ CSV com todas as colunas obrigatórias
✅ Zero duplicatas
✅ IDs sequenciais sem gaps
✅ CSV válido (abre em Excel)
✅ Logs completos gerados

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Por favor, escolha uma opção:

1. ✅ Aprovar e prosseguir com o plano
2. 🔄 Sugerir ajustes ao plano
3. 👁️  Ver detalhes técnicos completos (YAML)
4. ❌ Cancelar tarefa

Sua escolha [1-4]:
```

---

## Exemplo 2: Análise de Conformidade

**Agente:** @AnalistaTecnico
**Objetivo:** Analisar conformidade de requisitos contra base de conhecimento
**Complexidade:** Alta

### Entrada do Usuário

```
Usuário: Analise a conformidade do CSV "requisitos_estruturados.csv"
```

### Fase STRUCTURE (Resumida)

#### 1. INTERPRETAÇÃO

```markdown
📋 Meu Entendimento da Tarefa

Objetivo: Analisar cada requisito do CSV contra a base de conhecimento (Pinecone)
         e gerar CSV de resultado com status de conformidade

Inputs:
- CSV de entrada: requisitos_estruturados.csv (47 linhas)
- Base de conhecimento: Pinecone (via n8n microsserviço)
- Threshold de confiança: 0.85 (do .env)

Outputs esperados:
- CSV de resultado com colunas adicionais: Status, Justificativa, Evidência, Produto, Link, Confiança
- Localização: data/analyses/[ID]/resultado_analise.csv

Critérios de Sucesso:
- Todos os 47 requisitos analisados (100%)
- Cada análise tem evidência da base de conhecimento
- Items com confiança < 85% marcados para revisão humana
- Precisão geral > 85% (NFR2)

Confirme se está correto.
```

---

#### 2. DECOMPOSIÇÃO (Simplificada)

```yaml
steps:
  - id: 1
    name: "Validar CSV de entrada e conectividade com n8n"
    estimated_time: "20s"

  - id: 2
    name: "Processar lote 1 (requisitos 1-25)"
    estimated_time: "10min"

  - id: 3
    name: "Processar lote 2 (requisitos 26-47)"
    estimated_time: "9min"

  - id: 4
    name: "Consolidar resultados e identificar itens para revisão"
    estimated_time: "1min"

  - id: 5
    name: "Gerar CSV de resultado e relatório"
    estimated_time: "30s"
```

---

#### 3. CHECKPOINTS CHAVE

```yaml
checkpoints:
  etapa_2:
    - INSPECT: "Cada requisito do lote foi analisado"
    - VALIDATE: "25 requisitos processados (100% do lote)"
    - HALT: "Apresentar resultados do lote 1 para validação"

  etapa_4:
    - INSPECT: "Itens de baixa confiança foram identificados"
    - VALIDATE: "47 requisitos processados no total (100%)"

  etapa_5:
    - INSPECT: "CSV final tem todas as colunas obrigatórias"
    - VALIDATE: "Número de linhas do output = número de linhas do input"
    - HALT: "Apresentar análise final para aprovação"
```

---

#### 4. RISCOS ESPECÍFICOS

```yaml
risks:
  - risk: "Microsserviço n8n está offline ou lento"
    probability: "medium"
    impact: "high"
    mitigation: "Testar conectividade na etapa 1"
    contingency: "HALT e notificar usuário sobre necessidade de verificar n8n"

  - risk: "Base de conhecimento não tem informações sobre certos produtos"
    probability: "medium"
    impact: "medium"
    mitigation: "Marcar como 'REVISAO_HUMANA' quando confiança < 85%"
    contingency: "Gerar lista de gaps na base para ingestão futura"

  - risk: "Taxa de precisão < 85% (não atinge NFR2)"
    probability: "medium"
    impact: "high"
    mitigation: "Ajustar threshold de re-ranking, aumentar top_k"
    contingency: "Marcar mais itens para revisão humana (reduzir threshold)"
```

---

## Exemplo 3: Workflow Completo (Orquestrador)

**Agente:** @Orquestrador
**Objetivo:** Executar workflow completo de análise (modo ASSISTIDO)
**Complexidade:** Muito Alta

### Entrada do Usuário

```
Usuário: /iniciar-analise
```

### Fase STRUCTURE

#### 1. INTERPRETAÇÃO

```markdown
📋 Meu Entendimento da Tarefa

Objetivo: Executar workflow completo de análise de edital no modo ASSISTIDO

Workflow inclui:
1. Extração de metadados (Objeto, Escopo)
2. Estruturação de requisitos em CSV
3. Análise de conformidade
4. Geração de relatório final

Inputs:
- Arquivo do edital principal (a solicitar ao usuário)
- Arquivo de especificações técnicas (a solicitar)

Outputs esperados:
- CSV estruturado
- CSV de análise
- Relatório final
- Todos em: data/analyses/[novo_ID]/

Modo: ASSISTIDO (com HALTs para aprovação em cada etapa macro)

Confirme para eu solicitar os arquivos e prosseguir com o plano detalhado.
```

---

#### 2. DECOMPOSIÇÃO (High-Level)

```yaml
steps:
  - id: 1
    name: "Solicitar arquivos ao usuário"
    estimated_time: "30s"

  - id: 2
    name: "Executar Extração de Metadados (delegado ao @Orquestrador interno)"
    estimated_time: "2min"

  - id: 3
    name: "Executar Estruturação (delegar ao @EstruturadorDeDocumentos)"
    estimated_time: "5min 30s"

  - id: 4
    name: "Executar Análise (delegar ao @AnalistaTecnico)"
    estimated_time: "20min"

  - id: 5
    name: "Compilar Relatório Final (DELIVER)"
    estimated_time: "1min"
```

---

#### 3. CHECKPOINTS (Multi-Nível)

**O Orquestrador garante que cada agente delegado execute seu próprio SHIELD:**

```yaml
checkpoints:
  etapa_2:
    - Agente interno executa: STRUCTURE → EXECUTE → INSPECT → VALIDATE
    - HALT: "Apresentar Objeto/Escopo para aprovação do usuário"
    - Se aprovado → prossegue

  etapa_3:
    - @EstruturadorDeDocumentos executa seu próprio SHIELD completo
    - HALT: "Apresentar CSV estruturado para aprovação"
    - Se aprovado → prossegue

  etapa_4:
    - @AnalistaTecnico executa seu próprio SHIELD completo
    - HALT intermediário: Após cada lote (lote 1, lote 2)
    - HALT final: "Apresentar análise completa"

  etapa_5:
    - VALIDATE: "Todos os artefatos foram gerados"
    - DELIVER: "Apresentar relatório consolidado"
    - HALT: "Aprovação final do usuário"
```

---

#### 4. ESTIMATIVAS (Workflow Completo)

```yaml
resources:
  estimated_duration:
    optimistic: "20min"
    realistic: "30min"
    pessimistic: "45min"

  estimated_tokens: 50000

  estimated_api_calls:
    n8n: 47  # Um por requisito
    pinecone: 940  # 20 resultados por requisito (via n8n)

  estimated_disk_space: "5MB"
```

---

#### 5. APRESENTAÇÃO (Simplificada)

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PLANO DE EXECUÇÃO - WORKFLOW COMPLETO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Tarefa:** Análise Completa de Edital (Modo Assistido)
**Duração Estimada:** 30min (realista)

## Fases Macro

### Fase 1: Extração de Metadados (~2min)
- Identificar Objeto e Escopo do edital
- ⏸️ HALT: Validação dos metadados

### Fase 2: Estruturação (~5min 30s)
- Delegar para @EstruturadorDeDocumentos
- Ele executará seu próprio plano SHIELD
- ⏸️ HALT: Validação do CSV estruturado

### Fase 3: Análise de Conformidade (~20min)
- Delegar para @AnalistaTecnico
- Processamento em lotes com HALTs intermediários
- ⏸️ HALT 3.1: Após lote 1
- ⏸️ HALT 3.2: Após lote 2 (análise completa)

### Fase 4: Entrega (~1min)
- Compilar todos os resultados
- Gerar relatório final
- ⏸️ HALT Final: Apresentação do relatório

## Total de Pausas para Aprovação: 5

## Recursos

- ⏱️ Duração total: 20min - 30min - 45min
- 🔢 Tokens: ~50,000
- 🌐 Chamadas n8n: ~47
- 💾 Espaço: ~5MB

## Critérios de Sucesso Global

✅ Workflow completado de ponta a ponta
✅ Todos os checkpoints passaram
✅ Precisão da análise > 85%
✅ Relatório final gerado e aprovado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deseja prosseguir? [Opções 1-4]
```

---

## 🎓 Lições dos Exemplos

### 1. Granularidade Varia por Complexidade

- **Tarefa Simples:** Etapas mais detalhadas, diretas
- **Tarefa Complexa:** Etapas macro que delegam sub-planos

### 2. Checkpoints Aninhados

- Orquestrador tem HALTs macro
- Agentes delegados têm seus próprios HALTs micro
- Ambos seguem SHIELD de forma independente

### 3. Estimativas Conservadoras

- Sempre incluir 3 cenários: otimista, realista, pessimista
- Melhor superestimar e entregar antes

### 4. Riscos Contextuais

- Riscos variam por tipo de tarefa
- Sempre pensar em: inputs corrompidos, serviços offline, volume inesperado

---

**Estes exemplos servem como referência para implementar a capacidade STRUCTURE em qualquer agente.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
