const authService = require('../services/authService');
const { ok } = require('../utils/response');

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
    // Baik "email tidak ditemukan" (NotFoundError) maupun "password salah"
    // (InvalidInputError) sengaja dibalas SAMA, 401 "email atau password
    // salah" -- supaya tidak membocorkan ke penyerang apakah suatu email
    // terdaftar atau tidak. Ini meniru persis switch-case di AuthHandler.Login Go.
    err.status = 401;
    err.code = 'UNAUTHORIZED';
    err.message = 'email atau password salah';
    next(err);
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
