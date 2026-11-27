[← Daftar tutorial project](index.md)

Tutorial · Dokumentasi API

# Setup Swagger dari Awal (Modul User)

Dari project yang baru punya modul user sampai semua endpoint-nya bisa diuji dari browser.

## 01 Apa Itu Swagger

**Swagger UI** adalah halaman web yang menampilkan daftar endpoint API dan menyediakan tombol untuk mencobanya langsung dari browser, tanpa Postman. Isinya dibaca dari deskripsi berformat **OpenAPI** yang kita tulis.

| Istilah | Arti |
|----|----|
| OpenAPI | Aturan penulisan deskripsi API (endpoint, isian, balasan). |
| Swagger UI | Tampilan web yang membaca deskripsi itu. |
| `swagger-ui-express` | Paket npm yang menyajikan Swagger UI dari server Express. |
| `src/docs/swagger.js` | File deskripsi yang akan kita buat. |

Dokumentasi tidak otomatis

Swagger hanya menampilkan apa yang ditulis di file deskripsi. Ia tidak membuat atau memvalidasi endpoint. Kalau API berubah, deskripsinya ikut diubah. Mau dibuat dari route dengan satu perintah? Lihat [Generate Swagger Otomatis](swagger-generate.md).

## 02 Syarat Awal

Project Express-mu sudah punya modul user dan bisa dijalankan dengan `npm run dev`. Pastikan lima route ini ada di `src/app.js`:

| Route                       | Fungsi                    |
|-----------------------------|---------------------------|
| `POST /api/auth/register`   | Daftar                    |
| `POST /api/auth/login`      | Masuk, menghasilkan token |
| `GET /api/profile`          | Lihat profil              |
| `PUT /api/profile`          | Ubah profil               |
| `PUT /api/profile/password` | Ubah password             |

Belum punya? Buat dulu lewat [Fondasi Modul User](00-fondasi.md). Fondasi dan folder `starter` **sudah berisi Swagger**, jadi halaman ini dipakai untuk memahami cara membuatnya.

Sudah ada src/docs/swagger.js?

Berarti Swagger sudah terpasang. Jangan ditimpa kalau di dalamnya sudah ada dokumentasi lain; simpan salinannya dulu.

## 03 Langkah 1: Install Paket

Hentikan server (`Ctrl+C`), lalu di folder project:

terminal

    npm install --save-exact swagger-ui-express@5.0.1
    mkdir -p src/docs

## 04 Langkah 2: Buat Kerangka

Buat file baru `src/docs/swagger.js`:

src/docs/swagger.js

    // Dokumentasi API dalam format OpenAPI 3.
    // Swagger UI membaca objek ini lalu membuat halamannya.
    module.exports = {
      openapi: '3.0.3',
      info: {
        title: 'API Project',
        version: '1.0.0',
        description: 'Dokumentasi modul user',
      },
      servers: [{ url: '/api' }],
      tags: [],
      components: { securitySchemes: {} },
      paths: {},
    };

| Bagian | Fungsi |
|----|----|
| `openapi` | Versi format. |
| `info` | Judul, versi, dan keterangan di bagian atas halaman. |
| `servers` | Awalan semua path. Karena sudah `/api`, path ditulis tanpa `/api`. |
| `tags` | Nama kelompok endpoint. |
| `components` | Definisi yang dipakai ulang, misalnya jenis token. |
| `paths` | Daftar endpoint. Masih kosong. |

## 05 Langkah 3: Daftarkan di app.js

Buka `src/app.js`. Tempel kode berikut **di atas** baris `app.use(errorHandler);`:

src/app.js — tempel di atas app.use(errorHandler)

    const swaggerUi = require('swagger-ui-express');
    const swaggerSpec = require('./docs/swagger');

    // /swagger/index.html dialihkan: file bawaan paket di alamat itu berisi demo "Petstore"
    app.get('/swagger/index.html', (req, res) => res.redirect('/swagger/'));
    app.use(
      '/swagger',
      swaggerUi.serve,
      swaggerUi.setup(swaggerSpec, { swaggerOptions: { persistAuthorization: true } }),
    );

| Baris | Fungsi |
|----|----|
| `swaggerUi.serve` | Mengirim file tampilan (HTML, CSS, JavaScript). |
| `swaggerUi.setup(swaggerSpec, ...)` | Mengisi tampilan dengan deskripsi kita. |
| `persistAuthorization: true` | Token tetap tersimpan setelah halaman dimuat ulang. |

Opsional, supaya alamatnya muncul di terminal, tambahkan baris ini di `server.js` di bawah pesan `server berjalan di port ...`:

server.js — di dalam app.listen

        console.log(`swagger: http://localhost:${config.port}/swagger/`);

terminal — jalankan server

    npm run dev

