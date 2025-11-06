# Architecture Decision Records (ADR)

## Contexto

Este documento registra as decisões arquiteturais tomadas durante o desenvolvimento do Sistema de Análise de Editais com IA, especialmente aquelas que representam **adaptações do PRD original** para a realidade técnica disponível.

---

## ADR-001: Implementação de Agentes como Prompts Estruturados (em vez de Processos Isolados)

**Data:** 06/11/2025
**Status:** ✅ APROVADO
**Decisores:** Equipe de Arquitetura

### Contexto

O PRD original (v5.3, História 1.8) especifica:
> "Implementação da Capacidade de Orquestração via SDK que permite ao @Orquestrador iniciar, controlar e receber resultados de outros processos de terminal de forma programática e isolada."

**Problema:** Claude Code não oferece um SDK ou API para orquestração programática de processos isolados.

### Decisão

Implementar agentes como **prompts estruturados com YAML frontmatter**, carregados dinamicamente pelo contexto principal, em vez de processos separados.

### Alternativas Consideradas

1. **Múltiplas sessões bash com comunicação via arquivos**
   - ❌ Frágil
   - ❌ Difícil de depurar
   - ❌ Controle de estado complexo

2. **MCP Servers customizados**
   - ⚠️ Requer infraestrutura adicional
   - ⚠️ Curva de aprendizado
   - ✅ Possível evolução futura

3. **Prompts estruturados (ESCOLHIDA)**
   - ✅ Simples e manutenível
   - ✅ Controle total do fluxo
   - ✅ Estado consistente
   - ✅ Fácil de testar

### Consequências

**Positivas:**
- Implementação mais simples e rápida
- Debugging facilitado
- UX unificada e fluida
- Versionamento mais fácil (prompts como código)

**Negativas:**
- "Clean Handoff" é lógico, não físico (menos isolamento)
- Todo o contexto roda na mesma sessão (limite de tokens)

**Mitigações:**
- Documentar explicitamente o "fim" de cada contexto de agente
- Usar checklists para garantir completude antes de transições
- Implementar chunking/streaming para gestão de tokens

---

## ADR-002: Slash Commands como Interface Primária

**Data:** 06/11/2025
**Status:** ✅ APROVADO

### Contexto

O PRD especifica "Interface de Linha de Comando (CLI) conversacional" (Seção 4).

### Decisão

Usar **Slash Commands nativos do Claude Code** (`.claude/commands/*.md`) como interface primária.

### Justificativa

- Integração nativa com o ambiente do usuário
- Experiência consistente com outras ferramentas do IDE
- Descoberta fácil (autocomplete)
- Não requer instalação de ferramentas externas

### Comandos Principais

- `/iniciar-analise` → Modo Assistido (História 4.2)
- `/flow` → Modo FLOW automatizado (História 4.3)
- `/consulta-rapida <pergunta>` → Consulta instantânea (História 4.4)
- `/estruturar-edital <arquivo>` → Apenas estruturação (standalone)

---

## ADR-003: Sistema de Arquivos como Camada de Persistência

**Data:** 06/11/2025
**Status:** ✅ APROVADO

### Contexto

Precisamos de um mecanismo para:
- Manter histórico de análises
- Persistir estado entre comandos
- Armazenar CSVs, logs, outputs

### Decisão

Usar **sistema de arquivos local** com estrutura padronizada:

```
data/
├── analyses/           # Uma pasta por análise
│   ├── ANA-20250806-001/
│   │   ├── metadata.json
│   │   ├── edital_original.pdf
│   │   ├── requisitos_estruturados.csv
│   │   ├── resultado_analise.csv
│   │   └── logs.txt
│   └── ...
├── state/
│   ├── index_analises.csv      # Índice master
│   └── current_session.json    # Estado da sessão ativa
└── templates/
    └── output_template.csv
```

### Alternativas Consideradas

1. **Banco de dados SQLite**
   - ⚠️ Overhead desnecessário para MVP
   - ✅ Melhor para escala futura

2. **Sistema de arquivos (ESCOLHIDA)**
   - ✅ Zero configuração
   - ✅ Transparente para o usuário
   - ✅ Fácil auditoria e backup

### Consequências

- Fácil para o usuário entender e auditar
- Simples de versionar (git)
- Pode ficar desorganizado com muitas análises (mitigar com limpeza periódica)

---

## ADR-004: n8n como Camada de Serviços (Ingestão + Consulta)

