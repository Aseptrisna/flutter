const produkService = require('../services/produkService');
const { ok, paginated } = require('../utils/response');
const { relativePath, deleteFile } = require('../utils/upload');
const { InvalidInputError } = require('../errors');
const config = require('../config');

function parseId(value) {
  const id = Number(value);
  if (!Number.isInteger(id)) throw new InvalidInputError('id tidak valid');
  return id;
}

async function detail(req, res, next) {
  try {
    const produk = await produkService.detail(parseId(req.params.id));
    ok(res, 200, produk);
  } catch (err) {
    next(err);
  }
}

async function listByUmkm(req, res, next) {
  try {
    const umkmId = parseId(req.params.id);
    const { data, total, page, limit } = await produkService.listByUmkm(umkmId, req.query.page, req.query.limit);
    paginated(res, 200, data, page, limit, total);
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const umkmId = parseId(req.params.id);
    const harga = Number.parseFloat(req.body.harga);
    if (Number.isNaN(harga)) throw new InvalidInputError('harga produk wajib berupa angka');

    const foto = relativePath('produk', req.file);
    const { nama, deskripsi } = req.body;
    const produk = await produkService.createForOwnUmkm(req.userId, umkmId, nama, harga, deskripsi, foto);
    ok(res, 201, produk);
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const id = parseId(req.params.id);
    const harga = Number.parseFloat(req.body.harga);
    if (Number.isNaN(harga)) throw new InvalidInputError('harga produk wajib berupa angka');

    const fotoBaru = relativePath('produk', req.file);
    const { nama, deskripsi } = req.body;
    const { produk, fotoLama } = await produkService.updateOwn(req.userId, id, nama, harga, deskripsi, fotoBaru);
    deleteFile(config.uploadDir, fotoLama);
    ok(res, 200, produk);
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const id = parseId(req.params.id);
    const produk = await produkService.deleteOwn(req.userId, id);
    deleteFile(config.uploadDir, produk.foto);
    ok(res, 200, { message: 'produk berhasil dihapus' });
  } catch (err) {
    next(err);
  }
}

module.exports = { detail, listByUmkm, create, update, remove };
