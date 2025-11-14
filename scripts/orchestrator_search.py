#!/usr/bin/env python3
"""
Orchestrator Search Command - *buscar "<query>"

Busca rápida na base de conhecimento usando RAG
"""

import sys
import subprocess
from pathlib import Path


def search_knowledge_base(query: str, top_k: int = 5):
    """
    Busca na base de conhecimento

    Args:
        query: Consulta de busca
        top_k: Número de resultados a retornar
    """
    # Usar script RAG existente
    rag_script = Path("scripts/rag_search.py")

    if not rag_script.exists():
        print(f"\n❌ Erro: Script RAG não encontrado em {rag_script}\n")
        return

    print(f"\n🔍 Buscando: \"{query}\"\n")
    print("═" * 80)

    # Executar busca RAG
    try:
        result = subprocess.run(
            ["python3", str(rag_script), "--requirement", query, "--top-k", str(top_k)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            # Formatar output do RAG
            print(result.stdout)
        else:
            print(f"❌ Erro na busca:\n{result.stderr}")

    except subprocess.TimeoutExpired:
        print("❌ Erro: Busca excedeu tempo limite de 60 segundos")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

    print("═" * 80)
    print("\n💡 Para análise completa, use /analyze-edital\n")


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Erro: Query de busca não fornecida\n")
        print('Uso: *buscar "<query>"\n')
        print('Exemplo: *buscar "prazo validade proposta"\n')
        sys.exit(1)

    # Juntar todos os argumentos como query
    query = " ".join(sys.argv[1:])

    # Remover aspas se presentes
    query = query.strip('"').strip("'")

    if not query:
        print("\n❌ Erro: Query vazia\n")
        sys.exit(1)

    search_knowledge_base(query)


if __name__ == "__main__":
    main()
