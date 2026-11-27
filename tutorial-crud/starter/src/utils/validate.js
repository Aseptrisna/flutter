const { InvalidInputError } = require('../errors');

const MAKS_INT = 2147483647; // batas kolom Int di PostgreSQL
const POLA_TANGGAL = /^\d{4}-\d{2}-\d{2}$/;

function gagal(pesan) {
  throw new InvalidInputError(pesan);
}

// Satu pemeriksa untuk tiap tipe kolom. Mengembalikan nilai yang siap disimpan.
const pemeriksa = {
  teks(nama, nilai, aturan) {
    if (typeof nilai !== 'string' || nilai.trim() === '') gagal(`${nama} harus berupa teks`);
    if (aturan.max && nilai.trim().length > aturan.max) gagal(`${nama} maksimal ${aturan.max} karakter`);
    return nilai.trim();
  },
  bulat(nama, nilai, aturan) {
    const min = aturan.min ?? 0;
    if (!Number.isInteger(nilai) || nilai < min || nilai > MAKS_INT) {
      gagal(`${nama} harus bilangan bulat minimal ${min}`);
    }
    return nilai;
  },
  angka(nama, nilai, aturan) {
    if (typeof nilai !== 'number' || nilai < aturan.min || nilai > aturan.max) {
      gagal(`${nama} harus angka antara ${aturan.min} dan ${aturan.max}`);
    }
    return nilai;
  },
  boolean(nama, nilai) {
    if (typeof nilai !== 'boolean') gagal(`${nama} harus true atau false`);
    return nilai;
  },
  tanggal(nama, nilai) {
    const pesan = `${nama} harus tanggal berformat YYYY-MM-DD`;
    if (typeof nilai !== 'string' || !POLA_TANGGAL.test(nilai)) gagal(pesan);
    const tanggal = new Date(`${nilai}T00:00:00Z`);
    // tanggal mustahil seperti 2026-02-30 bergeser atau tidak valid
    if (Number.isNaN(tanggal.getTime()) || tanggal.toISOString().slice(0, 10) !== nilai) gagal(pesan);
    return tanggal;
  },
  pilihan(nama, nilai, aturan) {
    if (!aturan.opsi.includes(nilai)) gagal(`${nama} harus salah satu dari: ${aturan.opsi.join(', ')}`);
    return nilai;
  },
};

// validate memeriksa body sesuai aturan, lalu mengembalikan HANYA kolom yang
// terdaftar. Kolom lain yang dikirim klien (misalnya user_id) otomatis dibuang.
function validate(body, aturan) {
  const hasil = {};
  for (const [nama, a] of Object.entries(aturan)) {
    const nilai = body ? body[nama] : undefined;
    if (nilai === undefined || nilai === null || nilai === '') {
      if (a.wajib) gagal(`${nama} wajib diisi`);
      hasil[nama] = a.tipe === 'boolean' ? false : null;
    } else {
      hasil[nama] = pemeriksa[a.tipe](nama, nilai, a);
    }
  }
  return hasil;
}

// parseId mengubah :id dari URL menjadi angka yang aman.
function parseId(value) {
  const id = Number(value);
  if (!Number.isInteger(id) || id < 1 || id > MAKS_INT) gagal('id tidak valid');
  return id;
}

module.exports = { validate, parseId };
