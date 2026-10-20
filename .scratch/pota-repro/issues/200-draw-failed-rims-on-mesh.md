# 200 - Draw what the chain broke: failed pieces before/after on mesh

Status: open
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User request (m04604): C01 is the PROVEN case, not the question. Draw the D chain (densify -> split -> thin -> walk) on the OTHER pots\u2019 sherds where it FAILED, to see what changed on each rim and why it failed. Same-mesh + same-camera triplets (fresh input / thinned output / author where available), mm units, scale bars, eye-checked.

Priority cases (in order -- do all that the saved data supports):
1. B01 (194/198): the killer case -- rim BYTE-IDENTICAL fresh vs thinned, yet dropped 3/3. Draw fresh loop + thinned loop + author on the B01 mesh. Expectation: the two loops coincide, proving visually that nothing on THIS rim changed and the failure is global. If they do not coincide, that itself is the finding -- report it.
2. B09 (194/198): rim-truth gate-GREEN (+0.168, cov 74/75) yet dropped 3/3. Draw fresh vs thinned vs author. What does a gate-green loop that seats nothing look like?
3. One B piece the thin actually reshaped and dropped (P3 or P4 -- 198 Comments names survivors per run; pick a piece dropped 3/3 whose rim changed most): fresh vs thinned vs author.
4. Pot A control pieces (196): pick the 1-2 pieces whose strict edges went most wrong (196 Comments attribution); fresh vs thinned vs author on their meshes.
5. J03 (193): fresh doubled (371-pt open) vs 185-v3 thin loop (178-pt closed) vs author ORIG on the J03 mesh. The clean loop that still does not seat.

## Boundary
Laptop-side rendering only. Find loops in existing artifacts (.scratch/pota194_repro/, /data/gpfs/projects/punim2657/pota194_repro/ manifests + laptop artifacts/pota194[pota194_fetch tgzs], .scratch/pota196_repro/, artifacts/pota193/, pota185/ORIG). Do NOT recompute walks or E2E, do NOT touch tracked files except this ticket. New PNGs under artifacts/pota200/ (untracked) only.

## Constraints
Same mesh + same camera within each triplet or the comparison is void. If a loop file for a case cannot be found (e.g. a 194/196 intermediate was not saved), draw the cases that exist and NAME the missing one in Comments -- do not fake it, do not substitute a different piece. COMMIT NOTHING.

## Acceptance
One triplet PNG per case above that the data supports (minimum: cases 1, 2, 5), all eye-checked, in artifacts/pota200/, plus a one-line verdict per case: what visibly changed on the rim (or did not), and what that implies about where the failure lives (this rim vs global).

## Required evidence
Comments: PNG paths + source artifact per loop (md5 where available) + eye-check per panel + per-case verdict line (changed/unchanged, rim vs global) + any case that could not be drawn and why. Final output: same, self-contained.
