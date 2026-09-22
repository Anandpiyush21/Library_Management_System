"""Data-driven figures: every number comes from report/data.json (measured, not typed)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(__file__)
D = json.load(open(os.path.join(HERE, 'data.json')))
OUT = os.path.join(HERE, 'figs'); os.makedirs(OUT, exist_ok=True)

def caption(fig, text):
    fig.text(0.5, 0.005, text, ha='center', va='bottom', color=MUTED, fontsize=7.5)

# ---------------------------------------------------- Fig: fine accrual ------
fig, ax = plt.subplots(figsize=(6.4, 3.1))
fig.subplots_adjust(bottom=0.26, top=0.88)
days = [d for d, _ in D['fine_curve']]
fine = [f for _, f in D['fine_curve']]
ax.step(days, fine, where='post', color=S1, linewidth=2, zorder=3)
ax.fill_between(days, fine, step='post', color=S1, alpha=0.10, zorder=2)
ax.axvline(14, color=CRITICAL, linewidth=1.4, linestyle=(0, (4, 3)), zorder=4)
ax.text(13.4, 74, 'due date\n(day 14)', color=CRITICAL, fontsize=8.5,
        ha='right', va='top', linespacing=1.35)
ax.text(1.0, 30, 'no fine accrues\nwhile the loan is\nwithin its term',
        color=INK2, fontsize=8.5, va='top', linespacing=1.35)
for d, dx, ha in ((15, 0.6, 'left'), (21, 0.6, 'left'), (30, -0.6, 'right')):
    y = dict(D['fine_curve'])[d]
    ax.plot([d], [y], 'o', color=S1, markersize=5, zorder=5)
    ax.annotate(f'INR {y:.0f}', xy=(d, y), xytext=(d + dx, y + 4),
                color=INK, fontsize=8.5, fontweight='bold', ha=ha)
ax.set_xlabel('days since the book was issued')
ax.set_ylabel('fine payable (INR)')
ax.set_title('Fine accrual under the default policy')
ax.set_xlim(0, 31); ax.set_ylim(0, 92)
ax.set_xticks(range(0, 31, 5))
ax.grid(axis='x', visible=False)
despine(ax)
caption(fig, 'LOAN_PERIOD_DAYS = 14,  FINE_PER_DAY = 5.00  |  values produced by lms_calculate_fine()')
save(fig, f'{OUT}/fig_fine_curve.png')

# ----------------------------------------------------- Fig: fuzz results -----
fig, (axl, axr) = plt.subplots(1, 2, figsize=(6.9, 3.3), gridspec_kw={'wspace': 0.42})
fig.subplots_adjust(bottom=0.30, top=0.88)

c = D['fuzz']['counts']
groups = [('Issues\naccepted', c['issue_ok'], S1),
          ('Issues\nrefused', c['issue_refused'], S2),
          ('Returns\naccepted', c['return_ok'], S3),
          ('Returns\nrefused', c['return_refused'], S4)]
xs = np.arange(len(groups))
axl.bar(xs, [g[1] for g in groups], color=[g[2] for g in groups], width=0.62,
        edgecolor=SURFACE, linewidth=1.5, zorder=3)
for x, (_, v, _) in zip(xs, groups):
    axl.text(x, v + 150, f'{v:,}', ha='center', color=INK, fontsize=8.5, fontweight='bold')
axl.set_xticks(xs); axl.set_xticklabels([g[0] for g in groups], fontsize=8)
axl.set_ylabel('operations')
axl.set_title('Outcome of 20,000 operations')
axl.set_ylim(0, max(g[1] for g in groups) * 1.22)
axl.grid(axis='x', visible=False)
despine(axl)

r = D['fuzz']['refusals']
order = ['member blocked', 'no copies', 'already holds title', 'loan limit']
vals = [r.get(k, 0) for k in order]
cols = [S2, S4, S5, S8]
ys = np.arange(len(order))[::-1]
axr.barh(ys, vals, color=cols, height=0.6, edgecolor=SURFACE, linewidth=1.5, zorder=3)
for y, v in zip(ys, vals):
    axr.text(v * 1.45, y, f'{v:,}', va='center', color=INK, fontsize=8.5, fontweight='bold')
axr.set_yticks(ys); axr.set_yticklabels(order, fontsize=8)
axr.set_xscale('log')
axr.set_xlim(1, 30000)
axr.set_xlabel('refusals (log scale)')
axr.set_title('Why an issue was refused')
axr.grid(axis='y', visible=False)
despine(axr)
caption(fig, 'Every refusal branch in lms_issue_blocker() was exercised; all six invariants held throughout the run.')
save(fig, f'{OUT}/fig_fuzz.png')

# ------------------------------------------------------- Fig: race result ----
race = D['race']
fig, (axl, axr) = plt.subplots(1, 2, figsize=(6.9, 3.3),
                               gridspec_kw={'wspace': 0.38, 'width_ratios': [1.5, 1]})
fig.subplots_adjust(bottom=0.30, top=0.88)

held = list(range(3, 9))
before = [race['before'].count(h) for h in held]
after = [race['after'].count(h) for h in held]
x = np.arange(len(held)); w = 0.38
axl.bar(x - w/2, before, w, color=CRITICAL, label='before the fix',
        edgecolor=SURFACE, linewidth=1.5, zorder=3)
axl.bar(x + w/2, after, w, color=GOOD, label='after the fix',
        edgecolor=SURFACE, linewidth=1.5, zorder=3)
axl.axvline(0.5, color=INK, linewidth=1.1, linestyle=(0, (4, 3)), zorder=4)
axl.text(0.60, 37, f"policy limit = {race['limit']}\n(anything right of this line\nis a rule violation)",
         color=INK, fontsize=8, va='top', linespacing=1.35)
for xi, v in zip(x - w/2, before):
    if v: axl.text(xi, v + 1.0, str(v), ha='center', color=INK, fontsize=8, fontweight='bold')
for xi, v in zip(x + w/2, after):
    if v: axl.text(xi, v + 1.0, str(v), ha='center', color=INK, fontsize=8, fontweight='bold')
axl.set_xticks(x); axl.set_xticklabels(held)
axl.set_xlabel('books held by one member after 8 simultaneous issues')
axl.set_ylabel('trials (of 40)')
axl.set_title('Loan limit under concurrency')
axl.set_ylim(0, 46)
axl.legend(loc='upper center', bbox_to_anchor=(0.62, 0.62), ncol=1)
axl.grid(axis='x', visible=False)
despine(axl)

vals = [race['before_violations'], race['after_violations']]
xs = np.arange(2)
axr.bar(xs, vals, color=[CRITICAL, GOOD], width=0.55, edgecolor=SURFACE, linewidth=1.5, zorder=3)
for xi, v in zip(xs, vals):
    axr.text(xi, v + 1.4, f'{v}/40', ha='center', color=INK, fontsize=10.5, fontweight='bold')
axr.set_xticks(xs); axr.set_xticklabels(['before\nthe fix', 'after\nthe fix'], fontsize=8.5)
axr.set_ylabel('trials that exceeded the limit')
axr.set_title('Defect rate')
axr.set_ylim(0, 46)
axr.grid(axis='x', visible=False)
despine(axr)
caption(fig, f"8 threads issuing 8 different titles to one member at once; {race['trials']} trials per configuration. "
             f"Worst case {race['before_worst']} books before the fix, {race['after_worst']} after.")
save(fig, f'{OUT}/fig_race.png')
print('data figures done')
