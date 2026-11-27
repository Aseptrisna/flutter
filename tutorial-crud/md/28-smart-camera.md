[← Daftar tutorial project](index.md)

Project 28 · CRUD 1 Tabel

# Smart Camera: CRUD Kamera

Menambahkan tabel milik project **Smart Camera** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `kamera` untuk project **Smart Camera**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/kamera` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/kamera/{id}` | Detail satu data |
| `POST /api/kamera` | Tambah |
| `PUT /api/kamera/{id}` | Ubah |
| `DELETE /api/kamera/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama` | teks | wajib | maks. 100 karakter; contoh: `"Kamera Gerbang"` |
| `lokasi` | teks | wajib | maks. 100 karakter; contoh: `"Pintu depan"` |
| `url_stream` | teks | wajib | maks. 255 karakter; contoh: `"rtsp://192.168.1.10:554/stream"` |
| `aktif` | true / false | opsional | contoh: `true` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model Kamera` dan satu baris relasi `kamera Kamera[]` di model `User`.

prisma/schema.prisma

    // Skema database. User dipakai semua project; tambahkan tabelmu di bawahnya.

    generator client {
      provider = "prisma-client-js"
    }

    datasource db {
      provider = "postgresql"
      url      = env("DATABASE_URL")
    }

    model User {
      id         Int      @id @default(autoincrement())
      nama       String   @db.VarChar(100)
      email      String   @unique @db.VarChar(150)
      password   String   @db.VarChar(255)
      created_at DateTime @default(now()) @db.Timestamp(6)

      kamera Kamera[]

      @@map("users")
    }

    model Kamera {
      id         Int      @id @default(autoincrement())
      user_id    Int
      nama       String   @db.VarChar(100)
      lokasi     String   @db.VarChar(100)
      url_stream String   @db.VarChar(255)
      aktif      Boolean  @default(false)
      created_at DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("kamera")
    }

terminal

    npx prisma migrate dev --name tambah_kamera

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/kameraRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama: true,
      lokasi: true,
      url_stream: true,
      aktif: true,
    };

    // Selalu dibatasi user_id, supaya pengguna hanya melihat datanya sendiri.
    function buildWhere(userId, q) {
      const where = { user_id: userId };
      if (q) where.nama = { contains: q, mode: 'insensitive' };
      return where;
    }

    async function create(data) {
      return await prisma.kamera.create({ data, select: kolom });
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.kamera.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows;
    }

    async function countByUser(userId, q) {
      return prisma.kamera.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return await prisma.kamera.findUnique({ where: { id }, select: kolom });
    }

    async function update(id, data) {
      return await prisma.kamera.update({ where: { id }, data, select: kolom });
    }

    async function remove(id) {
      await prisma.kamera.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

src/services/kameraService.js

    const kameraRepository = require('../repositories/kameraRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama: { tipe: 'teks', wajib: true, max: 100 },
      lokasi: { tipe: 'teks', wajib: true, max: 100 },
      url_stream: { tipe: 'teks', wajib: true, max: 255 },
      aktif: { tipe: 'boolean', wajib: false },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await kameraRepository.findAllByUser(userId, q, limit, offset);
      const total = await kameraRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await kameraRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return kameraRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return kameraRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await kameraRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/kameraHandler.js

    const kameraService = require('../services/kameraService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await kameraService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await kameraService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await kameraService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await kameraService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await kameraService.remove(req.userId, parseId(req.params.id));
        ok(res, 200, { message: 'data berhasil dihapus' });
      } catch (err) {
        next(err);
      }
    }

    module.exports = { list, detail, create, update, remove };

## 07 Route

Ganti seluruh isi `src/app.js`. Tambahannya: satu `require` handler dan lima route yang semuanya melewati `requireAuth`.

src/app.js

    const express = require('express');
    const cors = require('cors');
    const swaggerUi = require('swagger-ui-express');

    const swaggerSpec = require('./docs/swagger');
    const { requireAuth } = require('./middleware/auth');
    const { loginLimiter } = require('./middleware/rateLimit');
    const { errorHandler } = require('./middleware/errorHandler');

    const authHandler = require('./handlers/authHandler');
    const kameraHandler = require('./handlers/kameraHandler');

    const app = express();

    app.use(cors());
    app.use(express.json());

    // auth
    app.post('/api/auth/register', authHandler.register);
    app.post('/api/auth/login', loginLimiter, authHandler.login);

    // profile (butuh login)
    app.get('/api/profile', requireAuth, authHandler.profile);
    app.put('/api/profile', requireAuth, authHandler.updateProfile);
    app.put('/api/profile/password', requireAuth, authHandler.updatePassword);

    // --- route project-mu ---
    app.get('/api/kamera', requireAuth, kameraHandler.list);
    app.get('/api/kamera/:id', requireAuth, kameraHandler.detail);
    app.post('/api/kamera', requireAuth, kameraHandler.create);
    app.put('/api/kamera/:id', requireAuth, kameraHandler.update);
    app.delete('/api/kamera/:id', requireAuth, kameraHandler.remove);

    // health check
    app.get('/healthz', (req, res) => res.sendStatus(200));

    // dokumentasi Swagger. persistAuthorization: token tetap tersimpan setelah reload
    // /swagger/index.html (alamat di versi Go) dialihkan, karena file bawaan paket
    // di alamat itu menampilkan contoh "Petstore", bukan API kita.
    app.get('/swagger/index.html', (req, res) => res.redirect('/swagger/'));
    app.use(
      '/swagger',
      swaggerUi.serve,
      swaggerUi.setup(swaggerSpec, { swaggerOptions: { persistAuthorization: true } }),
    );

    // errorHandler WAJIB didaftarkan PALING TERAKHIR -- Express mengenali
    // middleware 4-parameter (err, req, res, next) sebagai error handler hanya
    // kalau ia didaftarkan setelah semua route lain.
    app.use(errorHandler);

    module.exports = app;

## 08 Swagger

Buat file dokumentasi, lalu daftarkan.

src/docs/kamera.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Smart Camera',
      path: 'kamera',
      properties: {
        nama: { type: 'string', maxLength: 100, example: 'Kamera Gerbang' },
        lokasi: { type: 'string', maxLength: 100, example: 'Pintu depan' },
        url_stream: { type: 'string', maxLength: 255, example: 'rtsp://192.168.1.10:554/stream' },
        aktif: { type: 'boolean', example: true },
      },
      required: ['nama', 'lokasi', 'url_stream'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul kamera ---
    const kamera = require('./kamera');
    module.exports.tags.push(kamera.tag);
    Object.assign(module.exports.paths, kamera.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Smart Camera**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama": "Kamera Gerbang",
      "lokasi": "Pintu depan",
      "url_stream": "rtsp://192.168.1.10:554/stream",
      "aktif": true
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/kamera \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama": "Kamera Gerbang", "lokasi": "Pintu depan", "url_stream": "rtsp://192.168.1.10:554/stream", "aktif": true}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama` dari body | `400` nama wajib diisi |
| POST | Isi `aktif` dengan teks `"ya"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Tolak `url_stream` yang tidak diawali `rtsp://` atau `http`.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
