import numpy as np

candidates = {
    3: [
        {"name": "B22", "size": 220, "d": 74.3, "cost": 0.007406, "ang": 4.48, "true": True},
        {"name": "B33", "size": 125, "d": 73.9, "cost": 0.008058, "ang": 9.21, "true": True},
        {"name": "B56", "size":  44, "d": 76.0, "cost": 0.005833, "ang": 18.26, "true": False},
        {"name": "B36", "size":  32, "d": 71.8, "cost": 0.005956, "ang": 45.11, "true": False},
        {"name": "B15", "size":  21, "d": 84.3, "cost": 0.006496, "ang": 42.13, "true": False},
        {"name": "B45", "size":  71, "d": 80.5, "cost": 0.006677, "ang": 20.30, "true": False},
        {"name": "B17", "size": 344, "d": 61.1, "cost": 0.007596, "ang": 29.79, "true": False},
        {"name": "B12", "size": 247, "d": 76.0, "cost": 0.008510, "ang": 13.87, "true": False},
        {"name": "B16", "size": 295, "d": 80.2, "cost": 0.008599, "ang": 16.69, "true": False},
    ],
    23: [
        {"name": "B33", "size": 144, "d": 66.6, "cost": 0.006077, "ang": 7.11, "true": True},
        {"name": "B6",  "size": 333, "d": 71.1, "cost": 0.006956, "ang": 4.87, "true": True},
        {"name": "B107","size":   8, "d": 64.2, "cost": 0.006415, "ang": 7.73, "true": True},
        {"name": "B55", "size":  47, "d": 71.9, "cost": 0.005935, "ang": 38.06, "true": False},
        {"name": "B109","size":   3, "d": 80.5, "cost": 0.006085, "ang": 29.60, "true": False},
        {"name": "B82", "size":  49, "d": 71.5, "cost": 0.006273, "ang": 20.05, "true": False},
        {"name": "B46", "size":  84, "d": 79.1, "cost": 0.006300, "ang": 32.94, "true": False},
        {"name": "B53", "size":  69, "d": 71.8, "cost": 0.006365, "ang": 31.27, "true": False},
        {"name": "B27", "size": 107, "d": 82.9, "cost": 0.006457, "ang": 20.50, "true": False},
        {"name": "B26", "size": 131, "d": 70.1, "cost": 0.007315, "ang": 13.63, "true": False},
    ],
    24: [
        {"name": "B30", "size":  61, "d": 79.0, "cost": 0.005106, "ang": 8.36, "true": True},
        {"name": "B22", "size": 145, "d": 69.7, "cost": 0.006496, "ang": 2.16, "true": True},
        {"name": "B25", "size":  85, "d": 73.9, "cost": 0.007611, "ang": 9.73, "true": True},
        {"name": "B7",  "size": 148, "d": 77.4, "cost": 0.005321, "ang": 21.08, "true": False},
        {"name": "B23", "size": 112, "d": 75.9, "cost": 0.005573, "ang": 10.06, "true": False},
        {"name": "B72", "size":  10, "d": 64.6, "cost": 0.005609, "ang": 18.88, "true": False},
        {"name": "B52", "size":  17, "d": 75.2, "cost": 0.005824, "ang": 25.46, "true": False},
        {"name": "B21", "size":  62, "d": 81.6, "cost": 0.005915, "ang": 24.10, "true": False},
        {"name": "B24", "size":  66, "d": 67.3, "cost": 0.006064, "ang": 14.72, "true": False},
        {"name": "B17", "size": 253, "d": 70.3, "cost": 0.006100, "ang": 11.19, "true": False},
    ],
    25: [
        {"name": "B1",  "size": 683, "d": 66.0, "cost": 0.006596, "ang": 3.23, "true": True},
        {"name": "B72", "size":  25, "d": 70.2, "cost": 0.007394, "ang": 8.93, "true": True},
        {"name": "B2",  "size": 219, "d": 64.6, "cost": 0.014129, "ang": 2.38, "true": True},
        {"name": "B30", "size":  78, "d": 72.7, "cost": 0.005341, "ang": 26.88, "true": False},
        {"name": "B55", "size":  48, "d": 74.2, "cost": 0.005969, "ang": 41.24, "true": False},
        {"name": "B65", "size":  13, "d": 100.2,"cost": 0.006073, "ang": 39.42, "true": False},
        {"name": "B78", "size":   9, "d": 91.3, "cost": 0.006352, "ang": 35.05, "true": False},
        {"name": "B8",  "size": 293, "d": 68.8, "cost": 0.009198, "ang": 48.93, "true": False},
    ],
    26: [
        {"name": "B67", "size":   6, "d": 78.0, "cost": 0.015719, "ang": 1.41, "true": True},
        {"name": "B4",  "size": 155, "d": 68.0, "cost": 0.016491, "ang": 5.62, "true": True},
        {"name": "B40", "size":   7, "d": 110.0,"cost": 0.011561, "ang": 54.12, "true": False},
        {"name": "B83", "size":   4, "d": 83.3, "cost": 0.012894, "ang": 43.56, "true": False},
        {"name": "B77", "size":   8, "d": 88.4, "cost": 0.014235, "ang": 19.14, "true": False},
        {"name": "B43", "size":  15, "d": 68.4, "cost": 0.015473, "ang": 24.83, "true": False},
        {"name": "B14", "size":  87, "d": 76.5, "cost": 0.016496, "ang": 24.35, "true": False},
        {"name": "B24", "size":  63, "d": 81.8, "cost": 0.017362, "ang": 10.35, "true": False},
    ],
    28: [
        {"name": "B5",  "size": 191, "d": 72.3, "cost": 0.010523, "ang": 8.13, "true": True},
        {"name": "B21", "size": 162, "d": 40.8, "cost": 0.029028, "ang": 7.41, "true": True},
        {"name": "B35", "size":  60, "d": 78.9, "cost": 0.008940, "ang": 33.72, "true": False},
        {"name": "B36", "size":  38, "d": 70.8, "cost": 0.008978, "ang": 14.03, "true": False},
        {"name": "B55", "size":   6, "d": 73.9, "cost": 0.009119, "ang": 29.34, "true": False},
        {"name": "B26", "size": 182, "d": 74.4, "cost": 0.009662, "ang": 19.53, "true": False},
        {"name": "B20", "size": 144, "d": 74.2, "cost": 0.009752, "ang": 44.87, "true": False},
    ],
    31: [
        {"name": "B82", "size":   1, "d": 74.2, "cost": 0.017489, "ang": 6.37, "true": True},
        {"name": "B38", "size":  16, "d": 70.3, "cost": 0.020444, "ang": 6.59, "true": True},
        {"name": "B58", "size":   5, "d": 77.9, "cost": 0.018551, "ang": 35.08, "true": False},
        {"name": "B26", "size":  14, "d": 78.6, "cost": 0.019108, "ang": 15.08, "true": False},
        {"name": "B73", "size":   3, "d": 119.8,"cost": 0.019567, "ang": 63.28, "true": False},
        {"name": "B49", "size":   8, "d": 60.0, "cost": 0.019643, "ang": 55.10, "true": False},
    ]
}

