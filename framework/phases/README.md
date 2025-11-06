# SHIELD Framework - Guias de Fases

**Versão:** 1.0
**Localização:** `framework/phases/`

---

## 📚 Visão Geral

Esta pasta contém os guias de implementação para cada fase do Framework SHIELD. Cada guia fornece instruções detalhadas, prompts reutilizáveis e exemplos de como executar a fase corretamente.

---

## 🗂️ Fases Disponíveis

### ✅ S - STRUCTURE (Estrutura)

**Status:** ✅ IMPLEMENTADO (História 1.1 - Sprint 1)

**Objetivo:** Planejar a tarefa de forma quantificada antes da execução

**Arquivos:**
- 📖 **[structure.md](structure.md)** - Guia teórico completo
- 🤖 **[structure_prompt.md](structure_prompt.md)** - Prompt reutilizável para agentes
- 📊 **[structure_examples.md](structure_examples.md)** - Exemplos práticos

**Quando usar:** Obrigatório no início de TODA tarefa (Modo Strict)

**Saída:** Arquivo YAML com plano detalhado (`data/state/plan_[id].yaml`)

**Exemplo de uso em um agente:**
```markdown
## Protocolo de Início de Tarefa

Quando você receber uma nova tarefa, siga a fase STRUCTURE:

{{incluir: framework/phases/structure_prompt.md}}
```

---

### ✅ E - EXECUTE (Execução)

**Status:** ✅ IMPLEMENTADO (História 1.2 - Sprint 1)

**Objetivo:** Executar tarefas de forma controlada com logging e error handling

**Arquivos:**
- 📖 **[execute.md](execute.md)** - Guia teórico completo
- 🤖 **[execute_prompt.md](execute_prompt.md)** - Prompt reutilizável para agentes
- 📊 **[execute_examples.md](execute_examples.md)** - Exemplos práticos

**Quando usar:** Para executar CADA etapa do plano (após aprovação)

**Saída:** ExecutionResult estruturado + logs completos

**Exemplo de uso:**
```markdown
## Protocolo de Execução

Para cada etapa do plano, execute seguindo:

{{incluir: framework/phases/execute_prompt.md}}
```

---

### 🔄 H - HALT (Parada)

**Status:** 🚧 A IMPLEMENTAR (História 1.5 - Sprint 2)

**Objetivo:** Pausar o workflow para solicitar aprovação do usuário

**Arquivos (futuros):**
- 📖 `halt.md` - Guia teórico
- 🤖 `halt_prompt.md` - Prompt reutilizável
- 📊 `halt_examples.md` - Exemplos de menus de aprovação

**Quando usar:** Após cada etapa macro, quando houver ambiguidade, ou conforme o plano

---

### ✅ I - INSPECT (Inspeção)

**Status:** ✅ IMPLEMENTADO (História 1.3 - Sprint 1)

**Objetivo:** Auto-inspeção rigorosa usando checklists

**Arquivos:**
- 📖 **[inspect.md](inspect.md)** - Guia teórico completo
- 🤖 **[inspect_prompt.md](inspect_prompt.md)** - Prompt reutilizável para agentes
- 📊 **[inspect_examples.md](inspect_examples.md)** - Exemplos de execução de checklists

**Quando usar:** Obrigatório após TODA fase EXECUTE

**Saída:** InspectionResult YAML + decisão (VALIDATE ou LOOP)

**Exemplo de uso:**
```markdown
## Após Executar uma Etapa

Execute auto-inspeção usando checklists:

{{incluir: framework/phases/inspect_prompt.md}}
```

---


---

### 🔁 L - LOOP (Repetição)

**Status:** 🚧 A IMPLEMENTAR (História 1.4 - Sprint 1)

**Objetivo:** Corrigir problemas identificados na fase INSPECT

**Arquivos (futuros):**
- 📖 `loop.md` - Guia teórico
- 🤖 `loop_prompt.md` - Prompt reutilizável
- 📊 `loop_examples.md` - Exemplos de ciclos de correção

**Quando usar:** Automático quando INSPECT falha, ou manual via feedback do usuário

---

### ✅ L.5 - VALIDATE (Validação Quantitativa)

**Status:** 🚧 A IMPLEMENTAR (História 1.6 - Sprint 2)

**Objetivo:** Validação quantitativa de 100% de completude

