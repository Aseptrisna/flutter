[← Daftar tutorial project](index.md)

Project 02 · CRUD 1 Tabel

# Topup ML: CRUD Paket Diamond

Menambahkan tabel milik project **Topup ML** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `paket_diamond` untuk project **Topup ML**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/paket-diamond` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/paket-diamond/{id}` | Detail satu data |
| `POST /api/paket-diamond` | Tambah |
| `PUT /api/paket-diamond/{id}` | Ubah |
| `DELETE /api/paket-diamond/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama` | teks | wajib | maks. 100 karakter; contoh: `"Paket Hemat 86"` |
| `jumlah_diamond` | bilangan bulat | wajib | minimal 1; contoh: `86` |
| `harga` | angka desimal | wajib | minimal 0; contoh: `22000` |
| `aktif` | true / false | opsional | contoh: `true` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model PaketDiamond` dan satu baris relasi `paketDiamond PaketDiamond[]` di model `User`.

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

      paketDiamond PaketDiamond[]

      @@map("users")
    }

    model PaketDiamond {
      id             Int      @id @default(autoincrement())
      user_id        Int
      nama           String   @db.VarChar(100)
      jumlah_diamond Int
      harga          Decimal  @db.Decimal(12, 2)
      aktif          Boolean  @default(false)
      created_at     DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("paket_diamond")
    }

terminal

    npx prisma migrate dev --name tambah_paket_diamond

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/paketDiamondRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama: true,
      jumlah_diamond: true,
      harga: true,
      aktif: true,
    };

    // mapRow mengubah tipe dari Prisma menjadi bentuk JSON yang ramah klien:
    // Decimal -> angka biasa, tanggal -> teks YYYY-MM-DD.
    function mapRow(row) {
      if (!row) return row;
      return {
        ...row,
        harga: row.harga === null ? null : Number(row.harga),
      };
    }

    // Selalu dibatasi user_id, supaya pengguna hanya melihat datanya sendiri.
    function buildWhere(userId, q) {
      const where = { user_id: userId };
      if (q) where.nama = { contains: q, mode: 'insensitive' };
      return where;
    }

    async function create(data) {
      return mapRow(await prisma.paketDiamond.create({ data, select: kolom }));
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.paketDiamond.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows.map(mapRow);
    }

    async function countByUser(userId, q) {
      return prisma.paketDiamond.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return mapRow(await prisma.paketDiamond.findUnique({ where: { id }, select: kolom }));
    }

    async function update(id, data) {
      return mapRow(await prisma.paketDiamond.update({ where: { id }, data, select: kolom }));
    }

    async function remove(id) {
      await prisma.paketDiamond.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

src/services/paketDiamondService.js

    const paketDiamondRepository = require('../repositories/paketDiamondRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama: { tipe: 'teks', wajib: true, max: 100 },
      jumlah_diamond: { tipe: 'bulat', wajib: true, min: 1 },
      harga: { tipe: 'angka', wajib: true, min: 0, max: 9999999999.99 },
      aktif: { tipe: 'boolean', wajib: false },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await paketDiamondRepository.findAllByUser(userId, q, limit, offset);
      const total = await paketDiamondRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await paketDiamondRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return paketDiamondRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return paketDiamondRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await paketDiamondRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/paketDiamondHandler.js

    const paketDiamondService = require('../services/paketDiamondService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await paketDiamondService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await paketDiamondService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await paketDiamondService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await paketDiamondService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await paketDiamondService.remove(req.userId, parseId(req.params.id));
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
    const paketDiamondHandler = require('./handlers/paketDiamondHandler');

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
    app.get('/api/paket-diamond', requireAuth, paketDiamondHandler.list);
    app.get('/api/paket-diamond/:id', requireAuth, paketDiamondHandler.detail);
    app.post('/api/paket-diamond', requireAuth, paketDiamondHandler.create);
    app.put('/api/paket-diamond/:id', requireAuth, paketDiamondHandler.update);
    app.delete('/api/paket-diamond/:id', requireAuth, paketDiamondHandler.remove);

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

src/docs/paketDiamond.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Topup ML',
      path: 'paket-diamond',
      properties: {
        nama: { type: 'string', maxLength: 100, example: 'Paket Hemat 86' },
        jumlah_diamond: { type: 'integer', example: 86 },
        harga: { type: 'number', example: 22000 },
        aktif: { type: 'boolean', example: true },
      },
      required: ['nama', 'jumlah_diamond', 'harga'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul paket-diamond ---
    const paketDiamond = require('./paketDiamond');
    module.exports.tags.push(paketDiamond.tag);
    Object.assign(module.exports.paths, paketDiamond.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Topup ML**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama": "Paket Hemat 86",
      "jumlah_diamond": 86,
      "harga": 22000,
      "aktif": true
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/paket-diamond \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama": "Paket Hemat 86", "jumlah_diamond": 86, "harga": 22000, "aktif": true}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama` dari body | `400` nama wajib diisi |
| POST | Isi `jumlah_diamond` dengan teks `"sepuluh"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Tambahkan query `?aktif=true` untuk menampilkan paket yang masih dijual saja.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
