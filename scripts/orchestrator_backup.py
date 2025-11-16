#!/usr/bin/env python3
"""
Orchestrator Backup Command

Cria backup de todas as sessões
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def main():
    """Entry point"""
    manager = StateManager()

    print("\n🔄 Criando backup de todas as sessões...")

    try:
        backup_file = manager.backup_all_sessions()

        # Estatísticas
        stats = manager.get_sessions_stats()

        print(f"\n✅ Backup criado com sucesso!")
        print(f"   📁 Arquivo: {backup_file}")
        print(f"   📊 Sessões incluídas: {stats['total']}")
        print(f"   💾 Tamanho total: {stats['total_size_mb']} MB")

        print(f"\n💡 Para restaurar: python scripts/orchestrator_restore.py {backup_file}\n")

    except Exception as e:
        print(f"\n❌ Erro ao criar backup: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
