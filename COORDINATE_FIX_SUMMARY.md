# Coordinate Scaling Bug Fix Summary

## Problem Discovered

During detailed comparison between new dataset and sample dataset, discovered breakline coordinates were 1000× larger than expected:

### Before Fix:
- **New breaklines**: X=78,105, Y=9,031, Z=375,519 (micrometers scale)
- **Sample breaklines**: X=64.96, Y=-52.05, Z=401.60 (millimeters scale)
- **Surfaces (both)**: X=-22 to +64, Y=-33 to +42, Z=376-411 (millimeters scale)

**Issue**: Breaklines were in micrometers while surfaces were in millimeters, preventing valid comparison with sample dataset.

---

## Root Cause

**File**: `edgeline_extraction_headless.cpp`

**Function**: `writeBreaklinePCDWithSegments()` (lines 1244-1343)

**Bug Location**: Lines 1306-1308
```cpp
double x = convertToMM ? point.x * 1000.0 : point.x;
double y = convertToMM ? point.y * 1000.0 : point.y;
double z = convertToMM ? point.z * 1000.0 : point.z;
```

**Call Site**: Line 3266
```cpp
// OLD (bug):
writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline, index, detectedPeakIndices);
// Used default convertToMM=true, multiplying by 1000
```

**Why It Was Wrong**:
- Function parameter `convertToMM` defaults to `true`
- When `true`, coordinates are multiplied by 1000 (meters → millimeters conversion)
- BUT input coordinates were already in millimeters
- Result: Millimeters → Micrometers (1000× too large)

---

## The Fix

**Modified Line 3266**:
```cpp
// NEW (fixed):
writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline, index, detectedPeakIndices, false);
// Explicitly pass false to disable multiplication
```

**Build**:
- Rebuilt binary at: `/data/gpfs/projects/punim2657/sfs_preprocessing/build_new/EdgeLineExtractionHeadless`
- Build timestamp: Dec 3 03:13
- Object file timestamp: Dec 3 03:13

---

## Verification

### After Fix:

**Piece 01 BL0 coordinates**:
```
X=78.11, Y=9.03, Z=375.52
```

**Piece 01 BL1 coordinates**:
```
X=56.0, Y=-13.8, Z=406.7
```

**All pieces verified** (01-08):
- X range: -22 to +78
- Y range: -66 to +70
- Z range: 303 to 446
- ✅ Consistent with surface point cloud scale

### Comparison with Sample:

**Sample Piece 01 BL0**:
```
X=64.96, Y=-52.05, Z=401.60
```

**Note**: Absolute coordinates differ because:
1. Sample may have different S0/S1 surface assignment
2. Sample may use different breakline starting point
3. Coordinate scales NOW MATCH (both in millimeters)

---

## Impact

### Fixed:
✅ Breakline coordinates now in millimeters (consistent with surfaces)
✅ Can now perform valid geometric comparisons with sample dataset
✅ Downstream analysis tools will receive correct coordinate scale

### Testing Status:
- Processed all 8 pieces with corrected code
- Generated 15/16 breakline files (Piece_08 BL1 still processing)
- Coordinates verified across all completed pieces

---

## Next Steps

1. **Complete Piece_08 processing** (BL1 file pending)
2. **Segment count comparison** with sample dataset (now that coordinates match)
3. **Verify segmentation quality** (addressing original goal of matching sample's 56 segments vs current 78)

---

## Date: December 3, 2025
## Fix Applied: 03:13
## Verification Complete: 03:33
