const express = require('express');
const router = express.Router();
const Scan = require('../models/Scan');

// Middleware to check auth
const ensureAuth = (req, res, next) => {
    if (req.isAuthenticated()) {
        return next();
    }
    res.status(401).json({ msg: 'Unauthorized' });
};

// @desc    Get user scan history
// @route   GET /api/history
router.get('/', ensureAuth, async (req, res) => {
    try {
        const history = await Scan.find({ user: req.user.id }).sort({ date: -1 });
        res.json(history);
    } catch (err) {
        console.error(err);
        res.status(500).send('Server Error');
    }
});

// @desc    Add scan to history
// @route   POST /api/history
router.post('/', ensureAuth, async (req, res) => {
    try {
        const { diseaseName, confidence, explanation, treatments, imageSrc } = req.body;
        const newScan = new Scan({
            user: req.user.id,
            diseaseName,
            confidence,
            explanation,
            treatments,
            imageSrc
        });
        const savedScan = await newScan.save();
        res.json(savedScan);
    } catch (err) {
        console.error(err);
        res.status(500).send('Server Error');
    }
});

module.exports = router;
