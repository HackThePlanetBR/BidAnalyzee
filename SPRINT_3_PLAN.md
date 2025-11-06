# Sprint 3 - Primeiro Agente Completo: Document Structurer

**Início:** 06/11/2025
**Épico:** Épico 2 - Agentes Especializados
**Objetivo:** Implementar o primeiro agente completo usando Framework SHIELD

---

## 🎯 Objetivo do Sprint

Implementar o agente **Document Structurer** que extrai e estrutura requisitos de editais PDF, usando **TODAS as 7 fases do Framework SHIELD**.

---

## 📋 Histórias do Sprint 3

### História 2.1: Document Structurer - Capability Definition
**Objetivo:** Definir capacidades, arquitetura e especificações do agente

**Entregáveis:**
- `agents/document_structurer/README.md` - Documentação completa
- `agents/document_structurer/capabilities.yaml` - Especificação de capacidades
- `agents/document_structurer/architecture.md` - Diagrama de arquitetura

**Critérios de Aceite:**
- [ ] Capacidades claramente definidas (input, output, limitações)
- [ ] Arquitetura documentada (fluxo SHIELD completo)
- [ ] Especificações técnicas (PDF → CSV, campos obrigatórios)

---

### História 2.2: Document Structurer - Prompt Engineering
**Objetivo:** Criar prompt completo do agente usando componentes SHIELD

**Entregáveis:**
- `agents/document_structurer/prompt.md` - Prompt principal do agente
- `agents/document_structurer/examples/` - Exemplos de uso
- `.claude/commands/structure-edital.md` - Slash command

**Critérios de Aceite:**
- [ ] Prompt inclui TODAS as 7 fases SHIELD (via {{incluir:...}})
- [ ] Persona clara e consistente
- [ ] Instruções específicas para extração de requisitos
- [ ] Slash command funcional

---

### História 2.3: Document Structurer - Integration Testing
**Objetivo:** Testar workflow end-to-end com edital real

**Entregáveis:**
- `tests/integration/test_document_structurer.py` - Testes de integração
- `tests/fixtures/edital_sample.pdf` - Edital de exemplo
- `docs/INTEGRATION_TEST_REPORT.md` - Relatório de testes

**Critérios de Aceite:**
- [ ] Teste end-to-end passa (STRUCTURE → EXECUTE → INSPECT → VALIDATE → DELIVER)
- [ ] CSV gerado está correto (47 requisitos)
- [ ] Todas as evidências salvas (InspectionResult, ValidationResult, logs)
- [ ] Modo Strict validado (100% obrigatório)

---

## 🔄 Fluxo do Document Structurer com SHIELD

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT STRUCTURER AGENT                     │
└─────────────────────────────────────────────────────────────────┘

INPUT: edital.pdf (345 páginas)

↓

┌─────────────┐
│ STRUCTURE   │ Planejar extração (5 etapas, 3 HALTs)
└──────┬──────┘
       │
       ↓ [Plan YAML]
┌──────┴──────┐
│    HALT     │ Usuário aprova plano?
└──────┬──────┘
       │
       ↓ [Aprovado]
┌──────┴──────┐
│  EXECUTE    │ Etapa 1: Extract text from PDF
│             │   → 345 páginas processadas
│             │   → Texto extraído: 1.2MB
└──────┬──────┘
       │
       ↓ [text_extracted.txt]
┌──────┴──────┐
│  EXECUTE    │ Etapa 2: Identify requirements
│             │   → Pattern matching
│             │   → 47 requisitos identificados
└──────┬──────┘
       │
       ↓ [requirements_raw.json]
┌──────┴──────┐
│  EXECUTE    │ Etapa 3: Structure as CSV
│             │   → CSV com 6 campos
│             │   → 47 linhas
└──────┬──────┘
       │
       ↓ [requirements.csv]
┌──────┴──────┐
│   INSPECT   │ Checklist: Anti-Alucinação (8) + Estruturação (8)
│             │   → 16/16 items PASS
└──────┬──────┘
       │
  ┌────┴────┐
  │ PASSOU? │
  └────┬────┘
       │
       ↓ [SIM]
┌──────┴──────┐
│  VALIDATE   │ Métricas:
│             │   → Completeness: 47/47 = 100%
│             │   → Integrity: 282/282 = 100%
│             │   → Consistency: 100%
│             │   → Traceability: 100%
└──────┬──────┘
       │
       ↓ [ValidationResult YAML]
┌──────┴──────┐
│    HALT     │ Usuário aprova entrega?
└──────┬──────┘
       │
       ↓ [Aprovado]
┌──────┴──────┐
│   DELIVER   │ Pacote de entrega:
│             │   → outputs/requirements.csv
│             │   → evidences/ (INSPECT, VALIDATE, logs)
│             │   → metadata/ (plan, timeline)
│             │   → sources/ (edital.pdf)
│             │   → README.md (relatório)
└──────┬──────┘
       │
       ↓

