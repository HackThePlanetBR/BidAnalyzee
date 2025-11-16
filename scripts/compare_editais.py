#!/usr/bin/env python3
"""
Edital Comparison Tool - Compara requisitos de múltiplos editais

Identifica:
- Requisitos únicos a cada edital
- Requisitos comuns entre editais
- Requisitos similares mas divergentes

Gera relatório detalhado de diferenças críticas
"""

import sys
import csv
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from difflib import SequenceMatcher
import json


@dataclass
class Requirement:
    """Representa um requisito de edital"""
    id: str
    item: str
    descricao: str
    categoria: str
    prioridade: str
    pagina: str
    confianca: str
    source_edital: str  # Nome do edital de origem


class EditalComparator:
    """Compara requisitos de múltiplos editais"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Args:
            similarity_threshold: Limiar de similaridade para considerar requisitos similares
        """
        self.similarity_threshold = similarity_threshold
        self.editais: Dict[str, List[Requirement]] = {}

    def load_edital(self, csv_path: str, edital_name: str = None) -> int:
        """
        Carrega requisitos de um edital

        Args:
            csv_path: Caminho do CSV de requisitos
            edital_name: Nome identificador do edital (usa nome do arquivo se None)

        Returns:
            Número de requisitos carregados
        """
        csv_file = Path(csv_path)

        if not csv_file.exists():
            raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

        if edital_name is None:
            edital_name = csv_file.stem

        requirements = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                req = Requirement(
                    id=row.get('id', row.get('ID', '')),
                    item=row.get('item', row.get('Item', '')),
                    descricao=row.get('descricao', row.get('Descrição', row.get('Descri\xe7\xe3o', ''))),
                    categoria=row.get('categoria', row.get('Categoria', '')),
                    prioridade=row.get('prioridade', row.get('Prioridade', '')),
                    pagina=row.get('pagina', row.get('Página', row.get('P\xe1gina', ''))),
                    confianca=row.get('confianca', row.get('Confiança', row.get('Confian\xe7a', ''))),
                    source_edital=edital_name
                )
                requirements.append(req)

        self.editais[edital_name] = requirements

        return len(requirements)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos (0.0-1.0)

        Args:
            text1: Primeiro texto
            text2: Segundo texto

        Returns:
            Score de similaridade (0.0 = diferente, 1.0 = idêntico)
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def find_exact_matches(self, edital1: str, edital2: str) -> List[Tuple[Requirement, Requirement]]:
        """
        Encontra requisitos exatamente iguais entre dois editais

        Args:
            edital1: Nome do primeiro edital
            edital2: Nome do segundo edital

        Returns:
            Lista de pares (req_edital1, req_edital2) que são exatamente iguais
        """
        exact_matches = []

        reqs1 = self.editais[edital1]
        reqs2 = self.editais[edital2]

        for r1 in reqs1:
            for r2 in reqs2:
                if r1.descricao.strip().lower() == r2.descricao.strip().lower():
                    exact_matches.append((r1, r2))

        return exact_matches

    def find_similar_matches(self, edital1: str, edital2: str) -> List[Tuple[Requirement, Requirement, float]]:
        """
        Encontra requisitos similares (mas não exatamente iguais) entre dois editais

        Args:
            edital1: Nome do primeiro edital
            edital2: Nome do segundo edital

        Returns:
            Lista de triplas (req_edital1, req_edital2, similarity_score)
        """
        similar_matches = []

        reqs1 = self.editais[edital1]
        reqs2 = self.editais[edital2]

        # Requisitos já matchados exatamente (para evitar duplicar)
        exact_set1 = set()
        exact_set2 = set()

        exact_matches = self.find_exact_matches(edital1, edital2)
        for r1, r2 in exact_matches:
            exact_set1.add(r1.id)
            exact_set2.add(r2.id)

        # Procurar requisitos similares
        for r1 in reqs1:
            if r1.id in exact_set1:
                continue  # Já tem match exato

            for r2 in reqs2:
                if r2.id in exact_set2:
                    continue  # Já tem match exato

                similarity = self.calculate_similarity(r1.descricao, r2.descricao)

                if similarity >= self.similarity_threshold:
                    similar_matches.append((r1, r2, similarity))

        # Ordenar por similaridade (maior primeiro)
        similar_matches.sort(key=lambda x: x[2], reverse=True)

        return similar_matches

    def find_unique_requirements(self, edital: str, other_editais: List[str]) -> List[Requirement]:
        """
        Encontra requisitos únicos a um edital (não presentes nos outros)

        Args:
            edital: Nome do edital
            other_editais: Lista de nomes dos outros editais para comparar

        Returns:
            Lista de requisitos únicos ao edital
        """
        unique = []
        reqs_edital = self.editais[edital]

        for req in reqs_edital:
            is_unique = True

            for other_edital in other_editais:
                reqs_other = self.editais[other_edital]

                # Verificar se tem match exato ou similar
                for req_other in reqs_other:
                    similarity = self.calculate_similarity(req.descricao, req_other.descricao)

                    if similarity >= self.similarity_threshold:
                        is_unique = False
                        break

                if not is_unique:
                    break

            if is_unique:
                unique.append(req)

        return unique

    def compare_two_editais(self, edital1: str, edital2: str) -> Dict[str, Any]:
        """
        Compara dois editais e retorna relatório detalhado

        Args:
            edital1: Nome do primeiro edital
            edital2: Nome do segundo edital

        Returns:
            Dicionário com resultados da comparação
        """
        exact_matches = self.find_exact_matches(edital1, edital2)
        similar_matches = self.find_similar_matches(edital1, edital2)

        unique_to_1 = self.find_unique_requirements(edital1, [edital2])
        unique_to_2 = self.find_unique_requirements(edital2, [edital1])

        total_reqs_1 = len(self.editais[edital1])
        total_reqs_2 = len(self.editais[edital2])

        common_count = len(exact_matches) + len(similar_matches)
        common_pct_1 = (common_count / total_reqs_1 * 100) if total_reqs_1 > 0 else 0
        common_pct_2 = (common_count / total_reqs_2 * 100) if total_reqs_2 > 0 else 0

        return {
            "edital1": edital1,
            "edital2": edital2,
            "total_requirements": {
                edital1: total_reqs_1,
                edital2: total_reqs_2
            },
            "exact_matches": {
                "count": len(exact_matches),
                "items": exact_matches
            },
            "similar_matches": {
                "count": len(similar_matches),
                "items": similar_matches
            },
            "unique_to_edital1": {
                "count": len(unique_to_1),
                "items": unique_to_1
            },
            "unique_to_edital2": {
                "count": len(unique_to_2),
                "items": unique_to_2
            },
            "overlap_percentage": {
                edital1: round(common_pct_1, 1),
                edital2: round(common_pct_2, 1)
            }
        }

    def compare_multiple_editais(self) -> Dict[str, Any]:
        """
        Compara todos os editais carregados (N editais)

        Returns:
            Dicionário com resultados da comparação múltipla
        """
        edital_names = list(self.editais.keys())

        if len(edital_names) < 2:
            raise ValueError("Necessário pelo menos 2 editais para comparar")

        # Comparações par a par
        pairwise_comparisons = []

        for i in range(len(edital_names)):
            for j in range(i + 1, len(edital_names)):
                comparison = self.compare_two_editais(edital_names[i], edital_names[j])
                pairwise_comparisons.append(comparison)

        # Requisitos comuns a TODOS os editais
        common_to_all = self._find_common_to_all(edital_names)

        # Requisitos únicos a cada edital
        unique_per_edital = {}
        for edital_name in edital_names:
            others = [e for e in edital_names if e != edital_name]
            unique = self.find_unique_requirements(edital_name, others)
            unique_per_edital[edital_name] = unique

        return {
            "editais": edital_names,
            "total_editais": len(edital_names),
            "pairwise_comparisons": pairwise_comparisons,
            "common_to_all": {
                "count": len(common_to_all),
                "items": common_to_all
            },
            "unique_per_edital": {
                edital: {"count": len(reqs), "items": reqs}
                for edital, reqs in unique_per_edital.items()
            }
        }

    def _find_common_to_all(self, edital_names: List[str]) -> List[Dict[str, Any]]:
        """
        Encontra requisitos presentes em TODOS os editais

        Args:
            edital_names: Lista de nomes dos editais

        Returns:
            Lista de requisitos comuns
        """
        if len(edital_names) == 0:
            return []

        # Usar primeiro edital como base
        base_edital = edital_names[0]
        common_reqs = []

        for req_base in self.editais[base_edital]:
            # Verificar se este requisito tem match em TODOS os outros editais
            has_match_in_all = True

            matches = {base_edital: req_base}

            for other_edital in edital_names[1:]:
                found_match = False

                for req_other in self.editais[other_edital]:
                    similarity = self.calculate_similarity(req_base.descricao, req_other.descricao)

                    if similarity >= self.similarity_threshold:
                        matches[other_edital] = req_other
                        found_match = True
                        break

                if not found_match:
                    has_match_in_all = False
                    break

            if has_match_in_all:
                common_reqs.append({
                    "descricao": req_base.descricao,
                    "categoria": req_base.categoria,
                    "prioridade": req_base.prioridade,
                    "occurrences": matches
                })

        return common_reqs


