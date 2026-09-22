# Architecture notes

Companion to the README: why the code is arranged this way, and what happens on
the two requests that matter most.

## 1. Layering in a framework-free PHP app

There is no framework here, so the layering is a convention rather than
something the runtime enforces:

* **Page scripts** (`*.php`, `admin/*.php`) handle one HTTP request each. They
  read input, call one or more `lms_*` helpers, and render HTML.
* **`includes/config.php`** is the single bootstrap. It resolves credentials,
  defines the policy constants, opens the PDO handle and pulls in the helper
  files. `admin/includes/config.php` is a one-line `require` of it, so there is
  exactly one place where the connection is configured.
* **`includes/auth.php`** owns sessions, passwords, CSRF and escaping.
* **`includes/library.php`** owns the circulation rules.

The rule of thumb when editing: if a change would alter *what the library
permits*, it belongs in `library.php`; if it alters *what the page looks like*,
it belongs in the page.

### PDO settings and why they matter

```php
PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION
PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ
PDO::ATTR_EMULATE_PREPARES   => false
```

`ERRMODE_EXCEPTION` means a failed write cannot pass unnoticed — the original
code checked `lastInsertId()` and assumed success otherwise.
`EMULATE_PREPARES => false` sends parameters to the server separately from the
SQL text. It also means **a named placeholder may not be used twice in one
statement**; queries that need the same value in several places bind `:q1`,
`:q2`, `:q3` (see `available-books.php`).

## 2. Request walkthrough: issuing a book

`admin/issue-book.php`

1. `lms_require_admin()` redirects anonymous requests to the login page.
2. `lms_csrf_verify()` rejects a POST whose token does not match the session.
3. `lms_issue_blocker($dbh, $studentId, $bookId)` returns either `null` or the
   single reason the loan is refused: unknown member, blocked account, no copy
   on the shelf, the member already holds that title, or the loan limit is
   reached. Collecting the checks in one function keeps the page from
   accumulating half of them.
4. `lms_issue_book()` opens a transaction, takes a **locking read of the member
   row** (`SELECT Status ... FOR UPDATE`) and re-checks the per-member rules
   inside it. The blocker's answer in step 3 is only a snapshot: two issues for
   the same member submitted at once would both pass it, and a stress run
   confirmed this — eight concurrent issues left one member holding eight books
   against a limit of three. The row lock serialises every concurrent issue for
   that member, so the second one sees the first. Then it runs:

   ```sql
   UPDATE tblbooks SET Count = Count - 1 WHERE id = :id AND Count > 0;
   INSERT INTO tblissuedbookdetails (StudentID, BookId) VALUES (:sid, :bid);
   ```

   The `AND Count > 0` guard is the concurrency control for the shelf count: if
   two librarians issue the last copy at the same moment, the second `UPDATE`
   matches zero rows, the transaction is rolled back and the page reports that
   the copy has just gone. Checking availability in PHP and then decrementing
   would lose that race.

   The two guards are different in kind and worth keeping straight. The copy
   count is protected by a condition *inside the write* — no lock needed. The
   per-member rules cannot be expressed that way, so they need the row lock
   above. `tests/stress/race_loan_limit.py` is the regression test for the
   second case.

## 3. Request walkthrough: returning a book

`admin/update-issue-bookdeails.php` → `lms_return_book()`

1. The ledger row is selected `FOR UPDATE`, which locks it for the transaction
   and makes a double return impossible.
2. An already-closed loan returns `false` — the page reports it rather than
   crediting a second copy to the shelf.
3. Otherwise, within one transaction: the loan is closed with its fine and
   return date, `tblbooks.Count` is incremented, and the fine is added to
   `tblstudents.fines`.

Restoring the copy count is a bug fix: the earlier code decremented on issue and
never incremented on return, so the catalogue slowly drained to zero.

## 4. Password migration

`tblstudents.Password` and `admin.Password` are `VARCHAR(255)` and may hold
either a bcrypt hash or a legacy 32-character md5 digest.

```
login → lms_verify_password()
          ├── stored value matches /^[a-f0-9]{32}$/i → hash_equals(md5(input))
          └── otherwise                              → password_verify(input)
       → lms_password_needs_rehash() → lms_upgrade_password()  (writes bcrypt)
```

The digest is therefore accepted exactly once per account; after that login the
row holds a bcrypt hash. This lets an existing deployment upgrade without
resetting anyone's password, and the legacy branch can be deleted later by
removing the `preg_match` case in `lms_verify_password()`.

## 5. Identifiers

Members are keyed by two things: the surrogate `tblstudents.id` and the
human-readable card number `StudentId` (`SID017`). The ledger and the request
table join on the card number, because that is what a librarian reads off a
card at the desk.

The next card number is allocated by `lms_next_student_id()`, which opens
`studentid.txt` with `LOCK_EX`, relies on PHP's string increment
(`"SID099"` → `"SID100"`), writes it back and releases the lock. The original
read-then-write had no lock, so two simultaneous signups could take the same
number; the unique key on `StudentId` would now reject the duplicate anyway.

## 6. Flash messages

Actions that redirect (issue, return, delete, block) leave a message in the
session with `lms_flash_set()`; the destination page renders and clears it with
`lms_flash_render()`. This replaced four hand-written variants that each read a
session key, printed it, and cleared it by assigning `""` inside an
`htmlentities()` call.

## 7. What is deliberately unchanged

The Bootstrap 3 / jQuery 1.10 front end, the page-per-URL structure and the
table names (including the `RetrunStatus` misspelling) are original. Renaming a
column would break nothing visible but would make this repository harder to
compare against the coursework version it grew from.
