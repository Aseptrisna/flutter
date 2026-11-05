const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require('../config');
const userRepository = require('../repositories/userRepository');
const { InvalidInputError, ConflictError, NotFoundError } = require('../errors');

function toSafeUser(user) {
  return { id: user.id, nama: user.nama, email: user.email };
}

async function register(nama, email, password) {
  if (!nama || !email || !password || password.length < 6) {
    throw new InvalidInputError('nama, email, dan password (min 6 karakter) wajib diisi');
  }

  const existing = await userRepository.findByEmail(email);
  if (existing) throw new ConflictError('email sudah terdaftar');

  const hashed = await bcrypt.hash(password, 10);
  const user = await userRepository.create({ nama, email, password: hashed });
  return toSafeUser(user);
}

async function login(email, password) {
  const user = await userRepository.findByEmail(email);
  if (!user) throw new NotFoundError('email atau password salah');

  const match = await bcrypt.compare(password, user.password);
  if (!match) throw new InvalidInputError('email atau password salah');

  const token = generateToken(user.id);
  return { token, user: toSafeUser(user) };
}

async function profile(userId) {
  const user = await userRepository.findById(userId);
  if (!user) throw new NotFoundError();
  return toSafeUser(user);
}

async function updateProfile(userId, nama, email) {
  if (!nama || !email) throw new InvalidInputError('gagal memperbarui profil');
  await userRepository.updateProfile(userId, nama, email);
}

async function updatePassword(userId, passwordLama, passwordBaru) {
  const user = await userRepository.findById(userId);
  if (!user) throw new NotFoundError();

  const match = await bcrypt.compare(passwordLama, user.password);
  if (!match) throw new InvalidInputError('password lama salah atau password baru terlalu pendek');

  if (!passwordBaru || passwordBaru.length < 6) {
    throw new InvalidInputError('password lama salah atau password baru terlalu pendek');
  }

  const hashed = await bcrypt.hash(passwordBaru, 10);
  await userRepository.updatePassword(userId, hashed);
}

function generateToken(userId) {
  return jwt.sign({ sub: userId }, config.jwtSecret, { algorithm: 'HS256', expiresIn: '24h' });
}

module.exports = { register, login, profile, updateProfile, updatePassword };
