"""
vqc.py — Advanced Hybrid Quantum-Classical Model.

Architecture (Upgraded):
  1. CNN Backbone       — Pre-trained ResNet-18 (frozen) → 512-d features
  2. Feature Reducer    — Linear(512 → 128) → ReLU → Linear(128 → N_QUBITS) → Tanh
  3. Data Re-uploading  — Re-encode inputs at EVERY layer (proven expressivity boost)
  4. StronglyEntangling — Full Rot(φ,θ,ω) + all-to-all CNOT entanglement per layer
  5. Measurement        — PauliZ expectations → FC(N_QUBITS→64) → ReLU → FC(64→classes)

Key upgrades over basic VQC:
  - Data Re-uploading: exponentially increases model expressivity (Pérez-Salinas 2020)
  - StronglyEntanglingLayers: 3 rotation gates per qubit + full entanglement
  - Deeper classical head: 2-layer MLP instead of single linear
  - Deeper feature reducer: 2-layer MLP for better dimensionality reduction
  - 6 VQC layers instead of 4 for more quantum depth
"""

import numpy as np
import pennylane as qml
import torch
import torch.nn as nn
import torchvision.models as models
from utils.config import CFG


# ── 1. Build the PennyLane device ────────────────────────────────────────────
dev = qml.device(CFG.QUANTUM_DEVICE, wires=CFG.N_QUBITS, shots=CFG.SHOTS)

N_VQC_LAYERS = 6  # deeper circuit for better expressivity


# ── 2. Advanced VQC with Data Re-uploading ────────────────────────────────────
def quantum_circuit_func(inputs, weights):
    """
    Data Re-uploading VQC using StronglyEntanglingLayers logic.
    Supports batching via inputs[..., i].
    """
    n_qubits = CFG.N_QUBITS
    n_layers = weights.shape[0]  # weights shape (L, Q, 3)
    
    for layer in range(n_layers):
        # Data Re-uploading (Batch-aware)
        for i in range(n_qubits):
            qml.RY((inputs[..., i] + 1.0) * 1.570796, wires=i)
            
        # Strongly Entangling Rotations
        for i in range(n_qubits):
            qml.Rot(weights[layer, i, 0], weights[layer, i, 1], weights[layer, i, 2], wires=i)
            
        # Entanglement
        for i in range(n_qubits):
            qml.CNOT(wires=[i, (i + 1) % n_qubits])
            
    return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]


# ── 3. Advanced Hybrid Quantum-Classical Model ──────────────────────────────
class HybridQuantumClassifier(nn.Module):
    """
    Optimized Hybrid model with BatchNorm and Data Re-uploading.
    """

    def __init__(self):
        super().__init__()

        # CNN Backbone (frozen)
        backbone = models.resnet18(pretrained=CFG.CNN_PRETRAINED)
        self.cnn_backbone = nn.Sequential(*list(backbone.children())[:-1])
        for param in self.cnn_backbone.parameters():
            param.requires_grad = False
        self.cnn_backbone.eval()

        # Deep Feature Reducer with BatchNorm
        self.feature_reducer = nn.Sequential(
            nn.Linear(CFG.CNN_FEATURE_DIM, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, CFG.N_QUBITS),
            nn.BatchNorm1d(CFG.N_QUBITS),
            nn.Tanh(),
        )

        # Quantum Layer using PennyLane TorchLayer
        weight_shapes = {"weights": (CFG.N_LAYERS, CFG.N_QUBITS, 3)}
        
        @qml.qnode(dev, interface="torch")
        def qnode(inputs, weights):
            return quantum_circuit_func(inputs, weights)
            
        self.quantum_layer = qml.qnn.TorchLayer(qnode, weight_shapes)

        # Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(CFG.N_QUBITS, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, CFG.NUM_CLASSES),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # CNN
        with torch.no_grad():
            cnn_out = self.cnn_backbone(x)
        cnn_features = cnn_out.view(cnn_out.size(0), -1)

        # Reducer
        reduced = self.feature_reducer(cnn_features)

        # Quantum
        quantum_out = self.quantum_layer(reduced)

        # Classifier
        logits = self.classifier(quantum_out)
        return logits

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return torch.argmax(self.forward(x), dim=1)

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return torch.softmax(self.forward(x), dim=1)


# ── Utility functions ────────────────────────────────────────────────────────

def get_circuit_diagram() -> str:
    """Return a text diagram of the quantum circuit for inspection."""
    dummy_inputs  = torch.zeros(CFG.N_QUBITS)
    dummy_weights = torch.zeros(CFG.N_LAYERS, CFG.N_QUBITS, 2)
    return qml.draw(quantum_circuit)(dummy_inputs, dummy_weights)


def count_parameters(model: nn.Module) -> int:
    """Count total trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ── Legacy VQC for Notebook 03 Compatibility ─────────────────────────────────

class QuantumClassifier(nn.Module):
    """
    Legacy 6-qubit pure VQC classifier used by Notebook 03.
    Expects manually extracted 6-dimensional angle features.
    """
    def __init__(self, n_qubits=6, n_layers=3, num_classes=5):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.num_classes = num_classes

        self.dev = qml.device('lightning.qubit', wires=n_qubits)
        self.weight_shapes = {"weights": (n_layers, n_qubits)}

        @qml.qnode(self.dev, interface='torch')
        def qnode(inputs, weights):
            qml.AngleEmbedding(inputs, wires=range(self.n_qubits))
            qml.BasicEntanglerLayers(weights, wires=range(self.n_qubits))
            return [qml.expval(qml.PauliZ(w)) for w in range(self.n_qubits)]

        self.qlayer = qml.qnn.TorchLayer(qnode, self.weight_shapes)
        self.fc = nn.Linear(n_qubits, len(CFG.CLASSES) if CFG.CLASSES else num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        q_out = self.qlayer(x)
        return self.fc(q_out)

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            logits = self.forward(x)
            return torch.argmax(logits, dim=1)

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            logits = self.forward(x)
            return torch.softmax(logits, dim=1)

