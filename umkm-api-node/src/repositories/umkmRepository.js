const prisma = require('../db');

// select eksplisit: created_at sengaja tidak ikut dikirim ke klien,
// sama seperti daftar kolom pada SELECT versi SQL mentah sebelumnya.
const umkmSelect = { id: true, user_id: true, nama: true, deskripsi: true, alamat: true, foto: true };

// where dipakai bersama oleh findAll & count supaya filter pencarian selalu
// konsisten. q kosong -> undefined -> Prisma mengabaikan filter sama sekali.
function buildWhere(q) {
  return q ? { nama: { contains: q, mode: 'insensitive' } } : undefined;
}

async function create(umkm) {
  return prisma.umkm.create({
    data: {
      user_id: umkm.user_id,
      nama: umkm.nama,
      deskripsi: umkm.deskripsi,
      alamat: umkm.alamat,
      foto: umkm.foto,
    },
    select: umkmSelect,
  });
}

// findAll mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
async function findAll(q, limit, offset) {
  return prisma.umkm.findMany({
    where: buildWhere(q),
    orderBy: { id: 'desc' },
    take: limit,
    skip: offset,
    select: umkmSelect,
  });
}

// prisma.count() langsung mengembalikan Number -- tidak perlu lagi
// Number(rows[0].count) seperti saat memakai node-postgres.
async function count(q) {
  return prisma.umkm.count({ where: buildWhere(q) });
}

async function findById(id) {
  return prisma.umkm.findUnique({ where: { id }, select: umkmSelect });
}

async function findByUserId(userId) {
  return prisma.umkm.findUnique({ where: { user_id: userId }, select: umkmSelect });
}

async function update(umkm) {
  await prisma.umkm.update({
    where: { id: umkm.id },
    data: { nama: umkm.nama, deskripsi: umkm.deskripsi, alamat: umkm.alamat, foto: umkm.foto },
  });
}

async function remove(id) {
  await prisma.umkm.delete({ where: { id } });
}

module.exports = { create, findAll, count, findById, findByUserId, update, remove };
