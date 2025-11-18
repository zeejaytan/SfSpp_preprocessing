# Dataset Validation Report: 19K Optimized vs Sample Dataset

**Generated**: 2025-11-19
**Report Date**: Complete dataset validation after 19K downsampling optimization

---

## CRITICAL FINDINGS SUMMARY

### ✅ COMPLETED
- Surface generation: **16 files** (Pot_A_Piece_01-08, each with _Surface_0 and _Surface_1)
- Breakline extraction: **16 files** (Pot_A_Piece_01-08, each with _Breakline_0 and _Breakline_1)
- Surface_F files: **8 files** (intermediate feature point files generated during processing)

### ❌ NOT COMPLETED
- Axis extraction: **0 files** (executable not available in container; requires Eigen library)

---

## 1. SURFACE_F FILE ANALYSIS

### Finding: Surface_F Files Generated Successfully

**New Dataset Surface_F Files:**
```
Dataset/Surfaces/Pot_A/
├── Pot_A_Piece_01_Surface_F.pcd (6 points)
├── Pot_A_Piece_02_Surface_F.pcd (14 points)
├── Pot_A_Piece_03_Surface_F.pcd (18 points)
├── Pot_A_Piece_04_Surface_F.pcd (10 points)
├── Pot_A_Piece_05_Surface_F.pcd (20 points)
├── Pot_A_Piece_06_Surface_F.pcd (25 points)
├── Pot_A_Piece_07_Surface_F.pcd (26 points)
└── Pot_A_Piece_08_Surface_F.pcd (14 points)
```

**Sample Dataset Surface_F Files:**
```
NURBS_Dataset_20251103/SfS_pp/Surfaces/
→ NO Surface_F files present in sample dataset
```

**Analysis**: Surface_F files are **intermediate feature point files** (x, y, z, normal_x, normal_y, normal_z, curvature) generated during preprocessing for surface analysis. They are NOT part of the final dataset output - the sample dataset doesn't include them. The new dataset correctly generates these intermediate files during processing.

---

## 2. BREAKLINE SEGMENTATION ANALYSIS

### Critical Difference: 3.3× Denser Breaklines in New Dataset

**Sample Dataset Breaklines (1,760 total points):**

| File | Points | Density |
|------|--------|---------|
| Pot_A_Piece_01_Breakline_0 | 59 | Low |
| Pot_A_Piece_01_Breakline_1 | 150 | Medium |
| Pot_A_Piece_02_Breakline_0 | 162 | Medium |
| Pot_A_Piece_02_Breakline_1 | 99 | Low |
| Pot_A_Piece_03_Breakline_0 | 130 | Low |
| Pot_A_Piece_03_Breakline_1 | 175 | Medium |
| Pot_A_Piece_04_Breakline_0 | 116 | Low |
| Pot_A_Piece_04_Breakline_1 | 194 | Medium |
| Pot_A_Piece_05_Breakline_0 | 140 | Low |
| Pot_A_Piece_05_Breakline_1 | 43 | **Very Low** |
| Pot_A_Piece_06_Breakline_0 | 30 | **Very Low** |
| Pot_A_Piece_06_Breakline_1 | 95 | Low |
| Pot_A_Piece_07_Breakline_0 | 132 | Low |
| Pot_A_Piece_07_Breakline_1 | 111 | Low |
| Pot_A_Piece_08_Breakline_0 | 30 | **Very Low** |
| Pot_A_Piece_08_Breakline_1 | 94 | Low |
| **Average** | **110 points** | **Sparse** |

**New Dataset Breaklines (5,860 total points):**

| File | Points | Density |
|------|--------|---------|
| Pot_A_Piece_01_Breakline_0 | 360 | Dense |
| Pot_A_Piece_01_Breakline_1 | 351 | Dense |
| Pot_A_Piece_02_Breakline_0 | 411 | **Very Dense** |
| Pot_A_Piece_02_Breakline_1 | 291 | Dense |
| Pot_A_Piece_03_Breakline_0 | 365 | Dense |
| Pot_A_Piece_03_Breakline_1 | 347 | Dense |
| Pot_A_Piece_04_Breakline_0 | 409 | **Very Dense** |
| Pot_A_Piece_04_Breakline_1 | 342 | Dense |
| Pot_A_Piece_05_Breakline_0 | 374 | Dense |
| Pot_A_Piece_05_Breakline_1 | 377 | Dense |
| Pot_A_Piece_06_Breakline_0 | 452 | **Very Dense** |
| Pot_A_Piece_06_Breakline_1 | 381 | Dense |
| Pot_A_Piece_07_Breakline_0 | 334 | Dense |
| Pot_A_Piece_07_Breakline_1 | 367 | Dense |
| Pot_A_Piece_08_Breakline_0 | 363 | Dense |
| Pot_A_Piece_08_Breakline_1 | 336 | Dense |
| **Average** | **366 points** | **Very Dense** |

### Key Statistics:

| Metric | Sample | New Dataset | Difference |
|--------|--------|-------------|-----------|
| **Total Points** | 1,760 | 5,860 | +4,100 (+232%) |
| **Average per Breakline** | 110 | 366 | +256 (+232%) |
| **Minimum** | 30 | 291 | +261 (+870%) |
| **Maximum** | 194 | 452 | +258 (+133%) |
| **File Count** | 16 ✓ | 16 ✓ | Match |
| **Consistency** | Highly variable (30-194) | Highly consistent (291-452) | New is uniform |

