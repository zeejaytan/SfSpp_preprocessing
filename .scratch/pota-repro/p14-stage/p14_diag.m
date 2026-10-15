% POTA-14: diagnose piece-6's direction miss. DIAGNOSE ONLY — no finder edits.
% H1 base-fragment: curvature/normal profile of P06 vs wall pieces 01-05.
% H2 disjoint sub-parts: af_split component counts on P06 at eps 5/10/20.
% H3 vote poverty: shipped-axle inlier fraction + raw-vote rank/margin of truth.
function p14_diag()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);

fprintf('P14 H1 profile vs wall pieces\n');
for frag = [1 2 3 4 5 6]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  d = SHIP(1,4:6)'; d = d/norm(d); p = SHIP(1,1:3)';
  v = [d; p];
  for q = 1:2
    if q == 1, X = C0; else, X = C1; end
    [~, ~, nT2, nT3] = af_parts(v, X);
    sp = max(X(1:3,:),[],2) - min(X(1:3,:),[],2);
    fprintf('P14-H1 P%02d S%d n=%d span=[%.1f %.1f %.1f] Rmed=%.1f Riqr=%.1f nT3med=%.3f fltFrac=%.3f\n', ...
      frag, q-1, size(X,2), sp(1), sp(2), sp(3), ...
      median(nT2), iqr(nT2), median(nT3), mean(nT3 < 0.3));
  end
end

fprintf('P14 H2 split diagnostics\n');
for frag = [6 5]
  [C0, C1] = read_surfaces('A', frag);
  C = [C0, C1];
  for eps = [5 10 20]
    [comp, ~] = af_split(C, eps, 300);
    pos = comp(comp > 0);
    if isempty(pos)
      fprintf('P14-H2 P%02d eps=%d ncomp=0 sizes=[]\n', frag, eps);
    else
      fprintf('P14-H2 P%02d eps=%d ncomp=%d sizes=[%s]\n', frag, eps, max(comp), num2str(accumarray(pos,1)','%d '));
    end
  end
end

fprintf('P14 H3 vote poverty on P06\n');
[C0, C1] = read_surfaces('A', 6);
SHIP = readmatrix(sprintf('%s/Pot_A_Piece_06_Axis.xyz', AXD), 'FileType','text');
d = SHIP(1,4:6)'; d = d/norm(d); p = SHIP(1,1:3)';
vship = [d; p];
Ntot = size(C0,2) + size(C1,2);
revS = af_orient(vship, C0, C1);
[~, ~, nShip] = af_inliers(vship, C0, C1, revS, 1.0);
fprintf('P14-H3 shipped inliers n=%d frac=%.3f rev=[%d %d]\n', nShip, nShip/Ntot, revS(1), revS(2));

tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); tA = toc;
[dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
fprintf('P14-H3 finder nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s]\n', ...
  size(VOUT,2), num2str(NOUT','%d '), tA, num2str(dd','%.2f '), num2str(rr','%.2f '));
if ~isempty(VOUT)
  fprintf('P14-H3 winner-vs-truth inliers %d vs %d\n', NOUT(1), nShip);
end

[VT, CR] = af_vote(C0, C1, 6000, 0.1, 1, 'raw', 6);
C0n = C0; C1n = C1;
C0n(4:6,:) = C0n(4:6,:) ./ sqrt(sum(C0n(4:6,:).^2));
C1n(4:6,:) = C1n(4:6,:) ./ sqrt(sum(C1n(4:6,:).^2));
S = [C0n(:,1:10:end), C1n(:,1:10:end)];
cb = compute_biaxial_cao_error(vship, S);
costShip = sum(apply_robustifier(@robustifier_gm, cb));
rankShip = 1 + sum(CR < costShip);
fprintf('P14-H3 vote winnerCost=%.4g shipCost=%.4g shipRank=%d/6000 margin=%.3f\n', ...
  CR(1), costShip, rankShip, (costShip - CR(1))/max(costShip,1e-300));
angs = zeros(size(VT,2),1);
for i = 1:size(VT,2)
  di = VT(1:3,i)/norm(VT(1:3,i));
  angs(i) = acosd(min(max(abs(di'*d),-1),1));
end
fprintf('P14-H3 vote minAng=%.2f nWithin5=%d nWithin10=%d\n', min(angs), sum(angs <= 5), sum(angs <= 10));

v1 = af_refine_raw(vship, C0(:,1:10:end), C1(:,1:10:end), revS, 1, 300, 1e-3);
vr = af_refine_raw(v1, C0, C1, revS, 1, 300, 1e-9);
[ddr, rrr, ~] = score_vs_shipped(vr, SHIP);
fprintf('P14-H3 refine-from-shipped derr=%.2f rerr=%.2f\n', ddr(1), rrr(1));
end
