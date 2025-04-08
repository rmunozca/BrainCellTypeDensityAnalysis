#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBSCAN Clustering for Neuroanatomical Point Cloud Data

This script processes neuroanatomical point cloud data using DBSCAN clustering
and visualizes the results. It loads point data from MAT files, calculates
minimum points based on percentile statistics, and performs DBSCAN clustering.

Author: rmunozca (original)
"""

import os
import glob
import pickle
import numpy as np
import scipy as sp
from scipy.io import loadmat
import matplotlib.pyplot as plt
import open3d as o3d
from skimage import io

#############################################################################
#                         CONFIGURATION PARAMETERS                          #
#############################################################################

# DBSCAN parameters
EPS = 150  # Epsilon value for DBSCAN clustering
PERCENTILES = ['10', '20', '30', '40', '50', '60', '70', '80', '90']  # Percentiles for min_points calculation

# Data parameters
CELL_TYPE = 'TH_CCF'  # Type of cell data to process

# File paths
BASE_PATH = '/home/rmunozca/Downloads/'  # Base directory for all data

# Scaling factors (depending on cell type)
SCALE_FACTORS = {
    'default': {'X': 20, 'Y': 20, 'Z': 50, 'cut': 325},
    'CCF': {'X': 25, 'Y': 25, 'Z': 50, 'cut': 228}
}

#############################################################################


def load_config():
    """Load configuration parameters for the analysis.
    
    Returns:
        dict: Configuration parameters
    """
    config = {
        # DBSCAN parameters
        'eps': EPS,
        'percentiles': PERCENTILES,
        
        # Data parameters
        'cell_type': CELL_TYPE,
        
        # File paths
        'base_path': BASE_PATH,
        
        # Scaling factors (depending on cell type)
        'scale_factors': SCALE_FACTORS
    }
    
    # Derive other paths from base path
    config['mat_path'] = os.path.join(config['base_path'], 'matFiles', config['cell_type'])
    config['output_main'] = os.path.join(config['base_path'], 'wholeBrainProject/outPutTest/')
    config['output_folder'] = os.path.join(config['output_main'], f"{config['cell_type']}_DBSCAN/")
    config['distances_path'] = os.path.join(config['output_main'], '1_Distances', f"{config['cell_type']}_DBSCAN/")
    config['mask_path'] = os.path.join(config['output_main'], '2_OR_Atlas/CCF_Mask_crop.tif')
    
    return config


def setup_environment(config):
    """Create necessary directories.
    
    Args:
        config (dict): Configuration parameters
    """
    if not os.path.exists(config['output_folder']):
        os.makedirs(config['output_folder'])


def load_point_data(config):
    """Load point data from MAT files.
    
    Args:
        config (dict): Configuration parameters
    
    Returns:
        tuple: (points_dict, points_np, points_np_half, num_files)
    """
    mat_files = glob.glob(os.path.join(config['mat_path'], '*.mat'))
    num_files = len(mat_files)
    print(f"Number of mat files: {num_files}")
    
    # Load points from each file into a dictionary
    points = {}
    for file_path in mat_files:
        mat = loadmat(file_path)
        points[file_path] = mat["pointList"]
    
    print('Files read finished')
    
    # Stack all points into a single array
    points_np = np.vstack([v for k, v in points.items()])
    
    # Keep only points below the cut threshold (half brain)
    points_np_half = points_np.copy()
    points_np_half = np.delete(points_np_half, np.where(points_np_half[:, 1] >= config['cut']), axis=0)
    
    return points, points_np, points_np_half, num_files


def get_counts(distances_path):
    """Read clustering statistics from pickle files.
    
    Args:
        distances_path (str): Path to the pickle files
    
    Returns:
        list: Counts from all pickle files
    """
    print('Reading pkl files')
    pkl_files = glob.glob(os.path.join(distances_path, '*.pkl'))
    print(f"Number of pkl files: {len(pkl_files)}")
    
    counts = {}
    for file_path in pkl_files:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            counts[file_path] = list(data.values())
    
    return list(counts.values())


def calculate_min_points(counts, percentiles, num_files):
    """Calculate minimum points for DBSCAN based on percentiles.
    
    Args:
        counts (list): Counts from pickle files
        percentiles (list): Percentile values to calculate
        num_files (int): Number of files
    
    Returns:
        list: Minimum points for each percentile
    """
    print('Calculating minimum points')
    min_points = []
    
    for percentile in percentiles:
        points_at_percentile = []
        for count in counts:
            points = sp.stats.scoreatpercentile(count, int(percentile))
            points_at_percentile.append(points)
        
        min_points.append(np.mean(points_at_percentile))
    
    # Scale by number of files
    min_points = [x * num_files for x in min_points]
    
    print('Minimum Points:')
    print(*min_points, sep='\n')
    
    return min_points


def run_dbscan(points_np_half, points_np2, min_points, eps, config):
    """Run DBSCAN clustering and save results.
    
    Args:
        points_np_half (np.ndarray): Half brain points
        points_np2 (np.ndarray): Scaled points
        min_points (int): Minimum points parameter for DBSCAN
        eps (int): Epsilon parameter for DBSCAN
        config (dict): Configuration parameters
    """
    # Create point cloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points_np2)
    
    print(f'DBSCAN for minimum points of: {min_points}')
    
    # Run DBSCAN clustering
    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
        labels = np.array(
            pcd.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))
    
    max_label = labels.max()
    print(f"Point cloud has {max_label + 1} clusters")
    
    # Color points by cluster
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0
    pcd.colors = o3d.utility.Vector3dVector(colors[:, :3])
    
    # Output file paths
    output_prefix = os.path.join(
        config['output_folder'],
        f"{config['cell_type']}_min_points{min_points}_eps{eps}"
    )
    
    # Save point cloud
    o3d.io.write_point_cloud(f"{output_prefix}_pointCloud_dbscan.ply", pcd)
    
    # Create and save 3D image
    save_3d_image(pcd, points_np_half, config, output_prefix)


def save_3d_image(pcd, points_np_half, config, output_prefix):
    """Create and save 3D image representation of the clustered points.
    
    Args:
        pcd (o3d.geometry.PointCloud): Point cloud with colors
        points_np_half (np.ndarray): Half brain points
        config (dict): Configuration parameters
        output_prefix (str): Prefix for output files
    """
    # Load mask
    mask = io.imread(config['mask_path'])
    mask = mask[..., np.newaxis]
    
    # Get points and colors
    xyz_load = np.asarray(pcd.points)
    xyz_colors = np.asarray(pcd.colors)
    
    # Scale back to original space
    c = np.array([1/config['X'], 1/config['Y'], 1/config['Z']])
    xyz_load2 = xyz_load * c
    
    # Prepare for 3D image
    img_shape = [600, 350, 400, 3]
    xyz_colors_2 = xyz_colors * 255
    x, y, z = [i[0] for i in xyz_load2], [i[1] for i in xyz_load2], [i[2] for i in xyz_load2]
    
    # Create 3D image
    img = np.zeros(img_shape, dtype='uint8')
    for i in range(len(xyz_load2)):
        try:
            img[int(x[i]), int(y[i]), int(z[i])] = xyz_colors_2[i]
        except IndexError:
            pass
    
    # Crop and adjust image
    img = img[:320, :, :, :]
    img = img.swapaxes(0, 2)
    img = img * mask
    
    # Save image
    io.imsave(f"{output_prefix}_pointCloud_dbscan.tif", img)


def main():
    """Main function to run the DBSCAN clustering pipeline."""
    # Load configuration
    config = load_config()
    
    # Create output directories
    setup_environment(config)
    
    # Set scaling factors based on cell type
    if 'CCF' in config['cell_type']:
        scale_config = config['scale_factors']['CCF']
    else:
        scale_config = config['scale_factors']['default']
    
    config.update(scale_config)
    
    # Load point data
    points, points_np, points_np_half, num_files = load_point_data(config)
    
    # Scale points for visualization
    points_np2 = points_np_half.copy()
    points_np2[:, 0] *= config['X']
    points_np2[:, 1] *= config['Y']
    points_np2[:, 2] *= config['Z']
    
    # Get counts and calculate minimum points
    counts = get_counts(config['distances_path'])
    min_points_list = calculate_min_points(counts, config['percentiles'], num_files)
    
    # Run DBSCAN for each minimum points value
    for min_pts in min_points_list:
        min_pts = int(min_pts)
        run_dbscan(points_np_half, points_np2, min_pts, config['eps'], config)


if __name__ == "__main__":
    main()
