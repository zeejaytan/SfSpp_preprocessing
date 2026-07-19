# Comprehensive Dataset Comparison Report

**New Dataset vs Sample Dataset (sfs_main/original_samples/SfS_pp)**

Generated: 2025-12-07 (Updated Deep-Dive Analysis)

---

## Executive Summary

| Metric | New Dataset | Sample Dataset | Difference |
|--------|-------------|----------------|------------|
| Total Segments | **59** | **38** | **+21 (55% more)** |
| Piece_08 BL1 | Missing | 2 segments | Need to regenerate |
| Surface Point Counts | ~15K uniform | Variable (1.5K-19K) | Different density |
| Coordinate System | Millimeters | Millimeters | ✅ Fixed |

**Key Finding**: The datasets are FUNDAMENTALLY DIFFERENT in surface segmentation and density, despite using the same input meshes.

---

## 1. Critical Differences Found

### 1.1 Segment Counts Per Breakline

| File | New | Sample | Diff |
|------|-----|--------|------|
| Piece_01_BL0 | 6 | 4 | +2 |
| Piece_01_BL1 | 9 | 4 | **+5** |
| Piece_02_BL0 | 4 | 2 | +2 |
| Piece_02_BL1 | 3 | 2 | +1 |
| Piece_03_BL0 | 4 | 3 | +1 |
| Piece_03_BL1 | 4 | 3 | +1 |
| Piece_04_BL0 | 4 | 3 | +1 |
| Piece_04_BL1 | 4 | 3 | +1 |
| Piece_05_BL0 | 4 | 3 | +1 |
| Piece_05_BL1 | 4 | 3 | +1 |
| Piece_06_BL0 | 2 | 1 | +1 |
| Piece_06_BL1 | 2 | 1 | +1 |
| Piece_07_BL0 | 3 | 2 | +1 |
| Piece_07_BL1 | 3 | 2 | +1 |
| Piece_08_BL0 | 3 | 2 | +1 |
| Piece_08_BL1 | - | 2 | Missing |
| **TOTAL** | **59** | **38** | **+21** |

### 1.2 Surface Point Count Differences (CRITICAL)

| Piece | New S0 | New S1 | Sample S0 | Sample S1 | New Total | Sample Total |
|-------|--------|--------|-----------|-----------|-----------|--------------|
| 01 | 16,648 | 13,885 | 19,463 | 17,145 | 30,533 | 36,608 |
| 02 | 17,812 | 16,111 | 12,178 | 13,455 | 33,923 | 25,633 |
| 03 | 17,902 | 16,264 | 11,577 | 12,798 | 34,166 | 24,375 |
| 04 | 18,956 | 17,091 | 9,399 | 10,462 | 36,047 | 19,861 |
| 05 | 16,503 | 15,457 | 9,309 | 9,798 | 31,960 | 19,107 |
| 06 | 16,007 | 14,371 | 6,574 | 7,317 | 30,378 | 13,891 |
| 07 | 13,114 | 12,179 | **1,745** | **1,796** | 25,293 | **3,541** |
| 08 | 14,949 | 14,757 | **1,576** | **1,761** | 29,706 | **3,337** |

**Key Observation**:
- Sample dataset has DECREASING density: Piece_01 (19K) → Piece_08 (1.5K)
- New dataset has CONSISTENT density: ~15K across all pieces
- Sample Pieces 07-08 have only **~1,700 points** vs our **~14,000 points** (8x difference!)

### 1.3 Coordinate Comparison

**Surface_0 First Point Coordinates:**

| Piece | New X,Y,Z | Sample X,Y,Z |
|-------|-----------|--------------|
| 01 | -8.84, -22.28, 411.12 | 64.19, -27.97, 395.39 |

**Breakline_0 First Point Coordinates:**

| Piece | New X,Y,Z | Sample X,Y,Z |
|-------|-----------|--------------|
| 01 | 78.11, 9.03, 375.52 | 64.96, -52.05, 401.60 |

**Finding**: Coordinates are COMPLETELY DIFFERENT - different surface regions are being selected.

---

## 2. Root Cause Analysis

### 2.1 Input Data Verification
- ✅ Input meshes are IDENTICAL (same vertex count: 100,064, same coordinates)
- ✅ Both datasets use the same OBJ mesh files

