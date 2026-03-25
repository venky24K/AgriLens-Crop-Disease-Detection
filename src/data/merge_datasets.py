"""
merge_datasets.py — Script to download and merge multiple Kaggle crop disease datasets.

Usage:
    pip install kagglehub
    python src/data/merge_datasets.py

This script:
1. Uses `kagglehub` to download 5 specific plant disease datasets.
2. Scans the downloaded folders for all image subfolders.
3. Normalizes folder names (e.g., 'Tomato___Early_blight' -> 'tomato_early_blight').
4. Identifies duplicate classes across different datasets.
5. For duplicates, keeps the folder with the MOST images.
6. Copies the best folders into `data/raw/MasterDataset/<normalized_name>/`.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
import re
from tqdm import tqdm
import sys

try:
    import kagglehub
except ImportError:
    print("❌ Error: 'kagglehub' is not installed.")
    print("Please run: pip install kagglehub")
    sys.exit(1)

# Make sure we can import config
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.config import CFG

DATASETS = [
    "emmarex/plantdisease",
    "kamal01/top-agriculture-crop-disease",
    "snikhilrao/crop-disease-detection-dataset",
    "vipoooool/new-plant-diseases-dataset",
    "jawadali1045/20k-multi-class-crop-disease-images"
]

def normalize_class_name(name: str) -> str:
    """
    Normalizes complex folder names into standard lowercase format.
    Example: 'Pepper__bell___Bacterial_spot' -> 'pepper_bell_bacterial_spot'
             'Tomato Early Blight' -> 'tomato_early_blight'
    """
    name = name.lower()
    name = re.sub(r'[^a-z0-9]', '_', name) # Replace non-alphanumeric with _
    name = re.sub(r'_+', '_', name)        # Collapse multiple __ to single _
    return name.strip('_')

def get_image_count(folder_path: Path) -> int:
    """Returns the number of valid images in a folder."""
    valid_exts = {".jpg", ".jpeg", ".png"}
    count = 0
    for f in folder_path.iterdir():
        if f.is_file() and f.suffix.lower() in valid_exts:
            count += 1
    return count

def run_merge():
    master_dir = CFG.DATA_RAW / "MasterDataset"
    
    print("=" * 60)
    print("🌾 QuantumCrop Dataset Downloader & Merger")
    print("=" * 60)

    # 1. Download datasets using kagglehub
    print("\n[1/3] Downloading datasets via kagglehub...")
    downloaded_paths = []
    
    for ds_name in DATASETS:
        print(f"\nDownloading: {ds_name}")
        path = kagglehub.dataset_download(ds_name)
        downloaded_paths.append(Path(path))
        print(f"Saved to: {path}")

    # 2. Scan raw directory and group by normalized class name
    print("\n[2/3] Scanning downloaded datasets for classes...")
    
    class_groups = defaultdict(list)
    valid_exts = {".jpg", ".jpeg", ".png"}
    
    for ds_path in downloaded_paths:
        for root, dirs, files in os.walk(ds_path):
            root_path = Path(root)
            
            # Skip if this is somehow the master dataset directory
            if "MasterDataset" in root_path.parts:
                continue
                
            # Does this folder contain images?
            has_images = any(f.lower().endswith(tuple(valid_exts)) for f in files)
            
            if has_images:
                # The folder name is assumed to be the class name
                class_name = root_path.name
                norm_name = normalize_class_name(class_name)
                img_count = get_image_count(root_path)
                
                # Filter out useless folders that are just dataset structure
                if img_count > 0 and len(norm_name) > 2 and "train" not in norm_name and "test" not in norm_name and "valid" not in norm_name:
                    class_groups[norm_name].append((root_path, img_count))
                
    if not class_groups:
        print("❌ No images found in the downloaded datasets.")
        return

    print(f"\nFound {len(class_groups)} unique crop/disease classes across the datasets.")

    # 3. Resolve duplicates
    print("\n[3/4] Resolving duplicates...")
    best_folders = {} # { 'normalized_name': Path }
    
    for norm_name, folders in class_groups.items():
        if len(folders) > 1:
            # Sort by image count descending
            folders.sort(key=lambda x: x[1], reverse=True)
            best_path, best_count = folders[0]
            print(f"  Merge '{norm_name}': Found {len(folders)} sources. Keeping largest ({best_count} imgs)")
            best_folders[norm_name] = best_path
        else:
            best_path, best_count = folders[0]
            best_folders[norm_name] = best_path

    # 4. Copy to MasterDataset
    print(f"\n[4/4] Copying {len(best_folders)} unique classes to {master_dir} ...")
    
    if master_dir.exists():
        print("  ⚠️ MasterDataset already exists. Deleting it for a fresh merge...")
        shutil.rmtree(master_dir)
        
    master_dir.mkdir(parents=True)
    
    for norm_name, source_path in tqdm(best_folders.items(), desc="Copying folders"):
        dest_path = master_dir / norm_name
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all valid images
        for file in source_path.iterdir():
            if file.is_file() and file.suffix.lower() in valid_exts:
                shutil.copy2(file, dest_path / file.name)
                
    print("\n✅ Merge Complete!")
    print(f"Master dataset created at: {master_dir}")
    print(f"Total unique classes: {len(best_folders)}")
    print("\nCFG.CLASSES in src/utils/config.py is set to None, so the pipeline")
    print("will automatically discover and use all these classes during training.")

if __name__ == "__main__":
    run_merge()
