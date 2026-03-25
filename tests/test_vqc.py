"""
test_vqc.py — Unit tests for the Hybrid Quantum-Classical model.
Run with: pytest tests/ -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch
import numpy as np
import pytest

from models.vqc import HybridQuantumClassifier, quantum_circuit, count_parameters
from models.classical import CNNBaseline
from utils.config import CFG


class TestQuantumCircuit:
    def test_output_length(self):
        inputs  = torch.zeros(CFG.N_QUBITS)
        weights = torch.zeros(CFG.N_LAYERS, CFG.N_QUBITS, 2)
        out = quantum_circuit(inputs, weights)
        assert len(out) == CFG.N_QUBITS, \
            f"Circuit should return {CFG.N_QUBITS} expectation values"

    def test_output_range(self):
        inputs  = torch.rand(CFG.N_QUBITS) * 2 - 1  # [-1, 1]
        weights = torch.rand(CFG.N_LAYERS, CFG.N_QUBITS, 2) * 2 * torch.pi
        out = quantum_circuit(inputs, weights)
        for val in out:
            assert -1.0 - 1e-5 <= float(val) <= 1.0 + 1e-5, \
                f"PauliZ expectation must be in [-1, 1], got {float(val)}"


class TestHybridQuantumClassifier:
    def setup_method(self):
        self.model = HybridQuantumClassifier()
        self.model.eval()
        # Batch of 2 random images (3, 224, 224)
        self.batch = torch.rand(2, 3, CFG.IMG_SIZE[0], CFG.IMG_SIZE[1])

    def test_forward_output_shape(self):
        logits = self.model(self.batch)
        assert logits.shape == (2, CFG.NUM_CLASSES), \
            f"Expected (2, {CFG.NUM_CLASSES}), got {logits.shape}"

    def test_predict_returns_valid_classes(self):
        preds = self.model.predict(self.batch)
        assert preds.shape == (2,)
        assert torch.all(preds >= 0) and torch.all(preds < CFG.NUM_CLASSES)

    def test_predict_proba_sums_to_one(self):
        probs = self.model.predict_proba(self.batch)
        sums = probs.sum(dim=1)
        assert torch.allclose(sums, torch.ones(2), atol=1e-5), \
            "Class probabilities must sum to 1"

    def test_parameter_count_positive(self):
        n = count_parameters(self.model)
        assert n > 0, "Model must have trainable parameters"

    def test_cnn_backbone_frozen(self):
        """CNN backbone parameters should not require grad."""
        if CFG.CNN_FREEZE:
            for param in self.model.cnn_backbone.parameters():
                assert not param.requires_grad, "CNN backbone should be frozen"

    def test_vqc_weights_trainable(self):
        assert self.model.vqc_weights.requires_grad, "VQC weights must require grad"

    def test_classifier_trainable(self):
        assert self.model.classifier.weight.requires_grad, "Classifier must require grad"


class TestCNNBaseline:
    def setup_method(self):
        self.model = CNNBaseline()
        self.model.eval()
        self.batch = torch.rand(2, 3, CFG.IMG_SIZE[0], CFG.IMG_SIZE[1])

    def test_forward_output_shape(self):
        logits = self.model(self.batch)
        assert logits.shape == (2, CFG.NUM_CLASSES), \
            f"Expected (2, {CFG.NUM_CLASSES}), got {logits.shape}"

    def test_predict_returns_valid_classes(self):
        preds = self.model.predict(self.batch)
        assert preds.shape == (2,)
        assert torch.all(preds >= 0) and torch.all(preds < CFG.NUM_CLASSES)
