#!/bin/bash
# POTA-226 edge ONLY on transplanted P27 @8 faces (no mesh rerun, 223/225 pattern).
#SBATCH --job-name=fix226-edge
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=/data/gpfs/projects/punim2657/pota226_edgeP27_8/edge226_%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/pota226_edgeP27_8/edge226_%j.err
set -uo pipefail
WROOT=/data/gpfs/projects/punim2657/sfs-fix-221
BUILD="$WROOT/build-220"
APPTAINER=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
POT=Pot_D
TREE=/data/gpfs/projects/punim2657/pota226_edgeP27_8
LAD=/data/gpfs/projects/punim2657/pota221_ladder/thr_8
echo '===== POTA-226 EDGE P27 @8 (transplanted faces) ====='; date; hostname
[ -x "$BUILD/EdgeLineExtractionHeadless" ] || { echo EDGE-BINARY-MISSING; exit 1; }
md5sum "$BUILD/EdgeLineExtractionHeadless"
echo '--- surface byte-identity check ---'
md5sum "$TREE/Temp/Data/Pot_D/Pot_D_Piece_27_Surface_0.xyz" "$TREE/Temp/Data/Pot_D/Pot_D_Piece_27_Surface_1.xyz"
md5sum "$LAD/Pot_D_Piece_27_Surface_0.xyz" "$LAD/Pot_D_Piece_27_Surface_1.xyz"
( cd "$TREE" && "$APPTAINER" exec --bind /data:/data "$SIF" env POT_NAME="$POT" "$BUILD/EdgeLineExtractionHeadless" ) > "$TREE/edge_8.log" 2>&1
echo "edge exit: $?"
grep -a -c "LOOP-SELECT" "$TREE/edge_8.log" || true
ls -la "$TREE/Dataset/Breaklines/$POT/" 2>&1
md5sum "$TREE/Dataset/Breaklines/$POT/"* 2>&1
echo DONE; date
