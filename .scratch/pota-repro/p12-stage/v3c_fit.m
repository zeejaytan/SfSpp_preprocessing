% POTA-12 V3c: bias nature + small-piece controls (fit data only, 05-08 sealed).
% (a) Half-split test P01/P04: fit spatial halves independently. Halves
% disagree w/ each other ~mm-scale => local geometric variability
% (irreducible for any fragment-only fitter); halves agree but off-ship =>
% systematic method bias (fixable).
% (b) Scale controls P01: uniform 1:10 downsample (~07 point count, full
% span) vs thin slabs (narrow but spanning) vs ball patch (narrow+local).
% (c) P02 hard-IRLS x8 (was still improving at it3: 5.17->3.46).
function v3c_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = [1 4]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  X = [C0(1:3,:), C1(1:3,:)];
  rng(3); [lab, ~] = kmeans(X', 2, 'Replicates', 3, 'MaxIter', 100);
  n0 = size(C0,2);
  VH = zeros(6,2);
  for h = 1:2
    B0 = C0(:, lab(1:n0)==h); B1 = C1(:, lab(n0+1:end)==h);
    VH(:,h) = fit_single(B0, B1);
    [dd, rr, pp] = score_vs_shipped(VH(:,h), SHIP);
    fprintf('V3c-a P%02d half%d n=(%d,%d) (%.2f,%.2f) %s\n', frag, h, ...
      size(B0,2), size(B1,2), dd(1), rr(1), passstr(all(pp)));
  end
  [dd, rr] = axis_pair_errors(VH(:,1), VH(:,2));
  fprintf('V3c-a P%02d half-vs-half (%.2f,%.2f)\n', frag, dd, rr);
end
[Q0, Q1] = read_surfaces('A', 1);
SH = readmatrix([AXD '/Pot_A_Piece_01_Axis.xyz'], 'FileType','text');
[VD, ~] = af_find_all(Q0(:,1:10:end), Q1(:,1:10:end), 0);
[dd, rr, pp] = score_vs_shipped(VD, SH);
fprintf('V3c-b uniform1:10 n=(%d,%d) (%.2f,%.2f) %s\n', size(Q0,2)/10, size(Q1,2)/10, ...
  dd(1), rr(1), passstr(all(pp)));
X = [Q0(1:3,:), Q1(1:3,:)];
x0 = median(X(1,:));
for w = [15 30]
  sel = abs(X(1,:) - x0) <= w;
  n0 = size(Q0,2);
  [VS, ~] = af_find_all(Q0(:,sel(1:n0)), Q1(:,sel(n0+1:end)), 0);
  [dd, rr, pp] = score_vs_shipped(VS, SH);
  fprintf('V3c-b slab%d n=(%d,%d) nset=%d (%.2f,%.2f) %s\n', w, sum(sel(1:n0)), ...
    sum(sel)-sum(sel(1:n0)), size(VS,2), dd(1), rr(1), passstr(all(pp)));
end
[C2, D2] = read_surfaces('A', 2);
SH2 = readmatrix([AXD '/Pot_A_Piece_02_Axis.xyz'], 'FileType','text');
v = fit_single(C2, D2);
for it = 1:8
  [m0, m1, n] = af_inliers(v, C2, D2, [true, false], 1.0);
  v = af_refine_raw(v, C2(:,m0), D2(:,m1), [true, false], 1, 300, 1e-9);
  [dd, rr, pp] = score_vs_shipped(v, SH2);
  if it==1 || it==4 || it==8
    fprintf('V3c-c P02 it%d n=%d (%.2f,%.2f) %s\n', it, n, dd(1), rr(1), passstr(all(pp)));
  end
end
end

function v = fit_single(C0, C1)
[VT, ~] = af_vote(C0, C1, 6000, 0.1, 0, 'raw', 6);
top = VT(:,1);
Cs = {C0, C1}; rev = [false, false];
for q = 1:2
  Rf = compute_cao_error(top, Cs{q}, false);
  Rr = compute_cao_error(top, Cs{q}, true);
  cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
  cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
  rev(q) = cr < cf;
end
v = af_refine_raw(top, C0, C1, rev, 1, 300, 1e-9);
end

function [dd, rr] = axis_pair_errors(a, b)
da = a(1:3)/norm(a(1:3)); db = b(1:3)/norm(b(1:3));
dd = acosd(min(1, abs(da'*db)));
pa = a(4:6); pb = b(4:6);
w = pb - pa; w = w - da*(da'*w);
rr = norm(w);
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
