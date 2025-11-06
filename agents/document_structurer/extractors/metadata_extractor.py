#!/usr/bin/env python3
"""
Metadata Extractor for Brazilian Public Procurement Documents (Editais)

Extracts key metadata from edital PDFs:
- Objeto (procurement object/purpose)
- Órgão (contracting agency)
- Valor Estimado (estimated value)
- Prazo de Entrega (delivery deadline)
- Modalidade (procurement modality)
- Número do Edital (edital number)
- Data de Publicação (publication date)
- Endereço de Entrega (delivery address)
- Contato Responsável (contact person)
- Anexos (required attachments)

Author: BidAnalyzee Team
Date: 2025-11-06
Version: 1.1.0
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class EditalMetadata:
    """
    Structured metadata extracted from edital.
    """
    objeto: Optional[str] = None
    orgao: Optional[str] = None
    valor_estimado: Optional[str] = None
    prazo_entrega: Optional[str] = None
    modalidade: Optional[str] = None
    numero_edital: Optional[str] = None
    data_publicacao: Optional[str] = None
    endereco_entrega: Optional[str] = None
    contato_responsavel: Optional[str] = None
    anexos: Optional[List[str]] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML/JSON serialization"""
        return {
            "objeto": self.objeto,
            "orgao": self.orgao,
            "valor_estimado": self.valor_estimado,
            "prazo_entrega": self.prazo_entrega,
            "modalidade": self.modalidade,
            "numero_edital": self.numero_edital,
            "data_publicacao": self.data_publicacao,
            "endereco_entrega": self.endereco_entrega,
            "contato_responsavel": self.contato_responsavel,
            "anexos": self.anexos,
            "confidence_scores": self.confidence_scores
        }


