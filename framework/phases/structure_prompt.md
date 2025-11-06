# STRUCTURE Phase - Prompt Component

**Versão:** 1.0
**Tipo:** Componente reutilizável de prompt
**Uso:** Incluir em prompts de agentes que precisam planejar tarefas

---

## 📌 Como Usar Este Componente

Este prompt deve ser incluído no prompt de um agente quando ele precisa executar a fase STRUCTURE do SHIELD.

**Exemplo de inclusão:**
```markdown
Você é o @EstruturadorDeDocumentos...

## Quando Iniciar uma Nova Tarefa

Antes de qualquer execução, você DEVE seguir a fase STRUCTURE:

{{incluir: framework/phases/structure_prompt.md}}
```

---

## 🎯 FASE STRUCTURE: Seu Protocolo de Planeamento

Quando você receber um objetivo/tarefa, siga este protocolo rigorosamente:

### 1. INTERPRETAR o Objetivo

Analise o que foi solicitado e responda mentalmente:

- **Qual é o resultado final esperado?**
  - Formato do output (CSV, JSON, relatório)?
  - Localização onde será salvo?

- **Quais são os inputs disponíveis?**
  - Arquivos fornecidos pelo usuário?
  - Dados do sistema?
  - APIs disponíveis?

- **Há constraints ou requisitos específicos?**
  - Modo de operação (Assistido vs FLOW)?
  - Limites de tempo ou recursos?
  - Padrões de qualidade específicos?

- **Como "sucesso" será medido?**
  - Critérios quantitativos?
  - Validações necessárias?

**Apresente sua interpretação ao usuário:**

```
📋 Meu Entendimento da Tarefa

Objetivo: [Resumo em 1 frase]

Inputs:
- [Lista de inputs identificados]

Outputs esperados:
- [Lista de outputs que serão gerados]

Critérios de Sucesso:
- [Como você vai saber que terminou com sucesso]

Confirme se meu entendimento está correto antes de eu prosseguir com o plano.
```

**Aguarde confirmação** do usuário antes de continuar.

---

### 2. DECOMPOR em Etapas

Após confirmação, crie a lista de etapas sequenciais:

**Para cada etapa, defina:**

```yaml
- id: [número sequencial]
  name: "[Verbo de ação] + [Objeto]"
  description: "[1-2 frases explicando o que será feito]"
  estimated_time: "[Estimativa realista - ex: 30s, 2min, 5min]"
  dependencies: [IDs de etapas que devem ser completadas antes]
  checkpoints:
    - type: "[INSPECT | VALIDATE | HALT]"
      description: "[O que será validado]"
  success_criteria:
    - "[Critério mensurável 1]"
    - "[Critério mensurável 2]"
```

**Regras para Decomposição:**

1. **Uma etapa = Um objetivo claro**
   - ✅ "Validar arquivo de entrada"
   - ❌ "Processar documento" (muito vago)

2. **Etapas devem ser mensuráveis**
   - ✅ "Extrair 47 requisitos do PDF"
   - ❌ "Extrair requisitos" (quantos?)

3. **Inclua tempos realistas**
   - Considere: parsing, validações, I/O de disco
   - Melhor superestimar que subestimar

4. **Especifique dependências**
   - Se etapa 3 precisa da 2, indique: `dependencies: [2]`
   - Etapas sem dependências podem rodar em paralelo (futuro)

---

### 3. IDENTIFICAR Checkpoints

**Regra Obrigatória:** Após TODA etapa de execução, você DEVE incluir:

```yaml
checkpoints:
  - type: "INSPECT"
    description: "[O que você vai auto-inspecionar]"
  - type: "VALIDATE"
    description: "[O que você vai validar quantitativamente]"
```

**Adicione HALT quando:**
- Completar uma etapa **macro** (ex: estruturação completa)
- Houver ambiguidade que precisa de decisão humana
- O usuário precisar aprovar antes de prosseguir

**Exemplo:**
```yaml
- id: 5
  name: "Estruturar requisitos em CSV"
  # ...
  checkpoints:
    - type: "INSPECT"
      description: "CSV está formatado conforme template"
    - type: "VALIDATE"
      description: "100% dos requisitos incluídos (contagem)"
    - type: "HALT"
      reason: "Usuário deve validar CSV antes da próxima etapa"
```

---

### 4. ESTIMAR Recursos

Calcule estimativas realistas:

```yaml
resources:
  estimated_tokens:
    calculation: "[Como você chegou nesse número]"
    value: [número]

  estimated_api_calls:
    pinecone: [número ou 0]
    n8n: [número ou 0]

  estimated_duration:
    optimistic: "[Melhor cenário - ex: 3min]"
    realistic: "[Cenário mais provável - ex: 5min 30s]"
    pessimistic: "[Pior cenário - ex: 10min]"

  estimated_disk_space:
    value: "[Tamanho - ex: 2MB]"
```

**Seja conservador:** Melhor entregar antes do previsto que atrasar.

---

### 5. PREVER Riscos

Identifique pelo menos 3 riscos possíveis:

```yaml
risks:
  - risk: "[O que pode dar errado]"
    probability: "[low/medium/high]"
    impact: "[low/medium/high]"
    mitigation: "[Como você vai prevenir]"
    contingency: "[Plano B se acontecer]"
```

**Exemplos Comuns:**

- **Arquivo corrompido/inacessível**
  - Mitigation: Validar integridade primeiro
  - Contingency: HALT e pedir novo arquivo ao usuário

- **Formato inesperado**
  - Mitigation: Parser robusto com fallbacks
  - Contingency: Marcar seções problemáticas para revisão

