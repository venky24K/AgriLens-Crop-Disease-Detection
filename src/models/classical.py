"""
classical.py — Classical baselines for benchmarking against QuantumCrop VQC.

Provides two classical baselines (following Lakhani 2025):
  1. CNNBaseline — Fine-tuned ResNet-18 (the paper's primary comparison)
  2. SVM         — RBF-kernel SVM on CNN-extracted features

Both use same data splits and metrics for fair comparison.
"""

import numpy as np
import joblib
import torch
import torch.nn as nn
import torchvision.models as models
from pathlib import Path
from typing import Union
from sklearn.svm import SVC, LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, classification_report

from utils.config import CFG


# ── 1. CNN Baseline (paper's primary classical comparator) ───────────────────

class CNNBaseline(nn.Module):
    """
    Classical CNN baseline: ResNet-18 (fine-tuned) with a classification head.

    Architecture:
      ResNet-18 (pre-trained) → Global Avg Pool → FC(512 → NUM_CLASSES)

    This is the "baseline CNN" from the paper that achieved 91.4% accuracy.
    """

    def __init__(self, freeze_backbone: bool = False):
        super().__init__()

        backbone = models.resnet18(pretrained=True)
        # Replace the final FC layer with our classification head
        num_features = backbone.fc.in_features
        backbone.fc = nn.Linear(num_features, CFG.NUM_CLASSES)

        self.model = backbone

        if freeze_backbone:
            # Freeze all except the final FC layer
            for name, param in self.model.named_parameters():
                if "fc" not in name:
                    param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch_size, 3, 224, 224)

        Returns:
            logits: Tensor of shape (batch_size, NUM_CLASSES)
        """
        return self.model(x)

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Return predicted class indices."""
        with torch.no_grad():
            logits = self.forward(x)
            return torch.argmax(logits, dim=1)

    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Return class probabilities via softmax."""
        with torch.no_grad():
            logits = self.forward(x)
            return torch.softmax(logits, dim=1)


# ── 2. SVM Baseline ─────────────────────────────────────────────────────────

def build_svm() -> Pipeline:
    """
    Returns an sklearn Pipeline: StandardScaler → SVM(RBF kernel).
    Operates on CNN-extracted features, not raw images.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("svm", LinearSVC(
            C=CFG.SVM_C,
            dual=False,
            random_state=CFG.RANDOM_SEED,
        ))
    ])


def train_svm(X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    """Train and return a fitted SVM pipeline."""
    model = build_svm()
    print("  Training SVM baseline on CNN features...")
    model.fit(X_train, y_train)
    print("  SVM training complete.")
    return model


def evaluate_svm(
    model: Pipeline,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: Union[list, None] = None,
) -> dict:
    """Evaluate SVM on test set. Returns dict with accuracy, F1, report."""
    names = class_names or CFG.CLASSES
    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    f1     = f1_score(y_test, y_pred, average="macro")
    from sklearn.metrics import precision_score, recall_score
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)

    unique_labels = sorted(set(y_test) | set(y_pred))
    
    # Fallback if names is still None (e.g. if CFG.CLASSES hasn't been populated yet)
    if names is None:
        report_names = [f"Class {i}" for i in unique_labels]
    else:
        report_names = [names[i] for i in unique_labels]
        
    report = classification_report(y_test, y_pred, labels=unique_labels, target_names=report_names, zero_division=0)

    print(f"\nSVM Results:")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Macro F1 : {f1:.4f}")
    print(f"\n{report}")

    return {"accuracy": acc, "precision": precision, "recall": recall, "f1_macro": f1, "report": report, "y_pred": y_pred}



def save_svm(model: Pipeline, path: Union[Path, None] = None) -> Path:
    """Persist trained SVM to disk."""
    save_path = path or (CFG.MODELS_DIR / "svm_baseline.joblib")
    joblib.dump(model, save_path)
    print(f"  SVM saved → {save_path}")
    return save_path


def load_svm(path: Union[Path, None] = None) -> Pipeline:
    """Load a previously saved SVM."""
    load_path = path or (CFG.MODELS_DIR / "svm_baseline.joblib")
    return joblib.load(load_path)


# ── 3. Random Forest Baseline ───────────────────────────────────────────────
from sklearn.ensemble import RandomForestClassifier

def build_rf() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=100,
            random_state=CFG.RANDOM_SEED,
            n_jobs=None
        ))
    ])

def train_rf(X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    model = build_rf()
    print("  Training Random Forest baseline on CNN features...")
    model.fit(X_train, y_train)
    print("  Random Forest training complete.")
    return model

def evaluate_rf(model: Pipeline, X_test: np.ndarray, y_test: np.ndarray, class_names: Union[list, None] = None) -> dict:
    names = class_names or CFG.CLASSES
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    from sklearn.metrics import precision_score, recall_score
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)

    unique_labels = sorted(set(y_test) | set(y_pred))
    
    if names is None:
        report_names = [f"Class {i}" for i in unique_labels]
    else:
        report_names = [names[i] for i in unique_labels]
        
    report = classification_report(y_test, y_pred, labels=unique_labels, target_names=report_names, zero_division=0)

    print(f"\nRandom Forest Results:")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Macro F1 : {f1:.4f}")

    return {"accuracy": acc, "precision": precision, "recall": recall, "f1_macro": f1, "report": report, "y_pred": y_pred}

def save_rf(model: Pipeline, path: Union[Path, None] = None) -> Path:
    save_path = path or (CFG.MODELS_DIR / "rf_baseline.joblib")
    joblib.dump(model, save_path)
    print(f"  Random Forest saved → {save_path}")
    return save_path

def load_rf(path: Union[Path, None] = None) -> Pipeline:
    load_path = path or (CFG.MODELS_DIR / "rf_baseline.joblib")
    return joblib.load(load_path)


# ── 4. Logistic Regression Baseline ─────────────────────────────────────────
from sklearn.linear_model import LogisticRegression

def build_lr() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(
            max_iter=1000,
            random_state=CFG.RANDOM_SEED,
            n_jobs=None
        ))
    ])

def train_lr(X_train: np.ndarray, y_train: np.ndarray) -> Pipeline:
    model = build_lr()
    print("  Training Logistic Regression baseline on CNN features...")
    model.fit(X_train, y_train)
    print("  Logistic Regression training complete.")
    return model

def evaluate_lr(model: Pipeline, X_test: np.ndarray, y_test: np.ndarray, class_names: Union[list, None] = None) -> dict:
    names = class_names or CFG.CLASSES
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    from sklearn.metrics import precision_score, recall_score
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)

    unique_labels = sorted(set(y_test) | set(y_pred))
    
    if names is None:
        report_names = [f"Class {i}" for i in unique_labels]
    else:
        report_names = [names[i] for i in unique_labels]
        
    report = classification_report(y_test, y_pred, labels=unique_labels, target_names=report_names, zero_division=0)

    print(f"\nLogistic Regression Results:")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Macro F1 : {f1:.4f}")

    return {"accuracy": acc, "precision": precision, "recall": recall, "f1_macro": f1, "report": report, "y_pred": y_pred}

def save_lr(model: Pipeline, path: Union[Path, None] = None) -> Path:
    save_path = path or (CFG.MODELS_DIR / "lr_baseline.joblib")
    joblib.dump(model, save_path)
    print(f"  Logistic Regression saved → {save_path}")
    return save_path

def load_lr(path: Union[Path, None] = None) -> Pipeline:
    load_path = path or (CFG.MODELS_DIR / "lr_baseline.joblib")
    return joblib.load(load_path)

