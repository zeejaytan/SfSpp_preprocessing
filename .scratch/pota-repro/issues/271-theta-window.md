# 271 — Sweep the tau_theta window, then run it in production

Answers: E1
Status: ready
Working in: C:/PR/SfSpp_preprocessing-248 + Spartan run trees (NO C++ change, NO build; NO main commits)
Needs-eye: no

## Why

270 settled the mechanism: the lip is inside `Surface_1` because region growing compares each candidate
against the **frontier** normal, never the seed (`mesh_processing_headless.cpp:1770`), so a 25 deg fold
crossed in 0.5-1.2 deg steps passes `tau_theta = 4.0`. (R) is excluded (zero merges fired; the lip is not
a cluster). The follow-up killed the curvature alternative: the paper's `tau_kappa = 1` gate at
`mesh_processing_headless.cpp:1766` is provably inert on our clouds (observed max curvature 0.1606 / 0.2733 /
0.1586 against a PCL bound of 1/3 and a threshold of 1.0; zero rejections, labels identical at kappa=1e12),
and no curvature threshold ranks the bands the right way (the crest is the **highest**-curvature band, and
P01's flank is *less* curved than its face). tau_theta is the only lever.

**But 270's recommended value (3.0) is known to be too aggressive, and nobody has tested the window that
matters.** 270's own numbers: P03's face-to-lip bottleneck is **3.45 deg**; P22's is **3.06 deg**; P01's is
~0.08 deg. A tau in **(3.06, 3.45)** severs P03's lip while leaving P22's growth intact -- yet the only
value replayed was 3.0, below P22's limit, which is exactly why P22 was reported fragmenting (16->18
clusters, coverage 0.654 -> 0.459). The clean setting, if it exists, is inside that window.

**And no build is needed.** tau_theta is read from `SFS_PAPER_THETA` (`mesh_processing_headless.cpp:2561`)
at the mesh stage, so the window can be swept and the winner run in production with the binaries we
already have.

## Goal

**Phase 1 (laptop, fast) — sweep the window in the replay, with a pre-registered rule.**
Replay `SFS_PAPER_THETA` = 3.1, 3.2, 3.3, 3.4, 3.45 on P03, and 3.2 / 3.3 / 3.4 on P22 and P01 (guards).
Reuse 270's replay scripts and the *same* clouds/labels/author lanes (md5s in 270's ticket section 7).
For each value report, per piece: cluster count, top-1 and top-2 sizes, kept-cluster outboard extent in the
stretch (s max), points kept in the face (s <= 0), and any change in the two-largest selection.

PRE-REGISTERED SELECTION RULE (write it down before running):
- P03 passes at tau if kept-cluster s max in the stretch is **<= +1.0 mm** (lip severed) and the face keeps
  **>= 85%** of its tau=4 points.
- Guards pass if P22's cluster count and top-1 size are **unchanged from tau=4** (within 1%) and P01's are
  unchanged (< 2%).
- **Select the LARGEST tau that passes everywhere** (maximum margin below P22's hard limit).
- If no tau in the window passes, **STOP** and report the table -- do not widen the window without asking
  the lead. The fallback discussion (per-piece tau, density-normalised gate) is the lead's call.

**Phase 2 (production, existing binaries) — run the winner, no rebuild.**
Reproduce ticket 267's run configuration **exactly** (same sbatch script, same env, same inputs; read them
out of 267's run tree or logs -- do not reconstruct them from memory), changing **only** `SFS_PAPER_THETA` at
the mesh stage. Lane set: P03 Bl0 and Bl1, P22 Bl0 and Bl1, P01 Bl0 and Bl1.
- **Control run at tau = 4 must reproduce ticket 267's numbers exactly** (P03 Bl0 0.52/100.0, Bl1 0.90/57.4;
  P22 Bl0 0.69/87.7, Bl1 0.57/95.1; P01 Bl0 0.75/98.8, Bl1 0.98/95.4). If it does not, the run is not
  comparable -- stop and report the mismatch before interpreting anything.
- Then the tau run on the same six lanes, scored with ticket 266's scorer (`pota266_score.py`).
- Verify the **mesh stage actually used** the env value (the `[PAPER-234] paper grow: thetaDeg=...` line at
  `mesh_processing_headless.cpp:2127`) -- an env var that silently did not apply would look like a negative.
- Report per-lane med / cov / jumps / maxjump, plus the surface's own outboard extent, so the causal chain
  (mesh extent -> edge line position) is visible, not just the score.

STOP conditions: control mismatch; env not applied; or the tau run leaves any guard lane off bar.

## Boundary

- No C++ edits, no rebuild. Use the binaries ticket 267 used (record their md5s).
- Only `SFS_PAPER_THETA` may differ from the 267 configuration. If you believe another flag must change,
  stop and ask the lead.
- Author lanes are ground truth as given. Score with the existing scorer, one-way precision as in 267.
- New files under `artifacts/pota271/` and `pota271_*.py` (untracked). Ticket file lives in
  C:/PR/SfSpp_preprocessing/.scratch/pota-repro/issues/. No commits.
- Judgement stays with the lead: report the tables and the run, do not decide what gets built next.

## Acceptance criteria

1. The pre-registered rule written into the ticket **before** the sweep, with the sweep table against it.
2. One chosen tau with its numbers, or an explicit "no tau passes" with the table.
3. Control run reproducing 267 to the decimal on all six lanes (or the mismatch reported).
4. Production run at the chosen tau: per-lane med / cov / jumps / maxjump + the mesh surface extent.
5. The `[PAPER-234] thetaDeg=` log line quoted as proof the env applied, plus every binary and input md5.
6. One figure: P03-Bl1 at tau=4 vs the chosen tau vs the author's line, same axes -- so the claim can be
   looked at, not only tabulated.
