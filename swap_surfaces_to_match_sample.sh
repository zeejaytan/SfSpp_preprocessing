#!/bin/bash
# Swap Surface_0 and Surface_1 to match sample dataset convention
# Sample convention: Surface_0 = inner surface (negative Z normals)
#                    Surface_1 = outer surface (positive Z normals)

SURFACES_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Surfaces/Pot_A"
TEMP_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing/Temp/Data/Pot_A"

echo "=== Swapping Surface Labels to Match Sample Convention ==="
echo ""

for piece in 01 02 03 04 05 06 07 08; do
    echo "Processing Piece ${piece}..."

    S0_XYZ="${SURFACES_DIR}/Pot_A_Piece_${piece}_Surface_0.xyz"
    S1_XYZ="${SURFACES_DIR}/Pot_A_Piece_${piece}_Surface_1.xyz"
    S0_PLY="${TEMP_DIR}/Pot_A_Piece_${piece}_Surface_0.ply"
    S1_PLY="${TEMP_DIR}/Pot_A_Piece_${piece}_Surface_1.ply"

    # Check if current S0 has positive Z normals (outer) - needs to become S1
    # Get average Z normal from first few points
    if [ -f "$S0_XYZ" ]; then
        AVG_Z=$(head -20 "$S0_XYZ" | awk '{sum+=$6; count++} END {print sum/count}')
        echo "  Current S0 avg Z normal: $AVG_Z"

        # If S0 has positive Z normals (outer surface), swap with S1
        IS_POSITIVE=$(echo "$AVG_Z > 0" | bc -l)

        if [ "$IS_POSITIVE" -eq 1 ]; then
            echo "  S0 is outer surface (positive Z) - swapping to match sample..."

            # Swap XYZ files
            mv "$S0_XYZ" "${S0_XYZ}.tmp"
            mv "$S1_XYZ" "$S0_XYZ"
            mv "${S0_XYZ}.tmp" "$S1_XYZ"

            # Swap PLY files if they exist
            if [ -f "$S0_PLY" ] && [ -f "$S1_PLY" ]; then
                mv "$S0_PLY" "${S0_PLY}.tmp"
                mv "$S1_PLY" "$S0_PLY"
                mv "${S0_PLY}.tmp" "$S1_PLY"
            fi

            echo "  ✓ Swapped S0 <-> S1"
        else
            echo "  S0 already inner surface (negative Z) - no swap needed"
        fi
    else
        echo "  WARNING: $S0_XYZ not found"
    fi
    echo ""
done

echo "=== Swap Complete ==="
echo ""
echo "Verifying new labels..."
for piece in 01 02 03 04 05 06 07 08; do
    S0="${SURFACES_DIR}/Pot_A_Piece_${piece}_Surface_0.xyz"
    S1="${SURFACES_DIR}/Pot_A_Piece_${piece}_Surface_1.xyz"

    if [ -f "$S0" ] && [ -f "$S1" ]; then
        Z0=$(head -20 "$S0" | awk '{sum+=$6; count++} END {printf "%.3f", sum/count}')
        Z1=$(head -20 "$S1" | awk '{sum+=$6; count++} END {printf "%.3f", sum/count}')
        echo "Piece ${piece}: S0 Z=${Z0} (should be negative/inner), S1 Z=${Z1} (should be positive/outer)"
    fi
done
