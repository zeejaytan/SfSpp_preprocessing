#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=logs/slurm-%j.out
#
# ticket 20, job 5 -- the density arm (plus the offline analysis in the same job).
# Builds the mesh stage once from a git archive
# of the ticket commit, then runs one environment-variable variant per run
# directory (variants.tsv). No tracked source is modified; no parameter is
# varied by copying the tree.
#
# submit: cd <job run dir> && sbatch --export=ALL,RUN_DIR=<job run dir>,COMMIT_SHA=<sha> submit.sbatch
set -uo pipefail
RUN=$(printenv RUN_DIR)
COMMIT=$(printenv COMMIT_SHA)
[ -n "$RUN" ] || { echo "[RUN] FATAL RUN_DIR unset"; exit 2; }
[ -n "$COMMIT" ] || { echo "[RUN] FATAL COMMIT_SHA unset"; exit 2; }
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DSET=$CANON/Dataset
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
RUNSROOT=/data/gpfs/projects/punim2657/SfSpp/runs
BUILDROOT=/data/gpfs/projects/punim2657/sfs-p20
STAGE1=$RUNSROOT/20261027-0055_d8af9d2_p07-juglet-stage1
unset NURBS_OUTPUT_BASE
mkdir -p "$RUN"/logs "$RUN"/out "$RUN"/bin/mesh "$RUN"/stage "$RUN"/out/boot "$RUN"/out/axes
STAMP=$(basename "$RUN" | cut -d_ -f1)
GIT7=$(basename "$RUN" | cut -d_ -f2)
md5_of() { md5sum "$1" | awk '{print $1}'; }
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT stamp=$STAMP git7=$GIT7"
echo "[RUN] SFS_ variables inherited from the environment: $(env | grep -cE '^SFS_') (0 expected)"

corpus_manifest() {
  : > "$1"
  local N P f
  for N in 1 2 3 4 5 6 7 8 9; do
    for f in "$DSET/Point/Juglet/Juglet_Piece_$N"_Point.pcd "$DSET/Mesh/Juglet/Juglet_Piece_$N"_Mesh.obj; do
      [ -f "$f" ] && printf "%s\t%s\n" "$(md5_of "$f")" "$f" >> "$1"
    done
  done
  P=Pot_A_Piece_07
  for f in "$CORP/Axes/$P"_Axis.xyz "$CORP/Mesh/$P"_Mesh.obj "$CORP/Point/Pot_A/$P"_Point.pcd; do
    [ -f "$f" ] && printf "%s\t%s\n" "$(md5_of "$f")" "$f" >> "$1"
  done
}
corpus_manifest "$RUN"/out/corpus_md5_before.tsv
echo "[RUN] corpus files hashed before: $(wc -l < "$RUN"/out/corpus_md5_before.tsv)"

git -C "$CANON" fetch origin --prune > "$RUN"/logs/fetch.log 2>&1
git -C "$CANON" cat-file -e "$COMMIT"^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
BT=$BUILDROOT/p20-build-$SLURM_JOB_ID
rm -rf "$BT"; mkdir -p "$BT"/src
git -C "$CANON" archive "$COMMIT" | tar -x -C "$BT"/src
cp -a "$CANON"/alglib "$BT"/src/alglib
INSTR=$BT/src/.scratch/juglet-breaklines/stage20/instruments
VARIANTS_IN=$(printenv VARIANTS_FILE)
[ -n "$VARIANTS_IN" ] || VARIANTS_IN=$INSTR/variants.tsv
[ -f "$VARIANTS_IN" ] || { echo "[RUN] FATAL variants file missing: $VARIANTS_IN"; exit 2; }
SWEEP=$(printenv SWEEP_DIR)
[ -n "$SWEEP" ] || { echo "[RUN] FATAL SWEEP_DIR unset"; exit 2; }
SWEEP_STAMP=$(printenv SWEEP_STAMP)
[ -n "$SWEEP_STAMP" ] || { echo "[RUN] FATAL SWEEP_STAMP unset"; exit 2; }
echo "[RUN] archived $(find "$BT"/src -type f | wc -l) files into $BT/src"
: > "$RUN"/out/source.md5
for f in mesh_processing_headless.cpp data_path.h; do
  printf "%s\t%s\t%s lines\n" "$f" "$(md5_of "$BT"/src/"$f")" "$(wc -l < "$BT"/src/"$f")" >> "$RUN"/out/source.md5
