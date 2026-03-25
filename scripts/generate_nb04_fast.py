import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}

TOP_10 = [
    'tomato_tomato_yellowleaf_curl_virus',
    'tomato_bacterial_spot',
    'potato_early_blight',
    'tomato_late_blight',
    'apple_apple_scab',
    'grape_black_rot',
    'apple_cedar_apple_rust',
    'tomato_spider_mites_two_spotted_spider_mite',
    'tomato_target_spot',
    'grape_esca_black_measles'
]

nb.cells = [
    nbf.v4.new_markdown_cell(
        "# 04 FAST Best Quantum Algorithm (Top 10 Classes)\n\n"
        "**Hybrid VQC with Data Re-uploading — Optimized for Speed & Accuracy**\n\n"
        "Target: 10 most common diseases only (10 classes instead of 101).\n"
        "Data: 400 images per class (robust sample).\n"
        "Model: Advanced 6-layer Data Re-uploading circuit."
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
        "\n"
        f"classes = {TOP_10}\n"
        "CFG.CLASSES = classes\n"
        "CFG.NUM_CLASSES = len(classes)\n"
        "print(f'Training on {len(classes)} classes...')\n"
        "print(f'Device: {CFG.DEVICE}')"
    ),
    nbf.v4.new_code_cell(
        "print('Loading Top 10 dataset (400 images per class)...')\n"
        "train_rec, val_rec, test_rec = load_dataset(max_per_class=400)\n"
        "train_loader, val_loader, test_loader = build_dataloaders(\n"
        "    train_rec, val_rec, test_rec,\n"
        "    batch_size=CFG.VQC_BATCH_SIZE, num_workers=0\n"
        ")\n"
        "print(f'Batches -> Train: {len(train_loader)}, Val: {len(val_loader)}, Test: {len(test_loader)}')"
    ),
    nbf.v4.new_code_cell(
        "print('Training Advanced Hybrid VQC (Top 10)...')\n"
        "model, history = train_hybrid(train_loader, val_loader, epochs=10)\n"
        "plot_training_curves(history, CFG.PLOTS_DIR / 'hybrid_vqc_fast_curves.png')\n"
        "print('Training complete!')"
    ),
    nbf.v4.new_code_cell(
        "print('Evaluating on test set...')\n"
        "results = evaluate_model(model, test_loader, 'Fast Hybrid VQC')\n"
        "print(f'\\nAccuracy: {results[\"accuracy\"]:.4f}')"
    ),
]

nbf.write(nb, "notebooks/04_best_quantum_algorithms.ipynb")
print("Fast notebook generated.")
