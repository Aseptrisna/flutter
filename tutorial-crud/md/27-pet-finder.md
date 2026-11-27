[← Daftar tutorial project](index.md)

Project 27 · CRUD 1 Tabel

# Pet Finder: CRUD Laporan Hilang

Menambahkan tabel milik project **Pet Finder** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `laporan_hilang` untuk project **Pet Finder**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/laporan-hilang` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/laporan-hilang/{id}` | Detail satu data |
| `POST /api/laporan-hilang` | Tambah |
| `PUT /api/laporan-hilang/{id}` | Ubah |
| `DELETE /api/laporan-hilang/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama_hewan` | teks | wajib | maks. 100 karakter; contoh: `"Bruno"` |
| `jenis` | teks | wajib | maks. 50 karakter; contoh: `"Anjing"` |
| `lokasi_terakhir` | teks | wajib | maks. 200 karakter; contoh: `"Kedaton, Bandar Lampung"` |
| `tanggal_hilang` | tanggal (YYYY-MM-DD) | wajib | contoh: `"2026-11-20"` |
| `status` | pilihan | wajib | Salah satu: `hilang`, `ditemukan` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama_hewan`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model LaporanHilang` dan satu baris relasi `laporanHilang LaporanHilang[]` di model `User`.

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

      laporanHilang LaporanHilang[]

      @@map("users")
    }

    model LaporanHilang {
      id              Int      @id @default(autoincrement())
      user_id         Int
      nama_hewan      String   @db.VarChar(100)
      jenis           String   @db.VarChar(50)
      lokasi_terakhir String   @db.VarChar(200)
      tanggal_hilang  DateTime @db.Date
      status          String   @db.VarChar(30)
      created_at      DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("laporan_hilang")
    }

terminal

    npx prisma migrate dev --name tambah_laporan_hilang

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/laporanHilangRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama_hewan: true,
      jenis: true,
      lokasi_terakhir: true,
      tanggal_hilang: true,
      status: true,
    };

    // mapRow mengubah tipe dari Prisma menjadi bentuk JSON yang ramah klien:
    // Decimal -> angka biasa, tanggal -> teks YYYY-MM-DD.
    function mapRow(row) {
      if (!row) return row;
      return {
        ...row,
        tanggal_hilang: row.tanggal_hilang && row.tanggal_hilang.toISOString().slice(0, 10),
      };
    }

    // Selalu dibatasi user_id, supaya pengguna hanya melihat datanya sendiri.
    function buildWhere(userId, q) {
      const where = { user_id: userId };
      if (q) where.nama_hewan = { contains: q, mode: 'insensitive' };
      return where;
    }

    async function create(data) {
      return mapRow(await prisma.laporanHilang.create({ data, select: kolom }));
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.laporanHilang.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows.map(mapRow);
    }

    async function countByUser(userId, q) {
      return prisma.laporanHilang.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return mapRow(await prisma.laporanHilang.findUnique({ where: { id }, select: kolom }));
    }

    async function update(id, data) {
      return mapRow(await prisma.laporanHilang.update({ where: { id }, data, select: kolom }));
    }

    async function remove(id) {
      await prisma.laporanHilang.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

src/services/laporanHilangService.js

    const laporanHilangRepository = require('../repositories/laporanHilangRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama_hewan: { tipe: 'teks', wajib: true, max: 100 },
      jenis: { tipe: 'teks', wajib: true, max: 50 },
      lokasi_terakhir: { tipe: 'teks', wajib: true, max: 200 },
      tanggal_hilang: { tipe: 'tanggal', wajib: true },
      status: { tipe: 'pilihan', wajib: true, opsi: ['hilang', 'ditemukan'] },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await laporanHilangRepository.findAllByUser(userId, q, limit, offset);
      const total = await laporanHilangRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await laporanHilangRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return laporanHilangRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return laporanHilangRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await laporanHilangRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/laporanHilangHandler.js

    const laporanHilangService = require('../services/laporanHilangService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await laporanHilangService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await laporanHilangService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await laporanHilangService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await laporanHilangService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await laporanHilangService.remove(req.userId, parseId(req.params.id));
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
    const laporanHilangHandler = require('./handlers/laporanHilangHandler');

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
    app.get('/api/laporan-hilang', requireAuth, laporanHilangHandler.list);
    app.get('/api/laporan-hilang/:id', requireAuth, laporanHilangHandler.detail);
    app.post('/api/laporan-hilang', requireAuth, laporanHilangHandler.create);
    app.put('/api/laporan-hilang/:id', requireAuth, laporanHilangHandler.update);
    app.delete('/api/laporan-hilang/:id', requireAuth, laporanHilangHandler.remove);

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

src/docs/laporanHilang.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Pet Finder',
      path: 'laporan-hilang',
      properties: {
        nama_hewan: { type: 'string', maxLength: 100, example: 'Bruno' },
        jenis: { type: 'string', maxLength: 50, example: 'Anjing' },
        lokasi_terakhir: { type: 'string', maxLength: 200, example: 'Kedaton, Bandar Lampung' },
        tanggal_hilang: { type: 'string', format: 'date', example: '2026-11-20' },
        status: { type: 'string', enum: ['hilang', 'ditemukan'], example: 'hilang' },
      },
      required: ['nama_hewan', 'jenis', 'lokasi_terakhir', 'tanggal_hilang', 'status'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul laporan-hilang ---
    const laporanHilang = require('./laporanHilang');
    module.exports.tags.push(laporanHilang.tag);
    Object.assign(module.exports.paths, laporanHilang.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Pet Finder**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama_hewan": "Bruno",
      "jenis": "Anjing",
      "lokasi_terakhir": "Kedaton, Bandar Lampung",
      "tanggal_hilang": "2026-11-20",
      "status": "hilang"
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/laporan-hilang \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama_hewan": "Bruno", "jenis": "Anjing", "lokasi_terakhir": "Kedaton, Bandar Lampung", "tanggal_hilang": "2026-11-20", "status": "hilang"}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama_hewan` dari body | `400` nama_hewan wajib diisi |
| POST | Isi `tanggal_hilang` dengan `2026-02-30` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Buat endpoint publik (tanpa login) berisi laporan berstatus hilang.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
