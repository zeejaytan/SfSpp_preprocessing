#!/bin/bash
# Test complete preprocessing pipeline on all Pot A pieces

echo "=== Testing Complete Preprocessing Pipeline on All Pot A Pieces ==="
echo "🏺 Found 8 pieces in Pot A"
echo ""

# Initialize counters
TOTAL_PIECES=8
SUCCESSFUL_PIECES=0
FAILED_PIECES=0

# Arrays to track results
SUCCESSFUL_LIST=()
FAILED_LIST=()

echo "📁 Cleaning previous results..."
rm -rf Surfaces/Pot_A_Piece_*_Surface_*.xyz
rm -rf axis_output/Pot_A_Piece_*_Axis.txt

echo ""
echo "🔄 Starting batch processing..."
echo ""

for piece_id in {01..08}; do
    echo "=========================================="
    echo "🏺 Processing Pot A Piece ${piece_id}"
    echo "=========================================="
    
    MESH_FILE="Dataset/Mesh/Pot_A/Pot_A_Piece_${piece_id}_Mesh.obj"
    
    # Check if mesh file exists
    if [ ! -f "$MESH_FILE" ]; then
        echo "❌ Mesh file not found: $MESH_FILE"
        FAILED_PIECES=$((FAILED_PIECES + 1))
        FAILED_LIST+=("Piece_${piece_id}: Mesh file missing")
        continue
    fi
    
    echo "📁 Input mesh: $MESH_FILE"
    
    # Step 1: C++ Surface Processing
    echo ""
    echo "🔧 Step 1: C++ Surface Processing"
    
    # Use container for processing
    /apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer exec \
        --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
        --bind /tmp:/tmp \
        --workdir /workspace \
        sfs_preprocessing_working.sif \
        /bin/bash -c "
            export DISPLAY=
            cd /workspace
            echo 'Running mesh processing for Pot_A_Piece_${piece_id}...'
            timeout 300 ./mesh_processing_complete Dataset/Mesh/Pot_A/Pot_A_Piece_${piece_id}_Mesh.obj A ${piece_id}
        "
    
    MESH_RESULT=$?
    
    if [ $MESH_RESULT -ne 0 ]; then
        echo "❌ C++ surface processing failed for Piece ${piece_id}"
        FAILED_PIECES=$((FAILED_PIECES + 1))
        FAILED_LIST+=("Piece_${piece_id}: C++ processing failed")
        continue
    fi
    
    # Check if surface files were generated  
    SURFACE_0="Surfaces/Pot_A_Piece_${piece_id}_Surface_0.xyz"
    SURFACE_1="Surfaces/Pot_A_Piece_${piece_id}_Surface_1.xyz"
    
    if [ ! -f "$SURFACE_0" ] || [ ! -f "$SURFACE_1" ]; then
        echo "❌ Surface files not generated for Piece ${piece_id}"
        FAILED_PIECES=$((FAILED_PIECES + 1))
        FAILED_LIST+=("Piece_${piece_id}: Surface files missing")
        continue
    fi
    
    # Get surface file sizes
    SURFACE_0_SIZE=$(wc -l < "$SURFACE_0" 2>/dev/null || echo "0")
    SURFACE_1_SIZE=$(wc -l < "$SURFACE_1" 2>/dev/null || echo "0")
    
    echo "✅ Surface files generated:"
    echo "   📁 $SURFACE_0 ($SURFACE_0_SIZE points)"
    echo "   📁 $SURFACE_1 ($SURFACE_1_SIZE points)"
    
    # Step 2: MATLAB Axis Extraction
    echo ""
    echo "🎯 Step 2: MATLAB Axis Extraction"
    
    module load MATLAB
    
    matlab -nodisplay -nosplash -r "
        try
            fprintf('🎯 Starting axis extraction for Pot A Piece ${piece_id}\n');
            cd('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');
            
            % Extract axis
            vt = extract_axis('A', ${piece_id#0}, false);
            
            if size(vt, 2) >= 1
                axis_dir = vt(1:3, 1);
                axis_pos = vt(4:6, 1);
                
                % Save axis to file
                axis_file = sprintf('/data/gpfs/projects/punim2657/sfs_preprocessing/axis_output/Pot_A_Piece_%02d_Axis.txt', ${piece_id#0});
                
                % Create output directory if it doesn't exist
                [axis_dir_path, ~, ~] = fileparts(axis_file);
                if ~exist(axis_dir_path, 'dir')
                    mkdir(axis_dir_path);
                end
                
                % Write axis data
                fid = fopen(axis_file, 'w');
                fprintf(fid, '%.12f\n', axis_dir(1));
                fprintf(fid, '%.12f\n', axis_dir(2));
                fprintf(fid, '%.12f\n', axis_dir(3));
                fprintf(fid, '%.12f\n', axis_pos(1));
                fprintf(fid, '%.12f\n', axis_pos(2));
                fprintf(fid, '%.12f\n', axis_pos(3));
                fclose(fid);
                
                fprintf('✅ Axis extraction successful for Piece ${piece_id}\n');
                fprintf('📁 Results saved to: %s\n', axis_file);
                fprintf('🎯 Axis direction: [%.6f, %.6f, %.6f]\n', axis_dir(1), axis_dir(2), axis_dir(3));
                fprintf('🎯 Axis position:  [%.6f, %.6f, %.6f]\n', axis_pos(1), axis_pos(2), axis_pos(3));
                
                exit(0);
            else
                fprintf('❌ No axes extracted for Piece ${piece_id}\n');
                exit(1);
            end
        catch ME
            fprintf('❌ MATLAB axis extraction failed for Piece ${piece_id}: %s\n', ME.message);
            exit(1);
        end
    " 2>/dev/null
    
    MATLAB_RESULT=$?
    
    if [ $MATLAB_RESULT -ne 0 ]; then
        echo "❌ MATLAB axis extraction failed for Piece ${piece_id}"
        FAILED_PIECES=$((FAILED_PIECES + 1))
        FAILED_LIST+=("Piece_${piece_id}: MATLAB processing failed")
        continue
    fi
    
    # Check if axis file was generated
    AXIS_FILE="axis_output/Pot_A_Piece_${piece_id}_Axis.txt"
    
    if [ ! -f "$AXIS_FILE" ]; then
        echo "❌ Axis file not generated for Piece ${piece_id}"
        FAILED_PIECES=$((FAILED_PIECES + 1))
        FAILED_LIST+=("Piece_${piece_id}: Axis file missing")
        continue
    fi
    
    AXIS_LINES=$(wc -l < "$AXIS_FILE" 2>/dev/null || echo "0")
    
    if [ "$AXIS_LINES" -ne 6 ]; then
        echo "❌ Invalid axis file format for Piece ${piece_id} (expected 6 lines, got $AXIS_LINES)"
        FAILED_PIECES=$((FAILED_PIECES + 1))
        FAILED_LIST+=("Piece_${piece_id}: Invalid axis format")
        continue
    fi
    
    echo "✅ Complete preprocessing successful for Piece ${piece_id}"
    echo "📁 Axis file: $AXIS_FILE (6 values)"
    
    SUCCESSFUL_PIECES=$((SUCCESSFUL_PIECES + 1))
    SUCCESSFUL_LIST+=("Piece_${piece_id}")
    echo ""
done

echo ""
echo "=========================================="
echo "🏆 BATCH PROCESSING COMPLETE"
echo "=========================================="
echo ""
echo "📊 Results Summary:"
echo "   Total pieces:      $TOTAL_PIECES"
echo "   Successful:        $SUCCESSFUL_PIECES"
echo "   Failed:            $FAILED_PIECES"
echo "   Success rate:      $(( SUCCESSFUL_PIECES * 100 / TOTAL_PIECES ))%"
echo ""

if [ $SUCCESSFUL_PIECES -gt 0 ]; then
    echo "✅ Successful pieces:"
    for piece in "${SUCCESSFUL_LIST[@]}"; do
        echo "   - $piece"
    done
    echo ""
fi

if [ $FAILED_PIECES -gt 0 ]; then
    echo "❌ Failed pieces:"
    for failure in "${FAILED_LIST[@]}"; do
        echo "   - $failure"
    done
    echo ""
fi

echo "📁 Generated Files:"
echo "Surface files:"
ls -la Surfaces/Pot_A_Piece_*_Surface_*.xyz 2>/dev/null | head -10
echo ""
echo "Axis files:"
ls -la axis_output/Pot_A_Piece_*_Axis.txt 2>/dev/null

echo ""
if [ $SUCCESSFUL_PIECES -eq $TOTAL_PIECES ]; then
    echo "🎉 ALL POT A PIECES PROCESSED SUCCESSFULLY!"
    echo "🎯 Complete preprocessing pipeline is working perfectly!"
elif [ $SUCCESSFUL_PIECES -gt 0 ]; then
    echo "⚠ PARTIAL SUCCESS - Some pieces processed successfully"
    echo "🔧 May need investigation for failed pieces"
else
    echo "❌ NO PIECES PROCESSED SUCCESSFULLY"
    echo "🔧 Pipeline needs debugging"
fi

echo ""
echo "=== Batch Processing Finished ==="