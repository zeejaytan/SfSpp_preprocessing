function [comp, ncomp] = af_split(C, eps, minpts)
% AF_SPLIT connected components of the point cloud at gap EPS (mm), via
% voxel union-find: non-empty eps-voxels linked under 26-adjacency merge.
% Over-joins parts closer than ~eps (documented best-effort split for
% disjoint multi-part pieces; connected multi-axis handled by peel path).
% Points in components smaller than MINPTS are dropped. COMP = labels.
if nargin < 2 || isempty(eps), eps = 10; end
if nargin < 3 || isempty(minpts), minpts = 300; end
X = C(1:3,:);
key = floor(X/eps);
[uk, ~, bin] = unique(key', 'rows'); % uk M×3, bin N×1 voxel ids
M = size(uk,1);
parent = 1:M;
for s = -1:1
for t = -1:1
for u = -1:1
  if s==0 && t==0 && u==0, continue; end
  [tf, loc] = ismember(uk + [s t u], uk, 'rows');
  for m = find(tf)'
    parent = uf_union(parent, m, loc(m));
  end
end
end
end
for m = 1:M, parent(m) = uf_find(parent, m); end
clab = parent(bin)'; % per-point root
[~, ~, comp] = unique(clab);
ncomp = max(comp);
cnt = accumarray(comp, 1);
small = ismember(comp, find(cnt < minpts));
comp(small) = 0; % 0 = dropped splinters
end

function parent = uf_union(parent, a, b)
ra = uf_find(parent, a); rb = uf_find(parent, b);
if ra ~= rb, parent(rb) = ra; end
end

function r = uf_find(parent, a)
while parent(a) ~= a, a = parent(a); end
r = a;
end
