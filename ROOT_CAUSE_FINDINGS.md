# Root Cause Analysis: Breakline Segmentation Inconsistency

## Summary
Piece 01 Breakline 1 has only 82 points split into 16 segments (vs sample's 214 points in 5 segments). Investigation reveals **THREE compounding issues** in the processing pipeline.

---

## Issue #1: Point Sequencing Failure (584 → 162 points = 72% loss)

### Problem
The `getPointsInSequence()` function loses 422 points during boundary point ordering.

### Root Cause
The greedy nearest-neighbor sequencing algorithm:
1. Starts at point 0
2. Searches K=50 nearest neighbors
3. Picks first unused neighbor
4. **Gets trapped in disconnected regions**

```cpp
for (size_t t = 1; t < cloud->points.size(); t++) {
    // Find K nearest neighbors
    // Pick first unused neighbor
    // If all neighbors used → silently continues without adding point
}
```

### Evidence (Piece 01 BL1)
- **Input:** 584 boundary points after outlier removal
- **Expected:** 584 sequenced points
- **Actual:** 162 sequenced points
- **Lost:** 422 points (72%)

### Why This Happens
The boundary likely has:
- **Multiple disconnected components** (different rim sections)
- **Loops or branches** where algorithm gets trapped
- **Dead ends** where all K neighbors are already used

### Impact on Results
Starting with only 162 points instead of 584 means:
- Less geometric information for sphere-marching
- Higher chance of discontinuities
- Reduced final breakline quality

---

## Issue #2: Adaptive Sphere Radius Too Small (162 → 95 points = 59% loss)

### Problem
Adaptive radius calculation produces 1.77mm radius (vs original's fixed 1.8mm), but input points are already sparse due to Issue #1.

### Formula
```cpp
sphereRadius = avgSpacing × 1.5
             = 1.18mm × 1.5
             = 1.77mm
```

### Why This Fails for Piece 01 BL1

| Metric | Piece 01 BL0 (Good) | Piece 01 BL1 (Bad) | Impact |
|--------|--------------------:|-------------------:|--------|
| **Sequenced points** | 359 | 162 | BL1 has 45% fewer |
| **Avg spacing** | 1.14mm | 1.18mm | BL1 slightly sparser |
| **Adaptive radius** | 1.70mm | 1.77mm | Similar |
| **Output points** | 219 (61% retained) | 95 (59% retained) | Similar retention |
| **Final segments** | 7 | 16 | 🔴 BL1 over-segmented |

The adaptive radius **works correctly** (similar retention %), but:
- **BL0 starts with 359 dense points** → 219-point smooth curve → 7 segments ✓
- **BL1 starts with only 162 sparse points** → 95-point gappy curve → 16 segments ✗

### Key Insight
The adaptive radius itself isn't the problem. The problem is it operates on **already degraded input** from Issue #1.

---

## Issue #3: Spatial Gaps Create False Peaks (95 → 82 points, 16 segments)

### Problem
The sparse 95-point breakline contains large spatial discontinuities that segment detection interprets as geometric features.

### Evidence
```
Point 8: (37492.9, 16267.7, 400050)
         ⬇ 46.9mm gap
Point 9: (6104.04, -13104.2, 418820)
```

Also: 16.2mm gap between points 58→59

### Why Gaps Form
With only 95 points from sphere-marching:
1. Sphere advances along sparse input (162 pts)
2. Encounters region with wider point spacing
3. **Skips multiple points** to find next point outside sphere
4. Creates discontinuous "jump" in breakline path

### Peak Detection Response
The `detectSeparateLineSegments()` algorithm:
- Calculates distance from each point to chord spanning ±10 neighbors
- **Large gaps look like peaks** (high distance scores)
- Splits breakline into 16 tiny segments (avg 5 points each)

### Comparison with Sample
| Dataset | Continuity | Max Gap | Segments | Avg Points/Seg |
|---------|-----------|---------|----------|----------------|
| **Sample** | Continuous | <5mm | 5 | 43 |
| **New** | Broken | 46.9mm | 16 | 5 |

---

## Why Adaptive Radius Works for Other Pieces

Looking at ALL pieces:

| Piece | BL | Sequenced | Sphere Out | Final Pts | Segments | Status |
|-------|----|-----------|-----------:|----------:|---------:|--------|
| 01 | 0 | 359 | 219 | 219 | 7 | ✓ Good |
| **01** | **1** | **162** | **95** | **82** | **16** | **✗ Bad** |
| 02 | 0 | 401 | 261 | 261 | 5 | ✓ Good |
| 02 | 1 | 294 | 218 | 218 | 5 | ✓ Good |
| 03-08 | ... | 300-450 | 180-310 | Similar | 3-5 | ✓ Good |

**Pattern:**
- **Most pieces:** 300-450 sequenced points → smooth curves → 3-5 segments ✓
- **Piece 01 BL1:** Only 162 sequenced points → gappy curve → 16 segments ✗

The adaptive radius **works fine when sequencing works**. The outlier is caused by **sequencing failure**, not radius calculation.

---

## Why Sample Dataset Succeeds

### Sample Processing (Hypothesis)
The original code likely has:

1. **Better boundary sequencing:**
   - Different K-nearest algorithm
   - Handles disconnected components better
   - Achieves ~584 → ~500+ sequenced points

2. **Fixed sphere radius:**
   - Always uses 1.8mm (vs our 1.77mm)
   - Slightly more forgiving for sparse inputs

3. **Post-processing:**
   - May have gap-filling interpolation
   - May have continuity validation
   - May reject/retry failed sequencing

### Result
Sample gets **214 continuous points** → 5 natural segments ✓

---

## Solutions

### Option A: Fix Sequencing (Recommended)
**Goal:** Get 500+ sequenced points instead of 162

1. Improve `getPointsInSequence()` algorithm:
   - Detect and handle disconnected components
   - Use larger K or multiple starting points
   - Fall back to spatial ordering if greedy fails

2. Validate sequencing output:
   - Check retention rate (>80%)
   - Measure max gap (should be <10mm)
   - Retry with different parameters if fails

### Option B: Use Fixed Sphere Radius
**Goal:** Match sample's exact processing

1. Replace adaptive radius with fixed 1.8mm
2. Simpler, but doesn't address sequencing failure
3. May still produce gaps for sparse inputs

### Option C: Post-Process Gap Filling
**Goal:** Interpolate across discontinuities

1. Detect gaps >10mm in sphere-marched output
2. Add interpolated points to bridge gaps
3. Ensure continuity before segment detection

---

## Recommendation

**Fix sequencing first (Option A)**, because:
- It's the earliest failure in the pipeline
- Losing 72% of points is unacceptable
- Downstream processing can't recover from this
- Fixes root cause, not symptoms

Then consider:
- Fixed 1.8mm radius (Option B) for simplicity
- Gap filling (Option C) as safety net

---

## Test Criteria

After fixes, Piece 01 BL1 should achieve:
- ✓ Sequencing: 500+ points (>85% retention from 584)
- ✓ Sphere-marching: 180-250 points
- ✓ Continuity: Max gap <5mm
- ✓ Segmentation: 3-6 segments (not 16)
- ✓ Match sample quality
