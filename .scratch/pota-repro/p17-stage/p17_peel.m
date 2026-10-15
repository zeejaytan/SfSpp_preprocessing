% POTA-17 H2 vote-dilution / refine-degeneracy probe (diagnostic only).
% Replicates af_find_seq round logic with printed traces, plus shipped-axis
% probes (vote rank, refine-from-shipped hold, tight-inlier fraction).
% Shipped axes are a measurement reference only — never finder input.
% Finder code itself is untouched (this file re-implements the round loop
% read-only on top of the frozen af_* functions).
function p17_peel(reqs)
PRIST = '/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX = '/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM  = '/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R  = '/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD   = '/data/gpfs/projects/punim2657/Temp/potsac-p10-run/axle_finder';
SURD  = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces';
AXD   = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for r = 1:size(reqs,1)
  pot = reqs{r,1}; frags = reqs{r,2};
  for frag = frags
    try
      run_one(pot, frag, SURD, AXD);
    catch ME
      fprintf('P17PEEL %s P%02d ERROR %s\n', pot, frag, ME.message);
    end
  end
end
end

function run_one(pot, frag, SURD, AXD)
C0 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_0.xyz', SURD, pot, frag), 'FileType','text')'; C0 = C0(1:6,:);
C1 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_1.xyz', SURD, pot, frag), 'FileType','text')'; C1 = C1(1:6,:);
SHIP = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Axis.xyz', AXD, pot, frag), 'FileType','text');
N0 = size(C0,2) + size(C1,2);
minfracN = 0.10*N0;
fprintf('P17PEEL %s P%02d N0=%d minfracN=%.0f nans=%d\n', pot, frag, N0, minfracN, size(SHIP,1));
% ---- shipped probes (diagnostic reference) ----
for a = 1:size(SHIP,1)
  v = [SHIP(a,4:6)'; SHIP(a,1:3)']; % SHIP rows are [pos dir]; finder vecs are [dir;pos]
  cb = compute_biaxial_cao_error(v, [C0, C1]);
  gship = sum(apply_robustifier(@robustifier_gm, cb));
  rev = af_orient(v, C0, C1);
  v1 = af_refine_raw(v, C0(:,1:10:end), C1(:,1:10:end), rev, 1, 300, 1e-3);
  vr = af_refine_raw(v1, C0, C1, rev, 1, 300, 1e-9);
  [dd, rr] = axerr(vr, v);
  [~, ~, ninl] = af_inliers(vr, C0, C1, rev);
  fprintf('P17PEEL %s P%02d ship%d gship=%.0f rev=[%d %d] hold=(%.2fdeg,%.2fmm) inlf %.4f\n', ...
    pot, frag, a, gship, rev(1), rev(2), dd, rr, ninl/N0);
end
% ---- peel rounds (af_find_seq mirror, M=1) ----
R0 = C0; R1 = C1; seed = 0;
for round = 1:4
  if size(R0,2) < 50 || size(R1,2) < 50
    fprintf('P17PEEL %s P%02d round%d STOP-cloud (%d,%d pts)\n', pot, frag, round, size(R0,2), size(R1,2)); break;
  end
  [VT, CR] = af_vote(R0, R1, 6000, 0.1, seed+round, 'raw', 6);
  K = min(1000, size(VT,2));
  [VC, ~, ~] = af_cluster(VT(:,1:K), CR(1:K), 10, 2, 1.5, 1);
  % vote-rank of each shipped axis in THIS round's vote costs
  rk = zeros(size(SHIP,1),1);
  for a = 1:size(SHIP,1)
    va = [SHIP(a,4:6)'; SHIP(a,1:3)'];
    cb = compute_biaxial_cao_error(va, [R0, R1]);
    g = sum(apply_robustifier(@robustifier_gm, cb));
    rk(a) = 1 + sum(CR < g);
  end
  rev = af_orient(VC(:,1), R0, R1);
  v1 = af_refine_raw(VC(:,1), R0(:,1:10:end), R1(:,1:10:end), rev, 1, 300, 1e-3);
  v = af_refine_raw(v1, R0, R1, rev, 1, 300, 1e-9);
  [~, ~, best_n] = af_inliers(v, R0, R1, rev);
  fprintf('P17PEEL %s P%02d round%d winner_n=%d (%.3f of N0) shiprank=[%s] topcost=%.0f\n', ...
    pot, frag, round, best_n, best_n/N0, num2str(rk','%d '), CR(1));
  if best_n < minfracN
    fprintf('P17PEEL %s P%02d round%d STOP-minfrac\n', pot, frag, round); break;
  end
  [m0, m1, ~] = af_inliers(v, R0, R1, rev);
  R0 = R0(:, ~m0); R1 = R1(:, ~m1);
end
% ---- full-chain nset for dedup-kill accounting ----
[VOUT, NOUT] = af_find_all(C0, C1, 0);
fprintf('P17PEEL %s P%02d chain nset=%d counts=[%s]\n', pot, frag, size(VOUT,2), num2str(NOUT','%d '));
end

function [dd, rr] = axerr(a, b)
da = a(1:3)/norm(a(1:3)); db = b(1:3)/norm(b(1:3));
dd = acosd(min(1, abs(da'*db)));
w = a(4:6) - b(4:6); w = w - db*(db'*w);
rr = norm(w);
end
