[← Daftar tutorial project](index.md)

Project 13 · CRUD 1 Tabel

# Warteg: CRUD Lauk

Menambahkan tabel milik project **Warteg** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `lauk` untuk project **Warteg**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/lauk` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/lauk/{id}` | Detail satu data |
| `POST /api/lauk` | Tambah |
| `PUT /api/lauk/{id}` | Ubah |
| `DELETE /api/lauk/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama` | teks | wajib | maks. 100 karakter; contoh: `"Orek Tempe"` |
| `harga` | angka desimal | wajib | minimal 0; contoh: `4000` |
| `porsi_tersedia` | bilangan bulat | wajib | minimal 0; contoh: `25` |
| `keterangan` | teks | opsional | contoh: `"Pedas sedang"` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model Lauk` dan satu baris relasi `lauk Lauk[]` di model `User`.

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

      lauk Lauk[]

      @@map("users")
    }

    model Lauk {
      id             Int      @id @default(autoincrement())
      user_id        Int
      nama           String   @db.VarChar(100)
      harga          Decimal  @db.Decimal(12, 2)
      porsi_tersedia Int
      keterangan     String?
      created_at     DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("lauk")
    }

terminal

    npx prisma migrate dev --name tambah_lauk

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/laukRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama: true,
      harga: true,
      porsi_tersedia: true,
      keterangan: true,
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
      return mapRow(await prisma.lauk.create({ data, select: kolom }));
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.lauk.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows.map(mapRow);
    }

    async function countByUser(userId, q) {
      return prisma.lauk.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return mapRow(await prisma.lauk.findUnique({ where: { id }, select: kolom }));
    }

    async function update(id, data) {
      return mapRow(await prisma.lauk.update({ where: { id }, data, select: kolom }));
    }

    async function remove(id) {
      await prisma.lauk.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

src/services/laukService.js

    const laukRepository = require('../repositories/laukRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama: { tipe: 'teks', wajib: true, max: 100 },
      harga: { tipe: 'angka', wajib: true, min: 0, max: 9999999999.99 },
      porsi_tersedia: { tipe: 'bulat', wajib: true, min: 0 },
      keterangan: { tipe: 'teks', wajib: false },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await laukRepository.findAllByUser(userId, q, limit, offset);
      const total = await laukRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await laukRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return laukRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return laukRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await laukRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/laukHandler.js

    const laukService = require('../services/laukService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await laukService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await laukService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await laukService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await laukService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await laukService.remove(req.userId, parseId(req.params.id));
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
    const laukHandler = require('./handlers/laukHandler');

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
    app.get('/api/lauk', requireAuth, laukHandler.list);
    app.get('/api/lauk/:id', requireAuth, laukHandler.detail);
    app.post('/api/lauk', requireAuth, laukHandler.create);
    app.put('/api/lauk/:id', requireAuth, laukHandler.update);
    app.delete('/api/lauk/:id', requireAuth, laukHandler.remove);

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

src/docs/lauk.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Warteg',
      path: 'lauk',
      properties: {
        nama: { type: 'string', maxLength: 100, example: 'Orek Tempe' },
        harga: { type: 'number', example: 4000 },
        porsi_tersedia: { type: 'integer', example: 25 },
        keterangan: { type: 'string', example: 'Pedas sedang' },
      },
      required: ['nama', 'harga', 'porsi_tersedia'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul lauk ---
    const lauk = require('./lauk');
    module.exports.tags.push(lauk.tag);
    Object.assign(module.exports.paths, lauk.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Warteg**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama": "Orek Tempe",
      "harga": 4000,
      "porsi_tersedia": 25,
      "keterangan": "Pedas sedang"
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/lauk \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama": "Orek Tempe", "harga": 4000, "porsi_tersedia": 25, "keterangan": "Pedas sedang"}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama` dari body | `400` nama wajib diisi |
| POST | Isi `harga` dengan teks `"seribu"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Buat endpoint `PUT /api/lauk/{id}/jual` yang mengurangi 1 porsi dan menolak bila habis.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
