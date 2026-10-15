function c = af_wcost(vt, C0, C1, w, rarm)
% AF_WCOST normalized-angular biaxial GM cost with surface balance.
% Per point: angular residual q = softmin over fwd/rev of |R|/|T2| (bounded,
% scale-free; the |T3|->0 blowup cancels in the ratio). Confidence weight
% conf=|T3| (normals parallel to the axis carry no angular information).
% Each surface contributes its confidence-weighted mean (counts can't dominate),
% cost = mean of the two surfaces. GM width w (default 0.1 ~= sine of ~6deg).
% rarm: optional radius-arm exponent (0 = off; +1 weights by r/medR).
if nargin < 4 || isempty(w), w = 0.1; end
if nargin < 5 || isempty(rarm), rarm = 0; end
tau2 = w*w; s = 100;
cs = zeros(1,2); Cs = {C0, C1};
for q = 1:2
  X = Cs{q}; n = size(X,2);
  [Rfw, Rrv, nT2, nT3] = af_parts(vt, X);
  den = max(nT2, 5); % points within 5mm of the axis: clamp, don't explode
  qf = sum((Rfw ./ den).^2, 1);
  qr = sum((Rrv ./ den).^2, 1);
  cm = min(qf, qr);
  qq = -1/s*log(exp(s*-(qf-cm)) + exp(s*-(qr-cm))) + cm;
  rho = 2*qq*tau2 ./ (qq + tau2); % GM rho (matches robustifier_gm row 1)
  conf = min(nT3, 1);
  if rarm ~= 0
    r = max(nT2, 5); med = median(r);
    conf = conf .* (r/med).^rarm;
  end
  cs(q) = sum(conf .* rho) / max(sum(conf), 1e-12);
end
c = mean(cs);
end
