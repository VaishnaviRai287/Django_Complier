# APIForge Schema Evolution Walkthrough (DEMO)

This guide takes you through a complete, step-by-step walkthrough of compiling, modifying, and evolving relational database schemas using APIForge (Phase 13).

---

## Tutorial Scenario: Building a Relational E-Commerce Backend

We will start with a baseline database schema representing customers and orders, compile it, apply evolutionary schema changes (renames, type shifts, additions), review risk levels and cascading impacts, and verify watch mode.

---

### Step 1: Write the Baseline Schema

Create a directory path `examples/` if it does not exist. Create a file named `examples/demo_shop.api` containing:

```dsl
resource Customer {
    name string
    email email
}

resource Order {
    customer belongs_to Customer
    price decimal
}
```

---

### Step 2: Compile & Establish the Baseline

Compile the schema into a Django project. Run the following command in your terminal:

```bash
apiforge generate examples/demo_shop.api
```

#### Expected Output
The compiler runs all passes (Lexer $\to$ Parser $\to$ Semantic Analyzer $\to$ Codegen $\to$ Snapshot), outputs a compilation metrics summary, and caches the snapshot in `.apiforge/schema.json`:

```text
Successfully generated Django app at: /Users/prashantkumar/Documents/APIForge/generated

Compilation Report

Resources: 2
Fields: 3
Relationships: 1

Generated Files:
✓ models.py
✓ serializers.py
✓ views.py
✓ urls.py

Compilation Time: 2 ms
```

Verify that the snapshot matches the parsed DSL:
```bash
apiforge snapshot
```

---

### Step 3: Boot the Django Backend

To see the generated code in action, navigate to the generated directory, create migrations, run them, and boot the server:

```bash
cd generated/
python manage.py makemigrations app
python manage.py migrate
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/api/`. You will see the Django REST Framework browsable API showing CRUD endpoints for:
*   `customers` (`http://127.0.0.1:8000/api/customers/`)
*   `orders` (`http://127.0.0.1:8000/api/orders/`)

---

### Step 4: Evolve the Schema

Return to the root workspace. Let's make the following updates to `examples/demo_shop.api`:
1.  **Rename a field:** Rename `name` to `full_name` in the `Customer` resource.
2.  **Change a field type:** Change the `price` field in `Order` from `decimal` to `integer` (warning risk).
3.  **Add fields:** Add `status string` to `Order`.
4.  **Add a new resource:** Add a `Product` resource.
5.  **Add relations:** Add an `OrderItem` resource that binds to both `Order` and `Product`.

Edit `examples/demo_shop.api` so it matches the following content:

```dsl
resource Customer {
    full_name string
    email email
}

resource Product {
    title string
    price decimal
}

resource Order {
    customer belongs_to Customer
    price integer
    status string
}

resource OrderItem {
    order belongs_to Order
    product belongs_to Product
}
```

---

### Step 5: Audit the Diff

Before updating files, verify how the diff engine groups structural changes. Run:

```bash
apiforge diff examples/demo_shop.api
```

#### Expected Output
The diff engine automatically identifies the field rename with a confidence score, flags the type shift, and notices the new resources:

```text
Added resource:
  Product
  OrderItem

Added field:
  Order.status

Possible Rename Detected

  Customer.name
  →
  Customer.full_name

  Confidence: 92%

Field Type Changed

  Order.price

  decimal
  →
  integer
```

---

### Step 6: Review Migration Risks & Component Cascades

To assess database conversion risks and see which generated files require modification due to relational dependencies, run the planner command:

```bash
apiforge plan examples/demo_shop.api
```

#### Expected Output
The planner reads the diff outputs, evaluates risk codes (`SAFE`, `WARNING`, `DESTRUCTIVE`), and traces incoming relationship cascading paths using BFS:

```text
Migration Plan

[SAFE]
AddResource(Product)

[SAFE]
AddResource(OrderItem)

[SAFE]
AddField(Order.status)

[SAFE]
RenameField(Customer.name → full_name)

[WARNING]
ChangeType(Order.price)
decimal → integer

Potential precision loss (fractional digits will be truncated).

Affected Resources

  Customer
  Order
  OrderItem
  Product

Affected Generated Components

  customer/models.py
  customer/serializers.py

  order/models.py
  order/serializers.py
  order/views.py

  orderitem/models.py
  orderitem/serializers.py
  orderitem/views.py

  product/models.py
  product/serializers.py
```

> [!NOTE]
> **Cascading Traversal Notice:**
> Changing `Order` cascaded to affect the `OrderItem` files. Because `OrderItem` references `Order` via a `belongs_to` relation, updates in the parent schema trigger rebuild warnings in downstream files.

---

### Step 7: Live Watch Mode Verification

To monitor changes continuously in your terminal, run:

```bash
apiforge watch examples/demo_shop.api
```

1.  Keep the watcher running.
2.  Open `examples/demo_shop.api` in your editor.
3.  Add `description string` to `Product`.
4.  Save the file.
5.  Watch the terminal instantly clear and print the updated live diff and plan:

```text
--- Change detected at 23:10:45 ---

[Schema Diff]
Added field:
  Product.description

[Migration Plan]
Migration Plan

[SAFE]
AddField(Product.description)

========================================
```

Press `Ctrl+C` to terminate the watch daemon.
