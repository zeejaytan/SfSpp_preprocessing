% POTA-10: frozen (a)-finder cross-pot run (pots B-J). NO tuning.
% Direct Surfaces/Axes loading (read_surfaces shim is Pot-A-only).
% Shipped axles are the test key only, never finder input.
% Bar: direction <=5deg strict everywhere; position reported (position-conditional).
function p10_run(pot, frags)
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p10-run/axle_finder';
SURD ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
nDir=0; nStrict=0; n=0;
for frag = frags
  C0 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_0.xyz', SURD, pot, frag), 'FileType','text')'; C0=C0(1:6,:);
  C1 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_1.xyz', SURD, pot, frag), 'FileType','text')'; C1=C1(1:6,:);
  SHIP = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Axis.xyz', AXD, pot, frag), 'FileType','text');
  tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); tA = toc;
  if isempty(VOUT)
    dd = inf(size(SHIP,1),1); rr = inf(size(SHIP,1),1); pp = false(size(SHIP,1),1);
    cnts = '';
  else
    [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
    cnts = num2str(NOUT','%d ');
  end
  dirpass = all(dd <= 5);
  fprintf('P10 %s P%02d chain nset=%d nans=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] strict=%s dirpass=%s\n', ...
    pot, frag, size(VOUT,2), size(SHIP,1), cnts, tA, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)), passstr(dirpass));
  n=n+1; nDir=nDir+dirpass; nStrict=nStrict+all(pp);
end
fprintf('P10 %s SUMMARY ran=%d dirpass=%d strict=%d\n', pot, n, nDir, nStrict);
end
function s = passstr(ok)
if ok, s='PASS'; else, s='FAIL'; end
end
