# Framework SHIELD - Operating Principles

**Versão:** 1.0 (adaptado do PRD v5.3)
**Data:** 06 de novembro de 2025

---

## 1. Declaração de Obrigatoriedade

> "Toda e qualquer funcionalidade descrita neste PRD, contida em qualquer Épico ou História de Utilizador, deve ser implementada em estrita conformidade com os princípios do Framework SHIELD. Esta metodologia é a principal diretriz de qualidade e governança do projeto."

Este documento é a **referência oficial** para a metodologia SHIELD mencionada no PRD (Seção 2).

---

## 2. Visão Geral do SHIELD

### O que é SHIELD?

SHIELD é um framework de governança e execução para sistemas de IA que garante:

- ✅ **Controlo total:** O utilizador aprova cada etapa crítica
- ✅ **Qualidade garantida:** Múltiplas validações (pela IA e pelo utilizador)
- ✅ **Zero assunções:** O sistema opera apenas com dados fornecidos e validados
- ✅ **Transparência:** Cada decisão e resultado é justificado e auditável
- ✅ **Adaptabilidade:** O framework se ajusta à complexidade de cada tarefa

### Acrônimo SHIELD

| Fase | Nome | Propósito |
|------|------|-----------|
| **S** | **STRUCTURE** | Planeamento detalhado antes da execução |
| **H** | **HALT** | Pausas para aprovação do utilizador |
| **I** | **INSPECT** | Auto-inspeção rigorosa com checklists |
| **E** | **EXECUTE** | Execução controlada e isolada |
| **L** | **LOOP** | Ciclos de refinamento e correção |
| **L.5** | **VALIDATE** | Validação quantitativa de completude |
| **D** | **DELIVER** | Entrega formal com evidências |

---

## 3. Definição das Fases

### S - STRUCTURE (Estrutura)

**Objetivo:** Planejar a tarefa de forma quantificada e estruturada antes de qualquer execução.

**Responsável:** IA (com aprovação do Humano no primeiro HALT)

**O que a IA deve fazer:**
1. Interpretar o objetivo da tarefa
2. Decompor em etapas sequenciais e mensuráveis
3. Estimar recursos necessários (tempo, tokens, chamadas a APIs)
4. Identificar checkpoints de validação (HALTs)
5. Gerar um plano quantificado com to-dos

**Output:**
```yaml
plan:
  task: "Estruturar documento de edital em CSV"
  steps:
    - id: 1
      name: "Validar arquivo de entrada"
      estimated_time: "5s"
      checkpoints: []
    - id: 2
      name: "Extrair requisitos do PDF"
      estimated_time: "2min"
      checkpoints: ["HALT após extração"]
    - id: 3
      name: "Estruturar em CSV"
      estimated_time: "1min"
      checkpoints: ["VALIDATE antes de HALT final"]
  total_estimated_time: "3min 5s"
```

**Critério de Qualidade:**
- [ ] Todas as etapas são mensuráveis (não vagas)
- [ ] Há estimativas quantitativas
- [ ] Checkpoints de HALT estão identificados
- [ ] Dependências entre etapas estão claras

---

### H - HALT (Parada)

**Objetivo:** Pausar o fluxo para solicitar aprovação explícita do utilizador.

**Responsável:** Humano (decisão), IA (apresentação)

**Quando usar:**
- Após a conclusão de cada etapa **macro** do workflow (ex: após estruturação, após análise)
- Quando a IA identifica ambiguidade ou risco
- Sempre que o plano (STRUCTURE) indicar um checkpoint

**Como implementar:**

1. **IA apresenta o resultado da etapa:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ETAPA CONCLUÍDA: Estruturação do Edital
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Resumo:
- Total de requisitos extraídos: 47
- Formato de saída: requisitos_estruturados.csv
- Status: ✅ Todos os checklists passaram

📄 Arquivo gerado:
   data/analyses/ANA-20250806-001/requisitos_estruturados.csv

🔍 Prévia dos primeiros 5 requisitos:
   [Tabela com primeiros 5 requisitos]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

