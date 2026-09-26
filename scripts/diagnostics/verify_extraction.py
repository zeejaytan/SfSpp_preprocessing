"""
Proof that lifting the ordering functions out of the pipeline file changed
nothing.

WHY THIS IS TEXTUAL, NOT A PIPELINE RE-RUN
The change under test is a pure code MOVE: two functions were cut out of
edgeline_extraction_headless.cpp and pasted verbatim into
edge_line_ordering.cpp, and the pipeline now includes the new file. For a
move, the proof that matters is that the moved text is the same text. A
pipeline re-run is still worth doing (it catches compile-level differences
such as kNN tie-breaking changing with inlining) but it is a secondary
check, and it is the slower and weaker of the two -- it can only report
"output differs somewhere", not "the code is identical".

So: this script diffs the moved code against the code as it was at the
parent of the extraction commit, ignoring comments and blank lines. What
remains must be identical, or every difference must be justified in prose.

KNOWN, ACCEPTED DIFFERENCES
THREE dead locals were removed from getPointsInSequence --
`pcl::PointIndices::Ptr inliers`, `pcl::ExtractIndices extract`, and
`std::vector<int> indices` -- all written and never read, all leftovers
from the commented-out alternative walk. The first two were the only
reason the new file needed <pcl/point_indices.h>, which the 137 KB
pipeline file supplied transitively. Nothing read any of them, so removing
them cannot change behaviour.

The list below is asserted against the "before" side, so if the extraction
ever stops matching this description the script fails rather than quietly
accepting a new difference.

Usage:  python scripts/diagnostics/verify_extraction.py [extraction-commit]
"""

import difflib
import re
import subprocess
import sys

DEFAULT_COMMIT = "3ce060e"  # "Ticket 01: extract edge-line ordering..."
PATH = "original_nurbs_preprocessing/edgeline_extraction_headless.cpp"
NEW = "original_nurbs_preprocessing/edge_line_ordering.cpp"

# Removed deliberately; see KNOWN, ACCEPTED DIFFERENCES above.
ACCEPTED_REMOVALS = [
    "pcl::PointIndices::Ptr inliers(new pcl::PointIndices());",
    "pcl::ExtractIndices<pcl::PointXYZ> extract;",
    "std::vector<int> indices;",
]


def grab(src, sig):
    """The whole function body starting at `sig`, brace-matched."""
    i = src.index(sig)
    j = src.index("{", i)
    depth = 0
    for k in range(j, len(src)):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return src[i:k + 1]
    raise SystemExit(f"unbalanced braces for {sig}")


def code_only(text):
    """Strip comments and blank lines, so only code differences can show."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return [ln.rstrip() for ln in text.splitlines() if ln.strip()]


def main():
    commit = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COMMIT
    original = subprocess.run(
        ["git", "show", f"{commit}^:{PATH}"],
        capture_output=True,
        text=True,
        # Windows defaults to a legacy codepage (gbk here) and dies on the
        # C++ source's bytes. Pin UTF-8 rather than inherit the platform's.
        encoding="utf-8",
        errors="replace",
    )
    if original.returncode != 0:
        sys.exit(f"could not read {commit}^:{PATH}\n{original.stderr}")
    original = original.stdout
    with open(NEW, encoding="utf-8") as fh:
        extracted = fh.read()

    failures = 0
    for sig in ("bool pointExistsInCLoud", "void getPointsInSequence"):
        before = code_only(grab(original, sig))
        after = code_only(grab(extracted, sig))

        # Drop the lines we agreed to remove, from the BEFORE side only.
        accepted = [ln for ln in before if ln.strip() not in ACCEPTED_REMOVALS]
        removed = [ln for ln in before if ln.strip() in ACCEPTED_REMOVALS]

        if accepted == after:
            note = f" (after removing {len(removed)} accepted dead local(s))" if removed else ""
            print(f"  {sig:26s} IDENTICAL{note}")
            for ln in removed:
                print(f"      removed: {ln.strip()}")
            continue

        failures += 1
        print(f"  {sig:26s} DIFFERS -- not a pure move, investigate:")
        for line in difflib.unified_diff(
            accepted, after, "before", "after", lineterm="", n=1
        ):
            print(f"      {line}")

    print()
    if failures:
        print(f"FAIL: {failures} function(s) differ beyond the accepted removals.")
        print("The extraction is not behaviour-preserving. Do not trust any")
        print("result produced by the moved code until this is explained.")
        return 1
    print("PASS: the moved code is identical to the original, apart from the")
    print("declared dead locals. The extraction is behaviour-preserving.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
