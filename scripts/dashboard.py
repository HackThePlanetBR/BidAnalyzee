#!/usr/bin/env python3
"""
BidAnalyzee Dashboard - Métricas e Insights

Painel consolidado de estatísticas e visualizações de múltiplas análises
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import csv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.progress import BarColumn, Progress, TextColumn
    from rich import box
except ImportError:
    print("❌ Erro: rich library não instalada")
    print("Execute: pip install rich")
    sys.exit(1)

from agents.orchestrator.state import StateManager

console = Console()


class DashboardMetrics:
    """Calcula métricas para o dashboard"""

    def __init__(self):
        self.state_manager = StateManager()

    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """Retorna todas as análises com seus resultados"""
        sessions = self.state_manager.list_sessions()
        analyses = []

        for session_meta in sessions:
            session = self.state_manager.load_session(session_meta["session_id"])
            if not session or not session.data.analysis_result:
                continue

            # Carregar CSV de análise se existir
            csv_path = session.data.analysis_result.get("csv_path")
            if csv_path and Path(csv_path).exists():
                results = self._load_analysis_csv(csv_path)
                analyses.append({
                    "session_id": session.session_id,
                    "created_at": session.data.metadata.created_at,
                    "edital_name": session.data.edital_info.get("name", "N/A") if session.data.edital_info else "N/A",
                    "summary": session.data.analysis_result.get("summary", {}),
                    "results": results
                })

        return analyses

    def _load_analysis_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Carrega resultados de um CSV de análise"""
        results = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    results.append(row)
        except Exception as e:
            console.print(f"[yellow]⚠️  Erro ao ler {csv_path}: {e}[/yellow]")

        return results

    def calculate_global_metrics(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas globais de todas as análises"""
        if not analyses:
            return {}

        total_editais = len(analyses)
        total_requisitos = 0
        total_conforme = 0
        total_nao_conforme = 0
        total_parcial = 0
        total_requer_analise = 0

        for analysis in analyses:
            summary = analysis.get("summary", {})
            total_requisitos += summary.get("total", 0)
            total_conforme += summary.get("conforme", 0)
            total_nao_conforme += summary.get("nao_conforme", 0)
            total_parcial += summary.get("parcial", 0)
            total_requer_analise += summary.get("requer_analise", 0)

        return {
            "total_editais": total_editais,
            "total_requisitos": total_requisitos,
            "total_conforme": total_conforme,
            "total_nao_conforme": total_nao_conforme,
            "total_parcial": total_parcial,
            "total_requer_analise": total_requer_analise,
            "media_requisitos_por_edital": total_requisitos / total_editais if total_editais > 0 else 0,
            "taxa_conformidade": (total_conforme / total_requisitos * 100) if total_requisitos > 0 else 0
        }

    def get_category_stats(self, analyses: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Estatísticas por categoria"""
        category_stats = {}

        for analysis in analyses:
            for result in analysis.get("results", []):
                categoria = result.get("categoria", "Outros")
                veredicto = result.get("veredicto", "unknown")

                if categoria not in category_stats:
                    category_stats[categoria] = {
                        "total": 0,
                        "conforme": 0,
                        "nao_conforme": 0,
                        "parcial": 0,
                        "requer_analise": 0
                    }

                category_stats[categoria]["total"] += 1

                if "CONFORME" in veredicto.upper() and "NÃO" not in veredicto.upper() and "PARCIAL" not in veredicto.upper():
                    category_stats[categoria]["conforme"] += 1
                elif "NÃO CONFORME" in veredicto.upper():
                    category_stats[categoria]["nao_conforme"] += 1
                elif "PARCIAL" in veredicto.upper():
                    category_stats[categoria]["parcial"] += 1
                elif "REQUER" in veredicto.upper():
                    category_stats[categoria]["requer_analise"] += 1

        return category_stats

    def get_timeline_data(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Dados de timeline (análises ao longo do tempo)"""
        timeline = []

        for analysis in sorted(analyses, key=lambda a: a["created_at"]):
            created_dt = datetime.fromisoformat(analysis["created_at"])
            summary = analysis.get("summary", {})

            total = summary.get("total", 0)
            conforme = summary.get("conforme", 0)

            timeline.append({
                "date": created_dt.strftime("%d/%m"),
                "edital": analysis["edital_name"][:30],
                "total": total,
                "conforme": conforme,
                "taxa_conformidade": (conforme / total * 100) if total > 0 else 0
            })

        return timeline


def render_header() -> Panel:
    """Renderiza cabeçalho"""
    return Panel(
        "[bold blue]📊 BidAnalyzee - Dashboard de Métricas[/bold blue]\n"
        "[dim]Análise consolidada de múltiplas licitações[/dim]",
        box=box.DOUBLE,
        style="blue"
    )


def render_global_stats(metrics: Dict[str, Any]) -> Table:
    """Renderiza estatísticas globais"""
    table = Table(title="📈 Estatísticas Globais", box=box.ROUNDED)

    table.add_column("Métrica", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta", justify="right")

    table.add_row("Total de Editais Analisados", str(metrics.get("total_editais", 0)))
    table.add_row("Total de Requisitos", str(metrics.get("total_requisitos", 0)))
    table.add_row("Média Requisitos/Edital", f"{metrics.get('media_requisitos_por_edital', 0):.1f}")
    table.add_row("─" * 30, "─" * 10)
    table.add_row("[green]✅ Conformes[/green]", f"[green]{metrics.get('total_conforme', 0)}[/green]")
    table.add_row("[red]❌ Não Conformes[/red]", f"[red]{metrics.get('total_nao_conforme', 0)}[/red]")
    table.add_row("[yellow]⚠️  Parcialmente Conformes[/yellow]", f"[yellow]{metrics.get('total_parcial', 0)}[/yellow]")
    table.add_row("[blue]🔍 Requer Análise[/blue]", f"[blue]{metrics.get('total_requer_analise', 0)}[/blue]")
    table.add_row("─" * 30, "─" * 10)
    table.add_row("[bold]Taxa de Conformidade[/bold]", f"[bold]{metrics.get('taxa_conformidade', 0):.1f}%[/bold]")

    return table


def render_conformity_chart(metrics: Dict[str, Any]) -> Panel:
    """Renderiza gráfico de conformidade (ASCII bar chart)"""
    total = metrics.get("total_requisitos", 0)
    if total == 0:
        return Panel("[dim]Sem dados[/dim]", title="📊 Distribuição de Conformidade")

    conforme = metrics.get("total_conforme", 0)
    nao_conforme = metrics.get("total_nao_conforme", 0)
    parcial = metrics.get("total_parcial", 0)
    requer = metrics.get("total_requer_analise", 0)

    max_width = 50

    def bar(value, total, max_width):
        width = int((value / total) * max_width) if total > 0 else 0
        return "█" * width

    chart = f"""[green]✅ Conformes        [{conforme:4d}] {bar(conforme, total, max_width)} {conforme/total*100:.1f}%[/green]
[red]❌ Não Conformes   [{nao_conforme:4d}] {bar(nao_conforme, total, max_width)} {nao_conforme/total*100:.1f}%[/red]
[yellow]⚠️  Parciais        [{parcial:4d}] {bar(parcial, total, max_width)} {parcial/total*100:.1f}%[/yellow]
[blue]🔍 Requer Análise  [{requer:4d}] {bar(requer, total, max_width)} {requer/total*100:.1f}%[/blue]"""

    return Panel(chart, title="📊 Distribuição de Conformidade", box=box.ROUNDED)


def render_category_stats(category_stats: Dict[str, Dict[str, int]]) -> Table:
    """Renderiza estatísticas por categoria"""
    table = Table(title="📋 Top 10 Categorias (por volume)", box=box.ROUNDED, show_lines=True)

    table.add_column("Categoria", style="cyan", no_wrap=True)
    table.add_column("Total", justify="right")
    table.add_column("✅", justify="right", style="green")
    table.add_column("❌", justify="right", style="red")
    table.add_column("⚠️ ", justify="right", style="yellow")
    table.add_column("Taxa", justify="right")

    # Ordenar por total
    sorted_cats = sorted(category_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:10]

    for categoria, stats in sorted_cats:
        total = stats["total"]
        conforme = stats["conforme"]
        nao_conforme = stats["nao_conforme"]
        parcial = stats["parcial"]
        taxa = (conforme / total * 100) if total > 0 else 0

        table.add_row(
            categoria[:30],
            str(total),
            str(conforme),
            str(nao_conforme),
            str(parcial),
            f"{taxa:.1f}%"
        )

    return table


def render_problem_areas(category_stats: Dict[str, Dict[str, int]]) -> Table:
    """Renderiza áreas problemáticas"""
    table = Table(title="⚠️  Top 5 Áreas Problemáticas (maior taxa de não conformidade)", box=box.ROUNDED)

    table.add_column("Categoria", style="red")
    table.add_column("Não Conformes", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Taxa NC", justify="right", style="red bold")

    # Calcular taxa de não conformidade
    problem_areas = []
    for categoria, stats in category_stats.items():
        total = stats["total"]
        nao_conforme = stats["nao_conforme"]
        if total >= 3:  # Mínimo 3 requisitos para considerar
            taxa_nc = (nao_conforme / total * 100) if total > 0 else 0
            problem_areas.append((categoria, nao_conforme, total, taxa_nc))

    # Ordenar por taxa de não conformidade
    problem_areas.sort(key=lambda x: x[3], reverse=True)

    for categoria, nc, total, taxa in problem_areas[:5]:
        table.add_row(
            categoria[:40],
            str(nc),
            str(total),
            f"{taxa:.1f}%"
        )

    return table


def render_timeline(timeline_data: List[Dict[str, Any]]) -> Table:
    """Renderiza timeline de análises"""
    table = Table(title="📅 Timeline de Análises", box=box.ROUNDED)

    table.add_column("Data", style="cyan")
    table.add_column("Edital", style="white")
    table.add_column("Requisitos", justify="right")
    table.add_column("Conformes", justify="right", style="green")
    table.add_column("Taxa", justify="right")

    for item in timeline_data[-10:]:  # Últimas 10
        table.add_row(
            item["date"],
            item["edital"],
            str(item["total"]),
            str(item["conforme"]),
            f"{item['taxa_conformidade']:.1f}%"
        )

    return table


def main():
    """Entry point"""
    console.clear()
    console.print(render_header())

    # Carregar dados
    with console.status("[bold green]Carregando dados de análises...", spinner="dots"):
        metrics_calc = DashboardMetrics()
        analyses = metrics_calc.get_all_analyses()

    if not analyses:
        console.print("\n[yellow]📭 Nenhuma análise encontrada.[/yellow]")
        console.print("\n💡 Execute análises de editais primeiro.\n")
        sys.exit(0)

    # Calcular métricas
    global_metrics = metrics_calc.calculate_global_metrics(analyses)
    category_stats = metrics_calc.get_category_stats(analyses)
    timeline_data = metrics_calc.get_timeline_data(analyses)

    # Renderizar dashboard
    console.print()
    console.print(render_global_stats(global_metrics))
    console.print()
    console.print(render_conformity_chart(global_metrics))
    console.print()
    console.print(render_category_stats(category_stats))
    console.print()
    console.print(render_problem_areas(category_stats))
    console.print()
    console.print(render_timeline(timeline_data))
    console.print()

    # Footer
    console.print(Panel(
        f"[dim]Dashboard gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}[/dim]\n"
        f"[dim]Total de {len(analyses)} análises processadas[/dim]",
        box=box.ROUNDED,
        style="dim"
    ))


if __name__ == "__main__":
    main()
