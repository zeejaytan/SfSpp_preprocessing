function p18_probemesh()
MESHD='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh';
p = sprintf('%s/Pot_H_Piece_01_Mesh_DS.obj', MESHD);
fid = fopen(p,'r');
Vs = []; Fs = [];
while true
  ln = fgetl(fid);
  if ~ischar(ln), break; end
  if strncmp(ln,'v ',2)
    Vs(end+1,:) = sscanf(ln(3:end),'%f %f %f')';
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
fprintf('PROBE sizeV=%s sizeF=%s minF=%d maxF=%d nanV=%d nanF=%d\n', ...
  mat2str(size(Vs)), mat2str(size(Fs)), min(Fs(:)), max(Fs(:)), sum(isnan(Vs(:))), sum(isnan(Fs(:))));
try
  fig = figure('visible','off');
  patch('Vertices',Vs,'Faces',Fs,'FaceColor',[0.75 0.75 0.75],'EdgeColor','none', ...
    'FaceLighting','gouraud','AmbientStrength',0.5);
  fprintf('PROBE patch OK\n');
  close(fig);
catch ME
  fprintf('PROBE patch FAIL: %s\n', ME.message);
  for k = 1:numel(ME.stack)
    fprintf('PROBE STACK %s line %d in %s\n', ME.stack(k).file, ME.stack(k).line, ME.stack(k).name);
  end
end
end
