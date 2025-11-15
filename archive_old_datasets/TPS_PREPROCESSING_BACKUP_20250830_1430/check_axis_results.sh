#!/bin/bash

# Check results of parallel axis extraction
echo "=== CHECKING PARALLEL AXIS EXTRACTION RESULTS ==="

# Check how many pieces were generated
GENERATED_COUNT=$(find TPS_Output/Axes/ -name "Pot_A_Piece_*_Axis.xyz" 2>/dev/null | wc -l)
echo "Generated axis files: $GENERATED_COUNT/8"

if [ $GENERATED_COUNT -eq 8 ]; then
    echo "✅ All 8 pieces completed successfully!"
    
    echo ""
    echo "Generated files:"
    find TPS_Output/Axes/ -name "Pot_A_Piece_*_Axis.xyz" | sort
    
    echo ""
    echo "File sizes:"
    ls -lh TPS_Output/Axes/Pot_A_Piece_*_Axis.xyz
    
    echo ""
    echo "Copying to main SFS dataset..."
    cp TPS_Output/Axes/Pot_A_Piece_*_Axis.xyz /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/Dataset/SfS_pp/Axes/
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully copied all axis files to main SFS dataset"
        
        echo ""
        echo "Sample axis values:"
        for i in {1..8}; do
            if [ -f "TPS_Output/Axes/Pot_A_Piece_$(printf '%02d' $i)_Axis.xyz" ]; then
                echo "  Piece $(printf '%02d' $i): $(head -1 TPS_Output/Axes/Pot_A_Piece_$(printf '%02d' $i)_Axis.xyz)"
            fi
        done
        
    else
        echo "❌ Failed to copy axis files to main dataset"
        exit 1
    fi
    
else
    echo "⚠️  Only $GENERATED_COUNT/8 pieces completed"
    
    echo ""
    echo "Missing pieces:"
    for i in {1..8}; do
        FILE="TPS_Output/Axes/Pot_A_Piece_$(printf '%02d' $i)_Axis.xyz"
        if [ ! -f "$FILE" ]; then
            echo "  ❌ Missing: Piece $(printf '%02d' $i)"
        else
            echo "  ✅ Complete: Piece $(printf '%02d' $i)"
        fi
    done
    
    echo ""
    echo "Check job logs for errors:"
    echo "  ls -la logs/"
    
    exit 1
fi

echo ""
echo "=== PARALLEL AXIS EXTRACTION COMPLETE ==="