#!/usr/bin/env python3
"""
Orchestrator List Command - *listar_analises

Lista histórico de análises realizadas
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def format_duration(created_at: str, updated_at: str) -> str:
    """Calcula duração entre timestamps"""
    from datetime import datetime

    created = datetime.fromisoformat(created_at)
    updated = datetime.fromisoformat(updated_at)
    duration = updated - created

    minutes = int(duration.total_seconds() / 60)
    if minutes < 60:
        return f"{minutes}min"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h{mins:02d}min"


def format_status_icon(status: str) -> str:
    """Retorna ícone para status"""
    icons = {
        "completed": "✅",
        "in_progress": "🔄",
        "failed": "❌",
        "cancelled": "⏸️"
    }
    return icons.get(status, "❓")


def format_stage(stage: str) -> str:
    """Formata nome do estágio"""
    stages = {
        "idle": "Aguardando",
        "extracting": "Extraindo",
        "analyzing": "Analisando",
        "completed": "Completo"
    }
    return stages.get(stage, stage)


def list_analyses(limit: int = 10):
    """
    Lista últimas análises

    Args:
        limit: Número máximo de análises a exibir
    """
    manager = StateManager()
    sessions = manager.list_sessions(limit=limit)

    if not sessions:
        print("\n📋 Nenhuma análise encontrada.")
        print("   Execute /structure-edital para iniciar uma nova análise.\n")
        return

    print(f"\n📋 HISTÓRICO DE ANÁLISES (últimas {len(sessions)})")
    print("═" * 80)

    for i, session in enumerate(sessions, 1):
        status_icon = format_status_icon(session["status"])
        stage = format_stage(session["workflow_stage"])
        duration = format_duration(session["created_at"], session["updated_at"])

        # Data de criação formatada
        from datetime import datetime
        created = datetime.fromisoformat(session["created_at"])
        date_str = created.strftime("%d/%m/%Y %H:%M")

        print(f"\n{i}. {status_icon} {session['session_id']}")
        print(f"   📅 Data: {date_str}")
        print(f"   🔄 Estágio: {stage}")
        print(f"   ⏱️  Duração: {duration}")
        print(f"   📊 Status: {session['status']}")

    print("\n" + "═" * 80)
    print(f"💡 Use '*sessao <id>' para ver detalhes de uma análise específica\n")


def main():
    """Entry point"""
    # Obter limite dos argumentos
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"❌ Erro: '{sys.argv[1]}' não é um número válido")
            sys.exit(1)

    list_analyses(limit)


if __name__ == "__main__":
    main()
