"""
Session Class - Representa uma sessão de análise
"""

from datetime import datetime
from pathlib import Path
import json
from typing import Optional, Dict, Any
from .session_schema import SessionData, SessionMetadata


class Session:
    """Gerencia uma sessão individual de análise"""

    def __init__(self, session_id: str, data: Optional[SessionData] = None):
        """
        Inicializa uma sessão

        Args:
            session_id: ID único da sessão
            data: Dados da sessão (None para nova sessão)
        """
        self.session_id = session_id

        if data is None:
            # Nova sessão
            metadata = SessionMetadata(
                session_id=session_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status="in_progress",
                workflow_stage="idle"
            )
            self.data = SessionData(metadata=metadata)
        else:
            self.data = data

    def update_stage(self, stage: str) -> None:
        """Atualiza o estágio do workflow"""
        self.data.metadata.workflow_stage = stage
        self.data.metadata.updated_at = datetime.now().isoformat()

    def update_status(self, status: str) -> None:
        """Atualiza o status da sessão"""
        self.data.metadata.status = status
        self.data.metadata.updated_at = datetime.now().isoformat()

    def add_error(self, error: str) -> None:
        """Adiciona um erro à sessão"""
        self.data.errors.append({
            "timestamp": datetime.now().isoformat(),
            "message": error
        })
        self.data.metadata.updated_at = datetime.now().isoformat()

    def set_edital_info(self, edital_path: str, edital_name: str) -> None:
        """Define informações do edital"""
        self.data.edital_info = {
            "path": edital_path,
            "name": edital_name,
            "timestamp": datetime.now().isoformat()
        }
        self.data.metadata.updated_at = datetime.now().isoformat()

    def set_extraction_result(self, csv_path: str, num_requirements: int) -> None:
        """Define resultado da extração"""
        self.data.extraction_result = {
            "csv_path": csv_path,
            "num_requirements": num_requirements,
            "timestamp": datetime.now().isoformat()
        }
        self.data.metadata.updated_at = datetime.now().isoformat()

    def set_analysis_result(self, csv_path: str, summary: Dict[str, Any]) -> None:
        """Define resultado da análise"""
        self.data.analysis_result = {
            "csv_path": csv_path,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        self.data.metadata.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return self.data.to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Cria a partir de dicionário"""
        session_data = SessionData.from_dict(data)
        return cls(session_data.metadata.session_id, session_data)
