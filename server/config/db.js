const mongoose = require('mongoose');

const connectDB = async () => {
    try {
        const conn = await mongoose.connect(process.env.MONGODB_URI, {
            bufferCommands: false, // Don't hang if DB is not connected
            serverSelectionTimeoutMS: 5000 // Fast fail
        });
        console.log(`🚀 MongoDB Connected: ${conn.connection.host}`);
    } catch (err) {
        console.error(`❌ MongoDB Connection Error: ${err.message}`);
        // Continuing without DB connection to allow UI access...
    }
};

module.exports = connectDB;
