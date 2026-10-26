#!/usr/bin/env bash
# ticket 20: one env-var variant of the mesh stage -> one run directory.
# usage: run_variant.sh <runs_root> <stamp> <git7> <commit> <tag> <pot> <piece>
#        <env string> <axis file> <axis kind> <job run dir> <sif> <apptainer>
#        <mesh binary> <stager> <submit copy> <python3>
set -uo pipefail
ROOT=$1; shift
STAMP=$1; shift
GIT7=$1; shift
COMMIT=$1; shift
TAG=$1; shift
POT=$1; shift
P=$1; shift
ENVS=$1; shift
AXIS=$1; shift
AKIND=$1; shift
JOBRUN=$1; shift
SIF=$1; shift
APT=$1; shift
MESHBIN=$1; shift
STAGER=$1; shift
SUBMITF=$1; shift
PY=$1; shift
RUN=$ROOT/"$STAMP"_"$GIT7"_p20-"$TAG"
if [ -e "$RUN" ]; then echo "[VAR] FATAL already exists: $RUN"; exit 7; fi
ST=$RUN/stage
mkdir -p "$RUN"/logs "$RUN"/out "$RUN"/stage
cp -f "$SUBMITF" "$RUN"/submit.sbatch
cp -f "$STAGER" "$RUN"/stage_piece_p20.sh
printf "class\tcount\tbytes\n" > "$RUN"/out/geometry_counts.tsv
T0=$(date +%s)
bash "$STAGER" "$ST" "$POT" "$P" "$AXIS" > "$RUN"/logs/stage.log 2>&1
SS=$?
LOG=$RUN/logs/mesh.log
: > "$LOG"
MS=99
if [ "$SS" -eq 0 ]; then
  ( cd "$ST" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$POT" SFS_AXIS_FILE="$ST"/Dataset/Axes/"$P"_Axis.xyz $ENVS "$MESHBIN" ) >> "$LOG" 2>&1
  MS=$?
fi
T1=$(date +%s)
EL=$((T1 - T0))
CL=$(grep -m1 'Number of clusters is equal to' "$LOG" | awk '{print $NF}')
[ -z "$CL" ] && CL=NA
SIZES=$(awk '/^Cluster [0-9]+ :/ { if (!s[$2]++) { o = (o == "" ? $NF : o "," $NF) } } END { print o }' "$LOG")
[ -z "$SIZES" ] && SIZES=none
MERGE=$(grep -m1 'PAPER-234\] pass [0-9]*: merge' "$LOG" | sed 's/.*\[PAPER-234\] //')
[ -z "$MERGE" ] && MERGE=none
CLS=$(grep -m1 'PAPER-234\] classify: face0' "$LOG" | sed 's/.*\[PAPER-234\] //')
[ -z "$CLS" ] && CLS=none
SWAP=$(grep -m1 -o 'swapped -> Surface_0=interior\|kept -> Surface_0=interior' "$LOG")
[ -z "$SWAP" ] && SWAP=none
ADP=$(grep -m1 'ADAPTIVE CGAL' "$LOG" | sed 's/^.*\] //')
[ -z "$ADP" ] && ADP=none
GROW=$(grep -m1 'paper grow:' "$LOG" | sed 's/^.*\[PAPER-234\] //')
[ -z "$GROW" ] && GROW=none
RULE=$(grep -m1 'SPLITTER-234' "$LOG" | sed 's/^.*\[SPLITTER-234\] //')
[ -z "$RULE" ] && RULE=none
mkdir -p "$RUN"/out/segmentation
PLY=$(find "$ST" -name '*_SampledWithNormals.ply' 2>/dev/null | head -1)
PMD5=NA
PBYTES=0
if [ -n "$PLY" ]; then
  cp -f "$PLY" "$RUN"/out/segmentation/"$P"_SampledWithNormals.ply
  PMD5=$(md5sum "$RUN"/out/segmentation/"$P"_SampledWithNormals.ply | awk '{print $1}')
  PBYTES=$(stat -c %s "$RUN"/out/segmentation/"$P"_SampledWithNormals.ply)
fi
S0=no; S1=no
[ -f "$ST"/Temp/Data/"$POT"/"$P"_Surface_0.ply ] && S0=yes
[ -f "$ST"/Temp/Data/"$POT"/"$P"_Surface_1.ply ] && S1=yes
NOTFOUND=$(grep -c 'Warning: Source file not found' "$LOG")
DUB=0
if [ -d "$ST" ]; then
  DUB=$(du -sb "$ST" | awk '{print $1}')
  find "$ST" -type f -printf '%f\t%s\n' 2>/dev/null | awk -F'\t' '{
      n = split($1, a, "."); e = (n > 1 ? a[n] : "none");
      if (e == "pcd" || e == "ply" || e == "xyz" || e == "obj" || e == "txt") f = e; else f = "other";
      c[f]++; b[f] += $2
    } END { for (k in c) printf "%s\t%d\t%d\n", k, c[k], b[k] }' >> "$RUN"/out/geometry_counts.tsv
  rm -rf "$ST"
