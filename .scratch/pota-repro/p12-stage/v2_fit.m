% POTA-12 V2: search + position-aware dedup on fit data only (05-08 sealed).
% (a) sampling study on P02/P04: (npts, iters) population quality + raw-top1.
% (b) af_find on 01-04: set size, top-1 errors, set errors, pass.
% (c) synthetic 2-axis: P01 + rigid-transformed P01 copy (fit data only);
% finder must return both axes within bar.
function v2_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
% (a) sampling study
for frag = [2 4]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  for cfg = [6 1000; 12 1000; 12 3000; 24 3000]'
    [VT, ~] = af_vote(C0, C1, cfg(2), 0.1, 0, 'raw', cfg(1));
    ng = 0;
    for k = 1:cfg(2)
      [~, ~, pp] = score_vs_shipped(VT(:,k), SHIP);
      if all(pp), ng = ng + 1; end
    end
    [dd, rr, pp] = score_vs_shipped(VT(:,1), SHIP);
    fprintf('V2a P%02d %2dpt/%4dit: in-bar %d/%d top1 (%.2f,%.2f) %s\n', ...
      frag, cfg(1), cfg(2), ng, cfg(2), dd(1), rr(1), passstr(all(pp)));
  end
end
% (b) full finder on 01-04
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  tic; [VOUT, ~] = af_find(C0, C1, 0); t = toc;
  [d1, r1, p1] = score_vs_shipped(VOUT(:,1), SHIP);
  [ds, rs, ps] = score_vs_shipped(VOUT, SHIP);
  fprintf('V2b P%02d nset=%d time=%.0fs top1 (%.2f,%.2f) %s | set derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), t, d1(1), r1(1), passstr(all(p1)), ...
    num2str(ds','%.2f '), num2str(rs','%.2f '), passstr(all(ps)));
end
% (c) synthetic 2-axis from P01 only
[C0, C1] = read_surfaces('A', 1);
SHIP1 = readmatrix(sprintf('%s/Pot_A_Piece_01_Axis.xyz', AXD, 1), 'FileType','text');
rng(7);
[Q, ~] = qr(randn(3));
if det(Q) < 0, Q(:,1) = -Q(:,1); end
t = [500; -300; 200];
R = @(X) [Q*X(1:3,:) + t; Q*X(4:6,:)];
D0 = [C0, C1]; D1 = R(D0);
M0 = [C0(:,1:2:end), C1(:,1:2:end)]; M1 = R(M0); % halve density (keep runtime sane)
d1 = SHIP1(1,4:6)'; d1 = d1/norm(d1); p1 = SHIP1(1,1:3)';
d2 = Q*d1; p2 = Q*p1 + t; p2 = p2 - d2*(d2'*p2); p1 = p1 - d1*(d1'*p1);
S2 = [p1', d1'; p2', d2'];
P0 = C0(:,1:2:end); P1 = C1(:,1:2:end);
A0 = [P0, R(P0)]; A1 = [P1, R(P1)];
tic; [VOUT, ~] = af_find(A0, A1, 0); t = toc;
[dd, rr, pp] = score_vs_shipped(VOUT, S2);
fprintf('V2c synth2axis nset=%d time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
  size(VOUT,2), t, num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
