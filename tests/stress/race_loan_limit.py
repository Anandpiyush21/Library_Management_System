"""Is the loan-limit / duplicate-title check safe under concurrency?

lms_issue_blocker() runs BEFORE lms_issue_book() opens its transaction, so two
simultaneous issues for the same member can both pass the check. The copy count
is protected by `WHERE Count > 0` inside the transaction; the per-member rules
have no such guard.
"""
import sqlite3, threading, tempfile, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from stress import build, Library, MAX_BOOKS_PER_USER

def run(trial):
    tmp = tempfile.mktemp(suffix='.db')
    db = build(tmp)
    db.execute("INSERT INTO tblcategory (CategoryName) VALUES ('CS')")
    db.execute("INSERT INTO tblauthors (AuthorName) VALUES ('A')")
    for i in range(1, 9):                      # 8 titles, plenty of copies
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
        barrier.wait()                          # all threads start together
        if lib.issue_blocker('SID001', n) is None:
            lib.issue('SID001', n)              # each thread takes a different title
        conn.close()
    ts = [threading.Thread(target=worker, args=(i,)) for i in range(1, N + 1)]
    [t.start() for t in ts]; [t.join() for t in ts]

    conn = sqlite3.connect(tmp, isolation_level=None)
    held = conn.execute("SELECT COUNT(*) FROM tblissuedbookdetails "
                        "WHERE StudentID='SID001' AND RetrunStatus=0").fetchone()[0]
    conn.close(); os.unlink(tmp)
    return held

print(f"8 threads issue 8 different titles to one member at once (limit = {MAX_BOOKS_PER_USER})\n")
over, worst = 0, 0
for t in range(40):
    held = run(t)
    worst = max(worst, held)
    if held > MAX_BOOKS_PER_USER:
        over += 1
print(f"  trials over the limit : {over}/40")
print(f"  worst case observed   : {worst} books held (limit {MAX_BOOKS_PER_USER})")
print()
if over:
    print("  FINDING: the per-member loan limit is not race-safe.")
    print("  The copy count survives this because its guard lives INSIDE the")
    print("  transaction (`UPDATE ... WHERE Count > 0`); the loan-limit and")
    print("  duplicate-title checks run before the transaction opens.")
else:
    print("  No violation observed in 40 trials (does not prove the check is safe).")
