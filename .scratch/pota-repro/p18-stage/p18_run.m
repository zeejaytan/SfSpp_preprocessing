function p18_run(pot, frags, cost_thr, share_thr)
% POTA-18: refusal-gate confusion run over B-J. Frozen finder + gate probe only.
% Per piece: gate stats (finder-observable) -> REFUSED skips the chain; else the
% frozen af_find_all chain runs and is scored vs shipped (test key only, for
% the confusion matrix). No tuning, no per-pot adjustments.
if nargin < 3 || isempty(cost_thr), cost_thr = 1.4; end
if nargin < 4 || isempty(share_thr), share_thr = 0.20; end
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p18-run/axle_finder';
P18R ='/data/gpfs/projects/punim2657/Temp/potsac-p18-run';
SURD ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD, P18R);
nRef=0; n=0;
for frag = frags
  C0 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_0.xyz', SURD, pot, frag), 'FileType','text')'; C0=C0(1:6,:);
  C1 = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Surface_1.xyz', SURD, pot, frag), 'FileType','text')'; C1=C1(1:6,:);
  SHIP = readmatrix(sprintf('%s/Pot_%s_Piece_%02d_Axis.xyz', AXD, pot, frag), 'FileType','text');
  tic; [refused, cost_pt, share, best_n, topcost] = af_gate(C0, C1, 0, cost_thr, share_thr); tG = toc;
  if refused
    nRef=nRef+1;
    fprintf('P18 %s P%02d gate costpt=%.3f r1share=%.3f (bestn=%d topcost=%.0f) REFUSED=1 chain=SKIPPED nans=%d time=%.0fs\n', ...
      pot, frag, cost_pt, share, best_n, topcost, size(SHIP,1), tG);
  else
    tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); tA = toc;
    if isempty(VOUT)
      dd = inf(size(SHIP,1),1); rr = inf(size(SHIP,1),1);
      cnts = '';
    else
      [dd, rr, ~] = score_vs_shipped(VOUT, SHIP);
      cnts = num2str(NOUT','%d ');
    end
    dirpass = all(dd <= 5);
    fprintf('P18 %s P%02d gate costpt=%.3f r1share=%.3f (bestn=%d topcost=%.0f) REFUSED=0 chain nset=%d nans=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] dirpass=%s\n', ...
      pot, frag, cost_pt, share, best_n, topcost, size(VOUT,2), size(SHIP,1), cnts, tA, ...
      num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(dirpass));
  end
  n=n+1;
end
fprintf('P18 %s SUMMARY ran=%d refused=%d admitted=%d (thr cost>%.2f share<%.2f)\n', pot, n, nRef, n-nRef, cost_thr, share_thr);
end
function s = passstr(ok)
if ok, s='PASS'; else, s='FAIL'; end
end
