% POTA-15 attempt (a): GM robustifier in af_refine_raw (residual only).
% Fit pieces 01-04 ONLY (05/07/08 sealed, P06 held for confirmation).
% Per piece: refine-from-shipped stability (rev frozen at shipped, sub+full,
% same protocol as p14 H3) + full-chain af_find_all errors. Bar: <=5deg/<=2mm.
function p15a_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p15-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);

okAll = true;
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  d = SHIP(1,4:6)'; d = d/norm(d); p = SHIP(1,1:3)';
  vship = [d; p];
  revS = af_orient(vship, C0, C1);
  % refine-from-shipped (probe: truth must be a fixed point of GM refine)
  v1 = af_refine_raw(vship, C0(:,1:10:end), C1(:,1:10:end), revS, 1, 300, 1e-3);
  vr = af_refine_raw(v1, C0, C1, revS, 1, 300, 1e-9);
  [dds, rrs, pps] = score_vs_shipped(vr, SHIP);
  fprintf('P15a P%02d refine-from-shipped (%.2f,%.2f) %s\n', frag, dds(1), rrs(1), passstr(all(pps)));
  okAll = okAll && all(pps);
  % selection-cost landscape: GM cost at shipped vs at refined (10% subsample, vote protocol)
  C0n = C0; C1n = C1;
  C0n(4:6,:) = C0n(4:6,:) ./ sqrt(sum(C0n(4:6,:).^2));
  C1n(4:6,:) = C1n(4:6,:) ./ sqrt(sum(C1n(4:6,:).^2));
  S = [C0n(:,1:10:end), C1n(:,1:10:end)];
  cS = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(vship, S)));
  cR = sum(apply_robustifier(@robustifier_gm, compute_biaxial_cao_error(vr, S)));
  fprintf('P15a P%02d GMcost ship=%.4g refined=%.4g walk=%s\n', frag, cS, cR, updown(cR <= cS));
  % full chain
  tic; [VOUT, NOUT] = af_find_all(C0, C1, 0); tA = toc;
  [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
  fprintf('P15a P%02d chain nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), num2str(NOUT','%d '), tA, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
  okAll = okAll && all(pp);
end
fprintf('P15a FIT-VERDICT %s\n', passstr(okAll));
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end

function s = updown(ok)
if ok, s = 'down-or-flat'; else, s = 'UP'; end
end
