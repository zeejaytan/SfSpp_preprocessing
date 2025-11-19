#!/bin/bash
#SBATCH --job-name=pot_a_5x_pipeline
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=cascade

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "=========================================="
echo "COMPLETE PIPELINE: Pot A with 5× Sphere Radius"
echo "Modified for sample-like breakline variation"
echo "=========================================="
echo "Started: $(date)"
echo ""

# Load modules
module load GCCcore/11.3.0
module load CMake
module load Apptainer
module load MATLAB/2023a

# Clean output directories
echo "Cleaning breakline and axis directories..."
rm -rf Dataset/Breaklines/Pot_A/* 2>/dev/null
rm -rf axis_output/Pot_A_Piece_*_Axis.txt 2>/dev/null
mkdir -p Dataset/Breaklines/Pot_A
mkdir -p axis_output

echo ""
echo "========== STAGE 1: BREAKLINE EXTRACTION =========="
echo "Using 5.0× sphere radius (no max clamp, densification disabled)"
echo "Started: $(date)"
echo ""

# Run breakline extraction
timeout 3600 apptainer exec --bind /data:/data \
  /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
  ./build_new/EdgeLineExtractionHeadless 2>&1 | tee edge_extraction_5x_complete.log

echo ""
echo "Breakline Extraction Completed: $(date)"
echo ""

# Analyze breakline results
echo "========== Breakline Point Counts =========="
echo ""

for i in 01 02 03 04 05 06 07 08; do
  echo "Piece_${i}:"
  for b in 0 1; do
    file="Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_${b}.pcd"
    if [ -f "$file" ]; then
      pts=$(grep "^POINTS " "$file" | awk '{print $2}')
      segs=$(head -3 "$file" | tail -1 | awk '{print $2}')
      echo "  Breakline_${b}: $pts points, $segs segments"
    else
      echo "  Breakline_${b}: NOT FOUND"
    fi
  done
  echo ""
done

# Calculate statistics
total=0
count=0
min=999999
max=0

for file in Dataset/Breaklines/Pot_A/*.pcd; do
  if [ -f "$file" ]; then
    pts=$(grep "^POINTS " "$file" | awk '{print $2}')
    total=$((total + pts))
    count=$((count + 1))
    if [ $pts -lt $min ]; then min=$pts; fi
    if [ $pts -gt $max ]; then max=$pts; fi
  fi
done

if [ $count -gt 0 ]; then
  avg=$((total / count))
  echo "========== Breakline Statistics =========="
  echo "Total breaklines: $count (expected 16)"
  echo "Total points: $total"
  echo "Average: $avg points per breakline"
  echo "Range: $min - $max points"
  echo ""
  echo "Comparison to Sample:"
  echo "  Sample: avg 110 pts, range 30-194"
  echo "  New 5×: avg $avg pts, range $min-$max"
  echo ""
fi

echo ""
echo "========== STAGE 2: AXIS EXTRACTION =========="
echo "Running MATLAB PotSAC axis extraction on new breaklines"
echo "Started: $(date)"
echo ""

# Run axis extraction for each piece
for piece_num in 01 02 03 04 05 06 07 08; do
  echo "Processing Piece ${piece_num}..."

  # Create MATLAB script for this piece
  cat > run_axis_piece_${piece_num}.m <<EOF
addpath('AxisExtraction');
addpath('AxisExtraction/utils');

piece_id = ${piece_num};
pot_id = 'A';

try
    fprintf('Extracting axis for Pot_%s_Piece_%02d\n', pot_id, piece_id);
    extract_axis(pot_id, piece_id);
    fprintf('Successfully completed Piece %02d\n', piece_id);
catch ME
    fprintf('Error in Piece %02d: %s\n', piece_id, ME.message);
    exit(1);
end
exit(0);
EOF

  # Run MATLAB
  matlab -batch "run_axis_piece_${piece_num}" > matlab_axis_pot_a_piece_${piece_num}.log 2>&1

  if [ -f "axis_output/Pot_A_Piece_${piece_num}_Axis.txt" ]; then
    echo "  ✓ Axis file generated"
  else
    echo "  ✗ Axis file NOT generated - check logs"
  fi
done

echo ""
echo "Axis Extraction Completed: $(date)"
echo ""

echo "========== Axis Output Files =========="
ls -lh axis_output/Pot_A_Piece_*_Axis.txt 2>/dev/null || echo "No axis files found"
echo ""

echo ""
echo "========== FINAL DATASET SUMMARY =========="
echo ""

surfaces=$(ls -1 Dataset/Surfaces/Pot_A/*.xyz 2>/dev/null | wc -l)
breaklines=$(ls -1 Dataset/Breaklines/Pot_A/*.pcd 2>/dev/null | wc -l)
axes=$(ls -1 axis_output/Pot_A_Piece_*_Axis.txt 2>/dev/null | wc -l)

echo "Surfaces:   $surfaces / 16 expected"
echo "Breaklines: $breaklines / 16 expected"
echo "Axes:       $axes / 8 expected"
echo ""

if [ $breaklines -eq 16 ] && [ $axes -eq 8 ]; then
  echo "✓ ALL COMPONENTS GENERATED SUCCESSFULLY"
else
  echo "✗ INCOMPLETE - Check logs for errors"
fi

echo ""
echo "Pipeline completed: $(date)"
echo "=========================================="
