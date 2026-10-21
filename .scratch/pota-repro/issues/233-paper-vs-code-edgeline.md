# Ticket 233: paper-vs-code edgeline method

Status: ready-for-agent
Answers: none (method provenance; feeds the splitter/walker repair decisions)

## Goal
How does the paper describe finding the edgeline (breakline), and how does that differ -- or not -- from what the pristine-line code actually does? Per-stage verdicts with quotes on the paper side and file:line on the code side.

## Boundary
Read-only. Paper side: C:/PR/papers (find the SfS reassembly paper; the repo README/docs cite it). Code side: the pristine-live edgeline path (edgeline_extraction_headless.cpp + pota153_walker_new_function.cpp lineage on origin/pristine-splitwalk, i.e. boundary estimation -> face separation -> walk -> rim gate). Do not edit code, run jobs, or touch any ticket but this one.

## Constraints
Quote the paper (section + page/column), cite the code (file + line numbers). Stage list to cover: (1) input cloud formation, (2) boundary/edge detection, (3) face separation/split, (4) the walk/trace itself, (5) loop selection / rim gate. For each: PAPER-SAYS / CODE-DOES / SAME / DIFFER (one line each).

## Acceptance criteria
- [ ] The paper's edgeline section identified (title/section/page)
- [ ] All five stages covered with PAPER-SAYS / CODE-DOES / verdict
- [ ] Every DIFFER names the exact behavioral consequence (which P22/P12/P27 symptom it explains, if any)
- [ ] Verdict line: FAITHFUL / DRIFTED-<stages> / CONTRADICTS-<stage>

## Required evidence to report
Paper quotes + code cites in ticket Comments; verdict line; self-contained report; leave Status for the lead.
