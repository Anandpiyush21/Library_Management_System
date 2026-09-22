import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
OUT = os.path.join(os.path.dirname(__file__), 'figs'); os.makedirs(OUT, exist_ok=True)

TINT1, TINT3, TINT4 = '#eaf2fd', '#e6f7f1', '#f3f1fb'

# ============================================ Fig 1: layered architecture ====
fig, ax = canvas(6.7, 5.0)

box(ax, 34, 91.5, 32, 6.5, 'Browser', fc='#ffffff', ec=BASELINE, fs=9.5, bold=True)

box(ax, 6, 66, 88, 17.5, '', fc=TINT1, ec='#b9d4f4')
text(ax, 10, 80.6, 'PRESENTATION', fs=7.5, color=S1, ha='left', bold=True)
text(ax, 10, 77.0, 'page scripts — one HTTP request each', fs=7.5, color=MUTED, ha='left')
for i, (lbl, sub) in enumerate([('Member portal', 'index · dashboard\nissued-books · profile'),
                                ('Librarian panel', 'admin/ issue · return\ncatalogue · members'),
                                ('AJAX endpoints', 'get_book · get_student\ncheck_availability')]):
    x = 11 + i * 27.5
    box(ax, x, 67.5, 24, 7.6, '', fc='#ffffff', ec='#b9d4f4')
    text(ax, x + 12, 73.2, lbl, fs=8, color=INK, bold=True)
    text(ax, x + 12, 69.9, sub, fs=6.8, color=MUTED)

box(ax, 6, 38, 88, 22, '', fc=TINT3, ec='#a9e0cb')
text(ax, 10, 57.2, 'DOMAIN / SUPPORT', fs=7.5, color='#0f7a55', ha='left', bold=True)
text(ax, 10, 53.6, 'includes/ — the only place a library rule is written down', fs=7.5, color=MUTED, ha='left')
for i, (lbl, sub) in enumerate([('config.php', 'credentials\npolicy constants\nPDO handle'),
                                ('auth.php', 'bcrypt · sessions\nCSRF · escaping'),
                                ('library.php', 'loan rules · fines\nissue/return txns'),
                                ('notify.php', 'overdue\nreminder mail')]):
    x = 9 + i * 20.5
    box(ax, x, 39.5, 18, 11.5, '', fc='#ffffff', ec='#a9e0cb')
    text(ax, x + 9, 49.0, lbl, fs=8, color=INK, bold=True)
    text(ax, x + 9, 44.0, sub, fs=6.8, color=MUTED)

box(ax, 6, 11, 88, 19.5, '', fc=TINT4, ec='#c9c2ec')
text(ax, 10, 27.7, 'DATA', fs=7.5, color=S7, ha='left', bold=True)
text(ax, 10, 24.1, 'MySQL / InnoDB — 7 tables, foreign keys, utf8mb4', fs=7.5, color=MUTED, ha='left')
for i, t in enumerate(['tblbooks', 'tblstudents', 'tblissuedbookdetails', 'tblcategory',
                       'tblauthors', 'tblrequest', 'admin']):
    x = 9 + (i % 4) * 21
    y = 17.2 if i < 4 else 12.4
    box(ax, x, y, 19, 3.8, t, fc='#ffffff', ec='#c9c2ec', fs=7.2)

arrow(ax, (50, 91.5), (50, 83.8), color=MUTED)
text(ax, 52, 87.6, 'HTTP', fs=7.2, color=MUTED, ha='left')
arrow(ax, (50, 66), (50, 60.2), color=MUTED)
text(ax, 52, 63.1, 'calls lms_*() helpers only', fs=7.2, color=MUTED, ha='left')
arrow(ax, (50, 38), (50, 30.8), color=MUTED)
text(ax, 52, 34.4, 'PDO: prepared statements, transactions', fs=7.2, color=MUTED, ha='left')

text(ax, 50, 5.0,
     'admin/includes/config.php is a one-line require of the root bootstrap, so both portals share\n'
     'one database handle, one policy and one set of helpers.', fs=7.8, color=INK2)
save(fig, f'{OUT}/fig_architecture.png')

# ================================================== Fig 2: ER diagram ========
fig, ax = canvas(6.7, 5.2)

