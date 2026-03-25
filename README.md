# 🌿 AgriLens: Quantum-Enhanced Crop Diagnostic Platform ⚛️

### High-Precision 22-Class Hybrid Quantum-Classical Diagnosis
**SRM University AP · Team QBit Farmers · Lakhani (2025) Methodology**

---

## 🚀 Overview
AgriLens is a state-of-the-art agricultural diagnostic platform that leverages **Hybrid Quantum-Classical Machine Learning** to detect disease in crops with unprecedented precision. By combining traditional Deep Learning (ResNet-18) with **Variational Quantum Classifiers (VQC)**, AgriLens identifies 22 distinct crop diseases across Apple, Grape, Potato, Tomato, and Corn.

---

## ✨ Key Features
- **⚛️ Hybrid Quantum Engine**: Uses Angle Encoding and Variational Circuits to refine classical features via quantum interference.
- **📊 22-Class Diagnosis**: Comprehensive support for 5 major crop families.
- **🛠️ Professional Dashboard**: Glassmorphism-based React UI with real-time scan history.
- **☁️ Cloud-Native Persistence**: Fully integrated with **MongoDB Atlas** for secure, global data storage.
- **💊 Treatment Plans**: Automated cure recommendations and explanations for every detected disease.

---

## 🏗️ Architecture
AgriLens follows a modern microservices architecture:
1. **Frontend**: React (Vite) + Tailwind CSS + Framer Motion.
2. **Gateway**: Node.js / Express API with JWT Authentication.
3. **Inference**: FastAPI service wrapping the PennyLane-PyTorch Hybrid Model.
4. **Database**: MongoDB Atlas (Cloud-hosted).

---

## 🧬 Supported Crops & Diseases (22 Classes)
AgriLens covers the following major variety of conditions:

-   **🍎 Apple**: Scab, Black Rot, Cedar Rust, Healthy
-   **🌽 Corn**: Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy
-   **🍇 Grape**: Black Rot, Esca (Black Measles), Leaf Blight, Healthy
-   **🥔 Potato**: Early Blight, Late Blight, Healthy
-   **🍅 Tomato**: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Two-Spotted Spider Mite, Target Spot, Yellow Leaf Curl, Mosaic Virus, Healthy

---

## 🛠️ Tech Stack
-   **Quantum ML**: PennyLane + Lightning Qubit
-   **Deep Learning**: PyTorch (CUDA Accelerated)
-   **Backend**: Node.js, Express, FastAPI
-   **Frontend**: React 18, Glassmorphism UI
-   **Database**: MongoDB Atlas

---

## 🚦 Quick Start

### 1. Model Engine (FastAPI)
```bash
python app/api.py
```

### 2. Backend API (Node.js)
```bash
cd "Web App/backend"
npm start
```

### 3. Frontend Dashboard (React)
```bash
cd "Web App/frontend"
npm run dev
```

*AgriLens: Empowering farmers with the precision of quantum computing.* 🌾⚛️✨
