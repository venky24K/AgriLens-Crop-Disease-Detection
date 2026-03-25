const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db');

// Load env vars
dotenv.config();

// Connect to database
connectDB();

const app = express();

// Body parser
app.use(express.json());

// Enable CORS
app.use(cors());

// Route files
const authRoutes = require('./routes/authRoutes');
const predictRoutes = require('./routes/predictRoutes');
const historyRoutes = require('./routes/historyRoutes');
const userRoutes = require('./routes/userRoutes');
const path = require('path');

// Mount routers
app.use('/api/auth', authRoutes);
app.use('/api/predict', predictRoutes);
app.use('/api/history', historyRoutes);
app.use('/api/user', userRoutes);

// Static folder for uploads
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

app.get('/', (req, res) => {
  res.send('AgriLens AI API is running...');
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running in ${process.env.NODE_ENV} mode on port ${PORT}`);
});
