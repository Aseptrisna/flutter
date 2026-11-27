const express = require('express');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');

const swaggerSpec = require('./docs/swagger');
const { requireAuth } = require('./middleware/auth');
const { loginLimiter } = require('./middleware/rateLimit');
const { errorHandler } = require('./middleware/errorHandler');

const authHandler = require('./handlers/authHandler');

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

// --- route project-mu ---

// health check
app.get('/healthz', (req, res) => res.sendStatus(200));

// dokumentasi Swagger. persistAuthorization: token tetap tersimpan setelah reload
// /swagger/index.html (alamat di versi Go) dialihkan, karena file bawaan paket
// di alamat itu menampilkan contoh "Petstore", bukan API kita.
app.get('/swagger/index.html', (req, res) => res.redirect('/swagger/'));
app.use(
  '/swagger',
  swaggerUi.serve,
  swaggerUi.setup(swaggerSpec, { swaggerOptions: { persistAuthorization: true } }),
);

// errorHandler WAJIB didaftarkan PALING TERAKHIR -- Express mengenali
// middleware 4-parameter (err, req, res, next) sebagai error handler hanya
// kalau ia didaftarkan setelah semua route lain.
app.use(errorHandler);

module.exports = app;
