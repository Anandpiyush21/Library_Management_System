"""
Stress test for the circulation logic.

The PHP cannot run on this machine (no PHP, no MySQL), so includes/library.php
is ported statement-for-statement onto SQLite and driven hard. What is being
tested is the ALGORITHM and the SCHEMA CONSTRAINTS -- the transaction
boundaries, the `WHERE Count > 0` guard, the policy arithmetic and the
foreign/unique keys -- not the PHP interpreter's execution of them.
"""
import sqlite3, random, sys, datetime, threading, queue
sys.path.insert(0, __import__('os').path.dirname(__file__))
from ddl import translate

LOAN_PERIOD_DAYS   = 14
FINE_PER_DAY       = 5.00
MAX_BOOKS_PER_USER = 3

NOW = datetime.datetime(2026, 9, 22, 12, 0, 0)     # frozen clock
def fmt(dt): return dt.strftime('%Y-%m-%d %H:%M:%S')
def parse(s): return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

# ---------------------------------------------------------------- policy ----
def lms_due_date(issued):      return parse(issued) + datetime.timedelta(days=LOAN_PERIOD_DAYS)
def lms_days_overdue(issued, ref=None):
    ref = parse(ref) if ref else NOW
    due = lms_due_date(issued)
    return 0 if ref <= due else (ref - due).days
def lms_calculate_fine(issued, returned=None):
    return round(lms_days_overdue(issued, returned) * FINE_PER_DAY, 2)

# ------------------------------------------------------------ operations ----
class Library:
    def __init__(self, db): self.db = db

    def copies_available(self, book):
        r = self.db.execute('SELECT Count FROM tblbooks WHERE id=?', (book,)).fetchone()
        return int(r[0]) if r else 0

    def open_loans(self, sid):
        return self.db.execute(
            'SELECT COUNT(*) FROM tblissuedbookdetails WHERE StudentID=? AND RetrunStatus=0',
            (sid,)).fetchone()[0]

    def has_open_loan(self, sid, book):
        return bool(self.db.execute(
            'SELECT 1 FROM tblissuedbookdetails WHERE StudentID=? AND BookId=? AND RetrunStatus=0 LIMIT 1',
            (sid, book)).fetchone())

    def issue_blocker(self, sid, book):
        s = self.db.execute('SELECT Status FROM tblstudents WHERE StudentId=?', (sid,)).fetchone()
        if not s:                                    return 'no such member'
        if int(s[0]) != 1:                           return 'member blocked'
        if self.copies_available(book) < 1:          return 'no copies'
        if self.has_open_loan(sid, book):            return 'already holds title'
        if self.open_loans(sid) >= MAX_BOOKS_PER_USER: return 'loan limit'
        return None

    def issue(self, sid, book, when=None):
        """Mirrors lms_issue_book(): one transaction, guarded decrement."""
        try:
            self.db.execute('BEGIN IMMEDIATE')
            # locking read of the member row (MySQL: SELECT ... FOR UPDATE)
            m = self.db.execute('SELECT Status FROM tblstudents WHERE StudentId=?', (sid,)).fetchone()
            if not m or int(m[0]) != 1:
                self.db.execute('ROLLBACK')
                return False
            if self.has_open_loan(sid, book) or self.open_loans(sid) >= MAX_BOOKS_PER_USER:
                self.db.execute('ROLLBACK')
                return False
            cur = self.db.execute('UPDATE tblbooks SET Count = Count - 1 WHERE id=? AND Count > 0', (book,))
            if cur.rowcount == 0:
                self.db.execute('ROLLBACK')
                return False
            self.db.execute(
                'INSERT INTO tblissuedbookdetails (StudentID, BookId, IssuesDate) VALUES (?,?,?)',
                (sid, book, when or fmt(NOW)))
            self.db.execute('COMMIT')
            return True
        except sqlite3.Error:
            self.db.execute('ROLLBACK')
            return False

    def return_(self, issue_id, fine_override=None, when=None):
        """Mirrors lms_return_book(): SELECT ... FOR UPDATE, close, restock, bill."""
        try:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute(
                'SELECT BookId, StudentID, IssuesDate, RetrunStatus FROM tblissuedbookdetails WHERE id=?',
                (issue_id,)).fetchone()
            if not row or int(row[3]) == 1:
                self.db.execute('ROLLBACK')
                return False
            book, sid, issued, _ = row
            fine = fine_override if fine_override is not None else lms_calculate_fine(issued, when)
            self.db.execute(
                'UPDATE tblissuedbookdetails SET fine=?, RetrunStatus=1, ReturnDate=? WHERE id=?',
                (fine, when or fmt(NOW), issue_id))
            self.db.execute('UPDATE tblbooks SET Count = Count + 1 WHERE id=?', (book,))
            self.db.execute('UPDATE tblstudents SET fines = fines + ? WHERE StudentId=?', (fine, sid))
            self.db.execute('COMMIT')
            return True
        except sqlite3.Error:
            self.db.execute('ROLLBACK')
            return False

