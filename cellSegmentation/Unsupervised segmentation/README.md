
## Nissl Cell Segmentation and Centroid Extraction

This script performs segmentation of Nissl-stained brain tissue images to extract cell contours and compute centroid coordinates.

---

## 📂 Input

- Folder of `.tif` images (Nissl-stained, 2D)
- Each image is processed individually

---

## 💾 Output

- For each input image, a `.csv` file is saved with detected cell centroids:
  ```
  image_X_centroids.csv
  ```
  Each file contains:
  ```
  x, y
  124, 87
  131, 90
  ...
  ```

---

## 🚀 How to Use

```bash
python NisslSegmentation_clean.py \
  --input_dir path/to/cellType_images \
  --output_dir path/to/save_csvs \
  --output_blob_dir path/to/temp_or_unused \
  --n_jobs 6
```

---

## ⚙️ Options

| Argument | Description |
|----------|-------------|
| `--input_dir` | Directory with `.tif` images |
| `--output_dir` | Directory to save centroid CSV files |
| `--output_blob_dir` | Placeholder for compatibility (not used) |
| `--n_jobs` | Number of parallel workers (default: 4) |

---

## 🧪 Dependencies

Install required Python libraries:
```bash
pip install numpy pandas opencv-python scikit-image joblib
```


