
---

## What `relation "sum_core_homepage" does not exist` actually means

That error is very specific:

> `django.db.utils.ProgrammingError: relation "sum_core_homepage" does not exist`

In Django-land:

* A **“relation”** is a database table.
* `"sum_core_homepage"` is the table name Django/Wagtail expects for a model whose:

  * `app_label` = `sum_core`
  * model name = `HomePage`
* So **some code in your tests is trying to query or insert into a model called `HomePage` in the `sum_core` app**, and there is **no table** for it in the test DB.

That can only happen if:

1. There *is* a `sum_core.HomePage` model with no migrations, or
2. The test is importing the wrong `HomePage` class (e.g. from `sum_core` instead of the `home` app), or
3. A migration exists but the app isn’t in `INSTALLED_APPS` for the test settings (less likely here, because everything was green before this task).

Given everything passed before M2-004, the most likely culprit is:

> The new tests (or the new code) are using the **wrong HomePage model**.

You already have a working `HomePage` in the **`home` app** (the test project), whose table is `home_homepage`. That’s the one all the existing tests were using successfully.

---

## Step 1 – Find who’s asking for `sum_core_homepage`

You don’t need to guess; you can go straight to the code and fix the references.

Look in the files the agent created/modified:

* `tests/blocks/test_testimonials_block.py`
* `tests/templates/test_homepage_rendering.py`
* any new imports in `core/sum_core/blocks/testimonials.py`
* any changes it made in `home/models.py`

You’re specifically hunting for:

```python
from sum_core.models import HomePage
# or
from sum_core import HomePage
# or
apps.get_model("sum_core", "HomePage")
# or
"sum_core_homepage" as db_table
```

If you see anything like that, that’s your smoking gun.

**What you want instead** is the `HomePage` from the test project’s `home` app, which lives at:

```python
from home.models import HomePage
```

That model uses the table `home_homepage`, which definitely *does* exist in your test DB (because earlier tests were passing and we migrated it in Milestone 1).

---

## Step 2 – Fix the tests to use the right HomePage

A very likely pattern in `tests/templates/test_homepage_rendering.py` is something like:

```python
from django.test import Client
from django.urls import reverse

from sum_core.models import HomePage  # ❌ likely wrong
```

Change that to:

```python
from django.test import Client
from django.urls import reverse

from home.models import HomePage  # ✅ correct test project HomePage
```

Then, wherever the test is creating or querying pages, it should be doing something like:

```python
@pytest.mark.django_db
def test_homepage_renders_testimonials_block(root_page):
    homepage = HomePage(
        title="Home",
        slug="home",
        body=[ ... testimonials block data ... ],
    )
    root_page.add_child(instance=homepage)
    homepage.save_revision().publish()

    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Testimonials" in response.content.decode()
```

Key point: the `HomePage` here is from `home.models`, not from any `sum_core` models.

---

## Step 3 – Make block tests DB-free where possible

Your **block** tests in `tests/blocks/test_testimonials_block.py` almost never need the database.

A good pattern is:

```python
from sum_core.blocks.testimonials import TestimonialsBlock

def test_testimonials_block_accepts_valid_data():
    block = TestimonialsBlock()
    value = block.to_python({
        "heading": "What our customers say",
        "intro": "<p>Intro text</p>",
        "testimonials": [
            {
                "quote": "Great work",
                "author_name": "Jane Smith",
                "company": "Solar House",
                "rating": 5,
                "photo": None,
            }
        ],
    })
    html = block.render(value)
    assert "Great work" in html
    assert "Jane Smith" in html
```

Notice:

* No `@pytest.mark.django_db`.
* No page creation.
* No reference to `HomePage` or the database at all.

If the agent added `@pytest.mark.django_db` to these tests and then used a `HomePage` there, that would also hit the missing table. Strip DB usage out of block tests unless there’s a very specific reason to involve pages.

---

## Step 4 – If (and only if) there is a real `sum_core.HomePage`

If you discover that the agent actually **created a new `HomePage` class inside `sum_core`** (e.g. in `core/sum_core/models.py` or similar), you’ve got two options:

1. **Preferable for now** – delete that new `HomePage` and keep all page models in the `home` app (test project only) until we later formalise shared core page types in another milestone; or

2. **If you truly want a `sum_core.HomePage`** – you must:

   * Add `sum_core` to `INSTALLED_APPS` for the test project (if not already).
   * Run `python core/sum_core/test_project/manage.py makemigrations sum_core`.
   * Run `python core/sum_core/test_project/manage.py migrate`.
   * Ensure tests also see those migrations.

Given our current plan, we’ve been deliberately keeping page models in the `home` test app and **not** defining core pages in `sum_core` yet, so I’d strongly lean towards option 1: remove any accidental `sum_core.HomePage` and point everything at `home.HomePage`.

---

## Step 5 – Re-run tests and sanity-check

Once you’ve:

* Fixed imports to use `home.models.HomePage`,
* Removed unnecessary DB usage from block tests,

run:

```bash
make test
```

You should see:

* No more `relation "sum_core_homepage" does not exist`.
* Existing Milestone 0/1 tests still green.
* New testimonials tests passing.

If any tests still mention `sum_core_homepage` in the traceback, search the repo for that string and clean up the remaining reference.

---

