const pool = require('../db');

async function create(user) {
  const { rows } = await pool.query(
    'INSERT INTO users (nama, email, password) VALUES ($1, $2, $3) RETURNING id',
    [user.nama, user.email, user.password]
  );
  return { ...user, id: rows[0].id };
}

async function findByEmail(email) {
  const { rows } = await pool.query(
    'SELECT id, nama, email, password FROM users WHERE email = $1',
    [email]
  );
  return rows[0] || null;
}

async function findById(id) {
  const { rows } = await pool.query(
    'SELECT id, nama, email, password FROM users WHERE id = $1',
    [id]
  );
  return rows[0] || null;
}

async function updateProfile(id, nama, email) {
  await pool.query('UPDATE users SET nama = $1, email = $2 WHERE id = $3', [nama, email, id]);
}

async function updatePassword(id, hashedPassword) {
  await pool.query('UPDATE users SET password = $1 WHERE id = $2', [hashedPassword, id]);
}

module.exports = { create, findByEmail, findById, updateProfile, updatePassword };
