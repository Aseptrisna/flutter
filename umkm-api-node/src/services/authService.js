const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require('../config');
const userRepository = require('../repositories/userRepository');
const { InvalidInputError, ConflictError, NotFoundError } = require('../errors');

function toSafeUser(user) {
  return { id: user.id, nama: user.nama, email: user.email };
}

// Batas panjang mengikuti kolom di schema.prisma (VarChar 100 dan 150).
const MAKS_NAMA = 100;
const MAKS_EMAIL = 150;

// isText: harus berupa teks yang tidak kosong. Body JSON bisa berisi angka,
// null, atau objek, jadi tipenya wajib diperiksa.
function isText(value) {
  return typeof value === 'string' && value.length > 0;
}

function isPassword(value) {
  return typeof value === 'string' && value.length >= 6;
}

function checkLength(nama, email) {
  if (nama.length > MAKS_NAMA || email.length > MAKS_EMAIL) {
    throw new InvalidInputError('nama maksimal 100 karakter dan email maksimal 150 karakter');
  }
}

// P2002 = kode Prisma untuk nilai unik yang kembar. Di tabel users satu-satunya
// kolom unik selain id adalah email.
function toEmailConflict(err) {
  return err.code === 'P2002' ? new ConflictError('email sudah terdaftar') : err;
}

async function register(nama, email, password) {
  if (!isText(nama) || !isText(email) || !isPassword(password)) {
    throw new InvalidInputError('nama, email, dan password (min 6 karakter) wajib diisi');
  }
  checkLength(nama, email);

  const existing = await userRepository.findByEmail(email);
  if (existing) throw new ConflictError('email sudah terdaftar');

  const hashed = await bcrypt.hash(password, 10);
  try {
    const user = await userRepository.create({ nama, email, password: hashed });
    return toSafeUser(user);
  } catch (err) {
    throw toEmailConflict(err); // dua pendaftaran email sama di waktu bersamaan
  }
}

async function login(email, password) {
  if (!isText(email) || !isText(password)) {
    throw new InvalidInputError('email atau password salah');
  }

  const user = await userRepository.findByEmail(email);
  if (!user) throw new NotFoundError('email atau password salah');

  const match = await bcrypt.compare(password, user.password);
  if (!match) throw new InvalidInputError('email atau password salah');

  const token = generateToken(user.id);
  return { token, user: toSafeUser(user) };
}

async function profile(userId) {
  const user = await userRepository.findById(userId);
  if (!user) throw new NotFoundError('pengguna tidak ditemukan');
  return toSafeUser(user);
}

async function updateProfile(userId, nama, email) {
  if (!isText(nama) || !isText(email)) throw new InvalidInputError('nama dan email wajib diisi');
  checkLength(nama, email);
  try {
    await userRepository.updateProfile(userId, nama, email);
  } catch (err) {
    throw toEmailConflict(err); // email sudah dipakai akun lain -> 409
  }
}

async function updatePassword(userId, passwordLama, passwordBaru) {
  const user = await userRepository.findById(userId);
  if (!user) throw new NotFoundError('pengguna tidak ditemukan');

  const pesan = 'password lama salah atau password baru terlalu pendek';
  if (!isText(passwordLama)) throw new InvalidInputError(pesan);

  const match = await bcrypt.compare(passwordLama, user.password);
  if (!match) throw new InvalidInputError(pesan);

  if (!isPassword(passwordBaru)) throw new InvalidInputError(pesan);

  const hashed = await bcrypt.hash(passwordBaru, 10);
  await userRepository.updatePassword(userId, hashed);
}

function generateToken(userId) {
  return jwt.sign({ sub: userId }, config.jwtSecret, { algorithm: 'HS256', expiresIn: '24h' });
}

module.exports = { register, login, profile, updateProfile, updatePassword };
