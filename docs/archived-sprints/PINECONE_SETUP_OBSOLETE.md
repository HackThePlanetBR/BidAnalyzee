# Pinecone Setup Guide - BidAnalyzee

**Versão:** 1.0
**Tempo Estimado:** 10-15 minutos

---

## 📖 O que é Pinecone?

Pinecone é um banco de dados vetorial gerenciado (serverless) que permite:
- Armazenar embeddings (vetores) de documentos técnicos
- Realizar buscas semânticas ultra-rápidas
- Escalar automaticamente conforme a demanda

No BidAnalyzee, o Pinecone armazena toda a base de conhecimento da solução (manuais, especificações técnicas), permitindo que o sistema encontre rapidamente as informações relevantes para cada requisito do edital.

---

## 🆓 Planos e Custos

### Starter (Free) - **RECOMENDADO PARA MVP**
- ✅ **Custo:** $0/mês
- ✅ **Vetores:** Até 100,000
- ✅ **Indexes:** 1
- ✅ **Queries:** Ilimitadas
- ✅ **Dimensões:** Até 2000

**Estimativa para MVP:**
- Base de conhecimento Genetec: ~5,000 artigos
- Vetores por artigo: ~3-5 (chunking)
- **Total:** ~15,000-25,000 vetores
- **Margem:** Tranquilamente dentro do free tier

### Standard (Paid)
- **Custo:** A partir de $70/mês
- **Uso:** Apenas se exceder 100K vetores ou precisar de múltiplos indexes

**Recomendação:** Comece com o Starter (Free). Só migre para pago se necessário.

---

## 🚀 Passo a Passo: Criar Conta e Index

### 1. Criar Conta

1. Acesse: https://app.pinecone.io/
2. Clique em **"Sign Up"**
3. Opções de cadastro:
   - **Google Account** (mais rápido)
   - Email + Senha
4. Preencha o formulário:
   ```
   Organization name: BidAnalyzee MVP
   Use case: Semantic Search
   Industry: Software Development
   ```
5. Confirme seu email (se usar email+senha)

### 2. Criar o Index

Após fazer login:

1. No dashboard, clique em **"Create Index"** (botão azul no topo direito)

2. Preencha os campos:

   ```
   Index Name: bidanalyzee-knowledge-base

   Dimensions: 1536
   (Nota: Este é o padrão para embeddings OpenAI text-embedding-ada-002
    e llama-text-embed-v2. NÃO mude a menos que use outro modelo.)

   Metric: cosine
   (Nota: Mede similaridade entre vetores. Cosine é o padrão para texto.)

   Pod Type: Starter (default)

   Region: us-east-1 (ou a mais próxima)
   (Opções: us-east-1, us-west-2, eu-west-1, asia-southeast-1)
   (Recomendação para Brasil: us-east-1)
   ```

3. Clique em **"Create Index"**

4. Aguarde a criação (~30 segundos)

5. Quando o status mudar para **"Ready"**, está pronto!

### 3. Obter Credenciais

1. No painel lateral esquerdo, clique em **"API Keys"**

2. Você verá:
   ```
   API Key: pcsk_XXXXXX...  (clique no ícone de copiar)
   Environment: us-east-1-aws
   ```

3. **Copie ambos!** Você precisará deles no `.env`

---

## 🔧 Configurar no .env

Abra o arquivo `.env` na raiz do projeto e preencha:

```bash
# Pinecone Configuration
PINECONE_API_KEY=pcsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=bidanalyzee-knowledge-base
PINECONE_DIMENSION=1536
PINECONE_METRIC=cosine
```

---

## ✅ Validar Conexão

### Opção 1: Via Python (Recomendado)

```bash
python scripts/test_pinecone_connection.py
```

**Output Esperado:**

```
🔍 Testando conexão com Pinecone...
✅ Conectado com sucesso!
   Index: bidanalyzee-knowledge-base
   Dimensões: 1536
   Métrica: cosine
   Total de vetores: 0
   Status: Ready
```

### Opção 2: Via cURL

```bash
curl -X GET "https://api.pinecone.io/indexes/bidanalyzee-knowledge-base" \
  -H "Api-Key: pcsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

**Output Esperado (JSON):**

```json
{
  "name": "bidanalyzee-knowledge-base",
  "dimension": 1536,
  "metric": "cosine",
  "status": {
    "ready": true,
    "state": "Ready"
  }
}
```

---

## 📊 Entendendo a Estrutura de Dados

### Como os dados são armazenados?

Cada artigo da documentação técnica é convertido em:

1. **Texto** → **Chunking** (divisão em partes de ~500 palavras)
2. Cada chunk → **Embedding** (vetor de 1536 dimensões)
3. Vetor + Metadados → **Armazenado no Pinecone**

**Exemplo de um registro:**

```json
{
  "id": "article-genetec-camera-specs-chunk-1",
  "values": [0.023, -0.145, 0.876, ...],  // 1536 números
  "metadata": {
    "source_url": "https://techdocs.genetec.com/cameras/specs",
    "title": "Especificações Técnicas - Câmeras IP",
    "product": "Genetec Security Center",
    "section": "Câmeras > Especificações Ambientais",
    "chunk_index": 1,
    "total_chunks": 5,
    "last_updated": "2025-11-06"
  }
}
```

### Metadados Importantes

Cada vetor tem metadados que permitem:
- **Filtrar** buscas por produto
- **Rastrear** a fonte original
- **Versionar** atualizações da base de conhecimento

---

## 🧪 Testar com Dados de Exemplo (Opcional)

Quer testar se está tudo funcionando? Vamos inserir 1 vetor de exemplo:

```python
# scripts/test_insert_example.py
import pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

