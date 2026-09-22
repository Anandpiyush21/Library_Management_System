"""Re-run the harness and capture real numbers for the report figures."""
import json, sys, os, io, time, contextlib, subprocess, random, datetime, sqlite3, tempfile, threading
sys.path.insert(0, 'tests/stress')
from stress import (build, seed, Library, check_invariants, fmt, NOW,
                    lms_calculate_fine, lms_days_overdue,
                    LOAN_PERIOD_DAYS, FINE_PER_DAY, MAX_BOOKS_PER_USER)
import stress

data = {}

# ---- 1. fuzz -------------------------------------------------------------
t0 = time.time()
db, counts, refusals, stock = stress.fuzz(20000, 20260922)
data['fuzz'] = {'iterations': 20000, 'seconds': round(time.time() - t0, 1),
                'counts': counts, 'refusals': refusals,
                'ledger_rows': db.execute('SELECT COUNT(*) FROM tblissuedbookdetails').fetchone()[0],
                'still_out': db.execute('SELECT COUNT(*) FROM tblissuedbookdetails WHERE RetrunStatus=0').fetchone()[0],
                'fines': round(db.execute('SELECT SUM(fines) FROM tblstudents').fetchone()[0], 2)}

# ---- 2. fine curve -------------------------------------------------------
data['fine_curve'] = [[d, lms_calculate_fine(fmt(NOW - datetime.timedelta(days=d)))] for d in range(0, 31)]

# ---- 3. race: loan limit, before vs after the fix -------------------------
def race_trial(guarded):
    tmp = tempfile.mktemp(suffix='.db')
    db = build(tmp)
    db.execute("INSERT INTO tblcategory (CategoryName) VALUES ('CS')")
    db.execute("INSERT INTO tblauthors (AuthorName) VALUES ('A')")
    for i in range(1, 9):
        db.execute("INSERT INTO tblbooks (BookName,CatId,AuthorId,Author,ISBNNumber,BookPrice,Count)"
                   " VALUES (?,1,1,'A',?,10,50)", (f'T{i}', f'ISBN{i:013d}'))
    db.execute("INSERT INTO tblstudents (StudentId,FullName,MobileNumber,EmailId,Password,Status)"
               " VALUES ('SID001','M','9','m@x.edu','p',1)")
    db.close()
    N = 8
    barrier = threading.Barrier(N)
    def worker(n):
        conn = sqlite3.connect(tmp, isolation_level=None, timeout=15)
        conn.execute('PRAGMA foreign_keys = ON')
        lib = Library(conn)
        if not guarded:                       # emulate the pre-fix code path
            lib.issue = lambda sid, book, when=None: _unguarded(conn, sid, book)
        barrier.wait()
        if lib.issue_blocker('SID001', n) is None:
            lib.issue('SID001', n)
        conn.close()
    ts = [threading.Thread(target=worker, args=(i,)) for i in range(1, N + 1)]
    [t.start() for t in ts]; [t.join() for t in ts]
    conn = sqlite3.connect(tmp, isolation_level=None)
    held = conn.execute("SELECT COUNT(*) FROM tblissuedbookdetails WHERE StudentID='SID001' AND RetrunStatus=0").fetchone()[0]
    conn.close(); os.unlink(tmp)
    return held

def _unguarded(conn, sid, book):
    """The original lms_issue_book(): no member-row lock, no re-check."""
    try:
        conn.execute('BEGIN IMMEDIATE')
        cur = conn.execute('UPDATE tblbooks SET Count = Count - 1 WHERE id=? AND Count > 0', (book,))
        if cur.rowcount == 0:
            conn.execute('ROLLBACK'); return False
        conn.execute('INSERT INTO tblissuedbookdetails (StudentID, BookId, IssuesDate) VALUES (?,?,?)',
                     (sid, book, fmt(NOW)))
        conn.execute('COMMIT'); return True
    except sqlite3.Error:
        conn.execute('ROLLBACK'); return False

before = [race_trial(False) for _ in range(40)]
after  = [race_trial(True)  for _ in range(40)]
data['race'] = {
    'trials': 40, 'threads': 8, 'limit': MAX_BOOKS_PER_USER,
    'before': before, 'after': after,
    'before_violations': sum(1 for h in before if h > MAX_BOOKS_PER_USER),
    'after_violations':  sum(1 for h in after  if h > MAX_BOOKS_PER_USER),
    'before_worst': max(before), 'after_worst': max(after),
}

# ---- 4. last-copy race ---------------------------------------------------
tmp = tempfile.mktemp(suffix='.db')
db = build(tmp)
db.execute("INSERT INTO tblcategory (CategoryName) VALUES ('CS')")
db.execute("INSERT INTO tblauthors (AuthorName) VALUES ('A')")
db.execute("INSERT INTO tblbooks (BookName,CatId,AuthorId,Author,ISBNNumber,BookPrice,Count)"
           " VALUES ('Hot',1,1,'A','ISBN1',10,1)")
for i in range(1, 13):
    db.execute("INSERT INTO tblstudents (StudentId,FullName,MobileNumber,EmailId,Password,Status)"
               " VALUES (?,?,'9',?,'p',1)", (f'SID{i:03d}', f'M{i}', f'm{i}@x.edu'))
db.close()
res, barrier, lock = [], threading.Barrier(12), threading.Lock()
def w(n):
    c = sqlite3.connect(tmp, isolation_level=None, timeout=15)
    c.execute('PRAGMA foreign_keys = ON')
    l = Library(c); barrier.wait()
    ok = l.issue(f'SID{n:03d}', 1)
    with lock: res.append(ok)
    c.close()
ts = [threading.Thread(target=w, args=(i,)) for i in range(1, 13)]
[t.start() for t in ts]; [t.join() for t in ts]
c = sqlite3.connect(tmp, isolation_level=None)
data['last_copy'] = {'threads': 12, 'winners': sum(res), 'losers': len(res) - sum(res),
                     'shelf': c.execute('SELECT Count FROM tblbooks WHERE id=1').fetchone()[0],
                     'ledger': c.execute('SELECT COUNT(*) FROM tblissuedbookdetails').fetchone()[0]}
c.close(); os.unlink(tmp)

# ---- 5. static analysis ---------------------------------------------------
def run(script):
    return subprocess.run([sys.executable, script], capture_output=True, text=True).stdout
data['static'] = {
    'schema': run('tests/stress/schema_check.py'),
    'bind':   run('tests/stress/bind_check.py'),
    'guard':  run('tests/stress/guard_check.py'),
}

# ---- 6. repo metrics ------------------------------------------------------
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
data['repo'] = {
    'php_files': int(sh("find . -name '*.php' -not -path './.git/*' | wc -l")),
    'php_loc':   int(sh("find . -name '*.php' -not -path './.git/*' | xargs cat | wc -l")),
    'diffstat':  sh("git diff --cached --stat | tail -1"),
    'tables':    7,
}
json.dump(data, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w'), indent=1)
print(json.dumps({k: (v if k not in ('static',) else '...') for k, v in data.items()}, indent=1)[:1800])
