import nbformat
import sys
import os
from pathlib import Path

def process_notebook(nb_path):
    print(f"Processing {nb_path}...")
    try:
        nb = nbformat.read(nb_path, as_version=4)
    except Exception as e:
        print(f"Failed to read {nb_path}: {e}")
        return

    # Replace old code with new code
    for cell in nb.cells:
        if cell.cell_type == 'code':
            src = cell.source
            # 1. Update data paths if hardcoded
            if "data/raw/PlantVillage" in src:
                src = src.replace("data/raw/PlantVillage", "data/raw/MasterDataset")
            
            # Use regex to replace any max_per_class=\\d+ with max_per_class=5
            import re
            src = re.sub(r'max_per_class=\d+', 'max_per_class=5', src)

            # 2. Fix the CFG.CLASSES reference if it assumes a list of 5
            if "CFG.CLASSES" in src and "len(CFG.CLASSES)" not in src and "enumerate(CFG.CLASSES)" not in src:
                # Some notebooks might try to print CFG.CLASSES directly.
                pass
                
            # Decrease epochs in VQC/CNN baseline for fast notebook execution
            if "report = benchmark_report(vqc_results, svm_results)" in src:
                src = src.replace("benchmark_report(vqc_results, svm_results)", "benchmark_report(vqc_results, svm_results, None)")

            if "CNN_EPOCHS" in src or "epochs=" in src:
                src = re.sub(r'epochs=\d+', 'epochs=1', src)

            cell.source = src



    # Save inplace
    nbformat.write(nb, nb_path)
    print(f"Updated {nb_path}")

for nb in ["01_data_exploration.ipynb", "02_classical_baseline.ipynb", "03_vqc_experiment.ipynb"]:
    process_notebook(Path("notebooks") / nb)
