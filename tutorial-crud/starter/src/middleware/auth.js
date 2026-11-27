const jwt = require('jsonwebtoken');
const config = require('../config');

// requireAuth membaca header Authorization, menerima baik "Bearer <token>"
// maupun token mentah tanpa prefix (supaya mahasiswa yang lupa mengetik
// "Bearer " di Swagger/Postman tidak selalu dibalas 401 yang membingungkan).
// jwt.verify dengan algorithms: ['HS256'] memaksa algoritma HS256 saja, agar
// token dengan header "alg" lain (termasuk "none") selalu ditolak.
function requireAuth(req, res, next) {
  const header = req.headers.authorization || '';
  if (!header) {
    return res.status(401).json({ error: { message: 'token tidak ditemukan', code: 'UNAUTHORIZED' } });
  }

  const token = header.slice(0, 7).toLowerCase() === 'bearer ' ? header.slice(7) : header;

  try {
    const payload = jwt.verify(token, config.jwtSecret, { algorithms: ['HS256'] });
    req.userId = Number(payload.sub);
    next();
  } catch (err) {
    return res.status(401).json({ error: { message: 'token tidak valid', code: 'UNAUTHORIZED' } });
  }
}

module.exports = { requireAuth };
