#!/usr/bin/env python3
"""
Orchestrator Session Command - *sessao <id>

Exibe detalhes de uma sessão específica
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager


def format_timestamp(iso_timestamp: str) -> str:
    """Formata timestamp ISO para exibição"""
    from datetime import datetime
    dt = datetime.fromisoformat(iso_timestamp)
    return dt.strftime("%d/%m/%Y às %H:%M:%S")


def show_session_details(session_id: str):
    """
    Exibe detalhes de uma sessão

    Args:
        session_id: ID da sessão
    """
    manager = StateManager()
    session = manager.load_session(session_id)

    if session is None:
        print(f"\n❌ Sessão '{session_id}' não encontrada.\n")
        print("💡 Use '*listar_analises' para ver sessões disponíveis.\n")
        return

    # Header
    print(f"\n📊 DETALHES DA SESSÃO: {session_id}")
    print("═" * 80)

    # Metadata
    metadata = session.data.metadata
    print(f"\n📋 Metadados")
    print(f"   Status: {metadata.status}")
    print(f"   Estágio: {metadata.workflow_stage}")
    print(f"   Criado: {format_timestamp(metadata.created_at)}")
    print(f"   Atualizado: {format_timestamp(metadata.updated_at)}")

    # Edital Info
    if session.data.edital_info:
        print(f"\n📄 Informações do Edital")
        print(f"   Nome: {session.data.edital_info.get('name', 'N/A')}")
        print(f"   Caminho: {session.data.edital_info.get('path', 'N/A')}")

    # Extraction Result
    if session.data.extraction_result:
        print(f"\n🔍 Resultado da Extração")
        print(f"   CSV: {session.data.extraction_result.get('csv_path', 'N/A')}")
        print(f"   Requisitos: {session.data.extraction_result.get('num_requirements', 0)}")
        print(f"   Timestamp: {format_timestamp(session.data.extraction_result.get('timestamp'))}")

    # Analysis Result
    if session.data.analysis_result:
        print(f"\n📊 Resultado da Análise")
        print(f"   CSV: {session.data.analysis_result.get('csv_path', 'N/A')}")

        summary = session.data.analysis_result.get('summary', {})
        if summary:
            print(f"   Resumo:")
            for key, value in summary.items():
                print(f"      {key}: {value}")

    # Errors
    if session.data.errors:
        print(f"\n⚠️  Erros ({len(session.data.errors)})")
        for i, error in enumerate(session.data.errors, 1):
            print(f"   {i}. [{error.get('timestamp', 'N/A')}] {error.get('message', 'N/A')}")

    print("\n" + "═" * 80 + "\n")


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Erro: ID da sessão não fornecido\n")
        print("Uso: *sessao <session_id>\n")
        print("Exemplo: *sessao session_20251114_153045\n")
        sys.exit(1)

    session_id = sys.argv[1]
    show_session_details(session_id)


if __name__ == "__main__":
    main()