2. **IA solicita aprovação com menu:**
```
Por favor, escolha uma opção:

1. ✅ Aprovar e prosseguir para a próxima etapa
2. 🔄 Solicitar ajustes (descreva o que deve ser corrigido)
3. 👁️  Ver detalhes completos antes de decidir
4. ❌ Cancelar análise

Sua escolha [1-4]:
```

3. **IA aguarda resposta e age conforme:**
   - Opção 1: Prossegue para próxima fase do STRUCTURE
   - Opção 2: Entra no LOOP para correção
   - Opção 3: Apresenta mais detalhes, depois repete o menu
   - Opção 4: Encerra o workflow com salvamento do estado

**Critério de Qualidade:**
- [ ] Resultado apresentado de forma clara e resumida
- [ ] Evidências estão disponíveis (arquivos, logs)
- [ ] Menu oferece todas as opções relevantes
- [ ] Sistema aguarda decisão antes de prosseguir

---

### I - INSPECT (Inspeção)

**Objetivo:** Validar a qualidade da etapa executada usando checklists específicos.

**Responsável:** IA (auto-inspeção), depois Humano (validação no HALT)

**Quando usar:**
- **Obrigatoriamente** após cada fase EXECUTE
- Antes de qualquer HALT

**Tipos de Checklists:**

1. **Checklist Fixo (Anti-Alucinação e Qualidade Geral)**
```yaml
checklist_fixo:
  - item: "Todas as informações foram extraídas do documento fornecido (sem invenções)?"
    status: true
  - item: "Há evidências (links, trechos) para cada afirmação?"
    status: true
  - item: "A formatação do output está conforme o template?"
    status: true
  - item: "Não há campos vazios ou 'N/A' sem justificativa?"
    status: true
```

2. **Checklist Dinâmico (Específico da Tarefa)**
```yaml
checklist_estruturacao:
  - item: "Cada linha do CSV representa um requisito único?"
    status: true
  - item: "Todas as colunas obrigatórias estão preenchidas (ID, Descrição, Tipo)?"
    status: true
  - item: "Não há requisitos duplicados?"
    status: true
  - item: "A numeração está sequencial e sem gaps?"
    status: true
```

**Como executar:**
1. IA carrega o checklist relevante (de `agents/{agent}/checklists/inspect.yaml`)
2. IA valida cada item do checklist contra o output gerado
3. IA registra o resultado (true/false) e justificativas
4. Se **todos** os itens = true: passa para VALIDATE
5. Se **algum** item = false: aciona LOOP para correção

**Output:**
```yaml
inspection_result:
  timestamp: "2025-11-06T10:30:00Z"
  agent: "document_structurer"
  checklist: "inspect.yaml"
  items_passed: 7
  items_failed: 1
  failed_items:
    - item: "Não há requisitos duplicados?"
      status: false
      reason: "Requisitos 12 e 23 têm descrições idênticas"
  action: "LOOP"
```

**Critério de Qualidade:**
- [ ] Checklist é específico para a tarefa
- [ ] Cada item é verificável objetivamente (não vago)
- [ ] IA justifica cada item que falhou
- [ ] Resultado é registrado em log

---

### E - EXECUTE (Execução)

**Objetivo:** Realizar o trabalho planejado de forma controlada.

**Responsável:** 100% IA (mas decisão de iniciar é do Humano via HALT)

**Princípio:** A IA só executa uma etapa **após a aprovação de 100% da fase anterior**.

**Regras de Execução:**
1. Nunca assumir informações não fornecidas
2. Se encontrar ambiguidade, pausar (HALT) e perguntar
3. Registrar logs de cada ação significativa
4. Manter evidências de decisões

**Exemplo de Fluxo:**
```python
def execute_estruturacao():
    log("Iniciando extração de requisitos do PDF...")

    # 1. Validar input
    if not validate_file_exists(edital_path):
        halt_and_ask_for_correct_path()

    # 2. Extrair texto
    texto = extract_text_from_pdf(edital_path)
    log(f"Extraídos {len(texto)} caracteres")

    # 3. Identificar requisitos
    requisitos = parse_requirements(texto)
    log(f"Identificados {len(requisitos)} requisitos")

    # 4. Estruturar em CSV
    csv_data = format_as_csv(requisitos)

    # 5. Salvar
    save_csv(csv_data, output_path)
    log(f"CSV salvo em {output_path}")

    return csv_data
```

