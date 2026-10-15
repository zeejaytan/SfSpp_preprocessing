function rev = af_orient(v, C0, C1)
% AF_ORIENT frozen per-surface orientation call at axis v: picks REV iff the
% reversed Cao error has the lower GM-robustified sum. Evidence: unanimous
% S0->REV, S1->fwd on all fit pieces with 1.5-2x margins (V1e, job 33076317).
Cs = {C0, C1}; rev = [false, false];
for q = 1:2
  Rf = compute_cao_error(v, Cs{q}, false);
  Rr = compute_cao_error(v, Cs{q}, true);
  cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
  cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
  rev(q) = cr < cf;
end
end
