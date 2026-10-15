function [VOUT, NOUT] = af_find_seq(C0, C1, seed, maxK, minfrac, niter, M)
% AF_FIND_SEQ sequential multi-axis finder. Each round: raw-GM vote (6-pt)
% -> cluster top-1000 into <=M diverse modes -> refine each (fixed-orient
% W=1, sub then full) -> POTA-16 (b): winner = min full-residual GM cost
% (vote's own robustifier), not max tight inlier count. Peel winner's
% inliers, repeat. Stops when winner < minfrac of original cloud, or at maxK. Sorted by count desc.
if nargin < 3 || isempty(seed), seed = 0; end
if nargin < 4 || isempty(maxK), maxK = 4; end
if nargin < 5 || isempty(minfrac), minfrac = 0.10; end
if nargin < 6 || isempty(niter), niter = 6000; end
if nargin < 7 || isempty(M), M = 1; end
N0 = size(C0,2) + size(C1,2);
R0 = C0; R1 = C1;
VOUT = zeros(6,0); NOUT = [];
for round = 1:maxK
  if size(R0,2) < 50 || size(R1,2) < 50, break; end
  [VT, CR] = af_vote(R0, R1, niter, 0.1, seed+round, 'raw', 6);
  K = min(1000, size(VT,2));
  [VC, ~, ~] = af_cluster(VT(:,1:K), CR(1:K), 10, 2, 1.5, max(M,1));
  Cs = {R0, R1}; rev = [false, false];
  for q = 1:2
    Rf = compute_cao_error(VC(:,1), Cs{q}, false);
    Rr = compute_cao_error(VC(:,1), Cs{q}, true);
    cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
    cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
    rev(q) = cr < cf;
  end
  % POTA-16 (b): winner by full-residual GM cost (vote's own robustifier),
  % not post-refine tight inlier count. Peel/minfrac machinery unchanged.
  Call = [R0, R1];
  VRm = zeros(6, size(VC,2)); GM = zeros(size(VC,2),1);
  for m = 1:size(VC,2)
    v1 = af_refine_raw(VC(:,m), R0(:,1:10:end), R1(:,1:10:end), rev, 1, 300, 1e-3);
    v = af_refine_raw(v1, R0, R1, rev, 1, 300, 1e-9);
    VRm(:,m) = v;
    cb = compute_biaxial_cao_error(v, Call);
    GM(m) = sum(apply_robustifier(@robustifier_gm, cb));
  end
  [~, wi] = min(GM); best_v = VRm(:,wi);
  [~, ~, best_n] = af_inliers(best_v, R0, R1, rev);
  if best_n < minfrac*N0, break; end
  VOUT = [VOUT, best_v]; NOUT = [NOUT; best_n];
  [m0, m1, ~] = af_inliers(best_v, R0, R1, rev);
  R0 = R0(:, ~m0); R1 = R1(:, ~m1);
end
end
