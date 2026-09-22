import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from draw import *
from matplotlib.patches import Polygon, Circle
OUT = os.path.join(os.path.dirname(__file__), 'figs'); os.makedirs(OUT, exist_ok=True)

# ===================================== Fig: password verification/migration ==
fig, ax = canvas(6.7, 3.9)

def diamond(cx, cy, w, h, label, fs=7.4):
    ax.add_patch(Polygon([(cx, cy + h/2), (cx + w/2, cy), (cx, cy - h/2), (cx - w/2, cy)],
                         closed=True, facecolor='#fdf1dc', edgecolor='#f2d59a',
                         linewidth=1.2, zorder=2))
    text(ax, cx, cy, label, fs=fs, color=INK, bold=True)

box(ax, 3, 72, 20, 11, 'login submitted\n(e-mail + password)', fc='#ffffff', ec=BASELINE, fs=7.4)
diamond(38, 77.5, 30, 20, 'stored hash looks like\nan unsalted md5 digest?')
box(ax, 60, 84, 37, 11, 'LEGACY PATH\nhash_equals(md5(input), stored)', fc='#fdeee7', ec='#f3c3ab', fs=7.2)
box(ax, 60, 66, 37, 11, 'CURRENT PATH\npassword_verify(input, stored)', fc='#e6f7f1', ec='#a9e0cb', fs=7.2)
diamond(78.5, 55, 30, 14, 'password matches?')
box(ax, 5, 49, 27, 12, 'reject\n(one generic message)', fc='#fbe9e9', ec='#efbebe', fs=7.4)
box(ax, 60, 27, 37, 14, 'lms_password_needs_rehash() ?\nrewrite the row with bcrypt,\nthen session_regenerate_id()',
    fc='#eaf2fd', ec='#b9d4f4', fs=7.2)
box(ax, 60, 11, 37, 10, 'signed in', fc='#ffffff', ec=BASELINE, fs=8.5, bold=True)

arrow(ax, (23, 77.5), (23.5, 77.5), color=INK2)
arrow(ax, (53, 79.5), (60, 88.0), color=INK2)
text(ax, 55.5, 85.5, 'yes', fs=7, color=S2, bold=True, bg=SURFACE)
arrow(ax, (53, 75.5), (60, 72.5), color=INK2)
text(ax, 55.5, 70.5, 'no', fs=7, color='#0f7a55', bold=True, bg=SURFACE)

# both verification paths converge on the same decision, routed around the boxes
ax.plot([68, 68, 78.5], [84, 63.5, 63.5], color=MUTED, linewidth=1.2, zorder=3)
ax.plot([89, 89, 78.5], [66, 63.5, 63.5], color=MUTED, linewidth=1.2, zorder=3)
arrow(ax, (78.5, 63.5), (78.5, 62.2), color=MUTED)
arrow(ax, (63.5, 55), (32, 55), color=INK2)
text(ax, 47, 57.6, 'no', fs=7, color=CRITICAL, bold=True, bg=SURFACE)
arrow(ax, (78.5, 48), (78.5, 41.4), color=INK2)
text(ax, 81, 44.6, 'yes', fs=7, color='#0f7a55', bold=True, ha='left', bg=SURFACE)
arrow(ax, (78.5, 27), (78.5, 21.4), color=INK2)

text(ax, 50, 5.0,
     'A legacy md5 digest is therefore accepted exactly once per account: that login rewrites the row as bcrypt.\n'
     'An existing installation upgrades without resetting anyone\'s password, and the legacy branch can later be\n'
     'deleted by removing a single preg_match case.', fs=7.5, color=INK2)
save(fig, f'{OUT}/fig_password.png')

# ================================================ Fig: verification coverage =
fig, ax = canvas(6.8, 4.0)

techniques = ['Static\nanalysis\n(3 scripts)', 'PHP unit\ntests\n(17 asserts)',
              'SQLite stress\nharness\n(20k ops)', 'Manual\nchecklist\n(docs/TESTING)']
concerns = [
    ('Table / column names used by the PHP exist',      [2, 0, 1, 0]),
    ('Every SQL placeholder is bound exactly once',     [2, 0, 0, 0]),
    ('Auth guard on every non-public page',             [2, 0, 0, 1]),
    ('CSRF token on every state-changing form',         [2, 0, 0, 1]),
    ('Loan policy arithmetic (due dates, fines)',       [0, 2, 2, 1]),
    ('Password hashing + legacy md5 upgrade',           [0, 2, 0, 1]),
    ('Card-number allocation',                          [0, 2, 2, 0]),
    ('Schema constraints (PK / UK / FK)',               [1, 0, 2, 1]),
    ('Transaction correctness + invariants',            [0, 0, 2, 1]),
    ('Concurrency (races on copies and loan limits)',   [0, 0, 2, 0]),
    ('PHP runtime behaviour (sessions, rendering)',     [0, 0, 0, 2]),
    ('MySQL-specific locking + fixed-point maths',      [0, 0, 0, 1]),
]
x0, colw, rowh, y0 = 46, 13, 5.4, 84
for j, t in enumerate(techniques):
    text(ax, x0 + colw * j + colw / 2, y0 + 8.0, t, fs=6.9, color=INK, bold=True)
for i, (name, marks) in enumerate(concerns):
    y = y0 - i * rowh
    if i % 2 == 0:
        ax.add_patch(plt.Rectangle((2, y - rowh / 2), 96, rowh, facecolor='#f4f3f0',
                                   edgecolor='none', zorder=0))
    text(ax, 3.5, y, name, fs=7.2, color=INK2, ha='left')
    for j, m in enumerate(marks):
        cx = x0 + colw * j + colw / 2
        if m == 2:
            ax.plot([cx], [y], 'o', markersize=8, color=GOOD, zorder=3)
        elif m == 1:
            ax.plot([cx], [y], 'o', markersize=8, markerfacecolor='#ffffff',
                    markeredgecolor=GOOD, markeredgewidth=1.6, zorder=3)
        else:
            text(ax, cx, y, '·', fs=9, color='#c9c8c2')

ly = y0 - len(concerns) * rowh - 4.0
ax.plot([32], [ly], 'o', markersize=8, color=GOOD, zorder=3)
text(ax, 34.5, ly, 'primary evidence', fs=7.2, color=INK2, ha='left')
ax.plot([56], [ly], 'o', markersize=8, markerfacecolor='#ffffff', markeredgecolor=GOOD, markeredgewidth=1.6, zorder=3)
text(ax, 58.5, ly, 'partial / supporting', fs=7.2, color=INK2, ha='left')

text(ax, 50, ly - 7.5,
     'The bottom two rows are the honest gap: no PHP or MySQL was available on the machine where this\n'
     'work was done, so the PHP was never executed and MySQL\'s own locking was never observed. Those\n'
     'rows rest on the manual checklist, which has not yet been run.', fs=7.5, color=INK2)
save(fig, f'{OUT}/fig_verification.png')
print('batch 3 done')
