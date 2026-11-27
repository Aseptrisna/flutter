const { InvalidFileTypeError } = require('../utils/upload');

// errorHandler adalah satu-satunya tempat error diterjemahkan jadi response
// JSON. Service/handler tinggal `throw` instance dari src/errors.js (atau
// panggil next(err)), tidak perlu switch-case berulang di tiap endpoint
// seperti pola errors.Is di versi Go -- karena di sini status HTTP & code
// sudah menempel di objek error-nya sendiri (lihat AppError).
function errorHandler(err, req, res, next) {
  // Error dari multer (upload foto) ditangani lebih dulu, bentuknya beda
  // dari AppError karena datang dari library pihak ketiga.
  if (err instanceof InvalidFileTypeError) {
    return res.status(400).json({ error: { message: err.message, code: 'BAD_REQUEST' } });
  }
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(400).json({
      error: { message: 'form tidak valid atau file terlalu besar', code: 'BAD_REQUEST' },
    });
  }

  // Body JSON yang rusak ditolak express.json() sebelum sampai ke handler.
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({ error: { message: 'body tidak valid', code: 'BAD_REQUEST' } });
  }

  if (err.status) {
    return res.status(err.status).json({ error: { message: err.message, code: err.code } });
  }

  console.error(err);
  res.status(500).json({ error: { message: 'kesalahan server', code: 'INTERNAL' } });
}

module.exports = { errorHandler };
