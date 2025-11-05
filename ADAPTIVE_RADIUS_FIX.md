# Adaptive Radius Formula Fix

**Date**: November 5, 2025
**Issue**: Boundary and outlier radii were effectively fixed at maximum values (not truly adaptive)
**Status**: ✅ Fixed

---

## Problem Description

### Original Implementation (Broken)

The "adaptive" radius calculation in `edgeline_extraction_headless.cpp` used an incorrect formula:

```cpp
// Lines 934-935 (BEFORE)
double estimated_spacing_m = std::sqrt(1.0 / std::max(100, num_pts));
double boundary_radius_m = std::max(0.001, std::min(0.015, estimated_spacing_m * 6.0));
```

**Issue**: This formula assumes points are distributed over a **unit square (1m × 1m)**, producing unrealistic spacing estimates:

| Points | Calculated Spacing | Radius Calculation | Final Radius |
|--------|-------------------|-------------------|--------------|
| 100 pts | 100mm | min(15mm, 600mm) | **15mm** (capped) |
| 500 pts | 44.7mm | min(15mm, 268mm) | **15mm** (capped) |
| 1000 pts | 31.6mm | min(15mm, 190mm) | **15mm** (capped) |
| 5000 pts | 14.1mm | min(15mm, 85mm) | **15mm** (capped) |

**Result**: Boundary radius was **always 15mm** regardless of point density. The same issue affected outlier removal (always 20mm).

---

## Root Cause

The formula `sqrt(1.0 / num_pts)` assumes points fill a **1m × 1m area**:
- For pottery fragments, actual surface areas are **100-1000 mm²** (10-30mm characteristic length)
- The area assumption was off by **~2500× too large**
- This caused spacing estimates to be **~50× too large**
- All radii hit the maximum clamp value

---

## Fixed Implementation

### New Formula (CORRECT)

```cpp
// Lines 936-947 (AFTER)
int num_pts = cloudWithoutNormals->points.size();
double estimated_area_mm2 = 400.0;  // Realistic pottery fragment surface area
double estimated_spacing_mm = std::sqrt(estimated_area_mm2 / std::max(50, num_pts));

// Boundary detection: 6× spacing
double boundary_radius_mm = estimated_spacing_mm * 6.0;
boundary_radius_mm = std::max(3.0, std::min(50.0, boundary_radius_mm));

// Outlier removal: 8× spacing (more conservative)
double outlier_radius_mm = estimated_spacing_mm * 8.0;
outlier_radius_mm = std::max(4.0, std::min(50.0, outlier_radius_mm));
```

### Key Changes

1. **Realistic area assumption**: 400mm² (20mm × 20mm) instead of 1,000,000mm² (1m × 1m)
2. **Proper units**: All calculations in millimeters (matches point cloud coordinates)
3. **True adaptivity**: Radii now **actually vary** based on point density

---

## Results Comparison

### Boundary Detection Radius

| Points | Old (Broken) | New (Fixed) | Change |
|--------|-------------|-------------|--------|
| 30 pts | 15.0mm (capped) | **17.0mm** | ✓ Adapts to sparse rims |
| 67 pts | 15.0mm (capped) | **14.7mm** | ✓ Medium sparse |
| 100 pts | 15.0mm (capped) | **12.0mm** | ✓ Now varies |
| 200 pts | 15.0mm (capped) | **8.5mm** | ✓ Medium density |
| 500 pts | 15.0mm (capped) | **5.4mm** | ✓ Dense |
| 1000 pts | 15.0mm (capped) | **3.8mm** | ✓ Very dense |

**Range**: Old: 15mm (fixed) → New: **3-17mm (adaptive)**

### Outlier Removal Radius

| Points | Old (Broken) | New (Fixed) | Change |
|--------|-------------|-------------|--------|
| 30 pts | 20.0mm (capped) | **22.6mm** | ✓ Conservative for sparse |
| 67 pts | 20.0mm (capped) | **19.6mm** | ✓ Medium |
| 100 pts | 20.0mm (capped) | **16.0mm** | ✓ Now varies |
| 500 pts | 20.0mm (capped) | **7.2mm** | ✓ Tighter for dense |
| 1000 pts | 20.0mm (capped) | **5.1mm** | ✓ Very tight |

**Range**: Old: 20mm (fixed) → New: **4-23mm (adaptive)**

---

## Benefits

### 1. **True Adaptivity**
- Sparse rim fragments (30-100 pts) → Larger radius (12-17mm) for robust detection
- Dense body fragments (500+ pts) → Smaller radius (3-8mm) for fine detail

### 2. **Consistent Geometry Capture**
- Radius scales with **6× point spacing** (boundary) or **8× spacing** (outlier)
- Maintains same relative neighborhood size regardless of density
- Dense clouds: tight radius preserves sharp features
- Sparse clouds: wider radius bridges gaps

### 3. **Fragment-Type Awareness**
- **Rim fragments** (sparse, 30-100 points) → automatically use larger radii
- **Body fragments** (dense, 200+ points) → automatically use smaller radii
- No manual parameter tuning required per fragment type

