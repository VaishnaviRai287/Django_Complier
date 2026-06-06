# APIForge

> **APIForge** is a production-grade incremental API schema compiler and evolution engine that compiles a custom `.api` Domain-Specific Language (DSL) into production-ready Django REST Framework backends.

APIForge tracks your database schemas across code changes, generating precise structural diffs and database evolution planning scripts without destroying existing data.

---

## 🛠️ Compiler Architecture

APIForge is built using clean, decoupled compiler passes to ensure type safety and high performance (<5ms compilation times):

1. **Lexical Analysis (`lexer.py`):** Scans the raw DSL char stream and generates a structured token stream.
2. **LL(1) Recursive Descent Parser (`parser.py` & `ast.py`):** Consumes tokens and constructs a structured type-safe Abstract Syntax Tree (AST).
3. **Semantic Validation (`semantic.py`):** Runs checks for name casings, duplicate fields, referential relationship target integrity, and suggests corrections for mistyped field types.
4. **Code Generator (`codegen.py`):** Translates AST configurations into self-contained Django projects complete with models, serializers, views, and URL routing.
5. **State Persistence (`snapshot.py`):** Caches compiler state inside `.apiforge/schema.json` to enable incremental change analysis.
6. **Diff Engine & Planner (`diff.py` & `planner.py`):** Compares live AST versions with persistent snapshots to formulate safe, non-destructive migration operations.
7. **Live File Watcher (`watcher.py`):** A file daemon that hot-reloads edits, displaying differences and migration plans instantly on save.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/APIForge.git
   cd APIForge
   ```

2. **Initialize and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the package in editable mode with development tools:**
   ```bash
   pip install -e .
   ```

---

## 📖 Step-by-Step Usage Guide

### 1. Write your first `.api` Specification
Create a file named `examples/blog.api` using our clean, declarative schema DSL:

```dsl
resource Author {
    name string
    email email
}

resource Post {
    title string
    content string
    author belongs_to Author
}
```

### 2. Parse and Validate the DSL
To inspect the compiler's parsed Abstract Syntax Tree representation in JSON format, run:
```bash
apiforge parse examples/blog.api
```
*Expected Output:*
```json
{
    "resources": [
        {
            "resource": "Author",
            "fields": [
                {
                    "name": "name",
                    "type": "string"
                },
                {
                    "name": "email",
                    "type": "email"
                }
            ]
        },
        ...
    ]
}
```

### 3. Generate the Django Backend Scaffolding
Compile your DSL file into a fully working, self-contained Django REST Framework project:
```bash
apiforge generate examples/blog.api
```
This command generates a `generated/` directory with a standard Django app structure and caches the baseline schema snapshot inside `.apiforge/schema.json`.

### 4. Run the Generated REST API
Change directories to the compiled project, run migrations, and boot the server:
```bash
cd generated/
python manage.py makemigrations app
python manage.py migrate
python manage.py runserver
```
Now, navigate your browser to `http://127.0.0.1:8000/api/` to explore the styled Django REST Framework browsable API!

### 5. Audit Schema Modifications (Incremental Diff)
Go back to the root workspace. Let's add a `likes` field to the `Post` resource and define a new `Comment` resource:
```bash
# Update specification file
echo -e "resource Author {\n    name string\n    email email\n}\n\nresource Post {\n    title string\n    content string\n    likes integer\n    author belongs_to Author\n}\n\nresource Comment {\n    body string\n}" > examples/blog.api
```
Now run the `diff` command to inspect structural changes compared to the baseline:
```bash
apiforge diff examples/blog.api
```
*Expected Output:*
```text
Added resource:
  Comment

Added field:
  Post.likes
```

### 6. Generate Migration Action Plans
Use the planner to convert structural changes into physical, ordered migration tasks:
```bash
apiforge plan examples/blog.api
```
*Expected Output:*
```text
Migration Plan:
  1. AddResource(name='Comment', fields=[body: string])
  2. AddField(resource='Post', name='likes', type='integer')
```

### 7. Run Watcher for Live hot-reloading
Start the live watch daemon to recompile, validate, and display plans instantly as you make changes to the specification file:
```bash
apiforge watch examples/blog.api
```
Whenever you hit save in your editor, the console clears and displays active compilation deltas and evolution paths.

---

## 🧪 Running Tests
Verify compiler passes and CLI scripts using pytest:
```bash
pytest tests/ -v
```

---

## 📄 License
This project is licensed under the MIT License.
