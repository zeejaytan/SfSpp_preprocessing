#!/usr/bin/env python3
"""make_guard68.py A_DIR B_DIR -- ticket 68 Part B: canonical empty-candidate guard.

Root fix in StateManager::Initialize (class/ranking_system.cpp:727 read ext_state_[0] with
ext_state_ empty whenever no root graph exists). With the early return, BuildStep sees zero states
and finishes with out_state_ empty; main.cpp and the batch shim then stop cleanly instead of
reading out_state_[0]. Sources are CRLF; inserts are written CRLF. Each anchor must occur once.
"""
import os
import sys

A, B = sys.argv[1], sys.argv[2]
NL = "\r\n"


def lines(*xs):
    return "".join(x + NL for x in xs)


EDITS = {
    "class/ranking_system.cpp": [
        ("\tnum_init_prio_ = ext_state_[0].total_priority_.size();" + NL,
         lines("\tif (ext_state_.empty()) {",
               "\t\tcout << \"SFS-NO-CANDIDATES no root graph from \" << initial_graph_.size()"
               " << \" pruned pairs; StateManager has no state\" << endl;",
               "\t\tnum_init_prio_ = 0;",
               "\t\treturn;",
               "\t}"),
         "before"),
    ],
    "main.cpp": [
        ("\tmanager.BuildStep();" + NL,
         lines("\tif (manager.out_state_.empty()) {",
               "\t\tcout << \"SFS-NO-CANDIDATES no assembly state to show; exit 0\" << endl;",
               "\t\treturn 0;",
               "\t}"),
         "after"),
    ],
    "hpc/tools/main_pristine_batch.cpp": [
        ("\tmanager.BuildStep();" + NL,
         lines("\tif (manager.out_state_.empty()) {",
               "\t\tcout << \"SFS-NO-CANDIDATES no assembly state to save; exit 0\" << endl;",
               "\t\treturn 0;",
               "\t}"),
         "after"),
    ],
}

for rel, edits in EDITS.items():
    text = open(os.path.join(A, rel), newline="", encoding="latin-1").read()
    for anchor, ins, where in edits:
        n = text.count(anchor)
        if n != 1:
            sys.exit("%s: anchor count %d (want 1): %r" % (rel, n, anchor))
        text = text.replace(anchor, ins + anchor if where == "before" else anchor + ins)
    with open(os.path.join(B, rel), "w", newline="", encoding="latin-1") as fh:
        fh.write(text)
    print("GUARD OK", rel)