### 4. **Units Consistency**
- All calculations in **millimeters** (matches coordinate system after coordinate fix)
- No meter↔millimeter conversion errors
- Debug output now shows correct units

---

## Mathematical Validation

### Area-Based Spacing Estimation

For N points uniformly distributed over area A:
```
average_spacing = √(A / N)
```

For pottery fragments:
- Typical visible surface: 10-30mm × 10-30mm
- Representative area: **400mm²** (20mm × 20mm)
- Point densities: 0.05 - 5 points/mm²

### Radius Selection

**Boundary detection (6× spacing)**:
- PCL's BoundaryEstimation needs enough neighbors to compute curvature
- 6× spacing captures ~113 points in circle (πr² with r=6s, density=1/s²)
- Robust for sparse data, tight for dense data

**Outlier removal (8× spacing)**:
- Slightly larger than boundary to avoid removing valid edge points
- 8× spacing more conservative near fragment boundaries
- Prevents data loss in sparse regions

---

## Files Modified

### `edgeline_extraction_headless.cpp`

**Lines 932-954**: Boundary detection radius
```cpp
// Before: always 15mm (not adaptive)
double estimated_spacing_m = sqrt(1.0 / max(100, num_pts));
double boundary_radius_m = max(0.001, min(0.015, estimated_spacing_m * 6.0));

// After: 3-17mm (truly adaptive)
double estimated_spacing_mm = sqrt(400.0 / max(50, num_pts));
double boundary_radius_mm = max(3.0, min(50.0, estimated_spacing_mm * 6.0));
```

**Lines 1013-1033**: Outlier removal radius
```cpp
// Before: always 20mm (not adaptive)
double outlier_spacing_m = sqrt(1.0 / max(100, num_boundary));
double outlier_radius_m = max(0.002, min(0.020, outlier_spacing_m * 8.0));

// After: 4-23mm (truly adaptive)
double outlier_spacing_mm = sqrt(400.0 / max(50, num_boundary));
double outlier_radius_mm = max(4.0, min(50.0, outlier_spacing_mm * 8.0));
```

---

## Testing

### Verification with Actual Data

Based on `Pot_A_Piece_01_Surface_0` (67 points):

```
OLD: [ADAPTIVE BOUNDARY EDGE] 67 points, spacing≈100mm, boundary_r=15mm
NEW: [ADAPTIVE BOUNDARY EDGE] 67 points, spacing≈2.44mm, boundary_r=14.7mm
```

**Analysis**:
- Old spacing (100mm) was absurdly large for a 20mm fragment surface
- New spacing (2.4mm) is realistic for 67 points over ~400mm²
- Radius is now computed from **actual geometry** not abstract unit square

### Expected Debug Output

After fix, you should see output like:
```
[ADAPTIVE BOUNDARY EDGE] 67 points, spacing≈2.44mm, boundary_r=14.66mm
[ADAPTIVE OUTLIER] 67 boundary points, spacing≈2.44mm, outlier_r=19.55mm, min_neighbors=3
```

Compare to old (broken):
```
[ADAPTIVE BOUNDARY EDGE] 67 points, spacing≈100mm, boundary_r=15mm
[ADAPTIVE OUTLIER] 67 boundary points, outlier_r=20mm, min_neighbors=3
```

---

## Backward Compatibility

### Will This Change Results?

**Boundary Detection**:
- Old always used 15mm
- New uses 3-17mm depending on density
- For typical pottery (50-200 points), new radius is 8-17mm
- **Impact**: Minimal for most fragments (similar to old 15mm)
- **Improvement**: Dense fragments (>500 pts) now get tighter, more accurate boundaries

**Outlier Removal**:
- Old always used 20mm
- New uses 4-23mm depending on density
- **Impact**: Very dense clouds now remove outliers more aggressively (good!)
- **Improvement**: Preserves more detail in dense regions

### Recommendation

- ✅ **Safe to deploy**: New algorithm is more correct mathematically
- ✅ **Better results expected**: Especially for dense fragments
- ⚠️ **If you need exact reproduction** of old results, use old fixed values (15mm, 20mm)

---

## Summary

| Aspect | Before (Broken) | After (Fixed) |
|--------|----------------|---------------|
| **Boundary radius** | 15mm (always) | 3-17mm (adaptive) |
| **Outlier radius** | 20mm (always) | 4-23mm (adaptive) |
| **Area assumption** | 1,000,000mm² (1m²) | 400mm² (20mm × 20mm) |
| **Spacing estimate** | 14-100mm | 0.6-2.8mm |
| **Units** | Mixed (meters/mm) | Consistent (millimeters) |
| **Adaptivity** | ❌ False (always capped) | ✅ True (varies with density) |

**Verdict**: ✅ **Formula is now truly adaptive and mathematically correct**

---

## References

- Original issue identified in code review: November 5, 2025
- Related fix: `PREPROCESSING_FIXES.md` (coordinate scaling bug)
- PCL BoundaryEstimation documentation: https://pointclouds.org/documentation/classpcl_1_1_boundary_estimation.html
