#!/usr/bin/env python3
"""
BidAnalyzee - Project Structure Validator
Validates that all required directories, files, and configurations are in place.
Version: 1.0
"""

import os
import sys
from pathlib import Path


def check_icon(passed: bool) -> str:
    """Return a checkmark or X icon based on test result."""
    return "✅" if passed else "❌"


def check_directory_exists(path: str) -> bool:
    """Check if a directory exists."""
    return os.path.isdir(path)


def check_file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def validate_structure():
    """Validate the complete project structure."""
    print("🔍 Validando estrutura do projeto BidAnalyzee...\n")

    all_passed = True

    # Required directories
    required_dirs = [
        ".claude/commands",
        "agents/orchestrator/checklists",
        "agents/document_structurer/checklists",
        "agents/technical_analyst/checklists",
        "framework/phases",
        "framework/checklists",
        "framework/templates",
        "workflows",
        "services/n8n",
        "services/pinecone",
        "services/document_parser",
        "data/analyses",
        "data/state",
        "data/templates",
        "scripts",
        "tests/unit",
        "tests/integration",
        "docs",
    ]

    print("📁 Diretórios:")
    for dir_path in required_dirs:
        exists = check_directory_exists(dir_path)
        print(f"  {check_icon(exists)} {dir_path}")
        if not exists:
            all_passed = False

    # Required files
    required_files = [
        "README.md",
        "IMPLEMENTATION_STRATEGY.md",
        "ARCHITECTURE_DECISIONS.md",
        "OPERATING_PRINCIPLES.md",
        "NEXT_STEPS.md",
        ".gitignore",
        ".env.example",
        "framework/templates/plan_template.yaml",
        "framework/templates/inspection_result.yaml",
        "framework/templates/validation_result.yaml",
        "framework/checklists/anti_alucinacao.yaml",
        "agents/document_structurer/checklists/inspect.yaml",
        "agents/technical_analyst/checklists/inspect.yaml",
        "docs/SETUP.md",
        "docs/PINECONE_SETUP.md",
    ]

    print("\n📄 Arquivos:")
    for file_path in required_files:
        exists = check_file_exists(file_path)
        print(f"  {check_icon(exists)} {file_path}")
        if not exists:
            all_passed = False

    # Check .env (warn if not exists, but don't fail)
    print("\n⚙️  Configuração:")
    env_exists = check_file_exists(".env")
    if env_exists:
        print(f"  ✅ .env (configurado)")
    else:
        print(f"  ⚠️  .env (não encontrado - copie de .env.example)")

    # Count templates and checklists
    print("\n📋 Framework SHIELD:")
    template_count = len([f for f in os.listdir("framework/templates") if f.endswith(".yaml")])
    print(f"  ✅ Templates: {template_count}/3")

    checklist_count = len([f for f in os.listdir("framework/checklists") if f.endswith(".yaml")])
    print(f"  ✅ Checklists (framework): {checklist_count}/1")

    agent_checklists = 0
    for agent in ["document_structurer", "technical_analyst"]:
        checklist_path = f"agents/{agent}/checklists/inspect.yaml"
        if check_file_exists(checklist_path):
            agent_checklists += 1
    print(f"  ✅ Checklists (agentes): {agent_checklists}/2")

    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("🎉 Estrutura validada com sucesso!")
        print("\n✅ Todos os diretórios e arquivos essenciais estão presentes.")
        print("\n📚 Próximos passos:")
        print("  1. Configure o .env (copie de .env.example)")
        print("  2. Siga o guia em docs/SETUP.md")
        print("  3. Inicie o Sprint 1!")
        return 0
    else:
        print("❌ Estrutura incompleta!")
        print("\n⚠️  Alguns diretórios ou arquivos estão faltando.")
        print("   Execute novamente o setup ou crie os itens manualmente.")
        return 1


if __name__ == "__main__":
    exit_code = validate_structure()
    sys.exit(exit_code)
