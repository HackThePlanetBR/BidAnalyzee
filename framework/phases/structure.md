# SHIELD Phase: STRUCTURE (Estrutura)

**Versão:** 1.0
**Fase:** S - STRUCTURE
**Responsável:** IA (com aprovação do Humano no primeiro HALT)
**Modo Obrigatório:** Strict

---

## 📖 Visão Geral

A fase **STRUCTURE** é a primeira fase do Framework SHIELD e a base de todo planeamento. Nesta fase, o agente interpreta um objetivo e cria um plano de execução detalhado, quantificado e estruturado antes de qualquer execução.

**Princípio Fundamental:** "Planejar antes de agir. Medir antes de prometer."

---

## 🎯 Objetivos da Fase STRUCTURE

1. **Decompor** o objetivo em etapas sequenciais e mensuráveis
2. **Estimar** recursos necessários (tempo, tokens, API calls)
3. **Identificar** checkpoints de validação (HALTs, INSPECTs, VALIDATEs)
4. **Prever** riscos e estratégias de mitigação
5. **Quantificar** critérios de sucesso
6. **Gerar** um plano auditável e aprovável

---

## 📋 Quando Usar

- ✅ **Obrigatório** no início de TODA tarefa (Modo Strict)
- ✅ Antes de qualquer fase [EXECUTE](execute.md)
- ✅ Quando o usuário solicita uma nova análise
- ✅ Quando um LOOP requer replanejamento significativo

---

## 🔧 Como Executar a Fase STRUCTURE

### Entrada (Input)

- **Objetivo da tarefa** (ex: "Estruturar edital em CSV")
- **Contexto** (arquivos disponíveis, constraints, outputs esperados)
- **Modo de operação** (Assistido vs FLOW)

### Processo

#### 1. Interpretar o Objetivo

**Perguntas a responder:**
- Qual é o resultado final esperado?
- Quais são os inputs disponíveis?
- Há constraints ou requisitos específicos?
- Qual é a definição de "sucesso" para esta tarefa?

**Exemplo:**
```
Objetivo: "Estruturar documento de edital em CSV"

Interpretação:
- Input: Arquivo PDF do edital (especificações técnicas)
- Output: CSV estruturado com colunas [ID, Descrição, Tipo, Categoria]
- Sucesso: Todos os requisitos extraídos, sem duplicatas, formato válido
- Constraint: Modo Strict (100% de completude)
```

#### 2. Decompor em Etapas

**Critérios para uma boa decomposição:**
- Cada etapa tem um objetivo claro e único
- Etapas são sequenciais (se há dependências) ou paralelas (se independentes)
- Cada etapa é **mensurável** (não vaga)
- Há estimativa de tempo para cada etapa

**Template de Etapa:**
```yaml
- id: [número]
  name: "[Verbo] + [Objeto] - ex: Validar arquivo de entrada"
  description: "[O que será feito em 1-2 frases]"
  estimated_time: "[Estimativa realista - ex: 30s, 2min]"
  dependencies: [lista de IDs de etapas anteriores]
  checkpoints: [lista de validações - INSPECT, VALIDATE, HALT]
  success_criteria: [lista de critérios mensuráveis]
```

**Exemplo Real:**
```yaml
steps:
  - id: 1
    name: "Validar arquivo de entrada"
    description: "Verificar se o arquivo existe, é legível e está no formato esperado (PDF/DOCX)"
    estimated_time: "10s"
    dependencies: []
    checkpoints:
      - type: "INSPECT"
        description: "Arquivo existe e é acessível"
    success_criteria:
      - "Arquivo existe no caminho fornecido"
      - "Formato é PDF ou DOCX"
      - "Arquivo não está corrompido"

  - id: 2
    name: "Extrair texto do documento"
    description: "Usar parser apropriado (PyPDF2/python-docx) para extrair texto completo"
    estimated_time: "1min 30s"
    dependencies: [1]
    checkpoints:
      - type: "INSPECT"
        description: "Texto extraído sem erros"
      - type: "VALIDATE"
        description: "Texto extraído tem > 1000 caracteres (indicador de sucesso)"
    success_criteria:
      - "Texto extraído completamente"
      - "Sem páginas/seções faltando"
      - "Encoding correto (UTF-8)"
```

#### 3. Identificar Checkpoints (HALT, INSPECT, VALIDATE)

**Regras para Checkpoints:**

**HALT (Aprovação do Usuário):**
- Após etapas **macro** do workflow
- Quando há ambiguidade que requer decisão humana
- Sempre que o plano indicar necessidade

**INSPECT (Auto-inspeção):**
- **Obrigatório** após TODA etapa de EXECUTE
- Antes de qualquer HALT

**VALIDATE (L.5 - Validação Quantitativa):**
- **Obrigatório** após INSPECT passar
- Antes de HALT ou DELIVER

**Exemplo de Sequência:**
```
EXECUTE → INSPECT → VALIDATE → HALT → [aprovação] → próxima EXECUTE
```

