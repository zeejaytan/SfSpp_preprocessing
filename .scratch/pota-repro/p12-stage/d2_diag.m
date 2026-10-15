% POTA-12 D2: why does the angular-cost vote winner miss? Fit pieces 01-02.
function d2_diag()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = [1 2]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  ds = SHIP(1,4:6)'; ds = ds/norm(ds); ps = SHIP(1,1:3)'; ps = ps - ds*(ds'*ps);
  vt0 = [ds; ps];
  % (a) residual cross-check mine vs pristine at shipped, 200-pt subset
  Cs = [C0(:,1:200), C1(:,1:200)];
  Rp = compute_cao_error(vt0, Cs);
  [Rm, ~, ~, ~] = af_parts(vt0, Cs);
  fprintf('D2 P%02d max|R_pristine - R_mine| = %.3g\n', frag, max(abs(Rp(:) - Rm(:))));
  % (b) costs: shipped vs vote winner, angular + raw-GM
  [VT, COST] = af_vote(C0, C1, 1000, 0.1, 0);
  cship = af_wcost(vt0, C0(:,1:10:end), C1(:,1:10:end), 0.1);
  Craw = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(VT(:,1), [C0(:,1:10:end), C1(:,1:10:end)])));
  Sraw = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(vt0, [C0(:,1:10:end), C1(:,1:10:end)])));
  fprintf('  angular: ship=%.6f winner=%.6f (rank of ship among vote: %d) | rawGM: ship=%.3f winner=%.3f\n', ...
    cship, COST(1), 1+sum(COST < cship), Sraw, Craw);
  % (c) top-5 winners' errors + population stats
  ngood = 0;
  for k = 1:5
    [dd, rr, ~] = score_vs_shipped(VT(:,k), SHIP);
    fprintf('  top%d: cost=%.6f derr=%.2f rerr=%.2f\n', k, COST(k), dd(1), rr(1));
  end
  for k = 1:1000
    [dd, rr, pp] = score_vs_shipped(VT(:,k), SHIP);
    if all(pp), ngood = ngood + 1; end
  end
  fprintf('  vote population within bar: %d/1000\n', ngood);
  % (d) winner geometry: distance of winner pos from shipped pos, dir angle
  dw = VT(1:3,1)/norm(VT(1:3,1));
  fprintf('  winner |pos-shippos|=%.1fmm winner-nT3med=%.2f ship-nT3med=%.2f\n', ...
    norm(VT(4:6,1)-ps), medT3(VT(:,1),C0,C1), medT3(vt0,C0,C1));
end
end

function m = medT3(vt, C0, C1)
[~, ~, ~, a] = af_parts(vt, C0); [~, ~, ~, b] = af_parts(vt, C1);
m = median([a, b]);
end
