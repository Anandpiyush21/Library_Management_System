"""Shared chart style: the dataviz reference palette, light surface, print output."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SURFACE   = '#ffffff'
INK       = '#0b0b0b'
INK2      = '#52514e'
MUTED     = '#898781'
GRID      = '#e1e0d9'
BASELINE  = '#c3c2b7'

S1, S2, S3, S4 = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
S5, S6, S7, S8 = '#e87ba4', '#008300', '#4a3aa7', '#e34948'

GOOD, WARNING, SERIOUS, CRITICAL = '#0ca30c', '#fab219', '#ec835a', '#d03b3b'

plt.rcParams.update({
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'savefig.facecolor': SURFACE,
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'text.color': INK,
    'axes.labelcolor': INK2,
    'axes.edgecolor': BASELINE,
    'axes.linewidth': 0.8,
    'axes.titlesize': 10.5,
    'axes.titleweight': 'bold',
    'axes.titlecolor': INK,
    'axes.grid': True,
    'grid.color': GRID,
    'grid.linewidth': 0.7,
    'xtick.color': MUTED,
    'ytick.color': MUTED,
    'xtick.labelcolor': INK2,
    'ytick.labelcolor': INK2,
    'legend.frameon': False,
    'legend.fontsize': 8.5,
    'figure.dpi': 200,
})

def despine(ax, keep=('left', 'bottom')):
    for side in ('top', 'right', 'left', 'bottom'):
        ax.spines[side].set_visible(side in keep)

def save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.12)
    plt.close(fig)
    print('wrote', path)
