# Sprint 4 - Document Structurer: Finalização e Enriquecimento

**Início:** 06/11/2025
**Épico:** Épico 2 - Agentes Especializados
**Objetivo:** Finalizar o agente Document Structurer com features de enriquecimento e rastreabilidade

---

## 🎯 Objetivo do Sprint

Adicionar funcionalidades complementares ao **Document Structurer** para:
1. Extrair metadados principais do edital (Objeto, Escopo, Órgão, Valor)
2. Manter histórico de análises (índice centralizado)
3. Validar end-to-end com cenários avançados (LOOP, erros, PDF real)

---

## 📋 Histórias do Sprint 4

### História 2.4: Extração de Objeto/Escopo
**Objetivo:** Extrair metadados principais do edital além dos requisitos técnicos

**Entregáveis:**
- `agents/document_structurer/extractors/metadata_extractor.py` - Extrator de metadados
- `agents/document_structurer/extractors/README.md` - Documentação do extrator
- `tests/unit/test_metadata_extractor.py` - Testes unitários
- Atualização do prompt.md com nova funcionalidade

**Critérios de Aceite:**
- [ ] Extrai objeto da licitação do edital
- [ ] Extrai escopo do projeto
- [ ] Extrai órgão contratante
- [ ] Extrai valor estimado (se disponível)
- [ ] Extrai prazo de entrega
- [ ] Salva metadados em `metadata.yaml` no delivery package
- [ ] Integrado ao fluxo SHIELD (EXECUTE step 0)

**Metadados extraídos:**
```yaml
metadata:
  objeto: "Aquisição de Sistema de Videomonitoramento"
  orgao: "Prefeitura Municipal de São Paulo"
  valor_estimado: "R$ 2.500.000,00"
  prazo_entrega: "180 dias"
  modalidade: "Pregão Eletrônico"
  numero_edital: "PMSP-2025-001"
  data_publicacao: "2025-01-15"
```

---

### História 2.5: Índice de Análises
**Objetivo:** Manter histórico centralizado de todas as análises executadas

**Entregáveis:**
- `data/index_analises.csv` - Índice centralizado
- `agents/document_structurer/index_manager.py` - Gerenciador de índice
- `tests/unit/test_index_manager.py` - Testes unitários
- Atualização do DELIVER phase para registrar no índice

**Critérios de Aceite:**
- [ ] CSV de índice com campos: ID, Data, Edital, Requisitos, Status, Tempo, Path
- [ ] Cada nova análise adiciona linha ao índice
- [ ] Índice permite consulta de análises anteriores
- [ ] Comando `/listar-analises` lista histórico
- [ ] Validação de duplicatas (mesmo edital não pode ser analisado 2x)

**Estrutura do índice:**
```csv
ID,Data,Edital,Requisitos,Status,Tempo,Path
1,2025-11-06 14:00,PMSP-2025-001,47,COMPLETO,15m20s,data/deliveries/analysis_PMSP-2025-001_20251106_140000
2,2025-11-07 09:30,PMRJ-2025-087,32,COMPLETO,7m30s,data/deliveries/analysis_PMRJ-2025-087_20251107_093000
```

---

### História 2.6: Testes End-to-End Avançados
**Objetivo:** Validar cenários complexos e edge cases

**Entregáveis:**
- `tests/integration/test_loop_scenarios.py` - Testes de LOOP
- `tests/integration/test_error_handling.py` - Testes de error handling
- `tests/fixtures/edital_with_errors.yaml` - Fixture com erros intencionais
- `docs/E2E_TEST_REPORT.md` - Relatório de testes avançados

**Critérios de Aceite:**
- [ ] Teste de LOOP com requisito complexo (decomposição)
- [ ] Teste de LOOP com categoria inválida
- [ ] Teste de LOOP com IDs não sequenciais
- [ ] Teste de error handling (PDF encrypted, scanned, corrupted)
- [ ] Teste de low confidence items (< 0.85)
- [ ] Todos os testes passam
- [ ] Relatório documentado

**Cenários de teste:**

1. **LOOP Scenario 1: Decomposição**
   - Input: Requisito "Sistema com resolução 4K e taxa de 60 fps"
   - Expected: 2 requisitos separados após LOOP

2. **LOOP Scenario 2: Categoria Inválida**
   - Input: Requisito com categoria "Administrativo" (inválida)
   - Expected: Reclassificado para "Serviço" após LOOP

3. **Error Scenario 1: PDF Encrypted**
   - Input: PDF protegido por senha
   - Expected: HALT com mensagem clara

4. **Error Scenario 2: Low Confidence**
   - Input: 5+ requisitos com confiança < 0.85
   - Expected: HALT checkpoint 2 acionado

---

## 🛠️ Stack Técnico

### Novas Dependências

```python
# Metadata extraction (if using real PDFs)
# pdfplumber==0.10.3  # For extracting from specific sections

# Additional utils
pathlib  # Already in stdlib
csv      # Already in stdlib
```

### Estrutura de Arquivos Atualizada

