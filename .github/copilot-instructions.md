# AI Agent Instructions for TMDL Parser

## Project Overview
This is a Python library for parsing Tabular Model Definition Language (TMDL) files into Python dictionaries. The project focuses on a clean, extensible implementation for reading Microsoft Analysis Services' TMDL format.

### Key elements of TMDL include:

- Full compatibility with the entire Tabular Object Model (TOM). Every TMDL object exposes the same properties as TOM.
- Text-based and optimized for human interaction and readability. TMDL uses a grammar syntax similar to YAML. Each TMDL object is represented in text with minimal delimiters and uses indentation to demark parent-child relationships.
- Better editing experience, especially on properties with embed expressions from different content-types, like Data Analysis Expression (DAX) and M.
- Better for collaboration because of its folder representation where each model object has an individual file representation, making it more source control friendly.

## Key Components & Architecture
- Core parsing logic lives in `src/tmdl/` directory
- Two-phase parsing approach:
  1. Fast path: direct JSON loading
  2. Fallback: tolerant parsing for non-standard TMDL (comments, trailing commas)
- Output is normalized Python dict preserving TMDL structure

## Development Workflow
- Python 3.9+ required per `pyproject.toml`
- Using `hatchling` build system
- Tests should be added in `tests/` directory
- Run tests before submitting changes (test command TBD)

## Project Conventions
- Module organization:
  - Public API methods in `src/tmdl/__init__.py`
  - Implementation details in submodules
- Dict structure mirrors TMDL format exactly:
  ```python
  {
      "name": str,
      "compatibilityLevel": int,
      "model": {
          "tables": [...],
          "relationships": [...],
          "measures": [...]
      }
  }
  ```
- Error handling: Preserve JSON parsing errors but wrap with context

## Integration Points
- Primary interface through `tmdl.loads()` function
- Takes either file path or string input
- Returns standard Python dict for maximum interoperability
- Optional validation available through `validate_tmdl()`

## Critical Files
- `src/tmdl/__init__.py`: Public API definitions
- `src/tmdl/main.py`: Core implementation
- `pyproject.toml`: Project metadata and dependencies
- `tests/`: Test cases including edge-case TMDL examples

## Work in Progress
The project is under initial development. When implementing new features:
1. Focus on correct parsing over performance optimizations
2. Maintain clear separation between IO, parsing, and validation
3. Add tests for new TMDL variations encountered
4. Keep dependencies minimal - core Python only where possible