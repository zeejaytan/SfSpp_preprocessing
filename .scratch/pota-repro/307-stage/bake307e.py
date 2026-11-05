#!/usr/bin/env python3
"""bake307e.py -- Stage B at NP=8 (the MO bar's repeat count).

The first Stage B sweep ran at NP=3 (copied from 306's spec_c1c.json) and every arm
landed at 4-5/8 + 5-7/15, including the control whose axis files are byte-identical to
ticket 305's 7/8 + 12/15 MMu seed-1 set.  NP is the assembler's internal repeat count, so
NP=3 under-scores everything and cannot be compared with the MO bar (8/8 + 15/15 at NP=8).
This bakes the same 12 runs at NP=8 into a local staging dir; one scp + one ssh submits them.
"""
import json, os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("driver", os.path.join(HERE, "..", "305-stage", "driver.py"))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)

TEMPLATE = os.path.join(HERE, "..", "305-stage", "e2e305.sbatch")
STAGE0 = os.path.join(HERE, "..", "305-stage")
LANES = "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_pota/geom"
AXBASE = "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0406_e6adf69_t307a-axes/out/pota"
OUT = os.path.join(HERE, "bake_e")
COMMIT = "e6adf69"

arms = [("base", "shipped default (cost prune ON)"), ("b1", "paper set: no cost<cost[0]*1.1 prune"),
        ("b5", "step 10 always (no under-5k step 1)"), ("b4", "ranking = post-refine cost")]
os.makedirs(OUT, exist_ok=True)
rows = []
for arm, desc in arms:
    for seed in (0, 1, 2):
        runid = "PLACEHOLDER_TS_%s_t307-%s-s%d-np8" % (COMMIT, arm, seed)
        subs = {"POT": "A", "NAMED": "8", "NP": "8", "FLOOR": "50", "ARMSPEC": "MM:2",
                "LANES": LANES, "AXDIR": "%s/%s_s%d" % (AXBASE, arm, seed),
                "NOTRUNC": "NONE", "COMMIT": COMMIT, "TAG": "t307-%s-s%d-np8" % (arm, seed)}
        body = driver.bake(TEMPLATE, subs, [])
        d = os.path.join(OUT, runid)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "submit.sbatch"), "w", newline="\n").write(body)
        meta = {"runid": runid, "commit": COMMIT, "tag": subs["TAG"], "params": subs, "env": [],
                "stage": "B at NP=8: %s" % desc,
                "submitted_from": "307-stage/bake307e.py"}
        open(os.path.join(d, "run.json"), "w", newline="\n").write(json.dumps(meta, indent=1) + "\n")
        rows.append((runid, arm, seed))
print("baked", len(rows), "runs into", OUT)
