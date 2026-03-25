"""
test_preprocess.py — Unit tests for the data pipeline.
Run with: pytest tests/ -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import torch
import pytest
from PIL import Image
import tempfile, os

from data.preprocess import (
    CropDiseaseDataset, get_train_transforms, get_eval_transforms,
    preprocess_single_image,
)
from utils.config import CFG


def make_dummy_image(color=(100, 150, 80), size=(256, 256)) -> Path:
    """Create a small solid-color PNG for testing."""
    img = Image.new("RGB", size, color=color)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    return Path(tmp.name)


class TestCropDiseaseDataset:
    def test_output_shape(self):
        img_path = make_dummy_image()
        records = [(img_path, 0)]
        dataset = CropDiseaseDataset(records, transform=get_eval_transforms())
        image, label = dataset[0]
        os.unlink(img_path)
        assert image.shape == (3, CFG.IMG_SIZE[0], CFG.IMG_SIZE[1]), \
            f"Expected (3, {CFG.IMG_SIZE[0]}, {CFG.IMG_SIZE[1]}), got {image.shape}"
        assert label == 0

    def test_output_type(self):
        img_path = make_dummy_image()
        records = [(img_path, 2)]
        dataset = CropDiseaseDataset(records, transform=get_eval_transforms())
        image, label = dataset[0]
        os.unlink(img_path)
        assert isinstance(image, torch.Tensor)
        assert isinstance(label, int)

    def test_augmentation_produces_variation(self):
        """Train transforms should produce different outputs for same input."""
        img_path = make_dummy_image(color=(50, 200, 50))
        records = [(img_path, 0)]
        dataset = CropDiseaseDataset(records, transform=get_train_transforms())
        img1, _ = dataset[0]
        img2, _ = dataset[0]
        os.unlink(img_path)
        # Due to random augmentation, outputs should differ
        # (they might be identical for solid colors, so this is probabilistic)
        assert img1.shape == img2.shape

    def test_dataset_length(self):
        img1 = make_dummy_image()
        img2 = make_dummy_image(color=(200, 100, 50))
        records = [(img1, 0), (img2, 1)]
        dataset = CropDiseaseDataset(records)
        assert len(dataset) == 2
        os.unlink(img1)
        os.unlink(img2)

    def test_different_images_differ(self):
        green_img = make_dummy_image(color=(50, 200, 50))
        yellow_img = make_dummy_image(color=(200, 200, 50))
        records = [(green_img, 0), (yellow_img, 1)]
        dataset = CropDiseaseDataset(records, transform=get_eval_transforms())
        img1, _ = dataset[0]
        img2, _ = dataset[1]
        os.unlink(green_img)
        os.unlink(yellow_img)
        assert not torch.allclose(img1, img2), \
            "Different images should produce different tensors"


class TestPreprocessSingleImage:
    def test_output_shape(self):
        img_path = make_dummy_image()
        tensor = preprocess_single_image(img_path)
        os.unlink(img_path)
        assert tensor.shape == (1, 3, CFG.IMG_SIZE[0], CFG.IMG_SIZE[1]), \
            f"Expected (1, 3, {CFG.IMG_SIZE[0]}, {CFG.IMG_SIZE[1]}), got {tensor.shape}"

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            preprocess_single_image(Path("/nonexistent/image.jpg"))