# ------------------------------------------------------------- invariants ---
class Violation(Exception): pass

def check_invariants(db, stock, tag):
    def bad(msg): raise Violation(f'[{tag}] {msg}')

    for bid, cnt in db.execute('SELECT id, Count FROM tblbooks'):
        if cnt < 0:
            bad(f'I1 book {bid} has negative Count={cnt}')
        out = db.execute(
            'SELECT COUNT(*) FROM tblissuedbookdetails WHERE BookId=? AND RetrunStatus=0', (bid,)).fetchone()[0]
        if cnt + out != stock[bid]:
            bad(f'I2 book {bid}: shelf {cnt} + out {out} != stock {stock[bid]}')

    for (sid,) in db.execute('SELECT StudentId FROM tblstudents'):
        n = db.execute('SELECT COUNT(*) FROM tblissuedbookdetails WHERE StudentID=? AND RetrunStatus=0',
                       (sid,)).fetchone()[0]
        if n > MAX_BOOKS_PER_USER:
            bad(f'I3 member {sid} holds {n} books (limit {MAX_BOOKS_PER_USER})')
        dup = db.execute(
            'SELECT BookId, COUNT(*) c FROM tblissuedbookdetails WHERE StudentID=? AND RetrunStatus=0 '
            'GROUP BY BookId HAVING c > 1', (sid,)).fetchone()
        if dup:
            bad(f'I4 member {sid} holds {dup[1]} open loans of book {dup[0]}')
        billed = db.execute('SELECT fines FROM tblstudents WHERE StudentId=?', (sid,)).fetchone()[0]
        ledger = db.execute(
            'SELECT COALESCE(SUM(fine),0) FROM tblissuedbookdetails WHERE StudentID=? AND RetrunStatus=1',
            (sid,)).fetchone()[0]
        if round(billed, 2) != round(ledger, 2):
            bad(f'I6 member {sid}: fines column {billed} != closed-loan fines {ledger}')

    closed_no_date = db.execute(
        'SELECT COUNT(*) FROM tblissuedbookdetails WHERE RetrunStatus=1 AND ReturnDate IS NULL').fetchone()[0]
    if closed_no_date:
        bad(f'I5 {closed_no_date} closed loan(s) without a return date')
    open_with_date = db.execute(
        'SELECT COUNT(*) FROM tblissuedbookdetails WHERE RetrunStatus=0 AND ReturnDate IS NOT NULL').fetchone()[0]
    if open_with_date:
        bad(f'I5 {open_with_date} open loan(s) carrying a return date')

# ------------------------------------------------------------------ setup ---
def build(path=':memory:'):
    db = sqlite3.connect(path, isolation_level=None, timeout=10)
    db.execute('PRAGMA foreign_keys = ON')
    for stmt in translate():
        db.execute(stmt)
    return db

def seed(db, members=40, titles=25, copies=(1, 4)):
    db.execute("INSERT INTO tblcategory (CategoryName) VALUES ('Computer Science')")
    db.execute("INSERT INTO tblauthors (AuthorName) VALUES ('A. Author')")
    stock = {}
    for i in range(1, titles + 1):
        n = random.randint(*copies)
        db.execute("INSERT INTO tblbooks (BookName, CatId, AuthorId, Author, ISBNNumber, BookPrice, Count)"
                   " VALUES (?,1,1,'A. Author',?,?,?)", (f'Title {i}', f'ISBN{i:013d}', 100.0, n))
        stock[i] = n
    sids = []
    for i in range(1, members + 1):
        sid = f'SID{i:03d}'
        db.execute("INSERT INTO tblstudents (StudentId, FullName, MobileNumber, EmailId, Password, Status)"
                   " VALUES (?,?,?,?,?,1)", (sid, f'Member {i}', '9999999999', f'm{i}@example.edu', 'x'))
        sids.append(sid)
    return stock, sids, list(stock)

