const GoogleStrategy = require('passport-google-oauth20').Strategy;
const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcryptjs');
const mongoose = require('mongoose');
const User = require('../models/User');

module.exports = function (passport) {
    // ─── GOOGLE STRATEGY ───
    passport.use(
        new GoogleStrategy(
            {
                clientID: process.env.GOOGLE_CLIENT_ID,
                clientSecret: process.env.GOOGLE_CLIENT_SECRET,
                callbackURL: 'http://localhost:5000/auth/google/callback',
            },
            async (accessToken, refreshToken, profile, done) => {
                // Fail fast if DB is not connected
                if (mongoose.connection.readyState !== 1) {
                    return done(new Error('Database connection is not established. Please verify your Atlas IP whitelist.'));
                }

                const newUser = {
                    googleId: profile.id,
                    name: profile.displayName,
                    email: profile.emails[0].value,
                    profilePic: profile.photos[0].value,
                };

                try {
                    let user = await User.findOne({ googleId: profile.id });

                    if (user) {
                        return done(null, user);
                    } else {
                        user = await User.create(newUser);
                        return done(null, user);
                    }
                } catch (err) {
                    console.error(err);
                    return done(err);
                }
            }
        )
    );

    // ─── LOCAL STRATEGY ───
    passport.use(
        new LocalStrategy({ usernameField: 'email' }, async (email, password, done) => {
            try {
                const user = await User.findOne({ email: email });
                if (!user) {
                    return done(null, false, { message: 'That email is not registered' });
                }

                // If user exists but is a Google user without a password
                if (!user.password) {
                    return done(null, false, { message: 'Please sign in with Google' });
                }

                // Match password
                const isMatch = await bcrypt.compare(password, user.password);
                if (isMatch) {
                    return done(null, user);
                } else {
                    return done(null, false, { message: 'Password incorrect' });
                }
            } catch (err) {
                return done(err);
            }
        })
    );

    passport.serializeUser((user, done) => {
        done(null, user.id);
    });

    passport.deserializeUser(async (id, done) => {
        try {
            const user = await User.findById(id);
            done(null, user);
        } catch (err) {
            done(err, null);
        }
    });
};