def entity(x, y_top, w, name, rows, tint):
    """Draw an entity; return its rect and edge anchors."""
    h = 4.6 + len(rows) * 3.3
    y = y_top - h
    box(ax, x, y, w, h, '', fc='#ffffff', ec=tint, lw=1.2)
    box(ax, x, y_top - 4.6, w, 4.6, '', fc=tint, ec=tint, lw=1.2)
    text(ax, x + w / 2, y_top - 2.3, name, fs=7.8, color=INK, bold=True)
    for i, (col, kind) in enumerate(rows):
        yy = y_top - 6.6 - i * 3.3
        text(ax, x + 1.8, yy, col, fs=6.7, color=INK2, ha='left')
        if kind:
            text(ax, x + w - 1.8, yy, kind, fs=6.0, color=MUTED, ha='right')
    return {'x': x, 'y': y, 'w': w, 'h': h, 'top': y_top,
            'L': (x, y + h / 2), 'R': (x + w, y + h / 2),
            'T': (x + w / 2, y_top), 'B': (x + w / 2, y),
            'Bl': (x + w * 0.28, y), 'Br': (x + w * 0.72, y),
            'Lo': (x, y + h * 0.28), 'Ro': (x + w, y + h * 0.28),
            'cx': x + w / 2}

def connect(a, b, ca, cb, one, many, label, offs=3.2):
    """Edge-to-edge connector with cardinalities placed OUTSIDE both boxes."""
    p1, p2 = a[ca], b[cb]
    arrow(ax, p1, p2, color=MUTED, lw=1.1, style='-')
    def push(p, side, d):
        s0 = side[0]
        dx = {'L': -d, 'R': d}.get(s0, 0)
        dy = {'T': d, 'B': -d}.get(s0, 0)
        return (p[0] + dx, p[1] + dy)
    l1, l2 = push(p1, ca, offs), push(p2, cb, offs)
    text(ax, l1[0], l1[1] + (1.7 if ca in 'LR' else 0), one, fs=7, color=S1, bold=True, bg=SURFACE)
    text(ax, l2[0], l2[1] + (1.7 if cb in 'LR' else 0), many, fs=7, color=S1, bold=True, bg=SURFACE)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    text(ax, mx, my, label, fs=6.8, color=MUTED, bg=SURFACE)

cat = entity(3, 97, 24, 'tblcategory', [('id', 'PK'), ('CategoryName', 'UK'), ('Status', '')], '#d9e8fb')
aut = entity(3, 74, 24, 'tblauthors', [('id', 'PK'), ('AuthorName', '')], '#d9e8fb')
adm = entity(3, 40, 24, 'admin', [('id', 'PK'), ('UserName', 'UK'), ('Password', 'bcrypt')], '#f7e0d6')
bok = entity(38, 97, 26, 'tblbooks', [('id', 'PK'), ('CatId', 'FK'), ('AuthorId', 'FK'),
                                      ('ISBNNumber', 'UK'), ('Count', 'copies')], '#cfe6dd')
iss = entity(36, 54, 30, 'tblissuedbookdetails', [('BookId', 'FK'), ('StudentID', 'FK'), ('IssuesDate', ''),
                                                  ('ReturnDate', ''), ('RetrunStatus', '0/1'), ('fine', '')], '#cfe6dd')
stu = entity(75, 97, 22, 'tblstudents', [('StudentId', 'UK'), ('EmailId', 'UK'), ('Password', 'bcrypt'),
                                         ('Status', '1/0'), ('fines', '')], '#e4dff7')
req = entity(75, 56, 22, 'tblrequest', [('RequestId', 'PK'), ('StudentId', 'FK'),
                                        ('BookTitle', ''), ('IsApproved', '')], '#e4dff7')

connect(cat, bok, 'R', 'L', '1', 'N', 'classifies')
connect(aut, bok, 'R', 'Bl', '1', 'N', 'wrote')
connect(bok, iss, 'Br', 'T', '1', 'N', 'is lent as')
connect(stu, iss, 'B', 'R', '1', 'N', 'borrows')
connect(stu, req, 'B', 'T', '1', 'N', 'requests')
text(ax, adm['cx'], adm['y'] - 4.0, 'librarian accounts\n(no FK: staff are not members)', fs=6.6, color=MUTED)

text(ax, 50, 7.0,
     'tblbooks.Count is the number of copies ON THE SHELF, not the number owned: issuing decrements it,\n'
     'returning restores it, both inside the transaction that writes the ledger row. The ledger joins members\n'
     'by the human-readable card number (StudentId) — what a librarian reads off a card at the desk.',
     fs=7.5, color=INK2)
save(fig, f'{OUT}/fig_er.png')
print('batch 1 done')