### 2.2 Preprocessing Differences

| Aspect | New Dataset | Sample Dataset |
|--------|-------------|----------------|
| Surface Density | Uniform ~15K | Variable 1.5K-19K |
| Surface Assignment | Consistent S0/S1 | Different S0/S1 mapping |
| Coordinate Origin | Different per piece | Different per piece |
| Breakline Detection | Adaptive parameters | Unknown parameters |

### 2.3 Why Surfaces Are Different

1. **Different Surface Assignment**: The clustering algorithm assigns Surface_0 vs Surface_1 based on Euclidean clustering order, not geometric properties. This can vary between runs.

2. **Different Downsampling**: Sample dataset appears to use variable/aggressive downsampling (especially for pieces 07-08), while new dataset uses uniform ~15K sampling.

3. **Different Region Growing**: The surface segmentation parameters may differ, causing different point assignment to each surface.

---

## 3. What Would Need to Change

### Option A: Match Sample's Surface Assignment
**Difficulty: HIGH**

To make new output match sample exactly:
1. Swap Surface_0 ↔ Surface_1 for pieces where assignment differs
2. Match the variable downsampling density (1.5K-19K gradient)
3. Match the exact coordinate regions per surface
4. Tune peak detection to produce fewer segments

**Challenge**: The surface assignment is non-deterministic in clustering. Would need to:
- Analyze each piece's geometry
- Determine which cluster corresponds to which sample surface
- Potentially require manual mapping

### Option B: Tune Segment Count Only
**Difficulty: MEDIUM**

To reduce segment count from 59 to ~38:
1. Increase peak detection divisor (currently 8, try 10-12)
2. Increase segment merging threshold
3. Reduce breakline point density

**Challenge**: May affect breakline quality and edge accuracy.

### Option C: Accept Differences
**Difficulty: LOW**

The datasets are fundamentally different due to:
- Different preprocessing pipeline settings
- Non-deterministic clustering
- Different density targets

The new dataset may actually be BETTER for downstream tasks due to:
- More consistent surface density
- More complete breakline coverage
- Higher point counts for pieces 07-08

---

## 4. File Format Comparison

### PCD Header Format
Both datasets use identical format:
```
# .PCD v0.7 - Point Cloud Data file format
# <num_segments> <total_points> 0
# <start_idx> <end_idx> 0
...
VERSION 0.7
FIELDS x y z normal_x normal_y normal_z curvature
SIZE 4 4 4 4 4 4 4
TYPE F F F F F F F
COUNT 1 1 1 1 1 1 1
```

✅ Format is COMPATIBLE

---

## 5. Recommendations

### Immediate Actions:
1. **Regenerate Piece_08_BL1** - Currently missing
2. **Document parameter differences** for reproducibility

### For Matching Sample Output:
1. The sample dataset appears to have been generated with different parameters
2. Exact matching would require understanding the original preprocessing settings
3. Consider if matching is necessary - new dataset may be higher quality

### For Future Development:
1. Make surface assignment deterministic (e.g., by centroid Z-coordinate)
2. Add configurable density targets per piece
3. Document all preprocessing parameters

---

## 6. File Locations

| Dataset | Location |
|---------|----------|
| New Breaklines | `Dataset/Breaklines/Pot_A/` |
| New Surfaces | `Dataset/Surfaces/Pot_A/` |
| Sample | `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/` |
| Source Mesh | `Dataset/Mesh/Pot_A/` (symlinks to temp_download) |

---

## 7. Conclusion

The new and sample datasets are **fundamentally different** despite using identical input meshes. The differences stem from:

1. **Different preprocessing parameters** (density, clustering, etc.)
2. **Non-deterministic surface assignment** in clustering
3. **Variable vs uniform downsampling**

To match the sample exactly would require either:
- Reverse-engineering the original preprocessing parameters
- Manual surface mapping and adjustment
- Accepting that exact matching may not be possible/necessary

**Recommendation**: Focus on ensuring the new dataset meets quality requirements rather than matching the sample exactly, as the new dataset may provide better coverage and consistency.

---

*Report generated: 2025-12-07*
*Analysis performed by SfS Preprocessing Pipeline Deep-Dive*