done
printf "instrument\t%s\t%s\n" "$(basename "$VARIANTS_IN")" "$(md5_of "$VARIANTS_IN")" >> "$RUN"/out/source.md5
for f in stage_piece_p20.sh run_variant.sh submit_p20_sweep.sbatch boot_axis.py; do
  printf "instrument\t%s\t%s\n" "$f" "$(md5_of "$INSTR"/"$f")" >> "$RUN"/out/source.md5
done
if [ -f "$RUN"/submit.sbatch ]; then
  if diff -q "$RUN"/submit.sbatch "$INSTR"/submit_p20_sweep.sbatch > /dev/null 2>&1; then
    echo "uploaded submit.sbatch == archived copy: yes" >> "$RUN"/out/source.md5
  else
    echo "uploaded submit.sbatch == archived copy: NO (diff follows)" >> "$RUN"/out/source.md5
  fi
fi

mkdir -p "$BT"/src/build; cd "$BT"/src/build
"$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. > "$RUN"/logs/cmake.log 2>&1
CE=$?; echo "[RUN] cmake exit=$CE"
[ "$CE" -eq 0 ] || { tail -20 "$RUN"/logs/cmake.log; exit 3; }
"$APT" exec --bind /data:/data "$SIF" make -j8 MeshPreprocessingHeadless > "$RUN"/logs/make.log 2>&1
ME=$?; echo "[RUN] make exit=$ME"
[ "$ME" -eq 0 ] || { tail -40 "$RUN"/logs/make.log; exit 4; }
M=$(find "$BT"/src/build -type f -name MeshPreprocessingHeadless | head -1)
[ -n "$M" ] || { echo "[RUN] FATAL binary not found"; exit 5; }
cp -f "$M" "$RUN"/bin/mesh/MeshPreprocessingHeadless
chmod +x "$RUN"/bin/mesh/MeshPreprocessingHeadless
MESH=$RUN/bin/mesh/MeshPreprocessingHeadless
printf '{"commit": "%s", "mesh_md5": "%s", "jobid": "%s"}\n' \
  "$COMMIT" "$(md5_of "$MESH")" "$SLURM_JOB_ID" > "$RUN"/out/build.json

# ---- axes: stage-1's own axis per piece, copied and hashed (not recomputed) ----
for N in 1 2 3 4 5 6 7 8 9; do
  P=Juglet_Piece_$N
  if [ -f "$STAGE1"/out/boot/"$P"_boot_Axis.xyz ]; then
    cp -f "$STAGE1"/out/boot/"$P"_boot_Axis.xyz "$RUN"/out/boot/
  else
    "$PY" "$INSTR"/boot_axis.py "$DSET/Point/Juglet/$P"_Point.pcd > "$RUN"/out/boot/"$P"_boot_Axis.xyz
  fi
done
for P in Juglet_Piece_1 Juglet_Piece_4 Juglet_Piece_6 Juglet_Piece_7; do
  [ -f "$STAGE1"/out/axes/"$P"_Axis.xyz ] && cp -f "$STAGE1"/out/axes/"$P"_Axis.xyz "$RUN"/out/axes/
