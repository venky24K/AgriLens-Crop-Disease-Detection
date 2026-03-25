"""
loader.py — Load and split the QuantumCrop dataset.

Supports dynamic loading from data/raw/MasterDataset/ (created by merge_datasets.py)
or any structured directory in data/raw/.
"""

import os
import random
from pathlib import Path
from typing import List, Tuple, Union

from utils.config import CFG

ImageRecord = Tuple[Path, int]   # (path_to_image, class_index)

def _discover_classes_and_images(root: Path) -> Tuple[List[str], List[ImageRecord]]:
    """
    Walk root directory (or MasterDataset/ if it exists) to dynamically find classes.
    """
    records: List[ImageRecord] = []
    valid_exts = {".jpg", ".jpeg", ".png"}
    
    # Prioritize MasterDataset if the user ran the merge script
    master_path = root / "MasterDataset"
    search_root = master_path if (master_path.exists() and master_path.is_dir()) else root

    # 1. Discover target classes
    if CFG.CLASSES is None:
        found_classes = [d.name for d in search_root.iterdir() if d.is_dir()]
        target_classes = sorted(list(set(found_classes)))
        if not target_classes:
            return [], []
            
        print(f"  Auto-discovered {len(target_classes)} classes in {search_root.name}/")
        # Update config dynamically for this run
        CFG.CLASSES = target_classes
        CFG.NUM_CLASSES = len(target_classes)
    else:
        target_classes = CFG.CLASSES

    # 2. Collect images mapping to class index
    for folder in sorted(search_root.iterdir()):
        if not folder.is_dir():
            continue
            
        folder_upper = folder.name.upper()
        matched_label = None
        
        for idx, cls in enumerate(target_classes):
            # Attempt exact or substring match
            if cls.upper() == folder_upper or cls.upper() in folder_upper or folder_upper in cls.upper():
                matched_label = idx
                break
                
        if matched_label is None:
            continue

        for img_path in folder.iterdir():
            if img_path.suffix.lower() in valid_exts:
                records.append((img_path, matched_label))

    return target_classes, records


def load_dataset(
    data_root: Union[Path, None] = None,
    max_per_class: int = 200,
) -> Tuple[List[ImageRecord], List[ImageRecord], List[ImageRecord]]:
    """
    Returns (train_records, val_records, test_records).
    Automatically updates CFG.CLASSES if it is None.
    """
    root = data_root or CFG.DATA_RAW
    
    if not root.exists():
        root.mkdir(parents=True)
        
    target_classes, all_records = _discover_classes_and_images(root)

    if not all_records:
        raise FileNotFoundError(
            f"No images found in {root}.\n"
            "Download your datasets into data/raw/ and run: python src/data/merge_datasets.py"
        )

    # Cap per class & shuffle
    random.seed(CFG.RANDOM_SEED)
    by_class: dict[int, list] = {i: [] for i in range(len(target_classes))}
    for rec in all_records:
        by_class[rec[1]].append(rec)

    balanced: List[ImageRecord] = []
    for cls_records in by_class.values():
        random.shuffle(cls_records)
        balanced.extend(cls_records[:max_per_class])

    random.shuffle(balanced)

    # Split
    n = len(balanced)
    n_test = int(n * CFG.TEST_SPLIT)
    n_val  = int(n * CFG.VAL_SPLIT)
    n_train = n - n_test - n_val

    train = balanced[:n_train]
    val   = balanced[n_train:n_train + n_val]
    test  = balanced[n_train + n_val:]

    print(f"Dataset loaded → train: {len(train)}, val: {len(val)}, test: {len(test)}")
    _print_class_distribution(train, "Train")
    return train, val, test

def _print_class_distribution(records: List[ImageRecord], split_name: str) -> None:
    from collections import Counter
    counts = Counter(label for _, label in records)
    print(f"  {split_name} class distribution:")
    for idx, cls in enumerate(CFG.CLASSES):
        count = counts.get(idx, 0)
        if count > 0:
            print(f"    [{idx}] {cls:<30} → {count} images")