index = pinecone.Index("bidanalyzee-knowledge-base")

# Vetor de exemplo (normalmente viria de um modelo de embedding)
example_vector = [0.1] * 1536  # Vetor dummy

# Inserir
index.upsert(
    vectors=[
        {
            "id": "test-001",
            "values": example_vector,
            "metadata": {
                "title": "Teste de Conexão",
                "source": "setup_guide"
            }
        }
    ]
)

print("✅ Vetor de teste inserido com sucesso!")

# Consultar
stats = index.describe_index_stats()
print(f"📊 Total de vetores no index: {stats['total_vector_count']}")
```

Execute:

```bash
python scripts/test_insert_example.py
```

---

## 🚨 Troubleshooting

### Erro: "Invalid API Key"

**Sintomas:**
```
pinecone.core.client.exceptions.UnauthorizedException: (403)
Reason: Forbidden
```

**Soluções:**
1. Verifique se a API Key está correta (copie novamente do dashboard)
2. Certifique-se de não ter espaços antes/depois da chave no `.env`
3. Gere uma nova API Key no Pinecone e atualize o `.env`

---

### Erro: "Index not found"

**Sintomas:**
```
pinecone.core.client.exceptions.NotFoundException: (404)
Index 'bidanalyzee-knowledge-base' not found
```

**Soluções:**
1. Verifique se o index foi criado no dashboard do Pinecone
2. Confirme que o nome no `.env` é exatamente igual ao do dashboard (case-sensitive)
3. Aguarde 30-60s após criar o index (pode levar um tempo para estar disponível)

---

### Erro: "Dimension mismatch"

**Sintomas:**
```
ValueError: Dimension mismatch. Expected 1536, got 768
```

**Causa:** Você está usando um modelo de embedding diferente.

**Soluções:**
1. Se usar `text-embedding-ada-002` (OpenAI) → dimensão 1536
2. Se usar `all-MiniLM-L6-v2` (Sentence Transformers) → dimensão 384
3. Se usar `llama-text-embed-v2` → dimensão 1536
4. **Ação:** Recrie o index com a dimensão correta

---

### Aviso: "High vector count"

Se você estiver próximo do limite (80K+ vetores no free tier):

**Opção 1: Otimizar Chunking**
- Aumentar tamanho dos chunks (menos chunks por artigo)
- Exemplo: 500 palavras → 1000 palavras

**Opção 2: Filtrar Conteúdo**
- Ingerir apenas artigos relevantes (não toda a documentação)
- Priorizar manuais técnicos sobre marketing

**Opção 3: Upgrade para Paid**
- Se necessário, migre para o plano Standard

---

## 📈 Monitoramento

### Dashboard do Pinecone

Acesse o dashboard para ver:
- **Total de vetores** armazenados
- **Queries por segundo**
- **Latência média** das buscas
- **Uso de storage**

### Via API

```bash
curl -X GET "https://api.pinecone.io/indexes/bidanalyzee-knowledge-base/describe_index_stats" \
  -H "Api-Key: sua_chave_aqui"
```

**Response:**

```json
{
  "dimension": 1536,
  "index_fullness": 0.15,
  "total_vector_count": 15234,
  "namespaces": {
    "": {
      "vector_count": 15234
    }
  }
}
```

---

## 🔄 Próximos Passos

Após configurar o Pinecone:

1. ✅ Valide a conexão: `python scripts/test_pinecone_connection.py`
2. 🔄 Continue o setup geral: `docs/SETUP.md`
3. 📚 No Sprint 5, você configurará o workflow n8n de ingestão
4. 🚀 Então a base de conhecimento será populada automaticamente

---

## 📚 Recursos Adicionais

- **Documentação Oficial:** https://docs.pinecone.io/
- **Pricing:** https://www.pinecone.io/pricing/
- **Python SDK:** https://docs.pinecone.io/docs/python-client
- **Exemplos:** https://docs.pinecone.io/docs/examples

---

**Criado por:** Equipe BidAnalyzee
**Última Atualização:** 06/11/2025
