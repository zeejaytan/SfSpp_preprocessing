#!/bin/bash
#
# Cleanup Preprocessing Directory - Remove TPS files and redundant scripts
# Created: 2025-11-03
# Purpose: Archive incorrect TPS-modified code and redundant scripts
#

set -e

PREPROCESSING_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
ARCHIVE_DIR="$PREPROCESSING_DIR/archive_incorrect_tps_$(date +%Y%m%d)"
CLEANUP_LOG="$PREPROCESSING_DIR/cleanup_log_$(date +%Y%m%d_%H%M%S).txt"

echo "========================================================================="
echo "     Preprocessing Directory Cleanup - Archive TPS and Redundant Files"
echo "========================================================================="
echo "Started: $(date)" | tee -a "$CLEANUP_LOG"
echo ""

cd "$PREPROCESSING_DIR"

# Create archive directory
echo "Creating archive directory: $ARCHIVE_DIR" | tee -a "$CLEANUP_LOG"
mkdir -p "$ARCHIVE_DIR"/{incorrect_code,redundant_scripts,tps_files,old_datasets}

echo "" | tee -a "$CLEANUP_LOG"
echo "=== Phase 1: Archive Incorrect TPS-Modified Code ===" | tee -a "$CLEANUP_LOG"

# Archive incorrect mesh_processing_complete.cpp (contains TPS normals)
if [ -f "mesh_processing_complete.cpp" ]; then
    echo "Archiving: mesh_processing_complete.cpp (INCORRECT - uses TPS normals)" | tee -a "$CLEANUP_LOG"
    mv mesh_processing_complete.cpp "$ARCHIVE_DIR/incorrect_code/"
    echo "  → Reason: Uses TPS computeSurfaceNormal() instead of NURBS fit.m_nurbs.EvNormal()" | tee -a "$CLEANUP_LOG"
fi

# Archive TPS backup file
if [ -f "edgeline_extraction.cpp.backup_with_tps" ]; then
    echo "Archiving: edgeline_extraction.cpp.backup_with_tps" | tee -a "$CLEANUP_LOG"
    mv edgeline_extraction.cpp.backup_with_tps "$ARCHIVE_DIR/tps_files/"
fi

# Archive TPS output directory (if it doesn't contain important files)
if [ -d "TPS_Output" ]; then
    FILE_COUNT=$(find TPS_Output -type f | wc -l)
    echo "Checking TPS_Output directory: $FILE_COUNT files" | tee -a "$CLEANUP_LOG"

    if [ "$FILE_COUNT" -lt 10 ]; then
        echo "Archiving: TPS_Output/ directory" | tee -a "$CLEANUP_LOG"
        mv TPS_Output "$ARCHIVE_DIR/tps_files/"
    else
        echo "WARNING: TPS_Output has $FILE_COUNT files - manual review recommended" | tee -a "$CLEANUP_LOG"
    fi
fi

echo "" | tee -a "$CLEANUP_LOG"
echo "=== Phase 2: Archive Redundant/Old Scripts ===" | tee -a "$CLEANUP_LOG"

# Keep only essential scripts, archive the rest
ESSENTIAL_SCRIPTS=(
    "run_nurbs_preprocessing.sbatch"
    "regenerate_nurbs_correct.sbatch"
    "build_pcl191_container.sbatch"
)

echo "Keeping essential scripts:" | tee -a "$CLEANUP_LOG"
for script in "${ESSENTIAL_SCRIPTS[@]}"; do
    echo "  ✓ $script" | tee -a "$CLEANUP_LOG"
done
echo "" | tee -a "$CLEANUP_LOG"

echo "Archiving redundant sbatch scripts..." | tee -a "$CLEANUP_LOG"
ARCHIVED_COUNT=0

