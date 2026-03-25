import sys
import os
from pathlib import Path
import tempfile
import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Make src/ importable from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.config import CFG
from data.preprocess import preprocess_single_image
from models.vqc import HybridQuantumClassifier

app = FastAPI(title="QuantumCrop Hybrid API", version="2.1.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify ["http://localhost:8080", "http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
model = None

# Overriding classes for the Top-10 high-accuracy model
INFERENCE_CLASSES = [
    "apple_apple_scab", "apple_black_rot", "apple_cedar_apple_rust", "apple_healthy",
    "grape_black_rot", "grape_esca_black_measles", "grape_healthy", "grape_leaf_blight_isariopsis_leaf_spot",
    "potato_early_blight", "potato_healthy", "potato_late_blight",
    "tomato_bacterial_spot", "tomato_early_blight", "tomato_healthy", "tomato_late_blight",
    "tomato_septoria_leaf_spot", "tomato_spider_mites_two_spotted_spider_mite", "tomato_target_spot", "tomato_tomato_yellowleaf_curl_virus",
    "corn_maize_common_rust", "corn_maize_healthy", "corn_maize_northern_leaf_blight"
]

@app.on_event("startup")
async def load_model():
    global model
    model_path = CFG.MODELS_DIR / "hybrid_vqc_best.pt"
    if not model_path.exists():
        print(f"ERROR: Model not found at {model_path}")
        return

    # Force 10 classes for the high-accuracy checkpoint
    from models.vqc import HybridQuantumClassifier
    CFG.CLASSES = INFERENCE_CLASSES 
    CFG.NUM_CLASSES = len(INFERENCE_CLASSES)
    
    model = HybridQuantumClassifier()
    model.load_state_dict(torch.load(model_path, map_location=CFG.DEVICE))
    model.eval()
    model.to(CFG.DEVICE)
    print(f"INFO: Hybrid Model (92.1% Accuracy) loaded on {CFG.DEVICE} with {len(INFERENCE_CLASSES)} classes")

TREATMENTS = {
    "tomato_tomato_yellowleaf_curl_virus": {
        "explanation": "Identified upward curling and yellow margins on leaves. High probability of TYLCV infection.",
        "treatment": ["Control whiteflies with yellow sticky traps.", "Use insecticidal soaps.", "Remove and destroy infected plants immediately."]
    },
    "tomato_bacterial_spot": {
        "explanation": "Detected small, water-soaked spots turning black/brown with yellow halos.",
        "treatment": ["Use copper-based bactericides.", "Avoid overhead irrigation.", "Remove infected foliage promptly."]
    },
    "potato_early_blight": {
        "explanation": "Identified bullseye-shaped brown spots on older leaves (Alternaria solani).",
        "treatment": ["Apply fungicides (Chlorothalonil/Mancozeb).", "Improve soil drainage.", "Rotate crops annually."]
    },
    "tomato_late_blight": {
        "explanation": "Detected dark green, water-soaked spots with white fungal growth underneath (Phytophthora infestans).",
        "treatment": ["Remove infected plants and soil.", "Apply fungicides like Metalaxyl.", "Ensure foliage remains dry."]
    },
    "apple_apple_scab": {
        "explanation": "Identified olive-green to black fungal spots on leaves (Venturia inaequalis).",
        "treatment": ["Apply protectant fungicides (Captan).", "Remove and burn fallen leaves.", "Prune for better air circulation."]
    },
    "grape_black_rot": {
        "explanation": "Detected small reddish-brown circular spots on leaves (Guignardia bidwellii).",
        "treatment": ["Prune during dormancy.", "Apply Myclobutanil fungicides.", "Remove 'mummies' (shriveled grapes) from vines."]
    },
    "apple_cedar_apple_rust": {
        "explanation": "Identified bright orange-yellow spots on the upper leaf surface.",
        "treatment": ["Remove nearby cedar trees.", "Use rust-specific fungicides.", "Plant resistant apple varieties."]
    },
    "tomato_spider_mites_two_spotted_spider_mite": {
        "explanation": "Detected fine stippling (yellow dots) and webbing on leaves.",
        "treatment": ["Use miticides or Neem oil.", "Introduce predatory mites (Phytoseiulus).", "Keep plants well-hydrated."]
    },
    "tomato_target_spot": {
        "explanation": "Identified large, circular spots with concentric rings (Corynespora cassiicola).",
        "treatment": ["Improve air circulation.", "Use protectant fungicides.", "Avoid overhead watering."]
    },
    "grape_esca_black_measles": {
        "explanation": "Detected 'tiger-stripe' discoloration (yellow/red between veins).",
        "treatment": ["Protect pruning wounds with sealants.", "Remove dead wood during winter.", "Improve vine vigor with fertilization."]
    },
    "apple_healthy": {
        "explanation": "No significant lesions, discoloration, or pests detected on apple foliage.",
        "treatment": ["Continue standard fertilization.", "Maintain regular watering.", "Monitor weekly for changes."]
    },
    "apple_black_rot": {
        "explanation": "Identified small brown spots on leaves expanding into 'frogeye' spots (Botryosphaeria obtusa).",
        "treatment": ["Prune dead wood and cankers.", "Apply lime-sulfur or fungicides.", "Remove mummified fruit from trees."]
    },
    "grape_healthy": {
        "explanation": "Grape foliage appears healthy with optimal photosynthetic efficiency.",
        "treatment": ["Regular pruning for air flow.", "Check for early signs of mites.", "Ensure balanced soil nutrients."]
    },
    "grape_leaf_blight_isariopsis_leaf_spot": {
        "explanation": "Identified small reddish-brown spots with irregular margins (Pseudocercospora vitis).",
        "treatment": ["Improve vine nutrition.", "Apply foliar fungicides.", "Thin canopy to reduce humidity."]
    },
    "potato_healthy": {
        "explanation": "Potato foliage is vibrant, green, and free of early/late blight symptoms.",
        "treatment": ["Maintain soil hilling.", "Monitor for Colorado Potato Beetles.", "Ensure regular deep watering."]
    },
    "tomato_healthy": {
        "explanation": "Tomato plant is in excellent health with no visible signs of virus or fungal stress.",
        "treatment": ["Ensure proper staking.", "Maintain consistent soil moisture.", "Monitor for hornworms."]
    },
    "tomato_early_blight": {
        "explanation": "Identified circular brown spots with concentric 'target' rings on lower leaves.",
        "treatment": ["Apply protective fungicides.", "Mulch to prevent soil splash.", "Remove lower infected foliage."]
    },
    "tomato_septoria_leaf_spot": {
        "explanation": "Detected small, circular spots with dark borders and gray centers (tousled appearance).",
        "treatment": ["Avoid overhead irrigation.", "Destroy crop residues.", "Rotate crops every 2-3 years."]
    },
    "corn_maize_healthy": {
        "explanation": "Corn foliage is vigorous and free of common rust or northern leaf blight lesions.",
        "treatment": ["Monitor for stalk borer.", "Maintain high nitrogen supply.", "Irrigate during silking."]
    },
    "corn_maize_common_rust": {
        "explanation": "Identified cinnamon-brown pustules on both upper and lower leaf surfaces.",
        "treatment": ["Plant rust-resistant hybrids.", "Use foliar fungicides if detected early.", "Incorporate old residue into soil."]
    },
    "corn_maize_northern_leaf_blight": {
        "explanation": "Detected large, cigar-shaped, grayish-green lesions (Exserohilum turcicum).",
        "treatment": ["Rotate with non-corn crops for 2+ years.", "Apply fungicides at first sign of lesions.", "Use resistant maize varieties."]
    },
    "Healthy": {
        "explanation": "Generic Healthy Fallback: Photosynthetic area appears intact.",
        "treatment": ["Monitor weekly.", "Standard watering."]
    }
}

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None, "device": str(CFG.DEVICE)}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Save upload to temp file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        # Run inference
        x_tensor = preprocess_single_image(tmp_path).to(CFG.DEVICE)
        probs = model.predict_proba(x_tensor).squeeze().cpu().detach().numpy()
        pred_idx = int(np.argmax(probs))
        pred_cls_raw = CFG.CLASSES[pred_idx]
        confidence = float(probs[pred_idx])

        # Cleanup
        os.unlink(tmp_path)

        # Metadata
        pred_cls_pretty = pred_cls_raw.replace("_", " ").title()
        metadata = TREATMENTS.get(pred_cls_raw, TREATMENTS["Healthy"])
        
        # Determine success vs danger
        result_type = "success" if "Healthy" in pred_cls_pretty else "danger"

        return {
            "name": pred_cls_pretty,
            "confidence": round(confidence * 100, 1),
            "type": result_type,
            "explanation": metadata["explanation"],
            "treatment": metadata["treatment"]
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
