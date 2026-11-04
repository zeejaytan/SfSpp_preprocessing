#!/usr/bin/env python3
"""patch_guard67.py SRC DST -- ticket 67: write a COPY of the batch shim with the empty-candidate guard.

StateManager's constructor reaches class/ranking_system.cpp:727 `ext_state_[0]` with ext_state_
empty whenever the pruned LCS list is empty (ext_state_ is only appended at :720 when the root
graph is non-empty). class/ cannot be edited from the shim, so the guard sits in the shim, just
before the StateManager is constructed: an empty list prints T67-NO-CANDIDATES and returns 0.
A second guard after BuildStep covers out_state_[0] at the fine-registration block.
Each anchor must occur exactly once, or the patch refuses (exit 2).
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()

GUARDS = [
    ('\tcout << "Total number pruned : " << LCS_out.size() << endl;\n',
     '\tif (LCS_out.empty()) {\n'
     '\t\tcout << "T67-NO-CANDIDATES pruned LCS list empty; StateManager skipped; exit 0" << endl;\n'
     '\t\treturn 0;\n'
     '\t}\n'),
    ('\tmanager.BuildStep();\n',
     '\tif (manager.out_state_.empty()) {\n'
     '\t\tcout << "T67-NO-STATES StateManager produced no output state; exit 0" << endl;\n'
     '\t\treturn 0;\n'
     '\t}\n'),
]

for anchor, guard in GUARDS:
    n = text.count(anchor)
    if n != 1:
        sys.stderr.write('anchor count %d (want 1): %r\n' % (n, anchor))
        sys.exit(2)
    text = text.replace(anchor, anchor + guard)

open(dst, 'w', newline='\n').write(text)
print('GUARD OK', dst)