### Analysis:

**Root Cause**: The new dataset's breakline density is directly tied to the surface point density:
- **Sample surfaces**: ~5,845 pts average → **110 pts** average breaklines (1.9% point ratio)
- **New surfaces**: ~15,962 pts average → **366 pts** average breaklines (2.3% point ratio)

The breakline extraction algorithm (`EdgeLineExtractionHeadless`) adaptively segments boundary edges based on surface density. Denser surfaces produce denser breaklines.

**Quality Assessment**:
- ✓ File structure matches (16 breakline pairs)
- ✓ Point distribution is consistent (291-452 range vs 30-194 range)
- ✗ **Breaklines are 3.3× denser than sample** - may not match expected SFS assembly parameters
- ⚠ Denser breaklines provide better edge definition but may require algorithm tuning

---

## 3. AXIS EXTRACTION INVESTIGATION

### Status: INCOMPLETE - No Executable Available

**Why Axis Extraction Failed:**

1. **Missing Executable**: The SLURM script tried to call `./build_new/MATLAB2Headless` which doesn't exist
2. **Source Code Exists**: `axis_extraction_cpp.cpp` is present but was **never added to CMakeLists.txt**
3. **Build Attempt Failed**: Added `AxisExtractionHeadless` to build system but compilation fails due to:
   - **Missing Eigen Library**: The container doesn't include Eigen headers
   - `axis_extraction_cpp.cpp:11` → `#include <Eigen/Dense>` → **File not found**

**What Should Be Generated:**

Sample dataset has 8 axis files:
```
Axes/Pot_A/
├── Pot_A_Piece_01_NURBS_Axis.xyz (60 bytes, 2 points)
├── Pot_A_Piece_02_NURBS_Axis.xyz (60 bytes, 2 points)
├── Pot_A_Piece_03_NURBS_Axis.xyz (120 bytes, 4 points)
├── Pot_A_Piece_04_NURBS_Axis.xyz (60 bytes, 2 points)
├── Pot_A_Piece_05_NURBS_Axis.xyz (61 bytes, 2 points)
├── Pot_A_Piece_06_NURBS_Axis.xyz (60 bytes, 2 points)
├── Pot_A_Piece_07_NURBS_Axis.xyz (58 bytes, 2 points)
└── Pot_A_Piece_08_NURBS_Axis.xyz (126 bytes, 4 points)
```

Each file contains principal axes computed via PotSAC (Rotation Optimal Symmetry Axis Computation).

**Options for Axis Extraction:**

1. **Install Eigen in container** (requires container rebuild)
2. **Create simplified axis extraction** using surface center of mass + normal direction
3. **Mark axis extraction as optional** for SFS assembly (current preprocessing works without it)
4. **Use MATLAB externally** (requires MATLAB installation on HPC system)

---

## OVERALL DATASET COMPARISON

### File Inventory:

| Component | Sample | New 19K | Match? |
|-----------|--------|---------|--------|
| **Surfaces** | 16 files | 16 files | ✓ Yes |
| **Breaklines** | 16 files | 16 files | ✓ Yes |
| **Axes** | 8 files | 0 files | ✗ No |
| **Surface_F** | 0 files | 8 files | N/A (intermediate) |

### Data Density:

| Metric | Sample | New 19K | Change |
|--------|--------|---------|--------|
| **Surface Points (avg)** | 5,845 | 15,962 | **+2.73×** |
| **Breakline Points (avg)** | 110 | 366 | **+3.32×** |
| **Total Points** | 93,520 | 255,392 | **+2.73×** |

---

## CONCLUSIONS

### ✅ What Works
1. Surface generation with 19K target successfully produces consistent, high-density point clouds
2. File structure perfectly matches sample dataset (16 pieces × 2 surfaces/piece)
3. Breakline extraction runs successfully and generates proper PCD files
4. Surface_F feature files are generated (not part of final output but useful for diagnostics)
5. Directory structure is compatible with SFS assembly pipeline

### ⚠️ What Requires Attention
1. **Density Mismatch**: New surfaces are 2.73× denser than sample
   - New average: 15,962 pts/surface
   - Sample average: 5,845 pts/surface
   - This scales all downstream processing by 3×

2. **Breakline Density**: 3.32× more points per breakline
   - New average: 366 pts
   - Sample average: 110 pts
   - Provides better edge definition but may need algorithm retuning

3. **Missing Axis Files**: No axis extraction available
   - Required for complete SFS assembly
   - Requires external dependencies (Eigen) not in container
   - Could be implemented with simplified method

### Recommendation
The 19K downsampling target successfully matches the sample dataset's surface geometry and file count. The **key decision point** is whether the 2.73× density increase is acceptable for your SFS assembly algorithm, or whether the target should be reduced to achieve closer density matching (e.g., 7K or 8K target).

---

## Next Steps

1. **Confirm Density**: Is 2.73× denser surface data acceptable for SFS assembly?
   - If YES: Proceed with 19K dataset
   - If NO: Retry with lower target (7K-8K range) to match sample density

2. **Axis Extraction**: Decide on approach:
   - Skip (if not required for assembly)
   - Implement simplified version
   - Install Eigen in container and rebuild

3. **Validate Assembly**: Run SFS assembly pipeline on new dataset and compare results

