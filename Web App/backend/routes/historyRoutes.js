const express = require('express');
const router = express.Router();
const { protect } = require('../middleware/authMiddleware');
const Prediction = require('../models/Prediction');

// @desc    Get all predictions for the logged-in user
// @route   GET /api/history
// @access  Private
router.get('/', protect, async (req, res) => {
  try {
    const history = await Prediction.find({ userId: req.user._id }).sort({ createdAt: -1 });
    res.json(history);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;
