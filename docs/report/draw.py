"""Minimal drawing toolkit for the report's schematic figures."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon

def canvas(w, h, xlim=(0, 100), ylim=(0, 100)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.axis('off')
    ax.grid(False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax

def box(ax, x, y, w, h, label, *, fc='#ffffff', ec=BASELINE, tc=INK, fs=9,
        bold=False, radius=1.6, lw=1.0, align='center', pad_top=None, alpha=1.0, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f'round,pad=0,rounding_size={radius}',
                                facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha,
                                linestyle=ls, zorder=2))
    if label:
        ty = y + h / 2 if pad_top is None else y + h - pad_top
        va = 'center' if pad_top is None else 'top'
        ha = {'center': 'center', 'left': 'left'}[align]
        tx = x + w / 2 if align == 'center' else x + 2.2
        ax.text(tx, ty, label, ha=ha, va=va, fontsize=fs, color=tc,
                fontweight='bold' if bold else 'normal', zorder=3, linespacing=1.45)

def arrow(ax, p1, p2, *, color=INK2, lw=1.2, style='-|>', ls='-', rad=0.0, zorder=4,
          mutation=11):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=mutation,
                                 color=color, linewidth=lw, linestyle=ls, zorder=zorder,
                                 connectionstyle=f'arc3,rad={rad}',
                                 shrinkA=0, shrinkB=0))

def text(ax, x, y, s, *, fs=8.5, color=INK2, ha='center', va='center', bold=False,
         style='normal', bg=None, rot=0):
    kw = {}
    if bg:
        kw['bbox'] = dict(facecolor=bg, edgecolor='none', pad=1.6)
    ax.text(x, y, s, fontsize=fs, color=color, ha=ha, va=va, rotation=rot,
            fontweight='bold' if bold else 'normal', fontstyle=style,
            zorder=5, linespacing=1.45, **kw)

def title(ax, s, sub=None, y=97):
    ax.text(50, y, s, fontsize=11, color=INK, ha='center', va='top', fontweight='bold', zorder=5)
    if sub:
        ax.text(50, y - 5.0, sub, fontsize=8.5, color=MUTED, ha='center', va='top', zorder=5)
