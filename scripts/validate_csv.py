#!/usr/bin/env python3
"""
CSV Validator Script

Validates CSV output from both Document Structurer and Technical Analyst agents.

Usage:
    python3 scripts/validate_csv.py --input file.csv [--type structurer|analyst]

Checks:
- CSV structure and format
- Required fields present
- Data types correct
- UTF-8 encoding
- No malformed lines
- Type-specific validations

Auto-detects CSV type if --type not specified.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Tuple, List, Optional


# Document Structurer CSV format (7 fields)
STRUCTURER_FIELDS = [
    'ID',
    'Requisito',
    'Categoria',
    'Criticidade',
    'Obrigatoriedade',
    'Quantidade',
    'Observacoes'
]

# Technical Analyst CSV format (8 fields)
ANALYST_FIELDS = [
    'ID',
    'Requisito',
    'Categoria',
    'Veredicto',
    'Confiança',
    'Evidências',
    'Raciocínio',
    'Recomendações'
]

VALID_VERDICTS = ['CONFORME', 'NAO_CONFORME', 'REVISAO']
VALID_CRITICIDADES = ['BAIXA', 'MEDIA', 'ALTA', 'CRITICA']
VALID_OBRIGATORIEDADES = ['OBRIGATORIO', 'DESEJAVEL', 'OPCIONAL']


def detect_csv_type(fieldnames: List[str]) -> Optional[str]:
    """
    Auto-detect CSV type based on fieldnames

    Returns:
        'structurer', 'analyst', or None
    """
    if set(STRUCTURER_FIELDS).issubset(set(fieldnames)):
        return 'structurer'
    elif set(ANALYST_FIELDS).issubset(set(fieldnames)):
        return 'analyst'
    return None


def validate_structurer_row(row: dict, row_num: int) -> List[str]:
    """Validate a Document Structurer CSV row"""
    errors = []

    # Validate Criticidade
    criticidade = row.get('Criticidade', '').strip().upper()
    if criticidade and criticidade not in VALID_CRITICIDADES:
        errors.append(f"Line {row_num}: Invalid Criticidade '{criticidade}'. Must be one of: {', '.join(VALID_CRITICIDADES)}")

    # Validate Obrigatoriedade
    obrig = row.get('Obrigatoriedade', '').strip().upper()
    if obrig and obrig not in VALID_OBRIGATORIEDADES:
        errors.append(f"Line {row_num}: Invalid Obrigatoriedade '{obrig}'. Must be one of: {', '.join(VALID_OBRIGATORIEDADES)}")

    # Validate Quantidade (must be valid number or N/A)
    quantidade = row.get('Quantidade', '').strip()
    if quantidade and quantidade.upper() != 'N/A':
        try:
            qty = float(quantidade.replace(',', '.'))
            if qty < 0:
                errors.append(f"Line {row_num}: Quantidade cannot be negative: {qty}")
        except ValueError:
            errors.append(f"Line {row_num}: Quantidade must be a number or 'N/A', got: '{quantidade}'")

    return errors


def validate_analyst_row(row: dict, row_num: int) -> List[str]:
    """Validate a Technical Analyst CSV row"""
    errors = []

    # Validate Veredicto
    veredicto = row.get('Veredicto', '').strip()
    if veredicto and veredicto not in VALID_VERDICTS:
        errors.append(f"Line {row_num}: Invalid Veredicto '{veredicto}'. Must be one of: {', '.join(VALID_VERDICTS)}")

    # Validate Confiança (must be float 0.0-1.0)
    try:
        confianca = float(row.get('Confiança', '0').replace(',', '.'))
        if not (0.0 <= confianca <= 1.0):
            errors.append(f"Line {row_num}: Confiança {confianca} out of range [0.0, 1.0]")
    except ValueError:
        errors.append(f"Line {row_num}: Confiança is not a valid number")

    return errors


def validate_csv(filepath: Path, csv_type: Optional[str] = None) -> Tuple[bool, List[str], Optional[str]]:
    """
    Validate CSV file

    Args:
        filepath: Path to CSV file
        csv_type: 'structurer', 'analyst', or None for auto-detect

    Returns:
        (is_valid, errors, detected_type)
    """
    errors = []
    detected_type = None

    # Check file exists
    if not filepath.exists():
        errors.append(f"File not found: {filepath}")
        return False, errors, None

    # Check encoding
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        errors.append("File is not UTF-8 encoded")
        return False, errors, None

    # Parse CSV
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Check header
            if not reader.fieldnames:
                errors.append("CSV has no header")
                return False, errors, None

            # Auto-detect type if not specified
            if csv_type is None:
                detected_type = detect_csv_type(reader.fieldnames)
                if detected_type is None:
                    errors.append(f"Cannot detect CSV type. Headers: {', '.join(reader.fieldnames)}")
                    errors.append(f"Expected either Structurer fields or Analyst fields")
                    return False, errors, None
            else:
                detected_type = csv_type

            # Set required fields based on type
            if detected_type == 'structurer':
                required_fields = STRUCTURER_FIELDS
            elif detected_type == 'analyst':
                required_fields = ANALYST_FIELDS
            else:
                errors.append(f"Invalid CSV type: {detected_type}")
                return False, errors, detected_type

            # Check required fields
            missing_fields = set(required_fields) - set(reader.fieldnames)
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")

            extra_fields = set(reader.fieldnames) - set(required_fields)
            if extra_fields:
                errors.append(f"Extra fields (not required): {', '.join(extra_fields)}")

            # Validate rows
            row_count = 0
            for row_num, row in enumerate(reader, start=2):  # start=2 because header is line 1
                row_count += 1

                # Check all fields present
                for field in required_fields:
                    if field not in row:
                        errors.append(f"Line {row_num}: Missing field '{field}'")
                    elif not row[field].strip():
                        # Allow empty Observacoes in Structurer
                        if not (detected_type == 'structurer' and field == 'Observacoes'):
                            errors.append(f"Line {row_num}: Empty field '{field}'")

                # Type-specific validations
                if detected_type == 'structurer':
                    errors.extend(validate_structurer_row(row, row_num))
                elif detected_type == 'analyst':
                    errors.extend(validate_analyst_row(row, row_num))

            if row_count == 0:
                errors.append("CSV has no data rows")

    except csv.Error as e:
        errors.append(f"CSV parsing error: {e}")
        return False, errors, detected_type
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return False, errors, detected_type

    is_valid = len(errors) == 0
    return is_valid, errors, detected_type


def main():
    parser = argparse.ArgumentParser(
        description="Validate CSV output from Document Structurer or Technical Analyst"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to CSV file to validate"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=['structurer', 'analyst'],
        default=None,
        help="CSV type (auto-detects if not specified)"
    )

    args = parser.parse_args()
    filepath = Path(args.input)

    print(f"\n{'='*70}")
    print(f"📋 VALIDATING CSV")
    print(f"{'='*70}")
    print(f"File: {filepath}")
    if args.type:
        print(f"Type: {args.type}")
    print(f"{'='*70}\n")

    is_valid, errors, detected_type = validate_csv(filepath, args.type)

    if detected_type:
        type_name = "Document Structurer" if detected_type == 'structurer' else "Technical Analyst"
        print(f"📊 Detected Type: {type_name}\n")

    if is_valid:
        print("✅ CSV is VALID")
        print("\nAll checks passed:")
        print("  ✅ UTF-8 encoding")
        print("  ✅ Required fields present")
        print("  ✅ Data types correct")
        print("  ✅ No malformed lines")
        if detected_type == 'structurer':
            print("  ✅ Valid Criticidade values")
            print("  ✅ Valid Obrigatoriedade values")
            print("  ✅ Valid Quantidade values")
        elif detected_type == 'analyst':
            print("  ✅ Valid Veredicto values")
            print("  ✅ Valid Confiança range [0.0-1.0]")
        print()
        return 0
    else:
        print("❌ CSV is INVALID\n")
        print(f"Found {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
