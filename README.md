# TMDL Parser (Python)

A small Python library to parse Tabular Model Definition Language (.tmdl) files and convert them into native Python dictionary objects.

TMDL (Tabular Model Definition Language) is a JSON-based representation used by Microsoft Analysis Services to define tabular models. This library focuses on reading .tmdl files and producing a convenient Python dict representation suitable for inspection, transformation, or programmatic manipulation.

Links
- TMDL overview: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview?view=sql-analysis-services-2025

Features
- Read .tmdl files and return a Python dict
- Preserve structure and most common metadata used in tabular models
- Simple, dependency-light implementation designed for extension

Installation
- This project is under development. For now, clone the repository and use the parser module directly:
  git clone <repo-url>
  cd tmdl
  python -m pip install -r requirements.txt  # if a requirements file exists

Basic usage
- Example: read a .tmdl file and get a Python dict

```python
# Example usage (pseudo-code)
import tmdl

model_dict = tmdl.loads("model.tmdl")
# model_dict is a nested Python dict mirroring the TMDL structure
```

API (suggested)
- tmdl.loads(path: str) -> dict
  - Read and parse a .tmdl file from disk.
- tmdl.loads(text: str) -> dict
  - Parse .tmdl content provided as a string.
- validate_tmdl(data: dict) -> list[str]
  - Optional validator to return warnings/errors about missing/unsupported fields.

Parser approach
- Most .tmdl files are JSON-like; the parser will:
  1. Try to load the content as JSON (fast path).
  2. If JSON load fails, apply a tolerant lexer/parser to handle minor formatting differences (comments, trailing commas, etc.).
  3. Convert the parsed structure into a normalized Python dict, keeping keys/values as-is where possible.
- Design emphasis: correctness and clear, inspectable output over aggressive transformation.

Supported elements & limitations
- Expected to support common model elements: metadata, tables, columns, relationships, measures, roles, partitions.
- Advanced or extremely custom properties may be preserved but not fully validated.
- Not a full replacement for Analysis Services tooling — use for automation and lightweight inspections.

Example output structure
- The returned dict mirrors the top-level structure of a .tmdl file, for example:
```python
{
    "name": "MyModel",
    "compatibilityLevel": 1575,
    "model": {
        "tables": [
            {
                "name": "Sales",
                "columns": [...],
                "partitions": [...],
            },
            ...
        ],
        "relationships": [...],
        "measures": [...],
    },
    # ...other top-level sections...
}
```

Development notes
- Write unit tests covering:
  - JSON-valid .tmdl files
  - .tmdl files with comments/trailing commas
  - Edge cases with nested objects and arrays
- Keep parser modular: separate IO, parsing, and normalization steps.
- Add optional streaming or incremental parsing for large files later.

Roadmap
- v0.1: Reliable JSON-path parsing + basic tolerant parser
- v0.2: Validation utilities and richer examples
- v0.3: Write and apply transforms (e.g., extract a subset of model elements)

Contributing
- Contributions welcome. Please open issues for bugs or feature requests and use pull requests for code changes. Include tests for new behaviors.

License
- MIT License