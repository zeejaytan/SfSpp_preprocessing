# 64 — Size the normal-estimation ball from the sherd's own thinnest wall (the 0.7 x rule)

**What to build:** the adaptive radius rule the conservator chose on 2026-11-03: per sherd, set the
normal-estimation ball to **0.7 x the thinnest non-edge (smooth-wall) thickness of that sherd**, as an
opt-in mode; the default path is untouched. Two deliverables: (1) a **label-free smooth-wall thickness
estimator** that works on the mesh alone and knows when to refuse; (2) the per-piece **wiring + floor
alarm** that turns the estimate into `SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=<value>` without ever
silently exceeding it.

**Answers:** U19, E1

**Blocked by:** 63 (its instrumented walk is the acceptance instrument; its predictor tables are the
validation targets)

**Status:** ready-for-agent
**Branch:** 64-adaptive-normal-radius, via `ticket_start.sh` at dispatch
**Worker:** —

## Spec

### Given (measured facts this stands on)

1. Mechanism (ticket 63): one sign-blind MST edge spanning the wall flips a whole sheet. On J1 the
   edge is 9123-18574, 1.470 mm, through a 1.46-1.48 mm local wall; thinnest smooth wall (t59 labels,
   1st pctile) **1.463 mm** vs k=19 max reach **1.627 mm**; the subtree below it is 8079 points =
   41.8 % of the flip. J2 (1.585 mm) and J7 (1.980 mm) have **zero** through-wall tree edges at
   every setting tested.
2. The rule reproduces the measured-good radius without being told it: 0.7 x 1.463 = **1.02 mm** on
   J1, against the fixed **1.0 mm** measured good end-to-end (t62 Stage 2: J1 flip 41.63 -> 0.2 %,
   genuine wall pairs 9/9, S0 within 10 % of t55, folded median dihedral +0.4-1.4 deg). A fixed
   1.0 mm is only safe while walls stay above ~1.4 mm; the rule generalises to thinner pots, where
   a fixed 1.0 would itself span the wall.
3. "Not at the edge" is the unbuilt part. Raw mesh minimum wall is 0.010 mm everywhere (rim
   artefacts); J2's label-free point-wise p1 is 0.08 mm at rims. The t59 dihedral labels give usable
   walls (J1 1.463 / J2 1.585 / J7 1.980; Pot A p1 2.504-3.959) but are an offline instrument — a
   label-free estimator (geometry only, no t59 region labels at runtime) does not exist yet.
4. Ray-pair thickness fails on decimated released clouds: Pot D thick_hit_share 0.001-0.006 (t63
   Stage 2). Coverage must be reported and the estimator must **refuse below a stated floor**
   rather than take a minimum from 0.6 % of rays.
5. Radius mode is shipped (ticket 24, commit `69b6539`): `SFS_NORMAL_MODE=radius` +
   `SFS_NORMAL_RADIUS_MM`. An auto-by-spacing variant (`SFS_NORMAL_RADIUS_AUTO=1` +
   `SFS_NORMAL_RADIUS_MULT`) also exists but sizes by cloud **density**, not by the wall — it is
   not this rule. The env is per-run global, but the mesh stage runs per piece
   (`scripts/stage_piece.sh`), so a wrapper can set a per-piece radius.
6. The 5..20 neighbour clamp still applies inside radius mode and stretches the ball in sparse
   spots — t63 measured clamped 1.4 reaching a 1.29 mm edge and flipping through it. The alarm must
   reason about **effective max reach**, not nominal radius.
7. A floor exists: bare radius 0.6 mm broke the walk graph into 1024 components (t63 Stage 1). The
   principled form is ">= 5 neighbours inside the ball on >= 99 % of points", measured per piece
   from the growth cloud.
8. Instruments on Spartan:
   - t63 instrumented walk: `runs/20261103-0211_249906a_t63-orientwalk/work/orient_walk.py` —
     through-wall MST edge count + flip share, run on the pipeline's own dumped points.
   - t59 labels + per-point thickness: `runs/20261102-1144_638504b_t59-breakstop-stage0/out/labels/*.npz`.
   - t62 Stage-2 radius-1.0 outputs: `runs/20261103-0035_ca520fe_t62-normalfix-s2/`.
   - Meshes `Dataset/Mesh/<pot>`; J1 mesh md5 b447066c29181fe7ba987439c22c5d9c.

### Build (three stages, in order)

**Stage 1 — label-free smooth-wall thickness estimator.** From the mesh alone: per-face ray-paired
thickness restricted to dihedral-smooth regions away from rim/lip boundaries (t59 stage-0 code is
the reference for the labels, not a runtime dependency). Report per piece: the 1st-pctile
smooth-wall estimate, the coverage it rests on, and the accepted/refused decision. **Validation
gate before anything downstream:** against t59's labelled walls on all nine Juglet (J1 1.463 /
J2 1.585 / J7 1.980 within +/- 0.1 mm; the other six reported alongside), Pot A 8 as the thick
control (2.504-3.959), Pot D 8 as the refusal case (coverage floor stated and triggered).

**Stage 2 — wiring, default-off, with the floor alarm.** A wrapper (run-dir script; whether it
becomes `scripts/` is the lead's call at review): for each piece, estimate the wall, compute
r = 0.7 x w, then either invoke the mesh stage with `SFS_NORMAL_MODE=radius
SFS_NORMAL_RADIUS_MM=<r>` or refuse loudly. The alarm: (a) refuse when Stage-1 coverage is below
its floor; (b) warn + report when r falls below the piece's 5-neighbour ball (measured from the
growth cloud spacing), stating the clamped value actually used; (c) after the run, verify with the
t63 walk that the **effective** max reach at the chosen r stayed under 0.7 x w. Nothing unset
changes; no tracked source edits without lead approval.

**Stage 3 — acceptance, nine Juglet + Pot A 8.** Auto radii land where expected (J1 ~1.02, J2
~1.11, J7 ~1.39; report all nine). Then: (i) t63 instrumented walk on every dumped field — zero
through-wall MST edges, flip < 1 %, all nine; (ii) `check_separation.py` vs the t55 baseline —
J1 genuine 9/9, S0 counts within 10 %; (iii) where the auto value equals a previously run setting
to the precision passed to the env var, outputs must reproduce that run where deterministic; Pot A
(the rule gives 1.75-2.77 mm) shows no harm vs t55 within the usual tolerance.

### Gates and budget

- Corpus read-only; `inputs.diff` empty; the unset arm is byte-identical.
- Every `sbatch` polled; final `sacct` State/ExitCode recorded in the ticket.
- Budget: <= 4 jobs, <= 4 h wall total.
- Worker appends `## Results` only: no Status edits, no commits, no merges. `verdict` /
  `human_note` in `runs/index.tsv` stay empty for the lead.

### Traps (paid for already)

- SSH from this laptop: `C:/Windows/System32/OpenSSH/ssh.exe spartan` (Git Bash ssh has no key);
  poll `sacct` directly.
- Spartan python: `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` (no pandas —
  aggregate in awk or fetch small TSVs to the laptop).
- sbatch files need Unix line endings (a DOS-ending sbatch was rejected once).
- Jobs must fetch the worktree commit before building (t61 pattern).
- Single writer in `.scratch/`: run `python C:/PR/scripts/check_scratch_writer.py SfSpp_preprocessing`
  before editing.

### Out of scope

The per-pot arrow gate (t61 field check, ~20 s/piece) stays the standing independent check on any
new pot regardless of this rule; installing it as a pipeline step is a separate decision, not this
ticket.