for script in *.sbatch; do
    # Skip if in essential list
    KEEP=0
    for essential in "${ESSENTIAL_SCRIPTS[@]}"; do
        if [ "$script" == "$essential" ]; then
            KEEP=1
            break
        fi
    done

    if [ $KEEP -eq 0 ]; then
        echo "  Archiving: $script" | tee -a "$CLEANUP_LOG"
        mv "$script" "$ARCHIVE_DIR/redundant_scripts/"
        ((ARCHIVED_COUNT++))
    fi
done

echo "  Total archived: $ARCHIVED_COUNT sbatch scripts" | tee -a "$CLEANUP_LOG"

echo "" | tee -a "$CLEANUP_LOG"
echo "=== Phase 3: Archive Old/Failed NURBS Datasets ===" | tee -a "$CLEANUP_LOG"

# Archive old failed NURBS datasets (keep only the latest and the one being generated)
echo "Checking for old NURBS datasets to archive..." | tee -a "$CLEANUP_LOG"

# List all NURBS datasets
NURBS_DATASETS=$(ls -d NURBS_Dataset_* 2>/dev/null | sort -r)

if [ -n "$NURBS_DATASETS" ]; then
    DATASET_COUNT=$(echo "$NURBS_DATASETS" | wc -l)
    echo "Found $DATASET_COUNT NURBS datasets" | tee -a "$CLEANUP_LOG"

    # Keep the 2 most recent, archive the rest
    echo "$NURBS_DATASETS" | tail -n +3 | while read dataset; do
        echo "  Archiving old dataset: $dataset" | tee -a "$CLEANUP_LOG"
        # Note the creation date
        DATE=$(stat -c %y "$dataset" | cut -d' ' -f1)
        echo "    Created: $DATE" | tee -a "$CLEANUP_LOG"
        # Don't actually move yet - user may want to review
        echo "    → Would move to archive (DRY RUN)" | tee -a "$CLEANUP_LOG"
    done
else
    echo "  No NURBS datasets found to archive" | tee -a "$CLEANUP_LOG"
fi

echo "" | tee -a "$CLEANUP_LOG"
echo "=== Phase 4: Clean Up Build Artifacts ===" | tee -a "$CLEANUP_LOG"

# List but don't delete build artifacts (user may need them)
echo "Build artifacts found:" | tee -a "$CLEANUP_LOG"
if [ -d "build" ]; then
    BUILD_SIZE=$(du -sh build 2>/dev/null | awk '{print $1}')
    echo "  build/ directory: $BUILD_SIZE" | tee -a "$CLEANUP_LOG"
fi

if [ -d "build_edgeline" ]; then
    BUILD_SIZE=$(du -sh build_edgeline 2>/dev/null | awk '{print $1}')
    echo "  build_edgeline/ directory: $BUILD_SIZE" | tee -a "$CLEANUP_LOG"
fi

if [ -d "build_simple" ]; then
    BUILD_SIZE=$(du -sh build_simple 2>/dev/null | awk '{print $1}')
    echo "  build_simple/ directory: $BUILD_SIZE" | tee -a "$CLEANUP_LOG"
fi

echo "  Note: Build artifacts NOT removed - may still be needed" | tee -a "$CLEANUP_LOG"

echo "" | tee -a "$CLEANUP_LOG"
echo "=== Phase 5: Archive Temporary/Log Files ===" | tee -a "$CLEANUP_LOG"

# Count log files
LOG_COUNT=$(ls *.log 2>/dev/null | wc -l)
OUT_COUNT=$(ls *.out 2>/dev/null | wc -l)
ERR_COUNT=$(ls *.err 2>/dev/null | wc -l)

echo "Temporary files found:" | tee -a "$CLEANUP_LOG"
echo "  .log files: $LOG_COUNT" | tee -a "$CLEANUP_LOG"
echo "  .out files: $OUT_COUNT" | tee -a "$CLEANUP_LOG"
echo "  .err files: $ERR_COUNT" | tee -a "$CLEANUP_LOG"

