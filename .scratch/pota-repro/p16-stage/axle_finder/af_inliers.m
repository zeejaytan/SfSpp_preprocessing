function [mask0, mask1, n] = af_inliers(v, C0, C1, rev, thr)
% AF_INLIERS tight-residual inlier masks under frozen orientation.
% Inlier iff |R| <= thr (Cao units) on its surface. n = total count.
if nargin < 5 || isempty(thr), thr = 1.0; end
R0 = compute_cao_error(v, C0, rev(1));
R1 = compute_cao_error(v, C1, rev(2));
mask0 = sqrt(sum(R0.^2,1)) <= thr;
mask1 = sqrt(sum(R1.^2,1)) <= thr;
n = sum(mask0) + sum(mask1);
end
