#!/bin/bash
#SBATCH --job-name=t37phase1
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1404_c16e274_t37-adaptive-default/logs/slurm-%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1404_c16e274_t37-adaptive-default/logs/slurm-%j.err
# ticket 37 -- the adaptive step becomes the default, and the regions under the floor.
#
# PHASE 1 (1 == 1) builds two binaries and answers the two identity proofs plus the arm
# table.  55 cells.
#   AFIX  the PRE-CHANGE binary (5bdaff6) + SFS_SPACING_POLICY=fixed   ]
#   BFIX  this ticket's binary         + SFS_SPACING_POLICY=fixed      ] proof 1: same md5 of
#   A     this ticket's binary, NO environment at all                    SampledWithNormals.ply
#                                                                      ] proof 2: ticket 36 arm B's
#   B     A + SFS_SINGLE_CLUSTER=write                                 ] surface counts on J1 10800/
#   C     B + SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=0.005             15780, J5 229/2317, J7 1753/
#   D     the pre-change behaviour: SFS_SPACING_POLICY=fixed           1997, Pot A 8 of 8
# Arm A runs on all 14 pieces because proof 2 needs Pot A 8 of 8 and the table needs 9; B, C and D
# run on the 9 pieces the ticket names; AFIX/BFIX on the 7 pieces proof 1 names.
# SFS_SPACING_SAMPLES stays unset everywhere: its default is already 200.  SFS_COUNT_SCALE is set
# only in C, because the ticket keeps the scaled counts off by default and the floor-cap switch is
# armed only when the counts are scaled (mesh_processing_headless.cpp:3625).
#
# PHASE 2 (1 == 2) is the part C/D grid: 16 cells, one binary, every cell with a rung-2
# dump and the python replica reading it before the dump is deleted.
#   NA   adaptive (the new default) + SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest
#   PDN  as NA, and the replica writes the part D per-point region files
#   FX   SFS_SPACING_POLICY=fixed + the same honest nearest-carry normals -- the spacing control
#   RA   adaptive with the pipeline's own re-estimated normals -- literally the new default
#        configuration, which is what part C's re-validation has to be proven on
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1404_c16e274_t37-adaptive-default
RUNID=20261027-1404_c16e274_t37-adaptive-default
NEW=c16e2743965a6b30afe78db63a7dd0b8f420b19f
ORIG=5bdaff656f7aa683d5d2bc66f7c3fc2e6c31986f
PHASE=1
IXTAG=t37-adaptive-default
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
BOOT=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1/out/boot
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=$RUN/instruments
OUT=$RUN/out
ECELLS=$OUT/cells
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
IDX=$RUNS/index.tsv
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
unset SFS_COUNT_SCALE SFS_SPACING_POLICY SFS_SPACING_SAMPLES SFS_NORMAL_SOURCE SFS_NORMAL_CARRY \
      SFS_SINGLE_CLUSTER SFS_FLOOR_CEILING SFS_DOWNSAMPLE_TARGET SFS_DUMP_STAGE SFS_DUMP_PIECES \
      SFS_PAPER_THETA SFS_PAPER_KAPPA SFS_PAPER_NB SFS_PAPER_CHAIN 2>/dev/null || true
export CANON CORP DS BOOT SIF APT PY INSTR OUT ECELLS RUN RUNID NEW ORIG PHASE IXTAG RUNS IDX JOBID P

cd "$RUN" || exit 1
mkdir -p "$OUT" "$ECELLS" logs

fail() {
  local rc=$1; shift
  {
    echo "runid=$RUNID"
    echo "jobid=$JOBID"
    echo "commit=$NEW"
    echo "tag=$IXTAG"
    echo "rc=$rc"
    echo "reason: $*"
    date -u +"at %Y-%m-%dT%H:%M:%SZ"
  } > "$OUT/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=$rc $* (see out/RUN-FAILED.txt)"
  exit "$rc"
}

