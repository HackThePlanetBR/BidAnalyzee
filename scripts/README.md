# Scripts Utilitários

Esta pasta contém scripts auxiliares para setup, validação e manutenção do projeto BidAnalyzee.

## Scripts Disponíveis

### `validate_structure.py`

**Propósito:** Valida que a estrutura completa do projeto está correta.

**Uso:**
```bash
python3 scripts/validate_structure.py
```

**O que verifica:**
- ✅ Todos os diretórios necessários existem
- ✅ Arquivos de documentação estão presentes
- ✅ Templates SHIELD estão criados
- ✅ Checklists dos agentes existem
- ⚠️ Arquivo .env está configurado (aviso)

**Output:**
- Exit code 0: Tudo OK
- Exit code 1: Estrutura incompleta

---

## Scripts Futuros (Próximos Sprints)

### `test_pinecone_connection.py` (Sprint 1)
Testa conexão com o Pinecone e valida credenciais.

### `test_n8n_connection.py` (Sprint 5)
Testa conexão com o n8n e lista workflows disponíveis.

### `setup_database.py` (Sprint 5)
Inicializa o index do Pinecone com schema correto.

### `import_workflows.py` (Sprint 5)
Importa os workflows n8n (ingestão + consulta) para a instância.

### `validate_config.py` (Sprint 1)
Valida que todas as variáveis do .env estão preenchidas corretamente.

---

## Convenções

- Todos os scripts devem ser executáveis: `chmod +x script.py`
- Todos os scripts devem ter shebang: `#!/usr/bin/env python3`
- Usar Python 3.9+ para compatibilidade
- Incluir docstring no topo do arquivo
- Retornar exit codes apropriados (0 = sucesso, 1 = erro)

---

**Última atualização:** Sprint 0
