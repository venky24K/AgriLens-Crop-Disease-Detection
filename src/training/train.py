"""
train.py — Training loops for QuantumCrop models.

Supports:
  - Hybrid VQC training (CNN backbone frozen, quantum + head trainable)
  - CNN baseline training (full fine-tuning)
  - Adam optimizer, CrossEntropy loss, cosine LR scheduler
  - Checkpoint saving on best validation accuracy
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
from typing import Tuple, Union

from models.vqc import HybridQuantumClassifier, count_parameters
from models.classical import CNNBaseline
from utils.config import CFG


def train_hybrid(
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = CFG.VQC_EPOCHS,
    lr: float = CFG.VQC_LR,
    save_path: Union[Path, None] = None,
) -> Tuple[HybridQuantumClassifier, dict]:
    """
    Train the Hybrid Quantum-Classical model.

    Only trainable parameters are optimized:
      - Feature reducer (Linear 512→8)
      - VQC weights (variational circuit parameters)
      - Classifier head (Linear 8→5)

    The CNN backbone (ResNet-18) is frozen.

    Returns:
        model   : trained HybridQuantumClassifier
        history : dict with train_loss, val_loss, val_acc per epoch
    """
    device = CFG.DEVICE
    model = HybridQuantumClassifier().to(device)

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    print(f"\nQuantumCrop Hybrid VQC — {count_parameters(model)} trainable parameters")
    print(f"  Qubits : {CFG.N_QUBITS}  |  Layers : {CFG.N_LAYERS}  |  Classes : {CFG.NUM_CLASSES}")
    print(f"  Device : {device}  |  Quantum : {CFG.QUANTUM_DEVICE}")

    optimizer  = torch.optim.Adam(trainable_params, lr=lr)
    criterion  = nn.CrossEntropyLoss()
    scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    history = {"train_loss": [], "val_loss": [], "val_acc": []}
    best_val_acc = 0.0
    save_path = save_path or (CFG.MODELS_DIR / "hybrid_vqc_best.pt")

    for epoch in range(1, epochs + 1):
        # ── Train ─────────────────────────────────────────────────────────
        model.train()
        if CFG.CNN_FREEZE:
            model.cnn_backbone.eval()  # keep BN layers in eval mode

        epoch_loss = 0.0
        n_samples = 0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * X_batch.size(0)
            n_samples += X_batch.size(0)

        train_loss = epoch_loss / n_samples
        scheduler.step()

        # ── Validate ──────────────────────────────────────────────────────
        model.eval()
        val_loss_total, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)

                logits = model(X_batch)
                val_loss_total += criterion(logits, y_batch).item() * X_batch.size(0)
                preds = torch.argmax(logits, dim=1)
                correct += (preds == y_batch).sum().item()
                total += y_batch.size(0)

        val_loss = val_loss_total / total
        val_acc = correct / total

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        # ── Checkpoint ────────────────────────────────────────────────────
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_path)

        if epoch % CFG.LOG_INTERVAL == 0 or epoch == 1:
            print(
                f"  Epoch {epoch:>3}/{epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Acc: {val_acc:.4f}"
                + (" ✓ best" if val_acc == best_val_acc else "")
            )

    print(f"\nHybrid VQC training complete. Best val accuracy: {best_val_acc:.4f}")
    print(f"Best model saved → {save_path}")

    # Load best weights before returning
    model.load_state_dict(torch.load(save_path, map_location=device))
    return model, history


def train_cnn_baseline(
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = CFG.CNN_EPOCHS,
    lr: float = CFG.CNN_LR,
    save_path: Union[Path, None] = None,
) -> Tuple[CNNBaseline, dict]:
    """
    Train the CNN baseline (ResNet-18, fine-tuned).

    This is the paper's classical comparison model (target: ~91% accuracy).

    Returns:
        model   : trained CNNBaseline
        history : dict with train_loss, val_loss, val_acc per epoch
    """
    device = CFG.DEVICE
    model = CNNBaseline(freeze_backbone=False).to(device)

    print(f"\nCNN Baseline (ResNet-18) — {count_parameters(model)} trainable parameters")
    print(f"  Device : {device}")

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    history = {"train_loss": [], "val_loss": [], "val_acc": []}
    best_val_acc = 0.0
    save_path = save_path or (CFG.MODELS_DIR / "cnn_baseline_best.pt")

    for epoch in range(1, epochs + 1):
        # ── Train ─────────────────────────────────────────────────────────
        model.train()
        epoch_loss = 0.0
        n_samples = 0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * X_batch.size(0)
            n_samples += X_batch.size(0)

        train_loss = epoch_loss / n_samples
        scheduler.step()

        # ── Validate ──────────────────────────────────────────────────────
        model.eval()
        val_loss_total, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)

                logits = model(X_batch)
                val_loss_total += criterion(logits, y_batch).item() * X_batch.size(0)
                preds = torch.argmax(logits, dim=1)
                correct += (preds == y_batch).sum().item()
                total += y_batch.size(0)

        val_loss = val_loss_total / total
        val_acc = correct / total

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        # ── Checkpoint ────────────────────────────────────────────────────
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_path)

        if epoch % CFG.LOG_INTERVAL == 0 or epoch == 1:
            print(
                f"  Epoch {epoch:>3}/{epochs} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Acc: {val_acc:.4f}"
                + (" ✓ best" if val_acc == best_val_acc else "")
            )

    print(f"\nCNN Baseline training complete. Best val accuracy: {best_val_acc:.4f}")
    print(f"Best model saved → {save_path}")

    model.load_state_dict(torch.load(save_path, map_location=device))
    return model, history


def load_hybrid_vqc(path: Union[Path, None] = None) -> HybridQuantumClassifier:
    """Load a saved Hybrid VQC checkpoint."""
    load_path = path or (CFG.MODELS_DIR / "hybrid_vqc_best.pt")
    model = HybridQuantumClassifier()
    model.load_state_dict(torch.load(load_path, map_location=CFG.DEVICE))
    model.eval()
    return model.to(CFG.DEVICE)


def load_cnn_baseline(path: Union[Path, None] = None) -> CNNBaseline:
    """Load a saved CNN Baseline checkpoint."""
    load_path = path or (CFG.MODELS_DIR / "cnn_baseline_best.pt")
    model = CNNBaseline()
    model.load_state_dict(torch.load(load_path, map_location=CFG.DEVICE))
    model.eval()
    return model.to(CFG.DEVICE)


# ── Legacy Functions ─────────────────────────────────────────────────────────

import torch.optim as optim
from models.vqc import QuantumClassifier

def train_vqc(X_train, y_train, X_val, y_val, epochs=1):
    model = QuantumClassifier()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    Xt = torch.tensor(X_train, dtype=torch.float32)
    yt = torch.tensor(y_train, dtype=torch.long)
    try:
        Xvt = torch.tensor(X_val, dtype=torch.float32)
        yvt = torch.tensor(y_val, dtype=torch.long)
    except Exception:
        Xvt, yvt = Xt, yt

    history = {'train_loss': [], 'val_loss': [], 'val_acc': []}
    for _ in range(epochs):
        model.train()
        optimizer.zero_grad()
        out = model(Xt)
        loss = criterion(out, yt)
        loss.backward()
        optimizer.step()
        
        model.eval()
        with torch.no_grad():
            vout = model(Xvt)
            vloss = criterion(vout, yvt)
            vacc = (torch.argmax(vout, 1) == yvt).float().mean()
            
        history['train_loss'].append(loss.item())
        history['val_loss'].append(vloss.item())
        history['val_acc'].append(vacc.item())
    
    return model, history

def load_vqc(): pass
