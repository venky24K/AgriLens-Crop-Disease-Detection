const mongoose = require('mongoose');

const predictionSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    imageUrl: {
      type: String,
      required: [true, 'Please add an image URL'],
    },
    status: {
      type: String,
      enum: ['Healthy', 'Diseased'],
      required: true,
    },
    disease: {
      type: String,
      required: true,
    },
    confidence: {
      type: Number,
      required: true,
    },
    treatment: {
      type: [String],
      default: [],
    },
    explanation: {
      type: String,
      default: '',
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('Prediction', predictionSchema);
