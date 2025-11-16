# Agent Tests - BidAnalyzee

## 📋 Visão Geral

Testes automatizados para os agents do BidAnalyzee, verificando:
- ✅ Conformidade com prompts e especificações
- ✅ Implementação completa do SHIELD Framework
- ✅ Qualidade dos outputs (CSVs, relatórios)
- ✅ Anti-alucinação e rastreabilidade
- ✅ Integração entre agents

## 🗂️ Estrutura

```
tests/agents/
├── conftest.py                      # Fixtures compartilhadas
├── test_document_structurer.py      # Testes do Document Structurer
├── test_technical_analyst.py        # Testes do Technical Analyst
├── test_orchestrator.py             # Testes do Orchestrator
├── test_shield_framework.py         # Testes do SHIELD Framework
└── README.md                        # Este arquivo
```

## 🧪 Arquivos de Teste

### 1. `conftest.py` - Fixtures Compartilhadas

Fornece dados de teste reutilizáveis:

- **`temp_dir`**: Diretório temporário para testes
- **`sample_pdf_content`**: Conteúdo de exemplo de edital
- **`sample_requirements_csv`**: CSV de requisitos estruturados
- **`sample_analysis_csv`**: CSV de análise de conformidade
- **`sample_rag_response`**: Resposta simulada de RAG search
- **`sample_session_state`**: Estado de sessão do Orchestrator
- **`shield_checklist`**: Checklists SHIELD completos
- **`expected_csv_fields`**: Campos esperados em CSVs

### 2. `test_document_structurer.py` - Document Structurer

**Classes de Teste:**

1. **`TestDocumentStructurerPrompt`** (4 testes)
   - Verifica metadata do prompt
   - Valida responsabilidades definidas
   - Confirma implementação SHIELD
   - Valida estrutura CSV (7 campos)

2. **`TestDocumentStructurerOutput`** (8 testes)
   - Campos obrigatórios presentes
   - Completude (sem campos vazios)
   - Rastreabilidade (campo `pagina`)
   - Scores de confiança válidos (0.0-1.0)
   - Categorias válidas
   - Prioridades válidas
   - Sem duplicatas
   - Encoding UTF-8

3. **`TestDocumentStructurerAntiHallucination`** (3 testes)
   - Todos os items têm referência de página
   - Confiança diminui com ambiguidade
   - Items extraídos apenas do PDF

4. **`TestDocumentStructurerSHIELD`** (6 testes)
   - STRUCTURE: Planejamento
   - HALT: Checkpoints
   - INSPECT: Verificações de qualidade
   - EXECUTE: Geração CSV
   - LOOP: Iteração em falhas
   - DELIVER: Output final + relatório

5. **`TestDocumentStructurerIntegration`** (3 testes)
   - README existe
   - Documentação de validação existe
   - Prompt referencia arquivos de validação

**Total: 24 testes**

### 3. `test_technical_analyst.py` - Technical Analyst

**Classes de Teste:**

1. **`TestTechnicalAnalystPrompt`** (5 testes)
   - Metadata do prompt
   - Capabilities (analyze, reason, judge, recommend)
   - SHIELD Framework
   - RAG search mencionado
   - Veredictos definidos

2. **`TestTechnicalAnalystOutput`** (7 testes)
   - Campos obrigatórios
   - Veredictos válidos (CONFORME, NÃO CONFORME, PARCIAL, REQUER ANÁLISE)
   - Justificativas presentes (≥ 20 chars)
   - Evidências presentes
   - Formato de evidências (`arquivo:linha`)
   - Níveis de confiança válidos
   - Recomendações presentes

3. **`TestTechnicalAnalystRAGIntegration`** (4 testes)
   - Script rag_search.py existe
   - Estrutura de resposta RAG válida
   - Similarity scores no intervalo [0.0, 1.0]
   - Múltiplas evidências retornadas (≥ 2)

4. **`TestTechnicalAnalystSHIELD`** (6 testes)
   - STRUCTURE: Leitura, critérios, estratégia
   - HALT: Checkpoint antes de batch
   - INSPECT: RAG, evidências, contradições, contexto legal
   - EXECUTE: RAG search, veredicto, justificativa, evidências
   - LOOP: Busca adicional se insuficiente
   - DELIVER: CSV + justificativas completas

