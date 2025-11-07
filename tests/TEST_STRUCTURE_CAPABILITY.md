# Teste da Capacidade STRUCTURE (História 1.1)

**Versão:** 1.0
**Data:** 06/11/2025
**História:** 1.1 - Implementação da Capacidade de Planeamento (SHIELD - Structure)

---

## 🎯 Objetivo do Teste

Validar que a capacidade STRUCTURE foi implementada corretamente e pode ser usada por qualquer agente para gerar planos de execução detalhados e quantificados.

---

## ✅ Critérios de Aceitação da História 1.1

Conforme o PRD, a História 1.1 deve entregar:

- [ ] **CA-1:** Uma capacidade reutilizável que qualquer agente pode usar
- [ ] **CA-2:** Geração de planos detalhados com fases e to-dos
- [ ] **CA-3:** Planos são quantificados (estimativas de tempo, recursos)
- [ ] **CA-4:** Planos incluem checkpoints (HALT, INSPECT, VALIDATE)
- [ ] **CA-5:** Planos identificam riscos e mitigações
- [ ] **CA-6:** Output no formato YAML conforme template

---

## 📋 Pré-requisitos

- [x] Estrutura do projeto criada (Sprint 0 ✅)
- [x] Templates SHIELD disponíveis
- [x] Documentação da fase STRUCTURE criada

---

## 🧪 Casos de Teste

### Teste 1: Validar Existência da Documentação

**Objetivo:** Confirmar que todos os arquivos necessários foram criados

**Passos:**
```bash
cd /home/user/BidAnalyzee

# Verificar guia teórico
ls -lh framework/phases/structure.md

# Verificar prompt reutilizável
ls -lh framework/phases/structure_prompt.md

# Verificar exemplos
ls -lh framework/phases/structure_examples.md

# Verificar README
ls -lh framework/phases/README.md
```

**Resultado Esperado:**
- ✅ Todos os 4 arquivos existem
- ✅ Cada arquivo tem > 5KB de conteúdo (não está vazio)

**Validação:**
```bash
python3 scripts/validate_structure.py
```

---

### Teste 2: Validar Completude do Guia Teórico

**Objetivo:** Verificar que o guia `structure.md` cobre todos os aspectos necessários

**Checklist:**

- [ ] **Seção: Visão Geral**
  - Define o objetivo da fase STRUCTURE
  - Explica o princípio fundamental

- [ ] **Seção: Quando Usar**
  - Lista cenários de uso obrigatório
  - Indica que é obrigatório em Modo Strict

- [ ] **Seção: Como Executar**
  - 6 passos detalhados (Interpretar, Decompor, Checkpoints, Estimar, Riscos, Critérios)
  - Cada passo tem exemplos práticos

- [ ] **Seção: Checklist de Qualidade**
  - Lista de verificação antes de apresentar plano

- [ ] **Seção: Exemplo Completo**
  - Exemplo real em YAML
  - Usa o template `plan_template.yaml`

- [ ] **Seção: Boas Práticas**
  - DO's e DON'Ts claramente definidos

**Comando:**
```bash
grep -E "##|###" framework/phases/structure.md
```

**Resultado Esperado:** Lista todas as seções principais

---

### Teste 3: Validar Prompt Reutilizável

**Objetivo:** Verificar que o prompt `structure_prompt.md` pode ser usado por agentes

**Checklist:**

- [ ] **Instruções Claras**
  - 8 passos numerados
  - Cada passo tem instruções específicas para a IA

- [ ] **Exemplos de Output**
  - Mostra como apresentar ao usuário
  - Inclui menu de aprovação

- [ ] **Checklist de Auto-Inspeção**
  - Lista de verificação antes de apresentar plano

- [ ] **Instruções de Salvamento**
  - Como salvar o plano em YAML
  - Formato de nome do arquivo

**Validação Manual:**
1. Abrir `framework/phases/structure_prompt.md`
2. Verificar se um desenvolvedor consegue entender como incluir isso em um prompt de agente
3. Confirmar que as instruções são claras e não ambíguas

---

### Teste 4: Validar Exemplos Práticos

**Objetivo:** Verificar que os exemplos cobrem diferentes cenários

**Checklist:**

- [ ] **Exemplo 1:** Estruturação de Edital (@EstruturadorDeDocumentos)
  - Complexidade: Média
  - Mostra workflow básico
  - Inclui YAML completo

- [ ] **Exemplo 2:** Análise de Conformidade (@AnalistaTecnico)
  - Complexidade: Alta
  - Mostra processamento em lotes
  - Inclui riscos específicos

- [ ] **Exemplo 3:** Workflow Completo (@Orquestrador)
  - Complexidade: Muito Alta
  - Mostra delegação a outros agentes
  - Checkpoints multi-nível

**Validação:**
```bash
grep -i "exemplo" framework/phases/structure_examples.md | wc -l
```

**Resultado Esperado:** Pelo menos 3 seções de exemplos

---

### Teste 5: Simulação Manual (Teste de Aceitação)

**Objetivo:** Simular o uso da capacidade STRUCTURE por um agente fictício

**Cenário de Teste:**

```markdown
# Você é o @EstruturadorDeDocumentos

Tarefa: "Estruturar o arquivo edital_teste.pdf em CSV"

Execute a fase STRUCTURE seguindo o guia em:
framework/phases/structure_prompt.md
```

