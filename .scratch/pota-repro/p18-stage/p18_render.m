function p18_render(frags)
% POTA-18 Needs-eye renders: H base-cap fragments with shipped axis/axes drawn.
% Top (camera along first shipped axis) + side (perpendicular) views, mm
% scale, equal aspect, 10mm scale bar. PNGs to <run>/renders/.
MESHD='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
OUTD ='/data/gpfs/projects/punim2657/Temp/potsac-p18-run/renders';
if ~exist(OUTD,'dir'), mkdir(OUTD); end
for frag = frags
  try
    render_one(MESHD, AXD, OUTD, frag);
  catch ME
    fprintf('P18RENDER H P%02d ERROR %s\n', frag, ME.message);
    for k = 1:numel(ME.stack)
      fprintf('P18RENDER STACK %s line %d in %s\n', ME.stack(k).file, ME.stack(k).line, ME.stack(k).name);
    end
  end
end
end

function render_one(MESHD, AXD, OUTD, frag)
[V, F] = read_obj_simple(sprintf('%s/Pot_H_Piece_%02d_Mesh_DS.obj', MESHD, frag));
SHIP = readmatrix(sprintf('%s/Pot_H_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
nA = size(SHIP,1);
ctr = mean(V,1);
d1 = SHIP(1,4:6)/norm(SHIP(1,4:6));   % top view looks along shipped axis 1
tmp = [0 0 1]; if abs(d1*tmp') > 0.9, tmp = [0 1 0]; end
side = tmp - d1*(d1*tmp'); side = side/norm(side);
span = max(max(V,[],1)-min(V,[],1));
L = span/2 + 15;                       % axis half-length (mm)
fig = figure('visible','off','Position',[100 100 1400 700]);
for panel = 1:2
  subplot(1,2,panel);
  patch('Vertices',V,'Faces',F,'FaceColor',[0.75 0.75 0.75],'EdgeColor','none', ...
    'FaceLighting','gouraud','AmbientStrength',0.5);
  hold on; axis equal; grid on;
  cols = lines(max(nA,1));
  for a = 1:nA
    da = SHIP(a,4:6)/norm(SHIP(a,4:6)); pa = SHIP(a,1:3);
    pc = pa - da*(da'*(pa-ctr));       % axis point nearest mesh centre
    P1 = pc - da*L; P2 = pc + da*L;
    plot3([P1(1) P2(1)],[P1(2) P2(2)],[P1(3) P2(3)],'-','Color',cols(a,:),'LineWidth',2);
  end
  if panel == 1
    view(d1); title(sprintf('H%02d top (along shipped ax1), %d shipped axes', frag, nA));
  else
    view(side); title(sprintf('H%02d side (perp ax1), mm, equal aspect', frag));
  end
  xlabel('x (mm)'); ylabel('y (mm)'); zlabel('z (mm)');
  light('Position',[1 1 1]); lighting gouraud;
  mn = min(V,[],1);                     % 10 mm scale bar at data-box corner
  plot3([mn(1) mn(1)+10],[mn(2) mn(2)],[mn(3) mn(3)],'k-','LineWidth',3);
  text(mn(1)+5, mn(2), mn(3), '10 mm');
end
sgtitle(sprintf('H%02d mesh + shipped axes, mm scale, equal aspect', frag));
png = sprintf('%s/H%02d_axis.png', OUTD, frag);
print(fig, png, '-dpng', '-r150');
close(fig);
fprintf('P18RENDER H P%02d wrote %s nA=%d nV=%d nF=%d\n', frag, png, nA, size(V,1), size(F,1));
end

function [V, F] = read_obj_simple(path)
% Minimal Meshlab-OBJ reader: 'v x y z' verts, 'f ...' faces (handles
% 'i//n' tokens and n-gon fans).
fid = fopen(path,'r');
Vs = []; Fs = [];
while true
  ln = fgetl(fid);
  if ~ischar(ln), break; end
  if strncmp(ln,'v ',2)
    vv = sscanf(ln(3:end),'%f %f %f')';
    Vs(end+1,:) = vv(1:3);   % Meshlab writes 'v x y z r g b' — keep xyz only
  elseif strncmp(ln,'f ',2)
    toks = strsplit(strtrim(ln(3:end)));
    idx = zeros(1,numel(toks));
    for k = 1:numel(toks)
      t = toks{k}; sl = find(t=='/',1);
      if isempty(sl), idx(k)=str2double(t); else, idx(k)=str2double(t(1:sl-1)); end
    end
    for k = 2:numel(idx)-1
      Fs(end+1,:) = idx([1 k k+1]);
    end
  end
end
fclose(fid);
V = Vs; F = Fs;
end
