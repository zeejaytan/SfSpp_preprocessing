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
# ticket 20, job 1 -- the sweep. Builds the mesh stage once from a git archive
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
[ -f "$INSTR"/variants.tsv ] || { echo "[RUN] FATAL instruments not in the archive: $INSTR"; exit 2; }
echo "[RUN] archived $(find "$BT"/src -type f | wc -l) files into $BT/src"
: > "$RUN"/out/source.md5
for f in mesh_processing_headless.cpp data_path.h; do
  printf "%s\t%s\t%s lines\n" "$f" "$(md5_of "$BT"/src/"$f")" "$(wc -l < "$BT"/src/"$f")" >> "$RUN"/out/source.md5
done
printf "instrument\tvariants.tsv\t%s\n" "$(md5_of "$INSTR"/variants.tsv)" >> "$RUN"/out/source.md5
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
while IFS=$'\t' read -r TAG POT P ENVS AKIND; do
  [ -z "$TAG" ] && continue
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
done < "$INSTR"/variants.tsv
echo "[RUN] variants run: $(($(wc -l < "$RUN"/out/variants.tsv) - 1)) of $(wc -l < "$INSTR"/variants.tsv)"

# ---- what was written and deleted, counted ----
{
  echo "# ticket 20 job $SLURM_JOB_ID -- geometry written by the stage trees and deleted again"
  echo "# class<TAB>count<TAB>bytes, summed over the $(( $(wc -l < "$RUN"/out/variants.tsv) - 1 )) variant stage trees"
  echo "# kept: run.json, submit.sbatch, logs/ (mesh log per variant), out/segmentation/*.ply (the segmentation input), out/*.tsv"
  for f in "$RUNSROOT"/*_p20-*/out/geometry_counts.tsv; do
    [ -f "$f" ] || continue
    awk -F'\t' 'NR > 1 { c[$1] += $2; b[$1] += $3 } END { for (k in c) printf "%s\t%d\t%d\n", k, c[k], b[k] }' "$f"
  done | awk -F'\t' '{ c[$1] += $2; b[$1] += $3; tc += $2; tb += $3 } END { for (k in c) printf "%s\t%d\t%d\n", k, c[k], b[k]; printf "TOTAL\t%d\t%d\n", tc, tb }' | sort
  echo "# du_before sum of stage trees: $(cat "$RUNSROOT"/*_p20-*/run.json 2>/dev/null | grep -o '"stage_bytes_deleted": [0-9]*' | awk '{s += $2} END {print s + 0}') bytes"
  echo "# du_after of runs root p20 trees: $(du -sb "$RUNSROOT"/*_p20-* 2>/dev/null | awk '{s += $1} END {print s + 0}') bytes"
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
