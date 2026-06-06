# APIForge Developer Journey: Building and Evolving APIs from Scratch

Welcome to the **APIForge Guided Workshop**! This document is designed to take a developer from having zero knowledge of APIForge to being fully capable of building, running, and evolving database backends. 

Whether you are here to learn how to use the compiler, build a new backend project, or understand how schema evolution heuristics protect database schemas during iterations, this workshop is for you.

---

## Table of Contents
1.  [Introduction: What is APIForge?](#introduction)
2.  [Section 1 — Installation & Setup](#section-1--installation)
3.  [Section 2 — Create Your First Project DSL](#section-2--create-your-first-project)
4.  [Section 3 — Parse the DSL Specification](#section-3--parse-the-dsl)
5.  [Section 4 — Generate the Django REST Backend](#section-4--generate-a-django-backend)
6.  [Section 5 — Run the Django Application](#section-5--run-the-django-application)
7.  [Section 6 — Test the API Endpoints](#section-6--test-the-generated-api)
8.  [Section 7 — Add Relationships (Foreign Keys)](#section-7--add-relationships)
9.  [Section 8 — Evolve the Schema (Diff & Plan)](#section-8--evolve-the-schema)
10. [Section 9 — Heuristic Rename Detection](#section-9--rename-detection)
11. [Section 10 — Type Change Auditing & Risks](#section-10--type-change-detection)
12. [Section 11 — Cascade Impact Analysis](#section-11--impact-analysis)
13. [Section 12 — Destructive Change Warnings](#section-12--destructive-changes)
14. [Section 13 — Live Hot-Reloading Watch Mode](#section-13--watch-mode)
15. [Section 14 — APIForge vs. Writing Django Manually](#section-14--how-this-compares-to-django)
16. [Section 15 — Internal Compiler Architecture](#section-15--internal-compiler-architecture)

---

## Introduction

### What is APIForge?
APIForge is an incremental API schema compiler and database evolution engine. It compiles a custom, declarative `.api` Domain-Specific Language (DSL) into a fully structured, operational Django REST Framework backend application.

### What Problem Does it Solve?
Building REST APIs manually in Django is tedious and boilerplate-heavy. For every resource, you must:
1.  Define a database model class in `models.py`.
2.  Write a serializer class in `serializers.py`.
3.  Implement a ViewSet controller in `views.py`.
4.  Wire up routes in `urls.py`.
5.  Manage Django configuration files and command execution scripts.

When schemas evolve (e.g. field renames or type modifications), keeping the entire pipeline consistent manually is error-prone. Standard migration tools often default to dropping columns and tables, resulting in immediate database data loss.

### How it Differs from Manually Writing Django Code
Instead of writing and wiring multiple Python files, you write a single, declarative schema file like this:
```dsl
resource Product {
    name string
    price decimal
}
```
The compiler parses this file and automatically scaffolds the entire multi-file Django structure, ensuring configuration accuracy.

### How it Differs from AI Code Generation
AI generation tools (e.g. ChatGPT, Claude) generate code fragments based on probabilistic text matching. They can introduce casing errors, omit configuration parameters, or hallucinate dependencies. 
APIForge is a **deterministic compiler**. It parses your DSL, builds a structured Abstract Syntax Tree (AST), validates syntax and referential integrity against strict semantic constraints, and guarantees compilation success.

---

## SECTION 1 — INSTALLATION

Let's start by installing APIForge on your development system.

### Installation Step-by-Step

Run the following commands in your terminal shell:

1.  **Clone the code repository:**
    ```bash
    git clone https://github.com/VaishnaviRai287/Django_Complier.git
    cd Django_Complier
    ```
    *   **Why:** Downloads the project code and moves your terminal shell into the root repository folder.

2.  **Initialize the Python Virtual Environment:**
    ```bash
    python3 -m venv .venv
    ```
    *   **Why:** Creates an isolated virtual environment (`.venv/`) to separate project dependencies from your system-wide Python installation.

3.  **Activate the Virtual Environment:**
    *   **On macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   **Why:** Configures your terminal session to use the virtual environment's Python interpreter and command executables.

4.  **Install APIForge in Editable Mode:**
    ```bash
    pip install -e .
    ```
    *   **Why:** Installs the compiler dependencies (`Click`, `Django`, `djangorestframework`) and links the command executable `apiforge` directly to your local code, allowing any code modifications to apply immediately.

#### Expected Output
```text
Obtaining file:///Users/prashantkumar/Documents/APIForge
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build wheel ... done
  Preparing editable metadata (pyproject.toml) ... done
Collecting click>=8.1.0 (from apiforge==0.1.0)
Collecting django>=4.2 (from apiforge==0.1.0)
Collecting djangorestframework>=3.14 (from apiforge==0.1.0)
Installing collected packages: click, django, djangorestframework, apiforge
  Running setup.py develop for apiforge
Successfully installed apiforge click django djangorestframework
```

### Verification & Troubleshooting

Verify that the CLI is installed and operational:
```bash
apiforge info
```
*Expected output:*
```text
APIForge v0.1.0
Phase: 13 — Schema Evolution Intelligence
Status: CLI operational

Run 'apiforge --help' to see available commands.
```

> [!TIP]
> **Troubleshooting Activation Errors:**
> If the `apiforge` command is not found, verify that your virtual environment is active (you should see `(.venv)` prefixed in your shell command prompt). If you receive execution permission errors on Windows, run PowerShell as Administrator and execute `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` to allow local script runs.

---

## SECTION 2 — CREATE YOUR FIRST PROJECT

Let's write a simple DSL file to represent a retail product.

### Create the Workspace Directory

Navigate to a clean working directory and create your project file:

```bash
mkdir ecommerce
cd ecommerce
```

Create a file named `ecommerce.api` containing the following schema:

```dsl
resource Product {
    name string
    price decimal
}
```

### Explaining the DSL Syntax
*   `resource Product { ... }`: Defines a data entity (resource) named `Product`. This compiles to a Django model database table.
*   `name string`: Declares a field named `name` of type `string`.
*   `price decimal`: Declares a field named `price` of type `decimal` (suitable for currency calculations).

---

## SECTION 3 — PARSE THE DSL

Before compiling code, let's verify what the front-end parser understands by inspecting the compiler's Abstract Syntax Tree (AST).

Run the parse command:
```bash
apiforge parse ecommerce.api
```

#### Expected Output
```json
{
    "resources": [
        {
            "resource": "Product",
            "fields": [
                {
                    "name": "name",
                    "type": "string"
                },
                {
                    "name": "price",
                    "type": "decimal"
                }
            ]
        }
    ]
}
```

### What is Happening Internally?
The parser scans your file, validates that brackets match, checks casing conventions, and compiles the text tokens into a structured JSON dictionary. The keys `resource` and `fields` represent parsed AST nodes.

---

## SECTION 4 — GENERATE A DJANGO BACKEND

Now compile the DSL specification into a fully runnable, complete Django REST project.

Run the generator:
```bash
apiforge generate ecommerce.api
```

#### Expected Output
```text
Successfully generated Django app at: /Users/prashantkumar/Documents/APIForge/ecommerce/generated

Compilation Report

Resources: 1
Fields: 2
Relationships: 0

Generated Files:
✓ models.py
✓ serializers.py
✓ views.py
✓ urls.py

Compilation Time: 1 ms
```

### Generated File Structures

The compiler scaffolds a standalone Django folder named `generated/` containing:

1.  **`generated/app/models.py`:**
    ```python
    from django.db import models

    class Product(models.Model):
        name = models.CharField(max_length=255)
        price = models.DecimalField(max_digits=10, decimal_places=2)

        def __str__(self):
            return str(self.name)
    ```
    *   **Why:** Declares the database table layout mapping DSL types to Python Django ORM fields. It automatically generates a smart `__str__` method preferring the text field `name`.

2.  **`generated/app/serializers.py`:**
    ```python
    from rest_framework import serializers
    from .models import Product

    class ProductSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = '__all__'
    ```
    *   **Why:** Translates Django database record objects to clean JSON strings for API inputs and outputs.

3.  **`generated/app/views.py`:**
    ```python
    from rest_framework import viewsets
    from .models import Product
    from .serializers import ProductSerializer

    class ProductViewSet(viewsets.ModelViewSet):
        queryset = Product.objects.all()
        serializer_class = ProductSerializer
    ```
    *   **Why:** The controller mapping incoming HTTP verb routes to Django database queries.

4.  **`generated/app/urls.py`:** Registers the endpoint paths (e.g. `/api/products/`) on a REST Framework default router routing table.

---

## SECTION 5 — RUN THE DJANGO APPLICATION

Now, let's start the database and run the server.

### Execute Database Migrations

From your root workspace directory, apply the database schema:

```bash
apiforge apply
```

#### Expected Output
APIForge locates the generated project and runs migrations programmatically:

```text
Locating generated project at 'generated'...
Running makemigrations...
Migrations for 'app':
  app/migrations/0001_initial.py
    + Create model Product
Running migrate...
Operations to perform:
  Apply all migrations: app, auth, contenttypes
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying app.0001_initial... OK

Migration successfully applied!
```

### Start the Server

Navigate into the generated project folder:
```bash
cd generated
```

Run the Django REST dev server:
```bash
python manage.py runserver
```

#### Expected Output
```text
System check identified no issues (0 silenced).
June 06, 2026 - 23:30:15
Django version 4.2.11, using settings 'settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Exploring the Browsable API in the Browser

Open your web browser and navigate to:
`http://127.0.0.1:8000/api/`

By default, the page displays the **Api Root** directory. 
*   **Verify Endpoint Links:** If you see parser/renderer metadata instead of resource links, click the blue **`GET`** dropdown next to the `OPTIONS` button to pull the standard JSON directory, which lists the `"products"` path.
*   **Navigate to Resource View:** Click the `"products"` link or navigate to `http://127.0.0.1:8000/api/products/`.
*   **Submit Forms directly:** Scroll to the bottom of the `/api/products/` screen. You will see a styled HTML input form. Enter values for `name` and `price`, then click **`POST`** to create a product record directly in the database without writing curl commands!

---

## SECTION 6 — TEST THE GENERATED API

Keep the server running. Open a new terminal tab or window, make sure you activate the virtual environment (`source .venv/bin/activate`), and test your backend REST endpoints.

### 1. Create a Product (POST)
Send a JSON payload to add a product record:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Developer Keyboard", "price": "149.99"}' \
  http://127.0.0.1:8000/api/products/
```
*Response:*
```json
{"id":1,"name":"Developer Keyboard","price":"149.99"}
```

### 2. Read All Products (GET)
List all active items:
```bash
curl http://127.0.0.1:8000/api/products/
```
*Response:*
```json
[{"id":1,"name":"Developer Keyboard","price":"149.99"}]
```

### 3. Update the Product (PUT)
Update the product pricing:
```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{"name": "Mechanical Keyboard", "price": "169.50"}' \
  http://127.0.0.1:8000/api/products/1/
```
*Response:*
```json
{"id":1,"name":"Mechanical Keyboard","price":"169.50"}
```

### 4. Remove the Product (DELETE)
Delete the record from the database:
```bash
curl -X DELETE http://127.0.0.1:8000/api/products/1/
```
*Response:* (Empty `204 No Content` status response code).

---

## SECTION 7 — ADD RELATIONSHIPS

Real-world database backends use relational links between tables. Let's add relationships to our e-commerce schema using the `belongs_to` keyword.

Navigate back to the folder containing `ecommerce.api` and replace its content with:

```dsl
resource Customer {
    name string
    email email
}

resource Product {
    name string
    price decimal
}

resource Order {
    customer belongs_to Customer
    product belongs_to Product
}
```

### Explaining belongs_to
*   `customer belongs_to Customer`: Creates a link indicating that every Order is owned by a Customer.
*   The code generator compiles this directly to a foreign key model layout:
    `customer = models.ForeignKey('Customer', on_delete=models.CASCADE)`

Compile the relational schema:
```bash
apiforge generate ecommerce.api
```
Verify that the generated views, serializers, and URL maps support relationships automatically.

---

## SECTION 8 — EVOLVE THE SCHEMA

Now, let's learn how to evolve our schema safely.

### The Business Requirement
You are asked to add inventory tracking by adding a `stock` field to products.

Open `ecommerce.api` in your editor and add `stock integer` to `Product`:

```dsl
resource Customer {
    name string
    email email
}

resource Product {
    name string
    price decimal
    stock integer
}

resource Order {
    customer belongs_to Customer
    product belongs_to Product
}
```

### Step 1: Audit Structural Diffs
Compare your live code edits against the baseline snapshot using `diff`:

```bash
apiforge diff ecommerce.api
```

#### Expected Output
```text
Added field:
  Product.stock
```

### Step 2: Review the Evolution Plan
Execute `plan` to check the migration operation list and risk evaluations:

```bash
apiforge plan ecommerce.api
```

#### Expected Output
```text
Migration Plan

[SAFE]
AddField(Product.stock)

Affected Resources

  Product

Affected Generated Components

  product/models.py
  product/serializers.py
```

*   **Why this matters:** The snapshot engine enables the diff engine to look back at your initial schema and identify changes incrementally.

---

## SECTION 9 — HEURISTIC RENAME DETECTION

Standard database tools treat a field rename as two separate steps: a deletion of the old field (data loss) and the addition of a new blank field (data missing). APIForge uses heuristics to detect renames automatically.

Let's rename `price` to `unit_price` in the `Product` resource:

```dsl
resource Product {
    name string
    unit_price decimal
    stock integer
}
```

Auditing the differences:
```bash
apiforge diff ecommerce.api
```

#### Expected Output
```text
Possible Rename Detected

  Product.price
  →
  Product.unit_price

  Confidence: 92%
```

Verify the migration plan:
```bash
apiforge plan ecommerce.api
```

#### Expected Output
```text
Migration Plan

[SAFE]
RenameField(Product.price → unit_price)

Affected Resources

  Product

Affected Generated Components

  product/models.py
  product/serializers.py
```

### How the Heuristic Math Works
The diff engine uses sequence matching, type equivalence, and relative positional indexing to pair removed and added fields. Since the types match (`decimal`), the base confidence starts at `70%`. Name similarity and index layout calculation raises confidence to `92%`. 

This allows you to preserve database column data during development.

---

## SECTION 10 — TYPE CHANGE DETECTION

What happens when we change the data type of an existing field? Let's change `unit_price decimal` to `unit_price integer` to check.

Modify `ecommerce.api`:
```dsl
resource Product {
    name string
    unit_price integer
    stock integer
}
```

Execute the diff:
```bash
apiforge diff ecommerce.api
```
*Expected diff output:*
```text
Field Type Changed

  Product.unit_price

  decimal
  →
  integer
```

Execute the plan:
```bash
apiforge plan ecommerce.api
```

#### Expected Output
```text
Migration Plan

[WARNING]
ChangeType(Product.unit_price)
decimal → integer

Potential precision loss (fractional digits will be truncated).

Affected Resources

  Product

Affected Generated Components

  product/models.py
  product/serializers.py
```

### How Risks Work
*   **WARNING Risk:** APIForge automatically checks data type conversions. Changing a decimal to an integer results in decimal digit truncation, so it raises a `[WARNING]` risk indicator to warn you before database schema execution.

---

## SECTION 11 — IMPACT ANALYSIS

In relational databases, resources are tightly linked. Changing a parent table cascades to children components. Let's test this by renaming the `Customer` resource to `Client`.

Modify the DSL:
```dsl
resource Client {
    name string
    email email
}

resource Product {
    name string
    unit_price integer
    stock integer
}

resource Order {
    customer belongs_to Client
    product belongs_to Product
}
```

Run the plan:
```bash
apiforge plan ecommerce.api
```

#### Expected Output
```text
Migration Plan

[SAFE]
RenameResource(Customer → Client)

Affected Resources

  Client
  Order

Affected Generated Components

  client/models.py
  client/serializers.py
  order/models.py
  order/serializers.py
  order/views.py
```

### Tracing Relational Cascades
APIForge builds a directed graph of schema relationships. When the `Customer` parent resource is renamed to `Client`, the cascade dependency algorithm automatically traces the relationship graph using BFS. It identifies that `Order` (child) is affected, indicating that downstream files like `order/models.py` and `order/serializers.py` will require updates.

---

## SECTION 12 — DESTRUCTIVE CHANGES

Let's test deleting an existing schema field to inspect data loss warnings.

Remove `stock` from `Product`:
```dsl
resource Product {
    name string
    unit_price integer
}
```

Run the plan:
```bash
apiforge plan ecommerce.api
```

#### Expected Output
```text
Migration Plan

[DESTRUCTIVE]
RemoveField(Product.stock)

Data loss possible (column will be dropped).

Affected Resources

  Product

Affected Generated Components

  product/models.py
  product/serializers.py
```

### Why This is Important
`[DESTRUCTIVE]` warnings serve as safety blocks. Seeing this tells you that running migrations will permanently delete database column data.

---

## SECTION 13 — WATCH MODE

Using the watch mode daemon allows you to see diffs and plans update live in your terminal as you edit schema files.

Launch the watcher:
```bash
apiforge watch ecommerce.api
```

Open `ecommerce.api` in your editor, add `discount decimal` to `Product`, and save:

```dsl
resource Product {
    name string
    unit_price integer
    discount decimal
}
```

#### Expected Watcher Output
The console clears instantly and displays the live diff and plan:

```text
--- Change detected at 23:40:12 ---

[Schema Diff]
Added field:
  Product.discount

[Migration Plan]
Migration Plan

[SAFE]
AddField(Product.discount)

========================================
```

Press `Ctrl+C` to terminate the watch daemon.

---

## SECTION 14 — HOW THIS COMPARES TO DJANGO

Let's compare the code required to build and evolve this application in raw Django vs. APIForge:

### 1. Traditional Django Workflow
For every schema iteration, you must open, modify, and coordinate multiple python files:

```text
┌──────────────┐   ┌────────────────────┐   ┌────────────────┐   ┌──────────────┐
│  models.py   │-->│   serializers.py   │-->│    views.py    │-->│   urls.py    │
└──────────────┘   └────────────────────┘   └────────────────┘   └──────────────┘
```

If you add a relationship or rename a field, you must manually rewrite Python code classes in all four files.

### 2. APIForge Workflow
You write and modify a single declarative DSL file:

```text
┌─────────────────┐        ┌─────────────────┐        ┌─────────────┐
│  ecommerce.api  │ -----> │  apiforge compiler│ -----> │  Django App │
└─────────────────┘        └─────────────────┘        └─────────────┘
```

The compiler handles validation, cascade detection, and coordinates Django project directories automatically.

---

## SECTION 15 — INTERNAL COMPILER ARCHITECTURE

APIForge compiles files through a structured pipeline:

```text
                     RAW DSL FILE (ecommerce.api)
                                 │
                                 ▼
                     LEXER SCANNER (lexer.py)
                                 │
                                 ▼ (Token stream)
                      LL(1) PARSER (parser.py)
                                 │
                                 ▼ (Abstract Syntax Tree)
                   SEMANTIC VALIDATOR (semantic.py)
                                 │
                                 ├────────────────────────┐
                                 ▼                        ▼
                   STATE SNAPSHOT (snapshot.py)     DJANGO GENERATOR (codegen.py)
                                 │                        │
                                 ▼                        ▼
                     DIFF ENGINE (diff.py)           STANDALONE APP (generated/)
                                 │
                                 ▼ (Differences)
                    MIGRATION PLANNER (planner.py)
                                 │
                                 ▼ (Cascade BFS Graph)
                         CLI / USER REPORTS
```

### Compiler Pass Descriptions
*   **Lexer Scanner:** Consumes characters and outputs a stream of structured Tokens containing coordinates (line numbers) for error reporting.
*   **LL(1) Parser:** Implements recursive descent to parse Token streams into AST nodes.
*   **Semantic Validator:** Checks syntax correctness, name casings, referential target integrity, and recommends corrections for unknown field types.
*   **Django Generator:** Scaffolds views, serializers, models, settings, and URLs in python.
*   **Snapshot System:** Stores baseline state representations in Git-ignored JSON format.
*   **Diff Engine:** Computes additions, deletions, renames, and type updates.
*   **Migration Planner:** Runs type coercion analysis, evaluates risks, and traverses relational cascades.


