#!/usr/bin/env python3
"""
Template Manager - Gerenciamento de templates de análise

Permite carregar, salvar, listar e customizar templates de configuração
para análises de editais.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TemplateManager:
    """Gerencia templates de análise"""

    def __init__(self, templates_dir: str = "data/templates"):
        """
        Inicializa o gerenciador de templates

        Args:
            templates_dir: Diretório dos templates
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        Lista todos os templates disponíveis

        Returns:
            Lista de metadados de templates
        """
        templates = []

        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                templates.append({
                    "file": template_file.name,
                    "name": data.get("name", template_file.stem),
                    "description": data.get("description", ""),
                    "category": data.get("category", "unknown"),
                    "version": data.get("version", "1.0"),
                    "tags": data.get("tags", [])
                })
            except Exception as e:
                print(f"⚠️  Erro ao ler {template_file.name}: {e}")
                continue

        return sorted(templates, key=lambda t: t["name"])

    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Carrega um template

        Args:
            template_name: Nome do arquivo do template (com ou sem .yaml)

        Returns:
            Dados do template ou None se não encontrado
        """
        if not template_name.endswith('.yaml'):
            template_name += '.yaml'

        template_file = self.templates_dir / template_name

        if not template_file.exists():
            return None

        with open(template_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_template(self, template_name: str, template_data: Dict[str, Any]) -> str:
        """
        Salva um template

        Args:
            template_name: Nome do template (sem .yaml)
            template_data: Dados do template

        Returns:
            Caminho do arquivo salvo
        """
        # Atualizar metadados
        if "metadata" not in template_data:
            template_data["metadata"] = {}

        template_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

        if "use_count" in template_data.get("metadata", {}):
            template_data["metadata"]["use_count"] += 1

        if not template_name.endswith('.yaml'):
            template_name += '.yaml'

        template_file = self.templates_dir / template_name

        with open(template_file, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return str(template_file)

    def delete_template(self, template_name: str) -> bool:
        """
        Deleta um template

        Args:
            template_name: Nome do template

        Returns:
            True se deletou, False se não existia
        """
        if not template_name.endswith('.yaml'):
            template_name += '.yaml'

        template_file = self.templates_dir / template_name

        if not template_file.exists():
            return False

        template_file.unlink()
        return True

    def create_custom_template(
        self,
        name: str,
        description: str,
        category: str,
        base_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cria um novo template customizado

        Args:
            name: Nome do template
            description: Descrição
            category: Categoria (ti, obras, servicos, etc)
            base_template: Template base para copiar (opcional)

        Returns:
            Template criado
        """
        if base_template:
            template_data = self.load_template(base_template)
            if not template_data:
                raise ValueError(f"Template base não encontrado: {base_template}")
        else:
            # Template vazio básico
            template_data = {
                "name": name,
                "description": description,
                "version": "1.0",
                "category": category,
                "tags": [],
                "analysis_config": {
                    "rag": {
                        "top_k": 5,
                        "similarity_threshold": 0.70,
                        "focus_areas": []
                    },
                    "expected_categories": [],
                    "category_weights": {"default": 1.0},
                    "validations": {
                        "require_certifications": [],
                        "require_technical_specs": True,
                        "require_warranties": False,
                        "minimum_warranty_months": 12
                    }
                },
                "export_config": {
                    "pdf": {
                        "include_diagrams": False,
                        "highlight_critical": True,
                        "group_by_category": True
                    },
                    "excel": {
                        "freeze_panes": True,
                        "conditional_formatting": True,
                        "charts": ["conformity_pie"]
                    }
                },
                "alerts": {
                    "critical_keywords": [],
                    "warning_keywords": []
                },
                "additional_checks": [],
                "metadata": {
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "created_by": "User",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "use_count": 0
                }
            }

        # Sobrescrever metadados
        template_data["name"] = name
        template_data["description"] = description
        template_data["category"] = category

        return template_data

    def get_template_stats(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna estatísticas sobre um template

        Args:
            template_name: Nome do template

        Returns:
            Estatísticas ou None
        """
        template = self.load_template(template_name)

        if not template:
            return None

        return {
            "name": template.get("name"),
            "category": template.get("category"),
            "use_count": template.get("metadata", {}).get("use_count", 0),
            "created_at": template.get("metadata", {}).get("created_at"),
            "last_updated": template.get("metadata", {}).get("last_updated"),
            "num_expected_categories": len(template.get("analysis_config", {}).get("expected_categories", [])),
            "num_critical_keywords": len(template.get("alerts", {}).get("critical_keywords", [])),
            "num_additional_checks": len(template.get("additional_checks", []))
        }


def cmd_list(args):
    """Lista templates"""
    manager = TemplateManager()
    templates = manager.list_templates()

    if not templates:
        print("\n📭 Nenhum template encontrado.\n")
        print("💡 Use 'create' para criar um novo template.\n")
        return

    print(f"\n📋 TEMPLATES DISPONÍVEIS ({len(templates)})")
    print("=" * 80)

    for t in templates:
        print(f"\n📄 {t['file']}")
        print(f"   Nome: {t['name']}")
        print(f"   Categoria: {t['category']}")
        print(f"   Descrição: {t['description']}")
        if t.get('tags'):
            print(f"   Tags: {', '.join(t['tags'])}")

    print("\n" + "=" * 80)
    print("💡 Use 'template_manager.py show <nome>' para ver detalhes\n")


def cmd_show(args):
    """Exibe detalhes de um template"""
    if not args:
        print("\n❌ Erro: Nome do template não fornecido\n")
        print("Uso: template_manager.py show <template_name>\n")
        sys.exit(1)

    manager = TemplateManager()
    template = manager.load_template(args[0])

    if not template:
        print(f"\n❌ Template '{args[0]}' não encontrado.\n")
        sys.exit(1)

    print(f"\n📄 TEMPLATE: {template.get('name')}")
    print("=" * 80)

    print(f"\n📋 Informações Gerais")
    print(f"   Nome: {template.get('name')}")
    print(f"   Descrição: {template.get('description')}")
    print(f"   Categoria: {template.get('category')}")
    print(f"   Versão: {template.get('version')}")
    if template.get('tags'):
        print(f"   Tags: {', '.join(template.get('tags', []))}")

    # Configurações de análise
    analysis = template.get('analysis_config', {})
    print(f"\n⚙️  Configurações de Análise")
    print(f"   RAG top_k: {analysis.get('rag', {}).get('top_k', 'N/A')}")
    print(f"   Threshold: {analysis.get('rag', {}).get('similarity_threshold', 'N/A')}")
    print(f"   Categorias esperadas: {len(analysis.get('expected_categories', []))}")

    if analysis.get('expected_categories'):
        print(f"\n   📊 Categorias:")
        for cat in analysis.get('expected_categories', []):
            weight = analysis.get('category_weights', {}).get(cat, 1.0)
            print(f"      - {cat} (peso: {weight})")

    # Validações
    validations = analysis.get('validations', {})
    if validations.get('require_certifications'):
        print(f"\n   ✅ Certificações exigidas:")
        for cert in validations.get('require_certifications', []):
            print(f"      - {cert}")

    # Alertas
    alerts = template.get('alerts', {})
    if alerts.get('critical_keywords'):
        print(f"\n⚠️  Palavras-chave críticas ({len(alerts.get('critical_keywords', []))}):")
        for kw in alerts.get('critical_keywords', [])[:5]:
            print(f"   - {kw}")
        if len(alerts.get('critical_keywords', [])) > 5:
            print(f"   ... e mais {len(alerts.get('critical_keywords', [])) - 5}")

    # Checks adicionais
    checks = template.get('additional_checks', [])
    if checks:
        print(f"\n📝 Verificações Adicionais ({len(checks)}):")
        for check in checks[:5]:
            print(f"   - {check.get('name')} ({check.get('importance', 'N/A')})")
        if len(checks) > 5:
            print(f"   ... e mais {len(checks) - 5}")

    # Metadados
    metadata = template.get('metadata', {})
    print(f"\n📊 Metadados")
    print(f"   Criado em: {metadata.get('created_at', 'N/A')}")
    print(f"   Atualizado em: {metadata.get('last_updated', 'N/A')}")
    print(f"   Uso: {metadata.get('use_count', 0)} vezes")

    print("\n" + "=" * 80 + "\n")


def cmd_create(args):
    """Cria novo template"""
    print("\n📝 CRIAR NOVO TEMPLATE")
    print("=" * 80)

    name = input("\nNome do template: ").strip()
    if not name:
        print("❌ Nome não pode ser vazio")
        sys.exit(1)

    description = input("Descrição: ").strip()
    category = input("Categoria (ti/obras/servicos/outro): ").strip().lower() or "outro"

    base = input("Template base (deixe vazio para criar do zero): ").strip()

    manager = TemplateManager()

    try:
        template_data = manager.create_custom_template(
            name=name,
            description=description,
            category=category,
            base_template=base if base else None
        )

        # Gerar nome de arquivo
        filename = name.lower().replace(" ", "_").replace("-", "_")
        saved_path = manager.save_template(filename, template_data)

        print(f"\n✅ Template criado com sucesso!")
        print(f"   📁 Arquivo: {saved_path}")
        print(f"\n💡 Edite o arquivo para customizar configurações.\n")

    except Exception as e:
        print(f"\n❌ Erro ao criar template: {e}\n")
        sys.exit(1)


def cmd_delete(args):
    """Deleta template"""
    if not args:
        print("\n❌ Erro: Nome do template não fornecido\n")
        print("Uso: template_manager.py delete <template_name>\n")
        sys.exit(1)

    template_name = args[0]

    print(f"\n⚠️  Você está prestes a deletar o template: {template_name}")
    response = input("Continuar? (s/n): ")

    if response.lower() != 's':
        print("\n⏸️  Operação cancelada.\n")
        return

    manager = TemplateManager()

    if manager.delete_template(template_name):
        print(f"\n✅ Template '{template_name}' removido com sucesso!\n")
    else:
        print(f"\n❌ Template '{template_name}' não encontrado.\n")
        sys.exit(1)


def cmd_help(args):
    """Exibe ajuda"""
    print("""
Template Manager - Gerenciamento de Templates de Análise

Uso:
    python scripts/template_manager.py <command> [args]

Comandos:
    list                  - Lista todos os templates
    show <name>           - Exibe detalhes de um template
    create                - Cria novo template (interativo)
    delete <name>         - Remove um template
    help                  - Exibe esta mensagem

Exemplos:
    python scripts/template_manager.py list
    python scripts/template_manager.py show ti_videomonitoramento
    python scripts/template_manager.py create
    python scripts/template_manager.py delete meu_template

Templates disponíveis por padrão:
    - ti_videomonitoramento.yaml
    - obras_engenharia.yaml
    - servicos_gerais.yaml
    """)


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
        'create': cmd_create,
        'delete': cmd_delete,
        'help': cmd_help,
        '--help': cmd_help,
        '-h': cmd_help,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"\n❌ Comando desconhecido: {command}\n")
        print("Use 'template_manager.py help' para ver comandos disponíveis.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