5. **`TestTechnicalAnalystConsistency`** (4 testes)
   - CONFORME tem evidências
   - NÃO CONFORME tem justificativa detalhada
   - REQUER ANÁLISE não tem confiança alta
   - Alta confiança correlaciona com evidências fortes

6. **`TestTechnicalAnalystIntegration`** (4 testes)
   - pipeline.py existe
   - rag_engine.py existe
   - config.py existe
   - report.py existe

**Total: 30 testes**

### 4. `test_orchestrator.py` - Orchestrator

**Classes de Teste:**

1. **`TestOrchestratorPrompt`** (5 testes)
   - Metadata do prompt
   - Responsabilidades definidas
   - Modos (manual, assistido, FLOW)
   - Comandos definidos
   - SHIELD Framework

2. **`TestOrchestratorState`** (6 testes)
   - StateManager existe
   - Session schema definido
   - Estrutura de estado (session_id, stage, status, etc.)
   - Stage válido
   - Status válido
   - Persistência JSON

3. **`TestOrchestratorCommands`** (3 testes)
   - README documenta comandos
   - Comando *ajuda disponível
   - Comando *listar_analises disponível

4. **`TestOrchestratorWorkflows`** (4 testes)
   - Modo Manual documentado
   - Modo Assistido documentado
   - Modo FLOW documentado
   - Stages de workflow definidos

5. **`TestOrchestratorSHIELD`** (6 testes)
   - STRUCTURE: Sessão, estado, workflow
   - HALT: Checkpoints entre agents
   - INSPECT: Validação de outputs
   - EXECUTE: Roteamento de comandos
   - LOOP: Retry em falhas
   - DELIVER: Workflow completo

6. **`TestOrchestratorIntegration`** (3 testes)
   - Diretório state existe
   - state/__init__.py existe
   - Scripts CLI existem

7. **`TestOrchestratorAgentCoordination`** (4 testes)
   - Gerencia Document Structurer
   - Gerencia Technical Analyst
   - Workflow extração → análise
   - Tratamento de erros documentado

8. **`TestOrchestratorStateBackupRestore`** (4 testes)
   - Método backup_all_sessions existe
   - Método restore_from_backup existe
   - Método cleanup_old_sessions existe
   - Método get_sessions_stats existe

**Total: 35 testes**

### 5. `test_shield_framework.py` - SHIELD Framework

**Classes de Teste:**

1. **`TestSHIELDFrameworkConsistency`** (5 testes)
   - Todos os agents declaram SHIELD
   - Todos têm STRUCTURE
   - Todos têm HALT
   - Todos têm INSPECT
   - Todos têm EXECUTE

2. **`TestSHIELDPhaseCompleteness`** (4 testes)
   - STRUCTURE tem planejamento
   - HALT tem checkpoints
   - INSPECT tem verificações de qualidade
   - EXECUTE tem ações concretas

3. **`TestSHIELDChecklist`** (4 testes)
   - Checklist cobre todas as fases
   - STRUCTURE tem mínimo de items
   - INSPECT tem mínimo de items (crítico)
   - DELIVER valida output final

4. **`TestSHIELDDocumentation`** (2 testes)
   - SHIELD documentado em todos os prompts
   - Acronym SHIELD explicado

5. **`TestSHIELDAntiHallucination`** (3 testes)
   - Document Structurer implementa rastreabilidade
   - Technical Analyst requer evidências
   - Confidence scores documentados

6. **`TestSHIELDLoopPhase`** (2 testes)
   - Todos os agents implementam LOOP/correção
   - Triggers de LOOP documentados

7. **`TestSHIELDIntegration`** (3 testes)
   - Workflow SHIELD end-to-end
   - Checkpoints previnem progressão inválida
   - Quality gates em transições

8. **`TestSHIELDMetrics`** (4 testes)
   - Relatórios de validação existem
   - quality_check.py existe
   - Valida completude
   - Valida consistência

**Total: 27 testes**

## 📊 Resumo

| Arquivo de Teste | Classes | Testes | Foco |
|------------------|---------|--------|------|
| `test_document_structurer.py` | 5 | 24 | Extração e estruturação |
| `test_technical_analyst.py` | 6 | 30 | Análise e conformidade |
| `test_orchestrator.py` | 8 | 35 | Coordenação e estado |
| `test_shield_framework.py` | 8 | 27 | Framework SHIELD |
| **TOTAL** | **27** | **116** | - |

