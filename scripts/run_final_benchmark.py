import os, sys, time, torch
import numpy as np
import nbformat as nbf
import papermill as pm

# 1. Define Top 10 Classes
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

def check_gpu():
    print("Checking GPU Status...")
    print(f"PyTorch version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"Device: {torch.cuda.get_device_name(0)}")
    else:
        print("WARNING: CUDA not found. Full GPU acceleration will be disabled.")
    return cuda_available

def run_final_benchmark():
    print("\n" + "="*50)
    print("🚀 QUANTUMCROP FINAL GPU BENCHMARK")
    print("="*50)
    
    # Check for lightning.gpu availability
    try:
        import pennylane as qml
        dev = qml.device("lightning.gpu", wires=6)
        print("✅ PennyLane-Lightning-GPU detected!")
        q_device = "lightning.gpu"
    except Exception as e:
        print(f"⚠️ lightning.gpu not available: {e}")
        print("Falling back to lightning.qubit (CPU-optimized)")
        q_device = "lightning.qubit"

    # Create the final notebook
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("# Final GPU Benchmark (Top 10 Classes)"),
        nbf.v4.new_code_cell(
            f"import sys, os\nsys.path.insert(0, os.path.abspath('../src'))\n"
            f"from utils.config import CFG\n"
            f"CFG.DEVICE = 'cuda' if '{torch.cuda.is_available()}' == 'True' else 'cpu'\n"
            f"CFG.QUANTUM_DEVICE = '{q_device}'\n"
            f"CFG.CLASSES = {TOP_10}\n"
            f"CFG.NUM_CLASSES = 10\n"
            f"print(f'Using Device: {{CFG.DEVICE}}')\n"
            f"print(f'Using Quantum Device: {{CFG.QUANTUM_DEVICE}}')"
        ),
        nbf.v4.new_code_cell(
            "from data.loader import load_dataset\n"
            "from data.preprocess import build_dataloaders\n"
            "from training.train import train_hybrid\n"
            "from training.evaluate import evaluate_model, benchmark_report\n\n"
            "train_rec, val_rec, test_rec = load_dataset(max_per_class=400)\n"
            "train_loader, val_loader, test_loader = build_dataloaders(train_rec, val_rec, test_rec, batch_size=32)\n"
            "model, history = train_hybrid(train_loader, val_loader, epochs=30)\n"
            "results = evaluate_model(model, test_loader, 'Final Hybrid VQC (GPU)')\n"
            "print(f'\\nFinal Accuracy: {results[\"accuracy\"]:.4f}')"
        )
    ]
    
    nbf.write(nb, "notebooks/06_final_gpu_benchmark.ipynb")
    print("\nExecuting final benchmark notebook via papermill...")
    pm.execute_notebook(
        "notebooks/06_final_gpu_benchmark.ipynb",
        "notebooks/06_final_gpu_benchmark_out.ipynb",
        kernel_name="python3"
    )
    print("✅ Benchmark complete!")

if __name__ == "__main__":
    if check_gpu():
        run_final_benchmark()
    else:
        print("Aborting GPU benchmark task. Please ensure CUDA-enabled PyTorch is installed correctly.")
