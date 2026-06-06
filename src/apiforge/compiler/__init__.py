"""Compiler package for APIForge.

This package contains the modular compiler passes of the schema engine:
- Lexer (`lexer.py`): Performs lexical scanning and produces Token streams.
- AST (`ast.py`): Defines syntax tree nodes (`SchemaNode`, `ResourceNode`, `FieldNode`).
- Parser (`parser.py`): Implements LL(1) recursive descent parsing.
- Semantic Analyzer (`semantic.py`): Enforces casings, duplicates, typo corrections, referential integrity.
- Code Generator (`codegen.py`): Compiles AST to standalone Django apps.
- Snapshot Persistent Manager (`snapshot.py`): Handles schema baseline snapshots.
- Diff Engine (`diff.py`): Computes structural differences, renames, and type changes.
- Planner (`planner.py`): Formulates risk-rated migration ops and relational dependency impacts.
- File Watcher (`watcher.py`): Manages live schema hot-reloading loop.
"""