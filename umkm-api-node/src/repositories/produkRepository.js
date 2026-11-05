const pool = require('../db');

// mapRow mengubah kolom "harga" (tipe NUMERIC di Postgres) dari string --
// begitulah node-postgres selalu membalasnya, supaya tidak diam-diam
// kehilangan presisi kalau dipaksa jadi float -- balik ke Number biasa,
// setara float64 Harga di struct domain.Produk versi Go.
function mapRow(row) {
  if (!row) return row;
  return { ...row, harga: Number(row.harga) };
}

async function create(produk) {
  const { rows } = await pool.query(
    `INSERT INTO produk (umkm_id, nama, harga, deskripsi, foto)
     VALUES ($1, $2, $3, $4, $5) RETURNING id`,
    [produk.umkm_id, produk.nama, produk.harga, produk.deskripsi, produk.foto]
  );
  return { ...produk, id: rows[0].id };
}

async function findById(id) {
  const { rows } = await pool.query(
    'SELECT id, umkm_id, nama, harga, deskripsi, foto FROM produk WHERE id = $1',
    [id]
  );
  return mapRow(rows[0]) || null;
}

async function findByUmkmId(umkmId, limit, offset) {
  const { rows } = await pool.query(
    `SELECT id, umkm_id, nama, harga, deskripsi, foto FROM produk
     WHERE umkm_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3`,
    [umkmId, limit, offset]
  );
  return rows.map(mapRow);
}

async function countByUmkmId(umkmId) {
  const { rows } = await pool.query('SELECT COUNT(*) FROM produk WHERE umkm_id = $1', [umkmId]);
  return Number(rows[0].count);
}

async function update(produk) {
  await pool.query(
    'UPDATE produk SET nama = $1, harga = $2, deskripsi = $3, foto = $4 WHERE id = $5',
    [produk.nama, produk.harga, produk.deskripsi, produk.foto, produk.id]
  );
}

async function remove(id) {
  await pool.query('DELETE FROM produk WHERE id = $1', [id]);
}

module.exports = { create, findById, findByUmkmId, countByUmkmId, update, remove };
