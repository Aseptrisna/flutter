const umkmRepository = require('../repositories/umkmRepository');
const { normalizePagination } = require('../utils/pagination');
const { InvalidInputError, ConflictError, NotFoundError, ForbiddenError } = require('../errors');

// list mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
// Mengembalikan list, total data, serta page/limit yang benar-benar dipakai
// (setelah dinormalisasi) agar handler bisa menuliskan meta pagination akurat.
async function list(q, rawPage, rawLimit) {
  const { page, limit } = normalizePagination(rawPage, rawLimit);
  const offset = (page - 1) * limit;

  const data = await umkmRepository.findAll(q, limit, offset);
  const total = await umkmRepository.count(q);
  return { data, total, page, limit };
}

async function detail(id) {
  const umkm = await umkmRepository.findById(id);
  if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
  return umkm;
}

async function myUmkm(userId) {
  const umkm = await umkmRepository.findByUserId(userId);
  if (!umkm) throw new NotFoundError('Anda belum memiliki UMKM');
  return umkm;
}

async function createOwn(userId, nama, deskripsi, alamat, foto) {
  if (!nama) throw new InvalidInputError('nama UMKM wajib diisi');

  const existing = await umkmRepository.findByUserId(userId);
  if (existing) throw new ConflictError('Anda sudah memiliki UMKM'); // 1 user hanya boleh punya 1 UMKM

  return umkmRepository.create({ user_id: userId, nama, deskripsi, alamat, foto });
}

// updateOwn mengembalikan UMKM hasil update beserta path foto lama (bisa kosong).
// Handler bertanggung jawab menghapus berkas foto lama dari disk setelah update berhasil.
async function updateOwn(userId, umkmId, nama, deskripsi, alamat, fotoBaru) {
  if (!nama) throw new InvalidInputError('nama UMKM wajib diisi');

  const umkm = await umkmRepository.findById(umkmId);
  if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
  if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik UMKM ini');

  let fotoLama = umkm.foto;
  umkm.nama = nama;
  umkm.deskripsi = deskripsi;
  umkm.alamat = alamat;
  if (fotoBaru) {
    umkm.foto = fotoBaru;
  } else {
    fotoLama = ''; // foto tidak diganti, tidak ada yang perlu dihapus
  }

  await umkmRepository.update(umkm);
  return { umkm, fotoLama };
}

async function deleteOwn(userId, umkmId) {
  const umkm = await umkmRepository.findById(umkmId);
  if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
  if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik UMKM ini');

  await umkmRepository.remove(umkmId);
  return umkm;
}

module.exports = { list, detail, myUmkm, createOwn, updateOwn, deleteOwn };
