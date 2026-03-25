from setuptools import setup, find_packages

setup(
    name="quantumcrop",
    version="0.1.0",
    description="Quantum-Enhanced Crop Disease Classification using Variational Quantum Classifiers",
    author="QBit Farmers — SRM University AP",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pennylane>=0.32.0",
        "torch>=2.3.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "streamlit>=1.35.0",
        "tqdm>=4.66.4",
        "pyyaml>=6.0.1",
    ],
)
