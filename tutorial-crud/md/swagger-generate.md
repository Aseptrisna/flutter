[← Daftar tutorial project](index.md)

Tutorial · Dokumentasi API

# Generate Swagger Otomatis di Node.js

Satu perintah untuk membuat dokumentasi API dari route Express, memakai swagger-autogen.

## 01 Apa Bedanya

**swagger-autogen** membaca `src/app.js` beserta handler yang dipakainya, lalu menulis file dokumentasi sendiri. Perannya sama dengan `swag init` di versi Go.

|  | [Tulis sendiri](swagger.md) | Generate (halaman ini) |
|----|----|----|
| Daftar endpoint | Diketik satu per satu | Dibaca dari route |
| Isi body | Diketik | Nama field terbaca dari `req.body`; contohnya lewat komentar |
| Setelah API berubah | Ubah file dokumentasi | Jalankan `npm run swagger` |
| File dokumentasi | `src/docs/swagger.js` | `src/docs/swagger-output.json` |

Pilih salah satu

Hasil keduanya sama-sama tampil di `/swagger/`. Yang dipakai ditentukan satu baris `require` di `app.js`.

## 02 Syarat Awal

Project Express-mu sudah punya modul user, bisa dijalankan dengan `npm run dev`, dan `/swagger/` sudah tampil. Itu terpenuhi kalau kamu mengikuti [Fondasi Modul User](00-fondasi.md) atau [Pertemuan 9a](../../pertemuan-09a.html).

