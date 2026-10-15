% POTA-17 H3 fragment-type probe (diagnostic only).
% Per surface: angle(mean normal, shipped axis dir), radial profile to the
% shipped axis, and tight-inlier share at held truth per surface (which
% surface carries the support?). Shipped axes = measurement reference only.
function p17_type(reqs)
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
      fprintf('P17TYPE %s P%02d ERROR %s\n', pot, frag, ME.message);
    end
  end
end
end

function run_one(pot, frag, SURD, AXD)
C0 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_0.xyz', SURD, pot, frag), 'FileType','text')'; C0 = C0(1:6,:);
C1 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_1.xyz', SURD, pot, frag), 'FileType','text')'; C1 = C1(1:6,:);
SHIP = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Axis.xyz', AXD, pot, frag), 'FileType','text');
Cs = {C0, C1};
for a = 1:size(SHIP,1)
  d = SHIP(a,4:6)'/norm(SHIP(a,4:6)); p = SHIP(a,1:3)';
  v = [d; p];
  rev = af_orient(v, C0, C1);
  v1 = af_refine_raw(v, C0(:,1:10:end), C1(:,1:10:end), rev, 1, 300, 1e-3);
  vr = af_refine_raw(v1, C0, C1, rev, 1, 300, 1e-9);
  line = sprintf('P17TYPE %s P%02d ax%d rev=[%d %d]', pot, frag, a, rev(1), rev(2));
  for q = 1:2
    Cq = Cs{q};
    Nq = Cq(4:6,:)./max(vecnorm(Cq(4:6,:)),eps);
    mn = mean(Nq,2); mn = mn/norm(mn);
    nang = acosd(min(1,abs(mn'*d))); % 90 = wall-like, 0/180 = base-like
    W = Cq(1:3,:) - p; ax = d'*W; rad = vecnorm(W - d*ax);
    Rq = compute_cao_error(vr, Cq, rev(q));
    inlf = mean(sqrt(sum(Rq.^2,1)) <= 1.0);
    line = sprintf('%s | S%d nang=%.1f rad=[%.1f %.1f %.1f] axext=%.1f inlf=%.3f', ...
      line, q-1, nang, min(rad), median(rad), max(rad), max(ax)-min(ax), inlf);
  end
  fprintf('%s\n', line);
end
end
