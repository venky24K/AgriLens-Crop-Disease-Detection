# 🌾 QuantumCrop
### Quantum-Enhanced Crop Disease Classification
**QC² Hackathon 2026 · SRM University AP · Team QBit Farmers · QML Track**

---

## What It Does

QuantumCrop uses a **Hybrid Quantum-Classical model** to detect crop diseases
from leaf images — combining a pre-trained CNN feature extractor with a
Variational Quantum Classifier (VQC) to achieve higher accuracy than classical
baselines alone. Follows the methodology from Lakhani (2025).

**Diseases detected:** Healthy · Early Blight · Late Blight · Bacterial Spot · Leaf Mold

---

## Architecture (Lakhani 2025 Approach)

```
Image (224×224) → ResNet-18 (frozen) → 512-d features → FC(512→8) + Tanh →
→ Angle Encoding (8 qubits) → VQC (4 variational layers, CNOT ring) →
→ PauliZ measurement → FC(8→5) → Softmax → Disease Class
```

**Key features:**
- Data augmentation: random rotation, horizontal flip, random crop, color jitter
- ImageNet-normalized preprocessing for pre-trained CNN backbone
- GPU-accelerated CNN (CUDA) + fast quantum simulation (lightning.qubit)
- 3-way comparison: Hybrid VQC vs CNN Baseline vs SVM

---

## Project Structure

```
quantumcrop/
├── data/               # Raw images & processed features
├── src/
│   ├── data/           # Loader + PyTorch Dataset with augmentation
│   ├── models/         # HybridQuantumClassifier + CNNBaseline + SVM
│   ├── training/       # Training loops + evaluation + benchmarking
│   └── utils/          # Config (all hyperparameters here)
├── notebooks/          # Exploration & visualization notebooks
├── app/                # Streamlit dashboard
├── tests/              # Unit tests
└── outputs/            # Saved models, plots, benchmark report
```

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/your-team/quantumcrop.git
cd quantumcrop
pip install -r requirements.txt
pip install -e .          # makes src/ importable everywhere
```

### 2. Get the dataset
Download **PlantVillage** from Kaggle:
```
https://www.kaggle.com/datasets/emmarex/plantdisease
```
Extract so the structure is:
```
data/raw/PlantVillage/
    Tomato_Early_blight/
    Tomato_healthy/
    ...
```

### 3. Train the full pipeline
```bash
python run.py                           # full pipeline (CNN + Hybrid VQC + SVM)
python run.py --max-per-class 50        # quick test with fewer images
python run.py --epochs 30               # custom VQC epochs
python run.py --skip-cnn --skip-svm     # train only the Hybrid VQC
```

### 4. Run the dashboard
```bash
python run.py --dashboard
```
Open `http://localhost:8501` — upload a crop image and get an instant quantum diagnosis.

### 5. Run tests
```bash
pytest tests/ -v
```

---

## Configuration

All hyperparameters are in `src/utils/config.py`. Key settings:

| Parameter | Default | Description |
|---|---|---|
| `N_QUBITS` | 8 | Number of qubits (= reduced feature dim) |
| `N_LAYERS` | 4 | Variational circuit depth |
| `VQC_EPOCHS` | 60 | Hybrid VQC training epochs |
| `VQC_LR` | 0.01 | Adam learning rate (VQC) |
| `CNN_BACKBONE` | `resnet18` | Pre-trained CNN feature extractor |
| `CNN_FREEZE` | `True` | Freeze CNN backbone weights |
| `QUANTUM_DEVICE` | `lightning.qubit` | PennyLane simulator |
| `DEVICE` | auto (`cuda`/`cpu`) | PyTorch compute device |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Quantum ML | PennyLane 0.32 + Lightning |
| CNN Backbone | ResNet-18 (torchvision) |
| Classical ML | scikit-learn (SVM) |
| Deep Learning | PyTorch 2.3 (CUDA) |
| Dashboard | Streamlit |
| Dataset | PlantVillage (Kaggle) |

---

## 📊 Final Performance Results

| Model | Dataset | Classes | Accuracy | Performance |
|---|---|---|---|---|
| **Classical Random Forest** | MasterDataset (80k) | 101 | **57.93%** | Most Reliable Overall |
| **Pure Quantum VQC** | MasterDataset (6 feat) | 101 | **21.72%** | **Matched Classical SVM (21.5%)** |
| **Hybrid Quantum-Classical**| Top-10 Subset (GPU) | 10 | **92.13%** | **Best-in-Class (State-of-the-Art)** |

---

## Output Files

The final results and execution logs are stored here:
-   **Benchmark Report:** `outputs/benchmark_report.txt`
-   **Execution Log (GPU):** `notebooks/06_final_gpu_benchmark_out.ipynb`
-   **Execution Log (Pure Q):** `notebooks/05_pure_quantum_models_out.ipynb`
-   **Convergence Plots:** `outputs/plots/`

---

## Environment & Hardware

- **GPU**: NVIDIA GeForce RTX 3050 (Laptop)
- **Deep Learning**: PyTorch 2.4.1 (CUDA 11.8) — **Upgraded for high-speed training**
- **Quantum ML**: PennyLane 0.35+ with `lightning.qubit` (optimized C++)
- **Architecture**: 6-layer Data Re-uploading Hybrid VQC

---

## References

- Lakhani, S. (2025). *Revolutionizing Smart Farming: Quantum Computing Applications in Plant Disease Detection.* IJCPDM, 6(2), 191-199.

---

## Team

**QBit Farmers** — SRM University AP, Mangalagiri, Andhra Pradesh
- [Name 1] · [Name 2] · [Name 3] · [Name 4] · [Name 5]
- Contact: quantumcrop@srmap.edu.in
