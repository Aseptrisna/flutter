const prisma = require('../db');

const produkSelect = { id: true, umkm_id: true, nama: true, harga: true, deskripsi: true, foto: true };

// mapRow mengubah kolom "harga" (tipe Decimal di Prisma) menjadi Number biasa.
// Prisma membalas NUMERIC/Decimal sebagai objek Decimal (di JSON jadi STRING
// "15000") supaya tidak kehilangan presisi -- kita konversi balik ke Number,
// setara float64 Harga di struct domain.Produk versi Go.
function mapRow(row) {
  if (!row) return row;
  return { ...row, harga: Number(row.harga) };
}

async function create(produk) {
  const row = await prisma.produk.create({
    data: {
      umkm_id: produk.umkm_id,
      nama: produk.nama,
      harga: produk.harga,
      deskripsi: produk.deskripsi,
      foto: produk.foto,
    },
    select: produkSelect,
  });
  return mapRow(row);
}

async function findById(id) {
  return mapRow(await prisma.produk.findUnique({ where: { id }, select: produkSelect }));
}

async function findByUmkmId(umkmId, limit, offset) {
  const rows = await prisma.produk.findMany({
    where: { umkm_id: umkmId },
    orderBy: { id: 'desc' },
    take: limit,
    skip: offset,
    select: produkSelect,
  });
  return rows.map(mapRow);
}

async function countByUmkmId(umkmId) {
  return prisma.produk.count({ where: { umkm_id: umkmId } });
}

async function update(produk) {
  await prisma.produk.update({
    where: { id: produk.id },
    data: { nama: produk.nama, harga: produk.harga, deskripsi: produk.deskripsi, foto: produk.foto },
  });
}

async function remove(id) {
  await prisma.produk.delete({ where: { id } });
}

module.exports = { create, findById, findByUmkmId, countByUmkmId, update, remove };