```
agents/document_structurer/
├── README.md
├── capabilities.yaml
├── architecture.md
├── prompt.md
│
├── extractors/                    # ⭐ NOVO
│   ├── README.md
│   └── metadata_extractor.py
│
├── index_manager.py               # ⭐ NOVO
│
├── checklists/
│   └── inspect.yaml
│
├── examples/
│   ├── example_1_simple.md
│   ├── example_2_medium.md
│   └── example_3_complex.md
│
└── tests/
    ├── test_extract.py
    ├── test_identify.py
    └── test_structure.py

data/
├── index_analises.csv             # ⭐ NOVO
├── deliveries/
│   └── analysis_{edital}_{timestamp}/
│       ├── outputs/
│       │   └── requirements_structured.csv
│       ├── evidences/
│       ├── metadata/
│       │   ├── plan.yaml
│       │   ├── edital_metadata.yaml  # ⭐ NOVO
│       │   └── timeline.yaml
│       ├── sources/
│       └── README.md

tests/
├── integration/
│   ├── test_document_structurer.py
│   ├── test_loop_scenarios.py     # ⭐ NOVO
│   └── test_error_handling.py     # ⭐ NOVO
│
├── unit/
│   ├── test_metadata_extractor.py # ⭐ NOVO
│   └── test_index_manager.py      # ⭐ NOVO
│
└── fixtures/
    ├── edital_sample_metadata.yaml
    └── edital_with_errors.yaml    # ⭐ NOVO
```

---

## 📈 Métricas de Sucesso

### Funcionalidade (Sprint 4)

- [ ] **Metadados extraídos:** 7 campos principais do edital
- [ ] **Índice funcional:** Histórico de análises mantido
- [ ] **LOOP testado:** 3 cenários de correção validados
- [ ] **Error handling:** 4 cenários de erro tratados

### Qualidade (Sprint 4)

- [ ] **Testes unitários:** 2 novos módulos testados
- [ ] **Testes integração:** 2 suites adicionais
- [ ] **Cobertura:** 80%+ (inclui novos módulos)
- [ ] **Documentação:** 100% (README para extractors)

---

## 🚦 Roadmap do Sprint 4

### Fase 1: Extração de Metadados (História 2.4)
**Tempo estimado:** 2-3 horas

- [ ] Criar metadata_extractor.py
- [ ] Definir padrões de extração (regex/patterns)
- [ ] Integrar ao EXECUTE phase (step 0)
- [ ] Adicionar ao delivery package
- [ ] Criar testes unitários
- [ ] Atualizar documentação

### Fase 2: Índice de Análises (História 2.5)
**Tempo estimado:** 1-2 horas

- [ ] Criar index_manager.py
- [ ] Criar data/index_analises.csv
- [ ] Integrar ao DELIVER phase
- [ ] Criar comando /listar-analises
- [ ] Validar duplicatas
- [ ] Criar testes unitários

### Fase 3: Testes Avançados (História 2.6)
**Tempo estimado:** 2-3 horas

- [ ] Criar edital_with_errors.yaml
- [ ] Implementar test_loop_scenarios.py
- [ ] Implementar test_error_handling.py
- [ ] Validar todos os cenários
- [ ] Documentar em E2E_TEST_REPORT.md

---

## 📊 Valor Agregado do Sprint 4

**Antes (Sprint 3):**
- ✅ Extrai requisitos técnicos
- ✅ Gera CSV estruturado
- ✅ Valida com SHIELD
- ❌ Não extrai metadados do edital
- ❌ Não mantém histórico
- ❌ LOOP não testado na prática

**Depois (Sprint 4):**
- ✅ Extrai requisitos técnicos
- ✅ Gera CSV estruturado
- ✅ Valida com SHIELD
- ✅ **Extrai metadados do edital** ⭐
- ✅ **Mantém histórico de análises** ⭐
- ✅ **LOOP testado com cenários reais** ⭐

**ROI do Sprint 4:**
- Metadados facilitam organização e busca
- Histórico evita reprocessamento
- Testes avançados garantem robustez em produção

---

## 🎓 Aprendizados Esperados

Ao final do Sprint 4, teremos:

1. ✅ **Document Structurer 110% completo**
   - Extração completa (requisitos + metadados)
   - Rastreabilidade total (índice histórico)
   - Robustez validada (LOOP + error handling)

2. ✅ **Padrão de extração de metadados**
   - Replicável para outros agentes
   - Patterns para documentos brasileiros

3. ✅ **Sistema de índice centralizado**
   - Base para dashboard futuro
   - Permite analytics de uso

---

## 📚 Referências

- **Sprint 3 Plan:** `SPRINT_3_PLAN.md`
- **Agent Architecture:** `agents/document_structurer/architecture.md`
- **Agent Prompt:** `agents/document_structurer/prompt.md`
- **Integration Test Report:** `docs/INTEGRATION_TEST_REPORT.md`
- **Framework SHIELD:** `framework/phases/README.md`

---

**Criado em:** 06/11/2025
**Sprint:** 4
**Épico:** 2 - Agentes Especializados
**Status:** 🚀 Iniciando agora!
