const express = require('express');
const cors = require('cors');
const path = require('path');

const config = require('./config');
const { requireAuth } = require('./middleware/auth');
const { loginLimiter } = require('./middleware/rateLimit');
const { errorHandler } = require('./middleware/errorHandler');
const { uploadSingle } = require('./utils/upload');

const authHandler = require('./handlers/authHandler');
const umkmHandler = require('./handlers/umkmHandler');
const produkHandler = require('./handlers/produkHandler');

const app = express();

app.use(cors());
app.use(express.json());

// auth
app.post('/api/auth/register', authHandler.register);
app.post('/api/auth/login', loginLimiter, authHandler.login);

// profile (butuh login)
app.get('/api/profile', requireAuth, authHandler.profile);
app.put('/api/profile', requireAuth, authHandler.updateProfile);
app.put('/api/profile/password', requireAuth, authHandler.updatePassword);

// umkm
app.get('/api/umkm', umkmHandler.list);
app.get('/api/umkm/saya', requireAuth, umkmHandler.myUmkm);
app.get('/api/umkm/:id', umkmHandler.detail);
app.post('/api/umkm', requireAuth, uploadSingle('umkm', 'foto'), umkmHandler.create);
app.put('/api/umkm/:id', requireAuth, uploadSingle('umkm', 'foto'), umkmHandler.update);
app.delete('/api/umkm/:id', requireAuth, umkmHandler.remove);

// produk
app.get('/api/umkm/:id/produk', produkHandler.listByUmkm);
app.post('/api/umkm/:id/produk', requireAuth, uploadSingle('produk', 'foto'), produkHandler.create);
app.get('/api/produk/:id', produkHandler.detail);
app.put('/api/produk/:id', requireAuth, uploadSingle('produk', 'foto'), produkHandler.update);
app.delete('/api/produk/:id', requireAuth, produkHandler.remove);

// static file untuk foto yang sudah diupload
app.use('/uploads', express.static(path.resolve(config.uploadDir)));

// health check
app.get('/healthz', (req, res) => res.sendStatus(200));

// errorHandler WAJIB didaftarkan PALING TERAKHIR -- Express mengenali
// middleware 4-parameter (err, req, res, next) sebagai error handler hanya
// kalau ia didaftarkan setelah semua route lain.
app.use(errorHandler);

module.exports = app;
