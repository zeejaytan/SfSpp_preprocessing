# Directory Cleanup Plan

**Analysis Date**: November 16, 2025
**Total Disk Usage**: ~47GB
**Target Space Savings**: ~20-25GB (reducing to ~22-25GB total)

---

## Current Disk Usage Breakdown

| Category | Size | Status |
|----------|------|--------|
| .git/ | 18GB | **KEEP** - Git repository |
| temp_download/ | 7.0GB | **REVIEW** - Raw PCD files |
| cache/ | 6.0GB | **CLEANUP** - Old container SIF files |
| Error logs (*.err *.out) | ~10GB | **CLEANUP** - SLURM logs |
| Temp/ | 440MB | **KEEP** - Working temp files |
| archive_old_datasets/ | 349MB | **KEEP** - Archived data |
| Test datasets | 509MB | **CLEANUP** - Old test outputs |
| Old NURBS datasets | ~200MB | **CLEANUP** - Superseded versions |
| build_new/ | 35MB | **KEEP** - Working executables |
| Scripts (*.sbatch, *.sh) | ~5MB | **REVIEW** - 96 script files |

---

## PRIORITY 1: Safe to Delete Immediately (~15GB savings)

### A. Giant Error Logs (9.6GB)

**Files to delete**:
```bash
# Multi-gigabyte logs from September pipeline runs
rm -f nurbs_complete_pipeline_15077021.err          # 5.6GB
rm -f nurbs_complete_pipeline_15077021.out          # 1.5GB
rm -f fixed_nurbs_pipeline_15117386.err             # 2.4GB
rm -f fixed_nurbs_pipeline_15117386.out             # 631MB
rm -f nurbs_complete_pipeline_15100761.err          # 800MB
rm -f nurbs_complete_pipeline_15100761.out          # 207MB
rm -f nurbs_complete_pipeline_15100865.err          # 684MB
rm -f nurbs_complete_pipeline_15100865.out          # 177MB
rm -f nurbs_preprocessing_15076948.err              # 651MB
rm -f nurbs_preprocessing_15076948.out              # 169MB
rm -f nurbs_complete_pipeline_15100909.err          # 385MB
rm -f nurbs_complete_pipeline_15100909.out          # 100MB
```

**Justification**: These are debug logs from August-September when the pipeline had excessive logging issues (390× slowdown). All issues have been fixed in the current version. These logs are no longer needed for debugging.

**Space saved**: ~9.6GB

---

### B. Old SLURM Logs from August-October (~2GB)

**Pattern-based cleanup**:
```bash
# August-September PCL build logs (>200 files, mostly duplicates)
rm -f pcl191_build_*.{err,out}                      # ~2MB each × 50 = 100MB
rm -f cloudcompare_*.{err,out}                      # ~1-2GB total
rm -f nurbs_pipeline_fixed_15211618.{err,out}      # 75MB + 9.3MB
rm -f nurbs_edgeline_*.{err,out}                    # ~1GB total
rm -f nurbs_tray000_*.{err,out}                     # ~5MB total
rm -f edgeline_*.{err,out}                          # ~500KB total
rm -f mesh_headless_*.{err,out}                     # ~5MB total
```

**Justification**: All October/November runs completed successfully. Old failure logs from August-September are not needed.

**Space saved**: ~2GB

---

### C. Duplicate Container Files in cache/ (5GB)

**Current containers**:
```
cache/sfs_prep_conda_nurbs.sif        1.2GB
cache/sfs_prep_manual_nurbs.sif       862MB
cache/sfs_prep_with_nurbs.sif         862MB
cache/sfs_prep_focused_nurbs.sif      818MB
cache/sfs_prep_complete_nurbs.sif     818MB
cache/sfs_prep_fallback.sif           818MB
cache/sfs_prep_base.sif               809MB
```

**Working containers (KEEP)**:
```
pcl_191_nurbs.sif                     292MB  ← Current working container
sfs_preprocessing_true_nurbs.sif      860MB  ← Backup container
```

**Delete all cache/ containers**:
```bash
rm -rf cache/*.sif
```

