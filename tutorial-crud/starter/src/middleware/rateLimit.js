const rateLimit = require('express-rate-limit');

// Maksimal 5 percobaan login per menit per alamat IP, agar brute-force
// password dibatasi -- setara middleware.RateLimit di versi Go.
const loginLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 5,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: { message: 'terlalu banyak percobaan, coba lagi nanti', code: 'TOO_MANY_REQUESTS' },
    });
  },
});

module.exports = { loginLimiter };
