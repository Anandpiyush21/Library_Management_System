# Changelog

## Rework — documented reference implementation

The application keeps its original shape (framework-free PHP, Bootstrap 3 front
end, page-per-URL) and its table names. What changed:

### Added
- `database/library.sql` — the schema was never in the repository, so the
  project could not be installed. Seven tables with foreign keys, unique
  constraints, indexes, utf8mb4 and seed data.
- `includes/library.php` — circulation rules: due dates, fines, loan limits,
  and transactional issue / return.
- `includes/auth.php` — passwords, sessions, CSRF tokens, output escaping.
- `admin/includes/notify.php` — overdue reminder e-mail itemising each loan.
- `tests/run-tests.php` — 17 assertions over the database-free logic.
- `docs/ARCHITECTURE.md`, `docs/TESTING.md`, `README.md`, `LICENSE`,
  `.gitignore`, `includes/config.local.php.example`.
- Loan-policy constants (`LOAN_PERIOD_DAYS`, `FINE_PER_DAY`,
  `MAX_BOOKS_PER_USER`); due dates, overdue days and accruing fines surfaced in
  both portals; catalogue search over author and ISBN; ledger filters
  (all / on loan / overdue); request status filters.

### Fixed
- `issued-books.php` accepted `?del=<id>` and deleted the row from `tblbooks` —
  any logged-in member could erase the catalogue.
- Returning a book never restored `tblbooks.Count`, so the catalogue drained.
- `admin/dashboard.php` prepared the wrong statement, so "Registered Users"
  actually counted issue records.
- `admin/mail-student.php` filtered on `$_SESSION['stdid']`, never set for an
  admin session, so the overdue list was always empty.
- `book-requests.php` listed every member's requests to every member.
- `admin/send-email.php` was linked but did not exist; reminders now send.
- Book issuing decremented the copy count outside a transaction and without
  checking availability, the loan limit or duplicate loans.
- Signup allocated card numbers without a lock (two signups could collide).
- The per-member circulation rules (loan limit, duplicate title, blocked
  account) were checked before the issue transaction opened, so simultaneous
  issues to one member all passed: 38 of 40 stress trials exceeded the limit,
  worst case 8 books against a limit of 3. They are now re-checked inside the
  transaction behind a locking read of the member row (0 of 40 trials).

### Changed
- Passwords: unsalted md5 → bcrypt, with legacy digests accepted once and
  transparently upgraded on next login.
- All state changes moved from `GET` links to CSRF-protected `POST` forms.
- PDO: exceptions enabled, native prepares, utf8mb4.
- Output escaped through `e()`; `error_reporting(0)` replaced by error logging.
- Credentials read from the environment or a gitignored local file.
- Session cookies hardened; session ID regenerated on login.