Checkpoint

Buka `http://localhost:8080/swagger/`. Harus tampil judul **API Project** dengan keterangan *No operations defined in spec!* Itu benar, karena `paths` masih kosong.

## 06 Langkah 4: Dokumentasikan Register

src/docs/swagger.js — tambahkan di paling bawah

    // ---------- register ----------
    module.exports.tags.push({ name: 'Auth', description: 'Daftar dan masuk' });

    module.exports.paths['/auth/register'] = {
      post: {
        tags: ['Auth'],
        summary: 'Daftar akun baru',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['nama', 'email', 'password'],
                properties: {
                  nama: { type: 'string', example: 'Budi Tester' },
                  email: { type: 'string', format: 'email', example: 'budi@test.com' },
                  password: { type: 'string', format: 'password', example: 'rahasia123' },
                },
              },
            },
          },
        },
        responses: {
          201: { description: 'Akun dibuat' },
          400: { description: 'Isian tidak lengkap atau password kurang dari 6 karakter' },
          409: { description: 'Email sudah terdaftar' },
        },
      },
    };

| Bagian | Arti |
|----|----|
| `paths['/auth/register']` | Alamat endpoint. |
| `post` | Method HTTP. |
| `tags` | Masuk ke kelompok mana. |
| `summary` | Judul singkat. |
| `requestBody` | Bentuk data yang dikirim. |
| `required` | Field yang wajib. |
| `example` | Isian contoh yang otomatis muncul saat *Try it out*. |
| `responses` | Kemungkinan status balasan. |

Simpan file. `npm run dev` menyalakan ulang server otomatis; muat ulang halaman `/swagger/` di browser.

Coba

Klik **POST /auth/register** → *Try it out* → *Execute*. Harus `201`. Tekan lagi: harus `409`.

## 07 Langkah 5: Fungsi Bantu & Login

Menulis `requestBody` sepanjang itu untuk setiap endpoint melelahkan. Buat fungsi bantu:

src/docs/swagger.js — tambahkan di paling bawah

    // ---------- fungsi bantu ----------
    // Body JSON; semua properti yang ditulis dianggap wajib.
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

    const email = { type: 'string', format: 'email', example: 'budi@test.com' };
    const password = { type: 'string', format: 'password', example: 'rahasia123' };

Sekarang login jauh lebih pendek:

src/docs/swagger.js — tambahkan di paling bawah

    // ---------- login ----------
    module.exports.paths['/auth/login'] = {
      post: {
        tags: ['Auth'],
        summary: 'Masuk dan dapatkan token (maks. 5 kali per menit)',
        requestBody: jsonBody({ email, password }),
        responses: {
          200: { description: 'Berhasil, respons berisi token' },
          401: { description: 'Email atau password salah' },
          429: { description: 'Terlalu banyak percobaan' },
        },
      },
    };

Simpan file. `npm run dev` menyalakan ulang server otomatis; muat ulang halaman `/swagger/` di browser.

Coba

**POST /auth/login** → *Execute* → `200`. Salin nilai `token` dari respons, tanpa tanda kutip.

## 08 Langkah 6: Token & Lihat Profil

src/docs/swagger.js — tambahkan di paling bawah

    // ---------- token (tombol Authorize) ----------
    module.exports.components.securitySchemes.bearerAuth = {
      type: 'http',
      scheme: 'bearer',
      bearerFormat: 'JWT',
    };
    const butuhToken = [{ bearerAuth: [] }];

    // ---------- lihat profil ----------
    module.exports.tags.push({ name: 'Profil', description: 'Butuh token' });

    module.exports.paths['/profile'] = {
      get: {
        tags: ['Profil'],
        summary: 'Lihat profil sendiri',
        security: butuhToken,
        responses: {
          200: { description: 'Data profil' },
          401: { description: 'Token tidak ada atau tidak valid' },
        },
      },
    };

| Bagian | Fungsi |
|----|----|
| `securitySchemes.bearerAuth` | Memberi tahu Swagger bahwa API memakai header `Authorization: Bearer ...`. Tombol *Authorize* sudah ada sejak kerangka; baris ini membuat jendelanya menyediakan kolom token. |
| `security: butuhToken` | Endpoint ini dikirim bersama token (ikon gembok). |

Simpan file. `npm run dev` menyalakan ulang server otomatis; muat ulang halaman `/swagger/` di browser.

1.  **GET /profile** → *Execute* → `401` (belum membawa token).
2.  Klik **Authorize**, tempel token **tanpa kata Bearer**, klik *Authorize*, lalu *Close*.
3.  *Execute* lagi → `200`.

## 09 Langkah 7: Ubah Profil & Password

