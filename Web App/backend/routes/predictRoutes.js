const express = require('express');
const router = express.Router();
const upload = require('../middleware/uploadMiddleware');
const { protect } = require('../middleware/authMiddleware');
const Prediction = require('../models/Prediction');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// @desc    Upload image and predict disease (Real Hybrid Model)
// @route   POST /api/predict
// @access  Private
router.post('/', protect, upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'Please upload an image' });
  }

  try {
    // 1. Prepare form data for FastAPI
    const form = new FormData();
    form.append('file', fs.createReadStream(req.file.path));

    // 2. Call FastAPI Hybrid Model (Port 8000)
    const response = await axios.post('http://localhost:8000/predict', form, {
      headers: {
        ...form.getHeaders(),
      },
    });

    const { name, confidence, type, treatment, explanation } = response.data;

    // 3. Save to MongoDB
    const prediction = await Prediction.create({
      userId: req.user._id,
      imageUrl: `/uploads/${req.file.filename}`,
      status: type === 'success' ? 'Healthy' : 'Diseased',
      disease: name,
      confidence: confidence / 100, // Normalize to 0-1
      treatment: treatment,
      explanation: explanation,
    });

    res.status(201).json(prediction);
  } catch (error) {
    console.error('Prediction Error:', error.message);
    res.status(500).json({ message: 'Error processing hybrid diagnosis' });
  }
});

module.exports = router;
