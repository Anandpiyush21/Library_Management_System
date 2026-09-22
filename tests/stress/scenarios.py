"""Targeted stress scenarios: contention, races, boundaries, allocator, seed data."""
import sqlite3, random, datetime, threading, tempfile, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from stress import (build, seed, Library, check_invariants, Violation, fmt, parse,
                    lms_calculate_fine, lms_days_overdue, lms_due_date,
                    NOW, LOAN_PERIOD_DAYS, FINE_PER_DAY, MAX_BOOKS_PER_USER)

fails = []
def expect(name, cond, detail=''):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}" + (f"   {detail}" if detail and not cond else ''))
    if not cond:
        fails.append(name)

# ------------------------------------------------------- 1. high contention --
def contention(label, members, titles, copies, iters, seed_value):
    """Drive issue/return hard against a given scarcity profile."""
    random.seed(seed_value)
    db = build()
    db.execute("INSERT INTO tblcategory (CategoryName) VALUES ('CS')")
    db.execute("INSERT INTO tblauthors (AuthorName) VALUES ('A')")
    stock = {}
    for i in range(1, titles + 1):
        db.execute("INSERT INTO tblbooks (BookName,CatId,AuthorId,Author,ISBNNumber,BookPrice,Count)"
                   " VALUES (?,1,1,'A',?,10,?)", (f'T{i}', f'ISBN{i:013d}', copies))
        stock[i] = copies
    sids = []
    for i in range(1, members + 1):
        sid = f'SID{i:03d}'
        db.execute("INSERT INTO tblstudents (StudentId,FullName,MobileNumber,EmailId,Password,Status)"
                   " VALUES (?,?,'9',?,'p',1)", (sid, f'M{i}', f'm{i}@x.edu'))
        sids.append(sid)
    lib = Library(db)
    tally = {}
    for i in range(iters):
        if random.random() < 0.6:
            sid, book = random.choice(sids), random.choice(list(stock))
            why = lib.issue_blocker(sid, book)
            tally[why or 'issued'] = tally.get(why or 'issued', 0) + 1
            if not why:
                lib.issue(sid, book, fmt(NOW - datetime.timedelta(days=random.randint(0, 30))))
        else:
            row = db.execute('SELECT id FROM tblissuedbookdetails WHERE RetrunStatus=0 '
                             'ORDER BY RANDOM() LIMIT 1').fetchone()
            if row:
                lib.return_(row[0])
        if i % 200 == 0:
            check_invariants(db, stock, f'{label} {i}')
    check_invariants(db, stock, f'{label} final')
    print(f"  {label}")
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"      {k:22} {v}")
    return tally

print("\n1. HIGH CONTENTION")
scarce = contention('scarce  (8 members, 4 titles x 1 copy, 6k ops)', 8, 4, 1, 6000, 7)
plenty = contention('plentiful (3 members, 3 titles x 12 copies, 6k ops)', 3, 3, 12, 6000, 11)
seen = set(scarce) | set(plenty)
expect('"no copies" branch reached', 'no copies' in seen)
expect('"loan limit" branch reached', 'loan limit' in seen)
expect('"already holds title" branch reached', 'already holds title' in seen)
expect('invariants held under both profiles', True)

# --------------------------------------------- 2. race for the last copy -----
print("\n2. RACE  (12 threads issue the single remaining copy simultaneously)")
tmp = tempfile.mktemp(suffix='.db')
db2 = build(tmp)
db2.execute("INSERT INTO tblcategory (CategoryName) VALUES ('CS')")
db2.execute("INSERT INTO tblauthors (AuthorName) VALUES ('A')")
db2.execute("INSERT INTO tblbooks (BookName,CatId,AuthorId,Author,ISBNNumber,BookPrice,Count)"
            " VALUES ('Hot Title',1,1,'A','ISBN0000000000001',10,1)")
for i in range(1, 13):
    db2.execute("INSERT INTO tblstudents (StudentId,FullName,MobileNumber,EmailId,Password,Status)"
                " VALUES (?,?,'9',?,'p',1)", (f'SID{i:03d}', f'M{i}', f'm{i}@x.edu'))
db2.close()

results, barrier = [], threading.Barrier(12)
lock = threading.Lock()
def worker(n):
    conn = sqlite3.connect(tmp, isolation_level=None, timeout=15)
    conn.execute('PRAGMA foreign_keys = ON')
    l = Library(conn)
    barrier.wait()
    ok = l.issue(f'SID{n:03d}', 1)
    with lock:
        results.append(ok)
    conn.close()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(1, 13)]
[t.start() for t in threads]; [t.join() for t in threads]

conn = sqlite3.connect(tmp, isolation_level=None)
shelf = conn.execute('SELECT Count FROM tblbooks WHERE id=1').fetchone()[0]
ledger = conn.execute('SELECT COUNT(*) FROM tblissuedbookdetails').fetchone()[0]
print(f"      winners={sum(results)}  losers={len(results)-sum(results)}  shelf={shelf}  ledger_rows={ledger}")
expect('exactly one thread got the copy', sum(results) == 1, f'{sum(results)} winners')
expect('shelf count did not go negative', shelf == 0, f'shelf={shelf}')
expect('exactly one ledger row written', ledger == 1, f'{ledger} rows')
conn.close(); os.unlink(tmp)

