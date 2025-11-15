#!/bin/bash
#SBATCH --job-name=sfs_preprocessing
#SBATCH --account=punim2657
#SBATCH --partition=physical
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=6:00:00
#SBATCH --output=sfs_preprocessing_%A_%a.out
#SBATCH --error=sfs_preprocessing_%A_%a.err
#SBATCH --array=1-8

# Complete SFS Preprocessing Pipeline SLURM Script
# Author: Claude Code Assistant
# Purpose: Runs complete mesh → surfaces → breaklines → axis pipeline for pottery fragments
# Usage: sbatch slurm_complete_preprocessing.sbatch
# Array job processes pieces 1-8 in parallel

set -e  # Exit on any error

# ===============================
# Configuration
# ===============================
POT_ID="A"  # Change this for different pots (A-J)
PIECE_ID=$(printf "%02d" ${SLURM_ARRAY_TASK_ID})

# Directories
PREPROCESSING_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SFS_MAIN_DIR="/data/gpfs/projects/punim2657/sfs_main"
OUTPUT_BASE_DIR="${SFS_MAIN_DIR}/sfs_test_reconstruction/Dataset/SfS_pp"

# Input/Output paths
MESH_INPUT="${PREPROCESSING_DIR}/Dataset/Mesh/Pot_${POT_ID}/Pot_${POT_ID}_Piece_${PIECE_ID}_Mesh.obj"
SURFACE_OUTPUT_DIR="${PREPROCESSING_DIR}/Surfaces"
BREAKLINE_OUTPUT_DIR="${OUTPUT_BASE_DIR}/Breaklines/Pot_${POT_ID}"
AXIS_OUTPUT_DIR="${OUTPUT_BASE_DIR}/Axes"

# Log files
LOG_DIR="${PREPROCESSING_DIR}/logs"
MESH_LOG="${LOG_DIR}/mesh_processing_${POT_ID}_${PIECE_ID}.log"
AXIS_LOG="${LOG_DIR}/axis_extraction_${POT_ID}_${PIECE_ID}.log" 
BREAKLINE_LOG="${LOG_DIR}/breakline_extraction_${POT_ID}_${PIECE_ID}.log"

# ===============================
# Setup
# ===============================
echo "==============================================="
echo "SFS Preprocessing Pipeline - Pot ${POT_ID}, Piece ${PIECE_ID}"
echo "Started: $(date)"
echo "SLURM Job ID: ${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
echo "Node: ${SLURM_NODELIST}"
echo "==============================================="

# Create directories
mkdir -p "${LOG_DIR}" "${SURFACE_OUTPUT_DIR}" "${BREAKLINE_OUTPUT_DIR}" "${AXIS_OUTPUT_DIR}"

# Change to preprocessing directory
cd "${PREPROCESSING_DIR}"

# Load required modules
module purge
module load MATLAB/2024b_Update_3
module load Apptainer/1.3.3

echo "📁 Input mesh: ${MESH_INPUT}"
echo "📁 Output directories:"
echo "   - Surfaces: ${SURFACE_OUTPUT_DIR}"
echo "   - Breaklines: ${BREAKLINE_OUTPUT_DIR}" 
echo "   - Axes: ${AXIS_OUTPUT_DIR}"
echo ""

# ===============================
# Step 1: Mesh Processing (C++ with TPS surfaces)
# ===============================
echo "🔧 Step 1/3: Mesh Processing with TPS Surface Fitting"
echo "----------------------------------------"
start_time=$(date +%s)

if [ ! -f "${MESH_INPUT}" ]; then
    echo "❌ ERROR: Input mesh file not found: ${MESH_INPUT}"
    exit 1
fi

# Run mesh processing in container
echo "🚀 Starting mesh-to-surface conversion..."
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    cache/sfs_prep_from_working.sif \
    ./build/mesh_processing_complete "${POT_ID}" "${SLURM_ARRAY_TASK_ID}" > "${MESH_LOG}" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Mesh processing failed. Check log: ${MESH_LOG}"
    exit 1
fi

# Verify surface files were created
SURFACE_0="${SURFACE_OUTPUT_DIR}/Pot_${POT_ID}_Piece_${PIECE_ID}_Surface_0.xyz"
SURFACE_1="${SURFACE_OUTPUT_DIR}/Pot_${POT_ID}_Piece_${PIECE_ID}_Surface_1.xyz"

if [[ -f "${SURFACE_0}" && -f "${SURFACE_1}" ]]; then
    surface_0_points=$(wc -l < "${SURFACE_0}")
    surface_1_points=$(wc -l < "${SURFACE_1}")
    echo "✅ Mesh processing completed successfully"
    echo "📊 Generated surfaces: ${surface_0_points} + ${surface_1_points} points"
else
    echo "❌ ERROR: Surface files not generated"
    exit 1
fi

end_time=$(date +%s)
mesh_duration=$((end_time - start_time))
echo "⏱️ Mesh processing time: ${mesh_duration}s"
echo ""

# ===============================
# Step 2: Axis Extraction (MATLAB PotSAC)
# ===============================
echo "🔧 Step 2/3: Axis Extraction with PotSAC Algorithm"
echo "----------------------------------------"
start_time=$(date +%s)

