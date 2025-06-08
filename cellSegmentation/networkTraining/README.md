
# Object Detection Training Pipeline (MATLAB)

This modular pipeline provides tools to train object detection models using MATLAB's Deep Learning Toolbox.

---

## 📦 Files

| File | Description |
|------|-------------|
| `trainDetectionNetwork.m` | Main wrapper function: coordinates loading, model, and training |
| `loadTrainingData.m` | Loads image filenames and bounding boxes from `.mat` label files |
| `buildDetectionModel.m` | Constructs a detection model (default: CNN-based detector) |
| `getTrainingOptions.m` | Defines training hyperparameters |

---

## 📁 Input Requirements

### 1. Images
- Stored in a directory (e.g., `training/images/`)
- Supported formats: `.jpg`, `.png`, `.tif`

### 2. Labels
- Stored as `.mat` files in a separate directory (e.g., `training/labels/`)
- Each `.mat` file must contain:
  - `bbox`: [N × 4] array of bounding boxes [x y w h]
  - `filename`: corresponding image file name

---

## 🧠 How to Train

In MATLAB:
```matlab
imageDir = 'path/to/images/';
labelDir = 'path/to/labels/';
detector = trainDetectionNetwork(imageDir, labelDir);
```

---

## ⚙️ Customize the Model

To change the model backbone or input size:
- Edit `buildDetectionModel.m` to switch from resnet50 to other backbones supported by MATLAB (e.g., resnet18, squeezenet)

---

## 🧪 Dependencies

- MATLAB R2021a or newer
- Deep Learning Toolbox
- Computer Vision Toolbox


