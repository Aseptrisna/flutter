[← Daftar tutorial project](index.md)

Project 01 · CRUD 1 Tabel

# LaundryCare: CRUD Pesanan

Menambahkan tabel milik project **LaundryCare** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `pesanan` untuk project **LaundryCare**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/pesanan` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/pesanan/{id}` | Detail satu data |
| `POST /api/pesanan` | Tambah |
| `PUT /api/pesanan/{id}` | Ubah |
| `DELETE /api/pesanan/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama_pelanggan` | teks | wajib | maks. 100 karakter; contoh: `"Rina"` |
| `layanan` | pilihan | wajib | Salah satu: `cuci_kering`, `cuci_setrika`, `setrika` |
| `berat_kg` | angka desimal | wajib | minimal 0.1; contoh: `3.5` |
| `total` | angka desimal | wajib | minimal 0; contoh: `28000` |
| `status` | pilihan | wajib | Salah satu: `diterima`, `diproses`, `selesai`, `diambil` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama_pelanggan`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model Pesanan` dan satu baris relasi `pesanan Pesanan[]` di model `User`.

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

      pesanan Pesanan[]

      @@map("users")
    }

    model Pesanan {
      id             Int      @id @default(autoincrement())
      user_id        Int
      nama_pelanggan String   @db.VarChar(100)
      layanan        String   @db.VarChar(30)
      berat_kg       Decimal  @db.Decimal(6, 2)
      total          Decimal  @db.Decimal(12, 2)
      status         String   @db.VarChar(30)
      created_at     DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("pesanan")
    }

terminal

    npx prisma migrate dev --name tambah_pesanan

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/pesananRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama_pelanggan: true,
      layanan: true,
      berat_kg: true,
      total: true,
      status: true,
    };

    // mapRow mengubah tipe dari Prisma menjadi bentuk JSON yang ramah klien:
    // Decimal -> angka biasa, tanggal -> teks YYYY-MM-DD.
    function mapRow(row) {
      if (!row) return row;
      return {
        ...row,
        berat_kg: row.berat_kg === null ? null : Number(row.berat_kg),
        total: row.total === null ? null : Number(row.total),
      };
    }

    // Selalu dibatasi user_id, supaya pengguna hanya melihat datanya sendiri.
    function buildWhere(userId, q) {
      const where = { user_id: userId };
      if (q) where.nama_pelanggan = { contains: q, mode: 'insensitive' };
      return where;
    }

    async function create(data) {
      return mapRow(await prisma.pesanan.create({ data, select: kolom }));
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.pesanan.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows.map(mapRow);
    }

    async function countByUser(userId, q) {
      return prisma.pesanan.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return mapRow(await prisma.pesanan.findUnique({ where: { id }, select: kolom }));
    }

    async function update(id, data) {
      return mapRow(await prisma.pesanan.update({ where: { id }, data, select: kolom }));
    }

    async function remove(id) {
      await prisma.pesanan.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

src/services/pesananService.js

    const pesananRepository = require('../repositories/pesananRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama_pelanggan: { tipe: 'teks', wajib: true, max: 100 },
      layanan: { tipe: 'pilihan', wajib: true, opsi: ['cuci_kering', 'cuci_setrika', 'setrika'] },
      berat_kg: { tipe: 'angka', wajib: true, min: 0.1, max: 9999.99 },
      total: { tipe: 'angka', wajib: true, min: 0, max: 9999999999.99 },
      status: { tipe: 'pilihan', wajib: true, opsi: ['diterima', 'diproses', 'selesai', 'diambil'] },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await pesananRepository.findAllByUser(userId, q, limit, offset);
      const total = await pesananRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await pesananRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return pesananRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return pesananRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await pesananRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/pesananHandler.js

    const pesananService = require('../services/pesananService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await pesananService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await pesananService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await pesananService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await pesananService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await pesananService.remove(req.userId, parseId(req.params.id));
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
    const pesananHandler = require('./handlers/pesananHandler');

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
    app.get('/api/pesanan', requireAuth, pesananHandler.list);
    app.get('/api/pesanan/:id', requireAuth, pesananHandler.detail);
    app.post('/api/pesanan', requireAuth, pesananHandler.create);
    app.put('/api/pesanan/:id', requireAuth, pesananHandler.update);
    app.delete('/api/pesanan/:id', requireAuth, pesananHandler.remove);

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

src/docs/pesanan.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'LaundryCare',
      path: 'pesanan',
      properties: {
        nama_pelanggan: { type: 'string', maxLength: 100, example: 'Rina' },
        layanan: { type: 'string', enum: ['cuci_kering', 'cuci_setrika', 'setrika'], example: 'cuci_kering' },
        berat_kg: { type: 'number', example: 3.5 },
        total: { type: 'number', example: 28000 },
        status: { type: 'string', enum: ['diterima', 'diproses', 'selesai', 'diambil'], example: 'diterima' },
      },
      required: ['nama_pelanggan', 'layanan', 'berat_kg', 'total', 'status'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul pesanan ---
    const pesanan = require('./pesanan');
    module.exports.tags.push(pesanan.tag);
    Object.assign(module.exports.paths, pesanan.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **LaundryCare**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama_pelanggan": "Rina",
      "layanan": "cuci_kering",
      "berat_kg": 3.5,
      "total": 28000,
      "status": "diterima"
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/pesanan \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama_pelanggan": "Rina", "layanan": "cuci_kering", "berat_kg": 3.5, "total": 28000, "status": "diterima"}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama_pelanggan` dari body | `400` nama_pelanggan wajib diisi |
| POST | Isi `berat_kg` dengan teks `"seribu"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Hitung `total` di service dari `berat_kg` dan tarif per layanan, supaya klien tidak bisa mengarang harga.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