**Critério de Qualidade:**
- [ ] Código/prompt é executado do início ao fim sem interrupções manuais
- [ ] Logs são gerados para cada ação significativa
- [ ] Erros são capturados e reportados (não silenciados)
- [ ] Output está em formato validável

---

### L - LOOP (Repetição)

**Objetivo:** Corrigir problemas identificados na fase INSPECT ou via feedback do usuário.

**Responsável:** IA (execução), acionado pela IA (falha no INSPECT) ou Humano (feedback no HALT)

**Quando acionar:**
1. **Automático:** Quando INSPECT retorna `items_failed > 0`
2. **Manual:** Quando usuário escolhe "Solicitar ajustes" no HALT

**Como funciona:**

1. **IA identifica o problema específico:**
```yaml
loop_context:
  trigger: "INSPECT_FAILED"
  failed_item: "Não há requisitos duplicados?"
  details: "Requisitos 12 e 23 têm descrições idênticas"
  action_required: "Remover ou mesclar duplicatas"
```

2. **IA re-executa a etapa com correção:**
```python
def loop_correcao():
    # Carregar contexto do loop
    problema = load_loop_context()

    # Aplicar correção específica
    if problema == "duplicatas":
        requisitos = remove_duplicates(requisitos)

    # Re-executar EXECUTE
    resultado = execute_estruturacao()

    # Re-executar INSPECT
    if inspect(resultado):
        return resultado  # Sucesso, sair do loop
    else:
        loop_correcao()  # Falhou de novo, repetir
```

3. **Limitar iterações:**
   - Máximo de 3 tentativas automáticas
   - Após 3 falhas, HALT obrigatório para pedir ajuda ao usuário

**Critério de Qualidade:**
- [ ] IA entende claramente o que precisa ser corrigido
- [ ] Correção é aplicada de forma cirúrgica (não refazer tudo)
- [ ] Há um limite de iterações (evita loops infinitos)
- [ ] Cada iteração é registrada em log

---

### L.5 - VALIDATE (Validação Quantitativa)

**Objetivo:** Comprovar, de forma **quantitativa**, que 100% da tarefa foi concluída.

**Responsável:** 100% IA

**Quando usar:**
- **Obrigatoriamente** após INSPECT passar e antes de qualquer HALT ou DELIVER
- Implementado conforme **Modo Strict** (NFR12)

**Diferença entre INSPECT e VALIDATE:**
- **INSPECT:** Valida **qualidade** ("os requisitos estão bem formatados?")
- **VALIDATE:** Valida **completude** ("todos os requisitos foram processados?")

**Como implementar:**

1. **IA define métricas quantitativas:**
```yaml
validation_metrics:
  task: "Estruturação de Edital"
  metrics:
    - name: "Total de requisitos no PDF"
      expected: 47
      actual: 47
      status: PASS
    - name: "Total de linhas no CSV"
      expected: 47
      actual: 47
      status: PASS
    - name: "Linhas com campos vazios"
      expected: 0
      actual: 0
      status: PASS
    - name: "Requisitos duplicados"
      expected: 0
      actual: 0
      status: PASS
  completeness: "100%"
  result: "PASS"
```

2. **IA valida cada métrica:**
```python
def validate():
    total_requisitos_pdf = count_requirements_in_pdf(edital_path)
    total_linhas_csv = count_lines_in_csv(output_path)

    if total_requisitos_pdf != total_linhas_csv:
        return {
            "status": "FAIL",
            "reason": f"Esperado {total_requisitos_pdf}, encontrado {total_linhas_csv}",
            "action": "LOOP"
        }

    # Outras validações...

    return {"status": "PASS", "completeness": "100%"}
```

