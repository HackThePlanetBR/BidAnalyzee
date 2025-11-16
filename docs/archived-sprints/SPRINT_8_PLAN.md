# Sprint 8 Plan - Orchestrator Agent (Base)

**Data de Início:** 08 de novembro de 2025
**Duração Estimada:** 1-2 semanas (40-80 horas)
**Objetivo:** Implementar @Orquestrador para coordenar agentes e gerenciar workflows

---

## 🎯 Objetivo do Sprint

Implementar a **História 4.1 - Orquestrador Base**, criando o componente que:
1. Coordena Document Structurer e Technical Analyst
2. Gerencia estado do sistema e análises
3. Fornece comandos de sistema (`*ajuda`, `*listar_analises`)
4. Prepara base para Modos Assistido/FLOW (Sprints 9-10)

---

## 📋 Critérios de Aceitação

- [ ] Classe `Orchestrator` implementada
- [ ] Sistema de gestão de estado (análises, sessões)
- [ ] Comando `*ajuda` funcional (lista comandos disponíveis)
- [ ] Comando `*listar_analises` funcional (histórico)
- [ ] Integração com Document Structurer
- [ ] Integração com Technical Analyst
- [ ] Persistência de estado em arquivos JSON
- [ ] Navegação entre contextos de agentes
- [ ] Testes unitários (80%+ cobertura)
- [ ] Testes de integração
- [ ] Documentação completa

---

## 🏗️ Arquitetura

### Visão Geral

```
┌────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                        │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │         Command Router                           │ │
│  │  /analyze-edital | *ajuda | *listar_analises    │ │
│  └──────────────────────────────────────────────────┘ │
│                       │                                │
│                       ▼                                │
│  ┌──────────────────────────────────────────────────┐ │
│  │         State Manager                            │ │
│  │  - Analysis Sessions                             │ │
│  │  - Agent Contexts                                │ │
│  │  - Workflow Status                               │ │
│  └──────────────────────────────────────────────────┘ │
│                       │                                │
│         ┌─────────────┼─────────────┐                  │
│         ▼             ▼             ▼                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐            │
│  │ Document  │ │Technical  │ │  Report   │            │
│  │Structurer │ │ Analyst   │ │ Generator │            │
│  └───────────┘ └───────────┘ └───────────┘            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Componentes

```python
Orchestrator
├── orchestrator.py              # Classe principal
├── state_manager.py             # Gerenciamento de estado
├── command_router.py            # Roteamento de comandos
├── session.py                   # Sessões de análise
├── config.py                    # Configuração
└── __init__.py                  # Exports

