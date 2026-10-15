% POTA-12 V2d: sequential multi-axis finder on fit data only (05-08 sealed).
% (a) af_find_seq M=1 on 01-04: must give nset=1 (stop criterion check).
% (b) synthetic disjoint 2-axis: seq M=12 direct (compromise-trap probe),
%     then spatial k=2 split + per-cluster seq.
% (c) P01 12-mode: max-inlier vs min-GM-cost agreement.
function v2d_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  tic; [VOUT, NOUT] = af_find_seq(C0, C1, 0, 4, 0.10, 6000, 1); t = toc;
  [dd, rr, pp] = score_vs_shipped(VOUT, SHIP);
  fprintf('V2d-a P%02d nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
    frag, size(VOUT,2), num2str(NOUT','%d '), t, ...
    num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
% synthetic cloud
[C0, C1] = read_surfaces('A', 1);
SHIP1 = readmatrix([AXD '/Pot_A_Piece_01_Axis.xyz'], 'FileType','text');
rng(7);
[Q, ~] = qr(randn(3));
if det(Q) < 0, Q(:,1) = -Q(:,1); end
t = [500; -300; 200];
R = @(X) [Q*X(1:3,:) + t; Q*X(4:6,:)];
d1 = SHIP1(1,4:6)'; d1 = d1/norm(d1); p1 = SHIP1(1,1:3)';
d2 = Q*d1; p2 = Q*p1 + t; p2 = p2 - d2*(d2'*p2); p1 = p1 - d1*(d1'*p1);
S2 = [p1', d1'; p2', d2'];
P0 = C0(:,1:2:end); P1 = C1(:,1:2:end);
A0 = [P0, R(P0)]; A1 = [P1, R(P1)];
tic; [VS, NS] = af_find_seq(A0, A1, 0, 4, 0.10, 6000, 12); t = toc;
if isempty(VS)
  fprintf('V2d-b direct nset=0 time=%.0fs (compromise trap: no round passes minfrac)\n', t);
else
[dd, rr, pp] = score_vs_shipped(VS, S2);
fprintf('V2d-b direct nset=%d counts=[%s] time=%.0fs derr=[%s] rerr=[%s] %s\n', ...
  size(VS,2), num2str(NS','%d '), t, num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
% spatial split probe (script-level, k=2 on positions)
X = [A0(1:3,:), A1(1:3,:)];
[Xc, ~] = kmeans(X', 2, 'Replicates', 3, 'MaxIter', 100);
VALL = zeros(6,0);
for c = 1:2
  n0 = size(A0,2)/2;
  labA0 = Xc(1:2*n0); labA1 = Xc(2*n0+1:end);
  B0 = A0(:, labA0==c); B1 = A1(:, labA1==c);
  [VV, ~] = af_find_seq(B0, B1, 0, 2, 0.10, 6000, 1);
  VALL = [VALL, VV];
end
[dd, rr, pp] = score_vs_shipped(VALL, S2);
fprintf('V2d-b spatial nset=%d derr=[%s] rerr=[%s] %s\n', ...
  size(VALL,2), num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
% (c) P01 mode ranking agreement
[Q0, Q1] = read_surfaces('A', 1);
SH = readmatrix([AXD '/Pot_A_Piece_01_Axis.xyz'], 'FileType','text');
[VT, CR] = af_vote(Q0, Q1, 3000, 0.1, 0, 'raw', 6);
[VC, ~, ~] = af_cluster(VT(:,1:min(1000,end)), CR(1:min(1000,end)), 10, 2, 1.5, 12);
rev = [true, false];
for m = 1:size(VC,2)
  v = af_refine_raw(VC(:,m), Q0, Q1, rev, 1, 300, 1e-9);
  cb = compute_biaxial_cao_error(v, [Q0, Q1]);
  gm = sum(apply_robustifier(@robustifier_gm, cb));
  [~, ~, n] = af_inliers(v, Q0, Q1, rev);
  [dd, rr, ~] = score_vs_shipped(v, SH);
  fprintf('V2d-c mode %2d gm=%.2f inliers=%d err=(%.2f,%.2f)\n', m, gm, n, dd(1), rr(1));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
