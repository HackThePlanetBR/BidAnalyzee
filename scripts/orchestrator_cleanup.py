#!/usr/bin/env python3
"""
Orchestrator Cleanup Command

Remove sessões antigas
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def main():
    """Entry point"""
    # Parse argumentos
    days = 30  # padrão
    keep_completed = True  # padrão

    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"❌ Erro: '{sys.argv[1]}' não é um número válido")
            sys.exit(1)

    if len(sys.argv) > 2:
        keep_completed = sys.argv[2].lower() in ['true', 'yes', 's', '1']

    manager = StateManager()

    # Estatísticas antes
    stats_before = manager.get_sessions_stats()

    print(f"\n🧹 Limpando sessões antigas...")
    print(f"   📅 Remover sessões com mais de {days} dias")
    print(f"   💾 Manter sessões completadas: {'Sim' if keep_completed else 'Não'}")
    print(f"\n   📊 Sessões atuais: {stats_before['total']}")

    if stats_before['total'] == 0:
        print("\n✅ Nenhuma sessão encontrada. Nada a limpar.\n")
        return

    try:
        removed = manager.cleanup_old_sessions(days=days, keep_completed=keep_completed)

        stats_after = manager.get_sessions_stats()

        print(f"\n✅ Limpeza concluída!")
        print(f"   🗑️  Sessões removidas: {removed}")
        print(f"   📊 Sessões restantes: {stats_after['total']}")

        if removed > 0:
            print(f"\n💾 Espaço liberado: {stats_before['total_size_mb'] - stats_after['total_size_mb']:.2f} MB\n")
        else:
            print("\n💡 Nenhuma sessão antiga encontrada.\n")

    except Exception as e:
        print(f"\n❌ Erro durante limpeza: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