3. **Se FAIL: aciona LOOP automaticamente**

**Critério de Qualidade:**
- [ ] Todas as métricas são **objetivamente mensuráveis** (não subjetivas)
- [ ] Há evidências numéricas para cada métrica
- [ ] Completude é expressa em percentual
- [ ] Resultado é PASS (100%) ou FAIL (< 100%)

---

### D - DELIVER (Entrega)

**Objetivo:** Formalizar a entrega final com todas as evidências e documentação.

**Responsável:** IA (compilação), mas só acontece após aprovação do Humano no último HALT

**O que inclui:**

1. **Resumo Executivo:**
```markdown
# Análise de Edital - Relatório Final

**ID da Análise:** ANA-20250806-001
**Data:** 06/11/2025 10:45:00
**Status:** ✅ CONCLUÍDA

## Resumo
- **Órgão:** Prefeitura de São Paulo
- **Objeto:** Aquisição de sistema de videomonitoramento
- **Total de requisitos:** 47
- **Conformidade:**
  - ✅ Conforme: 38 (81%)
  - ⚠️ Revisão Humana: 6 (13%)
  - ❌ Não Conforme: 3 (6%)

## Arquivos Gerados
- [requisitos_estruturados.csv](...)
- [resultado_analise.csv](...)
- [logs.txt](...)

## Recomendações
1. Revisar manualmente os 6 itens marcados para revisão
2. Avaliar viabilidade dos 3 itens não conformes
3. Considerar questionamentos sobre itens X, Y, Z
```

2. **Manifesto de Evidências:**
```yaml
evidence_manifest:
  analysis_id: "ANA-20250806-001"
  artifacts:
    - type: "CSV"
      path: "data/analyses/ANA-20250806-001/resultado_analise.csv"
      rows: 47
      checksum: "a3f5b8c..."
    - type: "LOG"
      path: "data/analyses/ANA-20250806-001/logs.txt"
      lines: 342
      checksum: "d9e1a2b..."
  validation_results:
    - phase: "STRUCTURE"
      status: "PASS"
    - phase: "INSPECT"
      status: "PASS"
    - phase: "VALIDATE"
      status: "PASS"
      completeness: "100%"
  shield_compliance: "FULL"
  mode: "STRICT"
```

3. **Índice Atualizado:**
```csv
ID,Orgao,Objeto,Data_Inicio,Status,Data_Conclusao
ANA-20250806-001,Prefeitura SP,Videomonitoramento,2025-11-06 09:30,CONCLUIDA,2025-11-06 10:45
```

**Critério de Qualidade:**
- [ ] Todos os arquivos prometidos foram gerados
- [ ] Índice foi atualizado
- [ ] Relatório final está completo e legível
- [ ] Evidências estão preservadas e auditáveis

---

## 4. Modo de Operação: STRICT

Conforme NFR12 do PRD, o sistema opera **exclusivamente no Modo Strict**.

### Características do Modo Strict

| Fase | Modo Normal (não usado) | Modo Strict (obrigatório) |
|------|-------------------------|---------------------------|
| STRUCTURE | Opcional | ✅ Obrigatório |
| INSPECT | Checklist resumido | ✅ Checklist completo |
| VALIDATE | Opcional | ✅ Obrigatório (L.5) |
| LOOP | Até 1 iteração | ✅ Até 3 iterações + HALT |
| Evidências | Recomendado | ✅ Obrigatório para tudo |
| Logs | Opcional | ✅ Obrigatório em arquivo |

### Implicações

- **Tempo:** Processos levam ~20-30% mais tempo (mas com 85%+ de precisão)
- **Tokens:** Consome ~15-20% mais tokens (checklist + logs)
- **Confiabilidade:** Máxima (tolerância zero a erros de processo)

---

## 5. Divisão de Responsabilidades

