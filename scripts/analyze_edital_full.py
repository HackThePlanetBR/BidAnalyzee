#!/usr/bin/env python3
"""
BidAnalyzee - FLOW Mode (Modo Automático)
/analyze-edital-full <pdf>

Executa workflow completo de análise de edital em modo automático:
1. Extração de requisitos (Document Structurer)
2. Análise de conformidade (Technical Analyst)
3. Geração de relatórios (PDF + Excel)

Pausas apenas em erros críticos ou decisões importantes.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.state import StateManager, Session


class WorkflowExecutor:
    """Executa workflow completo em modo FLOW"""

    def __init__(self, pdf_path: str, session_id: Optional[str] = None):
        self.pdf_path = Path(pdf_path).resolve()
        self.project_root = Path(__file__).parent.parent
        self.state_manager = StateManager()
        self.session_id = session_id or f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session = None
        self.errors: List[str] = []

    def print_header(self):
        """Exibe cabeçalho do FLOW mode"""
        print("\n" + "=" * 80)
        print("🚀 BidAnalyzee - FLOW MODE (Análise Automática)")
        print("=" * 80)
        print(f"\n📄 Edital: {self.pdf_path.name}")
        print(f"🆔 Sessão: {self.session_id}")
        print(f"⏱️  Iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("\n" + "=" * 80 + "\n")

    def print_stage(self, stage: str, description: str):
        """Exibe informações de um estágio"""
        print(f"\n{'─' * 80}")
        print(f"📍 ESTÁGIO: {stage}")
        print(f"📝 {description}")
        print(f"{'─' * 80}\n")

    def print_progress(self, message: str, emoji: str = "⏳"):
        """Exibe mensagem de progresso"""
        print(f"{emoji} {message}")

    def print_success(self, message: str):
        """Exibe mensagem de sucesso"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Exibe mensagem de erro"""
        print(f"❌ ERRO: {message}")
        self.errors.append(message)

    def print_warning(self, message: str):
        """Exibe mensagem de aviso"""
        print(f"⚠️  AVISO: {message}")

    def create_session(self):
        """Cria sessão de análise"""
        self.print_stage("INICIALIZAÇÃO", "Criando sessão de análise")

        try:
            self.session = self.state_manager.create_session(self.session_id)
            self.session.set_edital_info(
                str(self.pdf_path),
                self.pdf_path.stem
            )
            self.session.update_stage("extracting")
            self.state_manager.save_session(self.session)

            self.print_success(f"Sessão criada: {self.session_id}")
            return True

        except Exception as e:
            self.print_error(f"Falha ao criar sessão: {e}")
            return False

    def validate_pdf(self) -> bool:
        """Valida PDF antes de processar"""
        self.print_progress("Validando PDF...", "🔍")

        if not self.pdf_path.exists():
            self.print_error(f"PDF não encontrado: {self.pdf_path}")
            return False

        if self.pdf_path.suffix.lower() != '.pdf':
            self.print_error(f"Arquivo não é PDF: {self.pdf_path}")
            return False

        # Validar usando script existente
        validate_script = self.project_root / "scripts" / "validate_pdf.py"
        if validate_script.exists():
            try:
                result = subprocess.run(
                    ["python3", str(validate_script), str(self.pdf_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.print_success("PDF válido")
                    return True
                else:
                    self.print_error(f"PDF inválido: {result.stderr}")
                    return False

            except Exception as e:
                self.print_warning(f"Validação automática falhou: {e}")
                # Continuar mesmo assim

        self.print_success("PDF aceito (validação simplificada)")
        return True

    def extract_requirements(self) -> Optional[Path]:
        """Executa Document Structurer (Fase 1)"""
        self.print_stage(
            "FASE 1: EXTRAÇÃO DE REQUISITOS",
            "Document Structurer extraindo requisitos do PDF"
        )

        try:
            # Executar comando de estruturação
            self.print_progress("Iniciando extração de requisitos...")

            # O comando /structure-edital seria executado aqui
            # Por enquanto, vamos simular com chamada direta ao script

            # Caminho esperado do CSV de saída
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = self.project_root / "data" / "deliveries" / f"{self.pdf_path.stem}_{timestamp}"
            csv_path = output_dir / "requirements_structured.csv"

            self.print_progress(f"Output esperado: {csv_path}")

            # Aqui normalmente executaríamos o Document Structurer
            # Como não temos o comando direto, vamos indicar ao usuário
            print("\n⚠️  CHECKPOINT CRÍTICO: Extração de Requisitos")
            print("=" * 80)
            print("O Document Structurer precisa ser executado manualmente:")
            print(f"\nComando: /structure-edital {self.pdf_path}")
            print(f"\nAguardando execução...")
            print("\nPressione ENTER após a extração estar completa...")
            print("(ou digite 'skip' para pular esta fase)")
            print("=" * 80)

            response = input("\n> ").strip().lower()

            if response == 'skip':
                self.print_warning("Fase de extração pulada")
                return None

            # Perguntar pelo caminho do CSV gerado
            print("\nDigite o caminho do CSV gerado:")
            csv_input = input("> ").strip()

            if csv_input:
                csv_path = Path(csv_input)
                if csv_path.exists():
                    self.session.set_extraction_result(str(csv_path), 0)
                    self.state_manager.save_session(self.session)
                    self.print_success(f"CSV de requisitos: {csv_path}")
                    return csv_path
                else:
                    self.print_error(f"CSV não encontrado: {csv_path}")
                    return None

            return None

        except Exception as e:
            self.print_error(f"Erro na extração: {e}")
            self.session.add_error(f"Extraction failed: {e}")
            self.state_manager.save_session(self.session)
            return None

    def analyze_conformity(self, csv_path: Path) -> Optional[Path]:
        """Executa Technical Analyst (Fase 2)"""
        self.print_stage(
            "FASE 2: ANÁLISE DE CONFORMIDADE",
            "Technical Analyst analisando requisitos"
        )

        try:
            self.session.update_stage("analyzing")
            self.state_manager.save_session(self.session)

            self.print_progress("Iniciando análise de conformidade...")

            # Caminho esperado do CSV de análise
            analysis_csv = csv_path.parent / "analysis_results.csv"

            print("\n⚠️  CHECKPOINT CRÍTICO: Análise de Conformidade")
            print("=" * 80)
            print("O Technical Analyst precisa ser executado manualmente:")
            print(f"\nComando: /analyze-edital {csv_path}")
            print(f"\nAguardando execução...")
            print("\nPressione ENTER após a análise estar completa...")
            print("(ou digite 'skip' para pular esta fase)")
            print("=" * 80)

            response = input("\n> ").strip().lower()

            if response == 'skip':
                self.print_warning("Fase de análise pulada")
                return None

            # Perguntar pelo caminho do CSV de análise
            print("\nDigite o caminho do CSV de análise gerado:")
            csv_input = input("> ").strip()

            if csv_input:
                analysis_csv = Path(csv_input)
                if analysis_csv.exists():
                    self.session.set_analysis_result(
                        str(analysis_csv),
                        {"status": "completed"}
                    )
                    self.state_manager.save_session(self.session)
                    self.print_success(f"CSV de análise: {analysis_csv}")
                    return analysis_csv
                else:
                    self.print_error(f"CSV não encontrado: {analysis_csv}")
                    return None

            return None

        except Exception as e:
            self.print_error(f"Erro na análise: {e}")
            self.session.add_error(f"Analysis failed: {e}")
            self.state_manager.save_session(self.session)
            return None

    def generate_reports(self, analysis_csv: Path) -> Dict[str, Path]:
        """Gera relatórios PDF e Excel (Fase 3)"""
        self.print_stage(
            "FASE 3: GERAÇÃO DE RELATÓRIOS",
            "Gerando relatórios profissionais (PDF + Excel)"
        )

        try:
            self.session.update_stage("completed")

            reports = {}

            # PDF report (será implementado em D.2.1)
            self.print_progress("Gerando relatório PDF...")
            self.print_warning("Geração de PDF ainda não implementada (Sprint 10 - D.2.1)")

            # Excel report (será implementado em D.2.2)
            self.print_progress("Gerando relatório Excel...")
            self.print_warning("Geração de Excel ainda não implementada (Sprint 10 - D.2.2)")

            self.session.update_status("completed")
            self.state_manager.save_session(self.session)

            return reports

        except Exception as e:
            self.print_error(f"Erro na geração de relatórios: {e}")
            return {}

    def print_summary(self, start_time: float):
        """Exibe resumo da execução"""
        duration = time.time() - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        print("\n" + "=" * 80)
        print("📊 RESUMO DA EXECUÇÃO")
        print("=" * 80)
        print(f"\n🆔 Sessão: {self.session_id}")
        print(f"⏱️  Duração: {minutes}min {seconds}s")
        print(f"📄 Edital: {self.pdf_path.name}")

        if self.session:
            print(f"📊 Status: {self.session.data.metadata.status}")
            print(f"🔄 Estágio: {self.session.data.metadata.workflow_stage}")

        if self.errors:
            print(f"\n❌ Erros encontrados: {len(self.errors)}")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        else:
            print("\n✅ Execução sem erros")

        print("\n💡 Para ver detalhes da sessão:")
        print(f"   python3 scripts/orchestrator_session.py {self.session_id}")

        print("\n" + "=" * 80 + "\n")

    def run(self) -> bool:
        """Executa workflow completo"""
        start_time = time.time()

        self.print_header()

        # Fase 0: Inicialização
        if not self.create_session():
            return False

        # Validação de PDF
        if not self.validate_pdf():
            return False

        # Fase 1: Extração
        csv_path = self.extract_requirements()
        if not csv_path:
            self.print_error("Extração de requisitos falhou ou foi pulada")
            self.print_summary(start_time)
            return False

        # Fase 2: Análise
        analysis_csv = self.analyze_conformity(csv_path)
        if not analysis_csv:
            self.print_error("Análise de conformidade falhou ou foi pulada")
            self.print_summary(start_time)
            return False

        # Fase 3: Relatórios
        reports = self.generate_reports(analysis_csv)

        # Resumo final
        self.print_summary(start_time)

        return True


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Uso incorreto\n")
        print("Uso: python3 scripts/analyze_edital_full.py <pdf_path>")
        print("\nExemplo:")
        print("   python3 scripts/analyze_edital_full.py data/uploads/edital_001.pdf")
        print("\nEste comando executa o workflow completo:")
        print("   1. Extração de requisitos")
        print("   2. Análise de conformidade")
        print("   3. Geração de relatórios (PDF + Excel)")
        print("\nModo: FLOW (automático com checkpoints)")
        print()
        sys.exit(1)

    pdf_path = sys.argv[1]

    executor = WorkflowExecutor(pdf_path)
    success = executor.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
