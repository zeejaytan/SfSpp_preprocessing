function [VC, CC, kept] = af_cluster(VT, COST, ang_deg, pos_mm, maxcost_ratio, maxk)
% AF_CLUSTER position-aware dedup. Paper drops pairs with angle<=10deg by the
% higher cost; that merges parallel-but-offset axes (kills multi-axis pieces).
% Distinct iff angle > ang_deg OR radial offset > pos_mm. Keeps cost <
% maxcost_ratio*best, caps at maxk. VT sorted by COST ascending on entry.
if nargin < 3 || isempty(ang_deg), ang_deg = 10; end
if nargin < 4 || isempty(pos_mm), pos_mm = 2; end
if nargin < 5 || isempty(maxcost_ratio), maxcost_ratio = 1.1; end
if nargin < 6 || isempty(maxk), maxk = 6; end
cang = cosd(ang_deg);
keep = true(1, size(VT,2));
kept = [];
for i = 1:size(VT,2)
  if COST(i) > COST(1)*maxcost_ratio, keep(i) = false; continue; end
  di = VT(1:3,i)/norm(VT(1:3,i)); pi_ = VT(4:6,i);
  dup = false;
  for j = kept
    dj = VT(1:3,j)/norm(VT(1:3,j)); pj = VT(4:6,j);
    if abs(di'*dj) > cang
      w = pi_ - pj; w = w - dj*(dj'*w); % radial offset of i from axis j
      if norm(w) <= pos_mm, dup = true; break; end
    end
  end
  if dup, keep(i) = false; else, kept = [kept, i]; end
  if numel(kept) >= maxk
    keep(i+1:end) = false; break;
  end
end
VC = VT(:, keep); CC = COST(keep);
end