| Fase | IA | Humano | Notas |
|------|-----|--------|-------|
| **S - STRUCTURE** | ✅ Planeja | 🔍 Aprova no 1º HALT | IA propõe, humano valida |
| **H - HALT** | 📊 Apresenta | ✅ Decide | IA pausa, humano escolhe |
| **I - INSPECT** | ✅ Auto-inspeção | 🔍 Valida no HALT | IA se auto-avalia primeiro |
| **E - EXECUTE** | ✅ Executa | - | 100% IA (após aprovação) |
| **L - LOOP** | ✅ Corrige | 🔍 Orienta | IA corrige, humano pode guiar |
| **L.5 - VALIDATE** | ✅ Valida quantitativamente | - | 100% IA |
| **D - DELIVER** | ✅ Compila | 🔍 Aceita final | IA entrega, humano aceita |

**Legenda:**
- ✅ Responsabilidade primária
- 🔍 Validação/supervisão
- 📊 Facilitação

---

## 6. Fluxo Completo (Exemplo: Estruturação de Edital)

```
Usuário: /iniciar-analise

1️⃣ STRUCTURE
   IA: Gera plano com 3 etapas (Extração, Estruturação, Validação)
   ↓
   HALT #1: Apresenta plano
   Usuário: Aprova ✅

2️⃣ EXECUTE (Extração)
   IA: Lê PDF, extrai texto, identifica 47 requisitos
   ↓
   INSPECT: Checklist de qualidade de extração
   ✅ Todos os itens passaram
   ↓
   VALIDATE (L.5): 47 requisitos extraídos = 47 esperados (100%)
   ✅ Validação passou
   ↓
   HALT #2: Apresenta requisitos extraídos
   Usuário: Aprova ✅

3️⃣ EXECUTE (Estruturação)
   IA: Formata requisitos em CSV, adiciona colunas, salva arquivo
   ↓
   INSPECT: Checklist de formatação CSV
   ❌ Item falhou: "Não há requisitos duplicados"
   ↓
   LOOP: Remove duplicatas, re-executa
   ↓
   INSPECT: Checklist de formatação CSV (2ª tentativa)
   ✅ Todos os itens passaram
   ↓
   VALIDATE (L.5): 47 linhas no CSV = 47 requisitos (100%)
   ✅ Validação passou
   ↓
   HALT #3: Apresenta CSV estruturado
   Usuário: Aprova ✅

4️⃣ DELIVER
   IA: Gera relatório, atualiza índice, consolida evidências
   IA: "Estruturação concluída! Próxima etapa: Análise de Conformidade?"
   Usuário: Sim, prosseguir

[Repete para próximas etapas...]
```

---

## 7. Princípio da Tolerância Zero (Recomendação R-02)

### Definição

> "Tolerância Zero aplica-se ao **processo SHIELD**, não ao modelo de IA subjacente."

### O que isso significa?

- O **processo** não deve cometer erros de governança (pular validações, assumir informações, etc.)
- O **modelo de IA** pode ter limitações (até ~15% de casos de baixa confiança)
- O **SHIELD garante** que casos de baixa confiança sejam **identificados, marcados e tratados** corretamente

### Exemplo Prático

**Cenário:** Modelo analisa um requisito de edital e retorna:
```json
{
  "requisito": "Sistema deve operar em temperaturas de -10°C a +60°C",
  "conformidade": "PROVAVEL_CONFORME",
  "confianca": 72%,
  "justificativa": "Manual menciona 'operação em ambientes externos', mas não especifica faixa de temperatura exata"
}
```

**❌ Processo com ERRO (sem SHIELD):**
- Sistema marca como "✅ Conforme" baseado em "PROVAVEL_CONFORME"
- Prossegue para próximo requisito
- Relatório final afirma conformidade sem ressalvas
- **Risco:** Desqualificação na licitação por informação incorreta

**✅ Processo CORRETO (com SHIELD Strict):**
1. **INSPECT:** Identifica confiança < 85% (threshold configurado)
2. **Ação:** Marca item como "⚠️ REVISÃO HUMANA NECESSÁRIA"
3. **Log:** Registra justificativa da baixa confiança
4. **VALIDATE:** Conta esse item como "processado mas flagged"
5. **DELIVER:** Relatório final destaca:
   ```
   ⚠️ 1 item requer revisão humana:
   - Item 23: Temperatura de operação (confiança: 72%)
     Motivo: Especificação exata não encontrada no manual
     Ação recomendada: Consultar fabricante ou datasheet técnico
   ```

