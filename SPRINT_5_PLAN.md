# Sprint 5 Plan - Technical Analyst Agent (RAG Setup)

**Data de Início:** 07 de novembro de 2025
**Duração Estimada:** 1.5 semanas (6-8 horas)
**Objetivo:** Implementar sistema RAG local com arquitetura migration-ready para cloud

---

## 🎯 Objetivo do Sprint

Implementar a **História 5.1 - RAG Setup** do Technical Analyst Agent usando:
- ✅ **FAISS** (vector store local)
- ✅ **sentence-transformers** (embeddings locais, sem custo)
- ✅ **6 documentos mock** de alta qualidade
- ✅ **Arquitetura modular** preparada para migração futura (Pinecone + OpenAI)

### Por que Local primeiro?

1. **Zero bloqueios** - não depende de configuração de infraestrutura externa
2. **Zero custos** - tudo open-source
3. **Validação rápida** - testar conceito antes de investir em infra
4. **Migration-ready** - arquitetura correta desde o início
5. **Migração trivial** - trocar variáveis de ambiente quando pronto

---

## 📋 História 5.1: RAG Setup (Local + Cloud Ready)

### Descrição
Implementar sistema de Retrieval-Augmented Generation (RAG) para o Technical Analyst Agent, permitindo busca semântica em base de conhecimento sobre licitações e requisitos técnicos.

### Critérios de Aceitação
- [ ] Vector store FAISS configurado e funcional
- [ ] Pipeline de ingestão carrega documentos e gera embeddings
- [ ] Sistema de busca semântica retorna resultados relevantes
- [ ] 6 documentos mock criados com conteúdo de qualidade
- [ ] Arquitetura modular com interfaces abstratas
- [ ] Configuração via `.env` para fácil migração
- [ ] Testes unitários cobrindo funcionalidades principais
- [ ] Documentação clara de uso e migração

### Estimativa: 6-8 horas

---

## 🏗️ Arquitetura - Local vs Cloud

### Fase 1: Implementação Local (AGORA)

```
┌─────────────────────────────────────────────┐
│         Technical Analyst Agent             │
│                                             │
│  ┌────────────┐        ┌─────────────────┐ │
│  │   Query    │───────▶│  Vector Store   │ │
│  │ Processor  │        │    (FAISS)      │ │
│  └────────────┘        └─────────────────┘ │
│         │                       ▲           │
│         │                       │           │
│         ▼                       │           │
│  ┌────────────┐        ┌─────────────────┐ │
│  │ Conformity │        │   Embeddings    │ │
│  │  Analyzer  │        │ (sentence-trans)│ │
│  └────────────┘        └─────────────────┘ │
│                                ▲            │
└────────────────────────────────┼────────────┘
                                 │
                        ┌────────┴────────┐
                        │  Knowledge Base │
                        │   (6 Mock MDs)  │
                        └─────────────────┘
```

### Fase 2: Migração Cloud (FUTURO)

```
┌─────────────────────────────────────────────┐
│         Technical Analyst Agent             │
│                                             │
│  ┌────────────┐        ┌─────────────────┐ │
│  │   Query    │───────▶│  Vector Store   │ │
│  │ Processor  │        │   (Pinecone)    │ │
│  └────────────┘        └─────────────────┘ │
│         │                       ▲           │
│         │                       │           │
│         ▼                       │           │
│  ┌────────────┐        ┌─────────────────┐ │
│  │ Conformity │        │   Embeddings    │ │
│  │  Analyzer  │        │ (OpenAI API)    │ │
│  └────────────┘        └─────────────────┘ │
│                                ▲            │
└────────────────────────────────┼────────────┘
                                 │
                        ┌────────┴────────┐
                        │  n8n Pipeline   │
                        │ (Genetec Docs)  │
                        └─────────────────┘
```

**Migração:** Trocar 3 variáveis no `.env` + importar docs reais

---

## 📁 Estrutura de Diretórios

