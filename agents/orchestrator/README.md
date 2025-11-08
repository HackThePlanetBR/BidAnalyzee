# Orchestrator Agent

**Versão:** 1.0  
**Status:** ✅ Base Implementation Complete (Sprint 8)  
**Agent ID:** `@Orquestrador`

---

## 📋 Visão Geral

O **Orchestrator** é o agente maestro do sistema BidAnalyzee. Ele coordena todos os outros agentes (Document Structurer, Technical Analyst), gerencia o estado do sistema, roteia comandos, e orquestra workflows completos de análise de editais.

**Princípio:** O Orchestrator não faz análise técnica diretamente - ele delega para agentes especializados e coordena a execução.

---

## 🎯 Responsabilidades

### 1. Coordenação de Agentes
- Delegar extração de requisitos para @DocumentStructurer
- Delegar análise de conformidade para @AnalistaTecnico
- Garantir que outputs de um agente sejam inputs válidos para o próximo
- Monitorar execução e detectar falhas

### 2. Gestão de Estado
- Criar e gerenciar sessões de análise
- Persistir estado em `data/state/sessions/*.json`
- Manter índice de análises (`data/state/index.json`)
- Rastrear progresso de workflows

### 3. Roteamento de Comandos
- `*ajuda` - Lista comandos disponíveis
- `*listar_analises` - Histórico de análises
- `*sessao [id]` - Detalhes de sessão específica

### 4. Orquestração de Workflows
- **Manual** (Sprint 8): Aguarda aprovação em cada etapa
- **Assistido** (Sprint 9 - futuro): Sugere próximos passos
- **FLOW** (Sprint 10 - futuro): Execução automática

---

## 📁 Arquitetura

```
agents/orchestrator/
├── prompt.md                      # ✅ Agent prompt (SHIELD framework)
├── checklists/
│   ├── inspect.yaml               # ✅ Auto-inspeção durante execução
│   └── validate.yaml              # ✅ Validação final antes de entregar
├── README.md                      # ✅ Esta documentação
└── [Python implementation - Sprint 8+]
    ├── orchestrator.py            # ⏳ Classe principal (futuro)
    ├── state_manager.py           # ⏳ Gerenciamento de estado (futuro)
    ├── command_router.py          # ⏳ Roteamento de comandos (futuro)
    └── session.py                 # ⏳ Sessões de análise (futuro)
```

**Status Atual (Sprint 8 Base):**
- ✅ Prompt do agente completo
- ✅ Checklists SHIELD (inspect + validate)
- ⏳ Implementação Python (próximos sprints, se necessário)

---

## 🔄 Workflow Típico

### Análise Completa (PDF → Relatório)

```
1. Usuário: "Analise edital_001.pdf"
   ↓
2. Orchestrator: [S] STRUCTURE - Planeja workflow
   ↓
3. Orchestrator: [H] HALT - Apresenta plano, aguarda aprovação
   ↓
4. Usuário: "s" (aprova)
   ↓
5. Orchestrator: [I+E] Delega para @DocumentStructurer
   /structure-edital data/.../inputs/edital_001.pdf
   ↓
6. DocumentStructurer: Extrai requisitos → requirements_structured.csv
   ↓
7. Orchestrator: [L] LOOP - Verifica output, atualiza estado
   ↓
8. Orchestrator: [I+E] Delega para @AnalistaTecnico
   /analyze-edital data/.../outputs/requirements_structured.csv
   ↓
9. AnalistaTecnico: Analisa conformidade → analysis.csv
   ↓
10. Orchestrator: [L.5] VALIDATE - Valida tudo (checklist validate.yaml)
   ↓
11. Orchestrator: [D] DELIVER - Apresenta resumo executivo ao usuário
```

---

## 🗂️ Gestão de Estado

### Estrutura de Sessão

```json
{
  "session_id": "analysis_edital_001_20251108_143022",
  "status": "completed",
  "created_at": "2025-11-08T14:30:22Z",
  "updated_at": "2025-11-08T15:17:10Z",
  "edital_info": {
    "numero": "001/2024",
    "orgao": "Prefeitura Municipal",
    "pdf_path": "..."
  },
  "workflow": {
    "mode": "manual",
    "current_stage": "completed",
    "stages_completed": ["extraction", "analysis", "reporting"]
  },
  "results": {
    "document_structurer": {
      "status": "completed",
      "csv_path": ".../requirements_structured.csv",
      "total_requirements": 50
    },
    "technical_analyst": {
      "status": "completed",
      "csv_path": ".../analysis.csv",
      "conformity_summary": {
        "CONFORME": 35,
        "NAO_CONFORME": 2,
        "REVISAO": 13
      }
    }
  },
  "output_dir": "data/deliveries/analysis_edital_001_20251108_143022"
}
```

### Diretórios de Estado

