# Preprocessing Directory Cleanup Summary

## Date: 2025-11-03

## Files Archived

### Incorrect Code (TPS-Modified)
**Location**: `archive_incorrect_tps_20251103/incorrect_code/`

1. **mesh_processing_complete.cpp** (88KB)
   - **Problem**: Uses TPS `computeSurfaceNormal()` instead of NURBS `fit.m_nurbs.EvNormal()`
   - **Impact**: Generated incorrect normals causing 14x more rejections and 0% assembly success
   - **Status**: ❌ MUST NOT USE

### TPS-Related Files
**Location**: `archive_incorrect_tps_20251103/tps_files/`

1. **edgeline_extraction.cpp.backup_with_tps**
2. **TPS_Output/** directory (empty)

### Redundant Scripts
**Location**: `archive_incorrect_tps_20251103/redundant_scripts/`

- Multiple old/redundant `.sbatch` scripts (36 → keep only 3 essential)

## Essential Files Kept

### Correct NURBS Preprocessing Code
✅ **original_nurbs_preprocessing/mesh_processing_headless.cpp**
   - Uses proper NURBS normal computation: `fit.m_nurbs.EvNormal()`
   - Built: Oct 24, 2025
   - Status: CORRECT - USE THIS

✅ **original_nurbs_preprocessing/build/MeshPreprocessingHeadless**
   - Executable (5.5 MB)
   - Contains correct NURBS processing

✅ **original_nurbs_preprocessing/build/EdgeLineExtractionHeadless**
   - Breakline extraction executable

### Essential Scripts Kept
1. **run_nurbs_preprocessing.sbatch** - Main NURBS pipeline
2. **regenerate_nurbs_correct.sbatch** - Regeneration script  
3. **build_pcl191_container.sbatch** - Container build script

### Container
✅ **pcl_191_nurbs.sif** (292 MB)
   - PCL 1.9.1 with NURBS support

## Cleanup Actions

1. ✅ Archived incorrect TPS-modified code
2. ✅ Archived TPS-related files
3. ⚠️  Partial archiving of redundant scripts (stopped due to error)
4. ✅ Kept all correct/essential files

## What Was NOT Removed

- Build directories (`build/`, `build_simple/`, etc.) - may still be needed
- Recent log files (< 30 days)
- NURBS datasets (for manual review)
- Original GitHub code comparison in `/tmp/SfSpp_preprocessing/`

## Archive Location

**Main Archive**: `/data/gpfs/projects/punim2657/sfs_preprocessing/archive_incorrect_tps_20251103/`

**Size**: ~90KB (mostly the incorrect code file)

## Recommendations

1. **Verify Archive**: Review archived files before permanent deletion
   ```bash
   cd /data/gpfs/projects/punim2657/sfs_preprocessing/archive_incorrect_tps_20251103
   ls -R
   ```

2. **Complete Redundant Script Cleanup**: Manually review and archive remaining 35 `.sbatch` scripts
   - Keep only: `run_nurbs_preprocessing.sbatch`, `regenerate_nurbs_correct.sbatch`, `build_pcl191_container.sbatch`

3. **Remove Old NURBS Datasets**: After confirming new dataset works, remove old failed datasets
   - Keep latest 2 datasets only
   - Archive/delete: `NURBS_Dataset_20250905_*`, `NURBS_Dataset_20250906_*`, etc.

4. **Clean Build Artifacts**: After confirming everything works
   - May remove `build/`, `build_simple/`, `build_edgeline/`
   - Keep only `original_nurbs_preprocessing/build/`

5. **Permanent Deletion** (after review):
   ```bash
   rm -rf /data/gpfs/projects/punim2657/sfs_preprocessing/archive_incorrect_tps_20251103
   ```

## Key Takeaway

✅ **Incorrect TPS-modified code archived and removed from active use**

✅ **Correct NURBS preprocessing files identified and preserved**

✅ **Essential scripts kept, redundant scripts being archived**

The preprocessing directory is now cleaner and focuses on the correct NURBS implementation.