def print_comparison_report(comparison: Dict[str, Any], output_format: str = "text"):
    """
    Imprime relatório de comparação formatado

    Args:
        comparison: Resultado da comparação
        output_format: Formato de saída ('text' ou 'json')
    """
    if output_format == "json":
        # JSON output
        print(json.dumps(comparison, indent=2, ensure_ascii=False, default=str))
        return

    # Text output
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO DE COMPARAÇÃO DE EDITAIS")
    print("=" * 80)

    if "edital1" in comparison:
        # Comparação de 2 editais
        _print_two_edital_comparison(comparison)
    else:
        # Comparação de N editais
        _print_multiple_edital_comparison(comparison)


def _print_two_edital_comparison(comparison: Dict[str, Any]):
    """Imprime comparação de 2 editais"""
    edital1 = comparison["edital1"]
    edital2 = comparison["edital2"]

    print(f"\n📄 Editais Comparados:")
    print(f"   • {edital1} ({comparison['total_requirements'][edital1]} requisitos)")
    print(f"   • {edital2} ({comparison['total_requirements'][edital2]} requisitos)")

    print(f"\n📊 Resumo da Comparação:")
    print(f"   ✅ Requisitos idênticos: {comparison['exact_matches']['count']}")
    print(f"   ⚠️  Requisitos similares: {comparison['similar_matches']['count']}")
    print(f"   🔵 Únicos ao {edital1}: {comparison['unique_to_edital1']['count']}")
    print(f"   🔴 Únicos ao {edital2}: {comparison['unique_to_edital2']['count']}")

    print(f"\n📈 Taxa de Sobreposição:")
    print(f"   • {edital1}: {comparison['overlap_percentage'][edital1]}%")
    print(f"   • {edital2}: {comparison['overlap_percentage'][edital2]}%")

    # Detalhes de requisitos similares (top 5)
    if comparison['similar_matches']['count'] > 0:
        print(f"\n⚠️  Requisitos Similares mas Divergentes (Top 5):")
        for i, (r1, r2, sim) in enumerate(comparison['similar_matches']['items'][:5], 1):
            print(f"\n   {i}. Similaridade: {sim:.1%}")
            print(f"      [{edital1}] {r1.descricao[:70]}...")
            print(f"      [{edital2}] {r2.descricao[:70]}...")

    # Requisitos críticos únicos (Alta prioridade)
    unique_1_high = [r for r in comparison['unique_to_edital1']['items'] if r.prioridade == "Alta"]
    unique_2_high = [r for r in comparison['unique_to_edital2']['items'] if r.prioridade == "Alta"]

    if unique_1_high:
        print(f"\n⚡ Requisitos de Alta Prioridade Únicos ao {edital1}:")
        for req in unique_1_high[:5]:
            print(f"   • {req.item}: {req.descricao[:60]}...")

    if unique_2_high:
        print(f"\n⚡ Requisitos de Alta Prioridade Únicos ao {edital2}:")
        for req in unique_2_high[:5]:
            print(f"   • {req.item}: {req.descricao[:60]}...")

    print("\n" + "=" * 80 + "\n")


