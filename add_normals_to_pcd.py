#!/usr/bin/env python3
import numpy as np
import sys
import os
from sklearn.neighbors import NearestNeighbors

def estimate_normals(points, k=20):
    """Estimate normals using KNN and PCA"""
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(points)
    distances, indices = nbrs.kneighbors(points)
    
    normals = np.zeros_like(points)
    curvatures = np.zeros(points.shape[0])
    
    for i in range(points.shape[0]):
        # Get neighborhood points
        neighbors = points[indices[i]]
        
        # Center the neighborhood
        centered = neighbors - np.mean(neighbors, axis=0)
        
        # Compute covariance matrix and PCA
        cov = np.cov(centered.T)
        eigenvals, eigenvecs = np.linalg.eigh(cov)
        
        # Normal is the eigenvector with smallest eigenvalue
        normal = eigenvecs[:, 0]
        
        # Ensure consistent normal orientation (pointing "outward")
        if normal[2] < 0:  # Simple heuristic: point upward
            normal = -normal
            
        normals[i] = normal
        
        # Curvature is ratio of smallest to sum of eigenvalues
        curvatures[i] = eigenvals[0] / (eigenvals[0] + eigenvals[1] + eigenvals[2] + 1e-10)
    
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
    
    # Estimate normals
    normals, curvatures = estimate_normals(points)
    print("Computed normals and curvatures")
    
    # Create new header
    new_header = []
    for line in header_lines:
        if line.startswith('FIELDS'):
            new_header.append('FIELDS x y z normal_x normal_y normal_z curvature')
        elif line.startswith('SIZE'):
            new_header.append('SIZE 4 4 4 4 4 4 4')
        elif line.startswith('TYPE'):
            new_header.append('TYPE F F F F F F F')
        elif line.startswith('COUNT'):
            new_header.append('COUNT 1 1 1 1 1 1 1')
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
        print("Usage: python3 add_normals_to_pcd.py input.pcd output.pcd")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    convert_pcd_xyz_to_normals(input_file, output_file)