const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const passport = require('passport');
const session = require('express-session');
const cors = require('cors');
const connectDB = require('./config/db');

// Load config
dotenv.config();

// Passport config
require('./config/passport')(passport);

const app = express();

// Connect to DB
connectDB();

// Body parser
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: false, limit: '50mb' }));

// CORS
app.use(cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:5173',
    credentials: true
}));

// Sessions
app.use(
    session({
        secret: process.env.SESSION_SECRET || 'secret',
        resave: false,
        saveUninitialized: false,
        cookie: {
            secure: false, // Set to true in production with HTTPS
            maxAge: 24 * 60 * 60 * 1000 // 24 hours
        }
    })
);

// Passport middleware
app.use(passport.initialize());
app.use(passport.session());

// Routes
app.use('/auth', require('./routes/auth'));
app.use('/api/history', require('./routes/history'));

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`🚀 AgriLens Full-Stack Backend running in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`);
});
