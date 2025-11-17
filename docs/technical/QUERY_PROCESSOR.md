# Query Processor - Technical Analyst Agent

**Status:** ✅ COMPLETO (Sprint 5.2)
**Versão:** 1.0.0
**Data:** 08 de novembro de 2025

---

## 📋 Visão Geral

O **Query Processor** é o componente do Technical Analyst responsável por analisar requisitos técnicos contra a base de conhecimento usando o RAG Engine.

### Funcionalidades Principais

- ✅ Análise de conformidade de requisitos
- ✅ Geração de veredicto estruturado (CONFORME/NÃO_CONFORME/REVISÃO)
- ✅ Extração de evidências da base de conhecimento
- ✅ Cálculo de score de confiança
- ✅ Geração automática de recomendações
- ✅ Processamento em batch
- ✅ Rastreamento de estatísticas

---

## 🏗️ Arquitetura

```
┌──────────────────────────────┐
│     Query Processor          │
│                              │
│  analyze_requirement()       │
│         │                    │
│         ▼                    │
│  ┌──────────────────┐        │
│  │   RAG Engine     │        │
│  │   (search)       │        │
│  └──────────────────┘        │
│         │                    │
│         ▼                    │
│  ┌──────────────────┐        │
│  │  Conformity      │        │
│  │  Analysis        │        │
│  └──────────────────┘        │
│         │                    │
│         ▼                    │
│  ┌──────────────────┐        │
│  │  Evidence +      │        │
│  │  Recommendations │        │
│  └──────────────────┘        │
└──────────────────────────────┘
```

---

## 🚀 Uso Básico

### Análise Individual

```python
from agents.technical_analyst import QueryProcessor, RAGEngine

# Inicializar components
rag_engine = RAGEngine.from_config()
rag_engine.ingest_knowledge_base("data/knowledge_base/mock")

processor = QueryProcessor(rag_engine)

# Analisar requisito
requirement = {
    'id': 'REQ-001',
    'descricao': 'Câmeras IP com resolução mínima 4MP',
    'tipo': 'Técnico',
    'categoria': 'Hardware'
}

result = processor.analyze_requirement(requirement)

print(f"Veredicto: {result.conformity.value}")
print(f"Confiança: {result.confidence:.0%}")
print(f"Evidências: {len(result.evidence)}")
print(f"Fontes: {', '.join(result.sources)}")
```

### Análise em Batch

```python
requirements = [
    {'id': 'REQ-001', 'descricao': 'Câmeras IP 4MP'},
    {'id': 'REQ-002', 'descricao': 'Armazenamento 30 dias'},
    {'id': 'REQ-003', 'descricao': 'Atestado de capacidade técnica'}
]

results = processor.analyze_batch(requirements)

# Ver estatísticas
stats = processor.get_stats()
print(f"Total analisados: {stats['total_analyzed']}")
print(f"Conformes: {stats['percentages']['conforme']:.1f}%")
```

---

## 📊 Estrutura de Resultados

### ConformityAnalysis

```python
{
    "requirement_id": "REQ-001",
    "conformity": "CONFORME",  # ou NAO_CONFORME, REVISAO
    "confidence": 0.89,
    "evidence": [
        {
            "source": "requisitos_tecnicos.md",
            "text": "Câmeras IP devem ter resolução mínima de 4MP...",
            "relevance": 0.92,
            "chunk_index": 0
        }
    ],
    "reasoning": "O requisito está em conformidade com a base...",
    "recommendations": [
        "✅ Requisito validado automaticamente",
        "📋 Incluir evidências no relatório"
    ],
    "sources": ["requisitos_tecnicos.md"],
    "metadata": {
        "requirement": {...},
        "search_results_count": 3,
        "top_k": 5
    }
}
```

---

## ⚙️ Configuração

### Thresholds Padrão

```python
config = {
    'high_confidence': 0.85,  # CONFORME se >= 0.85
    'low_confidence': 0.60,   # REVISAO se < 0.60
    'min_evidence': 2         # Mínimo de fontes requeridas
}

processor = QueryProcessor(rag_engine, config=config)
```

### Lógica de Decisão

```
Confidence >= 0.85 + Evidence >= 2 → CONFORME
Confidence < 0.60 → REVISAO
0.60 <= Confidence < 0.85 → REVISAO (ambíguo)
```

---

## 🧪 Testes

### Cobertura

