#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBSCAN Point Cloud Processing and Visualization

This script processes point cloud PLY files from DBSCAN clustering results,
creates sparse point clouds, and generates visualization images with optional
CCF atlas overlay.

Author: rmunozca (original)
"""

import os
import glob
import numpy as np
from scipy import ndimage
import open3d as o3d
from skimage import io
from natsort import natsorted

#############################################################################
#                         CONFIGURATION PARAMETERS                          #
#############################################################################

# Data parameters
CELL_TYPE = 'VIP_CCF'  # Type of cell data to process

# File paths
BASE_PATH = '/home/rmunozca/Downloads/wholeBrainProject/outPutTest/'
INPUT_PATH = os.path.join(BASE_PATH, 'DBSCAN_byMeanDistance_10to90perc/')
OUTPUT_PATH = os.path.join(BASE_PATH, 'DBSCAN_percentiles_sparse_points/', f"{CELL_TYPE}_DBSCAN/")
ATLAS_PATH = os.path.join(BASE_PATH, '2_OR_Atlas/')
MAT_PATH = f'/home/rmunozca/Downloads/matFiles/{CELL_TYPE}'

# Atlas files
CCF_FILE = os.path.join(ATLAS_PATH, 'CCFv3_25um_crop_2.tif')
MASK_FILE = os.path.join(ATLAS_PATH, 'CCF_Mask_crop.tif')

# Image parameters
IMAGE_SHAPE = [400, 350, 320, 3]  # [width, height, depth, channels]
MAX_Z_LIMIT = 250  # Z-axis limit for final image
ZOOM_FACTOR = [2, 1, 1, 1]  # Zoom factors for final image

# Sparse sampling
SPARSE_FACTOR = 2  # Denominator for sparse sampling (higher = sparser)

#############################################################################


def setup_environment():
    """Create necessary output directories and load required files.
    
    Returns:
        tuple: (file_list, mask, ccf_atlas, scaling_factors, cut_threshold, num_files)
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    
    # Load mask and CCF atlas
    mask = io.imread(MASK_FILE)
    mask = mask[..., np.newaxis]
    
    ccf_atlas = io.imread(CCF_FILE)
    ccf_atlas = ccf_atlas[..., np.newaxis]
    
    # Get list of PLY files to process
    file_list = natsorted(glob.glob(os.path.join(INPUT_PATH, f"{CELL_TYPE}_DBSCAN/*.ply")))
    
    # Get list of MAT files to determine scaling factor
    mat_files = glob.glob(os.path.join(MAT_PATH, '*.mat'))
    num_files = len(mat_files)
    print(f'Number of mat files: {num_files}')
    
    # Set scaling factors based on cell type
    if 'CCF' not in CELL_TYPE:
        x_scale, y_scale, z_scale = 20, 20, 50
        cut_threshold = 325
    else:
        x_scale, y_scale, z_scale = 25, 25, 50
        cut_threshold = 228
    
    return file_list, mask, ccf_atlas, (x_scale, y_scale, z_scale), cut_threshold, num_files


