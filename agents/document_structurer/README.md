# Document Structurer Agent

**Versão:** 1.0
**Tipo:** Agente Especializado
**Framework:** SHIELD v1.0

---

## 🎯 Propósito

O **Document Structurer** é um agente especializado em extrair e estruturar requisitos técnicos de editais públicos brasileiros em formato PDF, produzindo um CSV padronizado pronto para análise.

---

## 📊 Capacidades

### Input Aceito

- **Formato:** PDF (Portable Document Format)
- **Tipo:** Editais públicos brasileiros
- **Tamanho:** Até 500 páginas
- **Requisitos:** Texto extraível (não requer OCR)
- **Exemplo:** PMSP-Videomonitoramento-2025-001.pdf (345 páginas)

### Output Produzido

**CSV Estruturado** com 7 campos obrigatórios:

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| **ID** | int | Identificador sequencial interno (1, 2, 3...) | 1, 2, 3, ..., 47 |
| **Item** | string | Número do item no edital original | "3.2.1", "5.4", "A.2" |
| **Descrição** | string | Texto completo do requisito | "Sistema de câmeras com resolução 4K" |
| **Categoria** | enum | Tipo do requisito | Hardware, Software, Serviço, Integração |
| **Prioridade** | enum | Nível de prioridade | Alta, Média, Baixa |
| **Página** | int | Página de origem no PDF | 23 |
| **Confiança** | float | Confiança da extração (0.0-1.0) | 0.95 |

**Exemplo de Output:**

```csv
ID,Item,Descrição,Categoria,Prioridade,Página,Confiança
1,"3.2.1","Sistema de câmeras IP com resolução 4K (3840x2160)",Hardware,Alta,23,0.95
2,"3.2.2","Software de análise de vídeo com algoritmos de IA",Software,Alta,25,0.92
3,"5.4","Integração com sistema de controle de acesso existente",Integração,Média,45,0.88
4,"A.2","Treinamento de operadores para uso do sistema",Serviço,Média,289,0.91
```

**Campos Explicados:**
- **ID:** Número sequencial usado pelos agentes para validar completude (verifica se IDs 1-N existem sem gaps)
- **Item:** Preserva a numeração original do edital para referência (pode ser "3.2.1", "5.4", etc.)

---

## ✅ O Que Este Agente FAZ

1. **Extrai texto de PDF**
   - Processa PDFs página por página
   - Suporta PDFs com texto extraível
   - Preserva estrutura de parágrafos

2. **Identifica requisitos técnicos**
   - Usa padrões linguísticos brasileiros
   - Detecta verbos modais ("deve", "deverá", "é obrigatório")
   - Identifica seções técnicas do edital

3. **Categoriza automaticamente**
   - Hardware: Equipamentos físicos, câmeras, servidores
   - Software: Aplicações, licenças, sistemas
   - Serviço: Treinamento, manutenção, suporte
   - Integração: APIs, protocolos, interfaces

4. **Atribui prioridade**
   - Alta: Requisitos obrigatórios, bloqueantes
   - Média: Requisitos importantes, não bloqueantes
   - Baixa: Requisitos desejáveis, nice-to-have

5. **Calcula confiança**
   - 0.90-1.00: Alta confiança (requisito explícito)
   - 0.85-0.89: Média confiança (requisito implícito)
   - < 0.85: Baixa confiança (marcado para revisão manual)

6. **Auto-inspeciona qualidade**
   - Aplica 16 items de checklist (8 fixos + 8 dinâmicos)
   - Modo Strict: 100% dos items devem passar

7. **Valida completude**
   - Verifica 4 métricas quantitativas (todas = 100%)
   - Garante rastreabilidade (cada requisito → página do PDF)

8. **Gera evidências completas**
   - InspectionResult YAML
   - ValidationResult YAML
   - Execution logs
   - Delivery package com README.md

---

## ❌ O Que Este Agente NÃO FAZ

1. **❌ Processar PDFs sem texto extraível**
   - Não faz OCR (Optical Character Recognition)
   - PDFs escaneados não são suportados

2. **❌ Interpretar imagens ou diagramas**
   - Ignora gráficos, tabelas complexas, fotos
   - Foca apenas em texto

3. **❌ Entender contexto de negócio sem instruções**
   - Não infere requisitos implícitos
   - Não "adivinha" intenções do edital

4. **❌ Inventar ou assumir requisitos**
   - Princípio Anti-Alucinação obrigatório
   - Tudo deve estar explícito no PDF

5. **❌ Processar formatos diferentes de PDF**
   - Não aceita Word, Excel, HTML, etc.
   - Conversão deve ser feita antes

---

## 🔄 Fluxo SHIELD Completo

Este agente implementa **TODAS as 7 fases** do Framework SHIELD:

```
STRUCTURE → HALT → EXECUTE → INSPECT → LOOP → VALIDATE → HALT → DELIVER
```

### Detalhamento por Fase

#### 1. STRUCTURE (Planejar)
- **Input:** Edital PDF + objetivo do usuário
- **Output:** Plan YAML com 5 etapas
- **Tempo:** ~1 minuto
- **Checkpoints:** 3 HALTs planejados

#### 2. HALT (Aprovar Plano)
- **Input:** Plan YAML
- **Output:** Aprovação do usuário
- **Tempo:** Aguarda input do usuário

#### 3. EXECUTE (Executar Etapas)
- **Etapa 1:** Extract text from PDF (2 min)
- **Etapa 2:** Identify requirements (3 min)
- **Etapa 3:** Structure as CSV (1 min)
- **Output:** requirements.csv
- **Tempo total:** ~6 minutos

#### 4. INSPECT (Auto-Inspeção)
- **Input:** requirements.csv
- **Checklists:** Anti-Alucinação (8) + Estruturação (8)
- **Output:** InspectionResult YAML
- **Tempo:** ~30 segundos