echo "🚀 Starting axis extraction..."
./matlab_axis_wrapper.sh "${POT_ID}" "${SLURM_ARRAY_TASK_ID}" > "${AXIS_LOG}" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Axis extraction failed. Check log: ${AXIS_LOG}"
    exit 1
fi

# Verify axis file was created and copy to SFS location
# MATLAB wrapper creates .txt files, but SFS expects .xyz extension
AXIS_SOURCE_TXT="axis_output/Pot_${POT_ID}_Piece_${PIECE_ID}_Axis.txt"
AXIS_SOURCE_XYZ="axis_output/Pot_${POT_ID}_Piece_${PIECE_ID}_Axis.xyz"
AXIS_TARGET="${AXIS_OUTPUT_DIR}/Pot_${POT_ID}_Piece_${PIECE_ID}_Axis.xyz"

# Check for either .txt or .xyz file from MATLAB wrapper
if [ -f "${AXIS_SOURCE_XYZ}" ]; then
    AXIS_SOURCE="${AXIS_SOURCE_XYZ}"
elif [ -f "${AXIS_SOURCE_TXT}" ]; then
    AXIS_SOURCE="${AXIS_SOURCE_TXT}"
else
    echo "❌ ERROR: No axis file generated (.txt or .xyz)"
    ls -la axis_output/Pot_${POT_ID}_Piece_${PIECE_ID}_* 2>/dev/null || echo "No matching files found"
    exit 1
fi

# Copy axis file to SFS location with .xyz extension
cp "${AXIS_SOURCE}" "${AXIS_TARGET}"
echo "✅ Axis extraction completed successfully"
echo "📁 Source axis file: ${AXIS_SOURCE}"
echo "📁 Target axis file: ${AXIS_TARGET}"

# Show axis parameters
if [ -f "${AXIS_TARGET}" ]; then
    echo "📊 Axis parameters:"
    axis_data=$(cat "${AXIS_TARGET}")
    # Parse single-line format: direction[1-3] position[4-6] 
    direction=$(echo ${axis_data} | awk '{print $1, $2, $3}')
    position=$(echo ${axis_data} | awk '{print $4, $5, $6}')
    echo "   Direction: [${direction}]"
    echo "   Position:  [${position}]"
fi

end_time=$(date +%s)
axis_duration=$((end_time - start_time))
echo "⏱️ Axis extraction time: ${axis_duration}s"
echo ""

# ===============================
# Step 3: Breakline Extraction (EdgeLineExtraction)
# ===============================
echo "🔧 Step 3/3: Breakline Extraction"
echo "----------------------------------------"
start_time=$(date +%s)

echo "🚀 Starting breakline extraction..."

# Run EdgeLineExtraction in container
/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
    cache/sfs_prep_from_working.sif \
    ./build/edgeline_extraction "${POT_ID}" "${SLURM_ARRAY_TASK_ID}" > "${BREAKLINE_LOG}" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Breakline extraction failed. Check log: ${BREAKLINE_LOG}"
    exit 1
fi

# Verify and copy breakline files
TEMP_BREAKLINE="../Temp/Temp_edge/Pot_${POT_ID}/*CompleteBreaklines*"
if ls ${TEMP_BREAKLINE} 1> /dev/null 2>&1; then
    cp ${TEMP_BREAKLINE} "${BREAKLINE_OUTPUT_DIR}/"
    breakline_count=$(ls "${BREAKLINE_OUTPUT_DIR}"/Pot_${POT_ID}_Piece_${PIECE_ID}*CompleteBreaklines* 2>/dev/null | wc -l)
    echo "✅ Breakline extraction completed successfully"
    echo "📁 Breakline files: ${breakline_count} generated"
else
    echo "⚠️  Warning: No breakline files generated (normal for some pieces)"
fi

end_time=$(date +%s)
breakline_duration=$((end_time - start_time))
echo "⏱️ Breakline extraction time: ${breakline_duration}s"
echo ""

# ===============================
# Summary
# ===============================
total_end_time=$(date +%s)
total_duration=$((total_end_time - $(date -d "$(stat -c %y "${MESH_LOG}")" +%s)))

echo "==============================================="
echo "🎉 PREPROCESSING PIPELINE COMPLETED"
echo "==============================================="
echo "Pot ${POT_ID}, Piece ${PIECE_ID} processing summary:"
echo "📋 Mesh Processing: ${mesh_duration}s"
echo "📋 Axis Extraction: ${axis_duration}s" 
echo "📋 Breakline Extraction: ${breakline_duration}s"
echo "📋 Total Time: ${total_duration}s"
echo ""
echo "📁 Generated Files:"
echo "   - Surfaces: ${SURFACE_0}"
echo "   -           ${SURFACE_1}"
echo "   - Axis:     ${AXIS_TARGET}"
echo "   - Breaklines: ${BREAKLINE_OUTPUT_DIR}/Pot_${POT_ID}_Piece_${PIECE_ID}*"
echo ""
echo "✅ All outputs ready for SFS main assembly pipeline"
echo "Completed: $(date)"
echo "==============================================="

# Final verification
if [[ -f "${SURFACE_0}" && -f "${SURFACE_1}" && -f "${AXIS_TARGET}" ]]; then
    echo "🎯 SUCCESS: All required files generated"
    exit 0
else
    echo "❌ FAILURE: Missing required output files"
    exit 1
fi