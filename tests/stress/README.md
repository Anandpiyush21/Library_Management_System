# Stress and static-analysis harness

The application is PHP, but these checks are Python. That is deliberate: they
run with nothing installed but `python3`, so the design can be verified on a
machine that has no PHP or MySQL — which is exactly where this harness was
written. They test the **design**: the SQL contract, the schema constraints and
the circulation algorithm. They do **not** execute the PHP. `php
tests/run-tests.php` and `docs/TESTING.md` cover that side.

Run everything from the project root:

```bash
python3 tests/stress/schema_check.py        # every table/column in the PHP exists in the schema
python3 tests/stress/bind_check.py          # every SQL placeholder is bound exactly once
python3 tests/stress/guard_check.py         # auth guard + CSRF coverage, page by page
python3 tests/stress/stress.py              # 20,000-operation fuzz against the invariants
python3 tests/stress/scenarios.py           # contention, races, fine boundaries, seed data
python3 tests/stress/race_loan_limit.py     # concurrent issues to one member
```

## How the circulation logic is tested

`stress.py` ports `includes/library.php` statement-for-statement onto SQLite —
`ddl.py` translates the real DDL from `database/library.sql`, keeping the
primary, unique and foreign keys — and then drives issue/return hard while
asserting after every 250 operations:

| | Invariant |
|---|---|
| I1 | `tblbooks.Count` is never negative |
| I2 | shelf count + open loans = total copies, for every title |
| I3 | no member exceeds `MAX_BOOKS_PER_USER` open loans |
| I4 | no member holds two open loans of the same title |
| I5 | closed loans have a return date; open loans do not |
| I6 | `tblstudents.fines` equals the sum of that member's closed-loan fines |

## Fidelity limits

* SQLite serialises writers across the whole database; MySQL/InnoDB relies on
  the row lock taken by `SELECT ... FOR UPDATE`. The harness therefore shows
  that the *algorithm* is correct when the transactions are serialised, not
  that MySQL takes the lock it is asked for.
* SQLite has no `FOR UPDATE`, so `BEGIN IMMEDIATE` stands in for it.
* Datatypes are approximate (`DECIMAL` → `REAL`), so the harness would not
  catch a rounding difference in MySQL's fixed-point arithmetic.
* Nothing here exercises PHP itself: sessions, CSRF enforcement at runtime,
  output escaping and the AJAX endpoints are checked statically by
  `guard_check.py` and by hand via `docs/TESTING.md`.

## What this harness found

A TOCTOU race in `lms_issue_book()`. The per-member rules (loan limit,
duplicate title, blocked account) were evaluated by `lms_issue_blocker()`
*before* the transaction opened, so eight simultaneous issues to one member all
passed the check: 38 of 40 trials exceeded the limit, one member ending up with
8 books against a limit of 3. The copy count was never affected, because its
guard (`AND Count > 0`) is part of the `UPDATE` inside the transaction.

The fix re-checks the per-member rules inside the transaction behind a locking
read of the member row. `race_loan_limit.py` is the regression test: 0 of 40
trials now exceed the limit.
