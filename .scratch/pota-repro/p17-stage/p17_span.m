% POTA-17 H1 span-floor probe (diagnostic only, NOT finder input).
% Per-piece shape-span metrics for H (all), G (all), D (all), J (all),
% A (reference). Shipped axes used ONLY as a measurement reference
% (radial/axial extent around truth) — never fed to any finder.
% One line per piece: counts, bbox, PCA eigvals, planarity, normal
% spread, split behaviour, radial/axial extent vs shipped axis 1.
function p17_span(reqs)
SURD = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces';
AXD  = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath('/data/gpfs/projects/punim2657/Temp/potsac-p10-run/axle_finder');
for r = 1:size(reqs,1)
  pot = reqs{r,1}; frags = reqs{r,2};
  for frag = frags
    f0 = sprintf('%s/Pot_%s_Piece_%02d_Surface_0.xyz', SURD, pot, frag);
    f1 = sprintf('%s/Pot_%s_Piece_%02d_Surface_1.xyz', SURD, pot, frag);
    fa = sprintf('%s/Pot_%s_Piece_%02d_Axis.xyz', AXD, pot, frag);
    if ~isfile(f0) || ~isfile(f1)
      fprintf('P17SPAN %s P%02d MISSING\n', pot, frag); continue;
    end
    C0 = readmatrix(f0, 'FileType','text')'; C0 = C0(1:6,:);
    C1 = readmatrix(f1, 'FileType','text')'; C1 = C1(1:6,:);
    n0 = size(C0,2); n1 = size(C1,2);
    X = [C0(1:3,:) C1(1:3,:)];
    bb = max(X,[],2) - min(X,[],2);          % bbox extents
    Xc = X - mean(X,2);
    L = sort(eig(Xc*Xc'/size(X,2)), 'descend')';  % PCA eigvals l1>=l2>=l3
    planar = L(3)/max(sum(L),eps);             % 0=volumetric/linear .. small=flat
    lin = (L(1)-L(2))/max(L(1),eps);           % near 1 = stick-like
    N0 = C0(4:6,:)./max(vecnorm(C0(4:6,:)),eps);
    N1 = C1(4:6,:)./max(vecnorm(C1(4:6,:)),eps);
    R0 = norm(mean(N0,2)); R1 = norm(mean(N1,2));  % 1 = parallel normals (flat)
    C = [C0, C1];
    [comp, nc] = af_split(C, 10, 300);
    keptfrac = mean(comp > 0);
    ncomp = nc - any(comp==0);                 % non-splinter components
    % radial/axial extent around shipped axis 1 (diagnostic reference only)
    if isfile(fa)
      SHIP = readmatrix(fa, 'FileType','text');
      nans = size(SHIP,1);
      d = SHIP(1,4:6)/norm(SHIP(1,4:6)); p = SHIP(1,1:3);
      W = X - p(:); ax = d(:)'*W; rad = vecnorm(W - d(:)*ax);
      radmax = max(rad); radmed = median(rad); axext = max(ax)-min(ax);
    else
      nans = -1; radmax = NaN; radmed = NaN; axext = NaN;
    end
    fprintf(['P17SPAN %s P%02d n=[%d %d] nans=%d bbox=[%.1f %.1f %.1f] ' ...
      'eig=[%.1f %.1f %.1f] planar=%.4f lin=%.3f R=[%.3f %.3f] ' ...
      'split_ncomp=%d kept=%.2f radmax=%.1f radmed=%.1f axext=%.1f\n'], ...
      pot, frag, n0, n1, nans, bb(1), bb(2), bb(3), L(1), L(2), L(3), ...
      planar, lin, R0, R1, ncomp, keptfrac, radmax, radmed, axext);
  end
end
end
