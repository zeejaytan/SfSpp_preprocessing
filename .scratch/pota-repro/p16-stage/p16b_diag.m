% POTA-16 phase-2 diagnostic (no finder changes): headroom check for attempt (b)
% + P07 peel trace + P08 rev check. Develops against 05/07/08 openly per ticket.
function p16b_diag()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p16-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);

for frag = [7,8]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  C = [C0, C1]; NS = [size(C0,2), size(C1,2)];
  [comp, ~] = af_split(C, 10, 300);
  fprintf('P16b P%02d split: %d comps sizes=[%s]\n', frag, max(comp), ...
    num2str(arrayfun(@(c) sum(comp==c), 1:max(comp))', '%d '));
  % round-1 vote replicated exactly (seed+round = 1), cluster top-1000 to 6 modes
  [VT, CR] = af_vote(C0, C1, 6000, 0.1, 1, 'raw', 6);
  K = min(1000, size(VT,2));
  [VC, ~, ~] = af_cluster(VT(:,1:K), CR(1:K), 10, 2, 1.5, 6);
  fprintf('P16b P%02d vote: %d raw hyps -> %d diverse modes\n', frag, size(VT,2), size(VC,2));
  % rev frozen as chain does (top cluster)
  Cs = {C0, C1}; rev = [false, false];
  for q = 1:2
    Rf = compute_cao_error(VC(:,1), Cs{q}, false);
    Rr = compute_cao_error(VC(:,1), Cs{q}, true);
    cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
    cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
    rev(q) = cr < cf;
  end
  % refine each mode (sub then full), report GM cost + inliers + vs-shipped
  C0n = C0; C1n = C1;
  C0n(4:6,:) = C0n(4:6,:) ./ sqrt(sum(C0n(4:6,:).^2));
  C1n(4:6,:) = C1n(4:6,:) ./ sqrt(sum(C1n(4:6,:).^2));
  S = [C0n(:,1:10:end), C1n(:,1:10:end)];
  for m = 1:size(VC,2)
    v1 = af_refine_raw(VC(:,m), C0(:,1:10:end), C1(:,1:10:end), rev, 1, 300, 1e-3);
    v = af_refine_raw(v1, C0, C1, rev, 1, 300, 1e-9);
    gm = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(v, S)));
    [~, ~, n] = af_inliers(v, C0, C1, rev);
    [dd, rr, ~] = score_vs_shipped(v, SHIP);
    [bd, bi] = min(dd);
    fprintf('P16b P%02d mode%d GM=%.4g inl=%d bestderr=%.2f(sh%d) rerr=%.2f\n', ...
      frag, m, gm, n, bd, bi, rr(bi));
  end
  % GM cost + refine-from-shipped per shipped axle (rev frozen at that axle)
  for s = 1:size(SHIP,1)
    d = SHIP(s,4:6)'; d = d/norm(d); p = SHIP(s,1:3)';
    vs = [d; p];
    gms = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(vs, S)));
    revS = af_orient(vs, C0, C1);
    w1 = af_refine_raw(vs, C0(:,1:10:end), C1(:,1:10:end), revS, 1, 300, 1e-3);
    wr = af_refine_raw(w1, C0, C1, revS, 1, 300, 1e-9);
    gmr = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(wr, S)));
    [dd2, rr2, ~] = score_vs_shipped(wr, SHIP);
    fprintf('P16b P%02d shipAx%d GMship=%.4g GMref=%.4g walk=%s refderr=%.2f rerr=%.2f\n', ...
      frag, s, gms, gmr, updown(gmr <= gms), min(dd2), rr2(find(dd2==min(dd2),1)));
  end
end
% P07 peel trace with M=1 (chain behaviour): per-round winner + stop reason
frag = 7;
[C0, C1] = read_surfaces('A', frag);
R0 = C0; R1 = C1; N0 = size(C0,2)+size(C1,2);
for round = 1:4
  if size(R0,2) < 50 || size(R1,2) < 50
    fprintf('P16b P07 peel round%d STOP-residual(%d,%d)\n', round, size(R0,2), size(R1,2)); break; end
  [VT, CR] = af_vote(R0, R1, 6000, 0.1, 0+round, 'raw', 6);
  K = min(1000, size(VT,2));
  [VC, ~, ~] = af_cluster(VT(:,1:K), CR(1:K), 10, 2, 1.5, max(1,1));
  Cs = {R0, R1}; rev = [false, false];
  for q = 1:2
    Rf = compute_cao_error(VC(:,1), Cs{q}, false);
    Rr = compute_cao_error(VC(:,1), Cs{q}, true);
    cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
    cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
    rev(q) = cr < cf;
  end
  v1 = af_refine_raw(VC(:,1), R0(:,1:10:end), R1(:,1:10:end), rev, 1, 300, 1e-3);
  v = af_refine_raw(v1, R0, R1, rev, 1, 300, 1e-9);
  [~, ~, n] = af_inliers(v, R0, R1, rev);
  fprintf('P16b P07 peel round%d winner_n=%d thresh=%.0f Barker=%.0f\n', ...
    round, n, 0.10*N0, size(R0,2)+size(R1,2));
  if n < 0.10*N0
    fprintf('P16b P07 peel round%d STOP-minfrac\n', round); break; end
  [m0, m1, ~] = af_inliers(v, R0, R1, rev);
  R0 = R0(:, ~m0); R1 = R1(:, ~m1);
end
end

function s = updown(ok)
if ok, s = 'down-or-flat'; else, s = 'UP'; end
end
