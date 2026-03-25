import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}

nb.cells = [
    nbf.v4.new_markdown_cell(
        "# 04 Advanced Quantum Algorithm Training\n\n"
        "**Hybrid VQC with Data Re-uploading + StronglyEntangling Rotations**\n\n"
        "Upgrades over basic VQC:\n"
        "- Data Re-uploading: input re-encoded at every layer (Pérez-Salinas 2020)\n"
        "- Full Rot(φ,θ,ω) gates instead of basic RY/RZ\n"
        "- Cross-qubit CNOT entanglement\n"
        "- Deeper feature reducer: 512→128→8\n"
        "- Deeper classifier: 8→64→NUM_CLASSES\n"
        "- 6 VQC layers instead of 4\n"
        "- 200 images/class, 10 epochs"
    ),
    nbf.v4.new_code_cell(
        "import sys, os\n"
        "sys.path.insert(0, os.path.abspath('../src'))\n"
        "import torch\n"
        "from utils.config import CFG\n"
        "from data.loader import load_dataset\n"
        "from data.preprocess import build_dataloaders\n"
        "from training.train import train_hybrid\n"
        "from training.evaluate import evaluate_model, plot_training_curves, benchmark_report\n"
        "from models.classical import load_svm, evaluate_svm, load_rf, evaluate_rf, load_lr, evaluate_lr\n"
        "print(f'Device: {CFG.DEVICE}')\n"
        "print(f'Qubits: {CFG.N_QUBITS}, Quantum Backend: {CFG.QUANTUM_DEVICE}')\n"
        "print('All imports OK')"
    ),
    nbf.v4.new_code_cell(
        "# Load dataset with 200 images per class for robust training\n"
        "print('Loading dataset (200 images per class)...')\n"
        "train_rec, val_rec, test_rec = load_dataset(max_per_class=200)\n"
        "print(f'Records -> Train: {len(train_rec)}, Val: {len(val_rec)}, Test: {len(test_rec)}')\n"
        "\n"
        "# Build PyTorch DataLoaders\n"
        "train_loader, val_loader, test_loader = build_dataloaders(\n"
        "    train_rec, val_rec, test_rec,\n"
        "    batch_size=CFG.VQC_BATCH_SIZE, num_workers=0\n"
        ")\n"
        "print(f'Batches -> Train: {len(train_loader)}, Val: {len(val_loader)}, Test: {len(test_loader)}')"
    ),
    nbf.v4.new_code_cell(
        "# Train Hybrid VQC for 10 epochs\n"
        "print('='*60)\n"
        "print('Training Advanced Hybrid VQC (Data Re-uploading)')\n"
        "print('  - 6 VQC layers with Rot + cross-CNOT entanglement')\n"
        "print('  - Data re-uploaded at every layer for max expressivity')\n"
        "print('  - Deep feature reducer: 512->128->8')\n"
        "print('  - Deep classifier: 8->64->NUM_CLASSES')\n"
        "print('='*60)\n"
        "\n"
        "model, history = train_hybrid(train_loader, val_loader, epochs=10)\n"
        "plot_training_curves(history, CFG.PLOTS_DIR / 'hybrid_vqc_advanced_curves.png')\n"
        "print('Training complete!')"
    ),
    nbf.v4.new_code_cell(
        "# Evaluate on test set\n"
        "print('Evaluating Advanced Hybrid VQC on test set...')\n"
        "hybrid_results = evaluate_model(model, test_loader, 'Advanced Hybrid VQC')\n"
        "print(f'\\nAdvanced Hybrid VQC Accuracy: {hybrid_results[\"accuracy\"]:.4f}')"
    ),
    nbf.v4.new_code_cell(
        "# Generate full N-way benchmark with classical baselines\n"
        "print('Generating final benchmark report...')\n"
        "try:\n"
        "    from data.preprocess import build_feature_matrix\n"
        "    X_test_feat, y_test_feat = build_feature_matrix(test_rec, desc='Test features')\n"
        "    svm_model = load_svm()\n"
        "    svm_results = evaluate_svm(svm_model, X_test_feat, y_test_feat)\n"
        "    rf_model = load_rf()\n"
        "    rf_results = evaluate_rf(rf_model, X_test_feat, y_test_feat)\n"
        "    lr_model = load_lr()\n"
        "    lr_results = evaluate_lr(lr_model, X_test_feat, y_test_feat)\n"
        "except Exception as e:\n"
        "    print(f'Could not load classical baselines: {e}')\n"
        "    svm_results = rf_results = lr_results = None\n"
        "\n"
        "benchmark_report(\n"
        "    hybrid_results=hybrid_results,\n"
        "    svm_results=svm_results,\n"
        "    rf_results=rf_results,\n"
        "    lr_results=lr_results\n"
        ")\n"
        "print('Done!')"
    ),
]

nbf.write(nb, "notebooks/04_best_quantum_algorithms.ipynb")
print("Notebook generated successfully.")
