function [Rfw, Rrv, nT2, nT3] = af_parts(vt, X)
% AF_PARTS fresh implementation of the Cao residual parts (paper eq. behind
% compute_cao_error, re-derived for axle_finder; pristine file stays untouched).
% vt 6x1 [dir;pos], X 6xn [point;normal]. Returns fwd/rev 3xn residuals and
% per-point norms nT2=|T2| (mm, radius-like) and nT3=|T3| (<=1, normal-vs-axis).
d = vt(1:3)/norm(vt(1:3)); p = vt(4:6);
n = size(X, 2);
D = repmat(d, 1, n); P = repmat(p, 1, n);
T1 = X(1:3,:) - P;
T2 = cross(T1, D, 1);
nT2 = sqrt(sum(T2.^2));
nfw = X(4:6,:); nrv = -nfw;
T3f = cross(nfw, D, 1); T3r = cross(nrv, D, 1);
nT3 = sqrt(sum(T3f.^2)); % identical for rev (sign flip preserves norm)
scl_f = sqrt(sum(T2.^2)) ./ max(sqrt(sum(T3f.^2)), 1e-12);
scl_r = sqrt(sum(T2.^2)) ./ max(sqrt(sum(T3r.^2)), 1e-12);
Rfw = T2 - scl_f .* T3f;
Rrv = T2 - scl_r .* T3r;
end
