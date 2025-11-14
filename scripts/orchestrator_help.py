#!/usr/bin/env python3
"""
Orchestrator Help Command - *ajuda

Exibe lista de comandos disponíveis no sistema
"""


def print_help():
    """Exibe ajuda dos comandos disponíveis"""

    help_text = """
🤖 BIDANALYZEE - COMANDOS DISPONÍVEIS
═══════════════════════════════════════════════════════════

📋 ANÁLISE DE EDITAIS
─────────────────────
  /structure-edital <pdf>    Extrai requisitos de edital PDF
  /analyze-edital <csv>      Analisa conformidade de requisitos

🎛️ ORQUESTRADOR
─────────────────────
  *ajuda                     Mostra esta mensagem de ajuda
  *listar_analises [N]       Lista últimas N análises (padrão: 10)
  *sessao <id>               Mostra detalhes de uma sessão
  *buscar "<query>"          Busca rápida na base de conhecimento

📊 EXEMPLOS DE USO
─────────────────────
  # Workflow completo
  /structure-edital data/uploads/edital_001.pdf
  /analyze-edital data/deliveries/.../requirements_structured.csv

  # Consultar histórico
  *listar_analises 5
  *sessao session_20251114_153045

  # Busca rápida
  *buscar "prazo validade proposta licitação"

📚 DOCUMENTAÇÃO
─────────────────────
  - Orchestrator: agents/orchestrator/README.md
  - Document Structurer: agents/document_structurer/README.md
  - Technical Analyst: agents/technical_analyst/README.md

💡 DICA: Use o modo Assistido - após cada comando, o sistema
         sugere automaticamente o próximo passo!
═══════════════════════════════════════════════════════════
"""

    print(help_text)


if __name__ == "__main__":
    print_help()
