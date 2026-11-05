const { Pool } = require('pg');
const config = require('./config');

// Neon mewajibkan koneksi SSL. Kita deteksi dari connection string supaya
// kode yang sama tetap bisa dipakai untuk Postgres lokal (tanpa SSL) saat
// development, dan ke Neon (dengan SSL) saat connection string-nya memuat
// "sslmode=require".
const useSsl = (config.databaseUrl || '').includes('sslmode=require');

const pool = new Pool({
  connectionString: config.databaseUrl,
  ssl: useSsl ? { rejectUnauthorized: false } : false,
});

pool.on('error', (err) => {
  console.error('Koneksi database bermasalah:', err.message);
});

module.exports = pool;