- ✅ **28 testes unitários** - Lógica isolada
- ✅ **14 testes de integração** - End-to-end com RAG
- ✅ **42 testes total** - 100% passando

### Executar Testes

```bash
# Testes unitários
pytest tests/unit/test_query_processor.py -v

# Testes de integração
pytest tests/integration/test_query_processor_integration.py -v

# Todos os testes
pytest tests/unit/test_query_processor.py \
       tests/integration/test_query_processor_integration.py -v
```

---

## 📈 Performance

| Métrica | Valor |
|---------|-------|
| Análise individual | < 1s |
| Batch (10 requisitos) | < 5s |
| Memória | < 100MB |
| Testes (42) | < 1s total |

---

## 💾 Exportação de Resultados

### JSON

```python
result = processor.analyze_requirement(requirement)

# Exportar para JSON
json_str = result.to_json()

# Salvar em arquivo
result.save("analysis_results/REQ-001.json")
```

### Dict

```python
result_dict = result.to_dict()
# {'requirement_id': 'REQ-001', 'conformity': 'CONFORME', ...}
```

---

## 📚 Componentes Relacionados

- **RAG Engine:** Busca semântica na base de conhecimento
- **Vector Store:** FAISS para armazenamento de embeddings
- **Embeddings Manager:** Geração de embeddings
- **Ingestion Pipeline:** Ingestão de documentos

---

## 🔄 Fluxo de Análise

```
1. Recebe requisito do Document Structurer
2. Constrói query otimizada
3. Busca no RAG Engine (top_k resultados)
4. Extrai evidências dos resultados
5. Calcula confiança (avg + max relevance)
6. Determina veredicto (CONFORME/REVISAO/NAO_CONFORME)
7. Gera reasoning explicativo
8. Gera recomendações acionáveis
9. Retorna ConformityAnalysis estruturado
```

---

## 📖 Exemplos de Uso

### Exemplo 1: Requisito Técnico

```python
req = {
    'id': 'REQ-001',
    'descricao': 'Câmeras IP com resolução 4MP e compressão H.265',
    'tipo': 'Técnico',
    'categoria': 'Hardware'
}

result = processor.analyze_requirement(req)
# Verdict: CONFORME
# Confidence: 92%
# Evidence: 3 sources
```

### Exemplo 2: Requisito Documental

```python
req = {
    'id': 'REQ-005',
    'descricao': 'Atestado de capacidade técnica com 2 clientes',
    'tipo': 'Documental',
    'categoria': 'Qualificação'
}

result = processor.analyze_requirement(req)
# Verdict: CONFORME
# Confidence: 88%
# Sources: documentacao_qualificacao.md
```

### Exemplo 3: Requisito Não Encontrado

```python
req = {
    'id': 'REQ-999',
    'descricao': 'Sistema de detecção de alienígenas',
    'tipo': 'Técnico'
}

result = processor.analyze_requirement(req)
# Verdict: REVISAO
# Confidence: 15%
# Recommendations: ["Revisar manualmente", "Base incompleta"]
```

---

## 📊 Estatísticas

```python
# Após análise de múltiplos requisitos
stats = processor.get_stats()

{
    'total_analyzed': 50,
    'verdicts': {
        'conforme': 35,
        'nao_conforme': 2,
        'revisao': 13
    },
    'percentages': {
        'conforme': 70.0,
        'nao_conforme': 4.0,
        'revisao': 26.0
    },
    'config': {
        'high_confidence_threshold': 0.85,
        'low_confidence_threshold': 0.60,
        'min_evidence_count': 2
    }
}
```

---

## ✅ Sprint 5.2 - Definition of Done

- [x] QueryProcessor implementado (~470 linhas)
- [x] Testes unitários (28 testes)
- [x] Testes de integração (14 testes)
- [x] Documentação completa
- [x] Integração com RAG Engine
- [x] Batch processing
- [x] Statistics tracking
- [x] JSON export
- [x] 100% testes passando

---

## 🎯 Próximos Passos

Sprint 5.3 (Planejada):
1. **Integração com Document Structurer**
   - Pipeline end-to-end: PDF → Estruturação → Análise
   - Comando `/analyze-edital` completo

2. **Relatório de Conformidade**
   - Geração de relatório consolidado
   - Export para CSV, Excel, PDF
   - Dashboard de resultados

---

**Última atualização:** 08 de novembro de 2025
**Autor:** Sistema BidAnalyzee
**Status:** ✅ Production Ready
