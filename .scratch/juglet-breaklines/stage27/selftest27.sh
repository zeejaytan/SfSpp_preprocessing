set -e
rm -rf C:/PR/worktrees/sfs/27/.tmp27; mkdir -p C:/PR/worktrees/sfs/27/.tmp27/cells/A/Pot_A/Pot_A_Piece_01/{surfaces,logs}
mkdir -p C:/PR/worktrees/sfs/27/.tmp27/cells/B/Pot_A/Pot_A_Piece_01/{surfaces,logs}
python - <<'PY'
import os
hdr = "ply\nformat ascii 1.0\nelement vertex %d\nproperty float x\nproperty float y\nproperty float z\nproperty float nx\nproperty float ny\nproperty float nz\nend_header\n"
pts = [(0,0,0),(1,0,0),(2,0,0)]
def wr(p, rows):
    with open(p,"w") as f:
        f.write(hdr % len(rows))
        for r in rows: f.write("%.6f %.6f %.6f 0 0 1\n" % r)
base="C:/PR/worktrees/sfs/27/.tmp27/cells"
wr(base+"/A/Pot_A/Pot_A_Piece_01/surfaces/Pot_A_Piece_01_Surface_0.ply", pts+[(0,0,0),(1,0,0)])
wr(base+"/A/Pot_A/Pot_A_Piece_01/surfaces/Pot_A_Piece_01_Surface_1.ply", pts)
wr(base+"/B/Pot_A/Pot_A_Piece_01/surfaces/Pot_A_Piece_01_Surface_0.ply", pts)
wr(base+"/B/Pot_A/Pot_A_Piece_01/surfaces/Pot_A_Piece_01_Surface_1.ply", pts)
open(base+"/A/Pot_A/Pot_A_Piece_01/logs/mesh.log","w").write("[DEDUPE-27] surface=0 mode=off in=5 out=3\n[DEDUPE-27] surface=1 mode=off in=3 out=3\n")
open(base+"/B/Pot_A/Pot_A_Piece_01/logs/mesh.log","w").write("[DEDUPE-27] surface=0 mode=on in=5 out=3\n[DEDUPE-27] surface=1 mode=on in=3 out=3\n")
open(base+"/A/Pot_A/Pot_A_Piece_01/breakdots.tsv","w").write("A\tPot_A\tPot_A_Piece_01\t0\tPot_A_Piece_01_Breakline_0.pcd\t61\t5\t61\t61\n")
os.makedirs("C:/PR/worktrees/sfs/27/.tmp27/dump/P/Pot_A_Piece_01", exist_ok=True)
open("C:/PR/worktrees/sfs/27/.tmp27/dump/P/Pot_A_Piece_01/r2_clusters_premerge.json","w").write('{"rung":2,"piece":"Pot_A_Piece_01","retry":0,"npts":100,"clusters":[40,30],"min_cluster":20,"points_in_no_cluster":30,"reason_counts":{}}')
open("C:/PR/worktrees/sfs/27/.tmp27/dump/P/Pot_A_Piece_01/r5_write.json","w").write('{"rung":5,"piece":"Pot_A_Piece_01","surface_vertices":[{"surface":0,"vertices":5,"distinct_positions":3},{"surface":1,"vertices":3,"distinct_positions":3}],"write_gate":"ok","retry":0,"points":100,"points_on_surface_0":5,"points_on_surface_1":3,"points_on_neither":92}')
PY
P=.scratch/juglet-breaklines/stage27/dedupe27.py
python $P surfaces C:/PR/worktrees/sfs/27/.tmp27/cells
python $P seteq C:/PR/worktrees/sfs/27/.tmp27/cells
python $P partA C:/PR/worktrees/sfs/27/.tmp27/dump/P
python $P dots C:/PR/worktrees/sfs/27/.tmp27/cells
echo ---- ; cat C:/PR/worktrees/sfs/27/.tmp27/cells/seteq27.tsv