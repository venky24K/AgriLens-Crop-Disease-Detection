"""
evaluate.py — Evaluate and compare Hybrid VQC vs CNN vs SVM.

Produces (following Lakhani 2025):
  - Per-class precision, recall, F1-score
  - Overall accuracy and macro F1
  - Confusion matrix plots
  - Training curve plots
  - Benchmark summary (3-way comparison)
  - Statistical significance test (paired t-test)
"""

import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Union
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report,
)

from utils.config import CFG


def evaluate_model(
    model,
    test_loader: DataLoader,
    model_name: str = "Model",
) -> dict:
    """
    Evaluate any PyTorch model on the test DataLoader.

    Returns dict with accuracy, precision, recall, f1_macro, report, y_pred, y_true.
    """
    device = CFG.DEVICE
    model.eval()
    model.to(device)

    all_preds, all_labels = [], []

    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            logits = model(X_batch)
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(y_batch.numpy())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)

    acc       = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    recall    = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1        = f1_score(y_true, y_pred, average="macro", zero_division=0)

    report = classification_report(
        y_true, y_pred,
        target_names=CFG.CLASSES,
        labels=range(len(CFG.CLASSES)),
        zero_division=0,
    )

    print(f"\n{model_name} Results:")
    print(f"  Accuracy  : {acc:.4f}")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall:.4f}")
    print(f"  Macro F1  : {f1:.4f}")
    print(f"\n{report}")

    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1_macro": f1,
        "report": report,
        "y_pred": y_pred,
        "y_true": y_true,
    }


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    title: str,
    save_path: Path,
) -> None:
    """Plot and save a confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred, labels=range(len(CFG.CLASSES)))
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Greens",
        xticklabels=CFG.CLASSES, yticklabels=CFG.CLASSES, ax=ax
    )
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved confusion matrix → {save_path}")


def plot_training_curves(history: dict, save_path: Path, title_prefix: str = "VQC") -> None:
    """Plot training & validation loss + accuracy curves."""
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(epochs, history["train_loss"], label="Train Loss", color="#6C63FF")
    ax1.plot(epochs, history["val_loss"],   label="Val Loss",   color="#FF6B6B", linestyle="--")
    ax1.set_title(f"{title_prefix} Training Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Cross-Entropy Loss")
    ax1.legend()

    ax2.plot(epochs, history["val_acc"], label="Val Accuracy", color="#06D6A0")
    ax2.set_title(f"{title_prefix} Validation Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_ylim(0, 1)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved training curves → {save_path}")


def benchmark_report(
    hybrid_results: Union[dict, None] = None,
    cnn_results: Union[dict, None] = None,
    svm_results: Union[dict, None] = None,
    save_path: Union[Path, None] = None,
    rf_results: Union[dict, None] = None,
    lr_results: Union[dict, None] = None,
) -> str:
    """
    Generate an N-way benchmark summary (Hybrid VQC vs Classical Baselines).
    Following the paper's comparison format.
    """
    baselines = {}
    if hybrid_results: baselines["Hybrid VQC"] = hybrid_results
    if cnn_results: baselines["Baseline 1"] = cnn_results
    if svm_results: baselines["SVM (Linear)"] = svm_results
    if rf_results: baselines["Random Forest"] = rf_results
    if lr_results: baselines["Logistic Regression"] = lr_results

    names_str = " vs ".join(baselines.keys())

    lines = [
        "=" * 100,
        "  QuantumCrop — Benchmark Report",
        f"  {names_str}",
        "=" * 100,
        "",
    ]
    
    header = f"  {'Metric':<15}"
    for name in baselines.keys():
        header += f" {name:>18}"
    lines.append(header)
    lines.append("-" * 100)

    for m_name, k in [('Accuracy', 'accuracy'), ('Precision', 'precision'), ('Recall', 'recall'), ('Macro F1', 'f1_macro')]:
        row = f"  {m_name:<15}"
        for res in baselines.values():
            row += f" {res.get(k, 0):>18.4f}"
        lines.append(row)

    lines.extend([
        "=" * 100,
    ])

    for name, res in baselines.items():
        if "report" in res:
            lines.extend([
                "",
                f"{name} Classification Report:",
            res.get("report", ""),
        ])

    report_str = "\n".join(lines)
    print(report_str)

    out = save_path or (CFG.OUTPUTS / "benchmark_report.txt")
    out.write_text(report_str)
    print(f"\n  Full report saved → {out}")
    return report_str


# ── Legacy Functions ─────────────────────────────────────────────────────────
from sklearn.metrics import precision_score, recall_score, classification_report

def evaluate_vqc(model, X_test, y_test):
    model.eval()
    with torch.no_grad():
        Xt = torch.tensor(X_test, dtype=torch.float32)
        logits = model(Xt)
        y_pred = torch.argmax(logits, dim=1).numpy()
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    
    unique_labels = sorted(set(y_test) | set(y_pred))
    names = CFG.CLASSES if CFG.CLASSES else [str(i) for i in range(101)]
    report_names = [names[i] for i in unique_labels]
    report = classification_report(y_test, y_pred, labels=unique_labels, target_names=report_names, zero_division=0)
    
    return {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1_macro': f1, 'y_pred': y_pred, 'report': report}