**Passos:**

1. **Leia o prompt reutilizável** (`structure_prompt.md`)
2. **Execute mentalmente** os 8 passos
3. **Gere um plano** seguindo as instruções

**Resultado Esperado:**

Um plano mental/escrito que inclua:
- [x] Interpretação do objetivo
- [x] Decomposição em 5-7 etapas
- [x] Checkpoints identificados (INSPECT, VALIDATE, HALT)
- [x] Estimativas de tempo
- [x] Pelo menos 3 riscos
- [x] Critérios de sucesso quantificados

**Validação:**

Se você conseguiu gerar mentalmente um plano completo seguindo apenas o prompt, o teste passou ✅

---

### Teste 6: Conformidade com Template YAML

**Objetivo:** Verificar que o exemplo de plano está conforme `plan_template.yaml`

**Passos:**

1. Abrir `framework/templates/plan_template.yaml`
2. Abrir `framework/phases/structure.md` (seção "Exemplo Completo")
3. Comparar estruturas

**Checklist de Conformidade:**

- [ ] Plano tem campo `plan.task`
- [ ] Plano tem campo `plan.agent`
- [ ] Plano tem campo `plan.estimated_duration`
- [ ] Plano tem campo `plan.context`
- [ ] Plano tem array `plan.steps[]`
- [ ] Cada step tem: id, name, description, estimated_time, dependencies, checkpoints, success_criteria
- [ ] Plano tem array `plan.halt_points[]`
- [ ] Plano tem array `plan.success_criteria[]`
- [ ] Plano tem objeto `plan.risks[]`
- [ ] Plano tem objeto `plan.resources`
- [ ] Plano tem objeto `metadata`

**Comando (verificar campos no exemplo):**
```bash
grep -oE "^  [a-z_]+:" framework/phases/structure.md | sort -u
```

---

### Teste 7: Integração com Outros Componentes

**Objetivo:** Verificar que a capacidade STRUCTURE referencia corretamente outros componentes do SHIELD

**Checklist:**

- [ ] **Referência a Templates:**
  - Menciona `framework/templates/plan_template.yaml`
  - Instruções de como usar o template

- [ ] **Referência a Checklists:**
  - Menciona checklists de INSPECT
  - Link para `framework/checklists/`

- [ ] **Referência a Outras Fases:**
  - Menciona EXECUTE como fase seguinte
  - Menciona INSPECT como checkpoint obrigatório
  - Menciona VALIDATE (L.5)
  - Menciona HALT para aprovação
  - Menciona LOOP para correções

**Validação:**
```bash
grep -i "framework/" framework/phases/structure.md
grep -i "execute\|inspect\|halt\|loop\|validate\|deliver" framework/phases/structure.md
```

---

## 📊 Relatório de Teste

Após executar todos os testes, preencha este checklist:

### Resultados Gerais

- [ ] **Teste 1:** Todos os arquivos existem ✅
- [ ] **Teste 2:** Guia teórico está completo ✅
- [ ] **Teste 3:** Prompt reutilizável é claro ✅
- [ ] **Teste 4:** Exemplos cobrem diferentes cenários ✅
- [ ] **Teste 5:** Simulação manual foi bem-sucedida ✅
- [ ] **Teste 6:** Exemplo conforme template YAML ✅
- [ ] **Teste 7:** Integrações com outros componentes OK ✅

### Critérios de Aceitação da História

- [ ] **CA-1:** Capacidade é reutilizável ✅
  - Evidência: Prompt pode ser incluído em qualquer agente

- [ ] **CA-2:** Gera planos detalhados ✅
  - Evidência: Guia tem 6 passos detalhados + exemplos

- [ ] **CA-3:** Planos são quantificados ✅
  - Evidência: Template inclui estimativas de tempo, tokens, disk space

- [ ] **CA-4:** Inclui checkpoints ✅
  - Evidência: Exemplos mostram INSPECT, VALIDATE, HALT

- [ ] **CA-5:** Identifica riscos ✅
  - Evidência: Template e exemplos incluem seção de riscos

- [ ] **CA-6:** Output em YAML ✅
  - Evidência: Plano usa template plan_template.yaml

### Status Final

**História 1.1:** ✅ APROVADA | ❌ REPROVADA

**Observações:**
```
[Escreva aqui quaisquer problemas encontrados ou sugestões de melhoria]
```

---

## 🐛 Troubleshooting

### Problema: Arquivo não encontrado

**Solução:**
```bash
# Verificar se você está no diretório correto
pwd
# Deve estar em: /home/user/BidAnalyzee

# Re-validar estrutura
python3 scripts/validate_structure.py
```

### Problema: Exemplo não está conforme template

**Solução:**
1. Abrir `framework/templates/plan_template.yaml`
2. Comparar com exemplo em `structure.md`
3. Corrigir discrepâncias

---

## ✅ Próximos Passos

Após validação da História 1.1:

1. **Commitar** a implementação
2. **Marcar História 1.1 como completa** no backlog
3. **Iniciar História 1.2:** Implementação da Capacidade EXECUTE

---

**Executado por:** [Nome do testador]
**Data:** [Data da execução]
**Resultado:** [APROVADA / REPROVADA]