class MetadataExtractor:
    """
    Extracts metadata from Brazilian edital text.

    Uses regex patterns optimized for Brazilian Portuguese
    administrative documents.
    """

    # Patterns for extracting different metadata fields
    PATTERNS = {
        "objeto": [
            r'(?:OBJETO|Objeto)[:\s]+(.{10,500}?)(?:\n\s*\n|\n\s*\d+\.)',
            r'(?:DO OBJETO|Do Objeto)[:\s]+(.{10,500}?)(?:\n\s*\n|\n\s*\d+\.)',
            r'(?:OBJETO DA LICITAÇÃO|Objeto da Licitação)[:\s]+(.{10,500}?)(?:\n\s*\n|\n\s*\d+\.)',
            r'Objeto[:\s]+(.{10,300})',
        ],

        "orgao": [
            r'(?:PREFEITURA MUNICIPAL DE|Prefeitura Municipal de)\s+([A-ZÀ-Ú\s]+?)(?:\n|,|\.|\s{2})',
            r'(?:GOVERNO DO ESTADO DE|Governo do Estado de)\s+([A-ZÀ-Ú\s]+?)(?:\n|,|\.|\s{2})',
            r'(?:ÓRGÃO|Órgão)[:\s]+(.{5,100}?)(?:\n|,)',
        ],

        "valor_estimado": [
            r'(?:VALOR ESTIMADO|Valor Estimado)[:\s]+R?\$?\s*([\d\.,]+)',
            r'(?:VALOR TOTAL|Valor Total)[:\s]+R?\$?\s*([\d\.,]+)',
            r'(?:VALOR GLOBAL|Valor Global)[:\s]+R?\$?\s*([\d\.,]+)',
        ],

        "prazo_entrega": [
            r'(?:PRAZO DE ENTREGA|Prazo de Entrega)[:\s]*(\d+\s*(?:dias|meses|anos))',
            r'(?:PRAZO|Prazo)[:\s]*(\d+\s*(?:dias|meses|anos))',
        ],

        "modalidade": [
            r'(PREGÃO ELETRÔNICO|Pregão Eletrônico)',
            r'(CONCORRÊNCIA PÚBLICA|Concorrência Pública)',
            r'(TOMADA DE PREÇOS|Tomada de Preços)',
            r'(CONVITE|Convite)',
            r'(DISPENSA|Dispensa)',
            r'(INEXIGIBILIDADE|Inexigibilidade)',
        ],

        "numero_edital": [
            r'(?:EDITAL|Edital)\s+(?:N[ºo°]?\.?\s*)?(\d+/\d{4})',
            r'(?:EDITAL|Edital)\s+(?:N[ºo°]?\.?\s*)?([A-Z]+-\d+-\d{4})',
            r'(?:PROCESSO|Processo)\s+(?:N[ºo°]?\.?\s*)?(\d+/\d{4})',
        ],

        "data_publicacao": [
            r'(?:DATA DE PUBLICAÇÃO|Data de Publicação)[:\s]*(\d{2}/\d{2}/\d{4})',
            r'(?:PUBLICADO EM|Publicado em)[:\s]*(\d{2}/\d{2}/\d{4})',
        ],

        "endereco_entrega": [
            r'(?:ENDEREÇO DE ENTREGA|Endereço de Entrega)[:\s]+(.{10,150}?)(?:\n)',
            r'(?:LOCAL DE ENTREGA|Local de Entrega)[:\s]+(.{10,150}?)(?:\n)',
        ],

        "contato_responsavel": [
            r'(?:E-?MAIL|E-?mail)[:\s]+([\w\.\-]+@[\w\.\-]+)',
            r'(?:TELEFONE|Telefone)[:\s]+([\(\)\d\s\-]{8,20})',
            r'(?:CONTATO|Contato)[:\s]+([A-ZÀ-Úa-zà-ú\s]{5,50})(?:\n)',
        ],

        "anexos": [
            r'(?:ANEXO|Anexo)\s+([IVX\d]+)\s*[-–]\s*(.{5,100}?)(?:\n)',
            r'(?:DOCUMENTOS? EXIGIDOS?|Documentos? Exigidos?)[:\s]*\n\s*[-•]\s*(.{5,100}?)(?:\n)',
        ],
    }

    def __init__(self):
        """Initialize the metadata extractor"""
        self.confidence_threshold = 0.70

    def extract(self, text: str, pages: List[Dict[str, Any]] = None) -> EditalMetadata:
        """
        Extract metadata from edital text.

        Args:
            text: Complete edital text (or first 50 pages for performance)
            pages: Optional list of page dicts with 'page' and 'text' keys

        Returns:
            EditalMetadata object with extracted fields
        """
        # Use only first 50 pages for metadata (usually in header sections)
        if pages and len(pages) > 50:
            search_text = "\n".join([p.get("text", "") for p in pages[:50]])
        else:
            search_text = text[:100000]  # First ~100KB

        metadata = EditalMetadata()

        # Extract each field
        metadata.objeto = self._extract_field(search_text, "objeto")
        metadata.orgao = self._extract_field(search_text, "orgao")
        metadata.valor_estimado = self._extract_field(search_text, "valor_estimado")
        metadata.prazo_entrega = self._extract_field(search_text, "prazo_entrega")
        metadata.modalidade = self._extract_field(search_text, "modalidade")
        metadata.numero_edital = self._extract_field(search_text, "numero_edital")
        metadata.data_publicacao = self._extract_field(search_text, "data_publicacao")
        metadata.endereco_entrega = self._extract_field(search_text, "endereco_entrega")
        metadata.contato_responsavel = self._extract_field(search_text, "contato_responsavel")
        metadata.anexos = self._extract_list_field(search_text, "anexos")

        # Calculate confidence scores
        metadata.confidence_scores = self._calculate_confidence(metadata)

        return metadata

    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extract a single metadata field using regex patterns.

        Args:
            text: Text to search
            field_name: Name of field (key in PATTERNS dict)

        Returns:
            Extracted value or None
        """
        patterns = self.PATTERNS.get(field_name, [])

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()

                # Clean up the extracted value
                value = self._clean_value(value, field_name)

                if value and len(value) > 3:  # Minimum viable length
                    return value

        return None

    def _extract_list_field(self, text: str, field_name: str) -> List[str]:
        """
        Extract a list of values from a metadata field (e.g., anexos).

        Args:
            text: Text to search
            field_name: Name of field (key in PATTERNS dict)

        Returns:
            List of extracted values (empty list if none found)
        """
        patterns = self.PATTERNS.get(field_name, [])
        results = []

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # For anexos, we might have either 1 or 2 capture groups
                if match.lastindex == 2:
                    # Pattern has 2 groups (e.g., "ANEXO I - Description")
                    value = f"{match.group(1)} - {match.group(2)}".strip()
                else:
                    # Pattern has 1 group
                    value = match.group(1).strip()

                value = self._clean_value(value, field_name)
                if value and len(value) > 3 and value not in results:
                    results.append(value)

        return results if results else []

    def _clean_value(self, value: str, field_name: str) -> str:
        """
        Clean extracted value (remove excess whitespace, format, etc.)

        Args:
            value: Raw extracted value
            field_name: Field name for context-specific cleaning

        Returns:
            Cleaned value
        """
        # Remove excess whitespace
        value = re.sub(r'\s+', ' ', value).strip()

        # Field-specific cleaning
        if field_name == "valor_estimado":
            # Ensure R$ prefix
            if not value.startswith("R$"):
                value = f"R$ {value}"

        elif field_name == "objeto":
            # Remove trailing punctuation except period
            value = value.rstrip(";:,")
            # Capitalize first letter
            if value:
                value = value[0].upper() + value[1:]

        elif field_name == "orgao":
            # Title case for agency names
            value = value.title()

        # Final strip to remove any remaining whitespace
        return value.strip()

    def _calculate_confidence(self, metadata: EditalMetadata) -> Dict[str, float]:
        """
        Calculate confidence scores for each extracted field.

        Based on:
        - Pattern strength (which pattern matched)
        - Value length and format validity
        - Presence of expected keywords

        Args:
            metadata: EditalMetadata object

        Returns:
            Dict mapping field names to confidence scores (0.0-1.0)
        """
        scores = {}

        # Simple heuristic-based confidence
        if metadata.objeto:
            # Longer objeto = more confident
            length_score = min(len(metadata.objeto) / 200, 1.0)
            # Contains keywords = bonus
            keyword_score = 0.2 if any(kw in metadata.objeto.lower() for kw in ["aquisição", "contratação", "fornecimento"]) else 0.0
            scores["objeto"] = min(0.7 + length_score * 0.2 + keyword_score, 1.0)
        else:
            scores["objeto"] = 0.0

        if metadata.orgao:
            # Contains "Prefeitura" or "Governo" = high confidence
            if any(kw in metadata.orgao for kw in ["Prefeitura", "Governo", "Ministério"]):
                scores["orgao"] = 0.95
            else:
                scores["orgao"] = 0.75
        else:
            scores["orgao"] = 0.0

        if metadata.valor_estimado:
            # Valid format R$ X.XXX,XX = high confidence
            if re.match(r'R\$\s*[\d\.,]+', metadata.valor_estimado):
                scores["valor_estimado"] = 0.90
            else:
                scores["valor_estimado"] = 0.70
        else:
            scores["valor_estimado"] = 0.0

        if metadata.prazo_entrega:
            # Contains number + unit = high confidence
            if re.match(r'\d+\s*(?:dias|meses|anos)', metadata.prazo_entrega):
                scores["prazo_entrega"] = 0.90
            else:
                scores["prazo_entrega"] = 0.70
        else:
            scores["prazo_entrega"] = 0.0

        if metadata.modalidade:
            # Exact match of known modality = very high confidence
            scores["modalidade"] = 0.98
        else:
            scores["modalidade"] = 0.0

        if metadata.numero_edital:
            # Format XX/YYYY = high confidence
            if re.match(r'\d+/\d{4}', metadata.numero_edital):
                scores["numero_edital"] = 0.95
            else:
                scores["numero_edital"] = 0.80
        else:
            scores["numero_edital"] = 0.0

        if metadata.data_publicacao:
            # Valid date format = high confidence
            if re.match(r'\d{2}/\d{2}/\d{4}', metadata.data_publicacao):
                scores["data_publicacao"] = 0.95
            else:
                scores["data_publicacao"] = 0.75
        else:
            scores["data_publicacao"] = 0.0

        if metadata.endereco_entrega:
            # Reasonable length = decent confidence
            if len(metadata.endereco_entrega) > 20:
                scores["endereco_entrega"] = 0.85
            else:
                scores["endereco_entrega"] = 0.70
        else:
            scores["endereco_entrega"] = 0.0

        if metadata.contato_responsavel:
            # Email or phone pattern = high confidence
            if '@' in metadata.contato_responsavel or re.search(r'\d{2,}', metadata.contato_responsavel):
                scores["contato_responsavel"] = 0.90
            else:
                scores["contato_responsavel"] = 0.75
        else:
            scores["contato_responsavel"] = 0.0

        if metadata.anexos and len(metadata.anexos) > 0:
            # Found anexos = high confidence
            # More anexos = slightly higher confidence
            base_confidence = 0.85
            bonus = min(len(metadata.anexos) * 0.02, 0.10)  # Up to 0.10 bonus
            scores["anexos"] = min(base_confidence + bonus, 0.98)
        else:
            scores["anexos"] = 0.0

        return scores

    def get_overall_confidence(self, metadata: EditalMetadata) -> float:
        """
        Calculate overall confidence score for metadata extraction.

        Uses weighted average where:
        - Critical fields (objeto, numero_edital) have weight 2.0
        - Important fields (orgao, modalidade) have weight 1.5
        - Optional fields (valor, prazo, data, endereco, contato, anexos) have weight 1.0
        - Completeness bonus: more fields extracted = higher confidence

        Args:
            metadata: EditalMetadata object

        Returns:
            Overall confidence score (0.0-1.0)
        """
        # Field importance weights
        field_weights = {
            "objeto": 2.0,
            "numero_edital": 2.0,
            "orgao": 1.5,
            "modalidade": 1.5,
            "valor_estimado": 1.0,
            "prazo_entrega": 1.0,
            "data_publicacao": 1.0,
            "endereco_entrega": 1.0,
            "contato_responsavel": 1.0,
            "anexos": 1.0
        }

        weighted_sum = 0.0
        total_weight = 0.0
        fields_extracted = 0

        for field, score in metadata.confidence_scores.items():
            if score > 0.0:
                weight = field_weights.get(field, 1.0)
                weighted_sum += score * weight
                total_weight += weight
                fields_extracted += 1

        if total_weight == 0:
            return 0.0

        # Base weighted average
        base_confidence = weighted_sum / total_weight

        # Completeness bonus (up to 0.1 points for extracting all 10 fields)
        completeness_bonus = (fields_extracted / 10.0) * 0.1

        # Final confidence (capped at 1.0)
        return min(base_confidence + completeness_bonus, 1.0)

    def validate_metadata(self, metadata: EditalMetadata) -> Dict[str, bool]:
        """
        Validate extracted metadata for completeness and quality.

        Args:
            metadata: EditalMetadata object

        Returns:
            Dict mapping field names to validation status (True/False)
        """
        validation = {}

        # Critical fields (should always be present)
        validation["objeto_present"] = metadata.objeto is not None
        validation["numero_edital_present"] = metadata.numero_edital is not None

        # Optional but important
        validation["orgao_present"] = metadata.orgao is not None
        validation["modalidade_present"] = metadata.modalidade is not None

        # Confidence thresholds
        validation["objeto_confident"] = metadata.confidence_scores.get("objeto", 0) >= self.confidence_threshold
        validation["overall_confident"] = self.get_overall_confidence(metadata) >= self.confidence_threshold

        return validation


# Convenience function
def extract_metadata(text: str, pages: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to extract metadata from edital text.

    Args:
        text: Complete edital text
        pages: Optional list of page dicts

    Returns:
        Dictionary with metadata and confidence scores
    """
    extractor = MetadataExtractor()
    metadata = extractor.extract(text, pages)

    return {
        "metadata": metadata.to_dict(),
        "overall_confidence": extractor.get_overall_confidence(metadata),
        "validation": extractor.validate_metadata(metadata)
    }