```
BidAnalyzee/
├── agents/
│   └── technical_analyst/
│       ├── __init__.py
│       ├── rag_engine.py           # NEW - RAG orchestration
│       ├── vector_store.py         # NEW - FAISS/Pinecone abstraction
│       ├── embeddings_manager.py   # NEW - Local/OpenAI embeddings
│       ├── ingestion_pipeline.py   # NEW - Document ingestion
│       ├── query_processor.py      # NEW - Query handling
│       ├── checklists/
│       │   └── rag_validation.yml  # NEW - RAG validation checklist
│       └── workflows/
│           └── rag_search.yml      # NEW - RAG search workflow
├── data/
│   ├── knowledge_base/
│   │   ├── mock/                   # NEW - Mock documents (now)
│   │   │   ├── lei_8666_1993.md
│   │   │   ├── lei_14133_2021.md
│   │   │   ├── requisitos_tecnicos_comuns.md
│   │   │   ├── documentacao_qualificacao.md
│   │   │   ├── prazos_cronogramas.md
│   │   │   └── criterios_pontuacao.md
│   │   └── real/                   # Future - Real docs from Genetec
│   └── vector_store/
│       └── faiss/                  # NEW - FAISS index storage
│           ├── index.faiss
│           └── metadata.json
├── tests/
│   ├── unit/
│   │   ├── test_vector_store.py    # NEW
│   │   ├── test_embeddings.py      # NEW
│   │   └── test_ingestion.py       # NEW
│   └── integration/
│       └── test_rag_search.py      # NEW
├── docs/
│   └── RAG_SETUP.md                # NEW - RAG documentation
├── SPRINT_5_PLAN.md                # THIS FILE
├── requirements.txt                # UPDATED - Add RAG dependencies
└── .env.example                    # UPDATED - Add RAG config
```

---

## 🔧 Stack Tecnológico

### Dependências Python

```python
# RAG Framework
langchain>=0.1.0              # RAG orchestration
langchain-community>=0.0.20   # Community integrations
langchain-openai>=0.0.5       # OpenAI integrations (future)

# Vector Store
faiss-cpu>=1.7.4              # Local vector store

# Embeddings
sentence-transformers>=2.2.2  # Local embeddings (free)
# openai>=1.10.0              # OpenAI embeddings (future)

# Utilities
tiktoken>=0.5.2               # Token counting
```

### Modelos de Embeddings

**Agora (Local):**
- `all-MiniLM-L6-v2` (384 dim, 80MB, rápido)
- Multilingual support
- Sem custo

**Futuro (Cloud):**
- `text-embedding-3-small` (OpenAI)
- Melhor qualidade
- $0.02/1M tokens

---

## 📝 Documentos Mock da Knowledge Base

### 1. `lei_8666_1993.md` (Lei de Licitações Antiga)
**Conteúdo:**
- Princípios fundamentais (legalidade, impessoalidade, moralidade)
- Modalidades de licitação (concorrência, tomada de preços, convite)
- Tipos de licitação (menor preço, melhor técnica, técnica e preço)
- Habilitação jurídica, técnica, econômico-financeira
- Recursos e prazos
- Sanções administrativas

### 2. `lei_14133_2021.md` (Nova Lei de Licitações)
**Conteúdo:**
- Mudanças em relação à Lei 8.666
- Novos procedimentos (diálogo competitivo)
- Critérios de sustentabilidade
- Contratação integrada
- Prazos atualizados
- Fase recursal simplificada

### 3. `requisitos_tecnicos_comuns.md`
**Conteúdo:**
- Requisitos de hardware típicos (servidores, câmeras, leitores)
- Requisitos de software (compatibilidade, licenciamento)
- Requisitos de rede (bandwidth, latência, protocolos)
- Requisitos de segurança (certificações, criptografia)
- Requisitos de integração (APIs, protocolos)
- Exemplos de especificações técnicas válidas

### 4. `documentacao_qualificacao.md`
**Conteúdo:**
- Documentos obrigatórios (certidões, registros)
- Qualificação técnica (atestados, certificações)
- Qualificação econômico-financeira (balanços, índices)
- Regularidade fiscal (federal, estadual, municipal)
- Regularidade trabalhista (CNDT)
- Exemplos de documentação completa

### 5. `prazos_cronogramas.md`
**Conteúdo:**
- Prazos legais (publicação, impugnação, recursos)
- Prazos de execução típicos
- Cronogramas físico-financeiros
- Marcos importantes (kick-off, entregas parciais, aceite final)
- Penalidades por atraso
- Extensões e prorrogações

### 6. `criterios_pontuacao.md`
**Conteúdo:**
- Critérios de pontuação técnica
- Pesos e ponderações
- Proposta de preço
- Metodologia de avaliação
- Desempate (preferências, sorteio)
- Exemplos de planilhas de pontuação

**Total estimado:** ~15,000 palavras (~50 páginas)

---

## 🔌 Configuração (.env)

### Configuração Local (Agora)