**Resultado:** Processo operou com "tolerância zero" porque identificou e tratou corretamente a incerteza do modelo.

---

## 8. Checklists Obrigatórios

### Checklist Fixo de Anti-Alucinação

**Aplicável a:** Todos os agentes, todas as fases

```yaml
checklist_anti_alucinacao:
  - "Todas as informações foram extraídas de fontes fornecidas (documentos, base de conhecimento)?"
  - "Não há invenção ou suposição de dados não presentes nas fontes?"
  - "Cada afirmação tem uma evidência rastreável (link, trecho, linha)?"
  - "Quando algo não foi encontrado, está explicitamente marcado como 'Não encontrado' (não como 'N/A' genérico)?"
  - "Não há contradições entre diferentes partes do output?"
```

### Checklist por Agente

#### @EstruturadorDeDocumentos
```yaml
checklist_estruturacao:
  - "Cada linha do CSV representa um requisito único?"
  - "Todas as colunas obrigatórias estão preenchidas?"
  - "Não há requisitos duplicados?"
  - "A numeração está sequencial sem gaps?"
  - "Requisitos complexos foram decompostos adequadamente?"
```

#### @AnalistaTecnico
```yaml
checklist_analise:
  - "Cada requisito foi analisado individualmente?"
  - "O status de conformidade está justificado com evidências da base de conhecimento?"
  - "Links de evidência apontam para seções relevantes (não genéricas)?"
  - "Requisitos com confiança < 85% estão marcados para revisão?"
  - "Produtos recomendados correspondem ao requisito analisado?"
```

---

## 9. Templates de Output

### Plan Template (STRUCTURE)

```yaml
plan:
  task: "[Nome da tarefa]"
  agent: "[Nome do agente responsável]"
  estimated_duration: "[Tempo estimado]"
  steps:
    - id: 1
      name: "[Nome da etapa]"
      description: "[O que será feito]"
      estimated_time: "[Tempo da etapa]"
      dependencies: []
      checkpoints: ["HALT após esta etapa", "VALIDATE obrigatório"]
    - id: 2
      name: "[Próxima etapa]"
      ...
  halt_points:
    - after_step: 1
      reason: "Validação da extração antes de prosseguir"
    - after_step: 3
      reason: "Aprovação final do CSV estruturado"
  success_criteria:
    - "47 requisitos extraídos (100%)"
    - "CSV válido conforme template"
    - "Zero duplicatas"
```

### Inspection Result Template (INSPECT)

```yaml
inspection:
  timestamp: "2025-11-06T10:30:00Z"
  agent: "[Nome do agente]"
  phase: "[Nome da etapa inspecionada]"
  checklist_used: "[Caminho do arquivo YAML]"
  results:
    - item: "[Descrição do item do checklist]"
      status: true  # ou false
      evidence: "[Justificativa ou evidência]"
    - item: "[Outro item]"
      status: false
      reason: "[Por que falhou]"
      corrective_action: "[O que será feito no LOOP]"
  summary:
    items_total: 8
    items_passed: 7
    items_failed: 1
    overall_status: "FAIL"  # ou "PASS"
  next_action: "LOOP"  # ou "VALIDATE"
```

### Validation Result Template (VALIDATE)

```yaml
validation:
  timestamp: "2025-11-06T10:35:00Z"
  agent: "[Nome do agente]"
  task: "[Nome da tarefa]"
  metrics:
    - name: "Total de requisitos esperados"
      expected: 47
      actual: 47
      status: "PASS"
    - name: "Total de linhas no CSV"
      expected: 47
      actual: 47
      status: "PASS"
    - name: "Campos vazios não justificados"
      expected: 0
      actual: 0
      status: "PASS"
  completeness: "100%"
  overall_status: "PASS"
  next_action: "HALT"  # ou "DELIVER"
```

---

