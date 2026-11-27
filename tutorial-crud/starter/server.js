const app = require('./src/app');
const config = require('./src/config');
const prisma = require('./src/db');

async function main() {
  // Tes koneksi database lebih dulu, gagal cepat kalau DATABASE_URL salah
  // daripada membiarkan server menyala tapi semua endpoint error 500.
  try {
    await prisma.$queryRaw`SELECT 1`;
    console.log('berhasil terhubung ke PostgreSQL');
  } catch (err) {
    console.error('gagal konek ke database:', err.message);
    process.exit(1);
  }

  const server = app.listen(config.port, () => {
    console.log(`server berjalan di port ${config.port}`);
    console.log(`swagger: http://localhost:${config.port}/swagger/`);
  });

  // graceful shutdown
  const shutdown = () => {
    console.log('server dimatikan dengan aman');
    server.close(async () => {
      await prisma.$disconnect();
      process.exit(0);
    });
  };
  process.on('SIGINT', shutdown);
  process.on('SIGTERM', shutdown);
}

main();
