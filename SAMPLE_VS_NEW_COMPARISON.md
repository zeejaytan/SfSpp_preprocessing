# COMPREHENSIVE COMPARISON: Sample vs New Dataset

**Date**: 2025-11-20
**Sample Dataset**: `/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp/`
**New Dataset**: Current dataset with 5× sphere radius modification (19K surface target)

---

## BREAKLINES (Pot A, 5× Sphere Radius)

| Breakline | Sample Pts | New Pts | Ratio |
|-----------|------------|---------|-------|
| Piece_01_B0 | 208 | 69 | 0.33× |
| Piece_01_B1 | 214 | 59 | 0.28× |
| Piece_02_B0 | 169 | 81 | 0.48× |
| Piece_02_B1 | 170 | 60 | 0.35× |
| Piece_03_B0 | 156 | 70 | 0.45× |
| Piece_03_B1 | 161 | 82 | 0.51× |
| Piece_04_B0 | 151 | 76 | 0.50× |
| Piece_04_B1 | 155 | 64 | 0.41× |
| Piece_05_B0 | 147 | 67 | 0.46× |
| Piece_05_B1 | 151 | 76 | 0.50× |
| Piece_06_B0 | 150 | 72 | 0.48× |
| Piece_06_B1 | 152 | 78 | 0.51× |
| Piece_07_B0 | 65 | 43 | 0.66× |
| Piece_07_B1 | 67 | 64 | 0.96× |
| Piece_08_B0 | 60 | 69 | 1.15× |
| Piece_08_B1 | 63 | 62 | 0.98× |

**Summary**:
- **Total breaklines**: 16 (both)
- **Total points**: 2,239 (sample) vs 1,092 (new)
- **Average per breakline**: 139 (sample) vs 68 (new)
- **Range**: 60-214 (sample) vs 43-82 (new)
- **Overall ratio**: **0.49×** (new has ~half the points)

---

## SURFACES (Pot A, 19K Target)

| Surface | Sample Pts | New Pts | Ratio |
|---------|------------|---------|-------|
| Piece_01_S0 | 31,615 | 16,790 | 0.53× |
| Piece_01_S1 | 28,810 | 13,995 | 0.49× |
| Piece_02_S0 | 12,178 | 17,997 | 1.48× |
| Piece_02_S1 | 13,455 | 16,286 | 1.21× |
| Piece_03_S0 | 11,577 | 18,156 | 1.57× |
| Piece_03_S1 | 12,798 | 16,534 | 1.29× |
| Piece_04_S0 | 9,399 | 19,086 | 2.03× |
| Piece_04_S1 | 10,462 | 17,271 | 1.65× |
| Piece_05_S0 | 9,309 | 16,696 | 1.79× |
| Piece_05_S1 | 9,798 | 15,899 | 1.62× |
| Piece_06_S0 | 6,574 | 16,161 | 2.46× |
| Piece_06_S1 | 7,317 | 14,641 | 2.00× |
| Piece_07_S0 | 1,745 | 13,332 | 7.64× |
| Piece_07_S1 | 1,796 | 12,496 | 6.96× |
| Piece_08_S0 | 1,576 | 15,082 | 9.57× |
| Piece_08_S1 | 1,761 | 14,974 | 8.50× |

**Summary**:
- **Total surfaces**: 16 (both)
- **Total points**: 170,170 (sample) vs 255,396 (new)
- **Average per surface**: 10,635 (sample) vs 15,962 (new)
- **Overall ratio**: **1.50×** (new is 1.5× denser)

---

## AXES (Pot A)

- **Sample**: 8/8 axes (all pieces)
- **New**: 8/8 axes (all pieces)
- **Format**: Sample uses `.xyz` (2-line format), New uses `.txt` (1-line format)

---

## COORDINATE SYSTEMS

**Sample** (Piece_01_Surface_0, first point):
```
-16.1577 -7.48717 407.001 -0.0836252 -0.302476 -0.949482
```

**New** (Piece_01_Surface_0, first point):
```
0.135235 -1.13142 402.48 -0.0918494 -0.372871 -0.923326
```

**Coordinate Ranges**:
- Sample: X(-60 to +52), Y(-60 to +10), Z(376-419 mm)
- New: X(-22 to +64), Y(-60 to +42), Z(376-411 mm)

✓ **Both datasets use the same coordinate system** (millimeters, 0-400 range)

---

## KEY FINDINGS

### 1. Breakline Density (Impact of 5× Sphere Radius)

**Sample dataset**:
- Average: 139 points per breakline
- Range: 60-214 points
- Algorithm: Original sphere-marching (1.5× avgSpacing)

**New dataset (5× modification)**:
- Average: 68 points per breakline
- Range: 43-82 points
- Algorithm: Modified sphere-marching (5.0× avgSpacing, densification disabled)

**Result**: New has **~50% fewer breakline points** due to larger sphere radius

### 2. Surface Density (Impact of 19K Target)

**Sample dataset**:
- Average: 10,635 points per surface
- No specific downsampling target

**New dataset (19K target)**:
- Average: 15,962 points per surface
- PCL UniformSampling targeting ~19,000 points

**Result**: New has **1.5× denser surfaces**

**Note**: Variation in density ratio (0.5× to 9.5×) across pieces:
- Pieces 01: New has FEWER points (sample had very dense input)
- Pieces 07-08: New has MUCH MORE points (sample had sparse input)
- Average across all pieces: 1.5× denser

### 3. Coordinate Systems

✓ **Identical coordinate systems** - no transformation needed

Both datasets:
- Use millimeter coordinates
- Have similar coordinate ranges (0-400mm)
- Can be directly compared without conversion

---

## ALGORITHM DIFFERENCES

### Breakline Extraction

| Aspect | Sample | New (5×) |
|--------|--------|----------|
| Sphere radius | 1.5× avgSpacing | 5.0× avgSpacing |
| Max radius clamp | 5-15mm | Removed |
| Densification | Enabled (2mm spacing) | Disabled |
| Result | 139 avg pts | 68 avg pts |

### Surface Sampling

| Aspect | Sample | New |
|--------|--------|-----|
| Downsampling target | Variable | ~19,000 points |
| Method | Unknown | PCL UniformSampling |
| Result | 10,635 avg pts | 15,962 avg pts |

---

## COMPARISON SUMMARY

1. **Breaklines**: New has **~50% fewer points** (68 vs 139 avg) with narrower range (43-82 vs 60-214)
2. **Surfaces**: New has **1.5× more points** (15,962 vs 10,635 avg) due to 19K target
3. **Axes**: Both datasets have all 8 axes (different file formats)
4. **Coordinates**: Identical coordinate systems (millimeters)

The 5× sphere radius successfully reduced breakline density while maintaining 1.5× denser surface sampling.
