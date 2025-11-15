# TPS Preprocessing Dataset - August 31, 2025

**Pipeline Type**: TPS (Thin Plate Spline) Surface Fitting  
**Generated**: Sun 31 Aug 2025 23:36:23 AEST  
**Pottery Collection**: Pot A (8 pieces)  
**Auto-organized**: Yes (organize_dataset.sh)

## Dataset Structure:
Matches original sample organization for compatibility:
```
TPS_Dataset_20250831/
└── SfS_pp/
    ├── Surfaces/     # TPS-fitted surfaces + Surface_F files
    ├── Axes/         # MATLAB PotSAC extracted axes  
    ├── Breaklines/   # ❌ MISSING - needs TPS-specific generation
    └── Mesh/         # Original OBJ mesh files
```

## File Inventory:
- **Surfaces**: 26 surface files
- **Surface_F**: 16 feature files  
- **Axes**: 8 axis files
- **Mesh**: 8 mesh files
- **Breaklines**: 0 files (missing)

## Usage:
```bash
# Replace main SFS dataset with TPS version
cp -r TPS_Dataset_20250831/SfS_pp/* /path/to/sfs_main/sfspreproc-docker/Dataset/SfS_pp/
```

## Comparison to Original NURBS Dataset:
- **Original**: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`
- **TPS Version**: `/data/gpfs/projects/punim2657/sfs_preprocessing/TPS_Dataset_20250831/SfS_pp/`

**Status**: Dataset ready except for missing breaklines
