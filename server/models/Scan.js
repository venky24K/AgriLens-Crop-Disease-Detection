const mongoose = require('mongoose');

const ScanSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    diseaseName: {
        type: String,
        required: true
    },
    confidence: {
        type: Number,
        required: true
    },
    explanation: {
        type: String
    },
    treatments: [{
        type: String
    }],
    imageSrc: {
        type: String, // Base64 or URL
        required: true
    },
    date: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Scan', ScanSchema);
