#!/usr/bin/env python3
"""Ticket 303: instrument main_pristine_batch.cpp for the axis-line diagnosis.

Reads the shipped hpc/tools/main_pristine_batch.cpp and writes a copy that

  1. keeps the two t67 guards (empty LCS list / empty out_state_ -> clean exit 0),
  2. prints, additively and only to stdout:
       T303-LCS        every LCS candidate right after FeatureComp
       T303-PRUNED     every candidate that survived PairwisePruning, with its
                       axis_angle_ and the axis-line pair it was matched on
       T303-STATES/STATE/GRAPH/NODE/EDGE/T
                       the state StateManager chose: each subgraph's root, its
                       node set, every node's placement, and every join's
                       axis-line pair and angle.

No algorithm, threshold, weight, solver or statement order is changed: every
insertion is a new block that only reads. The diff is the record.

    patch303.py <shipped.cpp> <out.cpp>
"""
import sys

TAB = "\t"


def block(lines):
    return "".join(l + "\n" for l in lines)


LCS_DUMP = block([
    TAB + "// ===== T303 DUMP: LCS candidates after FeatureComp (read-only) =====",
    TAB + "{",
    TAB + TAB + "int t303n = 0;",
    TAB + TAB + "for (list<LCSIndex>::iterator t303it = LCS_out.begin(); t303it != LCS_out.end(); ++t303it) {",
    TAB + TAB + TAB + 'cout << "T303-LCS fix " << t303it->shard_y_ << " mov " << t303it->shard_x_',
    TAB + TAB + TAB + '     << " ax_f " << t303it->axis_index_y_ << " ax_m " << t303it->axis_index_x_',
    TAB + TAB + TAB + '     << " size " << t303it->size_ << " score " << t303it->score_',
    TAB + TAB + TAB + '     << " inl " << t303it->inliner_ << endl;',
    TAB + TAB + TAB + "t303n++;",
    TAB + TAB + "}",
    TAB + TAB + 'cout << "T303-LCS-N " << t303n << endl;',
    TAB + "}",
])

PRUNED_DUMP = block([
    TAB + "// ===== T303 DUMP: surviving LCS candidates with their axis-line pair =====",
    TAB + "{",
    TAB + TAB + "int t303n = 0;",
    TAB + TAB + "for (list<LCSIndex>::iterator t303it = LCS_out.begin(); t303it != LCS_out.end(); ++t303it) {",
    TAB + TAB + TAB + 'cout << "T303-PRUNED fix " << t303it->shard_y_ << " mov " << t303it->shard_x_',
    TAB + TAB + TAB + '     << " ax_f " << t303it->axis_index_y_ << " ax_m " << t303it->axis_index_x_',
    TAB + TAB + TAB + '     << " ang " << t303it->axis_angle_',
    TAB + TAB + TAB + '     << " size " << t303it->size_ << " score " << t303it->score_',
    TAB + TAB + TAB + '     << " inl " << t303it->inliner_ << " area " << t303it->area_',
    TAB + TAB + TAB + '     << " ovl " << (t303it->overlap_ ? 1 : 0) << endl;',
    TAB + TAB + TAB + "t303n++;",
    TAB + TAB + "}",
    TAB + TAB + 'cout << "T303-PRUNED-N " << t303n << endl;',
    TAB + "}",
])

