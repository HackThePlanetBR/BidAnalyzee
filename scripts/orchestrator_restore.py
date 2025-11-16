#!/usr/bin/env python3
"""
Orchestrator Restore Command

Restaura sessões de um backup
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Erro: Arquivo de backup não fornecido\n")
        print("Uso: python scripts/orchestrator_restore.py <backup_file>\n")
        print("Exemplo: python scripts/orchestrator_restore.py data/state/backups/sessions_backup_20251116_143000.tar.gz\n")
        sys.exit(1)

    backup_file = sys.argv[1]

    print(f"\n🔄 Restaurando sessões de: {backup_file}\n")
    print("⚠️  ATENÇÃO: Isso irá sobrescrever todas as sessões atuais!")
    print("   Um backup das sessões atuais será criado automaticamente.\n")

    response = input("Continuar? (s/n): ")
    if response.lower() != 's':
        print("\n⏸️  Operação cancelada.\n")
        sys.exit(0)

    manager = StateManager()

    try:
        num_restored = manager.restore_from_backup(backup_file)

        print(f"\n✅ Restauração concluída com sucesso!")
        print(f"   📊 Sessões restauradas: {num_restored}")

        print(f"\n💡 Use 'python scripts/orchestrator_list.py' para ver as sessões\n")

    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro ao restaurar backup: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
