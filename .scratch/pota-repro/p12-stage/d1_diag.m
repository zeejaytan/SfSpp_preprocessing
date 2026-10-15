% POTA-12 D1: cost-landscape diagnostic on FIT pieces 01-04 only.
% Sealed pieces 05-08 are never loaded here.
function d1_diag()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, AFD);
widths = [0.05, 0.1, 0.2];
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  N0 = size(C0,2); N1 = size(C1,2);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  ds = SHIP(1,4:6)'; ds = ds/norm(ds); ps = SHIP(1,1:3)';
  ps = ps - ds*(ds'*ps);
  vt0 = [ds; ps];
  C = [C0, C1];
  % raw-GM saturation at shipped (patched pristine path, read-only)
  Cb = compute_biaxial_cao_error(vt0, C);
  sq = sum(Cb.^2, 1);
  Rh = robustifier_gm(sq);
  satfrac = mean(Rh(2,:) < 0.05);
  [~, ~, nT2, nT3] = af_parts(vt0, C);
  fprintf('D1 P%02d N0=%d N1=%d | rawGM satfrac=%.3f medsq=%.3g | nT2 med=%.0f p10=%.0f | nT3 med=%.2f p10=%.2f\n', ...
    frag, N0, N1, satfrac, median(sq), median(nT2), prctile(nT2,10), median(nT3), prctile(nT3,10));
  B = null(ds'); u1 = B(:,1);
  offs = [1 2 3 5 8]; tilts = [1 2 3 5 8 12];
  for w = widths
    c0 = af_wcost(vt0, C0, C1, w);
    pm = zeros(size(offs)); dm = zeros(size(tilts));
    for k = 1:numel(offs)
      v = vt0; v(4:6) = vt0(4:6) + offs(k)*u1;
      pm(k) = 100*(af_wcost(v,C0,C1,w)/c0 - 1);
    end
    for k = 1:numel(tilts)
      th = tilts(k)*pi/180;
      dv = ds*cos(th) + u1*sin(th); dv = dv/norm(dv);
      pv = ps - dv*(dv'*ps);
      dm(k) = 100*(af_wcost([dv;pv],C0,C1,w)/c0 - 1);
    end
    rnk = af_rank(vt0, C0, C1, w);
    fprintf('  w=%.2f c0=%.5f pos%%@[1 2 3 5 8]=[%s] dir%%@[1 2 3 5 8 12]=[%s] rank=%d/200\n', ...
      w, c0, num2str(pm,'%.1f '), num2str(dm,'%.1f '), rnk);
  end
  % radius-arm +1 / -1 at w=0.1
  for ra = [1 -1]
    c0 = af_wcost(vt0, C0, C1, 0.1, ra);
    v = vt0; v(4:6) = vt0(4:6) + 5*u1;
    pm5 = 100*(af_wcost(v,C0,C1,0.1,ra)/c0 - 1);
    th = 5*pi/180; dv = ds*cos(th)+u1*sin(th); dv=dv/norm(dv); pv = ps-dv*(dv'*ps);
    dm5 = 100*(af_wcost([dv;pv],C0,C1,0.1,ra)/c0 - 1);
    rnk = af_rank(vt0, C0, C1, 0.1, ra);
    fprintf('  w=0.10 rarm=%+d c0=%.5f pos%%@5=%.1f dir%%@5=%.1f rank=%d/200\n', ra, c0, pm5, dm5, rnk);
  end
end
end

function rnk = af_rank(vt0, C0, C1, w, rarm)
if nargin < 5, rarm = 0; end
rng(1);
c0 = af_wcost(vt0, C0, C1, w, rarm);
B = null(vt0(1:3)'); uu = B(:,1); vv = B(:,2);
Nc = 200; cnt = 0;
for k = 1:Nc
  th = 15*rand()*pi/180; ph = 2*pi*rand();
  ax = uu*cos(ph)+vv*sin(ph);
  dv = vt0(1:3)*cos(th)+ax*sin(th); dv = dv/norm(dv);
  rr = 10*sqrt(rand()); ph2 = 2*pi*rand();
  pv = vt0(4:6)+rr*(uu*cos(ph2)+vv*sin(ph2)); pv = pv - dv*(dv'*pv);
  if af_wcost([dv;pv],C0,C1,w,rarm) < c0, cnt = cnt + 1; end
end
rnk = 1 + cnt;
end
