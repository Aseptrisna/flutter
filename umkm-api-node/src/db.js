const { PrismaClient } = require('@prisma/client');

// Satu instance PrismaClient dipakai bersama seluruh aplikasi. PrismaClient
// sudah mengelola connection pool sendiri, jadi JANGAN membuat instance baru
// di tiap repository/request. Koneksi SSL untuk Neon otomatis ikut dari
// "sslmode=require" di DATABASE_URL -- tidak perlu konfigurasi ssl manual.
const prisma = new PrismaClient({
  log: ['warn', 'error'],
});

module.exports = prisma;
