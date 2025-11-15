#!/usr/bin/env python3
import numpy as np
import sys
import os

def simple_normal_estimation(points):
    """Simple normal estimation using local neighborhoods"""
    normals = np.zeros_like(points)
    curvatures = np.zeros(points.shape[0])
    
    for i in range(points.shape[0]):
        # Find nearby points using simple distance threshold
        distances = np.linalg.norm(points - points[i], axis=1)
        neighbors_idx = np.argsort(distances)[1:21]  # 20 nearest neighbors (excluding self)
        
        neighbors = points[neighbors_idx]
        
        if len(neighbors) < 3:
            # Not enough neighbors, use default up normal
            normals[i] = [0, 0, 1]
            curvatures[i] = 0.01
            continue
        
        # Center the neighborhood
        centered = neighbors - np.mean(neighbors, axis=0)
        
        # Compute covariance matrix
        cov = np.cov(centered.T)
        
        # Find eigenvalues and eigenvectors
        try:
            eigenvals, eigenvecs = np.linalg.eigh(cov)
            
            # Normal is eigenvector with smallest eigenvalue
            normal = eigenvecs[:, 0]
            
            # Ensure consistent orientation (prefer pointing up)
            if normal[2] < 0:
                normal = -normal
                
            normals[i] = normal
            
            # Simple curvature estimate
            eigenvals = np.sort(eigenvals)
            curvatures[i] = eigenvals[0] / (np.sum(eigenvals) + 1e-10)
            
        except np.linalg.LinAlgError:
            # Fallback to default normal
            normals[i] = [0, 0, 1]
            curvatures[i] = 0.01
    
    return normals, curvatures

def convert_pcd_xyz_to_normals(input_file, output_file):
    """Convert XYZ PCD file to include normals and curvature"""
    
    print(f"Converting {input_file} to {output_file}")
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Parse header
    header_lines = []
    data_start_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith('DATA'):
            data_start_idx = i + 1
            break
        header_lines.append(line.strip())
    
    # Extract points
    points = []
    for i in range(data_start_idx, len(lines)):
        if lines[i].strip():
            coords = [float(x) for x in lines[i].strip().split()]
            if len(coords) >= 3:
                points.append(coords[:3])
    
    points = np.array(points)
    print(f"Loaded {len(points)} points")
    
    # For testing, just use first 1000 points to speed up
    if len(points) > 1000:
        print("Using first 1000 points for testing...")
        points = points[:1000]
    
    # Estimate normals
    print("Computing normals...")
    normals, curvatures = simple_normal_estimation(points)
    print("Computed normals and curvatures")
    
    # Create new header
    new_header = []
    point_count = len(points)
    
    for line in header_lines:
        if line.startswith('FIELDS'):
            new_header.append('FIELDS x y z normal_x normal_y normal_z curvature')
        elif line.startswith('SIZE'):
            new_header.append('SIZE 4 4 4 4 4 4 4')
        elif line.startswith('TYPE'):
            new_header.append('TYPE F F F F F F F')
        elif line.startswith('COUNT'):
            new_header.append('COUNT 1 1 1 1 1 1 1')
        elif line.startswith('WIDTH'):
            new_header.append(f'WIDTH {point_count}')
        elif line.startswith('POINTS'):
            new_header.append(f'POINTS {point_count}')
        else:
            new_header.append(line)
    
    # Write output file
    with open(output_file, 'w') as f:
        # Write header
        for line in new_header:
            f.write(line + '\n')
        f.write('DATA ascii\n')
        
        # Write points with normals
        for i in range(len(points)):
            f.write(f"{points[i][0]:.6f} {points[i][1]:.6f} {points[i][2]:.6f} ")
            f.write(f"{normals[i][0]:.6f} {normals[i][1]:.6f} {normals[i][2]:.6f} ")
            f.write(f"{curvatures[i]:.6f}\n")
    
    print(f"Saved {len(points)} points with normals to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 add_normals_simple.py input.pcd output.pcd")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    convert_pcd_xyz_to_normals(input_file, output_file)