echo "[JOB] runid=$RUNID job=$JOBID tag=$IXTAG phase=$PHASE new=$NEW orig=$ORIG host=$(hostname)"
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
if ! git -C "$CANON" cat-file -e "${NEW}^{commit}" 2>>logs/fetch.log; then
  fail 2 "commit $NEW not in $CANON"
fi
if [ "$PHASE" = "1" ] && ! git -C "$CANON" cat-file -e "${ORIG}^{commit}" 2>>logs/fetch.log; then
  fail 2 "pre-change commit $ORIG not in $CANON"
fi
echo "[JOB] commits ok new=$(git -C "$CANON" rev-parse --short "$NEW") orig=$(git -C "$CANON" rev-parse --short "$ORIG")"

hash_inputs() {
  local out=$1 f
  {
    for f in "$DS"/Point/Juglet/*.pcd "$DS"/Mesh/Juglet/*.obj \
             "$CORP"/Point/Pot_A/*.pcd "$CORP"/Mesh/Pot_A_Piece_*.obj \
             "$CORP"/Axes/*.xyz "$BOOT"/*_boot_Axis.xyz \
             "$SIF" "$INSTR"/measure34.py "$INSTR"/run_cell37.sh \
             "$INSTR"/stage_piece_p37.sh "$INSTR"/pair_ref30.py \
             "$INSTR"/compare36.py "$INSTR"/replica37.py \
             "$INSTR"/submit37.sbatch.tmpl; do
      if [ -f "$f" ]; then
        printf "%s\t%s\t%s\n" "$(md5sum "$f" | cut -d' ' -f1)" "$(stat -c %s "$f")" "$f"
      else
        printf "MISSING\t0\t%s\n" "$f"
      fi
    done
  } | sort -k3 > "$out"
}

corpus_tree() {
  local out=$1
  {
    find "$CORP" -type f -printf "%p\t%s\t%T@\n" | sort
    find "$DS" -type f -printf "%p\t%s\t%T@\n" | sort
    if [ -d /opt/sfs-pristine ]; then
      echo "opt-sfs-pristine PRESENT $(ls -R /opt/sfs-pristine | md5sum | cut -d' ' -f1)"
    else
      echo "opt-sfs-pristine ABSENT"
    fi
  } > "$out"
}

pristine_record() {
  local out=$1
  {
    echo "# /opt/sfs-pristine, recorded from the compute node"
    if [ -d /opt/sfs-pristine ]; then
      echo "status PRESENT"
      ls -la /opt/sfs-pristine
    else
      echo "status ABSENT"
      ls -d /opt/sfs-pristine 2>&1 || true
      stat /opt/sfs-pristine 2>&1 || true
    fi
  } > "$out"
}

build_arm() {
  local name=$1 sha=$2 rc
  echo "[BUILD] $name from $sha"
  mkdir -p "build/$name/src/build"
  git -C "$CANON" archive "$sha" | tar -x -C "build/$name/src" || { echo "[BUILD] archive FAILED $sha"; return 1; }
  ( cd "build/$name/src/build" \
    && "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
    && "$APT" exec --bind /data:/data "$SIF" make -j"$P" MeshPreprocessingHeadless \
  ) > "logs/build-$name.log" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ] && [ -x "build/$name/src/build/MeshPreprocessingHeadless" ]; then
    cp -f "build/$name/src/build/MeshPreprocessingHeadless" "$OUT/bin-$name"
    echo "[BUILD] $name ok $(stat -c %s "$OUT/bin-$name") bytes md5=$(md5sum "$OUT/bin-$name" | cut -d' ' -f1)"
    return 0
  fi
  echo "[BUILD] $name FAILED rc=$rc -- tail of logs/build-$name.log:"
  tail -30 "logs/build-$name.log"
  return 1
}

# The arm switches are spelled out literally below, on purpose.  They were variables in the first
# version of the ticket 36 template (run 20261028-0004, job 33880164), and an exported function runs
# inside a child shell of xargs that never saw them: arms B and C expanded to the empty string and
# ran as copies of A.  A literal cannot be dropped by a missing export.
run_cell_one() {
  local line="$1" tag pot piece
  [ -n "${line:-}" ] || return 0
  read -r tag pot piece <<< "$line"
  POT="$pot"; PIECE="$piece"; TAG="$tag"
  REPLICA=0
  case "$tag" in
    AFIX) ENVS="SFS_SPACING_POLICY=fixed"; BIN="$OUT/bin-orig" ;;
    BFIX) ENVS="SFS_SPACING_POLICY=fixed"; BIN="$OUT/bin-new" ;;
    A)    ENVS=""; BIN="$OUT/bin-new" ;;
    B)    ENVS="SFS_SINGLE_CLUSTER=write"; BIN="$OUT/bin-new" ;;
    C)    ENVS="SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=0.005 SFS_SINGLE_CLUSTER=write"; BIN="$OUT/bin-new" ;;
    D)    ENVS="SFS_SPACING_POLICY=fixed"; BIN="$OUT/bin-new" ;;
    NA)   ENVS="SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest"; BIN="$OUT/bin-new"; REPLICA=1 ;;
    PDN)  ENVS="SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest"; BIN="$OUT/bin-new"; REPLICA=1 ;;
    FX)   ENVS="SFS_SPACING_POLICY=fixed SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest"; BIN="$OUT/bin-new"; REPLICA=1 ;;
    RA)   ENVS="SFS_SPACING_POLICY=piece"; BIN="$OUT/bin-new"; REPLICA=1 ;;
    *) echo "[CELL] unknown arm $tag in spec $line"; return 9 ;;
  esac
  if [ "$pot" = "Pot_A" ]; then AXIS="$CORP/Axes/${piece}_Axis.xyz"
  else AXIS="$BOOT/${piece}_boot_Axis.xyz"; fi
  STAGER="$INSTR/stage_piece_p37.sh"
  COMMIT="$NEW"
  CELLROOT="$ECELLS"
  MEAS="$INSTR/measure34.py"
  export POT PIECE TAG BIN ENVS AXIS STAGER COMMIT CELLROOT MEAS REPLICA INSTR
  bash "$INSTR/run_cell37.sh" "$tag"
}
export -f run_cell_one

hash_inputs "$OUT/inputs_before.md5"
corpus_tree "$OUT/corpus_before.txt"
pristine_record "$OUT/pristine.txt"
echo "[JOB] inputs hashed: $(wc -l < "$OUT/inputs_before.md5") rows, tree $(wc -l < "$OUT/corpus_before.txt") rows"
grep -m1 "opt-sfs-pristine" "$OUT/corpus_before.txt" || true
cat "$OUT/pristine.txt"

echo "[JOB] instrument selftest"
"$PY" "$INSTR/measure34.py" selftest 2>&1 | tee logs/selftest.log
SRC_RC=${PIPESTATUS[0]}
[ "$SRC_RC" -eq 0 ] || fail 5 "measure34.py selftest rc=$SRC_RC (logs/selftest.log); no measurement was taken"
echo "[JOB] the other instruments' selftests"
"$PY" "$INSTR/replica37.py" selftest 2>&1 | tee logs/selftest-replica37.log
REP_RC=${PIPESTATUS[0]}
[ "$REP_RC" -eq 0 ] || fail 6 "replica37.py selftest rc=$REP_RC (logs/selftest-replica37.log); part C would rest on a broken replica"
"$PY" "$INSTR/pair_ref30.py" --selftest 2>&1 | tee logs/selftest-pair30.log
PAIR_RC=${PIPESTATUS[0]}
[ "$PAIR_RC" -eq 0 ] || fail 6 "pair_ref30.py selftest rc=$PAIR_RC (logs/selftest-pair30.log); the pair statistic would be untrustworthy"
"$PY" "$INSTR/compare36.py" selftest 2>&1 | tee logs/selftest-compare36.log
CMP_RC=${PIPESTATUS[0]}
[ "$CMP_RC" -eq 0 ] || fail 6 "compare36.py selftest rc=$CMP_RC (logs/selftest-compare36.log); the repeat proof would rest on a broken comparator"

echo "[JOB] build"
if [ "$PHASE" = "1" ]; then
  build_arm orig "$ORIG" || fail 4 "the pre-change commit did not build; see logs/build-orig.log"
fi
build_arm new "$NEW" || fail 4 "this ticket's commit did not build; see logs/build-new.log"
if [ "$PHASE" = "1" ]; then
  {
    echo "# the two binaries this run compared -- proof 1 is a property of these bytes"
    for b in orig new; do
      echo "$b md5=$(md5sum "$OUT/bin-$b" | cut -d' ' -f1) bytes=$(stat -c %s "$OUT/bin-$b") commit=$([ "$b" = orig ] && echo "$ORIG" || echo "$NEW")"
    done
  } > "$OUT/binaries.txt"
  cat "$OUT/binaries.txt"
fi

: > "$OUT/cells.list"
add() { echo "$1 $2 $3" >> "$OUT/cells.list"; }
potof() { case "$1" in Pot_A*) echo Pot_A ;; *) echo Juglet ;; esac; }
if [ "$PHASE" = "1" ]; then
  PIECES="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_5 Juglet_Piece_7 Juglet_Piece_9 Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08"
  ARMS="AFIX BFIX A B C D"
  for pc in $PIECES; do add A "$(potof "$pc")" "$pc"; done
  for pc in Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_5 Juglet_Piece_7 Juglet_Piece_9 Pot_A_Piece_01 Pot_A_Piece_07 Pot_A_Piece_08; do
    for ar in B C D; do add "$ar" "$(potof "$pc")" "$pc"; done
  done
  for pc in Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_07 Pot_A_Piece_08 Juglet_Piece_1 Juglet_Piece_3 Juglet_Piece_7; do
    add AFIX "$(potof "$pc")" "$pc"
    add BFIX "$(potof "$pc")" "$pc"
  done
else
  PIECES="Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_5 Juglet_Piece_7 Juglet_Piece_9 Pot_A_Piece_07"
  ARMS="NA PDN FX RA"
  for pc in Juglet_Piece_3 Juglet_Piece_5 Juglet_Piece_7; do add NA "$(potof "$pc")" "$pc"; done
  for pc in Juglet_Piece_2 Juglet_Piece_9 Pot_A_Piece_07; do add PDN "$(potof "$pc")" "$pc"; done
  for pc in $PIECES; do add FX "$(potof "$pc")" "$pc"; done
  for pc in Juglet_Piece_3 Juglet_Piece_5 Juglet_Piece_7 Pot_A_Piece_07; do add RA "$(potof "$pc")" "$pc"; done
fi
echo "[JOB] cells: $(wc -l < "$OUT/cells.list")"
{
  echo "# ticket 37 cell commands, one per cell: the exact env the binary ran with"
  echo "# tag pot piece | switches"
  while read -r t pt pc; do
    case "$t" in
      AFIX) e="SFS_SPACING_POLICY=fixed"; b=bin-orig ;;
      BFIX) e="SFS_SPACING_POLICY=fixed"; b=bin-new ;;
      A)    e="(none) -- the new shipped default"; b=bin-new ;;
      B)    e="SFS_SINGLE_CLUSTER=write"; b=bin-new ;;
      C)    e="SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=0.005 SFS_SINGLE_CLUSTER=write"; b=bin-new ;;
      D)    e="SFS_SPACING_POLICY=fixed"; b=bin-new ;;
      NA)   e="SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest"; b=bin-new ;;
      PDN)  e="SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest (+ part D region dump)"; b=bin-new ;;
      FX)   e="SFS_SPACING_POLICY=fixed SFS_NORMAL_SOURCE=input SFS_NORMAL_CARRY=nearest"; b=bin-new ;;
      RA)   e="SFS_SPACING_POLICY=piece (adaptive, re-estimated normals)"; b=bin-new ;;
      *)    e="?"; b="?" ;;
    esac
    echo "$t|$pt|$pc	TAB	cd <stage> && $APT exec --bind /data:/data $SIF env POT_NAME=$pt SFS_AXIS_FILE=<stage>/Dataset/Axes/$pc"'_Axis.xyz'" SFS_DUMP_STAGE=<cell>/dump $e $OUT/$b"
  done < "$OUT/cells.list"
} > "$OUT/commands.txt"

date -u +"cells start %Y-%m-%dT%H:%M:%SZ"
xargs -a "$OUT/cells.list" -d "\n" -n 1 -P "$P" bash -c 'run_cell_one "$1"' _ >> logs/cells.log 2>&1
RC_X=$?
echo "[JOB] xargs rc=$RC_X; cell.tsv written: $(ls "$ECELLS"/*/*/*/cell.tsv 2>/dev/null | wc -l) of $(wc -l < "$OUT/cells.list")"
grep -h '^\[CELL\]' logs/cells.log 2>/dev/null || true
date -u +"cells end %Y-%m-%dT%H:%M:%SZ"

printf "tag\tpot\tpiece\tenvs\tmesh_exit\tmeas_exit\telapsed_s\tspacing_policy\tdiag_mm\ts0_mm\tsamples\traw_mm\tspacing_s_mm\tcount_policy\tcount_scale\tcount_mincluster\tcount_k1\tcount_k2\tnpts\tretries\tclusters_pre_merge\tclusters_post_merge\tsizes_post_merge\toutcome\tfloor\tfloor_from\tcapped\tsurf0\tsurf1\tsurf0_points\tsurf1_points\tsurf0_bytes\tkept\trepl_rc\trepl_verdict\n" > "$OUT/cells37.tsv"
for f in "$ECELLS"/*/*/*/cell.tsv; do
  [ -f "$f" ] && cat "$f" >> "$OUT/cells37.tsv"
done
echo "[JOB] cells37.tsv rows=$(( $(wc -l < "$OUT/cells37.tsv") - 1 ))"

echo "[JOB] aggregate measurement tables"
"$PY" "$INSTR/measure34.py" agg --cellroot "$ECELLS" --out "$OUT" 2>&1 | tee logs/agg.log
echo "[JOB] pair statistic on every cell that wrote two surfaces (ticket 30's ruler)"
"$PY" "$INSTR/pair_ref30.py" "$ECELLS" 2>&1 | tee logs/pair-run.log
PRC=${PIPESTATUS[0]}
if [ "$PRC" -eq 0 ] && [ -f "$ECELLS/measure30.tsv" ]; then
  cp -f "$ECELLS/measure30.tsv" "$OUT/pairs30.tsv"
  echo "[JOB] pairs30.tsv rows=$(wc -l < "$OUT/pairs30.tsv")"
else
  echo "[JOB] pair_ref30 FAILED rc=$PRC; pairs30.tsv not written"
fi

if [ "$PHASE" = "1" ]; then
  # proof 1: the md5 of the sampled-and-normals cloud, per piece, for the two binaries under
  # SFS_SPACING_POLICY=fixed.  Surfaces are deliberately NOT compared by md5 anywhere in this run:
  # the mesh stage draws 30 unseeded ray casts, so two runs of one binary differ there.
  "$PY" - "$ECELLS" "$OUT" <<'PYEOF'
import hashlib, os, sys
cells, out = sys.argv[1], sys.argv[2]
def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
def find(tag):
    d = {}
    root = os.path.join(cells, tag)
    for pot in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        for pc in sorted(os.listdir(os.path.join(root, pot))):
            p = os.path.join(root, pot, pc, "surfaces", pc + "_SampledWithNormals.ply")
            if os.path.isfile(p):
                d[(pot, pc)] = (md5(p), os.path.getsize(p))
    return d
o, n = find("AFIX"), find("BFIX")
rows = ["# proof 1: SampledWithNormals.ply under SFS_SPACING_POLICY=fixed, pre-change binary vs this ticket",
        "# pot\tpiece\torig_md5\torig_bytes\tnew_md5\tnew_bytes\tcomparison"]
for k in sorted(set(o) | set(n)):
    a, b = o.get(k), n.get(k)
    am, ab = a if a else ("missing", 0)
    bm, bb = b if b else ("missing", 0)
    rows.append("%s\t%s\t%s\t%d\t%s\t%d\t%s" % (k[0], k[1], am, ab, bm, bb,
                "IDENTICAL" if (a and b and am == bm) else ("MISSING" if not (a and b) else "DIFFERENT")))
open(os.path.join(out, "proof1.md5.tsv"), "w").write("\n".join(rows) + "\n")
print("\n".join(rows))
PYEOF
  echo "[JOB] proof1.md5.tsv written"
else
  {
    printf "config\tpiece\tnpts\tregions_before\tlargest\tge10\tge20\tge30\tge50\tge_pct1\tge_pct5\tge_pct10\tlargest_depth\tfail_angle\taf_per_point\tlargest_pops\tfloor\tsurvivors\tsizes_ge_floor\tvalidation\tpipeline_clusters\n"
    for f in "$ECELLS"/*/*/*/measure/replica.tsv; do
      [ -f "$f" ] && tail -1 "$f"
    done
  } > "$OUT/replica37.tsv"
  echo "[JOB] replica37.tsv rows=$(( $(wc -l < "$OUT/replica37.tsv") - 1 ))"
  mkdir -p "$OUT/prefloor"
  for f in "$ECELLS"/*/*/*/measure/*_prefloor_regions.ply "$ECELLS"/*/*/*/measure/*_prefloor_regions.json; do
    [ -f "$f" ] && cp -f "$f" "$OUT/prefloor/"
  done
  echo "[JOB] prefloor files: $(ls "$OUT/prefloor" 2>/dev/null | wc -l)"
  echo "[JOB] replica verdicts:"
  awk -F'\t' 'NR>1 {printf "  %s %s %s\n", $1, $2, $20}' "$OUT/replica37.tsv"
fi

{
  echo "# ticket 37 -- geometry written by this run, recorded BEFORE the delete."
  echo "# The binaries stay at out/bin-orig and out/bin-new; everything below is reproducible from"
  echo "# the recorded commits and the corpus by out/commands.txt."
  echo -e "key\text\tfiles\tbytes"
  "$PY" - "$RUN" <<'PYEOF'
import os, sys
from collections import defaultdict
run = sys.argv[1]
rows = []
for root, _d, fs in os.walk(os.path.join(run, "build")):
    for f in fs:
        p = os.path.join(root, f)
        try:
            n = os.path.getsize(p)
        except OSError:
            continue
        rows.append((os.path.relpath(p, run), os.path.splitext(f)[1].lower(), n))
rows.sort()
c = defaultdict(int)
b = defaultdict(int)
for rel, ext, n in rows:
    c[ext or "none"] += 1
    b[ext or "none"] += n
for ext in sorted(c):
    print("ext\t%s\t%d\t%d" % (ext, c[ext], b[ext]))
print("#")
print("total\tall\t%d\t%d" % (len(rows), sum(b.values())))
if len(rows) <= 4000:
    for rel, ext, n in rows:
        print("file\t%s\t%s\t%d" % (rel, ext or "none", n))
else:
    print("# per-file list omitted: %d files, the per-extension totals above are complete" % len(rows))
PYEOF
  echo "#"
  echo "# KEPT: out/cells37.tsv, out/surfaces34.tsv, out/pairs34.tsv, out/carried34.tsv,"
  echo "# out/replay34.tsv, out/pairs30.tsv, out/bin-*, out/commands.txt, out/cells.list,"
  echo "# out/inputs_before.md5, out/inputs_after.md5, out/corpus_before.txt, out/corpus_after.txt,"
  echo "# out/pristine.txt, out/cells/<tag>/<pot>/<piece>/{cell.tsv,logs/,surfaces/,measure/}, logs/"
} > "$OUT/GEOMETRY_DELETED.txt" 2>&1
head -8 "$OUT/GEOMETRY_DELETED.txt"
B_BYTES=$(du -sb "$RUN/build" 2>/dev/null | cut -f1)
B_FILES=$(find "$RUN/build" -type f 2>/dev/null | wc -l)
rm -rf "$RUN/build"
{
  echo "#"
  echo "# deleted at $(date -u +%Y-%m-%dT%H:%M:%SZ): $B_FILES files, $B_BYTES bytes (the build tree)"
  echo "# after the delete: $(find "$RUN/build" -type f 2>/dev/null | wc -l) files remain, build/ is $([ -d "$RUN/build" ] && echo present || echo gone)"
  echo "# per-cell stage and rung-dump counts: out/cells/<tag>/<pot>/<piece>/logs/geometry_counts.tsv"
} >> "$OUT/GEOMETRY_DELETED.txt"
echo "[JOB] build tree deleted: $B_FILES files, $B_BYTES bytes"
{
  echo "# cells whose stage and rung dump were NOT deleted because the measurement or the replica failed"
  found=0
  for d in "$ECELLS"/*/*/*/cell.tsv; do
    [ -f "$d" ] || continue
    k=$(cut -f33 "$d")
    if [ "$k" = "yes" ]; then echo "$d"; found=$((found + 1)); fi
  done
  echo "# count $found"
} > "$OUT/GEOMETRY_KEPT.txt" 2>&1
tail -4 "$OUT/GEOMETRY_KEPT.txt"

hash_inputs "$OUT/inputs_after.md5"
corpus_tree "$OUT/corpus_after.txt"
if diff -q "$OUT/inputs_before.md5" "$OUT/inputs_after.md5" > "$OUT/inputs.diff" 2>&1; then
  echo "[INPUTS] identical before and after: $(wc -l < "$OUT/inputs_before.md5") rows"
else
  echo "[INPUTS] DIFFERS"; cat "$OUT/inputs.diff"
fi
if diff -q "$OUT/corpus_before.txt" "$OUT/corpus_after.txt" > "$OUT/corpus.diff" 2>&1; then
  echo "[CORPUS] identical before and after: $(wc -l < "$OUT/corpus_before.txt") rows incl the pristine line"
else
  echo "[CORPUS] DIFFERS"; cat "$OUT/corpus.diff"
fi
grep -m1 "opt-sfs-pristine" "$OUT/corpus_after.txt" || true

# --- arm check: did each arm really run the switches it names? ---------------------------
# Worth checking, and run 20261028-0004 is why: the arm switches were passed through shell
# variables that the xargs child never saw, so arms B and C expanded to the empty string and ran as
# copies of A.  The log lines below are the pipeline's own report of what it read.
ARM_BAD=0
{
  echo "# ticket 37 arm check -- read from each arm's own per-piece mesh logs"
  echo "# arm cells spacing(correct/total) normal_input single_write count_scale verdict"
  for ar in $ARMS; do
    n=0; sp=0; ns=0; sc=0; cs=0
    for f in "$ECELLS/$ar"/*/*/logs/mesh.log; do
      [ -f "$f" ] || continue
      n=$((n + 1))
      case "$ar" in
        AFIX|BFIX|D|FX) grep -q '^\[SPACING-22\] policy=fixed' "$f" && sp=$((sp + 1)) ;;
        *)               grep -q '^\[SPACING-22\] policy=piece' "$f" && sp=$((sp + 1)) ;;
      esac
      grep -q 'normalSourceSet=yes' "$f" && ns=$((ns + 1))
      grep -q '^\[SWITCH-23\] singleCluster=write' "$f" && sc=$((sc + 1))
      grep -q '^\[COUNT-22\] policy=auto' "$f" && cs=$((cs + 1))
    done
    case "$ar" in
      AFIX|BFIX|A|D|RA) w_ns=0;    w_sc=0;    w_cs=0 ;;
      B)                w_ns=0;    w_sc=$n;   w_cs=0 ;;
      C)                w_ns=0;    w_sc=$n;   w_cs=$n ;;
      NA|PDN|FX)        w_ns=$n;   w_sc=0;    w_cs=0 ;;
      *)                w_ns=$n;   w_sc=$n;   w_cs=$n ;;
    esac
    w_sp=$n
    if [ "$sp" = "$w_sp" ] && [ "$ns" = "$w_ns" ] && [ "$sc" = "$w_sc" ] && [ "$cs" = "$w_cs" ]; then
      v=ok
    else
      v=MISMATCH; ARM_BAD=1
    fi
    echo "$ar $n $sp/$w_sp $ns/$w_ns $sc/$w_sc $cs/$w_cs $v"
  done
  echo "# the pipeline's own first line of each kind, arm by arm"
  for ar in $ARMS; do
    f=$(ls "$ECELLS/$ar"/*/*/logs/mesh.log 2>/dev/null | head -1)
    [ -n "$f" ] || continue
    echo "# $ar $(grep -m1 '^\[SPACING-22\]' "$f")"
    echo "# $ar $(grep -m1 'normalSourceSet=' "$f" | sed 's/.*\(normalSource=\)/\1/')"
    echo "# $ar $(grep -m1 '^\[COUNT-22\]' "$f")"
    echo "# $ar $(grep -m1 '^\[SWITCH-23\]' "$f")"
  done
  if [ "$PHASE" != "1" ]; then
    echo "# replica and dump, per cell (repl_rc, verdict, dump files)"
    for d in "$ECELLS"/*/*/*/cell.tsv; do
      [ -f "$d" ] || continue
      rc=$(cut -f34 "$d")
      vd=$(cut -f35 "$d")
      c=$(dirname "$d")
      npl=$(ls "$c"/measure/*_prefloor_regions.ply 2>/dev/null | wc -l)
      njs=$(ls "$c"/measure/*_prefloor_regions.json 2>/dev/null | wc -l)
      echo "# $(basename "$(dirname "$(dirname "$c")")")/$(basename "$(dirname "$c")")/$(basename "$c") repl_rc=$rc verdict=$vd partd_ply=$npl partd_json=$njs"
      # a replica MISMATCH is a result to report, not a broken job; a replica that did not run is
      [ "$rc" = "0" ] || [ "$rc" = "NA" ] || ARM_BAD=1
    done
  fi
} > "$OUT/ARMCHECK.txt" 2>&1
cat "$OUT/ARMCHECK.txt"
if [ "$ARM_BAD" -ne 0 ]; then
  {
    echo "runid=$RUNID"
    echo "jobid=$JOBID"
    echo "commit=$NEW"
    echo "tag=$IXTAG"
    echo "rc=12"
    echo "reason: at least one arm did not run the switches it names, or a replica did not run; out/ARMCHECK.txt says which"
    date -u +"at %Y-%m-%dT%H:%M:%SZ"
  } > "$OUT/RUN-FAILED.txt"
  echo "[JOB] FATAL rc=12 an arm ran the wrong switches (out/ARMCHECK.txt); no index row written"
  date -u +"end %Y-%m-%dT%H:%M:%SZ"
  exit 12
fi
echo "[JOB] arm check: every arm ran its own switches"

printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$NEW" "$IXTAG" >> "$IDX"
echo "[JOB] index row appended:"
tail -1 "$IDX" | cat -A | head -1
date -u +"end %Y-%m-%dT%H:%M:%SZ"
echo "[JOB] DONE rc 0"
