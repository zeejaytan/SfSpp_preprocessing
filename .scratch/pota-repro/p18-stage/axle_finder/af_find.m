function [VOUT, COUT] = af_find(C0, C1, seed)
% AF_FIND the frozen finder (V2 assembly): raw-GM vote (12-pt solves, 3000
% iters) -> position-aware cluster (10deg/2mm, x1.1 cost gate, max 6) ->
% per-cluster fixed-orient W=1 Huber refine (sub then full) -> post-dedup.
% Output set sorted by refined raw-GM cost ascending.
if nargin < 3 || isempty(seed), seed = 0; end
[VT, CR] = af_vote(C0, C1, 3000, 0.1, seed, 'raw', 12);
[VC, ~, ~] = af_cluster(VT, CR, 10, 2, 1.1, 6);
% orientation frozen once at the top cluster (surface property, not axis)
rev = [false, false]; Cs = {C0, C1};
for q = 1:2
  Rf = compute_cao_error(VC(:,1), Cs{q}, false);
  Rr = compute_cao_error(VC(:,1), Cs{q}, true);
  cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
  cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
  rev(q) = cr < cf;
end
K = size(VC,2);
VR = zeros(6,K);
for k = 1:K
  v1 = af_refine_raw(VC(:,k), C0(:,1:10:end), C1(:,1:10:end), rev, 1, 300, 1e-3);
  VR(:,k) = af_refine_raw(v1, C0, C1, rev, 1, 300, 1e-9);
end
Cfull = [C0, C1];
RC = zeros(K,1);
for k = 1:K
  cb = compute_biaxial_cao_error(VR(:,k), Cfull);
  RC(k) = sum(apply_robustifier(@robustifier_gm, cb));
end
[~, order] = sort(RC);
VS = VR(:, order); RCS = RC(order);
[VOUT, COUT, ~] = af_cluster(VS, RCS, 10, 2, 1.1, 6);
end