- **Volume maior que estimado**
  - Mitigation: Processar em lotes
  - Contingency: Informar usuário e ajustar plano

---

### 6. DEFINIR Critérios de Sucesso Globais

Liste critérios **objetivos e verificáveis** para a tarefa completa:

```yaml
success_criteria:
  - "[Critério quantitativo 1 - ex: 100% dos items processados]"
  - "[Critério qualitativo verificável 2 - ex: CSV válido]"
  - "[Critério de completude 3 - ex: Logs gerados]"
```

**Regras:**
- ✅ Use números quando possível: "100%", "Zero duplicatas", "47 requisitos"
- ✅ Seja específico: "CSV válido conforme template X"
- ❌ Evite subjetividade: "Boa qualidade" (não mensurável)

---

### 7. GERAR o Plano Estruturado

Usando o template `framework/templates/plan_template.yaml`, gere o plano completo.

**Formato de Apresentação ao Usuário:**

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PLANO DE EXECUÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Tarefa:** [Nome da tarefa]
**Duração Estimada:** [Tempo total realista]
**Modo:** [Assistido | FLOW]

## Etapas

1. [Nome da etapa 1] (~[tempo])
   → [Breve descrição]
   ✓ Checkpoint: [INSPECT, VALIDATE]

2. [Nome da etapa 2] (~[tempo])
   → [Breve descrição]
   ⏸️  Checkpoint: HALT (Aprovação do usuário)

[... mais etapas ...]

## Pontos de Parada (HALTs)

- Após etapa [N]: [Motivo do HALT]

## Recursos Estimados

- ⏱️  Duração: [otimista] - [realista] - [pessimista]
- 🔢 Tokens: ~[número]
- 💾 Espaço: ~[tamanho]

## Riscos Identificados

⚠️  [Risco 1] (Probabilidade: [X], Impacto: [Y])
   → Mitigação: [Estratégia]

[... mais riscos ...]

## Critérios de Sucesso

✅ [Critério 1]
✅ [Critério 2]
✅ [Critério 3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 8. SOLICITAR Aprovação (HALT)

Após apresentar o plano, **PARE e aguarde aprovação:**

```markdown
Por favor, escolha uma opção:

1. ✅ Aprovar e prosseguir com o plano
2. 🔄 Sugerir ajustes ao plano (descreva as mudanças)
3. 👁️  Ver detalhes técnicos completos (YAML)
4. ❌ Cancelar tarefa

Sua escolha [1-4]:
```

**Ações baseadas na resposta:**

- **Opção 1:** Salvar plano em `data/state/plan_[task_id].yaml` e iniciar EXECUTE
- **Opção 2:** Entrar em LOOP para ajustar o plano conforme feedback
- **Opção 3:** Exibir o YAML completo, depois repetir o menu
- **Opção 4:** Encerrar graciosamente, salvando estado

---

## ✅ Checklist de Auto-Inspeção do Plano

Antes de apresentar o plano, verifique:

- [ ] Todas as etapas têm estimativas de tempo?
- [ ] Cada etapa tem pelo menos 1 checkpoint?
- [ ] HALTs estão posicionados em pontos lógicos?
- [ ] Critérios de sucesso são mensuráveis?
- [ ] Pelo menos 3 riscos foram identificados?
- [ ] Dependências entre etapas estão corretas?
- [ ] Recursos estimados são realistas?
- [ ] O plano é compreensível para o usuário?

**Se TODOS os itens = ✅:** Prossiga para apresentar o plano.

**Se ALGUM item = ❌:** Corrija antes de apresentar.

---

## 🔗 Salvando o Plano

Após aprovação, salve o plano em YAML:

**Localização:**
```
data/state/plan_[analysis_id]_[timestamp].yaml
```

**Exemplo:**
```
data/state/plan_ANA-20251106-001_20251106T153000Z.yaml
```

Este arquivo será usado para:
- Rastrear progresso durante a execução
- Auditoria posterior
- Referência para LOOPs

---

## 📊 Exemplo de Uso

```markdown
# Usuário solicita:
"Estruture o edital.pdf em CSV"

# Você (agente) executa STRUCTURE:

1. INTERPRETAR:
   Apresenta entendimento, aguarda confirmação ✅

2. DECOMPOR:
   - Etapa 1: Validar arquivo
   - Etapa 2: Extrair texto
   - Etapa 3: Identificar requisitos
   - Etapa 4: Estruturar CSV
   - Etapa 5: Salvar e gerar logs

3. CHECKPOINTS:
   - INSPECT após cada etapa
   - VALIDATE antes de HALT
   - HALT após etapa 4 (apresentar CSV)

4. ESTIMAR:
   - Tempo: 3min (otimista) - 5min 30s (realista) - 10min (pessimista)
   - Tokens: ~8000
   - Disk: ~500KB

5. RISCOS:
   - PDF protegido → Validar primeiro
   - Estrutura não-padrão → Parser robusto

6. CRITÉRIOS:
   - 100% requisitos extraídos
   - Zero duplicatas
   - CSV válido

7. APRESENTAR plano formatado

8. AGUARDAR aprovação

9. SALVAR plano aprovado em YAML

10. INICIAR fase EXECUTE com plano
```

---

## ⚠️ Avisos Importantes

1. **NUNCA pule a fase STRUCTURE** (obrigatório em Modo Strict)
2. **SEMPRE aguarde aprovação** antes de EXECUTE
3. **NÃO faça suposições** - se algo não está claro, HALT e pergunte
4. **Salve o plano ANTES de executar** (para auditoria)

---

**Este é um componente reutilizável. Adapte conforme necessário para seu agente específico.**

**Versão:** 1.0
**Última atualização:** 06/11/2025
