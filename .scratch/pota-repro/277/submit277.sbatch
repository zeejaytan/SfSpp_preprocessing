#!/usr/bin/env bash
#SBATCH --job-name=p277axis
#SBATCH --time=00:40:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
# Ticket 277 proof job. Builds the post-change commit and its parent from git archive, stages one
# piece by symlink into the frozen corpus, and runs three proofs:
#   A  SFS_AXIS_FILE unset              -> the mesh stage must exit non-zero, naming the variable
#   B  SFS_AXIS_FILE at a missing path  -> the same class of failure, named differently
#   C  SFS_AXIS_FILE set, N runs per binary -> the piece's own run-to-run spread, and pre vs post
# A and B are also run with the pre-change binary, to show what the old code did instead.
# No assembler, no edge stage: this ticket is the mesh stage's axis guard only.
set -uo pipefail

[ -n "$RUN_DIR" ] || { echo "[RUN] FATAL RUN_DIR must be exported"; exit 1; }
[ -n "$COMMIT" ]  || { echo "[RUN] FATAL COMMIT must be exported"; exit 1; }
RUN=$RUN_DIR
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-248
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
PIECE="$PIECE"; [ -n "$PIECE" ] || PIECE=Pot_H_Piece_02
POT="$POT"; [ -n "$POT" ] || POT=Pot_H
REPS="$REPS"; [ -n "$REPS" ] || REPS=5

unset SFS_AXIS_FILE NURBS_OUTPUT_BASE
mkdir -p $RUN/logs $RUN/out $RUN/bin $RUN/scripts $RUN/stage $RUN/out/geom
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) commit=$COMMIT piece=$PIECE reps=$REPS"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE '^SFS_') (0 expected)"

# ---- build the post-change binary and its parent from git archive ----
git -C $CANON fetch origin --prune > $RUN/logs/fetch.log 2>&1
git -C $CANON cat-file -e $COMMIT^{commit} || { echo "[RUN] FATAL commit $COMMIT not in $CANON"; exit 2; }
PREV=$(git -C $CANON rev-parse $COMMIT^)
echo "[RUN] post commit=$COMMIT pre commit=$PREV"

build_one() { # build_one <commit> <tag>
  local c=$1 tag=$2 bt=$BUILDROOT/p277-$2-$SLURM_JOB_ID b
  rm -rf $bt; mkdir -p $bt/src
  git -C $CANON archive $c | tar -x -C $bt/src || return 3
  cp -a $CANON/alglib $bt/src/alglib
  mkdir -p $bt/src/build; cd $bt/src/build || return 3
  "$APT" exec --bind /data:/data "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. > $RUN/logs/cmake-$tag.log 2>&1 || return 4
  "$APT" exec --bind /data:/data "$SIF" make -j8 MeshPreprocessingHeadless > $RUN/logs/make-$tag.log 2>&1 || return 5
  b=$(find $bt/src/build -type f -name MeshPreprocessingHeadless | head -1)
  [ -n "$b" ] || return 6
  cp -f "$b" $RUN/bin/MeshPreprocessingHeadless.$tag; chmod +x $RUN/bin/MeshPreprocessingHeadless.$tag
  cp -f $bt/src/.scratch/pota-repro/277/spread277.py $RUN/scripts/spread277.py 2>/dev/null
  cp -f $bt/src/scripts/stage_piece.sh $RUN/scripts/stage_piece.sh
  printf '%s\t%s\t%s\n' "$tag" "$c" "$(md5sum $RUN/bin/MeshPreprocessingHeadless.$tag | awk '{print $1}')" >> $RUN/out/binaries.md5
  cd $RUN || return 6
  rm -rf $bt
}

: > $RUN/out/binaries.md5
build_one $PREV pre;  B=$?; echo "[RUN] build pre exit=$B";  [ $B -eq 0 ] || exit 10
build_one $COMMIT post; B=$?; echo "[RUN] build post exit=$B"; [ $B -eq 0 ] || exit 11
printf '{"commit": "%s", "prev_commit": "%s", "jobid": "%s", "piece": "%s", "reps": "%s"}\n' \
  "$COMMIT" "$PREV" "$SLURM_JOB_ID" "$PIECE" "$REPS" > $RUN/out/build.json
cat $RUN/out/binaries.md5

# ---- stage the piece once per run: symlinked geometry, copied axis, inputs.md5 per stage ----
stage_one() { # stage_one <name> -> echoes the stage dir
  local st=$RUN/stage/$1
  bash $RUN/scripts/stage_piece.sh "$st" "$POT" "$PIECE" > $RUN/logs/stage-$1.log 2>&1 || return 1
  echo "$st"
}

MESH_PRE=$RUN/bin/MeshPreprocessingHeadless.pre
MESH_POST=$RUN/bin/MeshPreprocessingHeadless.post

