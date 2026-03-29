#!/usr/bin/env python3
"""
Extract data files (CSV, JSON, Excel) from the notebook cell outputs.

The export cell encodes files as base64 strings in stdout with markers:
  FILE:<filename>:BASE64:<data>

Usage:
    python papers/extract_data.py
"""
import json
import base64
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'xgboost_Wanzo_Matching.ipynb')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def get_cell_stdout(cell):
    """Get all stdout text from a cell."""
    texts = []
    for output in cell.get('outputs', []):
        if output.get('output_type') == 'stream' and output.get('name', '') == 'stdout':
            text = output.get('text', '')
            if isinstance(text, list):
                text = ''.join(text)
            texts.append(text)
    return ''.join(texts)


def extract_data():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"ERROR: Notebook not found at {NOTEBOOK_PATH}")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Find the export cell (contains DATA_EXPORT_START marker)
    export_text = None
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        text = get_cell_stdout(cell)
        if '===DATA_EXPORT_START===' in text:
            export_text = text
            exec_count = cell.get('execution_count', '?')
            print(f"Found export cell (execution_count={exec_count})")
            break

    if not export_text:
        print("ERROR: No export cell found. Run the data export cell in the notebook first.")
        sys.exit(1)

    # Parse FILE: lines
    saved = 0
    for line in export_text.split('\n'):
        line = line.strip()
        if not line.startswith('FILE:'):
            continue

        parts = line.split(':BASE64:', 1)
        if len(parts) != 2:
            continue

        filename = parts[0].replace('FILE:', '')
        b64_data = parts[1]

        try:
            file_bytes = base64.b64decode(b64_data)
            out_path = os.path.join(OUTPUT_DIR, filename)
            with open(out_path, 'wb') as f:
                f.write(file_bytes)
            print(f"  Saved: {filename} ({len(file_bytes):,} bytes)")
            saved += 1
        except Exception as e:
            print(f"  ERROR decoding {filename}: {e}")

    print(f"\n{saved} files extracted to {OUTPUT_DIR}")


if __name__ == '__main__':
    extract_data()
