#!/bin/bash

# SFS Preprocessing Status Checker
# Usage: ./check_preprocessing_status.sh [POT_ID] [NUM_PIECES]
# Example: ./check_preprocessing_status.sh A 8

POT_ID="${1:-A}"
NUM_PIECES="${2:-8}"

echo "==============================================="
echo "SFS Preprocessing Status - Pot $POT_ID"
echo "==============================================="
echo "Checking pieces 1-$NUM_PIECES..."
echo ""

# Directories
PREPROCESSING_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
SFS_MAIN_DIR="/data/gpfs/projects/punim2657/sfs_main"
SURFACE_DIR="${PREPROCESSING_DIR}/Surfaces"
AXIS_DIR="${SFS_MAIN_DIR}/sfs_test_reconstruction/Dataset/SfS_pp/Axes"
BREAKLINE_DIR="${SFS_MAIN_DIR}/sfs_test_reconstruction/Dataset/SfS_pp/Breaklines/Pot_${POT_ID}"

echo "📁 Checking directories:"
echo "   Surfaces:   $SURFACE_DIR"
echo "   Axes:       $AXIS_DIR"
echo "   Breaklines: $BREAKLINE_DIR"
echo ""

# Status counters
surfaces_complete=0
axes_complete=0
breaklines_complete=0
total_expected=$NUM_PIECES

echo "📊 Processing Status:"
echo "Piece | Surfaces | Axis | Breaklines | Status"
echo "------|----------|------|------------|--------"

for i in $(seq 1 $NUM_PIECES); do
    piece_id=$(printf "%02d" $i)
    
    # Check surfaces (2 files expected)
    surface_0="${SURFACE_DIR}/Pot_${POT_ID}_Piece_${piece_id}_Surface_0.xyz"
    surface_1="${SURFACE_DIR}/Pot_${POT_ID}_Piece_${piece_id}_Surface_1.xyz"
    
    if [[ -f "$surface_0" && -f "$surface_1" ]]; then
        surface_status="✅ 2/2"
        ((surfaces_complete++))
    elif [[ -f "$surface_0" || -f "$surface_1" ]]; then
        surface_status="⚠️  1/2"
    else
        surface_status="❌ 0/2"
    fi
    
    # Check axis file
    axis_file="${AXIS_DIR}/Pot_${POT_ID}_Piece_${piece_id}_Axis.xyz"
    if [ -f "$axis_file" ]; then
        axis_status="✅"
        ((axes_complete++))
    else
        axis_status="❌"
    fi
    
    # Check breaklines (optional - some pieces may not have breaklines)
    breakline_files=$(ls "${BREAKLINE_DIR}"/Pot_${POT_ID}_Piece_${piece_id}*CompleteBreaklines* 2>/dev/null | wc -l)
    if [ $breakline_files -gt 0 ]; then
        breakline_status="✅ $breakline_files"
        ((breaklines_complete++))
    else
        breakline_status="⚪ 0"  # Gray circle for optional
    fi
    
    # Overall status
    if [[ -f "$surface_0" && -f "$surface_1" && -f "$axis_file" ]]; then
        overall_status="✅ Complete"
    else
        overall_status="❌ Incomplete"
    fi
    
    printf "  %2s  | %-8s | %-4s | %-10s | %s\n" "$piece_id" "$surface_status" "$axis_status" "$breakline_status" "$overall_status"
done

echo ""
echo "==============================================="
echo "📊 Summary:"
echo "   Surfaces Complete:   $surfaces_complete/$total_expected ($(( (surfaces_complete * 100) / total_expected ))%)"
echo "   Axes Complete:       $axes_complete/$total_expected ($(( (axes_complete * 100) / total_expected ))%)"
echo "   Breaklines Found:    $breaklines_complete/$total_expected ($(( (breaklines_complete * 100) / total_expected ))%) [optional]"
echo ""

if [ $surfaces_complete -eq $total_expected ] && [ $axes_complete -eq $total_expected ]; then
    echo "🎉 SUCCESS: All required preprocessing completed!"
    echo "Ready for SFS assembly testing"
    
    # Show file sizes and point counts
    echo ""
    echo "📊 File Statistics:"
    for i in $(seq 1 $NUM_PIECES); do
        piece_id=$(printf "%02d" $i)
        surface_0="${SURFACE_DIR}/Pot_${POT_ID}_Piece_${piece_id}_Surface_0.xyz"
        axis_file="${AXIS_DIR}/Pot_${POT_ID}_Piece_${piece_id}_Axis.xyz"
        
        if [[ -f "$surface_0" && -f "$axis_file" ]]; then
            points_0=$(wc -l < "$surface_0" 2>/dev/null || echo "0")
            points_1=$(wc -l < "${surface_0/_0.xyz/_1.xyz}" 2>/dev/null || echo "0")
            total_points=$((points_0 + points_1))
            
            axis_data=$(cat "$axis_file" 2>/dev/null || echo "")
            if [ -n "$axis_data" ]; then
                # Parse single-line format: direction[1-3] position[4-6]
                direction=$(echo $axis_data | awk '{print $1, $2, $3}')
                echo "   Piece $piece_id: ${total_points} points, axis direction [$direction]"
            fi
        fi
    done
    
    echo ""
    echo "🎯 Next step: Run SFS assembly test"
    echo "   cd $SFS_MAIN_DIR && ./run_sfs_test.sh"
    
elif [ $surfaces_complete -eq $total_expected ]; then
    echo "⚠️  Surfaces complete, but missing axes. Check MATLAB processing."
elif [ $axes_complete -eq $total_expected ]; then
    echo "⚠️  Axes complete, but missing surfaces. Check mesh processing."  
else
    echo "❌ Preprocessing incomplete. Missing both surfaces and axes."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check SLURM job status: squeue -u $USER"
    echo "2. Check log files: ls logs/*${POT_ID}*.log"
    echo "3. Resubmit failed jobs: ./submit_preprocessing_jobs.sh $POT_ID $NUM_PIECES"
fi

echo "==============================================="