done
for f in "$RUN"/out/boot/*.xyz "$RUN"/out/axes/*.xyz "$CORP"/Axes/Pot_A_Piece_07_Axis.xyz; do
  [ -f "$f" ] && printf "axis\t%s\t%s\n" "$(md5_of "$f")" "$f" >> "$RUN"/out/source.md5
done

# ---- the sweep ----
printf "tag\tpot\tpiece\tenv\tmesh_exit\tclusters\tsizes\tsurface_0\tsurface_1\tnotfound_lines\telapsed_s\tsegmentation_ply_md5\n" > "$RUN"/out/variants.tsv
: > "$RUN"/out/variants.log
NV=0
while IFS= read -r LINE; do
  case "$LINE" in ''|'#'*) continue ;; esac
  TAG=$(printf '%s' "$LINE" | cut -f1)
  POT=$(printf '%s' "$LINE" | cut -f2)
  P=$(printf '%s' "$LINE" | cut -f3)
  ENVS=$(printf '%s' "$LINE" | cut -f4)
  AKIND=$(printf '%s' "$LINE" | cut -f5)
  case "$AKIND" in
    boot) AX=$RUN/out/boot/"$P"_boot_Axis.xyz ;;
    pot)  AX=$RUN/out/axes/"$P"_Axis.xyz ;;
    corpus) AX=$CORP/Axes/"$P"_Axis.xyz ;;
    *) echo "[RUN] FATAL unknown axis kind '$AKIND' for $TAG"; exit 6 ;;
  esac
  if [ ! -f "$AX" ]; then echo "[RUN] FATAL axis missing $AX for $TAG"; exit 6; fi
  bash "$INSTR"/run_variant.sh "$RUNSROOT" "$STAMP" "$GIT7" "$COMMIT" "$TAG" "$POT" "$P" \
       "$ENVS" "$AX" "$AKIND" "$RUN" "$SIF" "$APT" "$MESH" \
       "$INSTR"/stage_piece_p20.sh "$INSTR"/submit_p20_sweep.sbatch "$PY" >> "$RUN"/out/variants.log 2>&1
  VE=$?
  echo "[RUN] variant $TAG exit=$VE"
  NV=$((NV + 1))
  if [ "$NV" -eq 1 ]; then
    V1=$RUNSROOT/"$STAMP"_"$GIT7"_p20-"$TAG"
    if [ -z "$(ls -A "$V1"/out/segmentation 2>/dev/null)" ]; then
      echo "[RUN] FATAL the first variant harvested no segmentation input -- stopping before the other $(( $(wc -l < "$VARIANTS_IN") - 1 ))"
      tail -25 "$V1"/logs/mesh.log 2>/dev/null
      tail -5 "$V1"/logs/stage.log 2>/dev/null
      exit 8
    fi
  fi
done < "$VARIANTS_IN"
echo "[RUN] variants run: $(($(wc -l < "$RUN"/out/variants.tsv) - 1)) of $(wc -l < "$VARIANTS_IN")"

# ---- what was written and deleted, counted ----
{
  echo "# ticket 20 job $SLURM_JOB_ID -- geometry written by the stage trees and deleted again"
  echo "# class<TAB>count<TAB>bytes, summed over the $(( $(wc -l < "$RUN"/out/variants.tsv) - 1 )) variant stage trees"
  echo "# kept: run.json, submit.sbatch, logs/ (mesh log per variant), out/segmentation/*.ply (the segmentation input), out/*.tsv"
  for f in "$RUNSROOT"/"$STAMP"_"$GIT7"_p20-*/out/geometry_counts.tsv; do
    [ -f "$f" ] || continue
    awk -F'\t' 'NR > 1 { c[$1] += $2; b[$1] += $3 } END { for (k in c) printf "%s\t%d\t%d\n", k, c[k], b[k] }' "$f"
  done | awk -F'\t' '{ c[$1] += $2; b[$1] += $3; tc += $2; tb += $3 } END { for (k in c) printf "%s\t%d\t%d\n", k, c[k], b[k]; printf "TOTAL\t%d\t%d\n", tc, tb }' | sort
  echo "# du_before sum of stage trees: $(cat "$RUNSROOT"/"$STAMP"_"$GIT7"_p20-*/run.json 2>/dev/null | grep -o '"stage_bytes_deleted": [0-9]*' | awk '{s += $2} END {print s + 0}') bytes"
  echo "# du_after of runs root p20 trees: $(du -sb "$RUNSROOT"/"$STAMP"_"$GIT7"_p20-* 2>/dev/null | awk '{s += $1} END {print s + 0}') bytes"
  echo "# frozen corpus and canonical checkout were read only; symlinked inputs were links, never copies"
} > "$RUN"/out/GEOMETRY_DELETED.txt

corpus_manifest "$RUN"/out/corpus_md5_after.tsv
if diff -q "$RUN"/out/corpus_md5_before.tsv "$RUN"/out/corpus_md5_after.tsv > /dev/null 2>&1; then
  echo "frozen corpus md5 unchanged: yes ($(wc -l < "$RUN"/out/corpus_md5_before.tsv) files)" > "$RUN"/out/corpus_verdict.txt