**Data:** 06/11/2025
**Status:** ✅ APROVADO

### Contexto

Precisamos de:
1. Ingestão automatizada de dados (scraping + embeddings + Pinecone)
2. Serviço de consulta RAG (busca + re-ranking)

### Decisão

Implementar **dois workflows n8n**:

1. **Workflow de Ingestão** (agendado)
   - Web Scraper → Processar conteúdo → Gerar embeddings → Inserir no Pinecone
   - Trigger: Cron (a cada 4 meses)
   - Logs em Google Sheets (MVP)

2. **Workflow de Consulta** (HTTP API)
   - Endpoint: `POST /query`
   - Input: `{ "query": "requisito do edital", "top_k": 20 }`
   - Output: `{ "results": [...], "confidence": 0.XX }`
   - Lógica: Embedding da query → Busca no Pinecone → Re-ranking → Top 3-5

### Justificativa

- Desacoplamento: Agentes só consomem a API, não gerenciam infraestrutura
- Reutilização: Outros sistemas podem usar o mesmo serviço
- Observabilidade: n8n tem logs e monitoring built-in
- Flexibilidade: Fácil adicionar novos modelos de embedding/re-ranking

### Localização

- Workflows exportados em `services/n8n/*.json`
- Documentação em `services/n8n/README.md`
- URL do serviço em `.env`

---

## ADR-005: YAML + Markdown para Definição de Agentes

**Data:** 06/11/2025
**Status:** ✅ APROVADO

### Contexto

Precisamos de uma forma de definir agentes que seja:
- Legível por humanos
- Versionável (git-friendly)
- Estruturada o suficiente para validação
- Flexível para iteração rápida de prompts

### Decisão

Usar **YAML frontmatter + Markdown** para prompts de agentes:

```yaml
---
agent: technical_analyst
version: 2.1
role: Analista Técnico de Conformidade
capabilities:
  - structure
  - execute
  - inspect
  - validate
  - loop
checklists:
  inspect: ./checklists/inspect.yaml
  validate: ./checklists/validate.yaml
dependencies:
  - service: n8n_query_service
    endpoint: ${N8N_QUERY_URL}
parameters:
  confidence_threshold: 0.85
  top_k_results: 20
  rerank_top_n: 5
---

# @AnalistaTecnico

Você é um agente especializado em análise de conformidade técnica...

## Seu Processo (SHIELD)

### STRUCTURE
Antes de analisar cada requisito, você DEVE:
...
```

### Benefícios

- Separação clara de metadata (YAML) e prompt (Markdown)
- IDEs renderizam Markdown automaticamente
- Fácil validar schema do YAML
- Prompts podem ser editados sem quebrar código

---

## ADR-006: Modo Strict como Padrão Obrigatório

**Data:** 06/11/2025
**Status:** ✅ APROVADO (conforme NFR12 do PRD)

### Contexto

O PRD (v5.3, Seção 2) estabelece:
> "O sistema deve operar exclusivamente no **Modo Strict** de rigor."

### Decisão

Implementar **apenas o Modo Strict**, sem modos "relaxados" ou "quick".

**Modo Strict significa:**
- ✅ Todos os checklists são obrigatórios
- ✅ Fase `L.5 - VALIDATE` sempre ativa
- ✅ Validação quantitativa (100% de completude)
- ✅ Evidências para cada decisão
- ✅ Tolerância zero a erros de processo

### Consequências

**Positivas:**
- Máxima confiabilidade
- Conformidade total com a governança SHIELD
- Auditabilidade completa

**Negativas:**
- Pode ser "mais lento" que abordagens heurísticas
- Usuários podem sentir "excesso de validação"

**Mitigação:**
- Comunicar claramente o valor do rigor
- Métricas de qualidade (85%+ de precisão) justificam o processo
- Modo FLOW acelera para usuários que confiam no sistema

---

## ADR-007: Tolerância Zero no Processo, Não no Modelo

**Data:** 06/11/2025
**Status:** ✅ APROVADO (conforme Recomendação R-02 do PO)

### Contexto

O PRD menciona "Tolerância Zero a Erros" mas também aceita "Precisão > 85%". Há uma aparente contradição.

### Decisão (Recomendação R-02)

**Tolerância Zero aplica-se ao PROCESSO, não ao modelo de IA:**

