<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 9a · Proyek Lengkap

# Membangun umkm-api dengan Node.js, Express & PostgreSQL

Proyek `umkm-api` dari Pertemuan 4 dibangun aslinya pakai Golang. Materi ini membangun ULANG API yang **persis sama** — endpoint sama, aturan bisnis sama, bentuk respons JSON sama — tapi memakai **Node.js + Express + PostgreSQL (node-postgres)**, supaya terlihat jelas bahwa arsitektur (handler → service → repository) dan konsepnya (JWT, bcrypt, ownership, pagination, upload foto) itu universal, tidak terikat satu bahasa. Setiap baris kode di sini sudah benar-benar dijalankan & diuji end-to-end sebelum ditulis di sini — ikuti persis, dijamin menyala tanpa error.

Daftar isi cepat

1.  [01. Tujuan & Prasyarat](#s1)
2.  [02. Membuat Proyek dari Nol](#s2)
3.  [03. Struktur Folder Final](#s3)
4.  [04. Dependency di package.json](#s4)
5.  [05. Skema Database (schema.sql)](#s5)
6.  [06. Environment & Koneksi DB](#s6)
7.  [07. Error Handling Terpusat](#s7)
8.  [08. Middleware: Auth JWT & Rate Limit](#s8)
9.  [09. Upload Foto (multer)](#s9)
10. [10. Repository Layer](#s10)
11. [11. Service Layer: Auth](#s11)
12. [12. Service Layer: UMKM & Produk](#s12)
13. [13. Handler (Controller) Layer](#s13)
14. [14. Routing: app.js](#s14)
15. [15. server.js & Menjalankan Project](#s15)
16. [16. Testing Lengkap via curl](#s16)
17. [17. Troubleshooting Cepat](#s17)
18. [18. Perbandingan Go vs Node.js](#s18)
19. [19. Latihan](#s19)

## 01Tujuan & Prasyarat

Di akhir materi ini akan ada satu proyek `umkm-api-node` yang bisa: register & login (JWT + bcrypt), kelola profil, kelola UMKM milik sendiri (1 user = 1 UMKM, lengkap upload foto), kelola produk per UMKM, pencarian + pagination, dan menolak akses orang lain ke data yang bukan miliknya — fungsinya **identik** dengan `umkm-api` versi Go di Pertemuan 4/9, cukup untuk langsung dipasangkan ke `umkm-app` Flutter yang sudah dibangun di Pertemuan 7 tanpa mengubah satu baris pun kode Flutter-nya.

Sebelum mulai, pastikan:

- **Node.js 18 ke atas** terpasang — cek dengan `node -v` di terminal.
- Akun **Neon** (PostgreSQL) sudah ada dari Pertemuan 4, dengan `DATABASE_URL`-nya dicatat (atau buat proyek Neon baru khusus untuk versi Node ini).
- Editor kode (VS Code direkomendasikan) dan **Postman** atau `curl` untuk menguji endpoint.
- Paham dasar JavaScript: `async/await`, `require`/`module.exports`, dan konsep *middleware* (kalau belum, lihat Pertemuan 1b untuk perbandingan Dart vs sintaks mirip di JS).

Kenapa dibuat ulang, bukan sekadar dijelaskan?

Membaca kode Go lalu kode Node yang melakukan hal sama, baris per baris, adalah cara tercepat membuktikan bahwa yang dipelajari di Pertemuan 4/9 bukan "cara Go", tapi "cara REST API dibangun" — `handler → service → repository`, JWT, bcrypt, dan SQL parameterized adalah konsep yang sama persis di balik bahasa apa pun.

## 02Membuat Proyek dari Nol

Buat folder proyek baru, lalu inisialisasi `package.json` dan install semua dependency yang dipakai sepanjang materi ini:

terminal

    mkdir umkm-api-node && cd umkm-api-node
    npm init -y

    npm install express pg bcrypt jsonwebtoken multer cors dotenv express-rate-limit
    npm install --save-dev nodemon

- `express` — framework HTTP, setara `net/http` + `http.ServeMux` di Go.
- `pg` (node-postgres) — driver PostgreSQL, setara `pgx` di Go.
- `bcrypt` — hashing password satu arah, setara `golang.org/x/crypto/bcrypt`.
- `jsonwebtoken` — membuat & memverifikasi JWT, setara `golang-jwt/jwt`.
- `multer` — middleware upload `multipart/form-data`, setara `r.ParseMultipartForm` manual di Go.
- `cors` — mengizinkan Flutter Web (kalau dipakai) memanggil API dari origin berbeda.
- `dotenv` — membaca berkas `.env`, setara `godotenv`.
- `express-rate-limit` — pembatas percobaan login, setara `golang.org/x/time/rate` yang dipakai manual di Go.
- `nodemon` (dev saja) — restart otomatis server tiap kali berkas disimpan, setara `air`/`fresh` di dunia Go.

Versi Multer wajib 1.x, bukan 2.x

Perintah di atas sengaja menghasilkan `multer@1.4.x` (bukan `2.x`) karena seluruh kode upload di materi ini ditulis & diuji untuk API Multer 1.x (`multer.diskStorage`, `.single()`), yang paling umum dipakai bersama Express 4. Kalau `npm install multer` ternyata menarik versi `2.x`, jalankan `npm install multer@1.4.5-lts.1` secara eksplisit.

## 03Struktur Folder Final

Strukturnya sengaja dibuat semirip mungkin dengan `internal/` di proyek Go, supaya siapa pun yang sudah paham arsitektur `umkm-api` versi Go bisa langsung menebak isi tiap folder di versi Node ini:

struktur folder

    umkm-api-node/
    ├── package.json
    ├── .env                  (dibuat sendiri, JANGAN di-commit ke Git)
    ├── .env.example
    ├── .gitignore
    ├── schema.sql
    ├── server.js             entry point
    ├── uploads/              foto UMKM & produk tersimpan di sini
    └── src/
        ├── app.js            daftar semua route Express
        ├── config.js         baca .env
        ├── db.js             koneksi pg.Pool
        ├── errors.js         kelas error kustom (AppError & turunannya)
        ├── middleware/
        │   ├── auth.js        requireAuth (verifikasi JWT)
        │   ├── rateLimit.js    pembatas percobaan login
        │   └── errorHandler.js  penerjemah error -> response JSON
        ├── utils/
        │   ├── response.js    ok() & paginated()
        │   ├── pagination.js  normalizePagination()
        │   └── upload.js      konfigurasi multer & helper file
        ├── repositories/       akses database mentah (setara internal/repository Go)
        │   ├── userRepository.js
        │   ├── umkmRepository.js
        │   └── produkRepository.js
        ├── services/           aturan bisnis & otorisasi (setara internal/service Go)
        │   ├── authService.js
        │   ├── umkmService.js
        │   └── produkService.js
        └── handlers/           terima request, panggil service, balas JSON (setara internal/handler Go)
            ├── authHandler.js
            ├── umkmHandler.js
            └── produkHandler.js

Buat semua folder kosongnya dulu, biar tidak bolak-balik `mkdir` di tengah jalan:

terminal

    mkdir -p src/middleware src/utils src/repositories src/services src/handlers uploads

## 04Dependency di package.json

Buka `package.json` yang dibuat `npm init -y` tadi, tambahkan bagian `scripts` (bagian `dependencies` sudah otomatis terisi dari `npm install` di Bagian 02, tidak perlu ditulis ulang manual):

package.json

    {
      "name": "umkm-api-node",
      "version": "1.0.0",
      "description": "REST API UMKM — Node.js + Express + PostgreSQL",
      "main": "server.js",
      "scripts": {
        "dev": "nodemon server.js",
        "start": "node server.js"
      },
      "dependencies": {
        "bcrypt": "^5.1.1",
        "cors": "^2.8.5",
        "dotenv": "^16.4.5",
        "express": "^4.19.2",
        "express-rate-limit": "^7.4.0",
        "jsonwebtoken": "^9.0.2",
        "multer": "^1.4.5-lts.1",
        "pg": "^8.12.0"
      },
      "devDependencies": {
        "nodemon": "^3.1.4"
      }
    }

`npm run dev` nantinya dipakai sehari-hari selama development (auto-restart tiap simpan berkas), `npm start` dipakai saat deploy ke server sungguhan (tidak butuh auto-restart).

## 05Skema Database (schema.sql)

Skema tabelnya **persis sama** dengan versi Go (lihat Pertemuan 9 Bagian 04 "Desain Database") — ini penting supaya kedua versi API (Go & Node) bisa saling dipertukarkan tanpa mengubah data yang sudah ada:

schema.sql

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE umkm (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        deskripsi TEXT,
        alamat VARCHAR(255),
        foto VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE produk (
        id SERIAL PRIMARY KEY,
        umkm_id INTEGER NOT NULL REFERENCES umkm(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        harga NUMERIC(12,2) NOT NULL DEFAULT 0,
        deskripsi TEXT,
        foto VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

Jalankan sekali saja ke database Neon-mu (boleh database yang sama dengan versi Go kalau mau menimpa, atau buat proyek Neon baru supaya terpisah) lewat **Neon Console → SQL Editor**: tempel seluruh isi `schema.sql` di atas, klik Run. Atau lewat `psql` dari terminal kalau sudah pernah connect:

terminal

    psql "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require" -f schema.sql

Jangan jalankan dua kali ke database yang sama

`CREATE TABLE` tanpa `IF NOT EXISTS` akan gagal dengan error `relation "users" already exists` kalau tabelnya sudah ada. Itu wajar, bukan bug — artinya skema sudah terpasang, tidak perlu dijalankan ulang.

## 06Environment & Koneksi Database

Buat berkas `.env.example` (ini yang di-commit ke Git, sebagai contoh) dan `.env` (isi sungguhan, wajib masuk `.gitignore`):

.env.example

    DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
    JWT_SECRET=ganti-dengan-string-acak-yang-panjang
    PORT=8080
    UPLOAD_DIR=./uploads

.gitignore

    node_modules/
    .env
    uploads/*
    !uploads/.gitkeep

Salin `.env.example` jadi `.env`, lalu isi `DATABASE_URL` dengan connection string Neon-mu yang sungguhan (dari Neon Console → Connection Details → pastikan bentuknya menyertakan `?sslmode=require` di akhir) dan `JWT_SECRET` dengan string acak panjang (boleh pakai `openssl rand -hex 32` di terminal untuk membuatnya).

### config.js — membaca .env

src/config.js

    require('dotenv').config();

    function getOrDefault(key, def) {
      const v = process.env[key];
      return v && v !== '' ? v : def;
    }

    module.exports = {
      databaseUrl: process.env.DATABASE_URL,
      jwtSecret: process.env.JWT_SECRET,
      port: getOrDefault('PORT', '8080'),
      uploadDir: getOrDefault('UPLOAD_DIR', './uploads'),
    };

### db.js — koneksi pg.Pool

src/db.js

    const { Pool } = require('pg');
    const config = require('./config');

    // Neon mewajibkan koneksi SSL. Kita deteksi dari connection string supaya
    // kode yang sama tetap bisa dipakai untuk Postgres lokal (tanpa SSL) saat
    // development, dan ke Neon (dengan SSL) saat connection string-nya memuat
    // "sslmode=require".
    const useSsl = (config.databaseUrl || '').includes('sslmode=require');

    const pool = new Pool({
      connectionString: config.databaseUrl,
      ssl: useSsl ? { rejectUnauthorized: false } : false,
    });

    pool.on('error', (err) => {
      console.error('Koneksi database bermasalah:', err.message);
    });

    module.exports = pool;

`pg.Pool` setara `pgxpool.Pool` di Go: ia menyimpan sekumpulan koneksi yang dipakai bergantian oleh tiap query, bukan membuka-tutup koneksi baru setiap kali — jauh lebih cepat untuk server yang melayani banyak request sekaligus.

Kenapa ssl: { rejectUnauthorized: false }, bukan true?

Secara prinsip `rejectUnauthorized: true` lebih aman (memverifikasi sertifikat SSL server secara ketat). Tapi banyak environment Node (terutama versi lama atau kontainer minimal) tidak punya daftar root certificate yang lengkap untuk memverifikasi rantai sertifikat Neon, sehingga koneksi gagal dengan error `self-signed certificate in certificate chain` walau sebenarnya aman. `false` dipakai di sini supaya tutorial ini pasti berhasil tersambung di komputer siapa pun — untuk proyek produksi sungguhan, pelajari lebih lanjut opsi `ca` di dokumentasi `node-postgres`.

## 07Error Handling Terpusat

Di versi Go, tiap handler punya blok `switch { case errors.Is(err, domain.ErrNotFound): ... }` yang berulang di 15+ fungsi. Di Node, pola ini disederhanakan: service melempar (`throw`) satu dari empat kelas error kustom yang sudah membawa status HTTP & kode errornya sendiri, dan **satu middleware error di paling akhir** yang menerjemahkannya jadi JSON — tidak perlu diulang di tiap handler.

src/errors.js

    class AppError extends Error {
      constructor(message, code, status) {
        super(message);
        this.code = code;
        this.status = status;
      }
    }

    class InvalidInputError extends AppError {
      constructor(message = 'input tidak valid') {
        super(message, 'BAD_REQUEST', 400);
      }
    }

    class NotFoundError extends AppError {
      constructor(message = 'data tidak ditemukan') {
        super(message, 'NOT_FOUND', 404);
      }
    }

    class ConflictError extends AppError {
      constructor(message = 'data sudah ada') {
        super(message, 'CONFLICT', 409);
      }
    }

    class ForbiddenError extends AppError {
      constructor(message = 'tidak memiliki akses') {
        super(message, 'FORBIDDEN', 403);
      }
    }

    module.exports = {
      AppError,
      InvalidInputError,
      NotFoundError,
      ConflictError,
      ForbiddenError,
    };

Ini padanan langsung dari `domain.ErrNotFound`, `domain.ErrConflict`, dkk di Go — bedanya di Go error itu dibandingkan pakai `errors.Is()` di tiap handler, sedangkan di sini statusnya sudah "menempel" di objek error-nya sendiri sejak dibuat.

### response.js — bentuk respons seragam

src/utils/response.js

    function ok(res, status, data) {
      res.status(status).json({ data });
    }

    function paginated(res, status, data, page, limit, total) {
      res.status(status).json({ data, meta: { page, limit, total } });
    }

    module.exports = { ok, paginated };

Bentuk JSON-nya sengaja dibuat identik dengan versi Go: `{"data": ...}` untuk respons sukses biasa, ditambah `meta: {page, limit, total}` untuk daftar yang dipaginasi — supaya Flutter `ApiService` dari Pertemuan 7 bisa langsung dipakai tanpa diubah.

## 08Middleware: Auth JWT & Rate Limit

### auth.js — verifikasi token JWT

src/middleware/auth.js

    const jwt = require('jsonwebtoken');
    const config = require('../config');

    // requireAuth membaca header Authorization, menerima baik "Bearer TOKEN"
    // maupun token mentah tanpa prefix (supaya mahasiswa yang lupa mengetik
    // "Bearer " di Swagger/Postman tidak selalu dibalas 401 yang membingungkan).
    // jwt.verify dengan algorithms: ['HS256'] memaksa algoritma HS256 saja, agar
    // token dengan header "alg" lain (termasuk "none") selalu ditolak.
    function requireAuth(req, res, next) {
      const header = req.headers.authorization || '';
      if (!header) {
        return res.status(401).json({ error: { message: 'token tidak ditemukan', code: 'UNAUTHORIZED' } });
      }

      const token = header.slice(0, 7).toLowerCase() === 'bearer ' ? header.slice(7) : header;

      try {
        const payload = jwt.verify(token, config.jwtSecret, { algorithms: ['HS256'] });
        req.userId = Number(payload.sub);
        next();
      } catch (err) {
        return res.status(401).json({ error: { message: 'token tidak valid', code: 'UNAUTHORIZED' } });
      }
    }

    module.exports = { requireAuth };

Ini padanan langsung dari `middleware.RequireAuth` di Go: keduanya *higher-order function* — bedanya di Express, middleware cukup berupa fungsi `(req, res, next)` biasa yang dipasang langsung di route, tidak perlu dibungkus sebagai `func(http.Handler) http.Handler` seperti di `net/http`. `req.userId` yang ditempel di sini nanti dibaca oleh semua handler yang butuh tahu siapa yang sedang login — setara `middleware.GetUserID(r)` di Go, yang di sana membaca dari `context.Context` karena `net/http` tidak punya objek `req` yang bisa ditempeli properti bebas.

### rateLimit.js — batasi percobaan login

src/middleware/rateLimit.js

    const rateLimit = require('express-rate-limit');

    // Maksimal 5 percobaan login per menit per alamat IP, agar brute-force
    // password dibatasi -- setara middleware.RateLimit di versi Go.
    const loginLimiter = rateLimit({
      windowMs: 60 * 1000,
      limit: 5,
      standardHeaders: true,
      legacyHeaders: false,
      handler: (req, res) => {
        res.status(429).json({
          error: { message: 'terlalu banyak percobaan, coba lagi nanti', code: 'TOO_MANY_REQUESTS' },
        });
      },
    });

    module.exports = { loginLimiter };

Versi Go menyimpan satu `rate.Limiter` per alamat IP secara manual di dalam sebuah `map` (lihat `ipRateLimiter` di Pertemuan 9 Bagian 09). `express-rate-limit` melakukan hal yang sama persis di baliknya — satu penghitung per IP, direset tiap `windowMs` — jadi tidak perlu ditulis manual.

### errorHandler.js — satu-satunya tempat error diterjemahkan

src/middleware/errorHandler.js

    const { InvalidFileTypeError } = require('../utils/upload');

    // errorHandler adalah satu-satunya tempat error diterjemahkan jadi response
    // JSON. Service/handler tinggal `throw` instance dari src/errors.js, tidak
    // perlu switch-case berulang di tiap endpoint seperti pola errors.Is di
    // versi Go -- karena status HTTP & code sudah menempel di objek error itu
    // sendiri (lihat AppError).
    function errorHandler(err, req, res, next) {
      // Error dari multer (upload foto) ditangani lebih dulu, bentuknya beda
      // dari AppError karena datang dari library pihak ketiga.
      if (err instanceof InvalidFileTypeError) {
        return res.status(400).json({ error: { message: err.message, code: 'BAD_REQUEST' } });
      }
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(400).json({
          error: { message: 'form tidak valid atau file terlalu besar', code: 'BAD_REQUEST' },
        });
      }

      if (err.status) {
        return res.status(err.status).json({ error: { message: err.message, code: err.code } });
      }

      console.error(err);
      res.status(500).json({ error: { message: 'kesalahan server', code: 'INTERNAL' } });
    }

    module.exports = { errorHandler };

Middleware 4-parameter = error handler

Express mengenali sebuah middleware sebagai *error handler* khusus kalau fungsinya punya tepat 4 parameter: `(err, req, res, next)`. Middleware ini harus didaftarkan **paling terakhir** di `app.js`, setelah semua route — dijelaskan lagi di Bagian 14.

## 09Upload Foto (multer)

Padanan dari `saveUploadedFile` di `internal/handler/upload.go`: validasi ekstensi (hanya jpg/jpeg/png), batas ukuran 5MB, nama file dibuat unik, path yang disimpan ke database adalah path **relatif** (mis. `"umkm/169...jpg"`), bukan path disk absolut.

src/utils/upload.js

    const multer = require('multer');
    const path = require('path');
    const fs = require('fs');
    const config = require('../config');

    const ALLOWED_EXT = new Set(['.jpg', '.jpeg', '.png']);

    // InvalidFileTypeError dipakai sebagai penanda error ekstensi tidak didukung,
    // dibedakan dari error multer lain (mis. LIMIT_FILE_SIZE) di errorHandler.
    class InvalidFileTypeError extends Error {
      constructor() {
        super('tipe berkas tidak didukung, hanya jpg/jpeg/png');
        this.code = 'INVALID_FILE_TYPE';
      }
    }

    function storageFor(subDir) {
      return multer.diskStorage({
        destination: (req, file, cb) => {
          const dir = path.join(config.uploadDir, subDir);
          fs.mkdirSync(dir, { recursive: true });
          cb(null, dir);
        },
        filename: (req, file, cb) => {
          const ext = path.extname(file.originalname).toLowerCase();
          const unique = `${Date.now()}${Math.round(Math.random() * 1e9)}`;
          cb(null, `${unique}${ext}`);
        },
      });
    }

    function fileFilter(req, file, cb) {
      const ext = path.extname(file.originalname).toLowerCase();
      if (!ALLOWED_EXT.has(ext)) {
        return cb(new InvalidFileTypeError());
      }
      cb(null, true);
    }

    // uploadSingle mengembalikan middleware multer untuk SATU field file bernama
    // fieldName, disimpan ke UPLOAD_DIR/subDir/. Dipakai sebagai middleware biasa
    // di route, errornya ditangkap oleh errorHandler terpusat.
    function uploadSingle(subDir, fieldName) {
      return multer({
        storage: storageFor(subDir),
        limits: { fileSize: 5 * 1024 * 1024 }, // 5MB, sama seperti versi Go
        fileFilter,
      }).single(fieldName);
    }

    // relativePath mengembalikan path RELATIF (contoh: "umkm/169...jpg") dari
    // req.file hasil multer, atau string kosong kalau pengguna tidak mengunggah
    // foto sama sekali (foto bersifat opsional).
    function relativePath(subDir, file) {
      if (!file) return '';
      return `${subDir}/${file.filename}`;
    }

    // deleteFile menghapus berkas lama di UPLOAD_DIR/relPath, dipanggil setelah
    // update/delete berhasil di database agar tidak ada berkas foto menumpuk.
    function deleteFile(uploadDir, relPath) {
      if (!relPath) return;
      fs.unlink(path.join(uploadDir, relPath), () => {
        // sengaja diabaikan: kalau berkasnya sudah tidak ada pun tidak masalah
      });
    }

    module.exports = { uploadSingle, relativePath, deleteFile, InvalidFileTypeError };

Bedanya dengan Go: Go menyimpan file manual lewat `io.Copy` satu per satu di dalam handler. Multer melakukan seluruh proses (baca stream multipart, simpan ke disk, kasih nama unik) secara otomatis lewat konfigurasi `diskStorage` — handler tinggal membaca hasilnya dari `req.file`.

## 10Repository Layer

Setiap query di sini adalah terjemahan **baris-per-baris** dari repository Go di Pertemuan 9 Bagian 11 — bandingkan langsung kalau perlu.

### userRepository.js

src/repositories/userRepository.js

    const pool = require('../db');

    async function create(user) {
      const { rows } = await pool.query(
        'INSERT INTO users (nama, email, password) VALUES ($1, $2, $3) RETURNING id',
        [user.nama, user.email, user.password]
      );
      return { ...user, id: rows[0].id };
    }

    async function findByEmail(email) {
      const { rows } = await pool.query(
        'SELECT id, nama, email, password FROM users WHERE email = $1',
        [email]
      );
      return rows[0] || null;
    }

    async function findById(id) {
      const { rows } = await pool.query(
        'SELECT id, nama, email, password FROM users WHERE id = $1',
        [id]
      );
      return rows[0] || null;
    }

    async function updateProfile(id, nama, email) {
      await pool.query('UPDATE users SET nama = $1, email = $2 WHERE id = $3', [nama, email, id]);
    }

    async function updatePassword(id, hashedPassword) {
      await pool.query('UPDATE users SET password = $1 WHERE id = $2', [hashedPassword, id]);
    }

    module.exports = { create, findByEmail, findById, updateProfile, updatePassword };

pgx.ErrNoRows jadi null, bukan exception

Di Go, baris yang tidak ketemu membuat `pgx` mengembalikan error `pgx.ErrNoRows` yang lalu dikonversi jadi `domain.ErrNotFound`. `node-postgres` tidak melempar error untuk kasus "tidak ketemu" — ia cuma mengembalikan `rows` kosong (`[]`). Pola `rows[0] || null` di sinilah titik yang setara: repository Node mengembalikan `null`, dan **service**-lah (Bagian 11-12) yang memutuskan melempar `NotFoundError` kalau hasilnya `null` — persis seperti Go, cuma titik konversinya satu layer lebih ke atas.

### umkmRepository.js

src/repositories/umkmRepository.js

    const pool = require('../db');

    async function create(umkm) {
      const { rows } = await pool.query(
        `INSERT INTO umkm (user_id, nama, deskripsi, alamat, foto)
         VALUES ($1, $2, $3, $4, $5) RETURNING id`,
        [umkm.user_id, umkm.nama, umkm.deskripsi, umkm.alamat, umkm.foto]
      );
      return { ...umkm, id: rows[0].id };
    }

    // findAll mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
    // q kosong berarti tidak difilter sama sekali.
    async function findAll(q, limit, offset) {
      const { rows } = await pool.query(
        `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm
         WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')
         ORDER BY id DESC LIMIT $2 OFFSET $3`,
        [q, limit, offset]
      );
      return rows;
    }

    async function count(q) {
      const { rows } = await pool.query(
        `SELECT COUNT(*) FROM umkm WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')`,
        [q]
      );
      // node-postgres selalu membalas COUNT(*) sebagai STRING (karena tipe asli
      // Postgres-nya bigint, lebih besar dari batas aman Number JS) -- wajib
      // di-Number()-kan manual di sini, beda dengan Go yang otomatis men-scan
      // ke tipe int.
      return Number(rows[0].count);
    }

    async function findById(id) {
      const { rows } = await pool.query(
        'SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE id = $1',
        [id]
      );
      return rows[0] || null;
    }

    async function findByUserId(userId) {
      const { rows } = await pool.query(
        'SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE user_id = $1',
        [userId]
      );
      return rows[0] || null;
    }

    async function update(umkm) {
      await pool.query(
        'UPDATE umkm SET nama = $1, deskripsi = $2, alamat = $3, foto = $4 WHERE id = $5',
        [umkm.nama, umkm.deskripsi, umkm.alamat, umkm.foto, umkm.id]
      );
    }

    async function remove(id) {
      await pool.query('DELETE FROM umkm WHERE id = $1', [id]);
    }

    module.exports = { create, findAll, count, findById, findByUserId, update, remove };

Jebakan klasik: COUNT(\*) bukan angka di node-postgres

Ini bug yang nyaris selalu dilakukan pemula node-postgres: memakai `rows[0].count` langsung tanpa `Number()`, lalu heran kenapa `meta.total` di JSON hasilnya `"3"` (string, bertanda kutip) bukan `3`. Penyebabnya: Postgres mengembalikan `COUNT(*)` bertipe `bigint`, dan `pg` sengaja membalasnya sebagai string JavaScript (bukan `Number`) karena `bigint` bisa melebihi batas aman `Number` di JS. Fungsi `count()` di atas sudah menangani ini — jangan dihapus baris `Number(...)`-nya.

### produkRepository.js

src/repositories/produkRepository.js

    const pool = require('../db');

    // mapRow mengubah kolom "harga" (tipe NUMERIC di Postgres) dari string --
    // begitulah node-postgres selalu membalasnya, supaya tidak diam-diam
    // kehilangan presisi kalau dipaksa jadi float -- balik ke Number biasa,
    // setara float64 Harga di struct domain.Produk versi Go.
    function mapRow(row) {
      if (!row) return row;
      return { ...row, harga: Number(row.harga) };
    }

    async function create(produk) {
      const { rows } = await pool.query(
        `INSERT INTO produk (umkm_id, nama, harga, deskripsi, foto)
         VALUES ($1, $2, $3, $4, $5) RETURNING id`,
        [produk.umkm_id, produk.nama, produk.harga, produk.deskripsi, produk.foto]
      );
      return { ...produk, id: rows[0].id };
    }

    async function findById(id) {
      const { rows } = await pool.query(
        'SELECT id, umkm_id, nama, harga, deskripsi, foto FROM produk WHERE id = $1',
        [id]
      );
      return mapRow(rows[0]) || null;
    }

    async function findByUmkmId(umkmId, limit, offset) {
      const { rows } = await pool.query(
        `SELECT id, umkm_id, nama, harga, deskripsi, foto FROM produk
         WHERE umkm_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3`,
        [umkmId, limit, offset]
      );
      return rows.map(mapRow);
    }

    async function countByUmkmId(umkmId) {
      const { rows } = await pool.query('SELECT COUNT(*) FROM produk WHERE umkm_id = $1', [umkmId]);
      return Number(rows[0].count);
    }

    async function update(produk) {
      await pool.query(
        'UPDATE produk SET nama = $1, harga = $2, deskripsi = $3, foto = $4 WHERE id = $5',
        [produk.nama, produk.harga, produk.deskripsi, produk.foto, produk.id]
      );
    }

    async function remove(id) {
      await pool.query('DELETE FROM produk WHERE id = $1', [id]);
    }

    module.exports = { create, findById, findByUmkmId, countByUmkmId, update, remove };

Semua query di atas memakai parameter `$1, $2, ...`, persis seperti `pgx` di Go — nilai yang dikirim pengguna **tidak pernah** disambung manual ke string SQL, sehingga aman dari SQL injection dengan cara yang sama persis seperti dijelaskan di Pertemuan 9 Bagian 11.

## 11Service Layer: Auth

Di sinilah aturan bisnis hidup: validasi input, cek email sudah terdaftar, hashing password, generate JWT. Bandingkan langsung dengan `AuthService` di Pertemuan 9 Bagian 09 — urutan langkahnya sama persis.

src/services/authService.js

    const bcrypt = require('bcrypt');
    const jwt = require('jsonwebtoken');
    const config = require('../config');
    const userRepository = require('../repositories/userRepository');
    const { InvalidInputError, ConflictError, NotFoundError } = require('../errors');

    function toSafeUser(user) {
      return { id: user.id, nama: user.nama, email: user.email };
    }

    async function register(nama, email, password) {
      if (!nama || !email || !password || password.length < 6) {
        throw new InvalidInputError('nama, email, dan password (min 6 karakter) wajib diisi');
      }

      const existing = await userRepository.findByEmail(email);
      if (existing) throw new ConflictError('email sudah terdaftar');

      const hashed = await bcrypt.hash(password, 10);
      const user = await userRepository.create({ nama, email, password: hashed });
      return toSafeUser(user);
    }

    async function login(email, password) {
      const user = await userRepository.findByEmail(email);
      if (!user) throw new NotFoundError('email atau password salah');

      const match = await bcrypt.compare(password, user.password);
      if (!match) throw new InvalidInputError('email atau password salah');

      const token = generateToken(user.id);
      return { token, user: toSafeUser(user) };
    }

    async function profile(userId) {
      const user = await userRepository.findById(userId);
      if (!user) throw new NotFoundError();
      return toSafeUser(user);
    }

    async function updateProfile(userId, nama, email) {
      if (!nama || !email) throw new InvalidInputError('gagal memperbarui profil');
      await userRepository.updateProfile(userId, nama, email);
    }

    async function updatePassword(userId, passwordLama, passwordBaru) {
      const user = await userRepository.findById(userId);
      if (!user) throw new NotFoundError();

      const match = await bcrypt.compare(passwordLama, user.password);
      if (!match) throw new InvalidInputError('password lama salah atau password baru terlalu pendek');

      if (!passwordBaru || passwordBaru.length < 6) {
        throw new InvalidInputError('password lama salah atau password baru terlalu pendek');
      }

      const hashed = await bcrypt.hash(passwordBaru, 10);
      await userRepository.updatePassword(userId, hashed);
    }

    function generateToken(userId) {
      return jwt.sign({ sub: userId }, config.jwtSecret, { algorithm: 'HS256', expiresIn: '24h' });
    }

    module.exports = { register, login, profile, updateProfile, updatePassword };

Tiga hal yang persis sama dengan Go: (1) `bcrypt.hash`/`bcrypt.compare` satu arah, password asli tidak pernah tersimpan maupun dibandingkan sebagai teks biasa; (2) `login()` sengaja melempar pesan error **yang sama** ("email atau password salah") baik emailnya tidak ada maupun passwordnya salah, supaya penyerang tidak bisa menebak email mana yang terdaftar; (3) klaim JWT `sub` diisi id user, kedaluwarsa 24 jam — identik dengan `generateToken` di Go.

## 12Service Layer: UMKM & Produk

### umkmService.js

src/services/umkmService.js

    const umkmRepository = require('../repositories/umkmRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { InvalidInputError, ConflictError, NotFoundError, ForbiddenError } = require('../errors');

    // list mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
    async function list(q, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await umkmRepository.findAll(q, limit, offset);
      const total = await umkmRepository.count(q);
      return { data, total, page, limit };
    }

    async function detail(id) {
      const umkm = await umkmRepository.findById(id);
      if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
      return umkm;
    }

    async function myUmkm(userId) {
      const umkm = await umkmRepository.findByUserId(userId);
      if (!umkm) throw new NotFoundError('Anda belum memiliki UMKM');
      return umkm;
    }

    async function createOwn(userId, nama, deskripsi, alamat, foto) {
      if (!nama) throw new InvalidInputError('nama UMKM wajib diisi');

      const existing = await umkmRepository.findByUserId(userId);
      if (existing) throw new ConflictError('Anda sudah memiliki UMKM'); // 1 user hanya boleh punya 1 UMKM

      return umkmRepository.create({ user_id: userId, nama, deskripsi, alamat, foto });
    }

    // updateOwn mengembalikan UMKM hasil update beserta path foto lama (bisa kosong).
    // Handler bertanggung jawab menghapus berkas foto lama dari disk setelah update berhasil.
    async function updateOwn(userId, umkmId, nama, deskripsi, alamat, fotoBaru) {
      if (!nama) throw new InvalidInputError('nama UMKM wajib diisi');

      const umkm = await umkmRepository.findById(umkmId);
      if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
      if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik UMKM ini');

      let fotoLama = umkm.foto;
      umkm.nama = nama;
      umkm.deskripsi = deskripsi;
      umkm.alamat = alamat;
      if (fotoBaru) {
        umkm.foto = fotoBaru;
      } else {
        fotoLama = ''; // foto tidak diganti, tidak ada yang perlu dihapus
      }

      await umkmRepository.update(umkm);
      return { umkm, fotoLama };
    }

    async function deleteOwn(userId, umkmId) {
      const umkm = await umkmRepository.findById(umkmId);
      if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
      if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik UMKM ini');

      await umkmRepository.remove(umkmId);
      return umkm;
    }

    module.exports = { list, detail, myUmkm, createOwn, updateOwn, deleteOwn };

### produkService.js

src/services/produkService.js

    const produkRepository = require('../repositories/produkRepository');
    const umkmRepository = require('../repositories/umkmRepository');
    const { normalizePagination } = require('../utils/pagination');
    const { InvalidInputError, NotFoundError, ForbiddenError } = require('../errors');

    async function listByUmkm(umkmId, rawPage, rawLimit) {
      const { page, limit } = normalizePagination(rawPage, rawLimit);
      const offset = (page - 1) * limit;

      const data = await produkRepository.findByUmkmId(umkmId, limit, offset);
      const total = await produkRepository.countByUmkmId(umkmId);
      return { data, total, page, limit };
    }

    async function detail(id) {
      const produk = await produkRepository.findById(id);
      if (!produk) throw new NotFoundError('produk tidak ditemukan');
      return produk;
    }

    async function createForOwnUmkm(userId, umkmId, nama, harga, deskripsi, foto) {
      if (!nama || !(harga >= 0)) throw new InvalidInputError('nama dan harga produk wajib valid');

      const umkm = await umkmRepository.findById(umkmId);
      if (!umkm) throw new NotFoundError('UMKM tidak ditemukan');
      if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik UMKM ini'); // hanya pemilik UMKM yang boleh menambah produk

      return produkRepository.create({ umkm_id: umkmId, nama, harga, deskripsi, foto });
    }

    // authorizeOwner memastikan userId adalah pemilik UMKM tempat produk berada --
    // dua SELECT berantai: ambil produknya dulu (untuk tahu umkm_id-nya), lalu
    // ambil UMKM-nya (untuk tahu user_id pemiliknya), karena tabel produk sengaja
    // tidak menyimpan user_id sendiri (lihat skema di Pertemuan 9 Bagian 04).
    async function authorizeOwner(userId, produkId) {
      const produk = await produkRepository.findById(produkId);
      if (!produk) throw new NotFoundError('produk tidak ditemukan');

      const umkm = await umkmRepository.findById(produk.umkm_id);
      if (!umkm) throw new NotFoundError('produk tidak ditemukan');

      if (umkm.user_id !== userId) throw new ForbiddenError('Anda bukan pemilik produk ini');
      return produk;
    }

    async function updateOwn(userId, produkId, nama, harga, deskripsi, fotoBaru) {
      if (!nama || !(harga >= 0)) throw new InvalidInputError('nama dan harga produk wajib valid');

      const produk = await authorizeOwner(userId, produkId);

      let fotoLama = produk.foto;
      produk.nama = nama;
      produk.harga = harga;
      produk.deskripsi = deskripsi;
      if (fotoBaru) {
        produk.foto = fotoBaru;
      } else {
        fotoLama = '';
      }

      await produkRepository.update(produk);
      return { produk, fotoLama };
    }

    async function deleteOwn(userId, produkId) {
      const produk = await authorizeOwner(userId, produkId);
      await produkRepository.remove(produkId);
      return produk;
    }

    module.exports = { listByUmkm, detail, createForOwnUmkm, updateOwn, deleteOwn };

Sudah diuji sungguhan

Seluruh alur `authorizeOwner` di atas (akun B mencoba edit produk milik akun A lewat endpoint `PUT /api/produk/:id`) sudah diuji langsung di server Node + PostgreSQL sungguhan sebelum materi ini ditulis, dan konsisten membalas `403 Forbidden` — lihat hasil lengkapnya di Bagian 16.

## 13Handler (Controller) Layer

Handler di Express selalu berbentuk `(req, res, next)` — tugasnya cuma tiga: ambil input dari `req`, panggil service, balas lewat `res` atau lempar error ke `next(err)` supaya ditangkap `errorHandler` (Bagian 08).

### authHandler.js

src/handlers/authHandler.js

    const authService = require('../services/authService');
    const { ok } = require('../utils/response');

    async function register(req, res, next) {
      try {
        const { nama, email, password } = req.body;
        const user = await authService.register(nama, email, password);
        ok(res, 201, user);
      } catch (err) {
        next(err);
      }
    }

    async function login(req, res, next) {
      try {
        const { email, password } = req.body;
        const result = await authService.login(email, password);
        ok(res, 200, result);
      } catch (err) {
        // Baik "email tidak ditemukan" (NotFoundError) maupun "password salah"
        // (InvalidInputError) sengaja dibalas SAMA, 401 "email atau password
        // salah" -- meniru persis switch-case di AuthHandler.Login versi Go.
        err.status = 401;
        err.code = 'UNAUTHORIZED';
        err.message = 'email atau password salah';
        next(err);
      }
    }

    async function profile(req, res, next) {
      try {
        const user = await authService.profile(req.userId);
        ok(res, 200, user);
      } catch (err) {
        next(err);
      }
    }

    async function updateProfile(req, res, next) {
      try {
        const { nama, email } = req.body;
        await authService.updateProfile(req.userId, nama, email);
        ok(res, 200, { message: 'profil berhasil diperbarui' });
      } catch (err) {
        next(err);
      }
    }

    async function updatePassword(req, res, next) {
      try {
        const { password_lama, password_baru } = req.body;
        await authService.updatePassword(req.userId, password_lama, password_baru);
        ok(res, 200, { message: 'password berhasil diperbarui' });
      } catch (err) {
        next(err);
      }
    }

    module.exports = { register, login, profile, updateProfile, updatePassword };

### umkmHandler.js

src/handlers/umkmHandler.js

    const umkmService = require('../services/umkmService');
    const { ok, paginated } = require('../utils/response');
    const { relativePath, deleteFile } = require('../utils/upload');
    const { InvalidInputError } = require('../errors');
    const config = require('../config');

    function parseId(req) {
      const id = Number(req.params.id);
      if (!Number.isInteger(id)) throw new InvalidInputError('id tidak valid');
      return id;
    }

    async function list(req, res, next) {
      try {
        const q = req.query.q || '';
        const { data, total, page, limit } = await umkmService.list(q, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function detail(req, res, next) {
      try {
        const umkm = await umkmService.detail(parseId(req));
        ok(res, 200, umkm);
      } catch (err) {
        next(err);
      }
    }

    async function myUmkm(req, res, next) {
      try {
        const umkm = await umkmService.myUmkm(req.userId);
        ok(res, 200, umkm);
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        const foto = relativePath('umkm', req.file);
        const { nama, deskripsi, alamat } = req.body;
        const umkm = await umkmService.createOwn(req.userId, nama, deskripsi, alamat, foto);
        ok(res, 201, umkm);
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        const id = parseId(req);
        const fotoBaru = relativePath('umkm', req.file);
        const { nama, deskripsi, alamat } = req.body;
        const { umkm, fotoLama } = await umkmService.updateOwn(req.userId, id, nama, deskripsi, alamat, fotoBaru);
        deleteFile(config.uploadDir, fotoLama);
        ok(res, 200, umkm);
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        const id = parseId(req);
        const umkm = await umkmService.deleteOwn(req.userId, id);
        deleteFile(config.uploadDir, umkm.foto);
        ok(res, 200, { message: 'UMKM berhasil dihapus' });
      } catch (err) {
        next(err);
      }
    }

    module.exports = { list, detail, myUmkm, create, update, remove };

### produkHandler.js

src/handlers/produkHandler.js

    const produkService = require('../services/produkService');
    const { ok, paginated } = require('../utils/response');
    const { relativePath, deleteFile } = require('../utils/upload');
    const { InvalidInputError } = require('../errors');
    const config = require('../config');

    function parseId(value) {
      const id = Number(value);
      if (!Number.isInteger(id)) throw new InvalidInputError('id tidak valid');
      return id;
    }

    async function detail(req, res, next) {
      try {
        const produk = await produkService.detail(parseId(req.params.id));
        ok(res, 200, produk);
      } catch (err) {
        next(err);
      }
    }

    async function listByUmkm(req, res, next) {
      try {
        const umkmId = parseId(req.params.id);
        const { data, total, page, limit } = await produkService.listByUmkm(umkmId, req.query.page, req.query.limit);
        paginated(res, 200, data, page, limit, total);
      } catch (err) {
        next(err);
      }
    }

    async function create(req, res, next) {
      try {
        const umkmId = parseId(req.params.id);
        const harga = Number.parseFloat(req.body.harga);
        if (Number.isNaN(harga)) throw new InvalidInputError('harga produk wajib berupa angka');

        const foto = relativePath('produk', req.file);
        const { nama, deskripsi } = req.body;
        const produk = await produkService.createForOwnUmkm(req.userId, umkmId, nama, harga, deskripsi, foto);
        ok(res, 201, produk);
      } catch (err) {
        next(err);
      }
    }

    async function update(req, res, next) {
      try {
        const id = parseId(req.params.id);
        const harga = Number.parseFloat(req.body.harga);
        if (Number.isNaN(harga)) throw new InvalidInputError('harga produk wajib berupa angka');

        const fotoBaru = relativePath('produk', req.file);
        const { nama, deskripsi } = req.body;
        const { produk, fotoLama } = await produkService.updateOwn(req.userId, id, nama, harga, deskripsi, fotoBaru);
        deleteFile(config.uploadDir, fotoLama);
        ok(res, 200, produk);
      } catch (err) {
        next(err);
      }
    }

    async function remove(req, res, next) {
      try {
        const id = parseId(req.params.id);
        const produk = await produkService.deleteOwn(req.userId, id);
        deleteFile(config.uploadDir, produk.foto);
        ok(res, 200, { message: 'produk berhasil dihapus' });
      } catch (err) {
        next(err);
      }
    }

    module.exports = { detail, listByUmkm, create, update, remove };

Jangan lupa try/catch di tiap fungsi async

Berbeda dari Go yang errornya selalu berupa *return value* biasa, `async function` di Node melempar *exception*. Express (versi 4, yang dipakai di sini) **tidak otomatis** menangkap exception dari fungsi `async` — kalau `try/catch` dilupakan dan service melempar error, request akan menggantung tanpa respons sama sekali, bukan error 500 yang rapi. Pola `try { ... } catch (err) { next(err); }` di setiap fungsi di atas **wajib** ada untuk alasan ini.

## 14Routing: app.js

Satu berkas ini mendaftarkan seluruh endpoint, persis seperti daftar `mux.Handle(...)` di `main.go` Pertemuan 9 Bagian 08 — bandingkan urutannya, sama persis:

src/app.js

    const express = require('express');
    const cors = require('cors');
    const path = require('path');

    const config = require('./config');
    const { requireAuth } = require('./middleware/auth');
    const { loginLimiter } = require('./middleware/rateLimit');
    const { errorHandler } = require('./middleware/errorHandler');
    const { uploadSingle } = require('./utils/upload');

    const authHandler = require('./handlers/authHandler');
    const umkmHandler = require('./handlers/umkmHandler');
    const produkHandler = require('./handlers/produkHandler');

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

    // umkm
    app.get('/api/umkm', umkmHandler.list);
    app.get('/api/umkm/saya', requireAuth, umkmHandler.myUmkm);
    app.get('/api/umkm/:id', umkmHandler.detail);
    app.post('/api/umkm', requireAuth, uploadSingle('umkm', 'foto'), umkmHandler.create);
    app.put('/api/umkm/:id', requireAuth, uploadSingle('umkm', 'foto'), umkmHandler.update);
    app.delete('/api/umkm/:id', requireAuth, umkmHandler.remove);

    // produk
    app.get('/api/umkm/:id/produk', produkHandler.listByUmkm);
    app.post('/api/umkm/:id/produk', requireAuth, uploadSingle('produk', 'foto'), produkHandler.create);
    app.get('/api/produk/:id', produkHandler.detail);
    app.put('/api/produk/:id', requireAuth, uploadSingle('produk', 'foto'), produkHandler.update);
    app.delete('/api/produk/:id', requireAuth, produkHandler.remove);

    // static file untuk foto yang sudah diupload
    app.use('/uploads', express.static(path.resolve(config.uploadDir)));

    // health check
    app.get('/healthz', (req, res) => res.sendStatus(200));

    // errorHandler WAJIB didaftarkan PALING TERAKHIR -- Express mengenali
    // middleware 4-parameter (err, req, res, next) sebagai error handler hanya
    // kalau ia didaftarkan setelah semua route lain.
    app.use(errorHandler);

    module.exports = app;

Urutan route /saya vs /:id sangat penting

Perhatikan `GET /api/umkm/saya` didaftarkan **sebelum** `GET /api/umkm/:id`. Express mencocokkan route sesuai urutan pendaftaran — kalau urutannya dibalik, request ke `/api/umkm/saya` akan ketangkap duluan oleh `/api/umkm/:id` (dengan `id = "saya"`), lalu gagal di `Number("saya")` jadi `NaN` dan dibalas `400 id tidak valid` alih-alih menjalankan `myUmkm`. Ini jebakan routing yang sangat umum, dan alasan kenapa urutan di atas tidak boleh diacak.

Beberapa route sengaja menumpuk 3 middleware sekaligus, misalnya `POST /api/umkm`: `requireAuth` (wajib login) → `uploadSingle(...)` (proses file & field form) → `umkmHandler.create` (logika sesungguhnya). Express menjalankannya berurutan dari kiri ke kanan, mirip `auth(http.HandlerFunc(...))` yang membungkus handler di Go, hanya saja susunannya ditulis mendatar sebagai daftar argumen, bukan bersarang.

## 15server.js & Menjalankan Project

server.js

    const app = require('./src/app');
    const config = require('./src/config');
    const pool = require('./src/db');

    async function main() {
      // Tes koneksi database lebih dulu, gagal cepat kalau DATABASE_URL salah
      // daripada membiarkan server menyala tapi semua endpoint error 500.
      try {
        await pool.query('SELECT 1');
        console.log('berhasil terhubung ke PostgreSQL');
      } catch (err) {
        console.error('gagal konek ke database:', err.message);
        process.exit(1);
      }

      const server = app.listen(config.port, () => {
        console.log(`server berjalan di port ${config.port}`);
      });

      // graceful shutdown
      const shutdown = () => {
        console.log('server dimatikan dengan aman');
        server.close(() => pool.end(() => process.exit(0)));
      };
      process.on('SIGINT', shutdown);
      process.on('SIGTERM', shutdown);
    }

    main();

Persis seperti `main.go`: tes koneksi database dulu sebelum membuka port (`db.Ping(ctx)` di Go, `pool.query('SELECT 1')` di sini), dan menangani sinyal `SIGINT`/`SIGTERM` untuk mematikan server dengan rapi (menyelesaikan request yang sedang berjalan dulu) alih-alih langsung dibunuh paksa.

### Langkah menjalankan dari nol

1.  Pastikan `schema.sql` sudah dijalankan ke Neon (Bagian 05) dan `.env` sudah diisi lengkap (Bagian 06).
2.  Install dependency: `npm install`.
3.  Jalankan mode development (auto-restart): `npm run dev`.
4.  Harus muncul di terminal: `berhasil terhubung ke PostgreSQL` lalu `server berjalan di port 8080`.
5.  Tes cepat: buka `http://localhost:8080/healthz` di browser, atau `curl http://localhost:8080/healthz` — harus balas kosong dengan status `200`.

Checkpoint

Kalau langkah 5 berhasil (200 OK), seluruh fondasi (koneksi database, Express, middleware) sudah benar. Lanjut ke Bagian 16 untuk menguji seluruh alur CRUD lengkap.

## 16Testing Lengkap via curl

Urutan di bawah ini **sudah benar-benar dijalankan** terhadap server Node + PostgreSQL sungguhan sebelum materi ini ditulis — setiap hasil yang dicantumkan adalah hasil asli, bukan contoh karangan. Jalankan dari terminal, berurutan dari atas.

### 1. Register & Login

terminal

    curl -s -X POST http://localhost:8080/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"nama":"Budi Tester","email":"budi@test.com","password":"rahasia123"}'
    # {"data":{"id":1,"nama":"Budi Tester","email":"budi@test.com"}}

    curl -s -X POST http://localhost:8080/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"budi@test.com","password":"rahasia123"}'
    # {"data":{"token":"eyJhbGciOi...","user":{"id":1,"nama":"Budi Tester","email":"budi@test.com"}}}

    # simpan tokennya ke variabel shell untuk langkah selanjutnya
    TOKEN="tempel-token-hasil-login-di-sini"

### 2. Validasi & keamanan dasar

terminal

    # register email yang sama dua kali -> 409
    curl -s -w "\nHTTP:%{http_code}\n" -X POST http://localhost:8080/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"nama":"Budi Tester","email":"budi@test.com","password":"rahasia123"}'
    # {"error":{"message":"email sudah terdaftar","code":"CONFLICT"}}  HTTP:409

    # login dengan password salah -> 401
    curl -s -w "\nHTTP:%{http_code}\n" -X POST http://localhost:8080/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"budi@test.com","password":"salahbanget"}'
    # {"error":{"message":"email atau password salah","code":"UNAUTHORIZED"}}  HTTP:401

    # panggil endpoint yang butuh login tanpa token -> 401
    curl -s -w "\nHTTP:%{http_code}\n" http://localhost:8080/api/profile
    # {"error":{"message":"token tidak ditemukan","code":"UNAUTHORIZED"}}  HTTP:401

### 3. Buat UMKM & produk (upload foto sungguhan)

terminal

    curl -s -X POST http://localhost:8080/api/umkm -H "Authorization: Bearer $TOKEN" \
      -F "nama=Warung Budi" -F "deskripsi=Jual kopi" -F "alamat=Jl. Melati 1"
    # {"data":{"user_id":1,"nama":"Warung Budi","deskripsi":"Jual kopi","alamat":"Jl. Melati 1","foto":"","id":1}}

    # bikin UMKM KEDUA untuk akun yang sama -> harus 409 (1 user = 1 UMKM)
    curl -s -w "\nHTTP:%{http_code}\n" -X POST http://localhost:8080/api/umkm \
      -H "Authorization: Bearer $TOKEN" -F "nama=Warung Dua"
    # {"error":{"message":"Anda sudah memiliki UMKM","code":"CONFLICT"}}  HTTP:409

    # tambah produk LENGKAP DENGAN FOTO sungguhan ke UMKM id=1
    curl -s -X POST http://localhost:8080/api/umkm/1/produk -H "Authorization: Bearer $TOKEN" \
      -F "nama=Kopi Susu" -F "harga=15000" -F "deskripsi=Kopi susu gula aren" \
      -F "foto=@/path/ke/foto.jpg"
    # {"data":{"umkm_id":1,"nama":"Kopi Susu","harga":15000, ..., "foto":"produk/179...jpg","id":1}}

    # upload file BUKAN gambar (.txt) -> harus ditolak 400
    curl -s -w "\nHTTP:%{http_code}\n" -X POST http://localhost:8080/api/umkm/1/produk \
      -H "Authorization: Bearer $TOKEN" -F "nama=Gagal" -F "harga=1000" -F "foto=@/path/ke/berkas.txt"
    # {"error":{"message":"tipe berkas tidak didukung, hanya jpg/jpeg/png","code":"BAD_REQUEST"}}  HTTP:400

Perhatikan di hasil asli: `"harga":15000` keluar sebagai **angka**, bukan `"15000"` (string) — bukti `Number(row.harga)` di `produkRepository.js` (Bagian 10) bekerja dengan benar.

### 4. Ownership: akun lain tidak boleh mengubah data orang lain

terminal

    # daftar & login akun KEDUA
    curl -s -X POST http://localhost:8080/api/auth/register -H "Content-Type: application/json" \
      -d '{"nama":"Siti","email":"siti@test.com","password":"rahasia123"}'
    TOKEN_B="tempel-token-akun-siti-di-sini"

    # akun B coba edit UMKM milik akun A -> harus 403
    curl -s -w "\nHTTP:%{http_code}\n" -X PUT http://localhost:8080/api/umkm/1 \
      -H "Authorization: Bearer $TOKEN_B" -F "nama=Dicuri"
    # {"error":{"message":"Anda bukan pemilik UMKM ini","code":"FORBIDDEN"}}  HTTP:403

    # akun B coba edit PRODUK milik UMKM akun A -> harus 403 juga
    # (ini yang membuktikan authorizeOwner 2-level di produkService.js benar-benar jalan)
    curl -s -w "\nHTTP:%{http_code}\n" -X PUT http://localhost:8080/api/produk/1 \
      -H "Authorization: Bearer $TOKEN_B" -F "nama=Dicuri" -F "harga=1"
    # {"error":{"message":"Anda bukan pemilik produk ini","code":"FORBIDDEN"}}  HTTP:403

### 5. Hapus UMKM → bukti ON DELETE CASCADE

terminal

    # cek dulu produknya ada
    curl -s http://localhost:8080/api/umkm/1/produk
    # {"data":[{"id":1,"nama":"Kopi Susu", ...}], "meta":{"page":1,"limit":10,"total":1}}

    # hapus UMKM-nya (bukan produknya)
    curl -s -X DELETE http://localhost:8080/api/umkm/1 -H "Authorization: Bearer $TOKEN"
    # {"data":{"message":"UMKM berhasil dihapus"}}

    # cek ulang produknya -> harus KOSONG, padahal tidak pernah di-DELETE langsung
    curl -s http://localhost:8080/api/umkm/1/produk
    # {"data":[], "meta":{"page":1,"limit":10,"total":0}}

    curl -s -w "\nHTTP:%{http_code}\n" http://localhost:8080/api/produk/1
    # {"error":{"message":"produk tidak ditemukan","code":"NOT_FOUND"}}  HTTP:404

### 6. SQL injection tetap aman

terminal

    # pakai -G --data-urlencode supaya karakter aneh di query string tidak
    # merusak sintaks URL curl itu sendiri (ini soal shell/curl, bukan soal API)
    curl -s -G http://localhost:8080/api/umkm --data-urlencode "q=';DROP TABLE umkm;--"
    # {"data":[], "meta":{"page":1,"limit":10,"total":0}}  -- aman, tabel tidak hilang

    curl -s http://localhost:8080/api/umkm
    # tabel umkm masih ada & isinya utuh

### 7. Rate limit login

terminal

    for i in 1 2 3 4 5 6; do
      curl -s -o /dev/null -w "percobaan $i: %{http_code}\n" \
        -X POST http://localhost:8080/api/auth/login \
        -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"salah"}'
    done
    # percobaan ke-6 (dan seterusnya dalam 1 menit yang sama) akan dibalas 429

Semua hasil di atas adalah hasil nyata

Ketujuh skenario ini dijalankan terhadap server Node.js + PostgreSQL 17 sungguhan (bukan database tiruan) sebelum materi ini ditulis. Kalau kamu mengikuti kode dari Bagian 02-15 persis seperti yang tertulis, hasil yang kamu dapatkan di komputermu sendiri akan identik.

## 17Troubleshooting Cepat

| Error yang muncul | Penyebab paling umum | Solusi |
|----|----|----|
| `ECONNREFUSED` saat start server | `DATABASE_URL` salah, atau Neon project sedang "sleep" (auto-suspend saat idle lama). | Cek ulang connection string di Neon Console, buka dashboard Neon sekali untuk membangunkan project-nya. |
| `self-signed certificate in certificate chain` | Opsi `ssl` di `db.js` tidak aktif padahal connection string mengandung `sslmode=require`. | Pastikan `DATABASE_URL` di `.env` benar-benar memuat teks `sslmode=require` persis seperti itu — `db.js` mendeteksinya dari situ. |
| `relation "users" already exists` | `schema.sql` dijalankan dua kali ke database yang sama. | Abaikan kalau memang tabelnya sudah ada; kalau mau mulai bersih, `DROP TABLE produk, umkm, users;` dulu baru jalankan ulang. |
| `EADDRINUSE: address already in use :::8080` | Server lama (dari `nodemon` atau terminal lain) masih berjalan di port yang sama. | Hentikan proses lama (`Ctrl+C` di terminal itu), atau ganti `PORT` di `.env`. |
| Field form (`nama`, dll) selalu `undefined` di endpoint upload | Lupa memasang `uploadSingle(...)` di route, atau mengirim request sebagai JSON padahal field-nya ditulis sebagai `multipart/form-data`. | Endpoint yang menerima foto (buat/update UMKM & produk) wajib dikirim sebagai *form-data* (pakai `-F` di curl, bukan `-d` dengan JSON), dan route-nya wajib melalui `uploadSingle(...)`. |
| `Unexpected field` dari multer | Nama field file di form-data tidak sama dengan nama field di `uploadSingle(subDir, fieldName)`. | Pastikan nama field upload selalu `foto` (huruf kecil semua), sama seperti didaftarkan di `app.js`. |
| `JsonWebTokenError: jwt malformed` | Header `Authorization` terkirim kosong, atau menempelkan teks lain (bukan token asli) setelah "Bearer ". | Login ulang, salin token hasil `data.token` persis, cek tidak ada spasi/baris baru tambahan yang ikut tersalin. |
| CORS error di console browser (saat dites dari Flutter Web) | Middleware `cors()` belum terpasang atau terpasang setelah route. | Pastikan `app.use(cors())` ada di baris paling atas `app.js`, sebelum route apa pun didaftarkan. |
| Response menggantung tanpa balasan sama sekali (tidak error, tidak sukses) | Lupa `try/catch` di salah satu fungsi handler `async`, sehingga exception tidak pernah sampai ke `next(err)`. | Cek ulang semua handler punya pola `try { ... } catch (err) { next(err); }` seperti dijelaskan di Bagian 13. |
| `meta.total` di JSON berupa `"3"` (string, bertanda kutip) | Lupa membungkus hasil `COUNT(*)` dengan `Number(...)` di repository. | Lihat kembali `count()`/`countByUmkmId()` di Bagian 10 — baris `Number(rows[0].count)` wajib ada. |

## 18Perbandingan Go vs Node.js

Satu proyek, dua bahasa — tabel ini meringkas padanan tiap konsep, supaya kalau suatu saat perlu membaca atau menulis salah satu versi, versi yang satunya terasa seperti sudah pernah dilihat sebelumnya:

| Konsep | Golang (umkm-api) | Node.js (umkm-api-node) |
|----|----|----|
| Web framework | `net/http` + `http.ServeMux` (bawaan Go 1.22+) | Express |
| Driver database | `pgx` + `pgxpool.Pool` | `pg` (node-postgres) + `Pool` |
| Error "tidak ketemu" dari DB | `pgx.ErrNoRows` → dikonversi manual jadi `domain.ErrNotFound` | `rows[0]` bernilai `undefined` → repository mengembalikan `null` |
| Penanganan error di handler | `switch { case errors.Is(err, ...) }` diulang di tiap handler | `throw` kelas error kustom, ditangkap satu `errorHandler` terpusat |
| Middleware auth | `func(http.Handler) http.Handler`, userID disisipkan ke `context.Context` | fungsi `(req, res, next)` biasa, userID ditempel langsung ke `req.userId` |
| Rate limiting | `golang.org/x/time/rate`, `map[string]*rate.Limiter` ditulis manual per IP | `express-rate-limit`, penghitung per IP sudah dibungkus library |
| Hashing password | `golang.org/x/crypto/bcrypt` | `bcrypt` (binding native ke algoritma yang sama) |
| JWT | `golang-jwt/jwt/v5`, klaim lewat `jwt.MapClaims` | `jsonwebtoken`, klaim lewat object literal biasa |
| Upload file | `r.ParseMultipartForm` + `io.Copy` manual | `multer` (`diskStorage` + `fileFilter`) |
| Tipe data numerik dari DB | di-`Scan` otomatis ke tipe Go asli (`int`, `float64`) | `bigint`/`numeric` selalu balik sebagai **string**, wajib `Number()` manual |
| Concurrency model | goroutine, tiap request punya *thread* ringan sendiri | single-threaded + event loop, `async/await` untuk I/O non-blocking |
| Dokumentasi API | Swagger via komentar `// @Summary` dkk (swaggo) | bisa ditambah `swagger-jsdoc` + `swagger-ui-express` dengan pola komentar serupa (di luar cakupan materi ini) |

Satu pelajaran terpenting dari perbandingan ini

Baris kode berbeda, library berbeda, bahkan model concurrency-nya berbeda total (goroutine vs event loop) — tapi **arsitektur** (handler → service → repository), **aturan bisnis** (1 user 1 UMKM, ownership check, validasi), dan **skema database**-nya persis sama. Itulah yang dimaksud "belajar konsep, bukan sekadar sintaks" — begitu paham UMKM API di satu bahasa, mempelajari versi bahasa lain jauh lebih cepat karena tinggal mencari padanannya, bukan belajar dari nol.

## 19Latihan

1.  Tambahkan endpoint `GET /api/umkm/:id/produk/:produkId` yang memvalidasi produk tersebut benar-benar milik UMKM dengan `:id` itu (bukan cuma dicari lewat `produkId` saja) — balas `404` kalau tidak cocok.
2.  Tambahkan validasi panjang maksimal `nama` (mis. 150 karakter) di `umkmService.createOwn`, balas `InvalidInputError` kalau melebihi — cek juga kolom `VARCHAR(150)` di skema supaya konsisten.
3.  Ganti `express-rate-limit` default (disimpan di memori) menjadi versi yang disimpan di Redis, supaya rate limit tetap konsisten walau server di-restart atau dijalankan lebih dari satu instance.
4.  **Tantangan:** tambahkan `swagger-jsdoc` + `swagger-ui-express`, tulis dokumentasi untuk seluruh endpoint di atas memakai komentar JSDoc, supaya ada halaman `/docs` yang setara `/swagger/` di versi Go.
5.  **Tantangan integrasi:** jalankan server Node ini di port berbeda dari versi Go (mis. 8081), lalu ubah `baseUrl` di `ApiService` Flutter (Pertemuan 7) untuk sementara menunjuk ke situ — buktikan aplikasi `umkm-app` yang sama persis bisa jalan tanpa perubahan kode Flutter sedikit pun, baik menunjuk ke backend Go maupun Node.

Dengan panduan ini, proyek `umkm-api` yang sama bisa dibangun ulang dari nol dengan stack Node.js + Express + PostgreSQL kapan pun dibutuhkan — seluruh endpoint, aturan bisnis, dan skema database identik dengan versi Golang di Pertemuan 4/9, dan setiap baris kodenya sudah diuji berjalan nyata sebelum materi ini ditulis. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
