#!/bin/bash
# cleanup_safe.sh - Safe cleanup of old logs and containers
# Removes ~15GB of old SLURM logs, container cache, and test datasets
# Does NOT touch: Dataset/, build_new/, source code, working containers, .git/

echo "=== SFS Preprocessing Directory Cleanup ==="
echo "Target: Delete old logs, containers, and test datasets"
echo ""
echo "This will delete:"
echo "  - Old SLURM error/output logs from August-October (~10GB)"
echo "  - Duplicate container files in cache/ (~6GB)"
echo "  - Old test datasets (~500MB)"
echo "  - Temporary point cloud files in root (~50MB)"
echo ""
echo "Will NOT delete:"
echo "  - Dataset/ (current validated dataset)"
echo "  - build_new/ (working executables)"
echo "  - Source code (*.cpp, *.m, *.h)"
echo "  - Working containers (pcl_191_nurbs.sif)"
echo "  - Documentation (*.md)"
echo "  - .git/ repository"
echo ""

# Safety check
read -p "Continue with cleanup? (type 'yes' to proceed): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Starting cleanup..."
echo ""

# Track deleted files
deleted_count=0
space_before=$(du -sb . 2>/dev/null | awk '{print $1}')

# Function to safely remove file/directory
safe_remove() {
    if [ -e "$1" ]; then
        rm -rf "$1"
        if [ $? -eq 0 ]; then
            echo "  ✓ Removed: $1"
            ((deleted_count++))
        else
            echo "  ✗ Failed to remove: $1"
        fi
    fi
}

echo "1. Removing giant error logs (9.6GB)..."
safe_remove nurbs_complete_pipeline_15077021.err
safe_remove nurbs_complete_pipeline_15077021.out
safe_remove fixed_nurbs_pipeline_15117386.err
safe_remove fixed_nurbs_pipeline_15117386.out
safe_remove nurbs_complete_pipeline_15100761.err
safe_remove nurbs_complete_pipeline_15100761.out
safe_remove nurbs_complete_pipeline_15100865.err
safe_remove nurbs_complete_pipeline_15100865.out
safe_remove nurbs_preprocessing_15076948.err
safe_remove nurbs_preprocessing_15076948.out
safe_remove nurbs_complete_pipeline_15100909.err
safe_remove nurbs_complete_pipeline_15100909.out

echo ""
echo "2. Removing old SLURM logs (~2GB)..."

# PCL build logs
for f in pcl191_build_*.err pcl191_build_*.out; do
    safe_remove "$f"
done

# CloudCompare logs
for f in cloudcompare_*.err cloudcompare_*.out; do
    safe_remove "$f"
done

# Old pipeline logs
safe_remove nurbs_pipeline_fixed_15211618.err
safe_remove nurbs_pipeline_fixed_15211618.out

# Edgeline logs
for f in nurbs_edgeline_*.err nurbs_edgeline_*.out; do
    safe_remove "$f"
done

# Tray logs
for f in nurbs_tray000_*.err nurbs_tray000_*.out; do
    safe_remove "$f"
done

for f in edgeline_tray*.err edgeline_tray*.out; do
    safe_remove "$f"
done

# Mesh headless logs
for f in mesh_headless_*.err mesh_headless_*.out; do
    safe_remove "$f"
done

# Edge headless logs
for f in edge_headless_*.err edge_headless_*.out; do
    safe_remove "$f"
done

for f in edgeline_headless_*.err edgeline_headless_*.out; do
    safe_remove "$f"
done

