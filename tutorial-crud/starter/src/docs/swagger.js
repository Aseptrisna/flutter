// Dokumentasi OpenAPI untuk modul user (auth & profil).
// Isinya hanya objek JavaScript biasa. Swagger UI membacanya lalu membuat
// halaman uji coba di http://localhost:8080/swagger/

// Bentuk body JSON; semua properti yang ditulis dianggap wajib.
function jsonBody(properties) {
  return {
    required: true,
    content: {
      'application/json': {
        schema: { type: 'object', required: Object.keys(properties), properties },
      },
    },
  };
}

// Contoh respons sukses.
function sukses(description, data) {
  return { description, content: { 'application/json': { example: { data } } } };
}

// Contoh respons gagal.
function gagal(message, code) {
  return { description: message, content: { 'application/json': { example: { error: { message, code } } } } };
}

// Potongan yang dipakai berulang.
const nama = { type: 'string', maxLength: 100, example: 'Budi Tester' };
const email = { type: 'string', format: 'email', maxLength: 150, example: 'budi@test.com' };
const password = { type: 'string', format: 'password', minLength: 6, example: 'rahasia123' };
const user = { id: 1, nama: 'Budi Tester', email: 'budi@test.com' };
const butuhToken = [{ bearerAuth: [] }];
const tokenSalah = gagal('token tidak valid', 'UNAUTHORIZED');

module.exports = {
  openapi: '3.0.3',
  info: {
    title: 'API Project',
    version: '1.0.0',
    description:
      'Modul user. Urutan uji: register, login, salin token, klik Authorize, ' +
      'tempel token (tanpa kata Bearer), lalu coba endpoint profil.',
  },
  servers: [{ url: '/api' }],
  tags: [
    { name: 'Auth', description: 'Daftar dan masuk' },
    { name: 'Profil', description: 'Butuh token' },
  ],
  components: {
    securitySchemes: {
      bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
    },
  },
  paths: {
    '/auth/register': {
      post: {
        tags: ['Auth'],
        summary: 'Daftar akun baru',
        requestBody: jsonBody({ nama, email, password }),
        responses: {
          201: sukses('Akun dibuat', user),
          400: gagal('nama, email, dan password (min 6 karakter) wajib diisi', 'BAD_REQUEST'),
          409: gagal('email sudah terdaftar', 'CONFLICT'),
        },
      },
    },
    '/auth/login': {
      post: {
        tags: ['Auth'],
        summary: 'Masuk dan dapatkan token (maks. 5 kali per menit)',
        requestBody: jsonBody({ email, password }),
        responses: {
          200: sukses('Berhasil masuk', { token: 'eyJhbGciOiJIUzI1NiIs...', user }),
          401: gagal('email atau password salah', 'UNAUTHORIZED'),
          429: gagal('terlalu banyak percobaan, coba lagi nanti', 'TOO_MANY_REQUESTS'),
        },
      },
    },
    '/profile': {
      get: {
        tags: ['Profil'],
        summary: 'Lihat profil sendiri',
        security: butuhToken,
        responses: { 200: sukses('Data profil', user), 401: tokenSalah },
      },
      put: {
        tags: ['Profil'],
        summary: 'Ubah nama dan email',
        security: butuhToken,
        requestBody: jsonBody({ nama, email }),
        responses: {
          200: sukses('Profil diubah', { message: 'profil berhasil diperbarui' }),
          400: gagal('nama dan email wajib diisi', 'BAD_REQUEST'),
          401: tokenSalah,
          409: gagal('email sudah terdaftar', 'CONFLICT'),
        },
      },
    },
    '/profile/password': {
      put: {
        tags: ['Profil'],
        summary: 'Ubah password',
        security: butuhToken,
        requestBody: jsonBody({
          password_lama: password,
          password_baru: { ...password, example: 'rahasiabaru456' },
        }),
        responses: {
          200: sukses('Password diubah', { message: 'password berhasil diperbarui' }),
          400: gagal('password lama salah atau password baru terlalu pendek', 'BAD_REQUEST'),
          401: tokenSalah,
        },
      },
    },
  },
};
