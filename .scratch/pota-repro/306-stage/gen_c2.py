#!/usr/bin/env python3
"""gen_c2.py -- ticket 306 Stage C2: build the 305-grid re-run spec.

Every scorable pot except A (C1 covers A), OO and MM arms, 2 repeats
(3 on the small pots C, F, G), authors' axes as the in-job control (OO).
usage: gen_c2.py <AXDIR> <UTCSTAMP>
"""
import json, sys

AXDIR = sys.argv[1]
TS = sys.argv[2]
LANES = {
 "B": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-b2/out/geom",
 "C": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-c2/out/geom",
 "D": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-d2/out/geom",
 "E": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2/out/geom",
 "F": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0520_9c5eec2_t305-lane-f3/out/geom",
 "G": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-g2/out/geom",
 "I": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0520_9c5eec2_t305-lane-i3/out/geom",
 "J": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0520_9c5eec2_t305-lane-j3/out/geom",
}
# named/np from the ticket-305 e2e runs (same values, so the grid is comparable)
NAMED = {"B": "9", "C": "4", "D": "29", "E": "31", "F": "7", "G": "7", "I": "30", "J": "12"}
NP = {"B": "9", "C": "4", "D": "29", "E": "31", "F": "7", "G": "7", "I": "30", "J": "19"}
SMALL = ("C", "F", "G")

spec = []
for k, pot in enumerate(sorted(LANES)):
    reps = 3 if pot in SMALL else 2
    spec.append({
        "runid": "%s_c333dc7_t306c2-pot%s" % (TS, pot.lower()),
        "template": "e2e305.sbatch",
        "subs": {
            "POT": pot, "NAMED": NAMED[pot], "NP": NP[pot], "FLOOR": "50",
            "ARMSPEC": "OO:%d MM:%d" % (reps, reps),
            "NOTRUNC": "NONE", "LANES": LANES[pot], "AXDIR": AXDIR,
            "COMMIT": "c333dc7", "TAG": "t306c2-pot%s" % pot.lower(),
        },
        "envs": [],
        "helpers": ["C:/PR/worktrees/sfs/306/.scratch/pota-repro/306-stage/c1_helpers/arm67.sh",
                    "patch_guard67.py", "mk_inc.py", "stage305.py", "acc305.py", "score305.py"],
    })
json.dump(spec, open(sys.argv[3] if len(sys.argv) > 3 else "spec_c2.json", "w"), indent=1)
print("wrote %d entries" % len(spec))
