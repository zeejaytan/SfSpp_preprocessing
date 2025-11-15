function [C0, C1] = read_surfaces(pot_id, frag_id, extended)

if nargin < 3, extended = false;
end


% 
% C0 = dlmread(sprintf('Z:/2020/Pottery Data/%s-%02d/Surfaces/%s-%02d-%02d.obj_samples_Int.xyz', ...
%                       namespace, pot_id, namespace, pot_id, frag_id))';
% C1 = dlmread(sprintf('Z:/2020/Pottery Data/%s-%02d/Surfaces/%s-%02d-%02d.obj_samples_Ext.xyz', ...
%                       namespace, pot_id, namespace, pot_id, frag_id))'; 

% root_dir = load_root_dir('D:/240718/GT', extended);
% root_dir = load_root_dir('D:/240718/Data_change/H(re)', extended);
root_dir = load_root_dir('D:/SFS_BB_temp/Plt_A', extended);

% C0 = readmatrix(sprintf('%s/Surfaces/Pot_%s_Piece_%02d_Surface_0.xyz', ...
%                root_dir, pot_id, frag_id), 'FileType', 'text')';
% C0 = readmatrix(sprintf('%s/Surface_axis/Pot_%s_Piece_%02d_Surface_0.xyz', ...
%                root_dir, pot_id, frag_id), 'FileType', 'text')';
C0 = readmatrix(sprintf('%s/Surfaces/Pot_%s_Piece_%02d_Surface_0.xyz', ...
                root_dir, pot_id, frag_id), 'FileType', 'text');
C0 = C0';  % Transpose: convert from (points×6) to (6×points) format
                  
if nargout > 1
%     C1 = readmatrix(sprintf('%s/Surfaces/Pot_%s_Piece_%02d_Surface_1.xyz', ...
%                    root_dir, pot_id, frag_id), 'FileType', 'text')';
%     C1 = readmatrix(sprintf('%s/Surface_axis/Pot_%s_Piece_%02d_Surface_1.xyz', ...
%                     root_dir, pot_id, frag_id), 'FileType', 'text')';
C1 = readmatrix(sprintf('%s/Surfaces/Pot_%s_Piece_%02d_Surface_1.xyz', ...
                    root_dir, pot_id, frag_id), 'FileType', 'text');
    C1 = C1';  % Transpose: convert from (points×6) to (6×points) format
    
    % Ensure both surfaces have the same number of points for potsac
    min_points = min(size(C0, 2), size(C1, 2));
    C0 = C0(:, 1:min_points);  % Take first min_points from C0
    C1 = C1(:, 1:min_points);  % Take first min_points from C1
    
    fprintf('📐 Resampled surfaces to %d points each\n', min_points);
end

end
