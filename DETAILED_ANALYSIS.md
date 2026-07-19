# Detailed Comparison: New Dataset vs Sample

## Summary

- **Total Segments**: New=78, Sample=56, Difference=+22
- **All 16 breaklines** have 1-5 more segments than sample
- **Peak detection divisor=8** is consistent across all pieces
- **Key issue**: Peak detection too sensitive (detecting too many segment boundaries)

---

## Piece 01 - CRITICAL OUTLIER

### Breakline 0 (Surface_1)
**Segments**: New=7, Sample=5 → **+2 extra**

| Stage | New | Sample | Notes |
|-------|-----|--------|-------|
| Boundary Detection | 383 pts (4mm radius) | ? | Dense surface (16,645 points) |
| Outlier Removal | 383 → 345 pts (-38) | ? | 2.5mm radius, 3 neighbors |
| Sequencing | 345 → 311 pts (K=34) | ? | 90% retention (good!) |
| Sphere-Marching | 311 → 204 pts | 208 pts | Similar final count |
| Peak Detection | divisor=8 | ? | **Detecting 7 vs 5 segments** |

**Analysis**: Pipeline working well (204 vs 208 points). Issue is peak detection sensitivity.

**Action**: Increase divisor 8 → 10-12 to reduce false peaks

---

### Breakline 1 (Surface_0) - **MAJOR PROBLEM**
**Segments**: New=10, Sample=5 → **+5 extra (worst case)**

| Stage | New | Sample | Notes |
|-------|-----|--------|-------|
| Boundary Detection | 567 pts (4mm radius) | ? | Moderately dense (13,883 points) |
| Outlier Removal | 567 → 480 pts (-87) | ? | 2.5mm radius, 3 neighbors |
| Sequencing | 480 → **129 pts** (K=48) | ? | **73% loss! (CRITICAL)** |
| Sphere-Marching | 129 → 90 pts | 214 pts | **Only 42% of sample** |
| Peak Detection | divisor=8 | ? | Detecting 10 vs 5 segments |

**Analysis**:
1. **Sequencing failure**: 480 → 129 pts (73% loss) indicates fragmented/disconnected boundary
2. **Final points**: Only 90 vs sample's 214 (58% missing)
3. **Over-segmentation**: Sparse breakline (90 pts) with gaps → false peaks → 10 segments

**Root Cause**: Boundary is fragmented even after filtering. Sequencing K=48 can't connect distant clusters.

**Actions**:
1. **Investigate boundary fragmentation**: Why does this surface have disconnected boundary clusters?
2. **Consider**: Reduce outlier removal strictness further for this piece
3. **Or**: Improve boundary detection to capture continuous edges

---

## Pieces 02-08 - CONSISTENT PATTERN

All remaining pieces show **+1 or +2 extra segments** per breakline.

### Example: Piece 02 Breakline 0
| Stage | New | Sample |
|-------|-----|--------|
| Boundary | 435 pts | ? |
| After Outlier | 434 pts (-1) | ? |
| Sequencing | 370 pts (K=43) | ? |
| Smoothed | 259 pts | 169 pts |
| Segments | 5 | 3 |

**Pattern**: Pipeline works well, but peak detection finds +2 extra segment boundaries.

---

## Key Findings

### 1. **Peak Detection Sensitivity** (MAIN ISSUE)
- All pieces use **divisor=8**
- Consistently detecting +1 to +5 more segments than sample
- **Solution**: Increase divisor to 10-14 (lower sensitivity)

### 2. **Piece 01 BL1 Sequencing Failure** (SECONDARY ISSUE)
- Unique problem: 73% point loss during sequencing
- Results in sparse, gappy breakline (90 pts vs 214)
- **Solution**:
  - Option A: Further reduce outlier removal strictness (min_neighbors 3→2)
  - Option B: Investigate why boundary is fragmented on this surface
  - Option C: Improve sequencing algorithm to handle gaps better

### 3. **Point Count Differences**
- **Pieces 07-08**: New has 3-4× MORE points than sample (sample seems downsampled?)
- **Most pieces**: New has 10-50% more points (acceptable variation)
- **Piece 01 BL1**: New has 42% FEWER points (problematic)

---

## Recommended Actions (Priority Order)

### Priority 1: Adjust Peak Detection Divisor
**Current**: divisor=8 for all dense breaklines
**Proposed**: divisor=12 (50% increase in sensitivity threshold)
**Expected Impact**: Reduce total segments from 78 → ~60-65

**Implementation**:
```cpp
// Line ~1631 in edgeline_extraction_headless.cpp
if (cloud_in.rows() > 100) {
    sensitivity_divisor = 12;  // was 8
```

### Priority 2: Fix Piece 01 BL1 Sequencing
**Current**: 480 filtered pts → 129 sequenced (73% loss)
**Investigation needed**:
1. Visualize boundary point cloud to see fragmentation
2. Check if boundary has multiple disconnected components
3. Consider surface-specific parameters

### Priority 3: Fine-tune Outlier Removal
**Current**: min_neighbors=3 (fixed)
**Proposed**: Adaptive based on boundary density
```cpp
int min_neighbors = (outlier_spacing_mm < 1.0) ? 4 : 3;
```

---

## Expected Final Results

After Priority 1 fix (divisor 8→12):
- **Piece 01**: 7+10 → 5+7 = 12 segments (vs sample 10)
- **Pieces 02-08**: ~66 segments (vs sample 46)
- **Total**: ~78 → ~65 segments (vs sample 56)

After Priority 2 fix (Piece 01 BL1):
- **Piece 01 BL1**: 7 → 5 segments
- **Total**: ~65 → ~63 segments

Final gap: ~63 vs 56 = 7 extra segments (acceptable tolerance)
