#!/bin/bash
# Generate TPS-compatible breaklines from mesh files
# Uses edgeline_extraction in container environment

set -e

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
CONTAINER="cache/sfs_prep_base.sif"
DATASET_DIR="TPS_Dataset_20250829"
BASE_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

echo "=== Generating TPS Breaklines ==="
echo "Container: $CONTAINER"
echo "Dataset: $DATASET_DIR"
echo "Start time: $(date)"
echo

cd "$BASE_DIR"

# Check if container exists
if [ ! -f "$CONTAINER" ]; then
    echo "❌ Container not found: $CONTAINER"
    echo "Available containers:"
    ls -la cache/*.sif
    exit 1
fi

# Check if dataset exists
if [ ! -d "$DATASET_DIR" ]; then
    echo "❌ Dataset not found: $DATASET_DIR"
    echo "Run organize_dataset.sh first"
    exit 1
fi

# Process each mesh file
for piece in {01..08}; do
    MESH_FILE="${DATASET_DIR}/SfS_pp/Mesh/Pot_A_Piece_${piece}_Mesh.obj"
    
    if [ -f "$MESH_FILE" ]; then
        echo "Processing piece $piece..."
        echo "  Input: $MESH_FILE"
        
        # Run edgeline extraction in container
        $CONTAINER_PATH exec \
            --bind "${BASE_DIR}:${BASE_DIR}" \
            "$CONTAINER" \
            /bin/bash -c "
                cd '${BASE_DIR}' && 
                echo 'Running edgeline extraction for piece $piece...' &&
                timeout 300 ./build/edgeline_extraction '$MESH_FILE' || {
                    echo 'Edgeline extraction failed or timed out for piece $piece'
                    exit 1
                }
            "
        
        # Check for generated breakline files
        BREAKLINE_0="Pot_A_Piece_${piece}_Breakline_0.pcd"
        BREAKLINE_1="Pot_A_Piece_${piece}_Breakline_1.pcd"
        
        if [ -f "$BREAKLINE_0" ]; then
            mv "$BREAKLINE_0" "${DATASET_DIR}/SfS_pp/Breaklines/"
            echo "  ✅ Generated: $BREAKLINE_0"
        fi
        
        if [ -f "$BREAKLINE_1" ]; then
            mv "$BREAKLINE_1" "${DATASET_DIR}/SfS_pp/Breaklines/"
            echo "  ✅ Generated: $BREAKLINE_1"
        fi
        
        echo "  Completed piece $piece"
        echo
    else
        echo "❌ Mesh file not found: $MESH_FILE"
    fi
done

# Update dataset documentation
BREAKLINE_COUNT=$(ls ${DATASET_DIR}/SfS_pp/Breaklines/*.pcd 2>/dev/null | wc -l)

echo "=== Breakline Generation Complete ==="
echo "Generated breaklines: $BREAKLINE_COUNT files"
echo "Location: ${DATASET_DIR}/SfS_pp/Breaklines/"

if [ $BREAKLINE_COUNT -gt 0 ]; then
    echo "✅ TPS breaklines successfully generated"
    echo "📁 Breakline files:"
    ls -la "${DATASET_DIR}/SfS_pp/Breaklines/"/*.pcd
    
    # Update README to reflect completion
    cat > "${DATASET_DIR}/SfS_pp/Breaklines/README.md" << EOF
# TPS Breaklines - Generated

**Status**: Successfully generated from mesh files
**Generated**: $(date)
**Method**: Edgeline extraction in container environment
**Files**: $BREAKLINE_COUNT breakline files

**Generated Files**:
$(ls ${DATASET_DIR}/SfS_pp/Breaklines/*.pcd | xargs -I {} basename {} | sed 's/^/- /')

**Ready for SFS integration**: Yes
EOF
    
    echo "📝 Updated breaklines documentation"
else
    echo "❌ No breaklines were generated - check errors above"
fi

echo "End time: $(date)"