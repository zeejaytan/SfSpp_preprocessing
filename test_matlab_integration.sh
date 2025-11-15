#!/bin/bash

echo "=== Testing MATLAB Integration ==="

# Test MATLAB availability
echo "🔍 Testing MATLAB availability..."
module load MATLAB/2024b_Update_3
matlab -nodisplay -nosplash -nodesktop -r "fprintf('MATLAB is working!\n'); exit(0);" -logfile test_matlab.log

if [ $? -eq 0 ]; then
    echo "✅ MATLAB is working correctly"
else
    echo "❌ MATLAB test failed"
    exit 1
fi

# Test with sample data (if available)
echo ""
echo "🧪 Testing axis extraction with sample data..."

# Check if we have sample surface data
SAMPLE_SURFACE_0="/data/gpfs/projects/punim2657/sfs_preprocessing/test_output/test_single/Surfaces/Pot_A_Piece_01_Surface_0.xyz"
SAMPLE_SURFACE_1="/data/gpfs/projects/punim2657/sfs_preprocessing/test_output/test_single/Surfaces/Pot_A_Piece_01_Surface_1.xyz"

if [ -f "$SAMPLE_SURFACE_0" ] && [ -f "$SAMPLE_SURFACE_1" ]; then
    echo "✅ Found sample surface data, running full test..."
    ./integrated_preprocessing_with_matlab.sh A 1
else
    echo "⚠️  No sample surface data found, skipping full test"
    echo "   Generate surface data first using the C++ preprocessing pipeline"
fi

echo ""
echo "🎉 MATLAB integration test completed!"
