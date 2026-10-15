function v = af_polish(v0, C0, C1)
% AF_POLISH final polish: hard-IRLS x8 (tight inliers |R|<=1 only, frozen
% orientation, Huber W=1). Evidence: P02 5.17->1.86mm over 8 iters (V3c-c,
% job 33086235); P01/P04 already at floor, unmoved (V3a/V3d).
rev = af_orient(v0, C0, C1);
v = v0;
for it = 1:8
  [m0, m1, ~] = af_inliers(v, C0, C1, rev, 1.0);
  if sum(m0) < 100 || sum(m1) < 100, break; end
  v = af_refine_raw(v, C0(:,m0), C1(:,m1), rev, 1, 300, 1e-9);
end
end
