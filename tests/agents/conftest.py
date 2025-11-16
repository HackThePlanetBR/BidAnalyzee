"""
Pytest fixtures for agent tests

Provides common test data and utilities for testing agents
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import csv
import json


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_pdf_content():
    """Sample PDF text content for testing"""
    return """
EDITAL DE LICITAÇÃO Nº 001/2025
PREGÃO ELETRÔNICO

ESPECIFICAÇÕES TÉCNICAS

1. SISTEMA DE VIDEOMONITORAMENTO

1.1. Câmeras de Monitoramento
- Resolução mínima: 1920x1080 (Full HD)
- Frame rate: mínimo 30 fps
- Certificação ANATEL obrigatória
- Compressão H.265

1.2. Servidor de Gravação
- Storage: mínimo 10TB
- Redundância RAID 5 obrigatória
- Sistema operacional Linux ou Windows Server

1.3. Software de Gestão
- Interface web responsiva
- Suporte a mínimo 100 câmeras simultâneas
- Backup automático configurável

2. REQUISITOS DE GARANTIA
- Garantia mínima: 36 meses
- Assistência técnica local
"""


@pytest.fixture
def sample_requirements_csv(temp_dir):
    """Generate sample requirements CSV for testing"""
    csv_path = temp_dir / "requirements.csv"

    requirements = [
        {
            "id": "REQ001",
            "item": "Câmera Full HD",
            "descricao": "Resolução mínima 1920x1080, 30fps, certificação ANATEL",
            "categoria": "Hardware",
            "prioridade": "Alta",
            "pagina": "3",
            "confianca": "0.95"
        },
        {
            "id": "REQ002",
            "item": "Servidor de Gravação",
            "descricao": "Storage 10TB, RAID 5, Linux/Windows Server",
            "categoria": "Hardware",
            "prioridade": "Alta",
            "pagina": "3",
            "confianca": "0.92"
        },
        {
            "id": "REQ003",
            "item": "Software de Gestão",
            "descricao": "Interface web, suporte 100 câmeras, backup automático",
            "categoria": "Software",
            "prioridade": "Média",
            "pagina": "4",
            "confianca": "0.88"
        }
    ]

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=requirements[0].keys())
        writer.writeheader()
        writer.writerows(requirements)

    return csv_path


@pytest.fixture
def sample_analysis_csv(temp_dir):
    """Generate sample analysis CSV for testing"""
    csv_path = temp_dir / "analysis.csv"

    analyses = [
        {
            "item": "Câmera Full HD",
            "categoria": "Hardware",
            "descricao": "Resolução mínima 1920x1080, 30fps, certificação ANATEL",
            "veredicto": "CONFORME",
            "justificativa": "Requisitos atendem legislação e normas técnicas vigentes",
            "evidencias": "Lei_8666.md:120, ANATEL_Norma.md:45",
            "nivel_confianca": "Alto",
            "recomendacoes": "Verificar homologação ANATEL antes da compra"
        },
        {
            "item": "Servidor de Gravação",
            "categoria": "Hardware",
            "descricao": "Storage 10TB, RAID 5, Linux/Windows Server",
            "veredicto": "CONFORME",
            "justificativa": "Configuração adequada para armazenamento e redundância",
            "evidencias": "Requisitos_TI.md:78",
            "nivel_confianca": "Alto",
            "recomendacoes": "Dimensionar storage considerando período de retenção"
        },
        {
            "item": "Software de Gestão",
            "categoria": "Software",
            "descricao": "Interface web, suporte 100 câmeras, backup automático",
            "veredicto": "PARCIALMENTE CONFORME",
            "justificativa": "Falta especificar protocolos de comunicação e APIs",
            "evidencias": "Requisitos_Software.md:34",
            "nivel_confianca": "Médio",
            "recomendacoes": "Especificar protocolos ONVIF e RTSP"
        }
    ]

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=analyses[0].keys())
        writer.writeheader()
        writer.writerows(analyses)

    return csv_path


@pytest.fixture
def sample_rag_response():
    """Sample RAG search response"""
    return {
        "query": "Resolução mínima câmera videomonitoramento",
        "results": [
            {
                "source": "requisitos_tecnicos.md",
                "text": "Câmeras de videomonitoramento devem ter resolução mínima de 1920x1080 pixels (Full HD)",
                "similarity": 0.92,
                "metadata": {"filename": "requisitos_tecnicos.md", "chunk_index": 12}
            },
            {
                "source": "ANATEL_Norma.md",
                "text": "Todos os equipamentos de comunicação devem possuir certificação ANATEL",
                "similarity": 0.87,
                "metadata": {"filename": "ANATEL_Norma.md", "chunk_index": 5}
            }
        ]
    }


@pytest.fixture
def sample_session_state():
    """Sample session state for Orchestrator"""
    return {
        "session_id": "test_session_001",
        "edital_name": "Edital_001_2025_Videomonitoramento.pdf",
        "created_at": "2025-11-16T10:00:00",
        "stage": "analysis",
        "status": "in_progress",
        "metadata": {
            "edital_type": "pregao_eletronico",
            "total_requirements": 15,
            "categories": ["Hardware", "Software", "Serviço"]
        },
        "outputs": {
            "requirements_csv": "data/sessions/test_session_001/requirements.csv",
            "analysis_csv": None
        }
    }


@pytest.fixture
def shield_checklist():
    """SHIELD framework checklist items"""
    return {
        "document_structurer": {
            "S_STRUCTURE": [
                "Plano de extração criado",
                "Estratégia de categorização definida",
                "Tempo estimado calculado"
            ],
            "H_HALT": [
                "Checkpoint antes de processamento batch",
                "Validação de entrada (PDF válido, tamanho aceitável)"
            ],
            "I_INSPECT": [
                "Todos os campos obrigatórios preenchidos",
                "Rastreabilidade (página) presente",
                "Score de confiança calculado",
                "Sem duplicatas"
            ],
            "E_EXECUTE": [
                "CSV gerado com encoding UTF-8",
                "7 campos obrigatórios presentes"
            ],
            "L_LOOP": [
                "Iteração se validação falhar",
                "Correção de erros detectados"
            ],
            "D_DELIVER": [
                "CSV válido entregue",
                "Relatório de qualidade gerado"
            ]
        },
        "technical_analyst": {
            "S_STRUCTURE": [
                "Requisito lido e compreendido",
                "Critérios técnicos identificados",
                "Estratégia de busca planejada"
            ],
            "H_HALT": [
                "Checkpoint antes de análise batch",
                "Confirmação do usuário para prosseguir"
            ],
            "I_INSPECT": [
                "RAG retornou evidências relevantes (≥2)",
                "Evidências cobrem todos os aspectos",
                "Contradições identificadas",
                "Contexto legal brasileiro considerado"
            ],
            "E_EXECUTE": [
                "RAG search executado",
                "Veredicto atribuído (CONFORME/NÃO CONFORME/PARCIAL/REQUER ANÁLISE)",
                "Justificativa completa fornecida",
                "Evidências citadas corretamente"
            ],
            "L_LOOP": [
                "Revisão se evidências insuficientes",
                "Busca adicional se necessário"
            ],
            "D_DELIVER": [
                "CSV de análise válido",
                "Todos os veredictos justificados"
            ]
        },
        "orchestrator": {
            "S_STRUCTURE": [
                "Sessão criada",
                "Estado inicial persistido",
                "Workflow planejado"
            ],
            "H_HALT": [
                "Checkpoint entre agentes",
                "Validação de outputs antes de passar para próximo agente"
            ],
            "I_INSPECT": [
                "Output do agente anterior válido",
                "Estado da sessão consistente",
                "Erros de agentes detectados"
            ],
            "E_EXECUTE": [
                "Comando roteado corretamente",
                "Agente invocado com parâmetros corretos",
                "Estado atualizado"
            ],
            "L_LOOP": [
                "Retry em caso de falha",
                "Rollback se necessário"
            ],
            "D_DELIVER": [
                "Workflow completo",
                "Todos os outputs gerados",
                "Estado final persistido"
            ]
        }
    }


@pytest.fixture
def expected_csv_fields():
    """Expected CSV field names for each stage"""
    return {
        "requirements": [
            "id", "item", "descricao", "categoria",
            "prioridade", "pagina", "confianca"
        ],
        "analysis": [
            "item", "categoria", "descricao", "veredicto",
            "justificativa", "evidencias", "nivel_confianca",
            "recomendacoes"
        ]
    }
