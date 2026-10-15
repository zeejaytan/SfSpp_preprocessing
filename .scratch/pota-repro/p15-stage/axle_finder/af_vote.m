function [VT, COST, CRAw] = af_vote(C0, C1, niter, w, seed, mode, npts)
% AF_VOTE MLESAC-style vote. Minimal 6-point Pottmann solver = pristine
% compute_pottmann_axis (read-only reuse, paper's solver); demean/rescale
% protocol mirrors the paper chain. npts>=6 points per solve (default 6;
% larger sets = least-squares Pottmann, same M-matrix, less sample noise).
% mode 'angular' (default): rank by af_wcost on the 10% subsample.
% mode 'raw': rank by raw GM-robustified biaxial Cao cost (paper chain's
% statistic, global shape); CRAw returns the angular cost of each candidate
% in raw-ranked order for staged selection.
if nargin < 3 || isempty(niter), niter = 1000; end
if nargin < 4 || isempty(w), w = 0.1; end
if nargin < 5 || isempty(seed), seed = 0; end
if nargin < 6 || isempty(mode), mode = 'angular'; end
if nargin < 7 || isempty(npts), npts = 6; end
rng(seed);
C0n = C0; C1n = C1;
C0n(4:6,:) = C0n(4:6,:) ./ sqrt(sum(C0n(4:6,:).^2));
C1n(4:6,:) = C1n(4:6,:) ./ sqrt(sum(C1n(4:6,:).^2));
S0 = C0n(:,1:10:end); S1 = C1n(:,1:10:end);
S = [S0, S1]; n = size(S,2);
VT = zeros(6, niter);
for iter = 1:niter
  k = randsample(n, npts);
  Xs = S(:,k);
  m = mean(Xs(1:3,:), 2);
  Xs(1:3,:) = Xs(1:3,:) - m;
  sc = mean(abs(Xs(:)));
  Xs(1:3,:) = Xs(1:3,:) / sc;
  v = compute_pottmann_axis(Xs);
  v(4:6) = v(4:6)*sc + m;
  v(4:6) = v(4:6) - v(1:3)*(v(1:3)'*v(4:6));
  VT(:,iter) = v;
end
COST = zeros(niter,1);
if strcmp(mode, 'raw')
  for iter = 1:niter
    cb = compute_biaxial_cao_error(VT(:,iter), S);
    COST(iter) = sum(apply_robustifier(@robustifier_gm, cb));
  end
else
  for iter = 1:niter
    COST(iter) = af_wcost(VT(:,iter), S0, S1, w);
  end
end
[COST, ia] = sort(COST);
VT = VT(:, ia);
CRAw = zeros(niter,1);
if nargout > 2
  for iter = 1:niter
    CRAw(iter) = af_wcost(VT(:,iter), S0, S1, w);
  end
end
end
