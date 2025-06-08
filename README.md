
Pipeline for registaring, analyzing and visualizing neuroanatomical point cloud data from whole brain imaging. The registration pipeline uses affine and b-spline transformations using intrinsic anatomical features with Elastix. 
The density-based analysis pipeline uses DBSCAN (Density-Based Spatial Clustering of Applications with Noise) to identify clusters of neuronal cells and visualize their spatial distribution in 3D.

This repository provides a modular and reproducible pipeline for:

1 - Whole-brain 3D registration.
2 - Whole-brain 3D transformation at high resolution
3 - 3D point cloud clustering using DBSCAN.
4 - Visualization and analysis of clustered cellular data.


Citation:

**A Comprehensive Atlas of Cell Type Density Patterns and Their Role in Brain Organization**

Rodrigo Muñoz-Castañeda#, Ramesh Palaniswamy, Jason Palmer, Rhonda Drewes, Corey Elowsky, Karla E. Hirokawa, Nicholas Cain, Kannan Umadevi Venkataraju, Hong-Wei Dong, Julie A. Harris, Zhuhao Wu, Pavel Osten#

#Corresponding Author

bioRxiv 2024.10.02.615922; doi: https://doi.org/10.1101/2024.10.02.615922


<img width="539" alt="Screenshot 2025-04-08 at 5 35 18 PM" src="https://github.com/user-attachments/assets/5523fb87-039c-4e12-ba53-092fee5aca88" />




The datasets used in this paper have been deposited for access at: http://download.brainimagelibrary.org/biccn/osten/cellcounting/ 


## Components

### 1. High-Resolution Image Registration (MATLAB)

| File | Purpose |
|------|---------|
| `registerWholeBrain.m` | Aligns whole-brain volume to reference space |
| `registerBrainSlice.m` | Optional slice-level refinement |
| `run_FullResolutionReg.sh` | Bash script to automate full registration pipeline |
| `nrrdread.m` | ⚠️ **Not included**. Proprietary function. Please supply your own NRRD reader or use alternatives from MATLAB Central |

To run:
```bash
bash scripts/run_FullResolutionReg.sh
```

---

### 2. DBSCAN Clustering (Python)

Cluster cellular point cloud data saved in `.mat` files.

```bash
python run_clustering.py \
    --input_dir path/to/mat_files \
    --output_dir path/to/save_labels \
    --eps 25 \
    --min_samples 10
```

Output: `.npy` files with cluster labels.

---

### 3. Visualization of Clustered Data (Python)

Render `.ply` outputs from DBSCAN results.
```bash
python run_processing.py \
    --input_dir path/to/ply_files
```

Each file is saved as a PNG image.

---

## Requirements

### MATLAB
- R2021a+ with Image Processing Toolbox
- ANTs (if required by registration pipeline)

### Python
Install dependencies via pip:
```bash
pip install -r requirements.txt
```

**requirements.txt** includes:
- numpy
- scipy
- open3d
- scikit-image
- matplotlib
- natsort

---

