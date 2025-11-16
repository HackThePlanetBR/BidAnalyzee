#!/usr/bin/env python3
"""
Orchestrator CLI - Interface unificada para gerenciamento de estado

Uso:
    python scripts/orchestrator_cli.py <command> [args]

Comandos disponíveis:
    list [limit]          - Lista sessões (padrão: 10)
    show <session_id>     - Exibe detalhes de uma sessão
    stats                 - Mostra estatísticas
    backup                - Cria backup de todas as sessões
    restore <file>        - Restaura sessões de um backup
    cleanup [days]        - Remove sessões antigas (padrão: 30 dias)
    delete <session_id>   - Remove uma sessão específica
    help                  - Exibe esta mensagem
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def cmd_list(args):
    """Lista sessões"""
    limit = 10
    if args and args[0].isdigit():
        limit = int(args[0])

    import orchestrator_list
    orchestrator_list.list_analyses(limit)


def cmd_show(args):
    """Exibe detalhes de uma sessão"""
    if not args:
        print("\n❌ Erro: ID da sessão não fornecido\n")
        print("Uso: orchestrator_cli.py show <session_id>\n")
        sys.exit(1)

    import orchestrator_session
    orchestrator_session.show_session_details(args[0])


def cmd_stats(args):
    """Exibe estatísticas"""
    import orchestrator_stats
    orchestrator_stats.main()


def cmd_backup(args):
    """Cria backup"""
    import orchestrator_backup
    orchestrator_backup.main()


def cmd_restore(args):
    """Restaura backup"""
    if not args:
        print("\n❌ Erro: Arquivo de backup não fornecido\n")
        print("Uso: orchestrator_cli.py restore <backup_file>\n")
        sys.exit(1)

    import orchestrator_restore
    sys.argv = ['orchestrator_restore.py', args[0]]
    orchestrator_restore.main()


def cmd_cleanup(args):
    """Limpa sessões antigas"""
    import orchestrator_cleanup
    if args:
        sys.argv = ['orchestrator_cleanup.py'] + args
    else:
        sys.argv = ['orchestrator_cleanup.py']
    orchestrator_cleanup.main()


def cmd_delete(args):
    """Remove uma sessão"""
    if not args:
        print("\n❌ Erro: ID da sessão não fornecido\n")
        print("Uso: orchestrator_cli.py delete <session_id>\n")
        sys.exit(1)

    manager = StateManager()
    session_id = args[0]

    print(f"\n⚠️  Você está prestes a deletar a sessão: {session_id}")
    response = input("Continuar? (s/n): ")

    if response.lower() != 's':
        print("\n⏸️  Operação cancelada.\n")
        return

    if manager.delete_session(session_id):
        print(f"\n✅ Sessão '{session_id}' removida com sucesso!\n")
    else:
        print(f"\n❌ Sessão '{session_id}' não encontrada.\n")
        sys.exit(1)


def cmd_help(args):
    """Exibe ajuda"""
    print(__doc__)


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        cmd_help([])
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        'list': cmd_list,
        'show': cmd_show,
        'stats': cmd_stats,
        'backup': cmd_backup,
        'restore': cmd_restore,
        'cleanup': cmd_cleanup,
        'delete': cmd_delete,
        'help': cmd_help,
        '--help': cmd_help,
        '-h': cmd_help,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"\n❌ Comando desconhecido: {command}\n")
        print("Use 'orchestrator_cli.py help' para ver comandos disponíveis.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
