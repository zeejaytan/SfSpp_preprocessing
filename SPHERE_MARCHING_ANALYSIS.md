# Sphere-Marching and Breakline Gap Analysis

## Problem Summary
Piece 01 Breakline 1 has only 82 points split into 16 tiny segments (vs sample's 214 points in 5 segments), with large spatial gaps of 46.9mm and 16.2mm causing false peak detection.

## Code Comparison: Original vs Modified

### 1. Sphere Radius

| Aspect | Original Code | Our Modified Code | Piece 01 BL1 Impact |
|--------|--------------|-------------------|---------------------|
| **Sphere radius** | **1.8** (fixed) | **0.55mm** (adaptive) | 🔴 **305% reduction** |
| Input points | - | 345 points | - |
| Avg spacing | - | 0.368mm | - |
| Calculated radius | - | `0.368 × 1.5 = 0.55mm` | - |
| Max radius cap | - | 5mm (dense data) | Not reached |

**Impact:** Our adaptive radius is **3.3× smaller** than original, causing:
- More aggressive sampling reduction (345 → 95 points)
- Potential skipping of low-density regions
- Introduction of spatial gaps

### 2. Boundary Extraction Parameters

| Parameter | Original | Our Code | Piece 01 BL1 |
|-----------|----------|----------|--------------|
| **Boundary radius** | **4.0** (fixed) | **3mm** (adaptive) | 25% smaller |
| Surface points | - | 13,885 points | - |
| Spacing estimate | - | 0.149mm | - |
| Calculated radius | - | `0.149 × 6 = 0.895mm` | Capped to 3mm |

### 3. Outlier Removal Parameters

| Parameter | Original | Our Code | Piece 01 BL1 |
|-----------|----------|----------|--------------|
| **Outlier radius** | **2.5** (fixed) | **7.66mm** (adaptive) | 306% larger |
| Boundary points | - | 436 points | - |
| Min neighbors | **6** (fixed) | **6** (adaptive) | Same |

### 4. Post-Processing

| Step | Original | Our Code | Impact |
|------|----------|----------|--------|
| **Densification** | Not explicitly shown | **DISABLED** (line 710) | 🔴 No gap filling |
| B-spline projection | Yes (surface fitting) | Yes | Same |
| Segment detection | Peak detection | Peak detection | Same |

## Root Cause Analysis

### Issue 1: Aggressive Sphere Radius Reduction
```
Original:  1.8mm sphere → moderate sampling
Modified:  0.55mm sphere (3.3× smaller) → aggressive sampling
Result:    Skips regions, creates gaps
```

For Piece 01 Breakline 1:
- **Input:** 345 sequenced boundary points (spacing ~0.368mm)
- **Sphere-marching:** Uses 0.55mm radius (only 1.5× spacing)
- **Output:** 95 points (72% reduction)
- **Problem:** In regions with slightly lower density, sphere "jumps" over multiple points, creating gaps

### Issue 2: Disabled Densification
```
Original:  May have densification/interpolation
Modified:  Densification DISABLED (line 710)
Result:    Gaps not filled before segment detection
```

The 95 points go directly to B-spline fitting with gaps intact, which then get detected as geometric features (peaks).

### Issue 3: Sphere-Marching Logic Vulnerability

Original algorithm:
```cpp
while (distTmp < sphereRadius && i < P.rows() - 2) {
    i++;  // Skip points inside sphere
}
```

When sphere radius is small relative to point cloud irregularities:
- **Dense regions:** Works well (points close together)
- **Sparse regions:** Skips too many points, creates large jumps
- **Result:** Discontinuous breakline path

## Gap Formation Mechanism

For Piece 01 BL1 gap at points 8→9:

```
Point 7: (39117.5, 15558.4, 399988)
Point 8: (37492.9, 16267.7, 400050)  ← Last point before gap
----- 46.9mm spatial jump -----
Point 9: (6104.04, -13104.2, 418820)  ← First point after gap
```

**Hypothesis:** Between original points 8-9, there were intermediate boundary points, but:
1. Sphere radius too small to "bridge" across lower-density region
2. Algorithm skipped from point 8 directly to distant point 9
3. Line-sphere intersection created a large jump instead of smooth transition

## Sample Dataset Success

Sample dataset likely used:
- **Fixed 1.8mm radius:** Better suited for pottery rim geometry
- **More conservative sampling:** Preserves continuity
- **Possible densification:** Fills gaps before segment detection
- **Result:** Continuous 214-point breakline → 5 natural segments

## Recommendations

1. **Restore original sphere radius:** Use fixed 1.8mm instead of adaptive
2. **Enable densification:** Re-enable Integration Point #1 (line 711)
3. **Add gap detection:** Detect large jumps and add interpolation
4. **Validate continuity:** Check max point-to-point distance before segmentation

## Test Case

Piece 01 Breakline 1 should produce:
- ✓ 200+ continuous points (not 82 with gaps)
- ✓ Max gap < 5mm (not 46.9mm)
- ✓ 3-5 segments (not 16)
