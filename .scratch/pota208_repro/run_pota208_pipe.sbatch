#!/bin/bash
# POTA-208 pristine-line pipe: mesh+edge from e2e-pristine binaries, ORIG axes, bundle v0.
# Adapts pota28 pipe mechanics; cure hunks/guards replaced by pristine guards.
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --job-name=pota208_pipe
#SBATCH --output=pota208_pipe_%j.out
#SBATCH --error=pota208_pipe_%j.err
set -uo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-e2e-pristine
SRC1="${WROOT}/edgeline_extraction_headless.cpp"
SRC2="${WROOT}/mesh_processing_headless.cpp"
BUILD="${WROOT}/build-e2e"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
POT=Pot_A
ORIG=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
TREE=/data/gpfs/projects/punim2657/pota208_pipe
BUN=/data/gpfs/projects/punim2657/pota208_bundle_v0/SfS_pp
echo "=== POTA-208 PRISTINE PIPE ==="; date; hostname
echo "### guard: worktree HEAD must be b1ed4d1"
[ "$(git -C "${WROOT}" rev-parse HEAD)" = "b1ed4d1ff7630ded7019375460c262ff8cf32447" ] || { echo WRONG-HEAD; exit 1; }
git -C "${WROOT}" status --porcelain | grep -v "^??" && { echo TRACKED-DIRTY; exit 1; } || echo "tracked clean"
echo "### guard: zero behavior markers (207 B/M sets)"
EB=$(grep -c -E 'convertToMM|ADAPTIVE|adaptiveDensifyBreakline|load_ply_pointnormals_robust|is_valid_normals|estimate_normals_from_xyz|load_pointnormals_from_cleaned_surface|transposeInPlace|sensitivity_divisor|BUG FIX|SEGMENT FILTER|SEGMENT SAFETY|RIM DETECTION SAFETY|geometric-curvature|getPointsOnFracturedSurface|Surface_F' "${SRC1}" || true)
EBDEF=$(grep -c "^void getPointsOnFracturedSurface" "${SRC1}" || true); EB=$((EB - EBDEF))
MB=$(grep -c -E 'ADAPTIVE|dynMinCluster|dynK|convertToMM|boundary_radius_mm|curv_k' "${SRC2}" || true)
echo "edge-markers=${EB} mesh-markers=${MB}"
[ "${EB}" = "0" ] || { echo EDGE-MARKERS-PRESENT; exit 1; }
[ "${MB}" = "0" ] || { echo MESH-MARKERS-PRESENT; exit 1; }
echo "### guard: cure hunks must be ABSENT (pristine)"
for tag in SFS-T24 SFS-T27 SFS-T21 SFS-T23 SFS-T13 SFS-T04 P22FIX; do grep -q "$tag" "${SRC1}" "${SRC2}" 2>/dev/null && { echo "CURE-HUNK-PRESENT:$tag"; exit 1; } || true; done
echo "no cure hunks"
[ -x "${BUILD}/MeshPreprocessingHeadless" ] || { echo MESH-BINARY-MISSING; exit 1; }
[ -x "${BUILD}/EdgeLineExtractionHeadless" ] || { echo EDGE-BINARY-MISSING; exit 1; }
echo "binaries OK"
echo "### mesh run (pristine; ORIG axes copied as pipeline input, 28 precedent)"
rm -rf "${TREE}"
mkdir -p "${TREE}/Temp/Data/${POT}" "${TREE}/Dataset/Mesh/${POT}" "${TREE}/Dataset/Point/${POT}" "${TREE}/Dataset/Surfaces/${POT}" "${TREE}/Dataset/Breaklines/${POT}" "${TREE}/Dataset/Axes"
n=0; for f in "${WROOT}/Dataset/Mesh/${POT}"/*.obj; do [ -e "$f" ] || continue; cp -L "$f" "${TREE}/Dataset/Mesh/${POT}/"; n=$((n+1)); done
for f in "${WROOT}/Dataset/Point/${POT}"/*; do [ -e "$f" ] || continue; cp "$f" "${TREE}/Dataset/Point/${POT}/"; done
for i in 01 02 03 04 05 06 07 08; do cp -L "${ORIG}/Axes/Pot_A_Piece_${i}_Axis.xyz" "${TREE}/Dataset/Axes/"; done
echo "meshes=${n}"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" env POT_NAME="${POT}" "${BUILD}/MeshPreprocessingHeadless" ) > "${TREE}/mesh_stage.log" 2>&1
echo "mesh exit $? (not trusted)"
for i in 01 02 03 04 05 06 07 08; do for s in 0 1; do f="${TREE}/Temp/Data/${POT}/Pot_A_Piece_${i}_Surface_${s}.xyz"; [ -f "$f" ] && echo "  p${i} S${s}: $(wc -l < "$f") pts" || echo "  p${i} S${s}: MISSING"; done; done
echo "### edge run (pristine)"
mkdir -p "${TREE}/Dataset/Breaklines/${POT}"
( cd "${TREE}" && "${APPTAINER}" exec --bind /data:/data "${SIF}" env POT_NAME="${POT}" "${BUILD}/EdgeLineExtractionHeadless" ) > "${TREE}/edgeline_stage.log" 2>&1
echo "edge exit $? (not trusted)"
echo "### header census (Bl0 + Bl1: segments + POINTS)"
for i in 01 02 03 04 05 06 07 08; do for b in 0 1; do f="${TREE}/Dataset/Breaklines/${POT}/Pot_A_Piece_${i}_Breakline_${b}.pcd"; [ -f "$f" ] && echo "p$i Bl$b: $(sed -n '2p' "$f") pts=$(grep -a '^POINTS' "$f" | awk '{print $2}')" || echo "p$i Bl$b MISSING"; done; done
echo "### 207-risk-1 audit: fracture (Bl1) outputs"
for i in 01 02 03 04 05 06 07 08; do f="${TREE}/Dataset/Breaklines/${POT}/Pot_A_Piece_${i}_Breakline_1.pcd"; [ -f "$f" ] && echo "p$i Bl1 pts=$(grep -a '^POINTS' "$f" | awk '{print $2}')" || echo "p$i Bl1 MISSING"; done
echo "### stage assembly bundle v0 (direct edge output)"
rm -rf "/data/gpfs/projects/punim2657/pota208_bundle_v0"; mkdir -p "${BUN}/Axes" "${BUN}/Breaklines" "${BUN}/Ground Truth" "${BUN}/Mesh" "${BUN}/Surfaces"
cp -L "${TREE}/Dataset/Breaklines/${POT}"/*.pcd "${BUN}/Breaklines/"
cp -L "${TREE}/Dataset/Surfaces/${POT}"/*.xyz "${BUN}/Surfaces/"
cp -L "${ORIG}/Axes"/Pot_A_Piece_*.xyz "${BUN}/Axes/"
cp -L "${ORIG}/Ground Truth"/Pot_A_Piece_*_T.txt "${ORIG}/Ground Truth"/Pot_A_simple_graph.txt "${BUN}/Ground Truth/"
cp -L "${TREE}/Dataset/Mesh/${POT}"/*.obj "${BUN}/Mesh/"
echo "breaklines=$(ls "${BUN}/Breaklines" | wc -l) surfaces=$(ls "${BUN}/Surfaces" | wc -l)"
md5sum "${BUN}/Breaklines"/*.pcd | sort > /data/gpfs/projects/punim2657/pota208_bun_v0_md5.txt
echo "=== POTA-208 pipe DONE; D-walk composition + stage next ==="; date
