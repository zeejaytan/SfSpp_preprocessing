function [refused, cost_pt, share, best_n, topcost] = af_gate(C0, C1, seed, cost_thr, share_thr)
% AF_GATE POTA-18 refusal gate probe (finder-observable only, no shipped key).
% Replicates af_find_seq round-1 EXACTLY on the full cloud (vote 6000/raw,
% seed+1; cluster top-1000 with maxk=1; orient; refine top-1 sub then full;
% tight-inlier count), then:
%   refused = (cost_pt > cost_thr) && (share < share_thr)
% cost_pt = vote-best raw GM cost per subsample point (CR(1)/nS, same 10%
% subsample af_vote scores); share = best_n/N0 (refined round-1 winner tight
% inliers over the full cloud). Defaults: seed=0, cost_thr=1.4, share_thr=0.20.
% Lives in the run dir, NOT in axle_finder/ (frozen dir untouched).
if nargin < 3 || isempty(seed), seed = 0; end
if nargin < 4 || isempty(cost_thr), cost_thr = 1.4; end
if nargin < 5 || isempty(share_thr), share_thr = 0.20; end
N0 = size(C0,2) + size(C1,2);
[VT, CR] = af_vote(C0, C1, 6000, 0.1, seed+1, 'raw', 6);
% Subsample size, same construction as af_vote (demean/normalise copies).
C0n = C0; C1n = C1;
C0n(4:6,:) = C0n(4:6,:) ./ sqrt(sum(C0n(4:6,:).^2));
C1n(4:6,:) = C1n(4:6,:) ./ sqrt(sum(C1n(4:6,:).^2));
nS = size(C0n(:,1:10:end),2) + size(C1n(:,1:10:end),2);
topcost = CR(1);
cost_pt = topcost / nS;
K = min(1000, size(VT,2));
[VC, ~, ~] = af_cluster(VT(:,1:K), CR(1:K), 10, 2, 1.5, 1);
Cs = {C0, C1}; rev = [false, false];
for q = 1:2
  Rf = compute_cao_error(VC(:,1), Cs{q}, false);
  Rr = compute_cao_error(VC(:,1), Cs{q}, true);
  cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
  cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
  rev(q) = cr < cf;
end
v1 = af_refine_raw(VC(:,1), C0(:,1:10:end), C1(:,1:10:end), rev, 1, 300, 1e-3);
v = af_refine_raw(v1, C0, C1, rev, 1, 300, 1e-9);
[~, ~, best_n] = af_inliers(v, C0, C1, rev);
share = best_n / N0;
refused = (cost_pt > cost_thr) && (share < share_thr);
end
