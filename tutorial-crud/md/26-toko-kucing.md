[← Daftar tutorial project](index.md)

Project 26 · CRUD 1 Tabel

# Toko Kucing: CRUD Kucing

Menambahkan tabel milik project **Toko Kucing** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `kucing` untuk project **Toko Kucing**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/kucing` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/kucing/{id}` | Detail satu data |
| `POST /api/kucing` | Tambah |
| `PUT /api/kucing/{id}` | Ubah |
| `DELETE /api/kucing/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `nama` | teks | wajib | maks. 100 karakter; contoh: `"Oyen"` |
| `ras` | teks | wajib | maks. 50 karakter; contoh: `"Persia"` |
| `umur_bulan` | bilangan bulat | wajib | minimal 0; contoh: `4` |
| `jenis_kelamin` | pilihan | wajib | Salah satu: `jantan`, `betina` |
| `harga` | angka desimal | wajib | minimal 0; contoh: `1200000` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `nama`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model Kucing` dan satu baris relasi `kucing Kucing[]` di model `User`.

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

      kucing Kucing[]

      @@map("users")
    }

    model Kucing {
      id            Int      @id @default(autoincrement())
      user_id       Int
      nama          String   @db.VarChar(100)
      ras           String   @db.VarChar(50)
      umur_bulan    Int
      jenis_kelamin String   @db.VarChar(30)
      harga         Decimal  @db.Decimal(12, 2)
      created_at    DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("kucing")
    }

terminal

    npx prisma migrate dev --name tambah_kucing

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/kucingRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      nama: true,
      ras: true,
      umur_bulan: true,
      jenis_kelamin: true,
      harga: true,
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
      return mapRow(await prisma.kucing.create({ data, select: kolom }));
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.kucing.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows.map(mapRow);
    }

    async function countByUser(userId, q) {
      return prisma.kucing.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return mapRow(await prisma.kucing.findUnique({ where: { id }, select: kolom }));
    }

    async function update(id, data) {
      return mapRow(await prisma.kucing.update({ where: { id }, data, select: kolom }));
    }

    async function remove(id) {
      await prisma.kucing.delete({ where: { id } });
    }

    module.exports = { create, findAllByUser, countByUser, findById, update, remove };

## 05 Service — Validasi & Hak Akses

Objek `aturan` menentukan isian yang sah; `validate` membuang kolom lain yang dikirim klien. `authorizeOwner` membalas `404` bila data tidak ada dan `403` bila milik orang lain. `PUT` menulis ulang seluruh data, jadi kolom opsional yang tidak dikirim menjadi kosong (atau `false`).

Service dan handler memanggil `src/utils/validate.js`. Kalau file ini belum ada di foldermu, buat **lebih dulu**. Isinya sama untuk semua project; kalau sudah ada dari Fondasi, lewati.

src/utils/validate.js

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

Lalu buat service-nya.

