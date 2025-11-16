# BidAnalyzee - Guia de Setup

**Versão:** 1.0
**Data:** 06 de novembro de 2025
**Tempo Estimado:** 30-45 minutos

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- [ ] **Claude Code** instalado e funcionando
- [ ] **Acesso ao n8n** (self-hosted em https://hacktheplanet.net.br/)
- [ ] **Conta Google** (para Google Sheets - temporário no MVP)
- [ ] **Python 3.9+** (para scripts utilitários)
- [ ] **Git** configurado

---

## 🚀 Setup Passo a Passo

### 1. Clone e Configuração Inicial

```bash
# 1. Clone o repositório
git clone https://github.com/HackThePlanetBR/BidAnalyzee.git
cd BidAnalyzee

# 2. Checkout do branch de desenvolvimento
git checkout claude/mvp-edital-analysis-system-011CUqud41XKsGBfxahsPMJv

# 3. Crie o arquivo .env a partir do exemplo
cp .env.example .env
```

---

### 2. Configurar Pinecone (Banco Vetorial)

⚠️ **Ação Necessária:** Você ainda não tem uma conta Pinecone. Siga os passos abaixo.

#### 2.1 Criar Conta Pinecone

1. Acesse: https://app.pinecone.io/
2. Clique em "Sign Up"
3. Escolha **"Starter (Free)"** plan
   - 1 index
   - 100K vetores
   - Suficiente para o MVP

#### 2.2 Criar o Index

Após criar a conta:

1. No dashboard do Pinecone, clique em **"Create Index"**
2. Preencha:
   ```
   Name: bidanalyzee-knowledge-base
   Dimensions: 1536
   Metric: cosine
   Region: Escolha a mais próxima do Brasil (ex: us-east-1)
   ```
3. Clique em "Create Index"

#### 2.3 Obter Credenciais

1. No dashboard, vá em **"API Keys"**
2. Copie:
   - **API Key** (chave longa começando com `pcsk_` ou similar)
   - **Environment** (ex: `us-east-1-aws`)

#### 2.4 Configurar no .env

Abra o arquivo `.env` e preencha:

```bash
PINECONE_API_KEY=sua_chave_aqui
PINECONE_ENVIRONMENT=us-east-1-aws  # ou o que você escolheu
PINECONE_INDEX_NAME=bidanalyzee-knowledge-base
```

📖 **Detalhes:** Consulte `docs/PINECONE_SETUP.md` para troubleshooting.

---

### 3. Configurar n8n (Automação)

Você já tem o n8n em **https://hacktheplanet.net.br/**. Agora precisamos:

#### 3.1 Obter API Key do n8n

1. Acesse: https://hacktheplanet.net.br/
2. Faça login
3. Vá em **Settings > API**
4. Clique em **"Create API Key"**
5. Copie a chave gerada

#### 3.2 Configurar no .env

```bash
N8N_API_KEY=sua_chave_n8n_aqui
```

#### 3.3 Importar Workflows (será feito no Sprint 5)

Os workflows de ingestão e consulta serão criados e importados posteriormente.
Por enquanto, apenas valide o acesso ao n8n.

**Teste de Conectividade:**

```bash
curl -H "X-N8N-API-KEY: sua_chave_aqui" https://hacktheplanet.net.br/api/v1/workflows
```

Se retornar JSON com lista de workflows (mesmo vazia), está funcionando.

---

### 4. Configurar Google Sheets (MVP Temporário)

Durante o MVP, usaremos Google Sheets para rastrear URLs ingeridas.

#### 4.1 Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto: **"BidAnalyzee MVP"**
3. Ative a **Google Sheets API**

#### 4.2 Criar Credenciais de Serviço

1. Vá em **"APIs & Services" > "Credentials"**
2. Clique em **"Create Credentials" > "Service Account"**
3. Nome: `bidanalyzee-service`
4. Após criar, clique no service account criado
5. Vá em **"Keys" > "Add Key" > "Create new key"**
6. Escolha **JSON** e baixe o arquivo

#### 4.3 Mover Credenciais

```bash
mkdir -p credentials
mv ~/Downloads/bidanalyzee-service-*.json credentials/google_credentials.json
```

#### 4.4 Criar Google Sheet

1. Acesse: https://sheets.google.com/
2. Crie uma nova planilha: **"BidAnalyzee - URL Tracking"**
3. Adicione as colunas na primeira linha:
   ```
   URL | Title | Last_Updated | Status | Error_Log
   ```
4. Copie o **ID da planilha** (da URL):
   ```
   https://docs.google.com/spreadsheets/d/[ESTE_É_O_ID]/edit
   ```
5. Compartilhe a planilha com o email do service account (está no JSON baixado)
   - Permissão: **Editor**

#### 4.5 Configurar no .env

```bash
GOOGLE_SHEETS_ID=id_da_planilha_aqui
GOOGLE_CREDENTIALS_PATH=./credentials/google_credentials.json
```

---

### 5. Instalar Dependências Python (Opcional, mas Recomendado)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências (quando o requirements.txt estiver pronto)
# pip install -r requirements.txt
```

**Nota:** O requirements.txt será criado nos próximos sprints.

---

### 6. Validar Configuração

Execute o script de validação:

```bash
python scripts/validate_setup.py
```

**Output Esperado:**

```
✅ Estrutura de diretórios: OK
✅ Arquivo .env: OK
✅ Pinecone: Conectado (Index: bidanalyzee-knowledge-base)
✅ n8n: Conectado (URL: https://hacktheplanet.net.br/)
✅ Google Sheets: Acessível
✅ Templates SHIELD: 3/3 encontrados
✅ Checklists: 3/3 encontrados

🎉 Setup completo! Você está pronto para o Sprint 1.
```

Se houver erros, consulte a seção **Troubleshooting** abaixo.

---

## 🔧 Troubleshooting

### Erro: "Pinecone API Key inválida"

**Causa:** API Key incorreta ou expirada.

**Solução:**
1. Verifique se copiou a chave completa (sem espaços)
2. Gere uma nova chave no dashboard do Pinecone
3. Atualize o `.env`

---

### Erro: "n8n Connection Refused"

**Causa:** URL incorreta ou n8n não está rodando.

**Solução:**
1. Verifique se `https://hacktheplanet.net.br/` está acessível no navegador
2. Confirme que o n8n está rodando:
   ```bash
   curl https://hacktheplanet.net.br/
   ```
3. Se estiver usando Docker, verifique o container:
   ```bash
   docker ps | grep n8n
   ```

---

### Erro: "Google Sheets Permission Denied"

**Causa:** Service account não tem acesso à planilha.

**Solução:**
1. Abra a planilha no Google Sheets
2. Clique em "Compartilhar"
3. Adicione o email do service account (está em `credentials/google_credentials.json`, campo `client_email`)
4. Dê permissão de **Editor**

---

### Erro: "Template file not found"

**Causa:** Estrutura de diretórios incompleta.

**Solução:**
```bash
# Re-executar criação de estrutura
python scripts/setup_structure.py
```

---

## 📚 Próximos Passos

Após completar o setup:

1. ✅ Valide a configuração: `python scripts/validate_setup.py`
2. 📖 Leia a documentação do Framework SHIELD: `OPERATING_PRINCIPLES.md`
3. 🏗️ Aguarde o Sprint 1 para começar a implementação dos agentes
4. 💬 Em caso de dúvidas, consulte a [documentação completa](../README.md)

---

## 🆘 Suporte

- **Issues:** [GitHub Issues](https://github.com/HackThePlanetBR/BidAnalyzee/issues)
- **Documentação:** Pasta `docs/`
- **Arquitetura:** `ARCHITECTURE_DECISIONS.md`

---

**Tempo de Setup:** ~30-45 minutos
**Dificuldade:** Intermediária
**Última Atualização:** 06/11/2025
