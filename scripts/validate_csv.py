#!/usr/bin/env python3
"""
CSV Validator Script

Validates analysis CSV output from Technical Analyst Agent.

Usage:
    python3 scripts/validate_csv.py --input analysis.csv

Checks:
- CSV structure and format
- Required fields present
- Data types correct
- UTF-8 encoding
- No malformed lines
"""

import argparse
import csv
import sys
from pathlib import Path


REQUIRED_FIELDS = [
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


def validate_csv(filepath: Path) -> tuple[bool, list[str]]:
    """
    Validate CSV file

    Returns:
        (is_valid, errors)
    """
    errors = []

    # Check file exists
    if not filepath.exists():
        errors.append(f"File not found: {filepath}")
        return False, errors

    # Check encoding
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        errors.append("File is not UTF-8 encoded")
        return False, errors

    # Parse CSV
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Check header
            if not reader.fieldnames:
                errors.append("CSV has no header")
                return False, errors

            missing_fields = set(REQUIRED_FIELDS) - set(reader.fieldnames)
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")

            extra_fields = set(reader.fieldnames) - set(REQUIRED_FIELDS)
            if extra_fields:
                errors.append(f"Extra fields (not required): {', '.join(extra_fields)}")

            # Validate rows
            row_count = 0
            for row_num, row in enumerate(reader, start=2):  # start=2 because header is line 1
                row_count += 1

                # Check all fields present
                for field in REQUIRED_FIELDS:
                    if field not in row or not row[field].strip():
                        errors.append(f"Line {row_num}: Empty or missing field '{field}'")

                # Validate Veredicto
                veredicto = row.get('Veredicto', '').strip()
                if veredicto and veredicto not in VALID_VERDICTS:
                    errors.append(f"Line {row_num}: Invalid Veredicto '{veredicto}'. Must be one of: {', '.join(VALID_VERDICTS)}")

                # Validate Confiança (must be float 0.0-1.0)
                try:
                    confianca = float(row.get('Confiança', '0'))
                    if not (0.0 <= confianca <= 1.0):
                        errors.append(f"Line {row_num}: Confiança {confianca} out of range [0.0, 1.0]")
                except ValueError:
                    errors.append(f"Line {row_num}: Confiança is not a valid number")

            if row_count == 0:
                errors.append("CSV has no data rows")

    except csv.Error as e:
        errors.append(f"CSV parsing error: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return False, errors

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate Technical Analyst CSV output"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to CSV file to validate"
    )

    args = parser.parse_args()
    filepath = Path(args.input)

    print(f"\n{'='*70}")
    print(f"📋 VALIDATING CSV")
    print(f"{'='*70}")
    print(f"File: {filepath}")
    print(f"{'='*70}\n")

    is_valid, errors = validate_csv(filepath)

    if is_valid:
        print("✅ CSV is VALID")
        print("\nAll checks passed:")
        print("  ✅ UTF-8 encoding")
        print("  ✅ Required fields present")
        print("  ✅ Data types correct")
        print("  ✅ No malformed lines")
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
