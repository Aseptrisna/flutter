const multer = require('multer');
const path = require('path');
const fs = require('fs');
const config = require('../config');

const ALLOWED_EXT = new Set(['.jpg', '.jpeg', '.png']);

// INVALID_FILE_TYPE dipakai sebagai penanda error ekstensi tidak didukung,
// dibedakan dari error multer lain (mis. LIMIT_FILE_SIZE) di errorHandler.
class InvalidFileTypeError extends Error {
  constructor() {
    super('tipe berkas tidak didukung, hanya jpg/jpeg/png');
    this.code = 'INVALID_FILE_TYPE';
  }
}

function storageFor(subDir) {
  return multer.diskStorage({
    destination: (req, file, cb) => {
      const dir = path.join(config.uploadDir, subDir);
      fs.mkdirSync(dir, { recursive: true });
      cb(null, dir);
    },
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      const unique = `${Date.now()}${Math.round(Math.random() * 1e9)}`;
      cb(null, `${unique}${ext}`);
    },
  });
}

function fileFilter(req, file, cb) {
  const ext = path.extname(file.originalname).toLowerCase();
  if (!ALLOWED_EXT.has(ext)) {
    return cb(new InvalidFileTypeError());
  }
  cb(null, true);
}

// uploadSingle mengembalikan middleware multer untuk SATU field file bernama
// fieldName, disimpan ke <uploadDir>/<subDir>/. Dipakai sebagai middleware
// biasa di route, errornya ditangkap oleh errorHandler terpusat.
function uploadSingle(subDir, fieldName) {
  return multer({
    storage: storageFor(subDir),
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB, sama seperti versi Go
    fileFilter,
  }).single(fieldName);
}

// relativePath mengembalikan path RELATIF (contoh: "umkm/169...jpg") dari
// req.file hasil multer, atau string kosong kalau pengguna tidak mengunggah
// foto sama sekali (foto bersifat opsional).
function relativePath(subDir, file) {
  if (!file) return '';
  return `${subDir}/${file.filename}`;
}

// deleteFile menghapus berkas lama di <uploadDir>/<relPath>, dipanggil setelah
// update/delete berhasil di database agar tidak ada berkas foto menumpuk.
function deleteFile(uploadDir, relPath) {
  if (!relPath) return;
  fs.unlink(path.join(uploadDir, relPath), () => {
    // sengaja diabaikan: kalau berkasnya sudah tidak ada pun tidak masalah
  });
}

module.exports = { uploadSingle, relativePath, deleteFile, InvalidFileTypeError };
