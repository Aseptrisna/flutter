[← Daftar tutorial project](index.md)

Project 10 · CRUD 1 Tabel

# Toko HP: CRUD Handphone

Menambahkan tabel milik project **Toko HP** di atas fondasi modul user, memakai Express, Prisma, dan Swagger.

## 01 Yang Akan Dibuat

CRUD tabel `handphone` untuk project **Toko HP**. Setiap data punya pemilik: pengguna hanya bisa melihat dan mengubah datanya sendiri.

| Endpoint | Fungsi |
|----|----|
| `GET /api/handphone` | Daftar milik sendiri, dengan `?q=`, `page`, `limit` |
| `GET /api/handphone/{id}` | Detail satu data |
| `POST /api/handphone` | Tambah |
| `PUT /api/handphone/{id}` | Ubah |
| `DELETE /api/handphone/{id}` | Hapus |

Syarat sebelum mulai

Selesaikan [Fondasi Modul User](00-fondasi.md) sampai `GET /profile` membalas `200`.

## 02 Rancangan Tabel

| Kolom | Tipe | Isian | Keterangan |
|----|----|----|----|
| `id` | bilangan bulat | otomatis | Primary key |
| `user_id` | bilangan bulat | dari token | Pemilik data |
| `merek` | teks | wajib | maks. 50 karakter; contoh: `"Samsung"` |
| `tipe` | teks | wajib | maks. 100 karakter; contoh: `"Galaxy A16"` |
| `ram_gb` | bilangan bulat | wajib | minimal 1; contoh: `8` |
| `harga` | angka desimal | wajib | minimal 0; contoh: `2999000` |
| `stok` | bilangan bulat | wajib | minimal 0; contoh: `7` |

Kolom `created_at` juga dibuat otomatis. Pencarian `?q=` mencocokkan kolom `tipe`.

## 03 Skema & Migrasi

Ganti seluruh isi `prisma/schema.prisma`. Yang baru: `model Handphone` dan satu baris relasi `handphone Handphone[]` di model `User`.

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

      handphone Handphone[]

      @@map("users")
    }

    model Handphone {
      id         Int      @id @default(autoincrement())
      user_id    Int
      merek      String   @db.VarChar(50)
      tipe       String   @db.VarChar(100)
      ram_gb     Int
      harga      Decimal  @db.Decimal(12, 2)
      stok       Int
      created_at DateTime @default(now()) @db.Timestamp(6)

      user User @relation(fields: [user_id], references: [id], onDelete: Cascade)

      @@index([user_id])
      @@map("handphone")
    }

terminal

    npx prisma migrate dev --name tambah_handphone

Hentikan dulu `npm run dev` saat migrasi, lalu nyalakan lagi setelah semua file di bawah selesai. Penjelasan migrasi: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5).

## 04 Repository — Akses Database

Hanya lapisan ini yang berbicara dengan database. Semua daftar dibatasi `user_id`.

