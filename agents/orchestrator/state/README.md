# State Management - BidAnalyzee Orchestrator

Sistema de gerenciamento de estado e persistência de sessões para o Orchestrator.

## 📋 Visão Geral

O State Management permite:
- ✅ Persistir sessões de análise
- ✅ Recuperar estado entre execuções
- ✅ Rastrear histórico de análises
- ✅ Fazer backup/restore de sessões
- ✅ Limpar sessões antigas automaticamente

## 🏗️ Arquitetura

```
agents/orchestrator/state/
├── __init__.py           # Exports públicos
├── state_manager.py      # Gerenciador principal
├── session.py            # Classe Session
├── session_schema.py     # Schemas de dados
└── README.md             # Esta documentação

data/state/
├── sessions/             # Arquivos JSON de sessões
│   ├── session_20251116_143000.json
│   └── session_20251116_150000.json
├── backups/              # Backups compactados
│   └── sessions_backup_20251116_160000.tar.gz
└── index.json            # Índice de sessões
```

## 🚀 Uso Programático

### Criar e Salvar Sessão

```python
from agents.orchestrator.state import StateManager

# Inicializar
manager = StateManager()

# Criar nova sessão
session = manager.create_session()

# Atualizar informações
session.set_edital_info(
    edital_path="/path/to/edital.pdf",
    edital_name="Edital 123/2025"
)

session.update_stage("extracting")

# Salvar
manager.save_session(session)
```

### Carregar Sessão Existente

```python
# Por ID
session = manager.load_session("session_20251116_143000")

# Última sessão
session = manager.get_latest_session()
```

### Listar Sessões

```python
# Todas as sessões (ordenadas por data)
sessions = manager.list_sessions()

# Últimas 10
sessions = manager.list_sessions(limit=10)

# Exibir
for s in sessions:
    print(f"{s['session_id']}: {s['status']} - {s['workflow_stage']}")
```

### Deletar Sessão

```python
deleted = manager.delete_session("session_20251116_143000")
if deleted:
    print("Sessão removida")
```

### Backup e Restore

```python
# Criar backup
backup_file = manager.backup_all_sessions()
print(f"Backup salvo em: {backup_file}")

# Restaurar
num_restored = manager.restore_from_backup(backup_file)
print(f"{num_restored} sessões restauradas")
```

### Limpeza Automática

```python
# Remover sessões com mais de 30 dias
removed = manager.cleanup_old_sessions(days=30)
print(f"{removed} sessões removidas")

# Remover tudo com mais de 7 dias (inclusive completadas)
removed = manager.cleanup_old_sessions(days=7, keep_completed=False)
```

### Estatísticas

```python
stats = manager.get_sessions_stats()

print(f"Total: {stats['total']}")
print(f"Por status: {stats['by_status']}")
print(f"Por estágio: {stats['by_stage']}")
print(f"Tamanho: {stats['total_size_mb']} MB")
```

## 🖥️ Uso via CLI

### CLI Unificado (Recomendado)

```bash
# Interface unificada
python scripts/orchestrator_cli.py <command> [args]

# Exemplos:
python scripts/orchestrator_cli.py list 20
python scripts/orchestrator_cli.py show session_20251116_143000
python scripts/orchestrator_cli.py stats
python scripts/orchestrator_cli.py backup
python scripts/orchestrator_cli.py cleanup 30
python scripts/orchestrator_cli.py delete session_20251116_143000
```

### Scripts Individuais

#### Listar Sessões

```bash
python scripts/orchestrator_list.py [limit]

# Exemplos:
python scripts/orchestrator_list.py      # últimas 10
python scripts/orchestrator_list.py 20   # últimas 20
```

#### Ver Detalhes

```bash
python scripts/orchestrator_session.py <session_id>

# Exemplo:
python scripts/orchestrator_session.py session_20251116_143000
```

#### Estatísticas

```bash
python scripts/orchestrator_stats.py
```

#### Backup

```bash
python scripts/orchestrator_backup.py

# Saída:
# ✅ Backup criado: data/state/backups/sessions_backup_20251116_160000.tar.gz
# 📊 Sessões incluídas: 15
# 💾 Tamanho total: 0.45 MB
```

#### Restore

