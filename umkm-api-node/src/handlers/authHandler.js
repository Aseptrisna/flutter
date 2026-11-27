const authService = require('../services/authService');
const { ok } = require('../utils/response');
const { AppError, InvalidInputError, NotFoundError } = require('../errors');

async function register(req, res, next) {
  try {
    const { nama, email, password } = req.body;
    const user = await authService.register(nama, email, password);
    ok(res, 201, user);
  } catch (err) {
    next(err);
  }
}

async function login(req, res, next) {
  try {
    const { email, password } = req.body;
    const result = await authService.login(email, password);
    ok(res, 200, result);
  } catch (err) {
    // "email tidak ditemukan" (NotFoundError) dan "password salah"
    // (InvalidInputError) sengaja dibalas SAMA, 401 -- supaya tidak membocorkan
    // ke penyerang apakah suatu email terdaftar atau tidak.
    if (err instanceof NotFoundError || err instanceof InvalidInputError) {
      return next(new AppError('email atau password salah', 'UNAUTHORIZED', 401));
    }
    next(err); // error lain (mis. database mati) tetap 500 dan tercetak di terminal
  }
}

async function profile(req, res, next) {
  try {
    const user = await authService.profile(req.userId);
    ok(res, 200, user);
  } catch (err) {
    next(err);
  }
}

async function updateProfile(req, res, next) {
  try {
    const { nama, email } = req.body;
    await authService.updateProfile(req.userId, nama, email);
    ok(res, 200, { message: 'profil berhasil diperbarui' });
  } catch (err) {
    next(err);
  }
}

async function updatePassword(req, res, next) {
  try {
    const { password_lama, password_baru } = req.body;
    await authService.updatePassword(req.userId, password_lama, password_baru);
    ok(res, 200, { message: 'password berhasil diperbarui' });
  } catch (err) {
    next(err);
  }
}

module.exports = { register, login, profile, updateProfile, updatePassword };
