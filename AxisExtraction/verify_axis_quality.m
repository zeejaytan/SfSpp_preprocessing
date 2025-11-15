% Verify that the extracted axis is geometrically meaningful for pottery analysis
fprintf('=== Verifying Axis Quality for Pottery Analysis ===\n');

try
    % Load surface data
    [C0, C1] = read_surfaces('A', 1, false);
    fprintf('Surface data loaded: %d + %d points\n', size(C0,2), size(C1,2));
    
    % Extract axis
    fprintf('Extracting axis...\n');
    vt = extract_axis('A', 1, false);
    
    if size(vt, 2) >= 1
        axis_dir = vt(1:3, 1);
        axis_pos = vt(4:6, 1);
        
        fprintf('\n=== Axis Properties ===\n');
        fprintf('Direction vector: [%.4f, %.4f, %.4f]\n', axis_dir(1), axis_dir(2), axis_dir(3));
        fprintf('Position vector:  [%.4f, %.4f, %.4f]\n', axis_pos(1), axis_pos(2), axis_pos(3));
        fprintf('Direction magnitude: %.6f (should be ~1.0)\n', norm(axis_dir));
        
        % Check orthogonality constraint (axis direction should be orthogonal to position)
        orthogonality = abs(dot(axis_dir, axis_pos));
        fprintf('Orthogonality check: |dir·pos| = %.6f (should be ~0)\n', orthogonality);
        
        % Check axis alignment with pottery geometry
        fprintf('\n=== Geometric Analysis ===\n');
        
        % Compute distances from surface points to axis
        combined_points = [C0(1:3,:), C1(1:3,:)];
        num_points = size(combined_points, 2);
        
        % Distance from each point to the axis line
        distances = zeros(1, num_points);
        for i = 1:num_points
            point = combined_points(:, i);
            % Vector from axis position to point
            to_point = point - axis_pos;
            % Project onto axis direction
            projection_length = dot(to_point, axis_dir);
            projection = projection_length * axis_dir;
            % Distance is the perpendicular component
            perpendicular = to_point - projection;
            distances(i) = norm(perpendicular);
        end
        
        fprintf('Distance to axis statistics:\n');
        fprintf('  Mean distance: %.2f\n', mean(distances));
        fprintf('  Std deviation: %.2f\n', std(distances));
        fprintf('  Min distance:  %.2f\n', min(distances));
        fprintf('  Max distance:  %.2f\n', max(distances));
        fprintf('  Median:        %.2f\n', median(distances));
        
        % For pottery, we expect most points to be at similar distances from axis
        % (roughly cylindrical/conical shape)
        cv = std(distances) / mean(distances);
        fprintf('  Coefficient of variation: %.3f\n', cv);
        
        if cv < 0.5
            fprintf('✓ Good axis consistency (CV < 0.5)\n');
        elseif cv < 1.0
            fprintf('⚠ Moderate axis consistency (0.5 ≤ CV < 1.0)\n');
        else
            fprintf('❌ Poor axis consistency (CV ≥ 1.0)\n');
        end
        
        % Check if axis direction makes sense for pottery
        % Pottery axes typically have some vertical component
        vertical_component = abs(axis_dir(3)); % Assuming Z is up
        fprintf('\n=== Pottery-Specific Checks ===\n');
        fprintf('Vertical component of axis: %.3f\n', vertical_component);
        
        if vertical_component > 0.7
            fprintf('✓ Strong vertical alignment (typical for pottery)\n');
        elseif vertical_component > 0.3
            fprintf('⚠ Moderate vertical alignment\n');
        else
            fprintf('❌ Weak vertical alignment (unusual for pottery)\n');
        end
        
        % Compute final error using the same method as the optimization
        fprintf('\n=== Error Analysis ===\n');
        combined_surface = [C0, C1];
        final_error = compute_biaxial_cao_error(vt(:,1), combined_surface);
        fprintf('Final biaxial Cao error: %.6f\n', final_error);
        
        if final_error < 1000
            fprintf('✓ Low error - good axis fit\n');
        elseif final_error < 10000
            fprintf('⚠ Moderate error - acceptable axis fit\n');
        else
            fprintf('❌ High error - poor axis fit\n');
        end
        
        fprintf('\n=== Overall Assessment ===\n');
        constraints_ok = (abs(norm(axis_dir) - 1.0) < 0.001) && (orthogonality < 0.01);
        geometry_ok = (cv < 1.0) && (final_error < 10000);
        pottery_ok = (vertical_component > 0.3);
        
        if constraints_ok && geometry_ok && pottery_ok
            fprintf('✅ AXIS EXTRACTION SUCCESSFUL - mathematically and geometrically valid\n');
        else
            fprintf('❌ AXIS EXTRACTION ISSUES DETECTED:\n');
            if ~constraints_ok
                fprintf('  - Mathematical constraints violated\n');
            end
            if ~geometry_ok
                fprintf('  - Geometric fit is poor\n');
            end
            if ~pottery_ok
                fprintf('  - Axis orientation unusual for pottery\n');
            end
        end
        
    else
        fprintf('❌ No axes extracted\n');
    end
    
catch ME
    fprintf('❌ Verification failed: %s\n', ME.message);
end