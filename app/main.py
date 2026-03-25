"""
main.py — QuantumCrop Streamlit Dashboard (Hybrid Quantum-Classical).

Run with:
    streamlit run app/main.py

Features:
  - Upload a crop image → get disease prediction + confidence
  - Shows quantum circuit diagram
  - Displays benchmark comparison (Hybrid VQC vs CNN vs SVM)
"""

import sys
from pathlib import Path

# Make src/ importable when running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
import numpy as np
import torch
from PIL import Image

from utils.config import CFG
from data.preprocess import preprocess_single_image
from models.vqc import get_circuit_diagram

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=CFG.APP_TITLE,
    page_icon="🌾",
    layout="wide",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title(f"{CFG.APP_TITLE}")
st.markdown(f"### {CFG.APP_SUBTITLE}")
st.markdown(
    "Upload a crop leaf image — QuantumCrop's Hybrid Quantum-Classical model "
    "(ResNet-18 + VQC) will detect the disease and report its confidence."
)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    show_circuit   = st.checkbox("Show quantum circuit diagram", value=False)
    show_benchmark = st.checkbox("Show benchmark report", value=False)
    st.divider()
    st.markdown("**Architecture:**")
    st.markdown(f"- CNN: ResNet-18 (frozen)")
    st.markdown(f"- Qubits: {CFG.N_QUBITS}")
    st.markdown(f"- Layers: {CFG.N_LAYERS}")
    st.markdown(f"- Device: `{CFG.DEVICE}`")
    st.divider()
    st.markdown("**Classes detected:**")
    for cls in CFG.CLASSES:
        st.markdown(f"- {cls.replace('_', ' ')}")

# ── Model loader (cached) ─────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model_path = CFG.MODELS_DIR / "hybrid_vqc_best.pt"
    if not model_path.exists():
        return None
    from models.vqc import HybridQuantumClassifier
    model = HybridQuantumClassifier()
    model.load_state_dict(torch.load(model_path, map_location=CFG.DEVICE))
    model.eval()
    return model.to(CFG.DEVICE)

model = load_model()

# ── Main: Upload & Predict ────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📷 Upload Crop Image")
    uploaded = st.file_uploader(
        "Choose a crop leaf image (JPG / PNG)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded Image", use_column_width=True)

with col2:
    st.subheader("🔬 Diagnosis")

    if uploaded is None:
        st.info("Upload an image on the left to get a diagnosis.")
    elif model is None:
        st.warning(
            "⚠️ No trained model found.\n\n"
            "Train the Hybrid VQC first:\n"
            "```bash\npython run.py\n```"
        )
    else:
        import tempfile

        # Save upload to temp file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(uploaded.getvalue())
            tmp_path = Path(tmp.name)

        with st.spinner("Running hybrid quantum inference..."):
            x_tensor = preprocess_single_image(tmp_path).to(CFG.DEVICE)
            probs    = model.predict_proba(x_tensor).squeeze().cpu().numpy()
            pred_idx = int(np.argmax(probs))
            pred_cls = CFG.CLASSES[pred_idx].replace("_", " ")
            confidence = float(probs[pred_idx]) * 100

        # Result display
        if pred_cls == "Healthy":
            st.success(f"✅ **{pred_cls}** — Confidence: {confidence:.1f}%")
        else:
            st.error(f"⚠️ **{pred_cls}** — Confidence: {confidence:.1f}%")

        # Probability bar chart
        st.markdown("**Class probabilities:**")
        for i, cls in enumerate(CFG.CLASSES):
            st.progress(
                float(probs[i]),
                text=f"{cls.replace('_', ' ')} — {probs[i]*100:.1f}%"
            )

# ── Quantum circuit diagram ───────────────────────────────────────────────────
if show_circuit:
    st.divider()
    st.subheader("⚛️ VQC Circuit Diagram")
    st.markdown(
        f"The circuit encodes {CFG.N_QUBITS} CNN-extracted features as qubit rotation angles, "
        f"then applies {CFG.N_LAYERS} variational layers with CNOT entanglement."
    )
    st.code(get_circuit_diagram(), language="text")

# ── Benchmark comparison ──────────────────────────────────────────────────────
if show_benchmark:
    st.divider()
    st.subheader("📊 Hybrid VQC vs CNN vs SVM Benchmark")
    report_path = CFG.OUTPUTS / "benchmark_report.txt"
    if report_path.exists():
        st.text(report_path.read_text())
    else:
        st.info("Run `python run.py` to generate the benchmark report.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small>QuantumCrop 🌾 — QC² Hackathon 2026 · SRM University AP · Team QBit Farmers</small></center>",
    unsafe_allow_html=True,
)
