# 07: Pristine PotSAC map (paper §IV-B2 → author files)

**What to build:** the map the repair stands on — every step of paper §IV-B2 (axle estimation) traced to the exact pristine file and line that implements it, or marked MISSING.

**Answers:** E1

**Blocked by:** none. **Blocks:** 08, 09.

**Status:** ready-for-agent

**Pristine-only rule (binding):** paper text + pristine checkout (`sfs_main/archive_2025_sfs_modified_src @ 9195c01`, upstream `DominicoRyu/SfSpp_preprocessing @ d5ee6865`) only. Do NOT open any `SfSpp_preprocessing` fork code, `sfs_axes/`, `notes/task3-axes-plan.md`, or issues/05. A ticket citing them fails review.

- [ ] For each §IV-B2 step (surface input → profile sampling → PotSAC vote → robust refinement → axle output): pristine file + line, or MISSING with what the paper says it should do
- [ ] Inputs/outputs per step: format, units, coordinate frame; where the shipped Pot A axle files (`Axes/Pot_A_Piece_0i_Axis.xyz`, position-first per `data_structure.cpp:146–187`) come out of the chain
- [ ] List every hardcoded constant in the axle path with file:line and the paper value it should match (if the paper gives one)
- [ ] Comments section: numbered gap table (paper-step → file:line or MISSING), no fix proposals