if __name__ == "__main__":
    # Example usage
    sample_text = """
    PREFEITURA MUNICIPAL DE SÃO PAULO

    EDITAL Nº 001/2025
    PREGÃO ELETRÔNICO

    DATA DE PUBLICAÇÃO: 15/01/2025

    1. OBJETO

    Aquisição de Sistema de Videomonitoramento Urbano com câmeras IP,
    servidores de armazenamento e software de gerenciamento, conforme
    especificações técnicas anexas.

    2. VALOR ESTIMADO

    R$ 2.500.000,00 (dois milhões e quinhentos mil reais)

    3. PRAZO DE ENTREGA

    180 dias corridos a partir da assinatura do contrato.
    """

    result = extract_metadata(sample_text)

    print("Extracted Metadata:")
    print("=" * 60)
    for key, value in result["metadata"].items():
        if value and key != "confidence_scores":
            print(f"{key}: {value}")

    print("\nConfidence Scores:")
    print("=" * 60)
    for key, score in result["metadata"]["confidence_scores"].items():
        if score > 0:
            print(f"{key}: {score:.2f}")

    print(f"\nOverall Confidence: {result['overall_confidence']:.2f}")

    print("\nValidation:")
    print("=" * 60)
    for key, status in result["validation"].items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {key}: {status}")