Workflows (Sprint 9-10)
├── assisted_mode.py             # Modo Assistido (HALT)
├── flow_mode.py                 # Modo FLOW (automático)
└── quick_consult.py             # Consulta Rápida
```

---

## 📂 Estrutura de Dados

### Analysis Session

```python
{
    "session_id": "analysis_edital_001_20251108_143022",
    "status": "completed | in_progress | failed",
    "created_at": "2025-11-08T14:30:22Z",
    "updated_at": "2025-11-08T14:45:10Z",
    "edital_info": {
        "numero": "001/2024",
        "orgao": "Prefeitura Municipal",
        "pdf_path": "/path/to/edital.pdf"
    },
    "workflow": {
        "mode": "manual | assisted | flow",
        "current_stage": "extraction | analysis | reporting | completed",
        "stages_completed": ["extraction", "analysis"]
    },
    "results": {
        "document_structurer": {
            "status": "completed",
            "csv_path": "/path/to/requirements.csv",
            "total_requirements": 50,
            "timestamp": "2025-11-08T14:35:00Z"
        },
        "technical_analyst": {
            "status": "completed",
            "report_path": "/path/to/analysis.json",
            "conformity_rate": 0.70,
            "timestamp": "2025-11-08T14:45:00Z"
        }
    },
    "output_dir": "data/deliveries/analysis_edital_001_20251108_143022"
}
```

### State Directory Structure

```
data/
├── state/
│   ├── sessions/                    # Sessões de análise
│   │   ├── analysis_001.json
│   │   ├── analysis_002.json
│   │   └── ...
│   ├── index.json                   # Índice de todas as sessões
│   └── current_session.json         # Sessão atual (se houver)
├── deliveries/                      # Outputs por análise
│   ├── analysis_edital_001_20251108/
│   │   ├── inputs/
│   │   │   └── edital.pdf
│   │   ├── outputs/
│   │   │   ├── requirements.csv
│   │   │   ├── analysis.json
│   │   │   ├── analysis.csv
│   │   │   └── report.md
│   │   └── session.json
│   └── ...
└── knowledge_base/                  # Knowledge base (já existe)
```

---

## 💻 Implementação

### 1. Orchestrator (agents/orchestrator/orchestrator.py)

```python
"""
Orchestrator Agent - Main Coordinator

Responsible for:
- Coordinating Document Structurer and Technical Analyst
- Managing analysis sessions and state
- Routing commands
- Workflow orchestration (base for Sprints 9-10)
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json

from .state_manager import StateManager
from .session import AnalysisSession, SessionStatus
from .command_router import CommandRouter
from agents.document_structurer import DocumentStructurer
from agents.technical_analyst import AnalysisPipeline


class Orchestrator:
    """
    Main orchestrator for BidAnalyzee system

    Coordinates all agents and manages workflow execution.

    Example:
        >>> orchestrator = Orchestrator()
        >>> session = orchestrator.create_session("edital_001.pdf")
        >>> orchestrator.run_full_analysis(session.session_id)
    """

    def __init__(
        self,
        state_dir: str = "data/state",
        deliveries_dir: str = "data/deliveries"
    ):
        """
        Initialize Orchestrator

        Args:
            state_dir: Directory for state management
            deliveries_dir: Directory for analysis outputs
        """
        self.state_dir = Path(state_dir)
        self.deliveries_dir = Path(deliveries_dir)

        # Ensure directories exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.deliveries_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.state_manager = StateManager(self.state_dir)
        self.command_router = CommandRouter(self)

        # Initialize agents
        self.document_structurer = DocumentStructurer()
        self.analysis_pipeline = AnalysisPipeline()

    # ==================== Session Management ====================

    def create_session(
        self,
        pdf_path: str,
        edital_info: Optional[Dict[str, Any]] = None
    ) -> AnalysisSession:
        """
        Create new analysis session

        Args:
            pdf_path: Path to edital PDF
            edital_info: Optional edital metadata

        Returns:
            Created AnalysisSession
        """
        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        edital_name = Path(pdf_path).stem
        session_id = f"analysis_{edital_name}_{timestamp}"

        # Create session
        session = AnalysisSession(
            session_id=session_id,
            pdf_path=pdf_path,
            edital_info=edital_info or {},
            output_dir=str(self.deliveries_dir / session_id)
        )

        # Save session
        self.state_manager.save_session(session)

        return session

    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Get session by ID"""
        return self.state_manager.get_session(session_id)

    def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        limit: Optional[int] = None
    ) -> List[AnalysisSession]:
        """
        List analysis sessions

        Args:
            status: Filter by status (optional)
            limit: Maximum number of sessions to return

        Returns:
            List of sessions
        """
        return self.state_manager.list_sessions(status=status, limit=limit)

    # ==================== Workflow Execution ====================

    def run_full_analysis(
        self,
        session_id: str,
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete analysis workflow

        Steps:
        1. Document Structurer: Extract requirements
        2. Technical Analyst: Analyze conformity
        3. Report Generation: Multi-format reports

        Args:
            session_id: Session ID
            auto_confirm: Auto-confirm stages (for FLOW mode)

        Returns:
            Analysis results dictionary
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        print(f"\n{'='*70}")
        print(f"🚀 INICIANDO ANÁLISE COMPLETA")
        print(f"{'='*70}")
        print(f"📋 Sessão: {session_id}")
        print(f"📄 Edital: {session.pdf_path}")
        print(f"{'='*70}\n")

        try:
            # Update session status
            session.status = SessionStatus.IN_PROGRESS
            session.workflow['current_stage'] = 'extraction'
            self.state_manager.save_session(session)

            # Stage 1: Document Structurer
            print("📋 ETAPA 1/3: Extração de Requisitos")
            extraction_result = self._run_extraction(session)

            if not auto_confirm:
                confirm = input("\n✋ Continuar para análise de conformidade? (s/n): ")
                if confirm.lower() != 's':
                    print("⏸️  Análise pausada pelo usuário")
                    session.status = SessionStatus.IN_PROGRESS
                    self.state_manager.save_session(session)
                    return {"status": "paused", "session_id": session_id}

            # Stage 2: Technical Analyst
            session.workflow['current_stage'] = 'analysis'
            session.workflow['stages_completed'].append('extraction')
            self.state_manager.save_session(session)

            print("\n🔍 ETAPA 2/3: Análise de Conformidade")
            analysis_result = self._run_analysis(session, extraction_result)

            # Stage 3: Report Generation (já incluído no AnalysisPipeline)
            session.workflow['current_stage'] = 'completed'
            session.workflow['stages_completed'].extend(['analysis', 'reporting'])
            session.status = SessionStatus.COMPLETED
            self.state_manager.save_session(session)

            print(f"\n{'='*70}")
            print(f"✅ ANÁLISE COMPLETA!")
            print(f"{'='*70}")
            print(f"📂 Resultados: {session.output_dir}")
            print(f"{'='*70}\n")

            return {
                "status": "completed",
                "session_id": session_id,
                "extraction": extraction_result,
                "analysis": analysis_result,
                "output_dir": session.output_dir
            }

        except Exception as e:
            print(f"\n❌ ERRO: {e}\n")
            session.status = SessionStatus.FAILED
            session.workflow['error'] = str(e)
            self.state_manager.save_session(session)
            raise

    def _run_extraction(self, session: AnalysisSession) -> Dict[str, Any]:
        """Run document structurer extraction"""
        output_dir = Path(session.output_dir) / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run Document Structurer
        result = self.document_structurer.structure_document(
            session.pdf_path,
            output_path=str(output_dir / "requirements.csv")
        )

        # Update session
        session.results['document_structurer'] = {
            'status': 'completed',
            'csv_path': str(output_dir / "requirements.csv"),
            'total_requirements': len(result.get('requirements', [])),
            'timestamp': datetime.now().isoformat()
        }
        self.state_manager.save_session(session)

        return result

    def _run_analysis(
        self,
        session: AnalysisSession,
        extraction_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run technical analyst conformity analysis"""
        csv_path = session.results['document_structurer']['csv_path']
        output_dir = Path(session.output_dir) / "outputs"

        # Run Analysis Pipeline
        report = self.analysis_pipeline.analyze_from_csv(
            csv_path,
            output_basename="analysis",
            export_formats=['json', 'csv', 'markdown']
        )

        # Get summary
        summary = report.get_summary()

        # Update session
        session.results['technical_analyst'] = {
            'status': 'completed',
            'report_path': str(output_dir / "analysis.json"),
            'conformity_rate': summary['conforme_pct'] / 100,
            'total_requirements': summary['total_requirements'],
            'conforme': summary['conforme'],
            'nao_conforme': summary['nao_conforme'],
            'revisao': summary['revisao'],
            'timestamp': datetime.now().isoformat()
        }
        self.state_manager.save_session(session)

        return {
            'summary': summary,
            'report_path': str(output_dir / "analysis.json")
        }

    # ==================== Commands ====================

    def cmd_ajuda(self) -> str:
        """Show help information"""
        return self.command_router.show_help()

    def cmd_listar_analises(
        self,
        limit: int = 10,
        status: Optional[str] = None
    ) -> str:
        """List analysis sessions"""
        return self.command_router.list_analyses(limit=limit, status=status)

    # ==================== Utilities ====================

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        all_sessions = self.list_sessions()

        return {
            'total_sessions': len(all_sessions),
            'completed': len([s for s in all_sessions if s.status == SessionStatus.COMPLETED]),
            'in_progress': len([s for s in all_sessions if s.status == SessionStatus.IN_PROGRESS]),
            'failed': len([s for s in all_sessions if s.status == SessionStatus.FAILED]),
            'state_dir': str(self.state_dir),
            'deliveries_dir': str(self.deliveries_dir)
        }
```

### 2. State Manager (agents/orchestrator/state_manager.py)

```python
"""
State Manager - Session Persistence

Manages persistence of analysis sessions and system state.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from datetime import datetime

from .session import AnalysisSession, SessionStatus


class StateManager:
    """Manages state persistence for Orchestrator"""

    def __init__(self, state_dir: str):
        """
        Initialize State Manager

        Args:
            state_dir: Directory for state files
        """
        self.state_dir = Path(state_dir)
        self.sessions_dir = self.state_dir / "sessions"
        self.index_file = self.state_dir / "index.json"

        # Ensure directories exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Load or create index
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load session index"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'sessions': {}, 'last_updated': None}

    def _save_index(self):
        """Save session index"""
        self.index['last_updated'] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def save_session(self, session: AnalysisSession):
        """Save session to disk"""
        # Save session file
        session_file = self.sessions_dir / f"{session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

        # Update index
        self.index['sessions'][session.session_id] = {
            'status': session.status.value,
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'pdf_path': session.pdf_path
        }
        self._save_index()

    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Load session from disk"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return AnalysisSession.from_dict(data)

    def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        limit: Optional[int] = None
    ) -> List[AnalysisSession]:
        """
        List all sessions

        Args:
            status: Filter by status
            limit: Maximum sessions to return

        Returns:
            List of sessions sorted by creation date (newest first)
        """
        sessions = []

        for session_id in self.index['sessions'].keys():
            session = self.get_session(session_id)
            if session:
                if status is None or session.status == status:
                    sessions.append(session)

        # Sort by creation date (newest first)
        sessions.sort(key=lambda s: s.created_at, reverse=True)

        if limit:
            sessions = sessions[:limit]

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()

            if session_id in self.index['sessions']:
                del self.index['sessions'][session_id]
                self._save_index()

            return True

        return False
```

### 3. Session (agents/orchestrator/session.py)

```python
"""
Analysis Session - Data Model

Represents a single analysis session.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class SessionStatus(Enum):
    """Session status"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AnalysisSession:
    """
    Analysis session data model

    Represents a complete edital analysis workflow.
    """

    session_id: str
    pdf_path: str
    output_dir: str
    edital_info: Dict[str, Any] = field(default_factory=dict)
    status: SessionStatus = SessionStatus.IN_PROGRESS
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    workflow: Dict[str, Any] = field(default_factory=lambda: {
        'mode': 'manual',
        'current_stage': 'extraction',
        'stages_completed': []
    })

    results: Dict[str, Any] = field(default_factory=lambda: {
        'document_structurer': {},
        'technical_analyst': {}
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisSession':
        """Create from dictionary"""
        # Convert status string to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = SessionStatus(data['status'])

        return cls(**data)

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
```

### 4. Command Router (agents/orchestrator/command_router.py)

```python
"""
Command Router - Command Handling

Routes and handles system commands (*ajuda, *listar_analises, etc.)
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .orchestrator import Orchestrator


class CommandRouter:
    """Routes and handles Orchestrator commands"""

    def __init__(self, orchestrator: 'Orchestrator'):
        """
        Initialize Command Router

        Args:
            orchestrator: Parent Orchestrator instance
        """
        self.orchestrator = orchestrator

    def show_help(self) -> str:
        """Show help information"""
        help_text = """
╔════════════════════════════════════════════════════════════════╗
║                  BidAnalyzee - Sistema de Ajuda                ║
╚════════════════════════════════════════════════════════════════╝

📋 COMANDOS PRINCIPAIS:

  /analyze-edital <pdf>    Analisar edital completo (extração + análise)
  /structure-edital <pdf>  Apenas extrair requisitos do edital

🔧 COMANDOS DO SISTEMA:

  *ajuda                   Mostrar esta ajuda
  *listar_analises [n]     Listar últimas N análises (padrão: 10)
  *listar_analises completed  Listar apenas análises completas
  *listar_analises in_progress  Listar análises em andamento

📚 DOCUMENTAÇÃO:

  docs/USER_GUIDE.md       Guia do usuário
  docs/TECHNICAL_ANALYST_RAG.md  Documentação técnica do RAG
  README.md                Visão geral do projeto

💡 EXEMPLOS:

  # Análise completa de edital
  /analyze-edital editais/edital_001.pdf

  # Listar últimas 5 análises
  *listar_analises 5

  # Ver apenas análises completas
  *listar_analises completed

╔════════════════════════════════════════════════════════════════╗
║  Para mais informações, consulte a documentação em docs/      ║
╚════════════════════════════════════════════════════════════════╝
"""
        return help_text

    def list_analyses(
        self,
        limit: int = 10,
        status: Optional[str] = None
    ) -> str:
        """
        List analysis sessions

        Args:
            limit: Maximum sessions to show
            status: Filter by status (completed, in_progress, failed)

        Returns:
            Formatted string with session list
        """
        from .session import SessionStatus

        # Convert status string to enum
        status_filter = None
        if status:
            try:
                status_filter = SessionStatus(status)
            except ValueError:
                return f"❌ Status inválido: {status}. Use: completed, in_progress, failed"

        sessions = self.orchestrator.list_sessions(
            status=status_filter,
            limit=limit
        )

        if not sessions:
            return "📭 Nenhuma análise encontrada."

        # Build table
        lines = []
        lines.append("\n╔════════════════════════════════════════════════════════════════╗")
        lines.append("║           HISTÓRICO DE ANÁLISES                               ║")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")

        for i, session in enumerate(sessions, 1):
            # Status emoji
            status_emoji = {
                SessionStatus.COMPLETED: "✅",
                SessionStatus.IN_PROGRESS: "🔄",
                SessionStatus.FAILED: "❌",
                SessionStatus.PAUSED: "⏸️"
            }.get(session.status, "❓")

            lines.append(f"{i}. {status_emoji} {session.session_id}")
            lines.append(f"   📄 PDF: {session.pdf_path}")
            lines.append(f"   📅 Criado: {session.created_at}")
            lines.append(f"   📊 Status: {session.status.value}")

            # Show results if completed
            if session.status == SessionStatus.COMPLETED:
                if 'technical_analyst' in session.results:
                    ta_result = session.results['technical_analyst']
                    conformity = ta_result.get('conformity_rate', 0) * 100
                    lines.append(f"   ✅ Taxa de Conformidade: {conformity:.1f}%")

            lines.append("")

        lines.append(f"Total: {len(sessions)} análise(s)")
        lines.append("")

        return "\n".join(lines)
```

---

## 🧪 Testes

### Unit Tests (tests/unit/test_orchestrator.py)

```python
import pytest
from agents.orchestrator import Orchestrator, AnalysisSession, SessionStatus


class TestOrchestrator:
    """Unit tests for Orchestrator"""

    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with temporary directories"""
        return Orchestrator(
            state_dir=str(tmp_path / "state"),
            deliveries_dir=str(tmp_path / "deliveries")
        )

    def test_create_session(self, orchestrator):
        """Test session creation"""
        session = orchestrator.create_session(
            pdf_path="test.pdf",
            edital_info={"numero": "001/2024"}
        )

        assert session is not None
        assert session.session_id.startswith("analysis_test")
        assert session.status == SessionStatus.IN_PROGRESS

    def test_get_session(self, orchestrator):
        """Test session retrieval"""
        # Create session
        session = orchestrator.create_session("test.pdf")

        # Retrieve session
        retrieved = orchestrator.get_session(session.session_id)

        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_list_sessions(self, orchestrator):
        """Test listing sessions"""
        # Create multiple sessions
        orchestrator.create_session("test1.pdf")
        orchestrator.create_session("test2.pdf")

        sessions = orchestrator.list_sessions()

        assert len(sessions) == 2

    def test_list_sessions_with_status_filter(self, orchestrator):
        """Test listing sessions with status filter"""
        # Create sessions
        s1 = orchestrator.create_session("test1.pdf")
        s2 = orchestrator.create_session("test2.pdf")

        # Update one to completed
        s1.status = SessionStatus.COMPLETED
        orchestrator.state_manager.save_session(s1)

        # Filter by completed
        completed = orchestrator.list_sessions(status=SessionStatus.COMPLETED)

        assert len(completed) == 1
        assert completed[0].session_id == s1.session_id
```

### Integration Tests (tests/integration/test_orchestrator_integration.py)

```python
import pytest
from pathlib import Path
from agents.orchestrator import Orchestrator


class TestOrchestratorIntegration:
    """Integration tests for Orchestrator with real agents"""

    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator"""
        return Orchestrator(
            state_dir=str(tmp_path / "state"),
            deliveries_dir=str(tmp_path / "deliveries")
        )

    def test_full_workflow_mock(self, orchestrator, sample_pdf):
        """Test complete workflow with mocked components"""
        # Create session
        session = orchestrator.create_session(sample_pdf)

        # Run analysis (with mocked agents)
        # This will be implemented after agents are integrated

        assert session.status == SessionStatus.IN_PROGRESS

    def test_cmd_ajuda(self, orchestrator):
        """Test help command"""
        help_text = orchestrator.cmd_ajuda()

        assert "BidAnalyzee" in help_text
        assert "/analyze-edital" in help_text
        assert "*ajuda" in help_text

    def test_cmd_listar_analises(self, orchestrator):
        """Test list analyses command"""
        # Create sessions
        orchestrator.create_session("test1.pdf")
        orchestrator.create_session("test2.pdf")

        # List analyses
        output = orchestrator.cmd_listar_analises(limit=10)

        assert "HISTÓRICO" in output
        assert "test1.pdf" in output
        assert "test2.pdf" in output
```

---

## 📅 Cronograma

### Semana 1 (5 dias)

**Dia 1-2: Setup e Data Models**
- [ ] Criar estrutura de diretórios
- [ ] Implementar `AnalysisSession` dataclass
- [ ] Implementar `StateManager`
- [ ] Testes unitários de Session + StateManager

**Dia 3-4: Orchestrator Core**
- [ ] Implementar classe `Orchestrator`
- [ ] Session management (create, get, list)
- [ ] Workflow execution básico
- [ ] Testes unitários do Orchestrator

**Dia 5: Commands**
- [ ] Implementar `CommandRouter`
- [ ] Comando `*ajuda`
- [ ] Comando `*listar_analises`
- [ ] Testes dos comandos

### Semana 2 (5 dias)

**Dia 6-7: Integração com Agentes**
- [ ] Integrar Document Structurer
- [ ] Integrar Technical Analyst (AnalysisPipeline)
- [ ] Workflow completo funcionando
- [ ] Testes de integração

**Dia 8: Polimento**
- [ ] Refatoração
- [ ] Error handling
- [ ] Logging melhorado
- [ ] Validações

**Dia 9: Documentação**
- [ ] Docstrings completas
- [ ] ORCHESTRATOR_README.md
- [ ] Exemplos de uso
- [ ] Atualizar documentação geral

**Dia 10: Validação Final**
- [ ] Code review
- [ ] Testes end-to-end
- [ ] Performance check
- [ ] Preparar para Sprint 9

---

## ✅ Definition of Done

História 4.1 (Orchestrator Base) está completa quando:

- [ ] Classe `Orchestrator` implementada e testada
- [ ] `StateManager` gerenciando sessões corretamente
- [ ] `AnalysisSession` com todos os campos necessários
- [ ] `CommandRouter` com comandos *ajuda e *listar_analises
- [ ] Integração com Document Structurer funcional
- [ ] Integração com Technical Analyst funcional
- [ ] Workflow completo funcionando (create session → extract → analyze → report)
- [ ] Persistência de estado em JSON
- [ ] Testes unitários > 80% cobertura
- [ ] Testes de integração passando
- [ ] Documentação completa
- [ ] Código commitado na branch
- [ ] Performance aceitável (< 10s overhead vs. agents diretos)
- [ ] Estado recuperável após crash

---

## 📊 Métricas de Sucesso

| Métrica | Target |
|---------|--------|
| Código (linhas) | ~800-1000 |
| Testes (linhas) | 400+ |
| Cobertura | > 80% |
| Overhead | < 10s vs. direto |
| Comandos | 2 (*ajuda, *listar) |
| Integrações | 2 (Structurer, Analyst) |

---

## 🎯 Preparação para Sprints 9-10

Este sprint cria a BASE para:

**Sprint 9: Modo Assistido**
- Workflow com HALTs
- Aprovação do usuário em cada etapa
- Feedback loops

**Sprint 10: Modos Automatizados**
- Modo FLOW (sem HALTs)
- Consulta Rápida
- Polimento UX

A arquitetura do Orchestrator já contempla esses workflows futuros através de:
- `workflow['mode']` - assistido, flow, consulta
- Session state management
- Command routing extensível

---

**Status:** 🚀 Ready to Start
**Próximo Passo:** Criar estrutura de diretórios e Session dataclass
**Responsável:** Claude (Orchestrator development)
**Data:** 08 de novembro de 2025