```bash
python scripts/orchestrator_restore.py <backup_file>

# Exemplo:
python scripts/orchestrator_restore.py data/state/backups/sessions_backup_20251116_160000.tar.gz

# Atenção: Criará backup automático das sessões atuais antes
```

#### Cleanup

```bash
python scripts/orchestrator_cleanup.py [days] [keep_completed]

# Exemplos:
python scripts/orchestrator_cleanup.py          # 30 dias, manter completadas
python scripts/orchestrator_cleanup.py 7        # 7 dias, manter completadas
python scripts/orchestrator_cleanup.py 7 false  # 7 dias, remover todas
```

## 📊 Estrutura de Dados

### SessionMetadata

```python
{
    "session_id": "session_20251116_143000",
    "created_at": "2025-11-16T14:30:00.123456",
    "updated_at": "2025-11-16T14:45:30.789012",
    "status": "completed",  # in_progress | completed | failed | cancelled
    "workflow_stage": "completed"  # idle | extracting | analyzing | completed
}
```

### SessionData

```python
{
    "metadata": {...},  # SessionMetadata
    "edital_info": {
        "path": "/path/to/edital.pdf",
        "name": "Edital 123/2025",
        "timestamp": "2025-11-16T14:30:00"
    },
    "extraction_result": {
        "csv_path": "/path/to/requirements.csv",
        "num_requirements": 87,
        "timestamp": "2025-11-16T14:35:00"
    },
    "analysis_result": {
        "csv_path": "/path/to/analysis.csv",
        "summary": {
            "total": 87,
            "conforme": 65,
            "nao_conforme": 8,
            "parcial": 10,
            "requer_analise": 4
        },
        "timestamp": "2025-11-16T14:45:00"
    },
    "errors": [
        {
            "timestamp": "2025-11-16T14:32:00",
            "message": "Erro ao processar página 45"
        }
    ]
}
```

## 🔄 Workflow de Estágios

```
idle → extracting → analyzing → completed
```

**Status possíveis:**
- `in_progress`: Análise em andamento
- `completed`: Concluída com sucesso
- `failed`: Falhou com erros
- `cancelled`: Cancelada pelo usuário

## ⚙️ Configuração

### Diretório de Estado

Por padrão: `data/state/`

Customizar:

```python
manager = StateManager(state_dir="/custom/path")
```

### Diretório de Backup

Por padrão: `data/state/backups/`

Customizar:

```python
backup_file = manager.backup_all_sessions(backup_dir="/custom/backup/path")
```

## 🛡️ Boas Práticas

### 1. Sempre Salvar Após Atualização

```python
session.update_stage("analyzing")
manager.save_session(session)  # Importante!
```

### 2. Tratar Erros

```python
try:
    session = manager.load_session(session_id)
    if session is None:
        print("Sessão não encontrada")
except Exception as e:
    print(f"Erro: {e}")
```

### 3. Backups Regulares

```bash
# Agendar backup diário (cron)
0 2 * * * cd /path/to/BidAnalyzee && python scripts/orchestrator_backup.py
```

### 4. Limpeza Periódica

```bash
# Agendar limpeza semanal (cron)
0 3 * * 0 cd /path/to/BidAnalyzee && python scripts/orchestrator_cleanup.py 30
```

### 5. Monitorar Espaço

```python
stats = manager.get_sessions_stats()
if stats["total_size_mb"] > 100:  # > 100MB
    print("⚠️  Considere fazer limpeza")
```

## 🐛 Troubleshooting

### "FileNotFoundError: index.json"

**Solução:** Diretórios criados automaticamente na primeira execução. Se persistir:

```bash
mkdir -p data/state/sessions data/state/backups
```

### "Session not found"

**Verificar:**
```bash
ls data/state/sessions/
python scripts/orchestrator_list.py
```

### "Backup corrupted"

**Verificar integridade:**
```bash
tar -tzf data/state/backups/sessions_backup_*.tar.gz
```

### Permissões

```bash
chmod -R 755 data/state/
chmod +x scripts/orchestrator_*.py
```

## 📚 Referências

- [StateManager API](state_manager.py)
- [Session API](session.py)
- [Schemas](session_schema.py)
- [CLI Scripts](../../../scripts/)

---

**Última atualização:** 16/11/2025
**Versão:** 1.0