# The binaries link against the container's PCL, so every run goes through apptainer, exactly as the
# live recipes do. POT_NAME selects Dataset/{Mesh,Point}/Pot_<X> and Temp/Data/Pot_<X> at run time.
run_mesh() { # run_mesh <tag> <binary> <stage> <unset|missing|real>
  local tag=$1 bin=$2 st=$3 mode=$4 rc s0 s1 have line md5s
  local ax=$st/Dataset/Axes/"$PIECE"_Axis.xyz
  s0=$st/Temp/Data/"$POT"/"$PIECE"_Surface_0.xyz
  s1=$st/Temp/Data/"$POT"/"$PIECE"_Surface_1.xyz
  rm -f "$s0" "$s1"
  case $mode in
    unset)   ( cd "$st" && "$APT" exec --bind /data:/data "$SIF" env -u SFS_AXIS_FILE POT_NAME="$POT" "$bin" ) > $RUN/logs/mesh-$tag.log 2>&1; rc=$? ;;
    missing) ( cd "$st" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$ax.DOES-NOT-EXIST" "$bin" ) > $RUN/logs/mesh-$tag.log 2>&1; rc=$? ;;
    real)    ( cd "$st" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$ax" "$bin" ) > $RUN/logs/mesh-$tag.log 2>&1; rc=$? ;;
  esac
  echo $rc > $RUN/out/exit-$tag.txt
  have=absent; md5s=none
  if [ -f "$s0" ] && [ -f "$s1" ]; then
    have=present
    md5s=$(md5sum "$s0" "$s1" | awk '{print $1}' | tr '\n' ',')
  fi
  line=$(grep -m1 'keep size order' $RUN/logs/mesh-$tag.log || true)
  [ -n "$line" ] || line=$(grep -m1 'PAPER-234. FATAL' $RUN/logs/mesh-$tag.log || true)
  [ -n "$line" ] || line=NO_AXIS_MESSAGE
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$tag" "$mode" "$rc" "$have" "$md5s" \
    "$(grep -m1 'PAPER-234. classify: face0' $RUN/logs/mesh-$tag.log || echo NO_CLASSIFY_LINE)" \
    "$line" >> $RUN/out/cases.tsv
  if [ "$mode" = real ]; then
    mkdir -p $RUN/out/geom/$tag
    [ -f "$s0" ] && cp -f "$s0" $RUN/out/geom/$tag/Surface_0.xyz
    [ -f "$s1" ] && cp -f "$s1" $RUN/out/geom/$tag/Surface_1.xyz
  fi
  echo "[RUN] $tag ($mode) exit=$rc surfaces=$have"
  return 0
}

: > $RUN/out/cases.tsv
printf 'case\taxis_mode\texit\tsurfaces\tsurface_md5\tclassify_line\taxis_message\n' >> $RUN/out/cases.tsv

# ---- A: the variable unset ----
ST=$(stage_one A) || { echo "[RUN] FATAL stage A"; exit 12; }
run_mesh A_unset "$MESH_POST" "$ST" unset
ST=$(stage_one A_old) || { echo "[RUN] FATAL stage A_old"; exit 12; }
run_mesh A_old_unset "$MESH_PRE" "$ST" unset

# ---- B: the variable set to a path that does not exist ----
ST=$(stage_one B) || { echo "[RUN] FATAL stage B"; exit 13; }
run_mesh B_missing "$MESH_POST" "$ST" missing
ST=$(stage_one B_old) || { echo "[RUN] FATAL stage B_old"; exit 13; }
run_mesh B_old_missing "$MESH_PRE" "$ST" missing

# ---- C: the variable set, N runs per binary, spread measured not assumed ----
for R in $(seq 1 $REPS); do
  STP=$(stage_one pre_$R)  || { echo "[RUN] FATAL stage pre_$R"; exit 14; }
  run_mesh pre_$R  "$MESH_PRE"  "$STP" real
  STQ=$(stage_one post_$R) || { echo "[RUN] FATAL stage post_$R"; exit 15; }
  run_mesh post_$R "$MESH_POST" "$STQ" real
done

# ---- inputs: every staged file, resolved, with md5s ----
cat $RUN/stage/pre_1/inputs.md5 $RUN/stage/post_1/inputs.md5 > $RUN/out/inputs.md5
echo "[RUN] inputs staged: $(wc -l < $RUN/out/inputs.md5) rows"

# ---- the axis actually read, byte for byte ----
printf '%s\t%s\n' "$(md5sum $RUN/stage/pre_1/Dataset/Axes/"$PIECE"_Axis.xyz | awk '{print $1}')" "axis $PIECE" > $RUN/out/parameter.md5

# ---- measure the spread and the change ----
"$PY" $RUN/scripts/spread277.py "$RUN" $REPS > $RUN/out/spread.log 2>&1
SE=$?; echo "[RUN] spread exit=$SE"; [ $SE -eq 0 ] || tail -20 $RUN/out/spread.log
[ -f $RUN/out/spread.json ] && cat $RUN/out/spread.json

echo "[RUN] ---- cases ----"; cat $RUN/out/cases.tsv
echo "[RUN] ---- failure message, case A ----"; grep -A5 'PAPER-234. FATAL' $RUN/logs/mesh-A_unset.log | head -8
echo "[RUN] ---- failure message, case B ----"; grep -A5 'PAPER-234. FATAL' $RUN/logs/mesh-B_missing.log | head -8
echo "[RUN] done $(date -Is)"
