#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nissl Cell Segmentation and Centroid Extraction

This script performs image segmentation on Nissl-stained brain sections to extract
cell contours and centroids. It supports parallel processing and configurable input/output paths.

Author: rmunozca
Refactored: 2025-06
"""

import os
import time
import argparse
import numpy as np
import pandas as pd
import cv2
from skimage import io
from joblib import Parallel, delayed


def check_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def segment_image(filename, input_path, output_path, output_blob_path):
    filepath = os.path.join(input_path, filename)
    try:
        img = io.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        centroids = []
        for cnt in contours:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((cx, cy))

        df = pd.DataFrame(centroids, columns=["x", "y"])
        output_csv = os.path.join(output_path, filename.replace(".tif", "_centroids.csv"))
        df.to_csv(output_csv, index=False)

        print(f"Processed: {filename} — {len(centroids)} centroids saved.")
    except Exception as e:
        print(f"Failed to process {filename}: {e}")

def main(input_dir, output_dir, output_blob_dir, n_jobs):
    check_folder(output_dir)
    check_folder(output_blob_dir)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.tif')]
    Parallel(n_jobs=n_jobs)(
        delayed(segment_image)(f, input_dir, output_dir, output_blob_dir) for f in files
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Segment Nissl images and extract centroids.")
    parser.add_argument("--input_dir", required=True, help="Path to input .tif images")
    parser.add_argument("--output_dir", required=True, help="Path to save centroid CSVs")
    parser.add_argument("--output_blob_dir", required=True, help="Placeholder output (not used)")
    parser.add_argument("--n_jobs", type=int, default=4, help="Number of parallel jobs")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.output_blob_dir, args.n_jobs)