```bash
# ============================================
# RAG Configuration - Sprint 5
# ============================================

# Vector Store
RAG_VECTOR_STORE=faiss                    # faiss | pinecone
RAG_FAISS_INDEX_PATH=data/vector_store/faiss

# Embeddings
RAG_EMBEDDINGS_PROVIDER=local             # local | openai
RAG_EMBEDDINGS_MODEL=all-MiniLM-L6-v2     # sentence-transformers model
RAG_EMBEDDINGS_DIMENSION=384              # Model dimension

# Knowledge Base
RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/mock
RAG_CHUNK_SIZE=1000                       # Characters per chunk
RAG_CHUNK_OVERLAP=200                     # Overlap between chunks

# Search
RAG_TOP_K=5                               # Number of results to return
RAG_SIMILARITY_THRESHOLD=0.7              # Minimum similarity score

# ============================================
# Future Cloud Configuration (Commented)
# ============================================

# Pinecone (Future)
# PINECONE_API_KEY=pk-...
# PINECONE_ENVIRONMENT=us-west1-gcp
# PINECONE_INDEX_NAME=bidanalyzee-mvp
# PINECONE_DIMENSION=1536

# OpenAI Embeddings (Future)
# OPENAI_API_KEY=sk-...
# OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
# OPENAI_EMBEDDINGS_DIMENSION=1536

# n8n Pipeline (Future)
# N8N_BASE_URL=https://n8n.yourcompany.com
# N8N_API_KEY=...
# N8N_WEBHOOK_URL=...

# Genetec Portal (Future)
# GENETEC_DOCS_URL=https://techdocs.genetec.com
# GENETEC_AUTH_REQUIRED=false
```

---

## 💻 Implementação - Componentes Principais

### 1. Vector Store Interface (`vector_store.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorStoreInterface(ABC):
    """Abstract interface for vector stores"""

    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store"""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """Clear the vector store"""
        pass


class FAISSVectorStore(VectorStoreInterface):
    """FAISS implementation - Local, fast, free"""
    # Implementation...


class PineconeVectorStore(VectorStoreInterface):
    """Pinecone implementation - Cloud, scalable (future)"""
    # Implementation...
```

### 2. Embeddings Manager (`embeddings_manager.py`)

```python
class EmbeddingsManager:
    """Manages embeddings generation with multiple providers"""

    def __init__(self, provider: str = "local", model: str = None):
        self.provider = provider
        self.model = model
        self._initialize_embeddings()

    def _initialize_embeddings(self):
        if self.provider == "local":
            # Use sentence-transformers
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(self.model)
        elif self.provider == "openai":
            # Use OpenAI (future)
            from langchain_openai import OpenAIEmbeddings
            self.embedder = OpenAIEmbeddings(model=self.model)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        # Implementation...

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        # Implementation...
```

### 3. Ingestion Pipeline (`ingestion_pipeline.py`)

```python
class IngestionPipeline:
    """Pipeline for ingesting documents into vector store"""

    def __init__(self, vector_store, embeddings_manager):
        self.vector_store = vector_store
        self.embeddings = embeddings_manager
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def ingest_from_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Ingest all markdown files from a directory
        Returns: Statistics about ingestion
        """
        # 1. Load markdown files
        # 2. Split into chunks
        # 3. Generate embeddings
        # 4. Store in vector store
        # 5. Return stats
        pass

    def ingest_from_n8n(self, webhook_data: Dict) -> Dict[str, Any]:
        """Future: Ingest from n8n webhook"""
        pass
```

### 4. RAG Engine (`rag_engine.py`)

```python
class RAGEngine:
    """Main RAG orchestration engine"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._initialize_components()

    def _initialize_components(self):
        # Initialize based on config
        if self.config["vector_store"] == "faiss":
            self.vector_store = FAISSVectorStore(...)
        elif self.config["vector_store"] == "pinecone":
            self.vector_store = PineconeVectorStore(...)

        self.embeddings = EmbeddingsManager(
            provider=self.config["embeddings_provider"],
            model=self.config["embeddings_model"]
        )

        self.ingestion = IngestionPipeline(
            self.vector_store,
            self.embeddings
        )

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform RAG search
        Returns: List of relevant documents with scores
        """
        # 1. Generate query embedding
        # 2. Search vector store
        # 3. Return formatted results
        pass

    def ingest_knowledge_base(self, path: str) -> Dict[str, Any]:
        """Ingest entire knowledge base"""
        return self.ingestion.ingest_from_directory(path)
```

### 5. Query Processor (`query_processor.py`)

```python
class QueryProcessor:
    """Processes queries for the Technical Analyst"""

    def __init__(self, rag_engine: RAGEngine):
        self.rag = rag_engine

    def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """
        Analyze a requirement against knowledge base

        Args:
            requirement: Technical requirement from edital

        Returns:
            {
                "conformity": "CONFORME | NAO_CONFORME | PARCIAL",
                "confidence": 0.85,
                "evidence": [...],
                "reasoning": "...",
                "sources": [...]
            }
        """
        # 1. Search knowledge base for relevant info
        # 2. Analyze conformity
        # 3. Generate evidence
        # 4. Return structured result
        pass
