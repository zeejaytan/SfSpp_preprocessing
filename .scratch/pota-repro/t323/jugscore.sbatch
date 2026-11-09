#!/bin/bash
#SBATCH --job-name=t323-jugscore
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-juglet/logs/jugscore_%j.out
# Ticket 323: score the Juglet F20K3 arms against Dataset/Juglet_GT (the key) with the unchanged
# pot scorer (score311_cpp.py, C++ CountResult bars 0.35 rad / 50 mm). F20O is void (its axes are not a reference).
set -euo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-juglet
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
GT=/data/gpfs/projects/punim2657/Dataset/Juglet_GT
K=$R/score/gtkey; mkdir -p $K
for n in 1 2 3 4 5 6 7 8 9; do ln -sf $GT/Juglet_Piece_${n}_T.txt $K/Pot_JUG_Piece_${n}_T.txt; done
ln -sf $GT/Juglet_simple_graph.txt $K/Pot_JUG_simple_graph.txt
md5sum $GT/*_T.txt $GT/Juglet_simple_graph.txt
for a in F20K3_r1 F20K3_r2; do
  $PY /data/gpfs/projects/punim2657/SfSpp/runs/20261110-0506_d628fc0_t322k1-potA/work/score311_cpp.py $R/out/$a $K JUG $R/score/${a}_key.json $a
  $PY -c "
import json; d=json.load(open('$R/score/${a}_key.json'))
nt={(1,5),(1,6),(3,7),(4,5),(4,6),(5,9),(6,8),(7,8),(8,9)}
print('$a', 'sherds', d['n_sherd'], '/9', 'T files', d['n_T_files'], 'missing', d['missing_T_pieces'])
ok=[(j['i'],j['j']) for j in d['joins'] if j['pass_cpp']]
print('joins pass /18', len(ok), ' touching-only pass', sum(p not in nt for p in ok), '/', 18-len(nt))
for j in d['joins']: print(j['i'], j['j'], 'nontouch' if (j['i'],j['j']) in nt else 'touch', j['deg'], j['t_mm'], j['pass_cpp'])
"
done
