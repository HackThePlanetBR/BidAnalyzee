# BidAnalyzee - Guia de Instalação

**Versão:** 1.0.0
**Data:** 16 de novembro de 2025
**Tempo Estimado:** 10-15 minutos
**Dificuldade:** Fácil

---

## 📋 Pré-requisitos

- **Python 3.9+** instalado
- **Git** instalado
- **Tesseract OCR** (opcional - apenas se for processar PDFs escaneados)

---

## 🚀 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/HackThePlanetBR/BidAnalyzee.git
cd BidAnalyzee
```

### 2. Instale as Dependências Python

```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar todas as dependências
pip install -r requirements.txt
```

**Dependências principais instaladas:**
- `faiss-cpu` - Vector store local (busca semântica ultra-rápida)
- `sentence-transformers` - Embeddings multilíngue local
- `langchain` - Framework RAG
- `PyPDF2` - Extração de texto de PDFs
- `pytesseract`, `pdf2image`, `Pillow` - OCR para PDFs escaneados
- `reportlab`, `openpyxl` - Geração de relatórios
- `pytest` - Framework de testes
- `rich` - Dashboard interativo
- Outras dependências auxiliares

### 3. (Opcional) Instalar Tesseract OCR

**Apenas necessário se você for processar PDFs escaneados (sem texto nativo).**

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

#### Windows:
1. Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale com suporte para português
3. Adicione ao PATH: `C:\Program Files\Tesseract-OCR`

Consulte [OCR_INSTALLATION.md](OCR_INSTALLATION.md) para detalhes.

### 4. Indexar a Knowledge Base

**Este passo é necessário para o sistema RAG funcionar.**

```bash
# Indexa os 6 documentos mock da knowledge base
python scripts/index_knowledge_base.py
```

**Output esperado:**
```
🔧 Initializing RAG Engine...
   Vector Store: faiss
   Embeddings: local (all-MiniLM-L6-v2)

📚 Ingesting knowledge base from: data/knowledge_base/mock
   Processing: lei_8666_1993.md
   Processing: lei_14133_2021.md
   Processing: requisitos_tecnicos_comuns.md
   Processing: documentacao_qualificacao.md
   Processing: prazos_cronogramas.md
   Processing: criterios_pontuacao.md

✅ Ingestion complete!
   Documents: 6
   Chunks: 156
   Time: 8.3s

💾 Index saved to: data/vector_store/faiss/
```

---

## ✅ Validar Instalação

### Teste 1: Verificar Dependências

```bash
python -c "import faiss; import sentence_transformers; print('✅ RAG dependencies OK')"
```

### Teste 2: Testar RAG Search

```bash
python scripts/rag_search.py --requirement "Processador Intel Core i7 com 8GB RAM" --top-k 3
```

**Output esperado:**
```
🔍 Searching for: Processador Intel Core i7 com 8GB RAM
✅ Found 3 results

[1] Similarity: 0.87
    Source: requisitos_tecnicos_comuns.md
    Text: "Processadores Intel Core i7 de 8ª geração ou superior..."

[2] Similarity: 0.82
    Source: criterios_pontuacao.md
    Text: "Memória RAM mínima de 8GB DDR4..."
...
```

### Teste 3: Rodar Testes Automatizados

```bash
pytest tests/agents/ -v
```

**Output esperado:**
```
tests/agents/test_document_structurer.py::... PASSED [ 20%]
tests/agents/test_technical_analyst.py::... PASSED [ 45%]
tests/agents/test_orchestrator.py::... PASSED [ 75%]
tests/agents/test_shield_framework.py::... PASSED [100%]

======================== 116 passed in 12.4s =========================
```

---

## 📊 Estrutura Criada

Após a instalação, você terá:

```
BidAnalyzee/
├── venv/                          # Ambiente virtual Python
├── data/
│   ├── knowledge_base/mock/       # 6 documentos (~153KB)
│   └── vector_store/faiss/        # Índice FAISS criado
├── requirements.txt               # Dependências (instaladas)
└── ...
```

---

## 🎯 Próximos Passos

Agora que o sistema está instalado:

1. 📘 **Leia o Guia do Usuário:** [USER_GUIDE.md](USER_GUIDE.md)
2. 🎓 **Faça o Tutorial:** [TUTORIAL.md](TUTORIAL.md) - Sua primeira análise
3. 🔍 **Explore os Scripts Disponíveis:**
   ```bash
   ls scripts/
   # analyze_edital_full.py - Pipeline completo
   # compare_editais.py - Comparação de editais
   # dashboard.py - Dashboard interativo
   # export_pdf.py / export_excel.py - Relatórios
   # validate_output.py - Validação de qualidade
   # rag_search.py - Busca na knowledge base
   ```

---

## 🔧 Troubleshooting

### Erro: "No module named 'faiss'"

**Solução:**
```bash
pip install faiss-cpu
```

### Erro: "sentence-transformers model download failed"

**Causa:** Primeira execução baixa o modelo (~90MB).

**Solução:**
- Aguarde o download completar (pode levar 1-2 minutos)
- Verifique conexão com internet
- Modelo fica em cache: `~/.cache/huggingface/`

### Erro: "pytesseract.TesseractNotFoundError"

**Causa:** Tesseract OCR não instalado (apenas necessário para PDFs escaneados).

**Solução:**
- Instale o Tesseract (ver passo 3 acima)
- Ou ignore se não for processar PDFs escaneados

### Erro: "Permission denied" ao indexar

**Solução:**
```bash
# Garanta permissões de escrita
chmod -R u+w data/
```

### Performance lenta no primeiro uso

**Normal:** Primeira indexação baixa o modelo de embeddings (~90MB) e processa os documentos.
- Execuções subsequentes usam cache e são muito mais rápidas

---

## 🌐 Configuração Avançada (Opcional)

### Customizar Configuração RAG

Crie um arquivo `.env` na raiz do projeto:

```bash
# Vector Store (default: faiss)
RAG_VECTOR_STORE=faiss

# Embeddings (default: local)
RAG_EMBEDDINGS_PROVIDER=local
RAG_EMBEDDINGS_MODEL=all-MiniLM-L6-v2

# Chunking (defaults otimizados)
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200

# Search (defaults otimizados)
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7

# Knowledge Base (default: mock)
RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/mock
```

### Usar Knowledge Base Real

1. Crie o diretório:
   ```bash
   mkdir -p data/knowledge_base/producao
   ```

2. Adicione seus documentos (`.md`, `.txt`):
   ```bash
   cp meus_documentos/*.md data/knowledge_base/producao/
   ```

3. Atualize `.env`:
   ```bash
   RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/producao
   ```

4. Re-indexe:
   ```bash
   python scripts/index_knowledge_base.py
   ```

---

## 📚 Documentação Relacionada

- 📘 [Guia do Usuário](USER_GUIDE.md) - Como usar o sistema
- 🎓 [Tutorial](TUTORIAL.md) - Primeira análise passo a passo
- ❓ [FAQ](FAQ.md) - Perguntas frequentes
- 🏛️ [Arquitetura](../ARCHITECTURE_DECISIONS.md) - Decisões técnicas
- 🛡️ [Framework SHIELD](../OPERATING_PRINCIPLES.md) - Metodologia de governança

---

## 🆘 Suporte

- **Issues:** [GitHub Issues](https://github.com/HackThePlanetBR/BidAnalyzee/issues)
- **Discussões:** [GitHub Discussions](https://github.com/HackThePlanetBR/BidAnalyzee/discussions)

---

**Instalação:** ~10-15 minutos
**Dificuldade:** Fácil (apenas `pip install`)
**Última Atualização:** 16/11/2025