```

---

## 🧪 Testes

### Unit Tests

1. **`test_vector_store.py`**
   - Test FAISS add/search/delete
   - Test similarity scoring
   - Test edge cases (empty, large batches)

2. **`test_embeddings.py`**
   - Test local embeddings generation
   - Test embedding dimensions
   - Test batch processing

3. **`test_ingestion.py`**
   - Test markdown file loading
   - Test text chunking
   - Test ingestion pipeline
   - Test statistics reporting

### Integration Tests

1. **`test_rag_search.py`**
   - Test end-to-end search
   - Test relevance of results
   - Test with mock documents
   - Test performance (< 1s per query)

---

## 📊 Métricas de Sucesso

| Métrica | Target | Como Medir |
|---------|--------|------------|
| Tempo de ingestão | < 10s para 6 docs | Pipeline timer |
| Tempo de busca | < 1s por query | Search timer |
| Relevância | Top-3 em 90% casos | Manual validation |
| Cobertura de testes | > 90% | pytest-cov |
| Tamanho do índice | < 50MB | Disk usage |
| Qualidade dos mocks | High fidelity | Manual review |

---

## 📅 Cronograma Detalhado

### Dia 1 (2-3h)
- [x] ✅ Criar SPRINT_5_PLAN.md
- [ ] Criar estrutura de diretórios
- [ ] Criar 3 primeiros documentos mock (Leis 8.666 e 14.133, requisitos técnicos)
- [ ] Configurar .env.example

### Dia 2 (2-3h)
- [ ] Criar 3 documentos mock restantes (qualificação, prazos, pontuação)
- [ ] Instalar dependências Python
- [ ] Implementar VectorStoreInterface + FAISSVectorStore

### Dia 3 (2-3h)
- [ ] Implementar EmbeddingsManager (local)
- [ ] Implementar IngestionPipeline
- [ ] Testar ingestão dos 6 documentos

### Dia 4 (2-3h)
- [ ] Implementar RAGEngine
- [ ] Implementar QueryProcessor (base)
- [ ] Testar busca end-to-end

### Dia 5 (1-2h)
- [ ] Criar testes unitários
- [ ] Criar testes de integração
- [ ] Documentar (RAG_SETUP.md)

**Total:** 6-8 horas (~5 dias úteis)

---

## 🔄 Migração Futura para Cloud

### Passo 1: Configurar Pinecone (30 min)
```bash
# 1. Criar conta no Pinecone (free tier)
# 2. Criar index "bidanalyzee-mvp" (dimension=1536)
# 3. Adicionar API key no .env

PINECONE_API_KEY=pk-xxx
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=bidanalyzee-mvp
RAG_VECTOR_STORE=pinecone  # Trocar de faiss para pinecone
```

### Passo 2: Configurar OpenAI Embeddings (15 min)
```bash
OPENAI_API_KEY=sk-xxx
RAG_EMBEDDINGS_PROVIDER=openai  # Trocar de local para openai
RAG_EMBEDDINGS_MODEL=text-embedding-3-small
```

### Passo 3: Configurar n8n Workflow (1h)
```bash
# 1. Criar workflow de web scraping no n8n
# 2. Configurar webhook endpoint
# 3. Testar ingestão

N8N_BASE_URL=https://n8n.yourcompany.com
N8N_WEBHOOK_URL=https://n8n.yourcompany.com/webhook/genetec-docs
```

### Passo 4: Importar Docs Reais (1h)
```bash
# 1. Executar n8n workflow
# 2. Validar documentos importados
# 3. Re-ingerir no Pinecone

RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/real  # Trocar de mock para real
```

**Total migração:** ~2.5 horas

---

## 📚 Referências

### Tecnologias
- **LangChain:** https://python.langchain.com/docs/
- **FAISS:** https://github.com/facebookresearch/faiss
- **sentence-transformers:** https://www.sbert.net/
- **Pinecone:** https://docs.pinecone.io/ (future)

### Documentação Legal
- **Lei 8.666/93:** http://www.planalto.gov.br/ccivil_03/leis/l8666cons.htm
- **Lei 14.133/2021:** http://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/L14133.htm

### Best Practices
- **RAG Design Patterns:** https://docs.llamaindex.ai/en/stable/
- **Vector Search:** https://www.pinecone.io/learn/vector-search/

---

## ✅ Definition of Done

História 5.1 está completa quando:

- [ ] Sistema RAG funcional com FAISS local
- [ ] 6 documentos mock criados e ingeridos
- [ ] Busca semântica retorna resultados relevantes (90%+ accuracy)
- [ ] Arquitetura modular com interfaces abstratas
- [ ] Configuração via `.env` implementada
- [ ] Testes unitários escritos e passando (90%+ coverage)
- [ ] Testes de integração escritos e passando
- [ ] Documentação completa (RAG_SETUP.md)
- [ ] Código commitado na branch atual
- [ ] Performance targets atingidos (< 10s ingestão, < 1s busca)

---

**Status:** 🚀 Ready to Start
**Próximo Passo:** Criar estrutura de diretórios
**Responsável:** Claude (Technical Analyst Agent development)
**Data:** 07 de novembro de 2025