src/services/kucingService.js

    const kucingRepository = require('../repositories/kucingRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      nama: { tipe: 'teks', wajib: true, max: 100 },
      ras: { tipe: 'teks', wajib: true, max: 50 },
      umur_bulan: { tipe: 'bulat', wajib: true, min: 0 },
      jenis_kelamin: { tipe: 'pilihan', wajib: true, opsi: ['jantan', 'betina'] },
      harga: { tipe: 'angka', wajib: true, min: 0, max: 9999999999.99 },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await kucingRepository.findAllByUser(userId, q, limit, offset);
      const total = await kucingRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await kucingRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return kucingRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return kucingRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await kucingRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/kucingHandler.js

    const kucingService = require('../services/kucingService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await kucingService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await kucingService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await kucingService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await kucingService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await kucingService.remove(req.userId, parseId(req.params.id));
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
    const kucingHandler = require('./handlers/kucingHandler');

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
    app.get('/api/kucing', requireAuth, kucingHandler.list);
    app.get('/api/kucing/:id', requireAuth, kucingHandler.detail);
    app.post('/api/kucing', requireAuth, kucingHandler.create);
    app.put('/api/kucing/:id', requireAuth, kucingHandler.update);
    app.delete('/api/kucing/:id', requireAuth, kucingHandler.remove);

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

File dokumentasi project memanggil `src/docs/crud.js`. Kalau file ini belum ada di foldermu, buat **lebih dulu**. Isinya sama untuk semua project; kalau sudah ada dari Fondasi, lewati.

src/docs/crud.js

    // crudDocs membuat dokumentasi Swagger untuk 5 endpoint CRUD sekaligus.
    function crudDocs({ tag, path, properties, required }) {
      const security = [{ bearerAuth: [] }];
      const contoh = { id: 1, user_id: 1 };
      for (const [nama, p] of Object.entries(properties)) contoh[nama] = p.example;

      const json = (example) => ({ 'application/json': { example } });
      const reply = (description, data) => ({ description, content: json({ data }) });
      const gagal = (description, code) => ({
        description,
        content: json({ error: { message: description, code } }),
      });

      const body = {
        required: true,
        content: { 'application/json': { schema: { type: 'object', required, properties } } },
      };
      const id = [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }];
      const query = ['q', 'page', 'limit'].map((name) => ({
        name,
        in: 'query',
        schema: { type: name === 'q' ? 'string' : 'integer' },
      }));

      const salahInput = gagal('input tidak valid', 'BAD_REQUEST');
      const tanpaToken = gagal('token tidak valid', 'UNAUTHORIZED');
      const bukanPemilik = gagal('Anda bukan pemilik data ini', 'FORBIDDEN');
      const tidakAda = gagal('data tidak ditemukan', 'NOT_FOUND');
      const base = { tags: [tag], security };

      return {
        tag: { name: tag, description: 'Data milik pengguna yang login' },
        paths: {
          [`/${path}`]: {
            get: {
              ...base,
              summary: 'Daftar data milik sendiri',
              parameters: query,
              responses: { 200: reply('Daftar data', [contoh]), 401: tanpaToken },
            },
            post: {
              ...base,
              summary: 'Tambah data',
              requestBody: body,
              responses: { 201: reply('Data dibuat', contoh), 400: salahInput, 401: tanpaToken },
            },
          },
          [`/${path}/{id}`]: {
            get: {
              ...base,
              summary: 'Detail data',
              parameters: id,
              responses: { 200: reply('Detail', contoh), 403: bukanPemilik, 404: tidakAda },
            },
            put: {
              ...base,
              summary: 'Ubah data (kirim semua kolom)',
              parameters: id,
              requestBody: body,
              responses: { 200: reply('Data diubah', contoh), 400: salahInput, 403: bukanPemilik, 404: tidakAda },
            },
            delete: {
              ...base,
              summary: 'Hapus data',
              parameters: id,
              responses: {
                200: reply('Terhapus', { message: 'data berhasil dihapus' }),
                403: bukanPemilik,
                404: tidakAda,
              },
            },
          },
        },
      };
    }

    module.exports = crudDocs;

Buat file dokumentasi, lalu daftarkan.

src/docs/kucing.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Toko Kucing',
      path: 'kucing',
      properties: {
        nama: { type: 'string', maxLength: 100, example: 'Oyen' },
        ras: { type: 'string', maxLength: 50, example: 'Persia' },
        umur_bulan: { type: 'integer', example: 4 },
        jenis_kelamin: { type: 'string', enum: ['jantan', 'betina'], example: 'jantan' },
        harga: { type: 'number', example: 1200000 },
      },
      required: ['nama', 'ras', 'umur_bulan', 'jenis_kelamin', 'harga'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul kucing ---
    const kucing = require('./kucing');
    module.exports.tags.push(kucing.tag);
    Object.assign(module.exports.paths, kucing.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Toko Kucing**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "nama": "Oyen",
      "ras": "Persia",
      "umur_bulan": 4,
      "jenis_kelamin": "jantan",
      "harga": 1200000
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/kucing \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"nama": "Oyen", "ras": "Persia", "umur_bulan": 4, "jenis_kelamin": "jantan", "harga": 1200000}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `nama` dari body | `400` nama wajib diisi |
| POST | Isi `umur_bulan` dengan teks `"sepuluh"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Tambahkan filter `?ras=`.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
