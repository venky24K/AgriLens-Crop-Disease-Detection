"""
config.py — Central configuration for QuantumCrop.

All hyperparameters, paths, and settings live here.
Import this in any module:  from utils.config import CFG
"""

from pathlib import Path
import torch

# ── Project root (always resolves correctly regardless of where script is run) ─
ROOT = Path(__file__).resolve().parents[2]


class CFG:
    # ── Paths ─────────────────────────────────────────────────────────────────
    DATA_RAW        = ROOT / "data" / "raw"
    DATA_PROCESSED  = ROOT / "data" / "processed"
    OUTPUTS         = ROOT / "outputs"
    MODELS_DIR      = ROOT / "outputs" / "models"
    PLOTS_DIR       = ROOT / "outputs" / "plots"

    # ── Device ────────────────────────────────────────────────────────────────
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ── Dataset ───────────────────────────────────────────────────────────────
    # Set to a list of strings to only load those folders. 
    # Set to None to dynamically load ALL folders found in DATA_RAW / "MasterDataset"
    CLASSES = [
        "apple_apple_scab", "apple_black_rot", "apple_cedar_apple_rust", "apple_healthy",
        "grape_black_rot", "grape_esca_black_measles", "grape_healthy", "grape_leaf_blight_isariopsis_leaf_spot",
        "potato_early_blight", "potato_healthy", "potato_late_blight",
        "tomato_bacterial_spot", "tomato_early_blight", "tomato_healthy", "tomato_late_blight",
        "tomato_septoria_leaf_spot", "tomato_spider_mites_two_spotted_spider_mite", "tomato_target_spot", "tomato_tomato_yellowleaf_curl_virus",
        "corn_maize_common_rust", "corn_maize_healthy", "corn_maize_northern_leaf_blight"
    ]
    NUM_CLASSES     = len(CLASSES)
    IMG_SIZE        = (224, 224)      # ResNet-18 standard input
    TEST_SPLIT      = 0.2
    VAL_SPLIT       = 0.1
    RANDOM_SEED     = 42

    # ── Data augmentation (following Lakhani 2025) ────────────────────────────
    AUGMENT_ROTATION    = 30         # random rotation ±30°
    AUGMENT_H_FLIP      = True       # random horizontal flip
    AUGMENT_V_FLIP      = False
    AUGMENT_COLOR_JITTER = 0.2       # brightness/contrast jitter
    AUGMENT_RANDOM_CROP  = True      # random resized crop

    # ── CNN backbone ──────────────────────────────────────────────────────────
    CNN_BACKBONE        = "resnet18"
    CNN_FEATURE_DIM     = 512        # ResNet-18 output dimension
    CNN_PRETRAINED      = True
    CNN_FREEZE          = True       # freeze backbone for stability

    # ── Feature reduction ─────────────────────────────────────────────────────
    FEATURE_REDUCTION_DIM = 6        # CNN features → 6-d for quantum encoding (matches spectral features)

    # ── Quantum circuit (VQC) ─────────────────────────────────────────────────
    N_QUBITS        = 6              # must equal FEATURE_REDUCTION_DIM
    N_LAYERS        = 3              # 3 layers is optimal for convergence
    QUANTUM_DEVICE  = "lightning.qubit" # CPU simulator is more stable for small qubits
    SHOTS           = None           # None = exact statevector simulation

    # ── Training — Hybrid VQC ─────────────────────────────────────────────────
    VQC_LR          = 0.005          # stable LR for BatchNorm architecture
    VQC_EPOCHS      = 30             # 30 epochs for full convergence
    VQC_BATCH_SIZE  = 16
    VQC_OPTIMIZER   = "adam"

    # ── Training — CNN Baseline ───────────────────────────────────────────────
    CNN_LR          = 0.001
    CNN_EPOCHS      = 30
    CNN_BATCH_SIZE  = 32

    # ── Classical baseline (SVM) ──────────────────────────────────────────────
    SVM_KERNEL      = "rbf"
    SVM_C           = 1.0
    SVM_GAMMA       = "scale"

    # ── Streamlit dashboard ───────────────────────────────────────────────────
    APP_TITLE       = "QuantumCrop 🌾"
    APP_SUBTITLE    = "Quantum-Enhanced Crop Disease Detection"

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_INTERVAL    = 5


# Ensure output directories exist at import time
for _dir in [CFG.DATA_RAW, CFG.DATA_PROCESSED, CFG.MODELS_DIR, CFG.PLOTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)
