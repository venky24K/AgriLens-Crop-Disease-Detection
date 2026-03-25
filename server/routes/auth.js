const express = require('express');
const passport = require('passport');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
const router = express.Router();

// @desc    Auth with Google
// @route   GET /auth/google
router.get('/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// @desc    Google auth callback
// @route   GET /auth/google/callback
router.get(
    '/google/callback',
    passport.authenticate('google', { failureRedirect: '/' }),
    (req, res) => {
        res.redirect(process.env.FRONTEND_URL || 'http://localhost:5173');
    }
);

// @desc    Local Sign Up
// @route   POST /auth/signup
router.post('/signup', async (req, res) => {
    const { name, email, password } = req.body;
    try {
        let user = await User.findOne({ email });
        if (user) {
            return res.status(400).json({ msg: 'User already exists' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        user = await User.create({
            name,
            email,
            password: hashedPassword,
            profilePic: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`
        });

        req.login(user, (err) => {
            if (err) return res.status(500).json({ msg: 'Login failed after signup' });
            res.status(201).json(user);
        });
    } catch (err) {
        console.error(err);
        res.status(500).send('Server error');
    }
});

// @desc    Local Sign In
// @route   POST /auth/signin
router.post('/signin', (req, res, next) => {
    passport.authenticate('local', (err, user, info) => {
        if (err) return next(err);
        if (!user) return res.status(400).json({ msg: info.message });
        req.logIn(user, (err) => {
            if (err) return next(err);
            return res.json(user);
        });
    })(req, res, next);
});

// @desc    Logout user
// @route   /auth/logout
router.get('/logout', (req, res, next) => {
    req.logout((err) => {
        if (err) return next(err);
        res.redirect(process.env.FRONTEND_URL || 'http://localhost:5173');
    });
});

// @desc    Get current user
// @route   GET /auth/user
router.get('/user', (req, res) => {
    if (req.isAuthenticated()) {
        res.json(req.user);
    } else {
        res.status(401).json({ msg: 'Not authenticated' });
    }
});

module.exports = router;
