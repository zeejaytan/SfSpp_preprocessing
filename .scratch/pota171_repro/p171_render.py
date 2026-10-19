import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
A = Path('artifacts/pota171')
def xyz(p):
    return np.loadtxt(A / p, delimiter=' ', usecols=(0,1,2))
counts = {
 'P01_0': (220,217,210), 'P01_1': (337,190,210),
 'P02_0': (181,97,743),  'P02_1': (174,174,171),
 'P03_0': (167,80,502),  'P03_1': (164,164,163),
 'P04_0': (162,103,259), 'P04_1': (162,162,156),
 'P05_0': (166,97,343),  'P05_1': (155,155,152),
 'P06_0': (160,129,158), 'P06_1': (156,148,152),
 'P07_0': (81,75,80),    'P07_1': (82,82,79),
 'P08_0': (79,79,77),    'P08_1': (76,66,71),
}
labels = list(counts)
nv = [counts[k][0]-11 for k in labels]
cu = [counts[k][1]-11 for k in labels]
ba = [counts[k][2]-11 for k in labels]
x = np.arange(len(labels))
plt.figure(figsize=(14,5))
plt.bar(x-0.25, cu, 0.25, label='veto-cured (155)', color='steelblue')
plt.bar(x, nv, 0.25, label='veto-free POTA171_NOVETO', color='firebrick')
plt.bar(x+0.25, ba, 0.25, label='production base (old seq)', color='gray', alpha=0.6)
plt.xticks(x, labels, rotation=45)
plt.ylabel('dots (pcd lines minus 11 header)')
plt.title('Pot A pairs: veto-free vs veto-cured vs production base (same staged surfaces)')
plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(A / 'p171_counts.png', dpi=90); plt.close()
print('counts ok')
pairs = [('Pot_A_Piece_02_Breakline_0','REGRESS P02 Bl_0: 170 vs 86'),('Pot_A_Piece_03_Breakline_0','REGRESS P03 Bl_0: 156 vs 69'),('Pot_A_Piece_01_Breakline_0','HOLD P01 Bl_0: 209 vs 206'),('Pot_A_Piece_01_Breakline_1','ANOMALY P01 Bl_1: 326 vs 179'),('Pot_A_Piece_08_Breakline_0','HOLD P08 Bl_0: 68 vs 68')]
for stem, title in pairs:
    c = xyz(stem + '_cure.xyz'); n = xyz(stem + '_noveto.xyz')
    fig, ax = plt.subplots(1, 2, figsize=(12,5))
    ax[0].scatter(c[:,0], c[:,1], s=4, c='steelblue', label='cured')
    ax[0].scatter(n[:,0], n[:,1], s=4, c='firebrick', alpha=0.5, label='noveto')
    ax[0].set_title(title + ' [top XY]'); ax[0].legend(fontsize=8)
    ax[0].set_aspect('equal', adjustable='datalim')
    ax[1].scatter(c[:,0], c[:,2], s=4, c='steelblue', label='cured')
    ax[1].scatter(n[:,0], n[:,2], s=4, c='firebrick', alpha=0.5, label='noveto')
    ax[1].set_title(title + ' [side XZ]'); ax[1].legend(fontsize=8)
    ax[1].set_aspect('equal', adjustable='datalim')
    fig.tight_layout(); fig.savefig(A / ('p171_' + stem + '.png'), dpi=90); plt.close(fig)
    print('overlay ok', stem, len(c), len(n))