function [F0, F1] = af_freeze_weights(vt, C0, C1)
% AF_FREEZE_WEIGHTS confidence-balance weights evaluated ONCE at the vote
% winner: F = |T3| per point (normals parallel to the axis carry no angular
% information). Surfaces balanced by counts so neither dominates.
[~, ~, ~, T0] = af_parts(vt, C0);
[~, ~, ~, T1] = af_parts(vt, C1);
F0 = min(T0, 1) / size(C0, 2);
F1 = min(T1, 1) / size(C1, 2);
end
