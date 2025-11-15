# TPS Preprocessing Dataset - August 29, 2025

**Pipeline Type**: TPS (Thin Plate Spline) Surface Fitting  
**Generated**: August 29, 2025  
**Pottery Collection**: Pot A (8 pieces)  
**Status**: 87.5% Complete (missing breaklines)

## Dataset Structure:
Matches original sample organization for compatibility:
```
TPS_Dataset_20250829/
└── SfS_pp/
    ├── Surfaces/     # TPS-fitted surfaces + Surface_F files
    ├── Axes/         # MATLAB PotSAC extracted axes  
    ├── Breaklines/   # ❌ MISSING - needs TPS-specific generation
    └── Mesh/         # Original OBJ mesh files
```

## Comparison to Original NURBS Dataset:
- **Original**: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`
- **TPS Version**: `/data/gpfs/projects/punim2657/sfs_preprocessing/TPS_Dataset_20250829/SfS_pp/`

## Key Differences from NURBS:
1. **Surfaces**: TPS mathematical fitting vs NURBS B-spline fitting
2. **File sizes**: TPS surfaces larger (31K vs 19K lines for piece 01)
3. **Breaklines**: Missing TPS-compatible versions
4. **Surface_F**: Generated from TPS geometry

## Usage:
```bash
# Replace main SFS dataset with TPS version
cp -r TPS_Dataset_20250829/SfS_pp/* /path/to/sfs_main/sfspreproc-docker/Dataset/SfS_pp/
```

## Critical Issue:
**Missing TPS Breaklines**: Dataset cannot be used for SFS testing until TPS-compatible breaklines are generated. Current contamination with NURBS breaklines causes geometric mismatch and poor feature matching (19 vs 444 expected matches).