def _print_multiple_edital_comparison(comparison: Dict[str, Any]):
    """Imprime comparação de N editais"""
    print(f"\n📄 Editais Comparados ({comparison['total_editais']}):")
    for edital in comparison['editais']:
        print(f"   • {edital}")

    print(f"\n✅ Requisitos Comuns a TODOS os Editais: {comparison['common_to_all']['count']}")

    if comparison['common_to_all']['count'] > 0:
        print("\n   Exemplos (Top 5):")
        for i, req in enumerate(comparison['common_to_all']['items'][:5], 1):
            print(f"   {i}. {req['descricao'][:70]}...")

    print(f"\n🔍 Requisitos Únicos por Edital:")
    for edital, data in comparison['unique_per_edital'].items():
        print(f"   • {edital}: {data['count']} requisitos únicos")

    print(f"\n📊 Comparações Par a Par:")
    for comp in comparison['pairwise_comparisons']:
        e1 = comp['edital1']
        e2 = comp['edital2']
        overlap = comp['overlap_percentage'][e1]
        print(f"   • {e1} vs {e2}: {overlap}% de sobreposição")

    print("\n" + "=" * 80 + "\n")


def main():
    """Entry point"""
    if len(sys.argv) < 3:
        print("\n❌ Erro: Necessário pelo menos 2 editais (CSVs de requisitos)\n")
        print("Uso: python scripts/compare_editais.py <edital1.csv> <edital2.csv> [edital3.csv ...]\n")
        print("Opções:")
        print("  --json           Saída em formato JSON")
        print("  --similarity N   Threshold de similaridade (0.0-1.0, padrão: 0.85)\n")
        print("Exemplo:")
        print("  python scripts/compare_editais.py edital_A.csv edital_B.csv")
        print("  python scripts/compare_editais.py edital_*.csv --json")
        print("  python scripts/compare_editais.py edital_A.csv edital_B.csv --similarity 0.90\n")
        sys.exit(1)

    # Parse arguments
    csv_files = []
    output_format = "text"
    similarity_threshold = 0.85

    for arg in sys.argv[1:]:
        if arg == "--json":
            output_format = "json"
        elif arg.startswith("--similarity"):
            # Next arg is the threshold
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                try:
                    similarity_threshold = float(sys.argv[idx + 1])
                except ValueError:
                    print(f"❌ Erro: Threshold de similaridade inválido: {sys.argv[idx + 1]}")
                    sys.exit(1)
        elif arg.endswith(".csv"):
            csv_files.append(arg)

    if len(csv_files) < 2:
        print("❌ Erro: Necessário pelo menos 2 arquivos CSV")
        sys.exit(1)

    # Initialize comparator
    comparator = EditalComparator(similarity_threshold=similarity_threshold)

    # Load editais
    print(f"\n🔍 Carregando {len(csv_files)} editais...\n")

    for csv_file in csv_files:
        try:
            count = comparator.load_edital(csv_file)
            edital_name = Path(csv_file).stem
            print(f"   ✅ {edital_name}: {count} requisitos")
        except FileNotFoundError as e:
            print(f"   ❌ {csv_file}: não encontrado")
            sys.exit(1)
        except Exception as e:
            print(f"   ❌ {csv_file}: erro ao carregar: {e}")
            sys.exit(1)

    print()

    # Perform comparison
    if len(csv_files) == 2:
        # Comparação de 2 editais
        edital1 = Path(csv_files[0]).stem
        edital2 = Path(csv_files[1]).stem
        comparison = comparator.compare_two_editais(edital1, edital2)
    else:
        # Comparação de N editais
        comparison = comparator.compare_multiple_editais()

    # Print report
    print_comparison_report(comparison, output_format=output_format)


if __name__ == "__main__":
    main()
