[← Daftar tutorial project](index.md)

Project 06 · CRUD 1 Tabel

# Klinik Hewan: CRUD Pasien Hewan

Menambahkan tabel milik project **Klinik Hewan** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `pasien_hewan` untuk project **Klinik Hewan**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/pasien-hewan` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/pasien-hewan/{id}` | Detail satu data |
| `POST /api/pasien-hewan` | Tambah |
| `PUT /api/pasien-hewan/{id}` | Ubah |
| `DELETE /api/pasien-hewan/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama_hewan` | teks | wajib | maks. 100 karakter; contoh: `"Milo"` |
| `jenis` | teks | wajib | maks. 50 karakter; contoh: `"Kucing"` |
| `umur_bulan` | bilangan bulat | wajib | minimal 0; contoh: `14` |
| `nama_pemilik` | teks | wajib | maks. 100 karakter; contoh: `"Andi"` |
| `keluhan` | teks | opsional | contoh: `"Tidak mau makan sejak kemarin"` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama_hewan`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model PasienHewan` dan satu baris relasi `pasienHewan PasienHewan[]` di model `User`.

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

      pasienHewan PasienHewan[]

      @@map("users")
    }

    model PasienHewan {
      id           Int      @id @default(autoincrement())
      user_id      Int
      nama_hewan   String   @db.VarChar(100)
      jenis        String   @db.VarChar(50)
      umur_bulan   Int
      nama_pemilik String   @db.VarChar(100)
      keluhan      String?
      created_at   DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("pasien_hewan")
    }

terminal

    npx prisma migrate dev --name tambah_pasien_hewan

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/pasienHewanRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama_hewan: true,
      jenis: true,
      umur_bulan: true,
      nama_pemilik: true,
      keluhan: true,
    };

    // Selalu dibatasi user_id, supaya pengguna hanya melihat datanya sendiri.
    function buildWhere(userId, q) {
      const where = { user_id: userId };
      if (q) where.nama_hewan = { contains: q, mode: 'insensitive' };
      return where;
    }

    async function create(data) {
      return await prisma.pasienHewan.create({ data, select: kolom });
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.pasienHewan.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows;
    }

    async function countByUser(userId, q) {
      return prisma.pasienHewan.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return await prisma.pasienHewan.findUnique({ where: { id }, select: kolom });
    }

    async function update(id, data) {
      return await prisma.pasienHewan.update({ where: { id }, data, select: kolom });
    }

    async function remove(id) {
      await prisma.pasienHewan.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

src/services/pasienHewanService.js

    const pasienHewanRepository = require('../repositories/pasienHewanRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama_hewan: { tipe: 'teks', wajib: true, max: 100 },
      jenis: { tipe: 'teks', wajib: true, max: 50 },
      umur_bulan: { tipe: 'bulat', wajib: true, min: 0 },
      nama_pemilik: { tipe: 'teks', wajib: true, max: 100 },
      keluhan: { tipe: 'teks', wajib: false },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await pasienHewanRepository.findAllByUser(userId, q, limit, offset);
      const total = await pasienHewanRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await pasienHewanRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return pasienHewanRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return pasienHewanRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await pasienHewanRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/pasienHewanHandler.js

    const pasienHewanService = require('../services/pasienHewanService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await pasienHewanService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await pasienHewanService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await pasienHewanService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await pasienHewanService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await pasienHewanService.remove(req.userId, parseId(req.params.id));
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
    const pasienHewanHandler = require('./handlers/pasienHewanHandler');

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
    app.get('/api/pasien-hewan', requireAuth, pasienHewanHandler.list);
    app.get('/api/pasien-hewan/:id', requireAuth, pasienHewanHandler.detail);
    app.post('/api/pasien-hewan', requireAuth, pasienHewanHandler.create);
    app.put('/api/pasien-hewan/:id', requireAuth, pasienHewanHandler.update);
    app.delete('/api/pasien-hewan/:id', requireAuth, pasienHewanHandler.remove);

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

src/docs/pasienHewan.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Klinik Hewan',
      path: 'pasien-hewan',
      properties: {
        nama_hewan: { type: 'string', maxLength: 100, example: 'Milo' },
        jenis: { type: 'string', maxLength: 50, example: 'Kucing' },
        umur_bulan: { type: 'integer', example: 14 },
        nama_pemilik: { type: 'string', maxLength: 100, example: 'Andi' },
        keluhan: { type: 'string', example: 'Tidak mau makan sejak kemarin' },
      },
      required: ['nama_hewan', 'jenis', 'umur_bulan', 'nama_pemilik'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul pasien-hewan ---
    const pasienHewan = require('./pasienHewan');
    module.exports.tags.push(pasienHewan.tag);
    Object.assign(module.exports.paths, pasienHewan.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Klinik Hewan**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama_hewan": "Milo",
      "jenis": "Kucing",
      "umur_bulan": 14,
      "nama_pemilik": "Andi",
      "keluhan": "Tidak mau makan sejak kemarin"
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/pasien-hewan \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama_hewan": "Milo", "jenis": "Kucing", "umur_bulan": 14, "nama_pemilik": "Andi", "keluhan": "Tidak mau makan sejak kemarin"}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama_hewan` dari body | `400` nama_hewan wajib diisi |
| POST | Isi `umur_bulan` dengan teks `"sepuluh"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Izinkan pencarian `?q=` mencocokkan nama hewan **atau** nama pemilik.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
