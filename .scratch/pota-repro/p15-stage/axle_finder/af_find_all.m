function [VOUT, NOUT] = af_find_all(C0, C1, seed)
% AF_FIND_ALL frozen finder assembly (V2): spatial split (eps 10mm) into
% components -> sequential peel (vote 6pt/6000 raw, refine top-1 mode,
% winner by inlier count, minfrac 10%, maxK 4) per component -> union ->
% position-aware dedup (10deg/2mm). Sorted by inlier count descending.
if nargin < 3 || isempty(seed), seed = 0; end
C = [C0, C1]; NS = [size(C0,2), size(C1,2)];
[comp, ~] = af_split(C, 10, 300);
VALL = zeros(6,0); NALL = [];
for c = 1:max(comp)
  idx = find(comp == c);
  i0 = idx(idx <= NS(1)); i1 = idx(idx > NS(1)) - NS(1);
  if numel(i0) < 100 || numel(i1) < 100, continue; end
  [VV, NN] = af_find_seq(C0(:,i0), C1(:,i1), seed, 4, 0.10, 6000, 1);
  VALL = [VALL, VV]; NALL = [NALL; NN];
end
if isempty(VALL), VOUT = VALL; NOUT = NALL; return; end
% final polish per mode, recount, sort, dedup
for k = 1:size(VALL,2)
  VALL(:,k) = af_polish(VALL(:,k), C0, C1);
end
NALL = zeros(size(VALL,2),1);
for k = 1:size(VALL,2)
  [~, ~, NALL(k)] = af_inliers(VALL(:,k), C0, C1, af_orient(VALL(:,k), C0, C1), 1.0);
end
[~, order] = sort(NALL, 'descend');
VS = VALL(:, order); NS2 = NALL(order);
[VOUT, NOUT] = af_cluster_inl(VS, NS2);
end

function [VO, NO] = af_cluster_inl(VS, NS2)
% Geometric dedup on inlier-sorted modes (peel's minfrac is already the
% count gate; here only the x1.1 near-tie rule + 10deg/2mm geometry).
cang = cosd(10);
keep = true(1, size(VS,2)); kept = [];
for i = 1:size(VS,2)
  if NS2(i) < NS2(1)/1.1, keep(i) = false; continue; end
  di = VS(1:3,i)/norm(VS(1:3,i)); pi_ = VS(4:6,i);
  dup = false;
  for j = kept
    dj = VS(1:3,j)/norm(VS(1:3,j)); pj = VS(4:6,j);
    if abs(di'*dj) > cang
      w = pi_ - pj; w = w - dj*(dj'*w);
      if norm(w) <= 2, dup = true; break; end
    end
  end
  if dup, keep(i) = false; else, kept = [kept, i]; end
  if numel(kept) >= 6, keep(i+1:end) = false; break; end
end
VO = VS(:, keep); NO = NS2(keep);
end