Belum ada `swagger-ui-express`? Kerjakan dulu [langkah 1](swagger.md#s3) dan [langkah 3 di tutorial manual](swagger.md#s5).

## 03 Langkah 1: Install

Di folder project:

terminal

    npm install --save-exact --save-dev swagger-autogen@2.23.7
    mkdir -p scripts

## 04 Langkah 2: Buat Script Generator

Buat file baru `scripts/generate-swagger.js`:

scripts/generate-swagger.js

    const swaggerAutogen = require('swagger-autogen')({ openapi: '3.0.3', autoHeaders: false });

    const doc = {
      info: { title: 'API Project', version: '1.0.0', description: 'Dibuat otomatis dari route Express' },
      servers: [{ url: '/' }],
    };

    // argumen: file hasil, file yang berisi route, keterangan tambahan
    swaggerAutogen('./src/docs/swagger-output.json', ['./src/app.js'], doc);

Lalu di `package.json`, tambahkan satu baris di bagian `scripts`:

package.json — di dalam scripts

    "swagger": "node scripts/generate-swagger.js",

## 05 Langkah 3: Generate

terminal

    npm run swagger

Terminal menampilkan `Swagger-autogen: Success` dan muncul file `src/docs/swagger-output.json`. File ini **jangan diedit manual** karena ditimpa setiap kali generate.

## 06 Langkah 4: Pakai Hasilnya

Di bagian atas `src/app.js`, ganti baris `require` Swagger:

src/app.js — ganti satu baris

    // baris lama: const swaggerSpec = require('./docs/swagger');
    const swaggerSpec = require('./docs/swagger-output.json');

Route bantu tidak perlu ikut didokumentasikan. Masih di `app.js`, ganti route `/healthz` dan `/swagger/index.html` menjadi:

src/app.js — health check

    // health check
    app.get('/healthz', (req, res) => {
      // #swagger.ignore = true
      res.sendStatus(200);
    });

src/app.js — pengalihan swagger

    app.get('/swagger/index.html', (req, res) => {
      // #swagger.ignore = true
      res.redirect('/swagger/');
    });

terminal

    npm run swagger
    npm run dev

Checkpoint

Buka `http://localhost:8080/swagger/`. Semua route muncul dalam satu kelompok **default**, dan body register sudah berisi `nama`, `email`, `password` dengan nilai `any`.

## 07 Langkah 5: Token & Contoh Isian

Ganti seluruh isi `scripts/generate-swagger.js`. Tambahannya: jenis token (supaya tombol *Authorize* berfungsi) dan contoh isian.

scripts/generate-swagger.js

    const swaggerAutogen = require('swagger-autogen')({ openapi: '3.0.3', autoHeaders: false });

    const email = 'budi@test.com';
    const password = 'rahasia123';

    const doc = {
      info: { title: 'API Project', version: '1.0.0', description: 'Dibuat otomatis dari route Express' },
      servers: [{ url: '/' }],
      // semua endpoint mengirim token; yang publik dikecualikan lewat komentar
      security: [{ bearerAuth: [] }],
      components: {
        securitySchemes: {
          bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
        },
        // cukup tulis contohnya, tipe datanya disimpulkan otomatis
        schemas: {
          Register: { nama: 'Budi Tester', email, password },
          Login: { email, password },
          Profil: { nama: 'Budi Baru', email },
          Password: { password_lama: password, password_baru: 'rahasiabaru456' },
        },
      },
    };

    // argumen: file hasil, file yang berisi route, keterangan tambahan
    swaggerAutogen('./src/docs/swagger-output.json', ['./src/app.js'], doc);

## 08 Langkah 6: Komentar di Handler

Kelompok, judul, contoh body, dan balasan diatur lewat komentar `#swagger`. Buka `src/handlers/authHandler.js`, tempel tiap komentar **di dalam** fungsinya, tepat setelah baris `async function`. Komentar di luar fungsi diabaikan.

src/handlers/authHandler.js

    async function register(req, res, next) {
      /*
        #swagger.tags = ['Auth']
        #swagger.summary = 'Daftar akun baru'
        #swagger.security = []
        #swagger.requestBody = {
          required: true,
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Register' } } }
        }
        #swagger.responses[201] = { description: 'Akun dibuat' }
        #swagger.responses[400] = { description: 'Isian tidak valid' }
        #swagger.responses[409] = { description: 'Email sudah terdaftar' }
      */
      // ...isi fungsi yang lama tetap

src/handlers/authHandler.js

    async function login(req, res, next) {
      /*
        #swagger.tags = ['Auth']
        #swagger.summary = 'Masuk dan dapatkan token'
        #swagger.security = []
        #swagger.requestBody = {
          required: true,
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Login' } } }
        }
        #swagger.responses[200] = { description: 'Berhasil, respons berisi token' }
        #swagger.responses[401] = { description: 'Email atau password salah' }
        #swagger.responses[429] = { description: 'Terlalu banyak percobaan' }
      */
      // ...isi fungsi yang lama tetap

src/handlers/authHandler.js

    async function profile(req, res, next) {
      /*
        #swagger.tags = ['Profil']
        #swagger.summary = 'Lihat profil sendiri'
        #swagger.responses[200] = { description: 'Data profil' }
      */
      // ...isi fungsi yang lama tetap

src/handlers/authHandler.js

    async function updateProfile(req, res, next) {
      /*
        #swagger.tags = ['Profil']
        #swagger.summary = 'Ubah nama dan email'
        #swagger.requestBody = {
          required: true,
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Profil' } } }
        }
        #swagger.responses[200] = { description: 'Profil diubah' }
        #swagger.responses[400] = { description: 'Isian tidak valid' }
        #swagger.responses[409] = { description: 'Email sudah terdaftar' }
      */
      // ...isi fungsi yang lama tetap

src/handlers/authHandler.js

    async function updatePassword(req, res, next) {
      /*
        #swagger.tags = ['Profil']
        #swagger.summary = 'Ubah password'
        #swagger.requestBody = {
          required: true,
          content: { 'application/json': { schema: { $ref: '#/components/schemas/Password' } } }
        }
        #swagger.responses[200] = { description: 'Password diubah' }
        #swagger.responses[400] = { description: 'Password lama salah atau password baru terlalu pendek' }
      */
      // ...isi fungsi yang lama tetap

| Komentar                  | Fungsi                                          |
|---------------------------|-------------------------------------------------|
| `#swagger.tags`           | Nama kelompok.                                  |
| `#swagger.summary`        | Judul singkat.                                  |
| `#swagger.security = []`  | Endpoint publik, tanpa token.                   |
| `#swagger.requestBody`    | Contoh isian, diambil dari `schemas` di script. |
| `#swagger.responses[409]` | Keterangan satu status balasan.                 |

terminal

    npm run swagger

Muat ulang halaman `/swagger/`.

Coba

Register → `201`. Login → `200`, salin `token`. Klik **Authorize**, tempel token tanpa kata `Bearer`. **GET /api/profile** → `200`.

## 09 CRUD Project-mu

Setelah mengikuti [tutorial project](index.md), jalankan `npm run swagger`: lima endpoint CRUD langsung terbaca, termasuk `{id}`, `q`, `page`, dan `limit`.

Yang **tidak** terbaca adalah isi body, karena handler meneruskan `req.body` utuh ke service. Tambahkan komentar pada fungsi `create` (dan `update`) di handler-mu. Ganti `Barang` dan contohnya dengan *contoh body* dari halaman project-mu.

src/handlers/…Handler.js — contoh

    async function create(req, res, next) {
      /*
        #swagger.tags = ['Barang']
        #swagger.summary = 'Tambah barang'
        #swagger.requestBody = {
          required: true,
          content: { 'application/json': { example: { nama: 'Kopi', stok: 10 } } }
        }
        #swagger.responses[201] = { description: 'Data dibuat' }
        #swagger.responses[400] = { description: 'Isian tidak valid' }
      */
      // ...isi fungsi yang lama tetap

Untuk `update`, ganti judulnya dan pakai status `200`. Beri `#swagger.tags` yang sama pada kelima fungsi supaya mengelompok.

Tutorial project mengganti app.js

Bagian Route di halaman project meminta mengganti seluruh `src/app.js`, sehingga baris `require` kembali ke `./docs/swagger`. Ulangi langkah 4. Bagian Swagger di halaman project (cara manual) boleh dilewati.

### Upload file

Kalau route-mu menerima file (misalnya di proyek UMKM), tulis komentar ini di dalam handler-nya:

contoh — upload file

    /*
      #swagger.requestBody = {
        required: true,
        content: {
          'multipart/form-data': {
            schema: { type: 'object', properties: { foto: { type: 'string', format: 'binary' } } }
          }
        }
      }
    */

## 10 Kebiasaan Sehari-hari

- Setiap menambah atau mengubah route dan komentar, jalankan `npm run swagger`. Kalau `npm run dev` sedang menyala, server restart sendiri; tinggal muat ulang halaman.
- Ikut sertakan `swagger-output.json` dalam commit. Server membutuhkannya, sedangkan `swagger-autogen` hanya terpasang di komputer development.

Opsional, supaya generate otomatis setiap kali memulai `npm run dev`:

package.json — di dalam scripts

    "predev": "npm run swagger",

## 11 Troubleshooting

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module './docs/swagger-output.json'` | Belum pernah generate. | `npm run swagger` |
| `Cannot find module 'swagger-autogen'` | Paket belum terpasang. | Ulangi langkah 1. |
| `'#swagger.requestBody' out of structure` | Kurung di komentar tidak lengkap. Terminal **tetap menulis Success**. | Perbaiki kurungnya, generate lagi. Baca selalu seluruh keluaran terminal. |
| Komentar tidak berpengaruh | Ditulis di luar fungsi, atau belum generate. | Pindahkan ke dalam fungsi. |
| Endpoint baru tidak muncul | Belum generate, atau route tidak terhubung dari `app.js`. | `npm run swagger` |
| Body berisi `any` atau kosong | Belum ada komentar `requestBody`. | Lihat langkah 6. |
| Sudah Authorize tetap `401` | Script belum berisi `security`, atau token kedaluwarsa. | Ulangi langkah 5, login lagi. |
| Tampilan masih yang lama | `app.js` masih memanggil `./docs/swagger`. | Ulangi langkah 4. |

## 12 Checklist

- `npm run swagger` selesai tanpa pesan `out of structure`.
- `/swagger/` menampilkan kelompok Auth dan Profil dengan contoh isian.
- Tanpa token, `GET /api/profile` membalas `401`; setelah Authorize, `200`.
- Di server produksi, route `/swagger` dimatikan atau dilindungi.

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
