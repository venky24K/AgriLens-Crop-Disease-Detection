"""
run.py — QuantumCrop full pipeline runner (Hybrid Quantum-Classical).

Usage:
    python run.py                    # full pipeline: CNN baseline → Hybrid VQC → evaluate
    python run.py --only-eval        # evaluate already-trained models
    python run.py --dashboard        # launch Streamlit dashboard
    python run.py --max-per-class 50 # limit images per class (faster)
    python run.py --epochs 30        # set VQC training epochs

This is the single entry point for the entire project.
"""

import sys
import argparse
from pathlib import Path

# Make src/ importable
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import CFG


def parse_args():
    parser = argparse.ArgumentParser(description="QuantumCrop Hybrid Pipeline")
    parser.add_argument("--only-eval", action="store_true",
                        help="Only run evaluation on already-trained models")
    parser.add_argument("--dashboard", action="store_true",
                        help="Launch the Streamlit dashboard")
    parser.add_argument("--max-per-class", type=int, default=200,
                        help="Max images per class (default: 200, lower = faster)")
    parser.add_argument("--epochs", type=int, default=CFG.VQC_EPOCHS,
                        help=f"VQC training epochs (default: {CFG.VQC_EPOCHS})")
    parser.add_argument("--cnn-epochs", type=int, default=CFG.CNN_EPOCHS,
                        help=f"CNN baseline epochs (default: {CFG.CNN_EPOCHS})")
    parser.add_argument("--skip-cnn", action="store_true",
                        help="Skip CNN baseline training")
    parser.add_argument("--skip-svm", action="store_true",
                        help="Skip SVM baseline training")
    return parser.parse_args()


def run_dashboard():
    import subprocess
    print("\n🌾 Launching QuantumCrop Dashboard...")
    subprocess.run(["streamlit", "run", "app/main.py"])


def run_pipeline(args):
    import torch
    from data.loader import load_dataset
    from data.preprocess import build_dataloaders
    from training.train import train_hybrid, train_cnn_baseline, load_hybrid_vqc, load_cnn_baseline
    from training.evaluate import (
        evaluate_model, plot_confusion_matrix, plot_training_curves, benchmark_report,
    )

    print("=" * 60)
    print("  🌾 QuantumCrop — Hybrid Quantum-Classical Pipeline")
    print(f"  Device: {CFG.DEVICE}")
    print("=" * 60)

    # ── STEP 1: Load dataset & build DataLoaders ──────────────────────────
    print("\n[1/5] Loading dataset & building DataLoaders...")
    train_rec, val_rec, test_rec = load_dataset(max_per_class=args.max_per_class)
    train_loader, val_loader, test_loader = build_dataloaders(
        train_rec, val_rec, test_rec,
        batch_size=CFG.VQC_BATCH_SIZE,
    )

    # ── STEP 2: Train CNN Baseline ────────────────────────────────────────
    if not args.only_eval and not args.skip_cnn:
        print(f"\n[2/5] Training CNN Baseline ({args.cnn_epochs} epochs)...")
        cnn_loader_train, cnn_loader_val, _ = build_dataloaders(
            train_rec, val_rec, test_rec,
            batch_size=CFG.CNN_BATCH_SIZE,
        )
        cnn_model, cnn_history = train_cnn_baseline(
            cnn_loader_train, cnn_loader_val, epochs=args.cnn_epochs,
        )
        plot_training_curves(
            cnn_history,
            CFG.PLOTS_DIR / "cnn_training_curves.png",
            title_prefix="CNN Baseline",
        )
    elif args.only_eval:
        print("\n[2/5] Loading saved CNN Baseline...")
        cnn_model = load_cnn_baseline()
    else:
        print("\n[2/5] Skipping CNN Baseline (--skip-cnn)")
        cnn_model = None

    # ── STEP 3: Train Hybrid VQC ──────────────────────────────────────────
    if not args.only_eval:
        print(f"\n[3/5] Training Hybrid VQC ({args.epochs} epochs)...")
        CFG.VQC_EPOCHS = args.epochs
        vqc_model, vqc_history = train_hybrid(
            train_loader, val_loader, epochs=args.epochs,
        )
        plot_training_curves(
            vqc_history,
            CFG.PLOTS_DIR / "vqc_training_curves.png",
            title_prefix="Hybrid VQC",
        )
    else:
        print("\n[3/5] Loading saved Hybrid VQC...")
        vqc_model = load_hybrid_vqc()

    # ── STEP 4: (Optional) Train SVM on CNN features ─────────────────────
    svm_results = None
    if not args.skip_svm:
        print("\n[4/5] Training SVM on CNN-extracted features...")
        from models.classical import train_svm, evaluate_svm, save_svm
        import numpy as np

        # Extract features using the CNN backbone
        vqc_model.eval()
        device = CFG.DEVICE

        def extract_cnn_features(loader):
            features, labels = [], []
            with torch.no_grad():
                for X_batch, y_batch in loader:
                    X_batch = X_batch.to(device)
                    cnn_out = vqc_model.cnn_backbone(X_batch)
                    cnn_feat = cnn_out.view(cnn_out.size(0), -1).cpu().numpy()
                    features.append(cnn_feat)
                    labels.append(y_batch.numpy())
            return np.vstack(features), np.concatenate(labels)

        X_train_svm, y_train_svm = extract_cnn_features(train_loader)
        X_test_svm, y_test_svm = extract_cnn_features(test_loader)

        svm_model = train_svm(X_train_svm, y_train_svm)
        save_svm(svm_model)
        svm_results = evaluate_svm(svm_model, X_test_svm, y_test_svm)
    else:
        print("\n[4/5] Skipping SVM (--skip-svm)")

    # ── STEP 5: Evaluate & Benchmark ──────────────────────────────────────
    print("\n[5/5] Evaluating models...")
    vqc_results = evaluate_model(vqc_model, test_loader, model_name="Hybrid VQC")

    plot_confusion_matrix(
        vqc_results["y_true"], vqc_results["y_pred"],
        title="Hybrid VQC Confusion Matrix",
        save_path=CFG.PLOTS_DIR / "vqc_confusion_matrix.png",
    )

    cnn_results = None
    if cnn_model is not None:
        cnn_results = evaluate_model(cnn_model, test_loader, model_name="CNN Baseline")
        plot_confusion_matrix(
            cnn_results["y_true"], cnn_results["y_pred"],
            title="CNN Baseline Confusion Matrix",
            save_path=CFG.PLOTS_DIR / "cnn_confusion_matrix.png",
        )

    if cnn_results is not None:
        benchmark_report(vqc_results, cnn_results, svm_results)

    print("\n✅ Pipeline complete!")
    print(f"   Models   → {CFG.MODELS_DIR}")
    print(f"   Plots    → {CFG.PLOTS_DIR}")
    print(f"   Report   → {CFG.OUTPUTS / 'benchmark_report.txt'}")
    print("\n   Run the dashboard: python run.py --dashboard")


if __name__ == "__main__":
    args = parse_args()
    if args.dashboard:
        run_dashboard()
    else:
        run_pipeline(args)
