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

    def backup_all_sessions(self, backup_dir: Optional[str] = None) -> str:
        """
        Cria backup de todas as sessões

        Args:
            backup_dir: Diretório de backup (usa data/state/backups se None)

        Returns:
            Caminho do arquivo de backup criado
        """
        import shutil
        import tarfile
        from datetime import datetime

        if backup_dir is None:
            backup_dir = self.state_dir / "backups"
        else:
            backup_dir = Path(backup_dir)

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"sessions_backup_{timestamp}.tar.gz"

        # Criar arquivo tar.gz
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(self.sessions_dir, arcname="sessions")
            if self.index_file.exists():
                tar.add(self.index_file, arcname="index.json")

        return str(backup_file)

    def restore_from_backup(self, backup_file: str) -> int:
        """
        Restaura sessões de um backup

        Args:
            backup_file: Caminho do arquivo de backup

        Returns:
            Número de sessões restauradas
        """
        import tarfile
        import shutil

        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup não encontrado: {backup_file}")

        # Criar backup das sessões atuais antes de restaurar
        if self.sessions_dir.exists():
            current_backup = self.backup_all_sessions()
            print(f"ℹ️  Backup atual salvo em: {current_backup}")

        # Limpar sessões atuais
        if self.sessions_dir.exists():
            shutil.rmtree(self.sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Extrair backup
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(self.state_dir)

        # Contar sessões restauradas
        sessions = self.list_sessions()
        return len(sessions)

    def cleanup_old_sessions(self, days: int = 30, keep_completed: bool = True) -> int:
        """
        Remove sessões antigas

        Args:
            days: Remover sessões mais antigas que N dias
            keep_completed: Se True, mantém sessões completas mesmo se antigas

        Returns:
            Número de sessões removidas
        """
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        sessions = self.list_sessions()
        removed_count = 0

        for session_meta in sessions:
            # Converter data de criação
            created_at = datetime.fromisoformat(session_meta["created_at"])

            # Decidir se deve remover
            should_remove = False

            if created_at < cutoff_date:
                if keep_completed and session_meta["status"] == "completed":
                    # Não remover sessões completadas
                    should_remove = False
                else:
                    should_remove = True

            if should_remove:
                self.delete_session(session_meta["session_id"])
                removed_count += 1

        return removed_count

    def get_sessions_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre sessões

        Returns:
            Dicionário com estatísticas
        """
        sessions = self.list_sessions()

        stats = {
            "total": len(sessions),
            "by_status": {},
            "by_stage": {},
            "oldest": None,
            "newest": None,
            "total_size_mb": 0
        }

        if not sessions:
            return stats

        # Contar por status e stage
        for session in sessions:
            status = session["status"]
            stage = session["workflow_stage"]

            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_stage"][stage] = stats["by_stage"].get(stage, 0) + 1

        # Oldest e newest
        sorted_sessions = sorted(sessions, key=lambda s: s["created_at"])
        stats["oldest"] = sorted_sessions[0]["session_id"]
        stats["newest"] = sorted_sessions[-1]["session_id"]

        # Tamanho total
        total_size = sum(
            (self.sessions_dir / f"{s['session_id']}.json").stat().st_size
            for s in sessions
            if (self.sessions_dir / f"{s['session_id']}.json").exists()
        )
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        return stats