# Archive old log files (> 30 days)
echo "" | tee -a "$CLEANUP_LOG"
echo "Archiving log files older than 30 days..." | tee -a "$CLEANUP_LOG"
OLD_LOGS=$(find . -maxdepth 1 -name "*.log" -o -name "*.out" -o -name "*.err" -mtime +30 2>/dev/null)

if [ -n "$OLD_LOGS" ]; then
    OLD_COUNT=$(echo "$OLD_LOGS" | wc -l)
    echo "  Found $OLD_COUNT old log files" | tee -a "$CLEANUP_LOG"
    echo "$OLD_LOGS" | while read logfile; do
        echo "  Moving: $logfile" >> "$CLEANUP_LOG"
        mv "$logfile" "$ARCHIVE_DIR/redundant_scripts/"
    done
else
    echo "  No old log files found" | tee -a "$CLEANUP_LOG"
fi

echo "" | tee -a "$CLEANUP_LOG"
echo "========================================================================="
echo "                         CLEANUP SUMMARY"
echo "========================================================================="
echo "" | tee -a "$CLEANUP_LOG"

# Generate summary
echo "Archive Location: $ARCHIVE_DIR" | tee -a "$CLEANUP_LOG"
echo "" | tee -a "$CLEANUP_LOG"

echo "Files Archived:" | tee -a "$CLEANUP_LOG"
echo "  Incorrect code:" | tee -a "$CLEANUP_LOG"
INCORRECT_COUNT=$(find "$ARCHIVE_DIR/incorrect_code" -type f 2>/dev/null | wc -l)
echo "    $INCORRECT_COUNT files" | tee -a "$CLEANUP_LOG"

echo "  TPS-related files:" | tee -a "$CLEANUP_LOG"
TPS_COUNT=$(find "$ARCHIVE_DIR/tps_files" -type f 2>/dev/null | wc -l)
echo "    $TPS_COUNT files" | tee -a "$CLEANUP_LOG"

echo "  Redundant scripts:" | tee -a "$CLEANUP_LOG"
SCRIPT_COUNT=$(find "$ARCHIVE_DIR/redundant_scripts" -type f 2>/dev/null | wc -l)
echo "    $SCRIPT_COUNT files" | tee -a "$CLEANUP_LOG"

echo "" | tee -a "$CLEANUP_LOG"
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | awk '{print $1}')
echo "Total Archive Size: $ARCHIVE_SIZE" | tee -a "$CLEANUP_LOG"
echo "" | tee -a "$CLEANUP_LOG"

echo "Essential Scripts Kept:" | tee -a "$CLEANUP_LOG"
for script in "${ESSENTIAL_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "  ✓ $script" | tee -a "$CLEANUP_LOG"
    else
        echo "  ✗ $script (NOT FOUND)" | tee -a "$CLEANUP_LOG"
    fi
done

echo "" | tee -a "$CLEANUP_LOG"
echo "Correct NURBS Preprocessing Files (KEPT):" | tee -a "$CLEANUP_LOG"
echo "  ✓ original_nurbs_preprocessing/mesh_processing_headless.cpp" | tee -a "$CLEANUP_LOG"
echo "  ✓ original_nurbs_preprocessing/build/MeshPreprocessingHeadless" | tee -a "$CLEANUP_LOG"
echo "  ✓ original_nurbs_preprocessing/build/EdgeLineExtractionHeadless" | tee -a "$CLEANUP_LOG"
echo "  ✓ pcl_191_nurbs.sif (container)" | tee -a "$CLEANUP_LOG"

echo "" | tee -a "$CLEANUP_LOG"
echo "========================================================================="
echo "Cleanup completed: $(date)" | tee -a "$CLEANUP_LOG"
echo "Cleanup log: $CLEANUP_LOG"
echo "========================================================================="
echo ""
echo "IMPORTANT: Review archived files before deleting:"
echo "  cd $ARCHIVE_DIR"
echo "  ls -R"
echo ""
echo "To permanently delete archived files (after review):"
echo "  rm -rf $ARCHIVE_DIR"
echo ""