#### 4. Estimar Recursos

**O que estimar:**

```yaml
resources:
  estimated_tokens:
    description: "Tokens totais estimados para a tarefa"
    calculation: "[Explicar como chegou no número]"
    value: 15000

  estimated_api_calls:
    pinecone:
      description: "Chamadas à API do Pinecone"
      value: 0  # Não usa Pinecone nesta tarefa
    n8n:
      description: "Chamadas ao microsserviço n8n"
      value: 0  # Não usa n8n nesta tarefa

  estimated_duration:
    optimistic: "3min"
    realistic: "5min 30s"
    pessimistic: "10min"

  estimated_disk_space:
    description: "Espaço em disco para outputs"
    value: "500KB"
```

#### 5. Prever Riscos

**Template de Risco:**
```yaml
- risk: "[Descrição do risco]"
  probability: "[low/medium/high]"
  impact: "[low/medium/high]"
  mitigation: "[Estratégia de mitigação]"
  contingency: "[Plano B se acontecer]"
```

**Exemplos:**
```yaml
risks:
  - risk: "Arquivo PDF está protegido por senha"
    probability: "low"
    impact: "high"
    mitigation: "Validar se o arquivo é acessível antes de processar"
    contingency: "HALT e solicitar ao usuário a senha ou arquivo desbloqueado"

  - risk: "Texto extraído está mal formatado (tabelas, colunas)"
    probability: "medium"
    impact: "medium"
    mitigation: "Usar parser robusto com fallback para OCR"
    contingency: "Marcar seções problemáticas para revisão humana"

  - risk: "Documento tem mais de 500 requisitos (excede estimativa)"
    probability: "low"
    impact: "medium"
    mitigation: "Implementar processamento em lotes"
    contingency: "Informar usuário e ajustar plano dinamicamente"
```

#### 6. Definir Critérios de Sucesso Globais

**Características de bons critérios:**
- ✅ Objetivos e mensuráveis
- ✅ Verificáveis por código ou inspeção
- ✅ Claros para o usuário

**Exemplos:**
```yaml
success_criteria:
  - "100% dos requisitos do documento foram extraídos (validado por contagem)"
  - "CSV gerado está conforme template (todas as colunas obrigatórias presentes)"
  - "Zero requisitos duplicados (validado por hash de conteúdo)"
  - "Arquivo CSV é válido e abre em Excel/LibreOffice sem erros"
  - "Logs completos foram gerados para auditoria"
```

### Saída (Output)

Um arquivo YAML seguindo o template `framework/templates/plan_template.yaml`, preenchido e completo.

**Localização do Output:**
```
data/state/plan_[task_id].yaml
```

---

## ✅ Checklist de Qualidade do Plano

Antes de apresentar o plano ao usuário (HALT), valide:

- [ ] **Clareza:** Cada etapa é compreensível sem ambiguidade?
- [ ] **Completude:** Todas as etapas necessárias estão incluídas?
- [ ] **Mensurabilidade:** Há estimativas quantitativas (tempo, recursos)?
- [ ] **Checkpoints:** HALTs, INSPECTs e VALIDATEs estão posicionados corretamente?
- [ ] **Riscos:** Principais riscos foram identificados e têm mitigação?
- [ ] **Critérios de Sucesso:** São objetivos e verificáveis?
- [ ] **Sequência:** Dependências entre etapas estão corretas?
- [ ] **Viabilidade:** As estimativas são realistas?

---

## 📊 Exemplo Completo: Estruturação de Edital

