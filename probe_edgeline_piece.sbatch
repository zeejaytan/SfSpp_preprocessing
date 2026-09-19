#!/bin/bash
#SBATCH --job-name=juglet_probe
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=1:00:00
#SBATCH --output=juglet_probe_%j.out
#SBATCH --error=juglet_probe_%j.err

# Probe: run the (patched, rebuilt) EdgeLineExtractionHeadless on ONE piece.
# Discriminates piece-1-specific geometry failure (H2) from systemic
# radius/normals failure (H1/H3). Surfaces must already exist in the bundle.
# Usage: sbatch probe_edgeline_piece.sbatch  (PIECE env var, default 2)

echo "=== Juglet breakline probe ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

POT_NAME="Juglet"
PIECE="${PIECE:-2}"
OUTPUT_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916"
APPTAINER="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
NURBS_IMG="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"

export POT_NAME
export NURBS_OUTPUT_BASE="${OUTPUT_BASE}"

echo "PIECE: ${PIECE}"

# Quarantine every Temp OBJ outside Temp/ (recursive scanner), stage one.
QDIR="${OUTPUT_BASE}/_quarantine"
mkdir -p ${QDIR}/temp_objs
find Temp -name "*.obj" -exec mv -f {} ${QDIR}/temp_objs/ \; 2>/dev/null || true
cp -f Dataset/Mesh/${POT_NAME}/${POT_NAME}_Piece_${PIECE}_Mesh.obj Temp/Data/${POT_NAME}/
echo "Staged: $(ls Temp/Data/${POT_NAME}/*.obj)"

echo "=== Breakline Extraction (piece ${PIECE} only) ==="
${APPTAINER} exec --bind /data:/data \
    --env POT_NAME="${POT_NAME}" \
    --env NURBS_OUTPUT_BASE="${OUTPUT_BASE}" \
    ${NURBS_IMG} /bin/bash -c \
    "cd /data/gpfs/projects/punim2657/sfs_preprocessing && ./original_nurbs_preprocessing/build/EdgeLineExtractionHeadless"
echo "exit=$?"
echo "Breaklines for piece ${PIECE}:"
ls ${OUTPUT_BASE}/SfS_pp/Breaklines/${POT_NAME}_Piece_${PIECE}_Breakline_* 2>/dev/null
echo "Done: $(date)"