```
data/
├── state/
│   ├── sessions/              # Sessões individuais
│   │   ├── analysis_001.json
│   │   └── analysis_002.json
│   ├── index.json             # Índice de todas as sessões
│   └── current_session.json   # Sessão ativa (se houver)
│
└── deliveries/                # Outputs organizados
    └── analysis_edital_001_20251108_143022/
        ├── inputs/
        │   └── edital.pdf
        ├── outputs/
        │   ├── requirements_structured.csv
        │   ├── analysis.csv
        │   └── report.md
        └── session.json       # Cópia do estado
```

---

## 🎛️ Comandos Disponíveis

### `*ajuda`
Lista todos os comandos disponíveis no sistema.

```
🤖 BIDANALYZEE - COMANDOS DISPONÍVEIS
📋 ANÁLISE: /structure-edital, /analyze-edital
🎛️ ORQUESTRADOR: *ajuda, *listar_analises, *sessao
```

### `*listar_analises`
Mostra histórico de todas as análises realizadas.

```
📊 HISTÓRICO DE ANÁLISES
[1] analysis_edital_001_20251108
    ├─ Status: ✅ Completed
    ├─ Conformidade: 70% (35/50)
    └─ Tempo: 47 min
```

### `*sessao [session_id]`
Exibe detalhes completos de uma sessão (ou sessão atual se ID omitido).

---

## 📊 SHIELD Framework

O Orchestrator segue rigorosamente o framework SHIELD:

| Fase | Nome | Descrição |
|------|------|-----------|
| **S** | STRUCTURE | Planeja workflow completo |
| **H** | HALT | Apresenta plano e aguarda aprovação do usuário |
| **I** | INSPECT | Auto-inspeção antes de cada ação (checklist inspect.yaml) |
| **E** | EXECUTE | Delega para agentes especializados |
| **L** | LOOP | Verifica resultado, decide próximo passo |
| **L.5** | VALIDATE | Validação final de qualidade (checklist validate.yaml) |
| **D** | DELIVER | Apresenta resultados consolidados ao usuário |

---

## ✅ Checklists

### Inspect Checklist (`inspect.yaml`)

Auto-inspeção durante execução:
- ✅ Pre-workflow: Session ID, diretórios, plano apresentado?
- ✅ Pre-agent delegation: Input válido, agent anterior completou?
- ✅ Post-agent execution: Output criado, formato válido?
- ✅ Workflow transition: Stage anterior completo, inputs válidos?
- ✅ Error handling: Erro capturado, usuário notificado?
- ✅ State management: Sessão salva, índice atualizado?

### Validate Checklist (`validate.yaml`)

Validação final antes de entregar:
- ✅ Session completeness: Todos os stages completados?
- ✅ Output files: CSVs existem, são válidos?
- ✅ Data consistency: Totais consistentes, IDs matcham?
- ✅ Quality checks: Nenhum campo vazio, raciocínios adequados?
- ✅ State persistence: Estado salvo, índice atualizado?
- ✅ Statistics: Taxa de conformidade calculada?
- ✅ Delivery readiness: Resumo executivo preparado?

---

## 🚀 Roadmap

### ✅ Sprint 8 (Atual) - Orchestrator Base
- [x] Prompt do agente (`prompt.md`)
- [x] Checklists SHIELD (`inspect.yaml`, `validate.yaml`)
- [x] Documentação (`README.md`)
- [ ] Implementação Python (opcional, se necessário)

### 🔮 Sprint 9 (Futuro) - Modo Assistido
- [ ] Orchestrator sugere próximos passos
- [ ] Usuário aprova cada sugestão
- [ ] Workflow mais fluido

### 🔮 Sprint 10 (Futuro) - Modo FLOW
- [ ] Execução automática completa
- [ ] Checkpoints HALT apenas em pontos críticos
- [ ] One-command full analysis

---

## 📖 Referências

- **Agent Prompt:** `agents/orchestrator/prompt.md`
- **Checklists:** `agents/orchestrator/checklists/`
- **Sprint Plan:** `SPRINT_8_PLAN.md`
- **Document Structurer:** `agents/document_structurer/`
- **Technical Analyst:** `agents/technical_analyst/`

---

## 💡 Filosofia

> "O Orchestrator é o maestro, não o músico. Ele conhece a partitura completa, coordena a entrada de cada instrumento, e garante que todos toquem em harmonia. Mas não toca os instrumentos - delega para os especialistas."

**Princípios:**
1. 🎯 **Coordenação > Execução**: Delega em vez de fazer
2. 🛡️ **Governança SHIELD**: Sempre seguir S-H-I-E-L-L.5-D
3. 📊 **Estado Confiável**: Persistir tudo, sempre atualizado
4. 👤 **User-Centric**: HALT antes de executar, feedback claro

---

**Status:** ✅ Sprint 8 Base - Completo  
**Próximo:** Sprint 9 - Modo Assistido (quando necessário)
