# APIForge Build Log

## Phase 0 — Project Bootstrap

**Date:** 2026-06-05  
**Status:** ✅ Complete

### What Was Built
- Python project with `src/` layout and `pyproject.toml`
- Virtual environment (`.venv/`)
- CLI entrypoint: `apiforge --help`, `apiforge --version`, `apiforge info`
- Test suite: 8 passing tests

### Why
Every project needs a proper foundation before features. This gives us an installable package, a CLI framework, and automated tests.

### Key Decisions
| Decision | Why |
|----------|-----|
| `src/` layout | Prevents import shadowing, professional standard |
| Click for CLI | Composable subcommands, built-in test runner |
| `pyproject.toml` | Modern Python packaging, single config file |
| pytest | Industry standard, better than unittest |

### Verification
```bash
apiforge --help       # ✅ Shows help
apiforge --version    # ✅ 0.1.0
pytest tests/ -v      # ✅ 8 passed
```

## Phase 1 — Parse a Single Resource

**Date:** 2026-06-05  
**Status:** ✅ Complete

### What Was Built
- Custom `.api` file format parser in `src/apiforge/compiler/parser.py`
- Simple regex-based parsing to extract resource name and its fields (only string types supported for now)
- Registered a new CLI subcommand `apiforge parse <file_path>` in `src/apiforge/cli/main.py`
- Formatted output utility `parse_to_json` to output parsed representation as a clean JSON
- Added comprehensive unit and integration tests (16 total passed) in `tests/test_parser.py`

### Why
To build a compiler, we must first parse/understand user input. Building a simple regex-based parser allows us to establish the input-to-output pipeline without over-engineering complex parser components (AST, tokenizers) before they are actually needed.

### Key Decisions
| Decision | Why |
|----------|-----|
| Regex-based parsing | Simple, fast to implement, matches the scope of Phase 1 (one resource, simple fields) |
| Lazy CLI Imports | Importing parser inside Click commands keeps CLI load/help commands instantaneous |
| Custom `.api` extension | Identifies files containing our custom API DSL |

### Verification
```bash
apiforge parse examples/product.api   # ✅ Parses & outputs JSON schema
.venv/bin/pytest tests/ -v             # ✅ 16 passed
apiforge info                         # ✅ Shows Phase: 1
```
