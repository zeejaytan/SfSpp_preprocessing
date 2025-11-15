# 🔧 SfS Preprocessing Test Plan

## 📊 **Current Status**

### ✅ **Completed:**
- **Downloaded dataset**: Raw mesh files for Pot_A through Pot_J (142 total fragments)
- **POT_A focus**: 8 mesh pieces matching our working main SfS system
- **Container definition**: Created Apptainer-compatible build file
- **Build job submitted**: SLURM job #14425014 building container

### 🔄 **In Progress:**
- **Container build**: PCL 1.9.1 + CGAL 5.0 + VTK 8.1.2 (1-3 hours)

## 🎯 **Preprocessing Pipeline Overview**

### **Input → Output Data Flow:**
```
Raw Mesh (.obj) 
    ↓
Step 1: MeshPreprocessing → Point Clouds + Surfaces
    ↓  
Step 2: EdgeLineExtraction → Breaklines
    ↓
Step 3: AxisExtraction (MATLAB) → Axis Files
    ↓
Main SfS System → Pottery Reconstruction
```

### **Detailed Process:**
1. **Mesh → Surface Processing**:
   - `./MeshPreprocessing` 
   - Input: `Dataset/Mesh/Pot_A/*.obj`
   - Output: `*_SampledWithNormals.ply`, `*_Surface_X.xyz`

2. **Surface → Breakline Processing**:
   - `./EdgeLineExtraction`
   - Input: Surface files from step 1
   - Output: `*_CompleteBreaklines.xyz`

3. **Axis Extraction** (MATLAB):
   - `preprocess_new_pots.m`
   - Input: Surface and breakline data
   - Output: `*_Axis.xyz`

## 🧪 **Test Sequence**

### **Phase 1: Container Verification (when build completes)**
```bash
# Test container functionality
apptainer exec sfs_preprocessing.sif /bin/bash -c "
    echo 'Testing dependencies...'
    pkg-config --modversion pcl_common
    find /usr/local -name '*cgal*' | head -5
    find /usr/local -name '*vtk*' | head -5
"
```

### **Phase 2: Build Preprocessing Tools**
```bash
# Inside container
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
# Should create: MeshPreprocessing, EdgeLineExtraction
```

### **Phase 3: Test Mesh Processing (Pot_A)**
```bash
# Run mesh processing on Pot_A (matches main SfS system)
apptainer exec --bind $(pwd):/workspace sfs_preprocessing.sif /bin/bash -c "
    cd /workspace/build
    ./MeshPreprocessing
"
```

### **Phase 4: Test Breakline Extraction**
```bash
# Run edge line extraction 
apptainer exec --bind $(pwd):/workspace sfs_preprocessing.sif /bin/bash -c "
    cd /workspace/build  
    ./EdgeLineExtraction
"
```

### **Phase 5: Data Format Integration**
```bash
# Check output formats match main SfS expectations
ls Dataset/Surfaces/Pot_A/
ls Dataset/Breaklines/Pot_A/
# Compare with: /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/Dataset/SfS_pp/
```

## 📋 **Expected Outputs**

### **For Pot_A (8 pieces):**
```
Dataset/
├── Surfaces/Pot_A/
│   ├── Pot_A_Piece_01_Surface_0.xyz
│   ├── Pot_A_Piece_01_Surface_1.xyz
│   ├── ...
│   └── Pot_A_Piece_08_Surface_X.xyz
├── Breaklines/Pot_A/  
│   ├── Pot_A_Piece_01_CompleteBreaklines.xyz
│   ├── ...
│   └── Pot_A_Piece_08_CompleteBreaklines.xyz
└── Axes/Pot_A/ (from MATLAB step)
    ├── Pot_A_Piece_01_Axis.xyz
    ├── ...
    └── Pot_A_Piece_08_Axis.xyz
```

## 🔄 **Format Conversion for Main SfS**

The main SfS system expects:
- **Breaklines**: `.pcd` format (not `.xyz`)
- **Surfaces**: `.xyz` format ✓
- **Axes**: `.xyz` format ✓

**Conversion needed:**
```bash
# Convert breaklines from .xyz to .pcd format
pcl_convert_pcd_ascii_binary input.xyz output.pcd 0
```

## ⚡ **Quick Test Script**

Create automated test when container is ready:

```bash
#!/bin/bash
# test_preprocessing_pipeline.sh

echo "=== Testing SfS Preprocessing Pipeline ==="

# Phase 1: Container test
echo "Testing container..."
apptainer exec sfs_preprocessing.sif echo "Container OK"

# Phase 2: Build tools
echo "Building preprocessing tools..."  
apptainer exec --bind $(pwd):/workspace sfs_preprocessing.sif /bin/bash -c "
    cd /workspace
    mkdir -p build && cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j4
"

# Phase 3: Run on single Pot_A piece (test)
echo "Testing on Pot_A_Piece_01..."
# ... processing commands ...

echo "Preprocessing test complete!"
```

## 🎯 **Success Criteria**

1. **Container builds successfully** (dependencies: PCL, CGAL, VTK)
2. **Tools compile without errors** (MeshPreprocessing, EdgeLineExtraction)  
3. **Pot_A processing completes** (matches existing 8-piece dataset)
4. **Output format compatibility** (convertible to main SfS format)
5. **Integration test passes** (preprocessed data works in main SfS)

## 📞 **Next Actions When Container Ready**

1. **Check build status**: `squeue -u $USER`
2. **Test container**: Run Phase 1 verification
3. **Build tools**: Compile preprocessing executables
4. **Run Pot_A test**: Process first pottery fragment
5. **Verify integration**: Test with main SfS system

**Estimated time remaining for container build: 30-120 minutes** ⏰