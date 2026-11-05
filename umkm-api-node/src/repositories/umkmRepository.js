const pool = require('../db');

async function create(umkm) {
  const { rows } = await pool.query(
    `INSERT INTO umkm (user_id, nama, deskripsi, alamat, foto)
     VALUES ($1, $2, $3, $4, $5) RETURNING id`,
    [umkm.user_id, umkm.nama, umkm.deskripsi, umkm.alamat, umkm.foto]
  );
  return { ...umkm, id: rows[0].id };
}

// findAll mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
// q kosong berarti tidak difilter sama sekali.
async function findAll(q, limit, offset) {
  const { rows } = await pool.query(
    `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm
     WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')
     ORDER BY id DESC LIMIT $2 OFFSET $3`,
    [q, limit, offset]
  );
  return rows;
}

async function count(q) {
  const { rows } = await pool.query(
    `SELECT COUNT(*) FROM umkm WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')`,
    [q]
  );
  // node-postgres selalu membalas COUNT(*) sebagai STRING (karena tipe asli
  // Postgres-nya bigint, lebih besar dari batas aman Number JS) -- wajib
  // di-Number()-kan manual di sini, beda dengan Go yang otomatis men-scan
  // ke tipe int.
  return Number(rows[0].count);
}

async function findById(id) {
  const { rows } = await pool.query(
    'SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE id = $1',
    [id]
  );
  return rows[0] || null;
}

async function findByUserId(userId) {
  const { rows } = await pool.query(
    'SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE user_id = $1',
    [userId]
  );
  return rows[0] || null;
}

async function update(umkm) {
  await pool.query(
    'UPDATE umkm SET nama = $1, deskripsi = $2, alamat = $3, foto = $4 WHERE id = $5',
    [umkm.nama, umkm.deskripsi, umkm.alamat, umkm.foto, umkm.id]
  );
}

async function remove(id) {
  await pool.query('DELETE FROM umkm WHERE id = $1', [id]);
}

module.exports = { create, findAll, count, findById, findByUserId, update, remove };
