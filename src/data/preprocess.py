"""
preprocess.py — Image preprocessing and dataset creation for QuantumCrop.

Following the Lakhani (2025) methodology:
  - Images standardized to 224×224, normalized to [0,1]
  - Data augmentation: random rotations, horizontal flipping, random resized crop
  - Creates PyTorch Dataset/DataLoader for training pipeline

Also provides a single-image inference function for the Streamlit dashboard.
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Union

from utils.config import CFG


# ── Image transforms ─────────────────────────────────────────────────────────

def get_train_transforms() -> transforms.Compose:
    """
    Training transforms with data augmentation (Lakhani 2025):
      - Random resized crop → 224×224
      - Random horizontal flip
      - Random rotation ±30°
      - Color jitter (brightness/contrast)
      - Normalize to ImageNet mean/std (for pre-trained ResNet)
    """
    aug_list = [
        transforms.Resize((256, 256)),       # resize slightly larger
    ]

    if CFG.AUGMENT_RANDOM_CROP:
        aug_list.append(transforms.RandomResizedCrop(CFG.IMG_SIZE, scale=(0.8, 1.0)))
    else:
        aug_list.append(transforms.CenterCrop(CFG.IMG_SIZE))

    if CFG.AUGMENT_ROTATION:
        aug_list.append(transforms.RandomRotation(CFG.AUGMENT_ROTATION))

    if CFG.AUGMENT_H_FLIP:
        aug_list.append(transforms.RandomHorizontalFlip(p=0.5))

    if CFG.AUGMENT_V_FLIP:
        aug_list.append(transforms.RandomVerticalFlip(p=0.5))

    if CFG.AUGMENT_COLOR_JITTER:
        j = CFG.AUGMENT_COLOR_JITTER
        aug_list.append(transforms.ColorJitter(brightness=j, contrast=j, saturation=j))

    aug_list.extend([
        transforms.ToTensor(),                # [0, 255] → [0, 1]
        transforms.Normalize(                 # ImageNet normalization
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])

    return transforms.Compose(aug_list)


def get_eval_transforms() -> transforms.Compose:
    """Validation/test transforms — no augmentation, just resize + normalize."""
    return transforms.Compose([
        transforms.Resize(CFG.IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


# ── PyTorch Dataset ──────────────────────────────────────────────────────────

class CropDiseaseDataset(Dataset):
    """
    PyTorch Dataset for crop leaf images.

    Each sample is a (image_tensor, label) pair.
    Images are loaded lazily and transformed on-the-fly.
    """

    def __init__(
        self,
        records: List[Tuple[Path, int]],
        transform: transforms.Compose = None,
    ):
        """
        Args:
            records   : list of (image_path, label_index) tuples
            transform : torchvision transforms to apply
        """
        self.records = records
        self.transform = transform or get_eval_transforms()

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.records[idx]

        # Load image as RGB PIL Image
        image = Image.open(img_path).convert("RGB")

        # Apply transforms
        image = self.transform(image)

        return image, label


# ── DataLoader builders ──────────────────────────────────────────────────────

def build_dataloaders(
    train_records: List[Tuple[Path, int]],
    val_records: List[Tuple[Path, int]],
    test_records: List[Tuple[Path, int]],
    batch_size: int = CFG.VQC_BATCH_SIZE,
    num_workers: int = 0,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Build train/val/test DataLoaders with appropriate transforms.

    Args:
        train_records : list of (path, label) for training (with augmentation)
        val_records   : list of (path, label) for validation (no augmentation)
        test_records  : list of (path, label) for testing (no augmentation)
        batch_size    : batch size for all loaders
        num_workers   : number of parallel data loading workers

    Returns:
        (train_loader, val_loader, test_loader)
    """
    train_dataset = CropDiseaseDataset(train_records, transform=get_train_transforms())
    val_dataset   = CropDiseaseDataset(val_records,   transform=get_eval_transforms())
    test_dataset  = CropDiseaseDataset(test_records,  transform=get_eval_transforms())

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers,
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers,
    )

    print(f"  DataLoaders built → train: {len(train_dataset)}, val: {len(val_dataset)}, test: {len(test_dataset)}")
    return train_loader, val_loader, test_loader


# ── Single-image inference (for Streamlit dashboard) ─────────────────────────

def preprocess_single_image(img_path: Union[Path, str]) -> torch.Tensor:
    """
    Load and preprocess a single image for model inference.

    Args:
        img_path: path to the image file

    Returns:
        Tensor of shape (1, 3, 224, 224) — ready for model input
    """
    image = Image.open(str(img_path)).convert("RGB")
    transform = get_eval_transforms()
    tensor = transform(image).unsqueeze(0)   # add batch dimension
    return tensor


# ── Legacy Functions for Notebook Compatibility ───────────────────────────────

import cv2
from tqdm import tqdm

def _normalize_to_angle(features: np.ndarray) -> np.ndarray:
    return np.clip((features - np.min(features)) / (np.max(features) - np.min(features) + 1e-8) * np.pi, 0, np.pi)

def extract_features(img_path: Path) -> np.ndarray:
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError('Invalid image')
    img = cv2.resize(img, (128, 128))
    
    b, g, r = cv2.split(img)
    ndvi_proxy = (g.astype(float) - r.astype(float)) / (g.astype(float) + r.astype(float) + 1e-8)
    
    mean_r, mean_g, mean_b = r.mean(), g.mean(), b.mean()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contrast = gray.std()
    energy = (gray ** 2).mean()
    
    raw_features = np.array([ndvi_proxy.mean(), mean_r, mean_g, mean_b, contrast, energy], dtype=np.float32)
    return _normalize_to_angle(raw_features)

import concurrent.futures
import os

def _process_single_record(record):
    path, label = record
    try:
        return extract_features(path), label
    except Exception:
        return None

def build_feature_matrix(records, desc='Extracting'):
    X, y = [], []
    max_w = min(32, (os.cpu_count() or 1) * 4)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as executor:
        results = list(tqdm(executor.map(_process_single_record, records), total=len(records), desc=desc))
        
    for res in results:
        if res is not None:
            feats, label = res
            X.append(feats)
            y.append(label)
            
    return np.array(X), np.array(y)

def save_features(X, y, split_name):
    np.save(f"../outputs/{split_name}_X.npy", X)
    np.save(f"../outputs/{split_name}_y.npy", y)
    
def load_features(split_name):
    X = np.load(f"../outputs/{split_name}_X.npy")
    y = np.load(f"../outputs/{split_name}_y.npy")
    return X, y

