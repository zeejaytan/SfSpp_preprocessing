# Ticket 66 worker status (resume-cold file)

Updated 2026-11-03 13:34 (UTC+11).

## Done
- Part A: commit `112da1e` (flag default true, `0`/`off`/`false`/empty = OFF, `[ADMIT-SIGN-66] default=on admit_sign=<0|1>` once per piece; filter and append order untouched). Pushed.
- Runner/submit/render: `run_cell66.sh`, `submit66.sbatch`, `t66_render.py` in this folder; build commit `fab76f5` (LF fix on top of `37e04b0`). Pushed.
- Submitted: run `20261103-1332_fab76f5_t66-admitsign-default`, **job 34262530** (sapphire, 8 cpu, 64G, 4h), node spartan-bm073.
  Index row appended (verdict/human_note empty). run.json + submit.sbatch in the run dir.
- 13:36: build OK -- MeshPreprocessingHeadless `748b174f814ab881afb627fab9a978df`, EdgeLineExtractionHeadless
  `cbf747dc3172fe0bbd188822df14092a`; cell U_jug running (order: U_jug, U_pota, U_potc, Z_jug, Z_pota, Z_potc, then scoring/render).
- Poller: `slurm_poll.sh 34262530 120` under nohup on spartan-login2, log `<run>/logs/poll-34262530.log`.

## Next (resume here)
1. Poll: `ssh spartan "tail -3 <run>/logs/poll-34262530.log; tail -30 <run>/logs/slurm-34262530.out"`.
2. When done: `sacct -j 34262530 --format=JobID,State,ExitCode,Elapsed` -> record in ticket.
3. Read `<run>/out/partB_U_jug_vs_t65T.tsv`, `partB_Z_jug_vs_t65C.tsv` (18 rows, all `same` = pass),
   `out/UvsZ_{jug,pota,potc}.tsv`, `passU_*.admit65.txt` (dropped counts), `outU_*/pieces66.tsv`
   (surface/Bl counts), `out/sep_U.tsv` (J1 blindDeg, farS0), `out/sector/sectors_U.tsv` +
   sector.log (f2r_le1, r2f_le1, ring_cov_deg5), `out/stage1/stage1_pieces.tsv` (fold_off2).
4. Fetch `out/fig/j1_bl0_{before,after,before_after}.png` to `artifacts/66/` (scp via OpenSSH).
5. Write Findings/Numbers into the ticket; FIXES-LEDGER row 14 draft; commit; push.

## Assumptions to report
- Pot A inputs = t41-pota inputs.md5 (corpus released cloud + corpus mesh + Dataset/Axes/Pot_A), not
  Dataset/Point/Pot_A (an archived 10k-100k point set, no manifest).
- Pot C 01 = Dataset derived cloud, gated by a run-local pin (md5 measured today + 840,835 pts from AGENTS.md).
- No runbook file exists in this repo; runbook note left for the lead.
