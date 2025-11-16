#!/usr/bin/env python3
"""
Orchestrator Stats Command

Exibe estatísticas sobre sessões
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def format_status(status: str) -> str:
    """Formata status com ícone"""
    icons = {
        "completed": "✅",
        "in_progress": "🔄",
        "failed": "❌",
        "cancelled": "⏸️"
    }
    icon = icons.get(status, "❓")
    return f"{icon} {status}"


def format_stage(stage: str) -> str:
    """Formata estágio"""
    stages = {
        "idle": "⏸️ Aguardando",
        "extracting": "📋 Extraindo",
        "analyzing": "🎯 Analisando",
        "completed": "✅ Completo"
    }
    return stages.get(stage, f"❓ {stage}")


def main():
    """Entry point"""
    manager = StateManager()

    print("\n📊 ESTATÍSTICAS DE SESSÕES")
    print("═" * 80)

    try:
        stats = manager.get_sessions_stats()

        if stats["total"] == 0:
            print("\n   📭 Nenhuma sessão encontrada.\n")
            print("   💡 Execute uma análise para criar a primeira sessão.\n")
            return

        # Estatísticas gerais
        print(f"\n📈 Geral")
        print(f"   Total de sessões: {stats['total']}")
        print(f"   Tamanho total: {stats['total_size_mb']} MB")

        if stats["oldest"]:
            print(f"   Mais antiga: {stats['oldest']}")
        if stats["newest"]:
            print(f"   Mais recente: {stats['newest']}")

        # Por status
        if stats["by_status"]:
            print(f"\n📊 Por Status")
            for status, count in sorted(stats["by_status"].items(), key=lambda x: -x[1]):
                formatted = format_status(status)
                percentage = (count / stats["total"]) * 100
                print(f"   {formatted}: {count} ({percentage:.1f}%)")

        # Por estágio
        if stats["by_stage"]:
            print(f"\n🔄 Por Estágio do Workflow")
            for stage, count in sorted(stats["by_stage"].items(), key=lambda x: -x[1]):
                formatted = format_stage(stage)
                percentage = (count / stats["total"]) * 100
                print(f"   {formatted}: {count} ({percentage:.1f}%)")

        print("\n" + "═" * 80)
        print(f"\n💡 Use 'python scripts/orchestrator_list.py' para ver lista detalhada")
        print(f"💡 Use 'python scripts/orchestrator_cleanup.py <days>' para limpar antigas\n")

    except Exception as e:
        print(f"\n❌ Erro ao obter estatísticas: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