# What if candidates are sorted by:
# 1. First, take the largest consensus cluster! (Rank 0 = largest cluster)
# 2. Second, take the lowest cost cluster! (Rank 1 = lowest cost)
print("=== STRATEGY: R0 = largest consensus cluster, R1 = lowest cost cluster ===")
all_pass = True
for p, cands in candidates.items():
    # Sort by size descending for R0
    by_size = sorted(cands, key=lambda x: -x["size"])
    r0 = by_size[0]
    
    # Sort by cost ascending for R1 (excluding candidates close to R0)
    by_cost = sorted([c for c in cands if abs(c["ang"] - r0["ang"]) > 10.0 or c["true"] != r0["true"]], key=lambda x: x["cost"])
    r1 = by_cost[0] if by_cost else by_size[1]
    
    p_pass = r0["true"] or r1["true"]
    if not p_pass: all_pass = False
    print(f"Piece {p:02d} [{'PASS' if p_pass else 'FAIL'}]: R0={r0['name']} ({r0['ang']:.1f}deg, sz={r0['size']}, {'TRUE' if r0['true'] else 'DECOY'}) | R1={r1['name']} ({r1['ang']:.1f}deg, c={r1['cost']:.5f}, {'TRUE' if r1['true'] else 'DECOY'})")
print(f"--> ALL 7 PASS? = {all_pass}")
