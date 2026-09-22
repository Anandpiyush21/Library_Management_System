import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from matplotlib.patches import Polygon, Rectangle
OUT = os.path.join(os.path.dirname(__file__), 'figs'); os.makedirs(OUT, exist_ok=True)

# ======================================= Fig: loan lifecycle state machine ===
fig, ax = canvas(6.8, 2.7, ylim=(20, 100))

for x, lbl, fc, ec in [(3,  'On the shelf', '#e6f7f1', '#a9e0cb'),
                       (28, 'On loan',      '#eaf2fd', '#b9d4f4'),
                       (52, 'Overdue',      '#fdf1dc', '#f2d59a'),
                       (76, 'Returned',     '#eef0ee', BASELINE)]:
    box(ax, x, 62, 21, 13, lbl, fc=fc, ec=ec, fs=9.5, bold=True, lw=1.3)

for x1, x2, name, detail in [(24, 28, 'issue',            'Count - 1\nledger row created'),
                             (49, 52, 'due date passes',  'fine starts accruing'),
                             (73, 76, 'return',           'Count + 1 · fine billed\nRetrunStatus = 1')]:
    arrow(ax, (x1, 68.5), (x2, 68.5), color=INK2, lw=1.4)
    text(ax, (x1 + x2) / 2, 80, name, fs=8, color=INK, bold=True)
    text(ax, (x1 + x2) / 2, 59.5, detail, fs=6.8, color=MUTED, va='top')

# orthogonal return routes, on two separate levels so nothing crosses a label
def ret_route(x_from, y_level, label, ls, color=MUTED):
    ax.plot([x_from, x_from, 13.5], [62, y_level, y_level], color=color,
            linewidth=1.2, linestyle=ls, zorder=3)
    arrow(ax, (13.5, y_level), (13.5, 61.0), color=color, lw=1.2, ls=ls)
    text(ax, (x_from + 13.5) / 2, y_level - 3.6, label, fs=7.2, color=MUTED)

for x1, x2, name, detail in []:
    pass
ret_route(38.5, 44, 'returned before the due date — no fine', '-')
ret_route(86.5, 28, 'the copy is back on the shelf and can be issued again', (0, (4, 3)))

text(ax, 50, 96,
     'A loan is one row in tblissuedbookdetails. "Overdue" is not a stored state — it is derived from IssuesDate\n'
     'and the loan policy every time a page is rendered, so no nightly job can fall behind.',
     fs=7.6, color=INK2, va='top')
save(fig, f'{OUT}/fig_loan_state.png')

# ================================================ Sequence diagram helper ====
def sequence(fig, ax, actors, steps, note=None, txn=None, txn_label=''):
    xs = [9, 35, 61, 87][:len(actors)]
    for x, a in zip(xs, actors):
        box(ax, x - 8.5, 88, 17, 8, a, fc='#ffffff', ec=BASELINE, fs=7.2, bold=True)
        ax.plot([x, x], [9, 88], color=GRID, linewidth=1.0, zorder=1)
    if txn:
        y0, y1 = txn
        ax.add_patch(Rectangle((xs[2] - 6, y1), (xs[3] - xs[2]) + 12, y0 - y1,
                               facecolor='#fdf1dc', edgecolor='#f2d59a',
                               linewidth=1.0, zorder=1, alpha=0.6))
        text(ax, xs[2] - 4.5, y0 - 1.4, txn_label, fs=6.6, color='#9a6a12', ha='left',
             va='top', bold=True)
    for (a, b, y, label, kind) in steps:
        x1, x2 = xs[a], xs[b]
        if a == b:
            ax.plot([x1, x1 + 6, x1 + 6, x1], [y, y, y - 3.0, y - 3.0],
                    color=INK2, linewidth=1.1, zorder=4)
            arrow(ax, (x1 + 2.5, y - 3.0), (x1, y - 3.0), color=INK2, lw=1.1, mutation=9)
            text(ax, x1 + 7.5, y - 1.4, label, fs=6.5, color=INK2, ha='left', bg=SURFACE)
        else:
            ls = (0, (4, 3)) if kind == 'ret' else '-'
            col = MUTED if kind == 'ret' else INK2
            arrow(ax, (x1, y), (x2, y), color=col, lw=1.1, ls=ls, mutation=9)
            text(ax, (x1 + x2) / 2, y + 2.9, label, fs=6.5, color=col, bg=SURFACE)
    if note:
        text(ax, 50, 7.5, note, fs=7.4, color=INK2)

# ======================================== Fig: issue-a-book sequence =========
fig, ax = canvas(6.9, 4.7)
sequence(fig, ax,
    ['Librarian\n(browser)', 'admin/\nissue-book.php', 'includes/\nlibrary.php', 'MySQL\n(InnoDB)'],
    [(0, 1, 82, 'POST studentid, bookid, csrf_token', 'call'),
     (1, 1, 76, 'require_admin() · csrf_verify()', 'self'),
     (1, 2, 67, 'lms_issue_blocker()', 'call'),
     (2, 3, 62, 'status · copies · open loans', 'call'),
     (2, 1, 56, 'null = allowed, else a reason', 'ret'),
     (1, 2, 49, 'lms_issue_book()', 'call'),
     (2, 3, 41, 'BEGIN', 'call'),
     (2, 3, 35.5, 'SELECT Status ... FOR UPDATE', 'call'),
     (2, 3, 30, 're-check limit + duplicate', 'call'),
     (2, 3, 23, 'UPDATE tblbooks SET Count=Count-1\nWHERE id=? AND Count>0', 'call'),
     (2, 3, 17, 'INSERT ledger row', 'call'),
     (2, 3, 12, 'COMMIT  (else ROLLBACK)', 'call'),
     (1, 0, 7, 'redirect + "due back on <date>"', 'ret')],
    txn=(45.5, 9.5), txn_label='one transaction',
    note=None)
text(ax, 50, 2.5, 'The zero-row result of the guarded UPDATE is what makes the last copy safe: the loser of the race\n'
                  'rolls back instead of driving Count negative.', fs=7.4, color=INK2)
save(fig, f'{OUT}/fig_seq_issue.png')

# ======================================== Fig: return-a-book sequence ========
fig, ax = canvas(6.9, 4.4)
sequence(fig, ax,
    ['Librarian\n(browser)', 'admin/update-\nissue-bookdeails', 'includes/\nlibrary.php', 'MySQL\n(InnoDB)'],
    [(0, 1, 82, 'opens the loan record', 'call'),
     (1, 2, 76, 'lms_calculate_fine(IssuesDate)', 'call'),
     (2, 1, 70, 'days overdue x FINE_PER_DAY', 'ret'),
     (0, 1, 63, 'POST return (fine may be overridden)', 'call'),
     (1, 2, 56, 'lms_return_book(rid, fine?)', 'call'),
     (2, 3, 50, 'BEGIN', 'call'),
     (2, 3, 45, 'SELECT ... WHERE id=? FOR UPDATE', 'call'),
     (2, 1, 39, 'already closed = false, no double credit', 'ret'),
     (2, 3, 33, 'UPDATE ledger: fine, status, date', 'call'),
     (2, 3, 28, 'UPDATE tblbooks SET Count=Count+1', 'call'),
     (2, 3, 23, 'UPDATE tblstudents SET fines=fines+?', 'call'),
     (2, 3, 18, 'COMMIT', 'call')],
    txn=(52.5, 15.0), txn_label='one transaction',
    note='Restoring the copy count is the step the original code omitted, so the catalogue drained over time.')
save(fig, f'{OUT}/fig_seq_return.png')
print('batch 2 done')