**Arquivos (futuros):**
- 📖 `validate.md` - Guia teórico
- 🤖 `validate_prompt.md` - Prompt reutilizável
- 📊 `validate_examples.md` - Exemplos de métricas quantitativas

**Quando usar:** Obrigatório após INSPECT passar, antes de HALT ou DELIVER

---

### 📦 D - DELIVER (Entrega)

**Status:** 🚧 A IMPLEMENTAR (História 1.7 - Sprint 2)

**Objetivo:** Entrega formal com evidências completas

**Arquivos (futuros):**
- 📖 `deliver.md` - Guia teórico
- 🤖 `deliver_prompt.md` - Prompt reutilizável
- 📊 `deliver_examples.md` - Exemplos de relatórios finais

**Quando usar:** Após aprovação do usuário no último HALT

---

## 🔄 Fluxo Completo do SHIELD

```
┌─────────────────┐
│   STRUCTURE     │ ← Você está aqui (História 1.1 ✅)
│  (Planejar)     │
└────────┬────────┘
         │
         ↓
    [Apresentar plano ao usuário]
         │
         ↓
┌────────┴────────┐
│      HALT       │ (História 1.5 🚧)
│   (Aprovar?)    │
└────────┬────────┘
         │
         ↓ [Aprovado]
┌────────┴────────┐
│     EXECUTE     │ (História 1.2 🚧)
│  (Executar      │
│   etapa 1)      │
└────────┬────────┘
         │
         ↓
┌────────┴────────┐
│     INSPECT     │ (História 1.3 🚧)
│  (Checklist)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Passou? │
    └────┬────┘
         │
    ❌ Não│  Sim ✅
         │    │
         ↓    ↓
    ┌────┴────┐
    │  LOOP   │ (História 1.4 🚧)
    │ (Corrig │
    │  ir)    │
    └────┬────┘
         │
         └─→ volta para EXECUTE
              │
              ↓
         ┌────┴────────┐
         │  VALIDATE   │ (História 1.6 🚧)
         │  (100%?)    │
         └────┬────────┘
              │
              ↓
         ┌────┴────────┐
         │    HALT     │
         │ (Mostrar    │
         │  resultado) │
         └────┬────────┘
              │
              ↓ [Todas as etapas concluídas]
         ┌────┴────────┐
         │   DELIVER   │ (História 1.7 🚧)
         │ (Entrega    │
         │  final)     │
         └─────────────┘
```

---

## 📖 Como Usar os Guias

### Para Desenvolvedores de Agentes

1. **Leia o guia teórico** (`[fase].md`) para entender a filosofia e regras
2. **Use o prompt reutilizável** (`[fase]_prompt.md`) no prompt do seu agente
3. **Consulte os exemplos** (`[fase]_examples.md`) para casos de uso específicos

### Para Desenvolvedores do Framework

1. **Siga o template** dos guias já criados (STRUCTURE)
2. **Mantenha consistência** em estrutura e formato
3. **Inclua sempre:**
   - Guia teórico (conceitos, quando usar, como executar)
   - Prompt reutilizável (instruções para a IA)
   - Exemplos práticos (casos reais)

---

## 🎓 Roadmap de Implementação

| História | Fase | Sprint | Status |
|----------|------|--------|--------|
| 1.1 | STRUCTURE | Sprint 1 | ✅ Completa |
| 1.2 | EXECUTE | Sprint 1 | ✅ Completa |
| 1.3 | INSPECT | Sprint 1 | ✅ Completa |
| 1.4 | LOOP | Sprint 1 | 🚧 Pendente |
| 1.5 | HALT | Sprint 2 | 🚧 Pendente |
| 1.6 | VALIDATE | Sprint 2 | 🚧 Pendente |
| 1.7 | DELIVER | Sprint 2 | 🚧 Pendente |

---

## 📚 Referências

- **Framework SHIELD completo:** `../OPERATING_PRINCIPLES.md`
- **Templates YAML:** `../templates/`
- **Checklists:** `../checklists/`
- **PRD:** `../../PRD.md` (seções sobre Épico 1)

---

## 🆘 Suporte

Se você está implementando um novo agente e tem dúvidas sobre como usar uma fase:

1. Consulte o guia teórico da fase
2. Veja os exemplos práticos
3. Use o prompt reutilizável como base
4. Adapte conforme necessário para seu contexto

---

**Última atualização:** 06/11/2025 (História 1.1 completa)
**Próxima atualização:** Após História 1.2 (EXECUTE)