**Justification**: All cache containers are superseded by `pcl_191_nurbs.sif` (the working container in root). Cache was for testing during August build phase.

**Space saved**: ~6GB

---

### D. Old Test Datasets (500MB)

**Directories to delete**:
```bash
rm -rf Tray-000_Dataset_20251021/                  # 320MB
rm -rf Tray-000_Dataset_20251021_METERS_BACKUP/    # 189MB
rm -rf TEST_CoordinateFix_20251104_164405/         # 114MB
rm -rf Test_Output_20251115/                       # Small
rm -rf Test_Verification_20251115_212818/          # Small
rm -rf Test_Fix3_Verification/                     # Small
```

**Justification**: These are test runs from October-November. Current validated dataset is in `Dataset/`. Test outputs are documented in validation markdown files.

**Space saved**: ~500MB

---

### E. Superseded NURBS Datasets (200MB)

**Directories to delete**:
```bash
rm -rf NURBS_Dataset_20250907_CompleteFixed/       # 26MB
# Keep NURBS_Dataset_20251103 as reference (99MB)
```

**Justification**: Old dataset versions before final fixes were applied. Current dataset is in `Dataset/`.

**Space saved**: ~26MB

---

## PRIORITY 2: Archive/Compress Candidates (~7GB potential savings)

### A. temp_download/ Raw PCD Files (7.0GB)

**Status**: Raw PCD files from initial dataset

**Options**:
1. **Compress** to tar.gz (expected: 7GB → ~2-3GB)
2. **Keep as-is** if actively used for regeneration
3. **Delete** if original source exists elsewhere

**Recommendation**: Check if raw PCD files exist in original dataset location (`/data/gpfs/projects/punim2657/Dataset/`). If yes, compress or delete. If no, keep as-is.

```bash
# If safe to compress:
tar -czf temp_download_backup.tar.gz temp_download/
rm -rf temp_download/
# Potential space saved: 4-5GB
```

---

## PRIORITY 3: Review and Organize

### A. Scripts Directory (96 scripts)

**Current status**: 96 .sbatch and .sh scripts in root directory

**Recommendation**: Organize into subdirectory:
```bash
mkdir -p archive_scripts
mv *.sbatch *.sh archive_scripts/
# Keep only actively used scripts in root:
mv archive_scripts/generate_complete_dataset_from_scratch.sbatch ./
mv archive_scripts/extract_all_nurbs_axes.m ./
```

**Space saved**: 0 (organizational only)

---

### B. Temporary Point Cloud Files in Root

**Files to clean**:
```bash
rm -f cloudForSpline.pcd
rm -f fileForNormalEst_*.{xyz,ply}
rm -f Pot_A_Piece_*_Surface_*     # Duplicates of Dataset/ files
rm -f Segments/*.xyz               # Old segment files
rm -f SegmentsRawPts/*.xyz         # Old raw points
```

**Space saved**: ~50MB

---

## PRIORITY 4: Keep (Critical Files)

### Must Keep:
- `Dataset/` - **Current validated dataset** (main output)
- `Complete_Dataset_Output/` - Latest complete run logs
- `build_new/` - Working executables (35MB)
- `NURBS_Dataset_20251103/` - Reference dataset (99MB)
- `archive_old_datasets/` - Historical archive (349MB)
- `Temp/` - Working temporary files (440MB)
- `.git/` - Git repository (18GB)
- Documentation files (*.md)
- Source code (*.cpp, *.m, *.h)
- Current working scripts
- Working containers: `pcl_191_nurbs.sif`, `sfs_preprocessing_true_nurbs.sif`

---

## Cleanup Script (Safe Execution)

Create executable cleanup script:

```bash
#!/bin/bash
# cleanup_safe.sh - Safe cleanup (Priority 1 only)

echo "=== SFS Preprocessing Directory Cleanup ==="
echo "Target: Delete old logs and containers"
echo ""

# Safety check
read -p "This will delete ~15GB of old logs. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "1. Removing giant error logs (9.6GB)..."
rm -f nurbs_complete_pipeline_15077021.{err,out}
rm -f fixed_nurbs_pipeline_15117386.{err,out}
rm -f nurbs_complete_pipeline_15100761.{err,out}
rm -f nurbs_complete_pipeline_15100865.{err,out}
rm -f nurbs_preprocessing_15076948.{err,out}
rm -f nurbs_complete_pipeline_15100909.{err,out}

echo "2. Removing old SLURM logs (2GB)..."
rm -f pcl191_build_*.{err,out}
rm -f cloudcompare_*.{err,out}
rm -f nurbs_pipeline_fixed_15211618.{err,out}
rm -f nurbs_edgeline_*.{err,out}
rm -f nurbs_tray000_1*.{err,out}
rm -f edgeline_tray*.{err,out}
rm -f mesh_headless_*.{err,out}
rm -f edge_headless_*.{err,out}
rm -f edgeline_headless_*.{err,out}

echo "3. Removing duplicate container files (6GB)..."
rm -rf cache/

echo "4. Removing old test datasets (500MB)..."
rm -rf Tray-000_Dataset_20251021/
rm -rf Tray-000_Dataset_20251021_METERS_BACKUP/
rm -rf TEST_CoordinateFix_20251104_164405/
rm -rf Test_Output_20251115/
rm -rf Test_Verification_20251115_212818/
rm -rf Test_Fix3_Verification/

echo "5. Removing superseded NURBS datasets (26MB)..."
rm -rf NURBS_Dataset_20250907_CompleteFixed/

echo "6. Removing temporary point cloud files in root..."
rm -f cloudForSpline.pcd
rm -f fileForNormalEst_*.{xyz,ply}
rm -f Pot_A_Piece_*_Surface_* 2>/dev/null
rm -f segmentationStats.txt

echo ""
echo "=== Cleanup Complete ==="
du -sh . 2>/dev/null
echo ""
echo "Estimated space saved: ~15GB"
echo "New directory size: ~30GB (down from ~47GB)"
echo ""
echo "Safe to delete files have been removed."
echo "Review Priority 2 (temp_download/) separately if needed."
```

---

## Execution Plan

### Step 1: Create cleanup script
```bash
nano cleanup_safe.sh
chmod +x cleanup_safe.sh
```

### Step 2: Execute Priority 1 cleanup
```bash
./cleanup_safe.sh
```

### Step 3: Verify results
```bash
du -sh /data/gpfs/projects/punim2657/sfs_preprocessing
```

### Step 4: (Optional) Archive temp_download/
```bash
# Only if raw PCD files exist elsewhere
tar -czf temp_download_backup.tar.gz temp_download/
rm -rf temp_download/
```

---

## Expected Results

| Phase | Before | After | Saved |
|-------|--------|-------|-------|
| Priority 1 Cleanup | 47GB | ~30GB | ~17GB |
| Priority 2 Archive (optional) | 30GB | ~25GB | ~5GB |
| **Total Potential** | **47GB** | **~25GB** | **~22GB** |

---

## Safety Notes

1. **Git repository (.git/)**: Never touched (18GB preserved)
2. **Current dataset (Dataset/)**: Never touched (main output)
3. **Working executables (build_new/)**: Never touched
4. **Documentation**: All .md files preserved
5. **Source code**: All .cpp, .m, .h files preserved
6. **Working containers**: pcl_191_nurbs.sif kept in root

---

## Post-Cleanup Validation

After cleanup, verify critical files still exist:
```bash
# Check working executables
ls -lh build_new/EdgeLineExtractionHeadless
ls -lh build_new/MeshPreprocessingHeadless

# Check current dataset
ls -lh Dataset/Surfaces/Pot_A/*.xyz | wc -l      # Should be 16
ls -lh Dataset/Breaklines/Pot_A/*.pcd | wc -l    # Should be 16
ls -lh Dataset/Axes/*.xyz | wc -l                 # Should be 8

# Check working container
ls -lh pcl_191_nurbs.sif

# Check documentation
ls -lh *.md
```

All should be present. If any missing, restoration needed from git.

---

**Cleanup Plan Status**: READY FOR EXECUTION
**Risk Level**: LOW (only deleting logs and old test files)
**Recommended Action**: Execute Priority 1 cleanup script immediately

---

**Plan Created**: November 16, 2025