## 🚀 Como Executar

### Executar Todos os Testes de Agents

```bash
pytest tests/agents/ -v
```

### Executar Teste Específico

```bash
# Document Structurer
pytest tests/agents/test_document_structurer.py -v

# Technical Analyst
pytest tests/agents/test_technical_analyst.py -v

# Orchestrator
pytest tests/agents/test_orchestrator.py -v

# SHIELD Framework
pytest tests/agents/test_shield_framework.py -v
```

### Executar Classe de Teste Específica

```bash
pytest tests/agents/test_document_structurer.py::TestDocumentStructurerPrompt -v
```

### Executar Teste Individual

```bash
pytest tests/agents/test_document_structurer.py::TestDocumentStructurerPrompt::test_prompt_metadata_exists -v
```

### Com Coverage

```bash
pytest tests/agents/ --cov=agents --cov-report=html
```

## ✅ O Que os Testes Verificam

### 1. **Conformidade com Prompts**
- Agents seguem suas especificações
- Metadata correto (agent name, version, framework)
- Responsabilidades implementadas

### 2. **SHIELD Framework**
- Todas as 6 fases implementadas (S-H-I-E-L-D)
- Checklists completos
- Checkpoints em momentos críticos
- Iteração e correção (LOOP)

### 3. **Qualidade de Outputs**
- CSVs com campos obrigatórios
- Encoding UTF-8
- Sem duplicatas
- Dados válidos (categorias, prioridades, veredictos)

### 4. **Anti-Alucinação**
- Rastreabilidade (referências de página)
- Evidências citadas corretamente (`arquivo:linha`)
- Scores de confiança calculados
- Justificativas completas

### 5. **Integração**
- Agents coordenados pelo Orchestrator
- Estado persistido corretamente
- Workflows completos (extração → análise)
- Tratamento de erros

## 🎯 Cobertura

Os testes cobrem:

- ✅ **Prompts** - Todos os 3 agents principais
- ✅ **Outputs** - Estrutura e qualidade de CSVs
- ✅ **SHIELD** - Todas as 6 fases
- ✅ **RAG** - Integração com busca de evidências
- ✅ **Estado** - Gestão de sessões
- ✅ **Comandos** - Roteamento e execução
- ✅ **Workflows** - Manual, Assistido, FLOW
- ✅ **Consistência** - Lógica entre campos
- ✅ **Anti-alucinação** - Rastreabilidade e evidências

## 📝 Adicionando Novos Testes

### 1. Para Novo Agent

Criar arquivo `tests/agents/test_<agent_name>.py`:

```python
import pytest
from pathlib import Path

class Test<AgentName>Prompt:
    def test_prompt_exists(self):
        prompt = Path("agents/<agent_name>/prompt.md")
        assert prompt.exists()

class Test<AgentName>Output:
    def test_output_valid(self):
        # Verificar output
        pass
```

### 2. Para Nova Fase SHIELD

Adicionar em `test_shield_framework.py`:

```python
def test_<agent>_has_<new_phase>(self):
    content = Path("agents/<agent>/prompt.md").read_text()
    assert "X - <NEW_PHASE>" in content
```

### 3. Para Nova Funcionalidade

Adicionar no arquivo de teste do agent correspondente:

```python
class Test<Feature>:
    def test_<feature>_implemented(self):
        # Verificar funcionalidade
        pass
```

## 🐛 Troubleshooting

### Fixtures não encontradas

```bash
# Garantir que conftest.py está sendo carregado
pytest tests/agents/ -v --fixtures
```

### Testes falhando

```bash
# Ver output completo
pytest tests/agents/ -v -s

# Ver apenas falhas
pytest tests/agents/ -v --tb=short
```

### Performance lenta

```bash
# Executar em paralelo (requer pytest-xdist)
pytest tests/agents/ -n auto
```

## 📚 Referências

- [pytest Documentation](https://docs.pytest.org/)
- [SHIELD Framework](../../agents/document_structurer/prompt.md)
- [Document Structurer](../../agents/document_structurer/README.md)
- [Technical Analyst](../../agents/technical_analyst/)
- [Orchestrator](../../agents/orchestrator/README.md)

---

**Última atualização:** 16/11/2025
**Versão:** 1.0
**Autor:** BidAnalyzee Team