src/repositories/handphoneRepository.js

    const prisma = require('../db');

    // Kolom yang dikirim ke klien. created_at sengaja tidak ikut.
    const kolom = {
      id: true,
      user_id: true,
      merek: true,
      tipe: true,
      ram_gb: true,
      harga: true,
      stok: true,
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
      if (q) where.tipe = { contains: q, mode: 'insensitive' };
      return where;
    }

    async function create(data) {
      return mapRow(await prisma.handphone.create({ data, select: kolom }));
    }

    async function findAllByUser(userId, q, limit, offset) {
      const rows = await prisma.handphone.findMany({
        where: buildWhere(userId, q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: kolom,
      });
      return rows.map(mapRow);
    }

    async function countByUser(userId, q) {
      return prisma.handphone.count({ where: buildWhere(userId, q) });
    }

    async function findById(id) {
      return mapRow(await prisma.handphone.findUnique({ where: { id }, select: kolom }));
    }

    async function update(id, data) {
      return mapRow(await prisma.handphone.update({ where: { id }, data, select: kolom }));
    }

    async function remove(id) {
      await prisma.handphone.delete({ where: { id } });
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

src/services/handphoneService.js

    const handphoneRepository = require('../repositories/handphoneRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { validate } = require('../utils/validate');
    const { NotFoundError, ForbiddenError } = require('../errors');

    // Aturan tiap kolom. Samakan dengan schema.prisma.
    const aturan = {
      merek: { tipe: 'teks', wajib: true, max: 50 },
      tipe: { tipe: 'teks', wajib: true, max: 100 },
      ram_gb: { tipe: 'bulat', wajib: true, min: 1 },
      harga: { tipe: 'angka', wajib: true, min: 0, max: 9999999999.99 },
      stok: { tipe: 'bulat', wajib: true, min: 0 },
    };

    async function list(userId, q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await handphoneRepository.findAllByUser(userId, q, limit, offset);
      const total = await handphoneRepository.countByUser(userId, q);
      return { data, total, page, limit };
    }

    // authorizeOwner: datanya harus ada (404) dan milik pengguna yang login (403).
    async function authorizeOwner(userId, id) {
      const data = await handphoneRepository.findById(id);
      if (!data) throw new NotFoundError('data tidak ditemukan');
      if (data.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik data ini');
      return data;
    }

    async function create(userId, body) {
      const data = validate(body, aturan);
      // user_id diambil dari token, bukan dari isian klien
      return handphoneRepository.create({ ...data, user_id: userId });
    }

    async function update(userId, id, body) {
      await authorizeOwner(userId, id);
      return handphoneRepository.update(id, validate(body, aturan));
    }

    async function remove(userId, id) {
      await authorizeOwner(userId, id);
      await handphoneRepository.remove(id);
    }

    module.exports = { list, detail: authorizeOwner, create, update, remove };

## 06 Handler — Request & Response

Mengambil input dari `req`, memanggil service, lalu membalas JSON.

src/handlers/handphoneHandler.js

    const handphoneService = require('../services/handphoneService');
    const { ok, paginated } = require('../utils/response');
    const { parseId } = require('../utils/validate');

    async function list(req, res, next) {
      try {
        const q = typeof req.query.q === 'string' ? req.query.q : '';
        const { data, total, page, limit } = await handphoneService.list(req.userId, q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        ok(res, 200, await handphoneService.detail(req.userId, parseId(req.params.id)));
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        ok(res, 201, await handphoneService.create(req.userId, req.body));
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        ok(res, 200, await handphoneService.update(req.userId, parseId(req.params.id), req.body));
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        await handphoneService.remove(req.userId, parseId(req.params.id));
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
    const handphoneHandler = require('./handlers/handphoneHandler');

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
    app.get('/api/handphone', requireAuth, handphoneHandler.list);
    app.get('/api/handphone/:id', requireAuth, handphoneHandler.detail);
    app.post('/api/handphone', requireAuth, handphoneHandler.create);
    app.put('/api/handphone/:id', requireAuth, handphoneHandler.update);
    app.delete('/api/handphone/:id', requireAuth, handphoneHandler.remove);

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

src/docs/handphone.js

    const crudDocs = require('./crud');

    module.exports = crudDocs({
      tag: 'Toko HP',
      path: 'handphone',
      properties: {
        merek: { type: 'string', maxLength: 50, example: 'Samsung' },
        tipe: { type: 'string', maxLength: 100, example: 'Galaxy A16' },
        ram_gb: { type: 'integer', example: 8 },
        harga: { type: 'number', example: 2999000 },
        stok: { type: 'integer', example: 7 },
      },
      required: ['merek', 'tipe', 'ram_gb', 'harga', 'stok'],
    });

src/docs/swagger.js — tambahkan di baris paling bawah

    // --- modul handphone ---
    const handphone = require('./handphone');
    module.exports.tags.push(handphone.tag);
    Object.assign(module.exports.paths, handphone.paths);

## 09 Jalankan & Uji

terminal

    npm run dev

Buka `http://localhost:8080/swagger/`, login, klik *Authorize*, lalu buka kelompok **Toko HP**.

1.  **POST** dengan contoh di bawah → `201`. Catat `id`-nya.
2.  **GET daftar** → `200`, data muncul dan `meta.total` bertambah.
3.  **GET /{id}** → `200`.
4.  **PUT /{id}** dengan nilai yang diubah → `200`.
5.  **DELETE /{id}** → `200`, lalu GET id yang sama → `404`.

contoh body

    {
      "merek": "Samsung",
      "tipe": "Galaxy A16",
      "ram_gb": 8,
      "harga": 2999000,
      "stok": 7
    }

terminal — alternatif tanpa Swagger

    TOKEN="tempel-token-hasil-login"
    curl -s -X POST http://localhost:8080/api/handphone \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"merek": "Samsung", "tipe": "Galaxy A16", "ram_gb": 8, "harga": 2999000, "stok": 7}'

### Uji jalur gagal

| Request | Yang dicoba | Harus dibalas |
|----|----|----|
| POST | Hapus `merek` dari body | `400` merek wajib diisi |
| POST | Isi `ram_gb` dengan teks `"sepuluh"` | `400` |
| GET /{id} | id `999999` | `404` data tidak ditemukan |
| GET, PUT, DELETE /{id} | Login sebagai akun kedua, pakai id milik akun pertama | `403` |
| GET (daftar) | Login sebagai akun kedua | `200`, data akun pertama tidak terlihat |
| Semua | Tanpa token | `401` |

## 10 Tantangan & Troubleshooting

Tantangan (kerjakan sendiri)

Tambahkan filter rentang harga `?min=` dan `?max=`.

| Gejala | Penyebab | Solusi |
|----|----|----|
| `Cannot find module` | Nama file atau folder berbeda dari tutorial. | Samakan huruf besar dan kecilnya. |
| `Cannot read properties of undefined` saat query | Prisma Client belum dibuat ulang. | `npx prisma generate`, lalu restart. |
| Prisma meminta *reset* | Database berisi tabel dari project lain. | Jawab tidak, pakai database baru. |
| Kelompok baru tidak muncul di Swagger | Baris tambahan di `swagger.js` belum ada. | Tambahkan, restart, muat ulang halaman. |

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
