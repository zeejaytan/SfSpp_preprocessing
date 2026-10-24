#!/bin/bash
#SBATCH --job-name=p287auth
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:40:00

# Ticket 287 OPTIONAL probe (lead-approved 2026-10-24, item 3): run the SAME two binaries from
# run 20261024-2046_edf679c_p287-seed on the AUTHORS' own surfaces for Pot D Piece 03 and
# Pot B Piece 01 -- two of the four frozen sheet pairs the wave-1 sweep deleted, and the two
# pieces two of the three bar lanes rest on.
# IDENTITY EVIDENCE ONLY. These lanes reproduce no prior number: every bar number in the ticket
# and in the p275 runs was measured on OUR sheets from OUR mesh stage, never on these files.
# No mesh stage runs: the authors' two Surface xyz, their Axis xyz and their Mesh DS obj are
# copied verbatim, md5'd before and after, and the edge stage is given only what it reads
# (Temp/Data/<POT>/<piece>_Surface_{0,1}.xyz, Dataset/Axes/<piece>_Axis.xyz, and any .obj whose
# 14-character stem names the piece).
set -u
RUN=${RUN_DIR:?}
CANON=${CANONICAL:?}
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
P287=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed
AUTHB=/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp
SCR=/data/gpfs/projects/punim2657/sfs-vote-248/p287-auth-${SLURM_JOB_ID}
mkdir -p "$RUN/logs" "$RUN/out" "$SCR"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
say "job $SLURM_JOB_ID on $(hostname) RUN=$RUN"
echo "binaries (run 20261024-2046_edf679c_p287-seed):"
md5sum "$P287/bin/EdgeLineExtractionHeadless_before" "$P287/bin/EdgeLineExtractionHeadless_after" | tee "$RUN/out/binaries.md5"
md5sum "$AUTHB/Surfaces/Pot_D_Piece_03_Surface_0.xyz" "$AUTHB/Surfaces/Pot_D_Piece_03_Surface_1.xyz" \
      "$AUTHB/Surfaces/Pot_B_Piece_01_Surface_0.xyz" "$AUTHB/Surfaces/Pot_B_Piece_01_Surface_1.xyz" \
      "$AUTHB/Axes/Pot_D_Piece_03_Axis.xyz" "$AUTHB/Axes/Pot_B_Piece_01_Axis.xyz" \
      "$AUTHB/Mesh/Pot_D_Piece_03_Mesh_DS.obj" "$AUTHB/Mesh/Pot_B_Piece_01_Mesh_DS.obj" | tee "$RUN/out/auth_inputs.md5"

probe() {  # $1 lab  $2 piece  $3 pot  $4 arm
  local lab="$1" piece="$2" pot="$3" arm="$4"
  local T="$SCR/run/${lab}_${arm}"
  local O="$RUN/out/${lab}_${arm}"
  rm -rf "$T"; mkdir -p "$O" "$T/Temp/Data/$pot" "$T/Dataset/Axes" "$T/Dataset/Breaklines/$pot"
  cp "$AUTHB/Surfaces/${piece}_Surface_0.xyz" "$T/Temp/Data/$pot/" || return 1
  cp "$AUTHB/Surfaces/${piece}_Surface_1.xyz" "$T/Temp/Data/$pot/" || return 1
  cp "$AUTHB/Axes/${piece}_Axis.xyz" "$T/Dataset/Axes/" || return 1
  cp "$AUTHB/Mesh/${piece}_Mesh_DS.obj" "$T/Temp/Data/$pot/${piece}.obj" || return 1
  md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*_Axis.xyz > "$O/sheets_pre.md5"
  ( cd "$T" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$pot" "$P287/bin/EdgeLineExtractionHeadless_$arm" > "$O/edge.log" 2>&1 )
  echo "EDGE_EXIT[$lab $arm]=$?" | tee "$O/exit.txt"
  md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*_Axis.xyz > "$O/sheets_post.md5"
  if diff -q "$O/sheets_pre.md5" "$O/sheets_post.md5" > /dev/null; then echo "sheets unchanged [$lab $arm]"; else echo "SHEETS CHANGED [$lab $arm]"; fi
  cp "$T/Dataset/Breaklines/$pot"/* "$O"/ 2>/dev/null
  ls -l "$O"/*.pcd 2>/dev/null
  echo "--- $lab $arm: seed / walk lines ---"
  grep -E 'FULL-263|SEED-287|STOP-267 BEGIN' "$O/edge.log" | head -6
}

for arm in before after; do
  probe D03 Pot_D_Piece_03 Pot_D "$arm"
  probe B01 Pot_B_Piece_01 Pot_B "$arm"
done

say "=== identity + behaviour, authors' sheets ==="
OUT="$RUN/out" python3 "$RUN/score287b.py" 2>&1 | tee "$RUN/out/score287b.txt"
say "=== done; scratch left at $SCR ==="
