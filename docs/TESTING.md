# Test checklist

`php tests/run-tests.php` covers the database-free logic. The flows below need
a running database and are checked by hand against a freshly loaded
`database/library.sql`.

## Setup

```bash
mysql -u root -p < database/library.sql
php -S localhost:8000
```

## Authentication

| # | Steps | Expected |
|---|---|---|
| A1 | Sign up with a 9-digit mobile number | Rejected: "Mobile number must be exactly 10 digits" |
| A2 | Sign up with a 6-character password | Rejected: minimum 8 characters |
| A3 | Sign up with an e-mail already registered | AJAX warns while typing; the insert is refused with a clear message |
| A4 | Complete a valid signup | Card number shown (`SID017`, `SID018`, …); the counter in `studentid.txt` advances |
| A5 | Log in with a wrong password | "Invalid e-mail address or password" |
| A6 | Log in with an unregistered e-mail | *The same* message as A5 (no account enumeration) |
| A7 | Admin blocks the member, member logs in | "Your account has been blocked" |
| A8 | Log in as `admin` / `Test@123` | Admin dashboard; `admin.Password` is already bcrypt |
| A9 | `UPDATE admin SET Password = MD5('Test@123')`, then log in | Login succeeds **and** the stored value is bcrypt again afterwards |

## Circulation

| # | Steps | Expected |
|---|---|---|
| C1 | Issue a book to a valid member | Success message naming the due date; `tblbooks.Count` drops by one |
| C2 | Issue the same title to the same member again | Refused: already holds a copy |
| C3 | Issue until the member holds `MAX_BOOKS_PER_USER` | The next issue is refused with the limit message |
| C4 | Issue a title whose `Count` is 0 | Refused: all copies on loan |
| C5 | Issue to a blocked member | Refused: account blocked |
| C6 | Return a book | `Count` restored, `RetrunStatus = 1`, `ReturnDate` stamped, fine added to `tblstudents.fines` |
| C7 | Return the same loan twice (browser back, submit again) | Second attempt reports the loan is already closed; the count is credited once |
| C8 | `UPDATE tblissuedbookdetails SET IssuesDate = NOW() - INTERVAL 20 DAY WHERE id = <n>` | Member and admin views show "overdue by 6 day(s)"; the return screen pre-fills a fine of 6 × `FINE_PER_DAY` |
| C9 | Override the pre-filled fine with `0` and return | The loan closes with no fine (waiver path) |

## Catalogue and members

| # | Steps | Expected |
|---|---|---|
| M1 | Delete a book that has an open loan | Refused with an explanation |
| M2 | Delete a category referenced by a book | Refused with an explanation |
| M3 | Add a book with an ISBN that already exists | Refused (unique key), not a fatal error |
| M4 | Add a book with a new author | A row appears in `tblauthors` and `AuthorId` is set |
| M5 | Search the catalogue by author surname and by ISBN | Both match |
| M6 | Block then re-activate a member | Status toggles; the action is a POST |

## Requests

| # | Steps | Expected |
|---|---|---|
| R1 | Raise a request as member A, then log in as member B | B sees only their own requests |
| R2 | Approve a request in the admin panel | Status becomes "Approved" for that member; the status filter works |

## Security spot checks

| # | Steps | Expected |
|---|---|---|
| S1 | Open `dashboard.php`, `issued-books.php`, `admin/manage-books.php` while logged out | Redirected to the relevant login page |
| S2 | Submit any POST form with the `csrf_token` field removed (browser dev tools) | HTTP 400, no state change |
| S3 | Request `issued-books.php?del=1` as a member | Nothing is deleted — the parameter no longer exists |
| S4 | Register a member whose name is `<script>alert(1)</script>` | The name renders as text everywhere it appears |
| S5 | Log in and inspect the session cookie | `HttpOnly` set; the session ID differs from the pre-login one |
| S6 | Enter `' OR '1'='1` in the login and search fields | Treated as a literal string |