else
  { echo "frozen corpus md5 changed: NO"; diff "$RUN"/out/corpus_md5_before.tsv "$RUN"/out/corpus_md5_after.tsv; } > "$RUN"/out/corpus_verdict.txt
fi
cat "$RUN"/out/corpus_verdict.txt
echo "[RUN] done $(date -Is) job=$SLURM_JOB_ID"

# ---- the offline analysis, in the same job (its build tree is the one above) ----
mkdir -p "$RUN"/out/renders
echo "[RUN] analysis start $(date -Is)"
"$PY" "$INSTR"/replay_analysis.py \
  --runs-root "$RUNSROOT" \
  --stamp "$SWEEP_STAMP" \
  --out "$RUN"/out \
  --dset "$DSET" \
  --corpus "$CORP" \
  --axes "$RUN"/out \
  --variants "$SWEEP"/out/variants.tsv \
  --renders "$RUN"/out/renders 2>&1 | tee "$RUN"/logs/analysis.log
ANEXIT=${PIPESTATUS[0]}
echo "[RUN] analysis exit=$ANEXIT"
ls -l "$RUN"/out/renders 2>/dev/null

# ---- what the arm has to be read from, in one table, without a second run ----
"$PY" - "$RUNSROOT" "$STAMP" "$GIT7" "$RUN"/out/arm_table.tsv <<'PYEOF'
import sys, glob, json, os, re
runsroot, stamp, git7, dest = sys.argv[1:5]
rows = []
for d in sorted(glob.glob(os.path.join(runsroot, stamp + "_" + git7 + "_p20-*"))):
    rj = os.path.join(d, "run.json")
    if not os.path.exists(rj):
        continue
    j = json.load(open(rj))
    if "piece" not in j:
        continue
    lg = os.path.join(d, "logs", "mesh.log")
    txt = open(lg, errors="replace").read() if os.path.exists(lg) else ""
    ply = glob.glob(os.path.join(d, "out", "segmentation", "*.ply"))
    npts = "-"
    if ply:
        for line in open(ply[0], errors="replace"):
            if line.startswith("element vertex"):
                npts = line.split()[-1]
                break
    cs = re.findall(r"Number of clusters is equal to (\d+)", txt)
    mg = re.findall(r"\[PAPER-234\] pass (\d+): merge (\d+) into (\d+)", txt)
    ps = re.findall(r"\[PAPER-234\] pass (\d+) done: (\d+) clusters", txt)
    ds = [ln.strip() for ln in txt.splitlines() if "DOWNSAMPLING" in ln]
    rows.append([j.get("tag"), j.get("piece"), (j.get("env") or "-"), npts,
                 cs[0] if cs else "-", cs[-1] if cs else "-",
                 j.get("cluster_sizes"),
                 ";".join("%s>%s" % (a, b) for _p, a, b in mg) or "-",
                 ";".join("%s:%s" % p for p in ps) or "-",
                 j.get("surface_0_written"), j.get("surface_1_written"),
                 j.get("source_file_not_found_lines"),
                 " | ".join(ds)[:400] or "-",
                 os.path.basename(d)])
cols = ["tag", "piece", "env", "points_into_clustering", "clusters_first", "clusters_final",
        "cluster_sizes", "merge_fused", "merge_passes", "surface_0", "surface_1",
        "notfound_lines", "downsampling_lines", "run_dir"]
with open(dest, "w") as fh:
    fh.write("\t".join(cols) + "\n")
    for r in rows:
        fh.write("\t".join(str(x) for x in r) + "\n")
print("[RUN] arm_table rows:", len(rows))
PYEOF
find "$BT" -type f 2>/dev/null | wc -l > "$RUN"/out/analysis_build_tree_files.txt
du -sb "$BT" 2>/dev/null | awk '{print $1}' > "$RUN"/out/analysis_build_tree_bytes.txt
rm -rf "$BT"
echo "[RUN] end $(date -Is) job=$SLURM_JOB_ID"
exit "$ANEXIT"