- O **processo SHIELD** não deve cometer erros (detectar, sinalizar, gerenciar incertezas)
- O **modelo de IA subjacente** pode ter ~15% de casos de baixa confiança
- O SHIELD garante que esses 15% sejam **corretamente identificados e marcados para revisão humana**

### Exemplo

Cenário: Modelo analisa um requisito e retorna confiança de 72% (abaixo de 85%).

❌ **Processo com erro:** Sistema marca como "Conforme" e segue em frente.

✅ **Processo correto (Modo Strict):**
1. Sistema detecta confiança < 85% (fase INSPECT)
2. Marca o item como "⚠️ Revisão humana necessária"
3. Registra no log a justificativa da baixa confiança
4. Notifica o usuário no final (fase DELIVER)

**Resultado:** O processo operou com "tolerância zero" porque identificou e tratou corretamente a incerteza.

---

## ADR-008: Logs de Aplicação Incluídos no Output

**Data:** 06/11/2025
**Status:** ✅ APROVADO (conforme NFR8 do PRD)

### Contexto

NFR8 estabelece:
> "O sistema deve gerar logs de aplicação em arquivo... o custo de tokens associado é um custo operacional marginal e aceitável."

### Decisão

Todos os agentes geram logs estruturados durante a execução:

```json
{
  "timestamp": "2025-11-06T10:30:00Z",
  "agent": "technical_analyst",
  "phase": "VALIDATE",
  "action": "validacao_quantitativa",
  "details": {
    "total_items": 50,
    "processed": 50,
    "flagged_for_review": 7,
    "completeness": "100%"
  },
  "status": "SUCCESS"
}
```

**Localização:** `data/analyses/{id}/logs.txt`

### Justificativa

- Observabilidade essencial para debugging
- Conformidade com o princípio SHIELD de transparência
- Auditoria de cada decisão do sistema
- Custo de tokens é marginal comparado ao valor

---

## ADR-009: Estratégia de Gestão de Tokens

**Data:** 06/11/2025
**Status:** ✅ APROVADO

### Contexto

Editais podem ter centenas de requisitos. Prompts longos + contexto acumulado podem exceder limites de tokens.

### Decisão

Implementar estratégia em camadas:

1. **Chunking de Requisitos**
   - Processar CSV em lotes de 25 requisitos
   - Cada lote é uma "mini-análise" independente
   - Resultados são agregados ao final

2. **Resumos Progressivos**
   - Após cada lote, gerar resumo executivo
   - Contexto do próximo lote inclui apenas o resumo (não todo o histórico)

3. **Streaming de Contexto**
   - Carregar apenas o checklist relevante para a fase atual
   - "Fechar" contextos de fases anteriores após HALT aprovado

4. **Monitoramento**
   - Log de uso de tokens em cada fase
   - Alerta se uso > 80% do limite

### Exemplo de Fluxo

```
Lote 1 (req 1-25)  → Análise → 15k tokens
Lote 2 (req 26-50) → Análise → 15k tokens (usando resumo do Lote 1)
Lote 3 (req 51-75) → Análise → 15k tokens (usando resumo dos Lotes 1-2)
```

---

## Resumo de Decisões

| ADR | Decisão | Impacto no PRD Original |
|-----|---------|-------------------------|
| 001 | Agentes como prompts | ⚠️ Adaptação da História 1.8 |
| 002 | Slash Commands | ✅ Alinhado com Seção 4 (UX) |
| 003 | Sistema de arquivos | ✅ Alinhado com FR7 |
| 004 | n8n para serviços | ✅ Alinhado com Histórias 3.1-3.3 |
| 005 | YAML + Markdown | ✅ Alinhado com NFR9 |
| 006 | Modo Strict obrigatório | ✅ Alinhado com Seção 2 e NFR12 |
| 007 | Tolerância Zero no processo | ✅ Alinhado com R-02 |
| 008 | Logs incluídos | ✅ Alinhado com NFR8 |
| 009 | Gestão de tokens | ✅ Habilita NFR1 (< 1 hora) |

---

## Próximas Decisões Pendentes

- [ ] **ADR-010:** Estratégia de testes (unitários vs. integração vs. E2E)
- [ ] **ADR-011:** Gestão de configuração (arquivo único vs. múltiplos)
- [ ] **ADR-012:** Estratégia de versionamento de prompts
- [ ] **ADR-013:** Formato de evidências no CSV de saída

---

**Documento Vivo:** Este ADR será atualizado conforme novas decisões forem tomadas durante a implementação.