# ------------------------------------------------ 3. fine/date boundaries ----
print("\n3. BOUNDARIES  (fine arithmetic around the due date)")
def d(n): return fmt(NOW - datetime.timedelta(days=n))
cases = [
    ('issued today',              d(0),  0,   0.0),
    ('day before due',            d(13), 0,   0.0),
    ('exactly on the due date',   d(14), 0,   0.0),
    ('one day late',              d(15), 1,   5.0),
    ('a week late',               d(21), 7,  35.0),
    ('a year late',               d(379), 365, 1825.0),
]
for name, issued, days, fine in cases:
    expect(f'{name}: {days}d overdue, INR {fine}',
           lms_days_overdue(issued) == days and lms_calculate_fine(issued) == fine,
           f'got {lms_days_overdue(issued)}d / INR {lms_calculate_fine(issued)}')
expect('fine freezes at the return date',
       lms_calculate_fine(d(30), d(15)) == 5.0, f'got {lms_calculate_fine(d(30), d(15))}')
expect('due date = issue + LOAN_PERIOD_DAYS',
       lms_due_date(d(0)).date() == (NOW + datetime.timedelta(days=14)).date())

db3 = build(); stock3, sids3, books3 = seed(db3, members=3, titles=3, copies=(2, 2))
lib3 = Library(db3)
lib3.issue('SID001', 1, d(30))
rid = db3.execute('SELECT id FROM tblissuedbookdetails').fetchone()[0]
lib3.return_(rid, 0.0)                                   # librarian waives
billed = db3.execute("SELECT fines FROM tblstudents WHERE StudentId='SID001'").fetchone()[0]
expect('waiver (override 0) bills nothing despite 16 days overdue', billed == 0.0, f'billed {billed}')
check_invariants(db3, stock3, 'waiver')

lib3.issue('SID002', 2, d(40))
rid2 = db3.execute("SELECT id FROM tblissuedbookdetails WHERE StudentID='SID002'").fetchone()[0]
lib3.return_(rid2)
billed2 = db3.execute("SELECT fines FROM tblstudents WHERE StudentId='SID002'").fetchone()[0]
expect('26 days overdue bills INR 130', billed2 == 130.0, f'billed {billed2}')

# ------------------------------------------------- 4. card-number allocator --
print("\n4. CARD NUMBERS  (PHP string increment semantics)")
def php_increment(s):
    """Emulates PHP's perl-style string increment, which lms_next_student_id relies on."""
    chars = list(s); i = len(chars) - 1
    while i >= 0:
        c = chars[i]
        if c == 'z': chars[i] = 'a'; i -= 1
        elif c == 'Z': chars[i] = 'A'; i -= 1
        elif c == '9': chars[i] = '0'; i -= 1
        elif c.isalnum(): chars[i] = chr(ord(c) + 1); return ''.join(chars)
        else: return ''.join(chars)
        if i < 0:
            first = s[0]
            prefix = '1' if first.isdigit() else ('a' if first.islower() else 'A')
            return prefix + ''.join(chars)
    return ''.join(chars)

for start, want in [('SID016', 'SID017'), ('SID099', 'SID100'), ('SID998', 'SID999')]:
    expect(f'{start} -> {want}', php_increment(start) == want, f'got {php_increment(start)}')
after999 = php_increment('SID999')
print(f"      note: SID999 -> {after999}  (carry runs into the letters)")
expect('no duplicate IDs across 5,000 allocations',
       len({(lambda s: s)(x) for x in (lambda: [ (globals().__setitem__('_c', php_increment(globals().get('_c', 'SID000'))) or globals()['_c']) for _ in range(5000)])()}) == 5000)
seen, cur = set(), 'SID000'
for _ in range(5000):
    cur = php_increment(cur); seen.add(cur)
expect('5,000 sequential allocations are all unique', len(seen) == 5000, f'{len(seen)} unique')

# ------------------------------------------------------- 5. seed data / DDL --
print("\n5. SEED DATA  (the INSERTs in database/library.sql against the real constraints)")
sql = open('database/library.sql').read()
db4 = build()
inserts = re.findall(r'INSERT INTO [^;]+;', sql, re.S)
ok = 0
for stmt in inserts:
    s = stmt.replace('`', '"')
    try:
        db4.executescript(s); ok += 1
    except sqlite3.Error as e:
        expect(f'seed insert failed: {e}', False)
expect(f'all {len(inserts)} seed INSERT blocks satisfy the constraints', ok == len(inserts))
expect('5 books, 5 categories, 5 authors, 1 admin seeded',
       db4.execute('SELECT COUNT(*) FROM tblbooks').fetchone()[0] == 5 and
       db4.execute('SELECT COUNT(*) FROM tblcategory').fetchone()[0] == 5 and
       db4.execute('SELECT COUNT(*) FROM tblauthors').fetchone()[0] == 5 and
       db4.execute('SELECT COUNT(*) FROM admin').fetchone()[0] == 1)
try:
    db4.execute("INSERT INTO tblbooks (BookName,ISBNNumber,Count) VALUES ('Dup','9780262046305',1)")
    expect('duplicate ISBN rejected', False, 'the unique key did not fire')
except sqlite3.IntegrityError:
    expect('duplicate ISBN rejected by the unique key', True)
try:
    db4.execute("INSERT INTO tblissuedbookdetails (BookId,StudentID) VALUES (1,'GHOST')")
    expect('loan for a non-existent member rejected', False, 'the foreign key did not fire')
except sqlite3.IntegrityError:
    expect('loan for a non-existent member rejected by the foreign key', True)

print("\n" + "=" * 70)
print(f"{'ALL SCENARIOS PASSED' if not fails else str(len(fails)) + ' FAILURE(S): ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
