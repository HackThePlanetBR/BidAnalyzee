#!/usr/bin/env python3
"""
Index Manager for Document Structurer

Maintains a centralized index of all analyses performed.

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.0.0
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class IndexManager:
    """Manages the central index of edital analyses"""

    def __init__(self, index_path: str = "data/index_analises.csv"):
        self.index_path = Path(index_path)
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create index file if it doesn't exist"""
        if not self.index_path.exists():
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Data", "Edital", "Requisitos", "Status", "Tempo", "Path"])

    def add_analysis(
        self,
        edital_name: str,
        total_requirements: int,
        status: str,
        execution_time: str,
        delivery_path: str
    ) -> int:
        """
        Add new analysis to index

        Returns: Analysis ID
        """
        # Read current entries
        entries = self.list_all()
        next_id = len(entries) + 1

        # Check for duplicates
        if self._is_duplicate(edital_name):
            raise ValueError(f"Analysis for '{edital_name}' already exists")

        # Add new entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.index_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                next_id,
                timestamp,
                edital_name,
                total_requirements,
                status,
                execution_time,
                delivery_path
            ])

        return next_id

    def list_all(self) -> List[Dict[str, str]]:
        """List all analyses"""
        if not self.index_path.exists():
            return []

        with open(self.index_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def get_by_id(self, analysis_id: int) -> Optional[Dict[str, str]]:
        """Get analysis by ID"""
        entries = self.list_all()
        for entry in entries:
            if int(entry["ID"]) == analysis_id:
                return entry
        return None

    def _is_duplicate(self, edital_name: str) -> bool:
        """Check if edital was already analyzed"""
        entries = self.list_all()
        return any(entry["Edital"] == edital_name for entry in entries)


# Convenience function
def register_analysis(edital_name: str, total_requirements: int, execution_time: str, delivery_path: str) -> int:
    """Register completed analysis in index"""
    manager = IndexManager()
    return manager.add_analysis(edital_name, total_requirements, "COMPLETO", execution_time, delivery_path)


if __name__ == "__main__":
    # Example usage
    manager = IndexManager()

    # Add example analysis
    try:
        analysis_id = manager.add_analysis(
            edital_name="PMSP-2025-001",
            total_requirements=47,
            status="COMPLETO",
            execution_time="15m20s",
            delivery_path="data/deliveries/analysis_PMSP-2025-001_20251106_140000"
        )
        print(f"✅ Analysis registered: ID {analysis_id}")
    except ValueError as e:
        print(f"⚠️ {e}")

    # List all
    print("\nAll analyses:")
    for entry in manager.list_all():
        print(f"  {entry['ID']}: {entry['Edital']} ({entry['Requisitos']} reqs) - {entry['Status']}")