#### 5. LOOP (Correção - se necessário)
- **Trigger:** INSPECT falhou
- **Ações:** Correções cirúrgicas (remove duplicatas, renumera, etc.)
- **Limite:** 3 iterações
- **Tempo:** ~1-3 minutos

#### 6. VALIDATE (Validação Quantitativa)
- **Input:** requirements.csv
- **Métricas:** Completeness, Integrity, Consistency, Traceability
- **Output:** ValidationResult YAML
- **Tempo:** ~30 segundos

#### 7. HALT (Aprovar Entrega)
- **Input:** Delivery package preview
- **Output:** Aprovação final do usuário
- **Tempo:** Aguarda input do usuário

#### 8. DELIVER (Entregar)
- **Output:** Pacote completo (outputs/ + evidences/ + metadata/ + README.md)
- **Tempo:** ~30 segundos

**Tempo Total:** ~10 minutos end-to-end (sem contar HALTs)

---

## 🎓 Exemplo de Uso

### Comando

```bash
/structure-edital data/uploads/PMSP-2025-001.pdf
```

### Execução

```
[STRUCTURE] Planning extraction from PMSP-2025-001.pdf (345 pages)...
[STRUCTURE] Plan created: 5 steps, 3 HALTs, estimated 15-20 min

[HALT] 🛑 Approve plan? [A/B/C]
User: A

[EXECUTE] Step 1/5: Extract text from PDF...
[EXECUTE] ✓ Extracted 1.2MB of text (345 pages)

[EXECUTE] Step 2/5: Identify requirements...
[EXECUTE] ✓ Found 47 requirements

[EXECUTE] Step 3/5: Structure as CSV...
[EXECUTE] ✓ Generated requirements.csv (47 rows)

[INSPECT] Running checklists...
[INSPECT] ✓ Anti-Alucinação: 8/8 passed
[INSPECT] ✓ Estruturação: 8/8 passed

[VALIDATE] Validating metrics...
[VALIDATE] ✓ Completeness: 100%
[VALIDATE] ✓ Integrity: 100%
[VALIDATE] ✓ Consistency: 100%
[VALIDATE] ✓ Traceability: 100%

[HALT] 🛑 Approve delivery? [A/B/C]
User: A

[DELIVER] Packaging delivery...
[DELIVER] ✓ Saved to: data/deliveries/analysis_pmsp_2025_001/

✅ Workflow completed successfully!
```

### Output Gerado

```
data/deliveries/analysis_pmsp_2025_001/
├── outputs/
│   └── requirements_structured.csv     (47 requisitos)
│
├── evidences/
│   ├── inspection_results/
│   │   └── inspection_001.yaml         (16/16 items passed)
│   ├── validation_results/
│   │   └── validation_001.yaml         (4 metrics = 100%)
│   └── execution_logs/
│       └── document_structurer_log.txt (logs completos)
│
├── metadata/
│   ├── plan.yaml                       (plano original)
│   └── timeline.yaml                   (timestamps de cada fase)
│
├── sources/
│   └── PMSP-2025-001.pdf               (edital original)
│
└── README.md                           (relatório executivo)
```

---

## 📊 Métricas de Performance

### Tempo de Execução

| Fase | Tempo Médio | Máximo |
|------|-------------|---------|
| STRUCTURE | 1 min | 2 min |
| EXECUTE (Extract) | 2 min | 5 min |
| EXECUTE (Identify) | 3 min | 8 min |
| EXECUTE (Structure) | 1 min | 2 min |
| INSPECT | 30 seg | 1 min |
| LOOP (se necessário) | 1-3 min | 5 min |
| VALIDATE | 30 seg | 1 min |
| DELIVER | 30 seg | 1 min |
| **Total** | **~10 min** | **~25 min** |

### Qualidade

| Métrica | Target | Modo Strict |
|---------|--------|-------------|
| Completeness | 100% | Obrigatório |
| Integrity | 100% | Obrigatório |
| Consistency | 100% | Obrigatório |
| Traceability | 100% | Obrigatório |

### Acurácia

| Aspecto | Taxa |
|---------|------|
| Requisitos identificados | >95% |
| Categorização correta | >90% |
| Priorização correta | >85% |
| Confiança média | >0.90 |

---

## 🛠️ Configuração

### Variáveis de Ambiente

```bash
# .env
MAX_LOOP_ITERATIONS=3
CONFIDENCE_THRESHOLD=0.85
PDF_TIMEOUT_SECONDS=600
MAX_PDF_PAGES=500
```

### Dependências

```bash
pip install PyPDF2==3.0.1
pip install pandas==2.1.3
pip install pyyaml==6.0.1
pip install structlog==23.2.0
```

---

## 🧪 Testes

### Testes Unitários

```bash
pytest agents/document_structurer/tests/
```

### Teste de Integração

```bash
pytest tests/integration/test_document_structurer.py
```

### Teste Manual

```bash
/structure-edital tests/fixtures/edital_sample.pdf
```

---

## 📚 Referências

- **Framework SHIELD:** [framework/phases/README.md](../../framework/phases/README.md)
- **Checklist do Agente:** [checklists/inspect.yaml](checklists/inspect.yaml)
- **Prompt Completo:** [prompt.md](prompt.md)
- **Arquitetura:** [architecture.md](architecture.md)
- **PRD:** Épico 2, História 2.1

---

## 🔄 Versão e Histórico

- **v1.0** (06/11/2025) - Implementação inicial com SHIELD v1.0

---

**Mantido por:** Equipe BidAnalyzee
**Framework:** SHIELD v1.0 (Modo Strict)
**Status:** ✅ Em desenvolvimento (Sprint 3)
