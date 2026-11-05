const umkmService = require('../services/umkmService');
const { ok, paginated } = require('../utils/response');
const { relativePath, deleteFile } = require('../utils/upload');
const { InvalidInputError } = require('../errors');
const config = require('../config');

function parseId(req) {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) throw new InvalidInputError('id tidak valid');
  return id;
}

async function list(req, res, next) {
  try {
    const q = req.query.q || '';
    const { data, total, page, limit } = await umkmService.list(q, req.query.page, req.query.limit);
    paginated(res, 200, data, page, limit, total);
  } catch (err) {
    next(err);
  }
}

async function detail(req, res, next) {
  try {
    const umkm = await umkmService.detail(parseId(req));
    ok(res, 200, umkm);
  } catch (err) {
    next(err);
  }
}

async function myUmkm(req, res, next) {
  try {
    const umkm = await umkmService.myUmkm(req.userId);
    ok(res, 200, umkm);
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const foto = relativePath('umkm', req.file);
    const { nama, deskripsi, alamat } = req.body;
    const umkm = await umkmService.createOwn(req.userId, nama, deskripsi, alamat, foto);
    ok(res, 201, umkm);
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const id = parseId(req);
    const fotoBaru = relativePath('umkm', req.file);
    const { nama, deskripsi, alamat } = req.body;
    const { umkm, fotoLama } = await umkmService.updateOwn(req.userId, id, nama, deskripsi, alamat, fotoBaru);
    deleteFile(config.uploadDir, fotoLama);
    ok(res, 200, umkm);
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const id = parseId(req);
    const umkm = await umkmService.deleteOwn(req.userId, id);
    deleteFile(config.uploadDir, umkm.foto);
    ok(res, 200, { message: 'UMKM berhasil dihapus' });
  } catch (err) {
    next(err);
  }
}

module.exports = { list, detail, myUmkm, create, update, remove };
