"""
State Manager - Gerencia persistência de sessões
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from .session import Session


class StateManager:
    """Gerencia estado do sistema (sessões)"""

    def __init__(self, state_dir: str = "data/state"):
        """
        Inicializa o gerenciador de estado

        Args:
            state_dir: Diretório para armazenar estado
        """
        self.state_dir = Path(state_dir)
        self.sessions_dir = self.state_dir / "sessions"
        self.index_file = self.state_dir / "index.json"

        # Criar diretórios se não existirem
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Cria uma nova sessão

        Args:
            session_id: ID da sessão (gerado automaticamente se None)

        Returns:
            Session criada
        """
        if session_id is None:
            # Gerar ID baseado em timestamp
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = Session(session_id)
        self.save_session(session)
        self._update_index(session)

        return session

    def load_session(self, session_id: str) -> Optional[Session]:
        """
        Carrega uma sessão existente

        Args:
            session_id: ID da sessão

        Returns:
            Session ou None se não existir
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Session.from_dict(data)

    def save_session(self, session: Session) -> None:
        """
        Salva uma sessão

        Args:
            session: Session a salvar
        """
        session_file = self.sessions_dir / f"{session.session_id}.json"

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

        self._update_index(session)

    def list_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista todas as sessões (ordenadas por data de criação, mais recentes primeiro)

        Args:
            limit: Número máximo de sessões a retornar

        Returns:
            Lista de metadados de sessões
        """
        index = self._load_index()
        sessions = sorted(
            index.get("sessions", []),
            key=lambda s: s["created_at"],
            reverse=True
        )

        if limit:
            sessions = sessions[:limit]

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Deleta uma sessão

        Args:
            session_id: ID da sessão

        Returns:
            True se deletou, False se não existia
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return False

        session_file.unlink()
        self._remove_from_index(session_id)

        return True

    def get_latest_session(self) -> Optional[Session]:
        """
        Retorna a sessão mais recente

        Returns:
            Session ou None
        """
        sessions = self.list_sessions(limit=1)

        if not sessions:
            return None

        return self.load_session(sessions[0]["session_id"])

    def _load_index(self) -> dict:
        """Carrega o índice de sessões"""
        if not self.index_file.exists():
            return {"sessions": []}

        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self, index: dict) -> None:
        """Salva o índice de sessões"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    def _update_index(self, session: Session) -> None:
        """Atualiza o índice com informações da sessão"""
        index = self._load_index()
        sessions = index.get("sessions", [])

        # Remover entrada antiga se existir
        sessions = [s for s in sessions if s["session_id"] != session.session_id]

        # Adicionar nova entrada
        sessions.append({
            "session_id": session.session_id,
            "created_at": session.data.metadata.created_at,
            "updated_at": session.data.metadata.updated_at,
            "status": session.data.metadata.status,
            "workflow_stage": session.data.metadata.workflow_stage
        })

        index["sessions"] = sessions
        self._save_index(index)

    def _remove_from_index(self, session_id: str) -> None:
        """Remove uma sessão do índice"""
        index = self._load_index()
        sessions = [s for s in index.get("sessions", []) if s["session_id"] != session_id]
        index["sessions"] = sessions
        self._save_index(index)
