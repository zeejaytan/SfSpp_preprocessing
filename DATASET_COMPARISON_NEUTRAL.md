# Dataset Comparison: Sample vs New (5× Sphere Radius)

**Date**: November 19, 2025  
**Objective**: Document differences between sample and new datasets

---

## SURFACES

| Metric | Sample | New |
|--------|--------|-----|
| Files | 16 | 16 |
| Total Points | 93,531 | 255,396 |
| Average per Surface | 5,845 | 15,962 |
| Target Density | ~6K | ~19K |

---

## BREAKLINES

### Overall Statistics

| Metric | Sample | New |
|--------|--------|-----|
| Files | 16 | 16 |
| Total Points | 1,760 | 1,092 |
| Average per Breakline | 110 | 68 |
| Min Points | 30 | 43 |
| Max Points | 194 | 82 |
| Range Spread | 164 (30-194) | 39 (43-82) |

### Per-Piece Breakdown

| Piece | Sample B0 | Sample B1 | New B0 | New B1 |
|-------|-----------|-----------|--------|--------|
| 01 | 59 | 150 | 69 | 59 |
| 02 | 162 | 99 | 81 | 60 |
| 03 | 130 | 175 | 70 | 82 |
| 04 | 116 | 194 | 76 | 64 |
| 05 | 140 | 43 | 67 | 76 |
| 06 | 30 | 95 | 72 | 78 |
| 07 | 132 | 111 | 43 | 64 |
| 08 | 30 | 94 | 69 | 62 |

### Segmentation Structure

**Sample Piece_01 Breakline_0** (59 points):
```
Total segments: 4
Segment 1: points 1-13   (13 points)
Segment 2: points 14-22  (9 points)
Segment 3: points 23-55  (33 points)
Segment 4: points 56-59  (4 points)
```

**New Piece_01 Breakline_0** (69 points):
```
Total segments: 4
Segment 1: points 1-8    (8 points)
Segment 2: points 9-21   (13 points)
Segment 3: points 22-49  (28 points)
Segment 4: points 50-69  (20 points)
```

**Sample Piece_07 Breakline_0** (132 points):
```
Total segments: 5
Segment 1: points 1-18    (18 points)
Segment 2: points 19-45   (27 points)
Segment 3: points 46-98   (53 points)
Segment 4: points 99-123  (25 points)
Segment 5: points 124-132 (9 points)
```

**New Piece_07 Breakline_0** (43 points):
```
Total segments: 4
Segment 1: points 1-3    (3 points)
Segment 2: points 4-21   (18 points)
Segment 3: points 22-30  (9 points)
Segment 4: points 31-43  (13 points)
```

---

## AXES

| Aspect | Sample | New |
|--------|--------|-----|
| Number of Files | 16 | 8 |
| File Coverage | Pieces 01-40 | Pieces 01-08 |
| Format | 2 lines | 1 line |
| Decimal Precision | 6 | 12 |

### Format Examples (Piece_01)

**Sample**:
```
-54.234979 -131.846461 59.653882 0.219556 0.325761 0.919606

```

**New**:
```
-54.173687805108 -131.825775025604 59.635827744411 0.219531034053 0.325795716543 0.919599519448
```

### Value Differences (Piece_01)

| Component | Sample | New | Difference |
|-----------|--------|-----|------------|
| Position X | -54.234979 | -54.173688 | +0.061291 |
| Position Y | -131.846461 | -131.825775 | +0.020686 |
| Position Z | 59.653882 | 59.635828 | -0.018054 |
| Direction X | 0.219556 | 0.219531 | -0.000025 |
| Direction Y | 0.325761 | 0.325796 | +0.000035 |
| Direction Z | 0.919606 | 0.919600 | -0.000006 |

---

## ALGORITHM PARAMETERS

### Sphere-Marching

| Parameter | Sample | New |
|-----------|--------|-----|
| Radius Multiplier | Unknown | 5.0× |
| Max Radius Clamp | Unknown | None |

### Densification

| Parameter | Sample | New |
|-----------|--------|-----|
| Adaptive Densification | Unknown | Disabled |
| Target Spacing | Unknown | N/A |

---

## FILE LOCATIONS

**Sample Dataset**:
```
/data/gpfs/projects/punim2657/sfs_preprocessing/NURBS_Dataset_20251103/SfS_pp/
├── Surfaces/
├── Breaklines/
└── Axes/
```

**New Dataset**:
```
/data/gpfs/projects/punim2657/sfs_preprocessing/
├── Dataset/Surfaces/Pot_A/
├── Dataset/Breaklines/Pot_A/
└── axis_output/
```

---

## RATIOS AND RELATIONSHIPS

| Comparison | Ratio |
|------------|-------|
| Surface points (New/Sample) | 2.73 |
| Breakline points (New/Sample) | 0.62 |
| Breakline range (New/Sample) | 0.24 |
| Axis files (New/Sample) | 0.50 |

---

**End of comparison**