## 10. Implementação Técnica

### Como Usar Este Framework

1. **Cada agente carrega seu prompt estruturado** de `agents/{agent_name}/prompt.md`
2. **Prompts incluem seções SHIELD** explícitas:
```markdown
## Protocolo SHIELD

### Fase STRUCTURE
[Instruções de como planejar...]

### Fase EXECUTE
[Instruções de execução...]

### Fase INSPECT
Você DEVE validar os seguintes checklists:
- Checklist Fixo (Anti-Alucinação): `framework/checklists/anti_alucinacao.yaml`
- Checklist Específico: `agents/document_structurer/checklists/inspect.yaml`

[Como executar a inspeção...]

### Fase LOOP
Se INSPECT falhou, você DEVE:
[Protocolo de correção...]

### Fase VALIDATE
Você DEVE validar quantitativamente:
[Métricas específicas desta tarefa...]
```

3. **Checklists são arquivos YAML** referenciados nos prompts
4. **Estado é persistido** em `data/state/` entre HALTs
5. **Logs são escritos** em `data/analyses/{id}/logs.txt`

### Arquitetura de Pastas

```
framework/
├── SHIELD_PRINCIPLES.md           # Este documento
├── phases/
│   ├── structure_template.yaml
│   ├── inspect_template.yaml
│   ├── validate_template.yaml
│   └── deliver_template.yaml
├── checklists/
│   ├── anti_alucinacao.yaml       # Checklist fixo
│   └── README.md
└── templates/
    ├── plan_template.yaml
    ├── inspection_result.yaml
    └── validation_result.yaml
```

---

## 11. Conformidade SHIELD (Auditoria)

Cada História de Usuário implementada deve ser auditável contra este documento.

### Checklist de Conformidade SHIELD

```yaml
conformidade_shield:
  historia: "[ID da História]"
  criterios:
    - criterio: "Fase STRUCTURE está implementada?"
      status: true
      evidencia: "Função generate_plan() em [caminho]"
    - criterio: "Fase HALT está implementada com menus?"
      status: true
      evidencia: "Menu de aprovação em [caminho]"
    - criterio: "Fase INSPECT usa checklists YAML?"
      status: true
      evidencia: "Checklist em agents/.../checklists/inspect.yaml"
    - criterio: "Fase LOOP tem limite de 3 iterações?"
      status: true
      evidencia: "Lógica em [caminho]"
    - criterio: "Fase VALIDATE (L.5) comprova 100% de completude?"
      status: true
      evidencia: "Métricas quantitativas em [caminho]"
    - criterio: "Fase DELIVER gera relatório e evidências?"
      status: true
      evidencia: "Relatório em data/analyses/.../relatorio.md"
    - criterio: "Opera em Modo Strict?"
      status: true
      evidencia: "Todos os checklists são obrigatórios"
  shield_compliant: true
```

---

## 12. Referências

- **PRD v5.3:** Product Requirements Document (Seção 2 - Metodologia SHIELD)
- **ADR-006:** Decisão de Modo Strict Obrigatório
- **ADR-007:** Tolerância Zero no Processo (Recomendação R-02)
- **NFR12:** Conformidade SHIELD como requisito não-funcional

---

## 13. Glossário

| Termo | Definição |
|-------|-----------|
| **Clean Handoff** | Transição entre agentes com contexto completo e sem pendências |
| **Modo Strict** | Modo de operação com todas as validações obrigatórias (máxima qualidade) |
| **Checklist Dinâmico** | Checklist específico de uma tarefa ou agente |
| **Checklist Fixo** | Checklist de anti-alucinação aplicável a todos os agentes |
| **Completude** | Métrica quantitativa de que 100% da tarefa foi executada |
| **Evidência** | Link, trecho ou arquivo que comprova uma afirmação |
| **HALT Point** | Checkpoint onde o sistema pausa para aprovação do usuário |

---

**Documento Vivo:** Este framework será refinado conforme o sistema evolui, mas os princípios fundamentais são imutáveis.

**Versão Atual:** 1.0 (baseline para o MVP)
