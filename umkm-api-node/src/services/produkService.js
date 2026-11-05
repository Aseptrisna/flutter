const produkRepository = require('../repositories/produkRepository');
const umkmRepository = require('../repositories/umkmRepository');
const { normalizePagination } = require('../utils/pagination');
const { InvalidInputError, NotFoundError, ForbiddenError } = require('../errors');

async function listByUmkm(umkmId, rawPage, rawLimit) {
  const { page, limit } = normalizePagination(rawPage, rawLimit);
  const offset = (page - 1) * limit;

  const data = await produkRepository.findByUmkmId(umkmId, limit, offset);
  const total = await produkRepository.countByUmkmId(umkmId);
  return { data, total, page, limit };
}

async function detail(id) {
  const produk = await produkRepository.findById(id);
  if (!produk) throw new NotFoundError('produk tidak ditemukan');
  return produk;
}

async function createForOwnUmkm(userId, umkmId, nama, harga, deskripsi, foto) {
  if (!nama || !(harga >= 0)) throw new InvalidInputError('nama dan harga produk wajib valid');

  const umkm = await umkmRepository.findById(umkmId);
  if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
  if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik UMKM ini'); // hanya pemilik UMKM yang boleh menambah produk

  return produkRepository.create({ umkm_id: umkmId, nama, harga, deskripsi, foto });
}

// authorizeOwner memastikan userId adalah pemilik UMKM tempat produk berada --
// dua SELECT berantai: ambil produknya dulu (untuk tahu umkm_id-nya), lalu
// ambil UMKM-nya (untuk tahu user_id pemiliknya), karena tabel produk sengaja
// tidak menyimpan user_id sendiri (lihat skema di Bagian 04 materi utama).
async function authorizeOwner(userId, produkId) {
  const produk = await produkRepository.findById(produkId);
  if (!produk) throw new NotFoundError('produk tidak ditemukan');

  const umkm = await umkmRepository.findById(produk.umkm_id);
  if (!umkm) throw new NotFoundError('produk tidak ditemukan');

  if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik produk ini');
  return produk;
}

async function updateOwn(userId, produkId, nama, harga, deskripsi, fotoBaru) {
  if (!nama || !(harga >= 0)) throw new InvalidInputError('nama dan harga produk wajib valid');

  const produk = await authorizeOwner(userId, produkId);

  let fotoLama = produk.foto;
  produk.nama = nama;
  produk.harga = harga;
  produk.deskripsi = deskripsi;
  if (fotoBaru) {
    produk.foto = fotoBaru;
  } else {
    fotoLama = '';
  }

  await produkRepository.update(produk);
  return { produk, fotoLama };
}

async function deleteOwn(userId, produkId) {
  const produk = await authorizeOwner(userId, produkId);
  await produkRepository.remove(produkId);
  return produk;
}

module.exports = { listByUmkm, detail, createForOwnUmkm, updateOwn, deleteOwn };
