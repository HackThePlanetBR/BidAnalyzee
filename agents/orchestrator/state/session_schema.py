"""
Session Schema - Estruturas de dados para State Management
"""

from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json


@dataclass
class SessionMetadata:
    """Metadados de uma sessão"""
    session_id: str
    created_at: str  # ISO format
    updated_at: str  # ISO format
    status: Literal["in_progress", "completed", "failed", "cancelled"]
    workflow_stage: Literal["idle", "extracting", "analyzing", "completed"]


@dataclass
class SessionData:
    """Dados de uma sessão completa"""
    metadata: SessionMetadata
    edital_info: Optional[Dict[str, Any]] = None
    extraction_result: Optional[Dict[str, Any]] = None
    analysis_result: Optional[Dict[str, Any]] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> dict:
        """Converte para dicionário (para JSON)"""
        return {
            "metadata": asdict(self.metadata),
            "edital_info": self.edital_info,
            "extraction_result": self.extraction_result,
            "analysis_result": self.analysis_result,
            "errors": self.errors
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionData":
        """Cria a partir de dicionário"""
        metadata = SessionMetadata(**data["metadata"])
        return cls(
            metadata=metadata,
            edital_info=data.get("edital_info"),
            extraction_result=data.get("extraction_result"),
            analysis_result=data.get("analysis_result"),
            errors=data.get("errors", [])
        )