OUTPUT: Delivery Package completo
```

---

## 📊 Capacidades do Document Structurer

### Input

- **Tipo:** PDF (edital público)
- **Tamanho:** Até 500 páginas
- **Formato:** Qualquer edital brasileiro padrão
- **Exemplo:** PMSP-Videomonitoramento-2025-001.pdf (345 páginas)

### Output Principal

**CSV Estruturado com 7 campos obrigatórios:**

```csv
ID,Item,Descrição,Categoria,Prioridade,Página,Confiança
1,"3.2.1","Sistema de câmeras com resolução 4K",Hardware,Alta,23,0.95
2,"3.2.2","Software de análise de vídeo com IA",Software,Alta,25,0.92
...
```

**Campos:**
1. **ID** (int): Sequencial interno 1 a N (para validação de completude)
2. **Item** (string): Número do item no edital original (e.g., "3.2.1", "5.4", "A.2")
3. **Descrição** (string): Texto completo do requisito
4. **Categoria** (enum): Hardware | Software | Serviço | Integração
5. **Prioridade** (enum): Alta | Média | Baixa
6. **Página** (int): Página de origem no PDF
7. **Confiança** (float): 0.0 a 1.0 (confiança da extração)

### Capacidades

✅ **O que o agente PODE fazer:**
- Extrair texto de PDF (via PyPDF2 ou similar)
- Identificar requisitos técnicos por padrões
- Categorizar requisitos automaticamente
- Gerar CSV estruturado
- Auto-inspecionar qualidade (16 items checklist)
- Validar completude quantitativamente (4 métricas)
- Gerar relatório executivo

❌ **O que o agente NÃO PODE fazer:**
- Processar PDFs com OCR (apenas texto extraível)
- Interpretar imagens/diagramas
- Entender contexto de negócio sem instruções
- Inventar requisitos não presentes no edital

### Limitações Conhecidas

- **Confiança mínima:** 85% (requisitos com < 85% vão para revisão)
- **Timeout:** 10 minutos por etapa
- **Memória:** Máximo 2GB de texto extraído
- **LOOP:** Máximo 3 tentativas de correção

---

## 🛠️ Stack Técnico

### Dependências

```python
# PDF Processing
PyPDF2==3.0.1          # Extração de texto
pdfplumber==0.10.3     # Alternativa para PDFs complexos

# Data Processing
pandas==2.1.3          # Manipulação de CSV
pyyaml==6.0.1          # YAML para templates

# Validation
jsonschema==4.20.0     # Validação de schemas

# Logging
structlog==23.2.0      # Logs estruturados
```

### Estrutura de Arquivos

```
agents/document_structurer/
├── README.md                       # Documentação completa
├── capabilities.yaml               # Especificação de capacidades
├── architecture.md                 # Diagrama de arquitetura
├── prompt.md                       # Prompt principal do agente
│
├── checklists/                     # Checklists específicos
│   └── inspect.yaml                # ✅ JÁ EXISTE (criado no Sprint 0)
│
├── examples/                       # Exemplos de uso
│   ├── example_1_simple.md        # Edital simples (20 páginas)
│   ├── example_2_medium.md        # Edital médio (100 páginas)
│   └── example_3_complex.md       # Edital complexo (345 páginas)
│
└── tests/                          # Testes unitários
    ├── test_extract.py             # Testa extração de texto
    ├── test_identify.py            # Testa identificação de requisitos
    └── test_structure.py           # Testa estruturação CSV
```

---

## 📈 Métricas de Sucesso

### Qualidade (Sprint 3)

- [ ] **Completeness:** 100% dos requisitos extraídos
- [ ] **Integrity:** 100% dos campos obrigatórios preenchidos
- [ ] **Consistency:** IDs sequenciais sem gaps
- [ ] **Traceability:** 100% dos requisitos têm página de origem
- [ ] **Modo Strict:** Todas as validações passam

### Performance (Sprint 3)

- [ ] **Tempo de extração:** < 2 minutos para 345 páginas
- [ ] **Tempo total (SHIELD):** < 10 minutos end-to-end
- [ ] **Memória:** < 2GB de RAM

### Qualidade do Código (Sprint 3)

- [ ] **Documentação:** 100% (README + arquitetura + exemplos)
- [ ] **Testes:** 80%+ de cobertura (unitários + integração)
- [ ] **Logs:** Completos e estruturados

---

## 🚦 Roadmap do Sprint 3

### Fase 1: Capability Definition (História 2.1)
**Tempo estimado:** 2-3 horas

- [ ] Criar README.md completo
- [ ] Definir capabilities.yaml
- [ ] Documentar arquitetura
- [ ] Definir estrutura de CSV (campos)
- [ ] Especificar limitações

### Fase 2: Prompt Engineering (História 2.2)
**Tempo estimado:** 3-4 horas

- [ ] Criar prompt.md usando componentes SHIELD
- [ ] Incluir {{incluir:...}} para todas as 7 fases
- [ ] Definir persona do agente
- [ ] Criar instruções específicas de extração
- [ ] Criar slash command `/structure-edital`
- [ ] Documentar exemplos de uso

### Fase 3: Integration Testing (História 2.3)
**Tempo estimado:** 2-3 horas

- [ ] Criar edital de exemplo (fixture)
- [ ] Implementar teste end-to-end
- [ ] Validar geração de CSV
- [ ] Validar evidências (InspectionResult, ValidationResult)
- [ ] Validar delivery package
- [ ] Gerar relatório de testes

---

## 🎓 Aprendizados Esperados

Ao final do Sprint 3, teremos:

1. ✅ **Validado o Framework SHIELD na prática**
   - Todas as 7 fases funcionando
   - Integração entre fases testada
   - Modo Strict validado

2. ✅ **Primeiro agente completo funcionando**
   - Extrai requisitos de editais
   - Produz CSV estruturado
   - Gera evidências completas

3. ✅ **Padrão para próximos agentes**
   - Estrutura de arquivos
   - Padrão de prompts
   - Processo de testes

---

## 📚 Referências

- **Framework SHIELD:** `framework/phases/README.md`
- **PRD:** Épico 2, Histórias 2.1-2.3
- **Checklist do agente:** `agents/document_structurer/checklists/inspect.yaml`
- **Template de Plan:** `framework/templates/plan_template.yaml`

---

**Criado em:** 06/11/2025
**Sprint:** 3
**Épico:** 2 - Agentes Especializados
**Status:** 🚀 Iniciando agora!
