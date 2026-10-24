#!/usr/bin/env python3
"""Ticket 290 Phase 3/4: finish the byte-difference record and update run.json.

Why: job 33748661 showed the two exported lanes have identical xyz + normals and differ only in the
7th column, which the exporter never initialises. Keep that as two quoted lines (numbers), delete the
two 5 KB exports (geometry), and leave run.json carrying the ticket's results.
"""
import hashlib
import json
import os
import subprocess

RUN = os.environ["RUN_DIR"]
OUT = os.path.join(RUN, "out")

line_a = "40.8228 32.5596 475.389 0.359796 -0.501863 -0.786562 4.20319e+08"
line_b = "40.8228 32.5596 475.389 0.359796 -0.501863 -0.786562 -4.18843e+09"

note = [
    "Ticket 290, job 33748661 - why two edge runs give different file md5s.",
    "",
    "Two edge stages from an identical Temp/Data (one mesh stage, tree copied):",
    "  lane 0: A 5347 B 5426 bytes; lane 1: A 6115 B 6206 bytes (B is n bytes larger = 1 per point line)",
    "  header: 15 lines each, byte-identical;  points: 79 / 91;  FIELDS x y z normal_x normal_y normal_z curvature",
    "  xyz: same order, bytewise-equal=True, max|dxyz| ordered = 0.000000",
    "  point set: equal after sorting=True; nearest-neighbour A->B and B->A max 0.000000 mean 0.000000 mm",
    "  normals: identical to the printed digit.",
    "",
    "The one difference is the 7th column (PCL's curvature slot), and it is a CONSTANT per file:",
    "",
    "  A line 16: " + line_a,
    "  B line 16: " + line_b,
    "",
    "Every point line of A carries 4.20319e+08 and every line of B carries -4.18843e+09. A value of that",
    "size is not a curvature (mm^-1 values here are of order 1e-2); it is stale heap content: the exporter",
    "never assigns the curvature field, so the byte written is whatever the cloud allocation last held,",
    "and the two processes held different garbage. That is also why B's lines are one character longer",
    "(-4.18843e+09 is one digit longer than 4.20319e+08).",
    "",
    "Consequence for every future verification: do NOT md5 an exported *_Breakline_*.pcd and conclude",
    "the run was not reproducible. Compare the xyz columns (or the scored numbers); the geometry is",
    "bit-identical, the unused 7th column is not. This also explains why ticket 288's pointwise",
    "max|dxyz| was 0.000000 across two separately built binaries.",
    "",
]
with open(os.path.join(OUT, "curvature_column.txt"), "w") as f:
    f.write("\n".join(note))

paths = [os.path.join(OUT, n) for n in ("cmpA_lane0.pcd", "cmpB_lane0.pcd")]
deleted = []
with open(os.path.join(OUT, "geometry.md5"), "a") as g:
    for p in paths:
        if os.path.exists(p):
            h = hashlib.md5(open(p, "rb").read()).hexdigest()
            g.write("%s  %s\n" % (h, p))
            deleted.append((p, h, os.path.getsize(p)))
            os.remove(p)

with open(os.path.join(OUT, "GEOMETRY_DELETED.txt"), "a") as f:
    for p, h, n in deleted:
        f.write("DELETED (after the byte diff was recorded in out/curvature_column.txt): %s md5 %s bytes %d\n"
                % (p, h, n))
    f.write("KEPT in its place: out/curvature_column.txt - two quoted data lines, not a lane.\n")

rj = os.path.join(RUN, "run.json")
d = json.load(open(rj))
d["results"] = {
    "ticket": "290 - frozen input corpus, one piece end to end",
    "inventory": {
        "verdict": "PASS",
        "released_rows": 143, "released_md5_mismatch": 0,
        "derived_rows": 5, "derived_md5_mismatch": 0,
        "scored_corpus": {"rows": 148, "pieces": 148, "files": 148,
                          "missing": 0, "duplicated": 0, "unaccounted": 0},
        "per_pot": {"A": 8, "B": 9, "C": 4, "D": 29, "E": 31, "F": 7, "G": 7, "H": 11, "I": 30, "J": 12},
        "encoding": {"binary": 143, "ascii": 5},
        "binary_fields": "normal_x normal_y normal_z x y z _",
        "ascii_fields": "x y z normal_x normal_y normal_z",
    },
    "symlink": {
        "read_through_a_symlink": True,
        "evidence": "POT_NAME=Pot_A with Dataset/Point a directory symlink: 'Copied Point file: "
                    "Pot_A_Piece_01_Point.pcd', '[DOWNSAMPLING RESTORE-244] input=999810 Result=85136'",
        "used_in_the_run": "file-level symlink Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd -> corpus",
        "caveat": "the dataset scan is recursive with no pot filter, so a whole-corpus directory "
                  "symlink makes the stage walk all 148 pieces",
    },
    "classify_line": [
        "[PAPER-234] classify: face0 n=4089 interior_frac=0.0000 face1 n=2880 interior_frac=1.0000 "
        "satA=0.0000 satB=6969.0000",
        "[PAPER-234] classify: swapped -> Surface_0=interior",
    ],
    "lanes": {
        "Bl0": {"n": 79, "median_mm": 1.079, "cov_ours_to_authors": 70.89, "cov_authors_to_ours": 75.68,
                "jumps": 0, "max_step_mm": 4.999, "len_mm": 145.40},
        "Bl1": {"n": 91, "median_mm": 1.913, "cov_ours_to_authors": 50.55, "cov_authors_to_ours": 63.77,
                "jumps": 0, "max_step_mm": 4.890, "len_mm": 166.89},
    },
    "verdict": "DROP-IN",
    "verdict_limits": [
        "Bl0 lands inside ticket 289's two draws on all four columns",
        "Bl1 is outside on n (91 vs 84-86) and median (1.913 vs 1.98-2.12); longer by 13.6 mm",
        "mechanism: the released cloud keeps the outliers our SOR removes (19% more points)",
    ],
    "reproducibility": {
        "mesh_stage_deterministic": True,
        "sheets_md5": ["32360b58ab00691cab6fefb04ffe2c04", "f9f3846e40b426292e685db862e9fb46"],
        "edge_scores_reproduce_exactly": True,
        "exported_files_byte_identical": False,
        "why": "the 7th (curvature) column is never initialised and carries stale heap bytes; xyz and "
               "normals are bit-identical - see out/curvature_column.txt",
    },
    "geometry": {
        "deleted": "out/lane*.pcd, out/surface_*.xyz, stage/, probe/, repeat/, cmp/, the node-local build tree",
        "kept": "run.json, submit*.sbatch, the scorers, logs/, out/*.txt, out/*.md5, out/png/, bin/",
        "record": "out/GEOMETRY_DELETED.txt + out/geometry.md5",
    },
    "picture": {
        "path": "out/png/p290_J09.png", "px": "1150x520", "bytes": 84928,
        "md5": "3577c62a134dd40e69810794973751c0",
        "laptop": "C:/PR/SfSpp_preprocessing/artifacts/pota290/png/p290_J09.png",
    },
}
d["status"] = "results-in; ticket written in the main clone, uncommitted"
json.dump(d, open(rj, "w"), indent=2, sort_keys=False)
print("[RUNJSON] keys=%s" % ",".join(sorted(d.keys())))
print("[DELETED] %s" % ", ".join("%s (%s)" % (os.path.basename(p), h) for p, h, n in deleted))
print(json.dumps(d["results"]["lanes"], indent=1))
