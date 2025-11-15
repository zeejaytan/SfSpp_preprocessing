#!/bin/bash

# MATLAB Axis Extraction Wrapper for SFS Preprocessing
# Usage: ./matlab_axis_wrapper.sh <pot_id> <frag_id> [extended]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <pot_id> <frag_id> [extended]"
    echo "Example: $0 A 1"
    exit 1
fi

POT_ID="$1"
FRAG_ID="$2"
EXTENDED="${3:-false}"

echo "🎯 Running MATLAB axis extraction for Pot $POT_ID, Fragment $FRAG_ID"

# Load MATLAB module
module load MATLAB/2024b_Update_3

# Set MATLAB paths
MATLAB_SCRIPT_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction"
OUTPUT_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/axis_output"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create a unique MATLAB command file per task to avoid races
SCRIPT_NAME="run_axis_extraction_${POT_ID}_${FRAG_ID}.m"
cat > "$SCRIPT_NAME" << MATLAB_EOF
% Add AxisExtraction directory to path
addpath('$MATLAB_SCRIPT_DIR');

% Set output directory
output_dir = '$OUTPUT_DIR';

% Run axis extraction
try
    fprintf('Starting axis extraction for Pot %s, Fragment %d\\n', '$POT_ID', $FRAG_ID);
    
    % Call the main axis extraction function
    vt = extract_axis('$POT_ID', $FRAG_ID, $EXTENDED);
    
    % Save results
    output_file = sprintf('%s/Pot_%s_Piece_%02d_Axis.txt', output_dir, '$POT_ID', $FRAG_ID);
    writematrix(vt, output_file, 'Delimiter', ' ');
    
    fprintf('✅ Axis extraction completed successfully\\n');
    fprintf('📁 Results saved to: %s\\n', output_file);
    fprintf('🎯 Found %d axes\\n', size(vt, 2));
    
    % Display best axis
    if size(vt, 2) > 0
        fprintf('Best axis - Direction: [%.6f, %.6f, %.6f]\\n', vt(1,1), vt(2,1), vt(3,1));
        fprintf('Best axis - Position:  [%.6f, %.6f, %.6f]\\n', vt(4,1), vt(5,1), vt(6,1));
    end
    
    exit(0);
catch ME
    fprintf('❌ Error in axis extraction: %s\\n', ME.message);
    exit(1);
end
MATLAB_EOF

# Run MATLAB (robust, task-unique script)
echo "🔄 Starting MATLAB axis extraction..."
matlab -nodisplay -nosplash -nodesktop \
  -logfile "matlab_axis_${POT_ID}_${FRAG_ID}.log" \
  -r "try, run('${SCRIPT_NAME}'); catch ME, disp(getReport(ME)); exit(1); end; exit(0);"

MATLAB_EXIT_CODE=$?

# Check results
if [ $MATLAB_EXIT_CODE -eq 0 ]; then
    RESULT_FILE="$OUTPUT_DIR/Pot_${POT_ID}_Piece_$(printf '%02d' $FRAG_ID)_Axis.txt"
    if [ -f "$RESULT_FILE" ]; then
        echo "✅ MATLAB axis extraction successful!"
        echo "📁 Results: $RESULT_FILE"
        echo "📊 Axis data:"
        head -3 "$RESULT_FILE" 2>/dev/null || echo "   (Could not preview results)"
    else
        echo "⚠️  MATLAB completed but no output file found"
        exit 1
    fi
else
    echo "❌ MATLAB axis extraction failed (exit code: $MATLAB_EXIT_CODE)"
    echo "📋 Check log: matlab_axis_${POT_ID}_${FRAG_ID}.log"
    exit 1
fi

# Clean up temporary files
rm -f "$SCRIPT_NAME"

echo "🎉 MATLAB axis extraction completed!"