STATE_DUMP = block([
    TAB + "// ===== T303 DUMP: the state StateManager chose =====",
    TAB + "{",
    TAB + TAB + 'cout << "T303-STATES " << (int)manager.out_state_.size() << endl;',
    TAB + TAB + "for (int t303g = 0; t303g < (int)manager.out_state_.size(); t303g++) {",
    TAB + TAB + TAB + "State& t303s = manager.out_state_[t303g];",
    TAB + TAB + TAB + 'cout << "T303-STATE " << t303g << " score " << t303s.state_score_',
    TAB + TAB + TAB + '     << " ngraph " << (int)t303s.graph_.size() << endl;',
    TAB + TAB + TAB + "for (int t303k = 0; t303k < (int)t303s.graph_.size(); t303k++) {",
    TAB + TAB + TAB + TAB + "RankingSubgraph& t303sg = t303s.graph_[t303k];",
    TAB + TAB + TAB + TAB + 'cout << "T303-GRAPH " << t303g << " " << t303k',
    TAB + TAB + TAB + TAB + '     << " root " << t303sg.root_node_ << " gscore " << t303sg.graph_score_',
    TAB + TAB + TAB + TAB + '     << " nedges " << (int)t303sg.sub_graph_.size() << endl;',
    TAB + TAB + TAB + TAB + "for (int t303n = 0; t303n < (int)t303sg.node_.size(); t303n++)",
    TAB + TAB + TAB + TAB + '    if (t303sg.node_[t303n]) cout << "T303-NODE " << t303g << " " << t303k',
    TAB + TAB + TAB + TAB + '        << " " << (t303n + 1) << endl;',
    TAB + TAB + TAB + TAB + "for (int t303n = 0; t303n < (int)t303sg.T_.size(); t303n++) {",
    TAB + TAB + TAB + TAB + TAB + "Matrix4d t303T;",
    TAB + TAB + TAB + TAB + TAB + "t303sg.T_[t303n].Output(t303T);",
    TAB + TAB + TAB + TAB + TAB + 'cout << "T303-T " << t303g << " " << t303k << " " << (t303n + 1);',
    TAB + TAB + TAB + TAB + TAB + "for (int t303r = 0; t303r < 3; t303r++)",
    TAB + TAB + TAB + TAB + TAB + "    for (int t303c = 0; t303c < 4; t303c++)",
    TAB + TAB + TAB + TAB + TAB + '        cout << " " << t303T(t303r, t303c);',
    TAB + TAB + TAB + TAB + TAB + "cout << endl;",
    TAB + TAB + TAB + TAB + "}",
    TAB + TAB + TAB + TAB + "for (list<LCSIndex>::iterator t303e = t303sg.edge_.begin(); t303e != t303sg.edge_.end(); ++t303e) {",
    TAB + TAB + TAB + TAB + TAB + 'cout << "T303-EDGE " << t303g << " " << t303k',
    TAB + TAB + TAB + TAB + TAB + '     << " fix " << t303e->shard_y_ << " mov " << t303e->shard_x_',
    TAB + TAB + TAB + TAB + TAB + '     << " ax_f " << t303e->axis_index_y_ << " ax_m " << t303e->axis_index_x_',
    TAB + TAB + TAB + TAB + TAB + '     << " ang " << t303e->axis_angle_ << " score " << t303e->score_ << endl;',
    TAB + TAB + TAB + TAB + "}",
    TAB + TAB + TAB + "}",
    TAB + TAB + "}",
    TAB + "}",
])

GUARD_LCS = block([
    TAB + "if (LCS_out.empty()) {",
    TAB + TAB + 'cout << "T67-NO-CANDIDATES pruned LCS list empty; StateManager skipped; exit 0" << endl;',
    TAB + TAB + "return 0;",
    TAB + "}",
])

GUARD_STATE = block([
    TAB + "if (manager.out_state_.empty()) {",
    TAB + TAB + 'cout << "T67-NO-STATES StateManager produced no output state; exit 0" << endl;',
    TAB + TAB + "return 0;",
    TAB + "}",
])

# (label, anchor that must occur exactly once, text inserted immediately after it)
PATCHES = [
    ("lcs-dump",
     TAB + "cout << \"Total number : \" << LCS_out.size() << endl;\n",
     LCS_DUMP),
    ("guard-lcs",
     TAB + "cout << \"Total number pruned : \" << LCS_out.size() << endl;\n",
     GUARD_LCS),
    ("pruned-dump",
     TAB + "cout << \"Total number pruned : \" << LCS_out.size() << endl;\n" + GUARD_LCS,
     PRUNED_DUMP),
    ("guard-state",
     TAB + "manager.BuildStep();\n",
     GUARD_STATE),
    ("state-dump",
     TAB + "manager.BuildStep();\n" + GUARD_STATE,
     STATE_DUMP),
]


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: patch303.py <shipped.cpp> <out.cpp>\n")
        return 2
    src = open(argv[1], encoding="utf-8").read()
    text = src
    for label, anchor, insert in PATCHES:
        n = text.count(anchor)
        if n != 1:
            sys.stderr.write("anchor count %d (want 1) for %s: %r\n" % (n, label, anchor[:70]))
            return 2
        text = text.replace(anchor, anchor + insert, 1)
    if text.count("point_.cols() < 50") != 1:
        sys.stderr.write("floor literal 'point_.cols() < 50' not present exactly once\n")
        return 2
    open(argv[2], "w", encoding="utf-8", newline="\n").write(text)
    print("T303 PATCH OK %s" % argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