# Other old logs
safe_remove build_sfs_prep_14425009.err
safe_remove build_sfs_prep_14425009.out
safe_remove build_sfs_prep_14425014.err
safe_remove build_sfs_prep_14425014.out
safe_remove native_sfs_prep_14425016.err
safe_remove native_sfs_prep_14425016.out
safe_remove pcd_with_normals_15077919.err
safe_remove pcd_with_normals_15077919.out
safe_remove edgeline_extraction_14918846.err
safe_remove edgeline_extraction_14918846.out
safe_remove edgeline_extraction_15050343.err
safe_remove edgeline_extraction_15050343.out
safe_remove edgeline_extraction_15168870.err
safe_remove edgeline_extraction_15168870.out
safe_remove edgeline_extraction_15195559.err
safe_remove edgeline_extraction_15195559.out
safe_remove nurbs_complete_fixed_15233267.err
safe_remove nurbs_complete_fixed_15233267.out
safe_remove nurbs_complete_fixed_15233276.err
safe_remove nurbs_complete_fixed_15233276.out
safe_remove nurbs_complete_fixed_15297704.err
safe_remove nurbs_complete_fixed_15297704.out
safe_remove nurbs_complete_fixed_15298422.err
safe_remove nurbs_complete_fixed_15298422.out
safe_remove nurbs_complete_pipeline_15118149.err
safe_remove nurbs_complete_pipeline_15118149.out
safe_remove nurbs_complete_pipeline_17500867.err
safe_remove nurbs_complete_pipeline_17500867.out
safe_remove nurbs_complete_pipeline_17530061.err
safe_remove nurbs_complete_pipeline_17530061.out
safe_remove nurbs_coord_fix_17906180.err
safe_remove nurbs_coord_fix_17906180.out
safe_remove nurbs_coord_fix_18056648.err
safe_remove nurbs_coord_fix_18056648.out
safe_remove nurbs_param_fix_15429454.err
safe_remove nurbs_param_fix_15429454.out
safe_remove nurbs_preprocessing_15006076.err
safe_remove nurbs_preprocessing_15006076.out
safe_remove nurbs_regen_correct_17499648.err
safe_remove nurbs_regen_correct_17499648.out
safe_remove nurbs_regen_correct_17499674.err
safe_remove nurbs_regen_correct_17499674.out
safe_remove edgeline_working_now.err
safe_remove edgeline_working_now.out
safe_remove edgeline_headless_now.err
safe_remove edgeline_headless_now.out
safe_remove edgeline_nurbs_now.err
safe_remove edgeline_nurbs_now.out
safe_remove nurbs_edge_run.err
safe_remove nurbs_edge_run.out

# Old "from_objdir" logs
for f in nurbs_from_objdir_*.err nurbs_from_objdir_*.out; do
    safe_remove "$f"
done

echo ""
echo "3. Removing duplicate container files in cache/ (~6GB)..."
if [ -d "cache" ]; then
    echo "  Removing cache/ directory..."
    safe_remove cache/
else
    echo "  cache/ already removed or doesn't exist"
fi

echo ""
echo "4. Removing old test datasets (~500MB)..."
safe_remove Tray-000_Dataset_20251021/
safe_remove Tray-000_Dataset_20251021_METERS_BACKUP/
safe_remove TEST_CoordinateFix_20251104_164405/
safe_remove Test_Output_20251115/
safe_remove Test_Verification_20251115_212818/
safe_remove Test_Fix3_Verification/

echo ""
echo "5. Removing superseded NURBS datasets..."
safe_remove NURBS_Dataset_20250907_CompleteFixed/

echo ""
echo "6. Removing temporary point cloud files in root..."
safe_remove cloudForSpline.pcd
safe_remove fileForNormalEst_Sampled.xyz
safe_remove fileForNormalEst_SampledWithNormals.ply
safe_remove fileForNormalEst_SampledWithNormals.xyz
safe_remove segmentationStats.txt

# Remove duplicate surface files in root (if they exist)
for f in Pot_A_Piece_*_Surface_*; do
    if [ -f "$f" ]; then
        safe_remove "$f"
    fi
done

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Files/directories removed: $deleted_count"
echo ""

# Calculate space saved
space_after=$(du -sb . 2>/dev/null | awk '{print $1}')
space_saved=$((space_before - space_after))
space_saved_gb=$(echo "scale=2; $space_saved / 1024 / 1024 / 1024" | bc)

echo "Space before: $(echo "scale=2; $space_before / 1024 / 1024 / 1024" | bc) GB"
echo "Space after:  $(echo "scale=2; $space_after / 1024 / 1024 / 1024" | bc) GB"
echo "Space saved:  ${space_saved_gb} GB"
echo ""

# Verify critical files still exist
echo "=== Verification ==="
echo ""

verify_file() {
    if [ -e "$1" ]; then
        echo "  ✓ $1"
    else
        echo "  ✗ MISSING: $1"
    fi
}

echo "Critical files check:"
verify_file "build_new/EdgeLineExtractionHeadless"
verify_file "build_new/MeshPreprocessingHeadless"
verify_file "pcl_191_nurbs.sif"
verify_file "Dataset/Surfaces/Pot_A"
verify_file "Dataset/Breaklines/Pot_A"
verify_file "Dataset/Axes"
verify_file "DATASET_COMPARISON.md"
verify_file "COMPLETE_PIPELINE_VALIDATION.md"

echo ""
echo "Dataset file counts:"
echo "  Surfaces: $(find Dataset/Surfaces/Pot_A -name "*.xyz" 2>/dev/null | wc -l) (expected: 16)"
echo "  Breaklines: $(find Dataset/Breaklines/Pot_A -name "*.pcd" 2>/dev/null | wc -l) (expected: 16)"
echo "  Axes: $(find Dataset/Axes -name "*.xyz" 2>/dev/null | wc -l) (expected: 8)"

echo ""
echo "Cleanup completed successfully!"
echo "Review DIRECTORY_CLEANUP_PLAN.md for Priority 2 (temp_download/) if needed."