src/docs/swagger.js — tambahkan di paling bawah

    // ---------- ubah profil ----------
    // ditambahkan sebagai method kedua pada path /profile yang sudah ada
    module.exports.paths['/profile'].put = {
      tags: ['Profil'],
      summary: 'Ubah nama dan email',
      security: butuhToken,
      requestBody: jsonBody({ nama: { type: 'string', example: 'Budi Baru' }, email }),
      responses: {
        200: { description: 'Profil diubah' },
        400: { description: 'Nama dan email wajib diisi' },
        401: { description: 'Token tidak valid' },
        409: { description: 'Email sudah terdaftar' },
      },
    };

    // ---------- ubah password ----------
    module.exports.paths['/profile/password'] = {
      put: {
        tags: ['Profil'],
        summary: 'Ubah password',
        security: butuhToken,
        requestBody: jsonBody({
          password_lama: password,
          password_baru: { ...password, example: 'rahasiabaru456' },
        }),
        responses: {
          200: { description: 'Password diubah' },
          400: { description: 'Password lama salah atau password baru terlalu pendek' },
          401: { description: 'Token tidak valid' },
        },
      },
    };

Perhatikan .put

Satu path hanya boleh didefinisikan sekali. Method kedua ditambahkan dengan `paths['/profile'].put = ...`. Kalau ditulis `paths['/profile'] = { put: ... }`, dokumentasi GET akan tertimpa dan hilang.

Simpan file. `npm run dev` menyalakan ulang server otomatis; muat ulang halaman `/swagger/` di browser.

Coba

**PUT /profile** → `200`. **PUT /profile/password** → `200`. Setelah itu login memakai password baru `rahasiabaru456`.

## 10 Menguji Jalur Gagal

| Endpoint | Yang dicoba | Harus dibalas |
|----|----|----|
| register | Email yang sama dua kali | `409` |
| register | Password 3 karakter | `400` |
| login | Password salah | `401` |
| login | Lebih dari 5 kali dalam 1 menit | `429` |
| GET /profile | *Logout* di jendela Authorize, lalu *Execute* | `401` |
| PUT /profile/password | Password lama salah | `400` |

Kalau balasannya berbeda (misalnya `500`), yang perlu diperiksa kode API-nya, bukan Swagger. Bandingkan dengan [Pertemuan 9a Bagian 11](../../pertemuan-09a.html#s11).

## 11 Menambah Endpoint Lain

Polanya selalu sama: tambahkan path, tulis method, lalu muat ulang. Contoh untuk endpoint milikmu sendiri (ganti `barang`). Dokumentasi hanya berfungsi kalau route-nya memang sudah ada di `app.js`.

Daftarkan dulu kelompoknya dengan `module.exports.tags.push({ name: 'Barang' });`

### Parameter di path dan query

contoh — path dan query parameter

    // path parameter: GET /barang/{id}   (di Express ditulis /barang/:id)
    // query parameter: GET /barang?q=kopi&page=1
    module.exports.paths['/barang/{id}'] = {
      get: {
        tags: ['Barang'],
        summary: 'Detail barang',
        security: butuhToken,
        parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }],
        responses: { 200: { description: 'Detail' }, 404: { description: 'Tidak ditemukan' } },
      },
    };

    module.exports.paths['/barang'] = {
      get: {
        tags: ['Barang'],
        summary: 'Daftar barang',
        security: butuhToken,
        parameters: [
          { name: 'q', in: 'query', schema: { type: 'string' } },
          { name: 'page', in: 'query', schema: { type: 'integer' } },
        ],
        responses: { 200: { description: 'Daftar' } },
      },
    };

### Upload file

contoh — upload file

    // upload file: tipe isinya multipart/form-data, file ditandai format binary
    module.exports.paths['/barang/{id}/foto'] = {
      put: {
        tags: ['Barang'],
        summary: 'Unggah foto barang',
        security: butuhToken,
        parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }],
        requestBody: {
          required: true,
          content: {
            'multipart/form-data': {
              schema: {
                type: 'object',
                properties: { foto: { type: 'string', format: 'binary' } },
              },
            },
          },
        },
        responses: { 200: { description: 'Foto tersimpan' } },
      },
    };

Untuk CRUD lengkap, tutorial [project masing-masing](index.md) memakai fungsi `crudDocs` yang membuat dokumentasi lima endpoint sekaligus.

