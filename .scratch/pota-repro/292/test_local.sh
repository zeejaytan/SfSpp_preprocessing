#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=python
R=test_run
rm -rf $R; mkdir -p $R/out/logs $R/out/lanes $R/out/png $R/out/tiles $R/out/status $R/out/errors $R/out/recheck $R/out/deleted $R/bin/edge $R/bin/mesh
cp score292.py recompute292.py miss_png.py summary292.py potpng292.py $R/
$PY - <<PYEOF
import numpy as np, os
R = "test_run"
def write(path, pts):
    n = len(pts)
    hdr = ["VERSION 0.7", "FIELDS x y z", "SIZE 4 4 4", "TYPE F F F", "COUNT 1 1 1",
           "WIDTH %d" % n, "HEIGHT 1", "VIEWPOINT 0 0 0 1 0 0 0", "POINTS %d" % n, "DATA ascii"]
    with open(path, "w") as f:
        f.write("\n".join(hdr) + "\n")
        for p in pts:
            f.write("%.6f %.6f %.6f\n" % tuple(p))
t = np.linspace(0, 2 * np.pi, 200, endpoint=False)
ring = np.vstack([100 * np.cos(t), 100 * np.sin(t), 5 * np.sin(3 * t)]).T
ours = ring.copy()
ours[:, 0] += 1.0
os.makedirs(R + "/tmp", exist_ok=True)
write(R + "/tmp/ours.pcd", ours)
write(R + "/tmp/auth.pcd", ring)
bad = ring.copy()
bad[:, 1] += 6.0
write(R + "/tmp/ours_bad.pcd", bad)
print("fake pcds written")
PYEOF

# one good lane, one stub lane that must fail the bar, one author-excluded piece
for spec in "Pot_A_Piece_01 0 tmp/ours.pcd tmp/auth.pcd" "Pot_A_Piece_01 1 tmp/ours_bad.pcd tmp/auth.pcd" "Pot_J_Piece_09 1 tmp/ours.pcd tmp/auth.pcd" "Pot_F_Piece_07 0 tmp/ours.pcd tmp/auth.pcd"; do
  set -- $spec
  POT=${1%%_Piece_*}
  ROW=$($PY score292.py $POT $1 $2 $R/$3 $R/$4)
  printf "%s\n" "$ROW" >> $R/out/lanes/$1.tsv
  AT=$($PY -c "import sys;print(sys.argv[1].split(chr(9))[12])" "$ROW")
  $PY miss_png.py $1 $2 $R/$3 $R/$4 $R/out/png $R/out/tiles "$AT"
  echo "$1 $2 at_bar=$AT"
done
$PY recompute292.py Pot_A_Piece_01 0 $R/tmp/ours.pcd $R/tmp/auth.pcd $R/out/lanes/Pot_A_Piece_01.tsv

# status, errors, deleted records, a build.json
printf "Pot_A_Piece_01\tstage=0\tmesh=0\tedge=0\tclassify=1\tsecs=41\tlanes=2\tbigfiles_in_out=0\tstage_root=/tmp\tbody_bag=1\tseed_lines=2\tstop_lines=0\tfull263=3\tvote247=6\n" > $R/out/status/Pot_A_Piece_01.tsv
printf "Pot_J_Piece_09\tstage=0\tmesh=0\tedge=0\tclassify=1\tsecs=38\tlanes=1\tbigfiles_in_out=0\tstage_root=/tmp\tbody_bag=1\tseed_lines=2\tstop_lines=0\tfull263=3\tvote247=6\n" > $R/out/status/Pot_J_Piece_09.tsv
printf "Pot_E_Piece_31\tpipeline\t1\tstage=0 mesh=1 edge=- classify=0\n" > $R/out/errors/Pot_E_Piece_31.tsv
printf "piece=Pot_A_Piece_01 node=x stage=/tmp/x\n16M\t/tmp/x\n42\n" > $R/out/deleted/Pot_A_Piece_01.tsv
echo "{\"commit\": \"787c149\", \"node\": \"n1\", \"edge_md5\": \"e\", \"mesh_md5\": \"m\"}" > $R/out/build.json
printf "corpus_unchanged=YES\n" > $R/out/corpus_check.txt
printf "files over 1 MiB outside bin: 0\n" > $R/out/geometry_check.txt

$PY summary292.py $R
$PY potpng292.py $R
echo "== summary head"; sed -n "1,30p" $R/out/summary.md
echo "== below-bar section"; sed -n "/## Lanes below bar/,/^$/p" $R/out/summary.md | head -12
echo "== files"; ls $R/out/png $R/out/tiles | head -20