fi
"$PY" - "$RUN" "$SLURM_JOB_ID" "$COMMIT" "$TAG" "$POT" "$P" "$ENVS" "$AXIS" "$AKIND" "$SS" "$MS" "$EL" "$CL" "$SIZES" "$MERGE" "$CLS" "$SWAP" "$ADP" "$GROW" "$RULE" "$S0" "$S1" "$NOTFOUND" "$PMD5" "$PBYTES" "$DUB" <<'PYEOF'
import json, os, sys
(rid_dir, job, commit, tag, pot, piece, envs, axis, akind, ss, ms, el,
 cl, sizes, merge, cls, swap, adp, grow, rule, s0, s1, notfound, pmd5,
 pbytes, dub) = sys.argv[1:]
seg = os.path.join(rid_dir, "out", "segmentation", piece + "_SampledWithNormals.ply")
d = {
    "runid": os.path.basename(rid_dir),
    "ticket": 20,
    "jobid": job,
    "commit": commit,
    "tag": "p20-" + tag,
    "pot": pot,
    "piece": piece,
    "env": envs,
    "axis": axis,
    "axis_kind": akind,
    "stage_exit": int(ss),
    "mesh_exit": int(ms),
    "elapsed_s": int(el),
    "clusters": cl,
    "cluster_sizes": sizes,
    "merge_line": merge,
    "classify_line": cls,
    "face_order": swap,
    "adaptive_normals": adp,
    "paper_grow": grow,
    "splitter_rule": rule,
    "surface_0_written": s0,
    "surface_1_written": s1,
    "source_file_not_found_lines": int(notfound),
    "segmentation_input": {
        "path": seg if os.path.exists(seg) else None,
        "md5": pmd5,
        "bytes": int(pbytes),
    },
    "stage_bytes_deleted": int(dub),
    "note": "environment-variable variant only; the same commit, SIF and binary produced every run in this job",
}
with open(os.path.join(rid_dir, "run.json"), "w") as fh:
    json.dump(d, fh, indent=2)
    fh.write("\n")
PYEOF
RID=$(basename "$RUN")
printf "%s\t%s\t%s\t%s\t\t\n" "$RID" "$SLURM_JOB_ID" "$COMMIT" "$TAG" >> "$ROOT"/index.tsv
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$TAG" "$POT" "$P" "$ENVS" "$MS" "$CL" "$SIZES" "$S0" "$S1" "$NOTFOUND" "$EL" "$PMD5" > "$RUN"/out/variant.tsv
cat "$RUN"/out/variant.tsv >> "$JOBRUN"/out/variants.tsv
echo "[VAR] $TAG piece=$POT/$P env=$ENVS mesh_exit=$MS clusters=$CL sizes=$SIZES surface=$S0$S1 notfound=$NOTFOUND elapsed=$EL s"