def process_point_cloud(file_path, scaling_factors, sparse_factor, mask, ccf_atlas):
    """Process a single point cloud file to create sparse representation and visualization.
    
    Args:
        file_path (str): Path to the PLY file
        scaling_factors (tuple): X, Y, Z scaling factors
        sparse_factor (int): Subsampling factor for sparse representation
        mask (np.ndarray): Brain mask for visualization
        ccf_atlas (np.ndarray): CCF atlas for overlay
        
    Returns:
        tuple: (sparse_pcd, visualization_image, combined_image)
    """
    # Extract file name for output
    name = os.path.basename(file_path)[:-4]  # Remove .ply extension
    
    # Load point cloud
    pcd = o3d.io.read_point_cloud(file_path)
    xyz_load = np.asarray(pcd.points)
    xyz_colors = np.asarray(pcd.colors)
    
    # Create sparse point cloud
    pcd_sparse = o3d.geometry.PointCloud()
    xyz_load_sparse = xyz_load[::sparse_factor].copy()
    xyz_colors_sparse = xyz_colors[::sparse_factor].copy()
    pcd_sparse.points = o3d.utility.Vector3dVector(xyz_load_sparse)
    pcd_sparse.colors = o3d.utility.Vector3dVector(xyz_colors_sparse)
    
    # Scale points for visualization
    x_scale, y_scale, z_scale = scaling_factors
    scale_factors = np.array([1/x_scale, 1/y_scale, 1/z_scale])
    xyz_scaled = xyz_load * scale_factors
    
    # Prepare colors for visualization (scale to 0-255)
    vis_colors = xyz_colors * 255
    
    # Create visualization image
    img = np.zeros(IMAGE_SHAPE, dtype='uint8')
    
    # Extract coordinates (note the swapped order compared to original)
    z, y, x = [i[0] for i in xyz_scaled], [i[1] for i in xyz_scaled], [i[2] for i in xyz_scaled]
    
    # Place points in image
    for i in range(0, len(xyz_scaled), sparse_factor):
        if np.any(vis_colors[i]):  # Skip points with zero color
            try:
                img[int(x[i]), int(y[i]), int(z[i])] = vis_colors[i]
            except IndexError:
                pass  # Skip points outside image boundaries
    
    # Apply mask
    masked_img = img * mask
    
    # Create combined image with CCF atlas
    combined_img = masked_img + ccf_atlas
    
    # Crop Z dimension
    combined_img = combined_img[:, :MAX_Z_LIMIT, :, :]
    
    # Apply zoom for final image
    zoomed_img = ndimage.zoom(combined_img, ZOOM_FACTOR)
    
    return pcd_sparse, masked_img, combined_img, zoomed_img


def save_results(pcd_sparse, vis_img, combined_img, file_name):
    """Save processed results to files.
    
    Args:
        pcd_sparse (o3d.geometry.PointCloud): Sparse point cloud
        vis_img (np.ndarray): Visualization image
        combined_img (np.ndarray): Combined image with CCF atlas
        file_name (str): Base name for output files
    """
    # Save sparse point cloud
    sparse_path = os.path.join(OUTPUT_PATH, f"{file_name}_NEW_2sparse_OriginalColors.ply")
    o3d.io.write_point_cloud(sparse_path, pcd_sparse)
    
    # Save visualization image
    vis_path = os.path.join(OUTPUT_PATH, f"{file_name}_sparse.tif")
    io.imsave(vis_path, vis_img)
    
    # Optional: Save combined image with CCF atlas
    # combined_path = os.path.join(OUTPUT_PATH, f"{file_name}_sparse_OriginalColors_CCF.tif")
    # io.imsave(combined_path, combined_img)


def main():
    """Main function to process all PLY files."""
    print(f"Processing point clouds for cell type: {CELL_TYPE}")
    
    # Setup environment and load required files
    file_list, mask, ccf_atlas, scaling_factors, cut_threshold, num_files = setup_environment()
    
    # Calculate sparse factor based on number of files
    sparse_factor = int(np.ceil(num_files/SPARSE_FACTOR))
    
    # Process individual files
    for idx, file_path in enumerate(file_list):
        print(f"Processing file {idx+1}/{len(file_list)}: {os.path.basename(file_path)}")
        
        # Extract file name for output
        name = os.path.basename(file_path)[:-4]  # Remove .ply extension
        
        # Process point cloud
        pcd_sparse, vis_img, combined_img, zoomed_img = process_point_cloud(
            file_path, scaling_factors, sparse_factor, mask, ccf_atlas
        )
        
        # Save results
        save_results(pcd_sparse, vis_img, combined_img, name)
    
    print("Processing complete!")


if __name__ == "__main__":
    main()