```yaml
plan:
  task: "Estruturar documento de edital em CSV"
  agent: "document_structurer"
  created_at: "2025-11-06T15:30:00Z"
  estimated_duration: "5min 30s"

  context:
    objective: "Extrair requisitos técnicos de um edital PDF e estruturá-los em CSV"
    inputs:
      - type: "file"
        description: "Edital em formato PDF"
        required: true
    outputs:
      - type: "csv"
        description: "Requisitos estruturados com colunas [ID, Descrição, Tipo, Categoria]"
        location: "data/analyses/[analysis_id]/requisitos_estruturados.csv"

  steps:
    - id: 1
      name: "Validar arquivo de entrada"
      description: "Verificar existência, formato e integridade do arquivo"
      estimated_time: "10s"
      dependencies: []
      checkpoints:
        - type: "INSPECT"
          description: "Arquivo é válido e acessível"
      success_criteria:
        - "Arquivo existe"
        - "Formato é PDF"
        - "Arquivo não está corrompido"

    - id: 2
      name: "Extrair texto do PDF"
      description: "Usar PyPDF2 para extrair texto completo do documento"
      estimated_time: "1min 30s"
      dependencies: [1]
      checkpoints:
        - type: "INSPECT"
          description: "Texto extraído sem erros de parsing"
        - type: "VALIDATE"
          description: "Texto tem > 1000 caracteres"
      success_criteria:
        - "Todas as páginas foram processadas"
        - "Encoding UTF-8 correto"

    - id: 3
      name: "Identificar seção de especificações técnicas"
      description: "Localizar no texto a seção que contém os requisitos"
      estimated_time: "30s"
      dependencies: [2]
      checkpoints:
        - type: "INSPECT"
          description: "Seção foi identificada corretamente"
      success_criteria:
        - "Seção identificada com marcadores (ex: '5. Especificações Técnicas')"
        - "Início e fim da seção delimitados"

    - id: 4
      name: "Extrair requisitos individuais"
      description: "Parsear a seção identificando cada requisito (linha ou parágrafo)"
      estimated_time: "2min"
      dependencies: [3]
      checkpoints:
        - type: "INSPECT"
          description: "Requisitos foram extraídos individualmente"
        - type: "VALIDATE"
          description: "Número de requisitos extraídos = número esperado"
      success_criteria:
        - "Cada requisito é uma entrada única"
        - "Requisitos compostos foram decompostos"

    - id: 5
      name: "Estruturar em formato CSV"
      description: "Criar CSV com colunas [ID, Descrição, Tipo, Categoria] e popular"
      estimated_time: "1min"
      dependencies: [4]
      checkpoints:
        - type: "INSPECT"
          description: "CSV está formatado corretamente"
        - type: "VALIDATE"
          description: "100% dos requisitos foram incluídos no CSV"
        - type: "HALT"
          reason: "Apresentar CSV estruturado para aprovação do usuário"
      success_criteria:
        - "CSV tem todas as colunas obrigatórias"
        - "Nenhuma linha está vazia"
        - "IDs são sequenciais"

    - id: 6
      name: "Salvar arquivo e gerar logs"
      description: "Salvar CSV final e logs de execução"
      estimated_time: "20s"
      dependencies: [5]
      checkpoints:
        - type: "VALIDATE"
          description: "Arquivos foram salvos corretamente"
      success_criteria:
        - "CSV salvo em data/analyses/[id]/"
        - "Logs salvos"
        - "Checksums calculados"

  halt_points:
    - after_step: 5
      reason: "Usuário deve validar se os requisitos foram extraídos corretamente antes de prosseguir"
      presentation:
        format: "table"
        include:
          - "Primeiras 10 linhas do CSV"
          - "Total de requisitos extraídos"
          - "Distribuição por tipo (se disponível)"

  success_criteria:
    - "100% dos requisitos do documento foram extraídos"
    - "CSV válido conforme template"
    - "Zero duplicatas"
    - "Todas as colunas obrigatórias preenchidas"

  risks:
    - risk: "PDF está protegido ou corrompido"
      probability: "low"
      impact: "high"
      mitigation: "Validar integridade na etapa 1"
    - risk: "Estrutura do documento é não-padrão"
      probability: "medium"
      impact: "medium"
      mitigation: "Identificação robusta de seções com fallbacks"

  resources:
    estimated_tokens: 8000
    estimated_api_calls:
      pinecone: 0
      n8n: 0
    estimated_disk_space: "500KB"

metadata:
  shield_version: "1.0"
  mode: "STRICT"
  created_by: "document_structurer"
  template_version: "1.0"
```

---

## 🎓 Boas Práticas

### DO ✅

- **Seja específico:** "Extrair 47 requisitos" em vez de "Extrair requisitos"
- **Estime conservadoramente:** Melhor superestimar do que subestimar
- **Inclua checkpoints frequentes:** INSPECT após cada EXECUTE
- **Documente suposições:** Se assumiu algo, deixe explícito
- **Pense nos riscos:** O que pode dar errado?

### DON'T ❌

- **Etapas vagas:** "Processar documento" (o que exatamente?)
- **Sem estimativas:** Sempre inclua tempo estimado
- **Pular checkpoints:** INSPECT é obrigatório após EXECUTE
- **Critérios subjetivos:** "Boa qualidade" não é mensurável
- **Ignorar dependências:** Especifique sempre a ordem correta

---

## 🔄 Integração com Outras Fases

```
STRUCTURE (você está aqui)
    ↓
    [Plano aprovado pelo usuário via HALT]
    ↓
EXECUTE (etapa 1 do plano)
    ↓
INSPECT (validar etapa 1)
    ↓
LOOP (se INSPECT falhou) → volta para EXECUTE
    ↓
VALIDATE (validação quantitativa)
    ↓
HALT (apresentar resultado da etapa 1)
    ↓
    [Usuário aprova]
    ↓
EXECUTE (etapa 2 do plano)
    ↓
    [Repete até todas as etapas]
    ↓
DELIVER (entrega final)
```

---

## 📚 Referências

- **Template YAML:** `framework/templates/plan_template.yaml`
- **Princípios SHIELD:** [OPERATING_PRINCIPLES.md](../../OPERATING_PRINCIPLES.md)
- **ADR-001:** Agentes como prompts estruturados
- **PRD História 1.1:** Implementação da Capacidade de Planeamento

---

**Versão:** 1.0
**Criado em:** 06/11/2025
**Última atualização:** 06/11/2025