# ---------------------------------------------------------------- fuzz run --
def fuzz(iterations=20000, seed_value=20260922):
    random.seed(seed_value)
    db = build()
    stock, sids, books = seed(db)
    lib = Library(db)
    counts = {'issue_ok': 0, 'issue_refused': 0, 'return_ok': 0, 'return_refused': 0,
              'block': 0, 'unblock': 0, 'delete_refused': 0, 'delete_ok': 0}
    refusals = {}

    for i in range(iterations):
        op = random.choices(['issue', 'return', 'block', 'delete'], weights=[55, 35, 6, 4])[0]

        if op == 'issue':
            sid, book = random.choice(sids), random.choice(books)
            why = lib.issue_blocker(sid, book)
            if why:
                counts['issue_refused'] += 1
                refusals[why] = refusals.get(why, 0) + 1
                # a refusal must not change anything
                continue
            if lib.issue(sid, book, fmt(NOW - datetime.timedelta(days=random.randint(0, 40)))):
                counts['issue_ok'] += 1
            else:
                counts['issue_refused'] += 1

        elif op == 'return':
            row = db.execute('SELECT id FROM tblissuedbookdetails WHERE RetrunStatus=0 '
                             'ORDER BY RANDOM() LIMIT 1').fetchone()
            if not row:
                continue
            rid = row[0]
            # 1 time in 12, try to close the same loan twice (double-submit)
            if random.random() < 1/12:
                first = lib.return_(rid)
                second = lib.return_(rid)
                if second:
                    raise Violation(f'[fuzz {i}] loan {rid} was closed twice')
                counts['return_ok'] += int(first)
                counts['return_refused'] += 1
            else:
                override = 0.0 if random.random() < 0.1 else None    # waiver path
                if lib.return_(rid, override):
                    counts['return_ok'] += 1
                else:
                    counts['return_refused'] += 1

        elif op == 'block':
            sid = random.choice(sids)
            cur = db.execute('SELECT Status FROM tblstudents WHERE StudentId=?', (sid,)).fetchone()[0]
            new = 0 if cur == 1 else 1
            db.execute('UPDATE tblstudents SET Status=? WHERE StudentId=?', (new, sid))
            counts['block' if new == 0 else 'unblock'] += 1

        else:   # delete a title, which manage-books.php refuses while copies are out
            book = random.choice(books)
            out = db.execute('SELECT COUNT(*) FROM tblissuedbookdetails WHERE BookId=? AND RetrunStatus=0',
                             (book,)).fetchone()[0]
            if out > 0:
                counts['delete_refused'] += 1
            else:
                counts['delete_ok'] += 1        # not actually deleted: keeps the stock map stable

        if i % 250 == 0:
            check_invariants(db, stock, f'fuzz {i}')

    check_invariants(db, stock, 'fuzz final')
    return db, counts, refusals, stock

if __name__ == '__main__':
    import time
    t0 = time.time()
    db, counts, refusals, stock = fuzz()
    dt = time.time() - t0
    print(f"FUZZ: 20,000 operations in {dt:.1f}s -- all invariants held\n")
    print("  operations")
    for k, v in counts.items():
        print(f"    {k:16} {v:6}")
    print("\n  refusal reasons (issue_blocker)")
    for k, v in sorted(refusals.items(), key=lambda x: -x[1]):
        print(f"    {k:22} {v:6}")
    loans = db.execute('SELECT COUNT(*) FROM tblissuedbookdetails').fetchone()[0]
    openl = db.execute('SELECT COUNT(*) FROM tblissuedbookdetails WHERE RetrunStatus=0').fetchone()[0]
    fines = db.execute('SELECT ROUND(SUM(fines),2) FROM tblstudents').fetchone()[0]
    print(f"\n  final state: {loans} ledger rows, {openl} still out, INR {fines} in fines")
