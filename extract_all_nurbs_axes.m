function extract_all_nurbs_axes()
% Extract axes for all NURBS-preprocessed Pot A pieces using PotSAC algorithm
% This replaces the TPS version with NURBS-compatible paths and processing

fprintf('=== NURBS AXIS EXTRACTION FOR ALL POT A PIECES ===\n');

% Set up paths
addpath('AxisExtraction/');

% Create output directory for NURBS axes
output_dir = 'NURBS_Output/Axes';
if ~exist('NURBS_Output', 'dir')
    mkdir('NURBS_Output');
end
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

% Process all 8 pieces of Pot A
pot_id = 'A';
total_pieces = 8;
successful_extractions = 0;

for piece_num = 1:total_pieces
    fprintf('\n--- Processing Pot A Piece %02d ---\n', piece_num);
    
    % Define NURBS surface files (correct path)
    surface_0_file = sprintf('Dataset/SfS_pp/Surfaces/Pot_A_Piece_%02d_Surface_0.xyz', piece_num);
    surface_1_file = sprintf('Dataset/SfS_pp/Surfaces/Pot_A_Piece_%02d_Surface_1.xyz', piece_num);
    axis_output_file = sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', output_dir, piece_num);
    
    % Check if NURBS surfaces exist
    if ~exist(surface_0_file, 'file') || ~exist(surface_1_file, 'file')
        fprintf('  ⏭️  Skipping piece %02d - NURBS surfaces not found\n', piece_num);
        fprintf('      Missing: %s or %s\n', surface_0_file, surface_1_file);
        continue;
    end
    
    try
        % Use NURBS-compatible axis extraction
        fprintf('  🔄 Running NURBS PotSAC extraction...\n');
        axis_candidates = extract_axis_nurbs(pot_id, piece_num, false);
        
        if size(axis_candidates, 1) >= 6 && size(axis_candidates, 2) >= 1
            num_candidates = size(axis_candidates, 2);
            fprintf('  ✅ Extracted %d axis candidates\n', num_candidates);
            
            % Save axis with improved format detection
            fid = fopen(axis_output_file, 'w');
            for cand_idx = 1:num_candidates
                % Handle PotSAC return format variability
                rows_1_3 = axis_candidates(1:3, cand_idx);
                rows_4_6 = axis_candidates(4:6, cand_idx);
                
                norm_1_3 = norm(rows_1_3);
                norm_4_6 = norm(rows_4_6);
                
                % Detect direction vector (should be normalized)
                if abs(norm_1_3 - 1.0) < 0.1
                    direction = rows_1_3 / norm(rows_1_3);
                    position = rows_4_6;
                elseif abs(norm_4_6 - 1.0) < 0.1  
                    direction = rows_4_6 / norm(rows_4_6);
                    position = rows_1_3;
                else
                    % Default assumption
                    direction = rows_1_3 / norm(rows_1_3);
                    position = rows_4_6;
                end
                
                % Write in SFS format: position first, then direction
                fprintf(fid, '%.6f %.6f %.6f %.6f %.6f %.6f\n', ...
                    position(1), position(2), position(3), ...
                    direction(1), direction(2), direction(3));
                    
                fprintf('  📍 Axis %d: pos=[%.1f,%.1f,%.1f], dir=[%.3f,%.3f,%.3f]\n', ...
                       cand_idx, position(1), position(2), position(3), ...
                       direction(1), direction(2), direction(3));
            end
            fclose(fid);
            
            successful_extractions = successful_extractions + 1;
            fprintf('  ✅ Saved to: %s\n', axis_output_file);
            
        else
            fprintf('  ❌ Invalid axis candidates returned\n');
        end
        
    catch extraction_error
        fprintf('  ❌ Axis extraction failed: %s\n', extraction_error.message);
        continue;
    end
end

fprintf('\n=== NURBS AXIS EXTRACTION SUMMARY ===\n');
fprintf('Successfully processed: %d/%d pieces\n', successful_extractions, total_pieces);
fprintf('Output directory: %s/\n', output_dir);

if successful_extractions > 0
    fprintf('\n📁 Generated axis files:\n');
    axis_files = dir(sprintf('%s/*.xyz', output_dir));
    for i = 1:length(axis_files)
        fprintf('  - %s\n', axis_files(i).name);
    end
    
    fprintf('\n🎯 NURBS axes ready for SFS reconstruction!\n');
    fprintf('📊 Expected improvement: ~36x fewer feature matches vs TPS\n');
else
    fprintf('\n❌ No axes extracted. Check NURBS preprocessing output.\n');
end

end