## 12 Troubleshooting

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module 'swagger-ui-express'` | Paket belum terpasang. | `npm install` |
| `Cannot find module './docs/swagger'` | Nama atau lokasi file salah. | Harus `src/docs/swagger.js`. |
| `/swagger/` membalas `Cannot GET` | Kode di `app.js` belum ditempel atau server belum di-restart. | Ulangi langkah 3. |
| `jsonBody is not defined` atau `butuhToken is not defined` | Urutan potongan terbalik. | Fungsi bantu dan `butuhToken` harus di atas pemakaiannya. |
| Endpoint tidak muncul | File belum disimpan, atau `paths` tertimpa. | Simpan, restart, muat ulang. |
| Tampil *Failed to fetch* atau `404` saat Execute | Path di dokumentasi berbeda dari route. | Samakan; ingat `servers` sudah berisi `/api`. |
| Sudah Authorize tetapi `401` | Menempel kata `Bearer` atau token kedaluwarsa. | *Logout*, tempel token saja. |

## 13 File Lengkap & Checklist

Isi akhir `src/docs/swagger.js` setelah semua langkah, untuk dibandingkan:

file lengkap — src/docs/swagger.js

    // Dokumentasi API dalam format OpenAPI 3.
    // Swagger UI membaca objek ini lalu membuat halamannya.
    module.exports = {
      openapi: '3.0.3',
      info: {
        title: 'API Project',
        version: '1.0.0',
        description: 'Dokumentasi modul user',
      },
      servers: [{ url: '/api' }],
      tags: [],
      components: { securitySchemes: {} },
      paths: {},
    };

    // ---------- register ----------
    module.exports.tags.push({ name: 'Auth', description: 'Daftar dan masuk' });

    module.exports.paths['/auth/register'] = {
      post: {
        tags: ['Auth'],
        summary: 'Daftar akun baru',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                type: 'object',
                required: ['nama', 'email', 'password'],
                properties: {
                  nama: { type: 'string', example: 'Budi Tester' },
                  email: { type: 'string', format: 'email', example: 'budi@test.com' },
                  password: { type: 'string', format: 'password', example: 'rahasia123' },
                },
              },
            },
          },
        },
        responses: {
          201: { description: 'Akun dibuat' },
          400: { description: 'Isian tidak lengkap atau password kurang dari 6 karakter' },
          409: { description: 'Email sudah terdaftar' },
        },
      },
    };

    // ---------- fungsi bantu ----------
    // Body JSON; semua properti yang ditulis dianggap wajib.
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

    const email = { type: 'string', format: 'email', example: 'budi@test.com' };
    const password = { type: 'string', format: 'password', example: 'rahasia123' };

    // ---------- login ----------
    module.exports.paths['/auth/login'] = {
      post: {
        tags: ['Auth'],
        summary: 'Masuk dan dapatkan token (maks. 5 kali per menit)',
        requestBody: jsonBody({ email, password }),
        responses: {
          200: { description: 'Berhasil, respons berisi token' },
          401: { description: 'Email atau password salah' },
          429: { description: 'Terlalu banyak percobaan' },
        },
      },
    };

    // ---------- token (tombol Authorize) ----------
    module.exports.components.securitySchemes.bearerAuth = {
      type: 'http',
      scheme: 'bearer',
      bearerFormat: 'JWT',
    };
    const butuhToken = [{ bearerAuth: [] }];

    // ---------- lihat profil ----------
    module.exports.tags.push({ name: 'Profil', description: 'Butuh token' });

    module.exports.paths['/profile'] = {
      get: {
        tags: ['Profil'],
        summary: 'Lihat profil sendiri',
        security: butuhToken,
        responses: {
          200: { description: 'Data profil' },
          401: { description: 'Token tidak ada atau tidak valid' },
        },
      },
    };

    // ---------- ubah profil ----------
    // ditambahkan sebagai method kedua pada path /profile yang sudah ada
    module.exports.paths['/profile'].put = {
      tags: ['Profil'],
      summary: 'Ubah nama dan email',
      security: butuhToken,
      requestBody: jsonBody({ nama: { type: 'string', example: 'Budi Baru' }, email }),
      responses: {
        200: { description: 'Profil diubah' },
        400: { description: 'Nama dan email wajib diisi' },
        401: { description: 'Token tidak valid' },
        409: { description: 'Email sudah terdaftar' },
      },
    };

    // ---------- ubah password ----------
    module.exports.paths['/profile/password'] = {
      put: {
        tags: ['Profil'],
        summary: 'Ubah password',
        security: butuhToken,
        requestBody: jsonBody({
          password_lama: password,
          password_baru: { ...password, example: 'rahasiabaru456' },
        }),
        responses: {
          200: { description: 'Password diubah' },
          400: { description: 'Password lama salah atau password baru terlalu pendek' },
          401: { description: 'Token tidak valid' },
        },
      },
    };

- `/swagger/` menampilkan 5 endpoint dalam kelompok Auth dan Profil.
- Register, login, dan ketiga endpoint profil berhasil dicoba.
- Tanpa token, endpoint profil membalas `401`.
- Di server produksi, route `/swagger` dimatikan atau dilindungi.

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
