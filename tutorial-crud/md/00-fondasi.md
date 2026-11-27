[← Daftar tutorial project](index.md)

Langkah 1 · Sama untuk Semua

# Fondasi: Modul User untuk Semua Project

Satu fondasi yang sama untuk seluruh mahasiswa sebelum membuat CRUD project masing-masing.

## 01 Apa yang Dibuat

Fondasi ini adalah **modul user** dari Pertemuan 9a: register, login, profil, ubah password, dan Swagger. Semua project memakai fondasi yang **sama persis**. Setelah fondasi jalan, kamu menambahkan satu tabel milik project-mu lewat tutorial masing-masing.

Pahami dulu konsepnya di [Pertemuan 9a](../../pertemuan-09a.html). Halaman ini hanya berisi langkah dan kode.

Punya salinan repo materi?

Folder `tutorial-crud/starter/` berisi fondasi ini. Salin foldernya, ganti namanya, jalankan `npm install`, lalu lompat ke bagian 05.

## 02 Membuat Proyek & Install

Ganti `project-api` dengan nama folder untuk project-mu.

terminal

    mkdir project-api && cd project-api
    npm init -y

    npm install --save-exact @prisma/client@6.19.3 bcrypt@6.0.0 cors@2.8.6 dotenv@16.6.1 express@4.22.3 express-rate-limit@7.5.1 jsonwebtoken@9.0.3 swagger-ui-express@5.0.1
    npm install --save-exact --save-dev nodemon@3.1.11 prisma@6.19.3

terminal — buat folder

    mkdir -p prisma src/docs src/middleware src/utils src/repositories src/services src/handlers

Buka `package.json`, ubah `main` menjadi `server.js` dan isi bagian `scripts` seperti di bawah. Bagian dependency sudah terisi otomatis.

package.json

    {
      "name": "api-project",
      "version": "1.0.0",
      "description": "REST API project mahasiswa — Express + Prisma + PostgreSQL",
      "main": "server.js",
      "scripts": {
        "dev": "nodemon server.js",
        "start": "node server.js",
        "migrate": "prisma migrate deploy",
        "migrate:dev": "prisma migrate dev",
        "generate": "prisma generate",
        "studio": "prisma studio",
        "postinstall": "prisma generate"
      },
      "dependencies": {
        "@prisma/client": "6.19.3",
        "bcrypt": "6.0.0",
        "cors": "2.8.6",
        "dotenv": "16.6.1",
        "express": "4.22.3",
        "express-rate-limit": "7.5.1",
        "jsonwebtoken": "9.0.3",
        "swagger-ui-express": "5.0.1"
      },
      "devDependencies": {
        "nodemon": "3.1.11",
        "prisma": "6.19.3"
      }
    }

## 03 File Konfigurasi & Database

Penjelasan: [Pertemuan 9a Bagian 05](../../pertemuan-09a.html#s5) dan [Pertemuan 9a Bagian 06](../../pertemuan-09a.html#s6).

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

      @@map("users")
    }

.env.example

    DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
    JWT_SECRET=ganti-dengan-string-acak-yang-panjang
    PORT=8080

.gitignore

    node_modules/
    .env

src/config.js

    require('dotenv').config();

    function getOrDefault(key, def) {
      const v = process.env[key];
      return v && v !== '' ? v : def;
    }

    module.exports = {
      jwtSecret: process.env.JWT_SECRET,
      port: getOrDefault('PORT', '8080'),
    };

src/db.js

    const { PrismaClient } = require('@prisma/client');

    // Satu instance PrismaClient dipakai bersama seluruh aplikasi. PrismaClient
    // sudah mengelola connection pool sendiri, jadi JANGAN membuat instance baru
    // di tiap repository/request. Koneksi SSL untuk Neon otomatis ikut dari
    // "sslmode=require" di DATABASE_URL -- tidak perlu konfigurasi ssl manual.
    const prisma = new PrismaClient({
      log: ['warn', 'error'],
    });

    module.exports = prisma;

## 04 Kode Pendukung

Penjelasan: [Pertemuan 9a Bagian 07](../../pertemuan-09a.html#s7) sampai [Pertemuan 9a Bagian 08](../../pertemuan-09a.html#s8). File `validate.js` dan `docs/crud.js` disiapkan untuk CRUD project-mu.

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

src/utils/response.js

    function ok(res, status, data) {
      res.status(status).json({ data });
    }

    function paginated(res, status, data, page, limit, total) {
      res.status(status).json({ data, meta: { page, limit, total } });
    }

    module.exports = { ok, paginated };

src/utils/pagination.js

    const DEFAULT_LIMIT = 10;
    const MAX_LIMIT = 100;

    // normalizePagination memastikan page minimal 1 dan limit berada pada rentang wajar.
    // Dipanggil dengan nilai mentah dari query string (bertipe string atau undefined).
    function normalizePagination(rawPage, rawLimit) {
      let page = parseInt(rawPage, 10);
      let limit = parseInt(rawLimit, 10);

      if (!Number.isInteger(page) || page < 1) page = 1;
      if (!Number.isInteger(limit) || limit <= 0) limit = DEFAULT_LIMIT;
      if (limit > MAX_LIMIT) limit = MAX_LIMIT;

      return { page, limit };
    }

    module.exports = { normalizePagination };

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

src/middleware/auth.js

    const jwt = require('jsonwebtoken');
    const config = require('../config');

    // requireAuth membaca header Authorization, menerima baik "Bearer <token>"
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

src/middleware/errorHandler.js

    // errorHandler adalah satu-satunya tempat error diterjemahkan jadi response
    // JSON. Service/handler tinggal `throw` instance dari src/errors.js (atau
    // panggil next(err)), tidak perlu switch-case berulang di tiap endpoint
    // seperti pola errors.Is di versi Go -- karena di sini status HTTP & code
    // sudah menempel di objek error-nya sendiri (lihat AppError).
    function errorHandler(err, req, res, next) {
      // Body JSON yang rusak ditolak express.json() sebelum sampai ke handler.
      if (err.type === 'entity.parse.failed') {
        return res.status(400).json({ error: { message: 'body tidak valid', code: 'BAD_REQUEST' } });
      }

      if (err.status) {
        return res.status(err.status).json({ error: { message: err.message, code: err.code } });
      }

      console.error(err);
      res.status(500).json({ error: { message: 'kesalahan server', code: 'INTERNAL' } });
    }

    module.exports = { errorHandler };

## 05 Modul User

Penjelasan per fungsi: [Pertemuan 9a Bagian 10](../../pertemuan-09a.html#s10), [Pertemuan 9a Bagian 11](../../pertemuan-09a.html#s11), dan [Pertemuan 9a Bagian 13](../../pertemuan-09a.html#s13).

src/repositories/userRepository.js

    const prisma = require('../db');

    const userSelect = { id: true, nama: true, email: true, password: true };

    async function create(user) {
      return prisma.user.create({
        data: { nama: user.nama, email: user.email, password: user.password },
        select: userSelect,
      });
    }

    async function findByEmail(email) {
      return prisma.user.findUnique({ where: { email }, select: userSelect });
    }

    async function findById(id) {
      return prisma.user.findUnique({ where: { id }, select: userSelect });
    }

    async function updateProfile(id, nama, email) {
      await prisma.user.update({ where: { id }, data: { nama, email } });
    }

    async function updatePassword(id, hashedPassword) {
      await prisma.user.update({ where: { id }, data: { password: hashedPassword } });
    }

    module.exports = { create, findByEmail, findById, updateProfile, updatePassword };

src/services/authService.js

    const bcrypt = require('bcrypt');
    const jwt = require('jsonwebtoken');
    const config = require('../config');
    const userRepository = require('../repositories/userRepository');
    const { InvalidInputError, ConflictError, NotFoundError } = require('../errors');

    function toSafeUser(user) {
      return { id: user.id, nama: user.nama, email: user.email };
    }

    // Batas panjang mengikuti kolom di schema.prisma (VarChar 100 dan 150).
    const MAKS_NAMA = 100;
    const MAKS_EMAIL = 150;

    // isText: harus berupa teks yang tidak kosong. Body JSON bisa berisi angka,
    // null, atau objek, jadi tipenya wajib diperiksa.
    function isText(value) {
      return typeof value === 'string' && value.length > 0;
    }

    function isPassword(value) {
      return typeof value === 'string' && value.length >= 6;
    }

    function checkLength(nama, email) {
      if (nama.length > MAKS_NAMA || email.length > MAKS_EMAIL) {
        throw new InvalidInputError('nama maksimal 100 karakter dan email maksimal 150 karakter');
      }
    }

    // P2002 = kode Prisma untuk nilai unik yang kembar. Di tabel users satu-satunya
    // kolom unik selain id adalah email.
    function toEmailConflict(err) {
      return err.code === 'P2002' ? new ConflictError('email sudah terdaftar') : err;
    }

    async function register(nama, email, password) {
      if (!isText(nama) || !isText(email) || !isPassword(password)) {
        throw new InvalidInputError('nama, email, dan password (min 6 karakter) wajib diisi');
      }
      checkLength(nama, email);

      const existing = await userRepository.findByEmail(email);
      if (existing) throw new ConflictError('email sudah terdaftar');

      const hashed = await bcrypt.hash(password, 10);
      try {
        const user = await userRepository.create({ nama, email, password: hashed });
        return toSafeUser(user);
      } catch (err) {
        throw toEmailConflict(err); // dua pendaftaran email sama di waktu bersamaan
      }
    }

    async function login(email, password) {
      if (!isText(email) || !isText(password)) {
        throw new InvalidInputError('email atau password salah');
      }

      const user = await userRepository.findByEmail(email);
      if (!user) throw new NotFoundError('email atau password salah');

      const match = await bcrypt.compare(password, user.password);
      if (!match) throw new InvalidInputError('email atau password salah');

      const token = generateToken(user.id);
      return { token, user: toSafeUser(user) };
    }

    async function profile(userId) {
      const user = await userRepository.findById(userId);
      if (!user) throw new NotFoundError('pengguna tidak ditemukan');
      return toSafeUser(user);
    }

    async function updateProfile(userId, nama, email) {
      if (!isText(nama) || !isText(email)) throw new InvalidInputError('nama dan email wajib diisi');
      checkLength(nama, email);
      try {
        await userRepository.updateProfile(userId, nama, email);
      } catch (err) {
        throw toEmailConflict(err); // email sudah dipakai akun lain -> 409
      }
    }

    async function updatePassword(userId, passwordLama, passwordBaru) {
      const user = await userRepository.findById(userId);
      if (!user) throw new NotFoundError('pengguna tidak ditemukan');

      const pesan = 'password lama salah atau password baru terlalu pendek';
      if (!isText(passwordLama)) throw new InvalidInputError(pesan);

      const match = await bcrypt.compare(passwordLama, user.password);
      if (!match) throw new InvalidInputError(pesan);

      if (!isPassword(passwordBaru)) throw new InvalidInputError(pesan);

      const hashed = await bcrypt.hash(passwordBaru, 10);
      await userRepository.updatePassword(userId, hashed);
    }

    function generateToken(userId) {
      return jwt.sign({ sub: userId }, config.jwtSecret, { algorithm: 'HS256', expiresIn: '24h' });
    }

    module.exports = { register, login, profile, updateProfile, updatePassword };

src/handlers/authHandler.js

    const authService = require('../services/authService');
    const { ok } = require('../utils/response');
    const { AppError, InvalidInputError, NotFoundError } = require('../errors');

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
        // "email tidak ditemukan" (NotFoundError) dan "password salah"
        // (InvalidInputError) sengaja dibalas SAMA, 401 -- supaya tidak membocorkan
        // ke penyerang apakah suatu email terdaftar atau tidak.
        if (err instanceof NotFoundError || err instanceof InvalidInputError) {
          return next(new AppError('email atau password salah', 'UNAUTHORIZED', 401));
        }
        next(err); // error lain (mis. database mati) tetap 500 dan tercetak di terminal
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

## 06 Swagger, Route & Server

Penjelasan: [Pertemuan 9a Bagian 14](../../pertemuan-09a.html#s14).

src/docs/swagger.js

    // Dokumentasi OpenAPI untuk modul user (auth & profil).
    // Isinya hanya objek JavaScript biasa. Swagger UI membacanya lalu membuat
    // halaman uji coba di http://localhost:8080/swagger/

    // Bentuk body JSON; semua properti yang ditulis dianggap wajib.
    function jsonBody(properties) {
      return {
        required: true,
        content: {
          'application/json': {
            schema: { type: 'object', required: Object.keys(properties), properties },
          },
        },
      };
    }

    // Contoh respons sukses.
    function sukses(description, data) {
      return { description, content: { 'application/json': { example: { data } } } };
    }

    // Contoh respons gagal.
    function gagal(message, code) {
      return { description: message, content: { 'application/json': { example: { error: { message, code } } } } };
    }

    // Potongan yang dipakai berulang.
    const nama = { type: 'string', maxLength: 100, example: 'Budi Tester' };
    const email = { type: 'string', format: 'email', maxLength: 150, example: 'budi@test.com' };
    const password = { type: 'string', format: 'password', minLength: 6, example: 'rahasia123' };
    const user = { id: 1, nama: 'Budi Tester', email: 'budi@test.com' };
    const butuhToken = [{ bearerAuth: [] }];
    const tokenSalah = gagal('token tidak valid', 'UNAUTHORIZED');

    module.exports = {
      openapi: '3.0.3',
      info: {
        title: 'API Project',
        version: '1.0.0',
        description:
          'Modul user. Urutan uji: register, login, salin token, klik Authorize, ' +
          'tempel token (tanpa kata Bearer), lalu coba endpoint profil.',
      },
      servers: [{ url: '/api' }],
      tags: [
        { name: 'Auth', description: 'Daftar dan masuk' },
        { name: 'Profil', description: 'Butuh token' },
      ],
      components: {
        securitySchemes: {
          bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
        },
      },
      paths: {
        '/auth/register': {
          post: {
            tags: ['Auth'],
            summary: 'Daftar akun baru',
            requestBody: jsonBody({ nama, email, password }),
            responses: {
              201: sukses('Akun dibuat', user),
              400: gagal('nama, email, dan password (min 6 karakter) wajib diisi', 'BAD_REQUEST'),
              409: gagal('email sudah terdaftar', 'CONFLICT'),
            },
          },
        },
        '/auth/login': {
          post: {
            tags: ['Auth'],
            summary: 'Masuk dan dapatkan token (maks. 5 kali per menit)',
            requestBody: jsonBody({ email, password }),
            responses: {
              200: sukses('Berhasil masuk', { token: 'eyJhbGciOiJIUzI1NiIs...', user }),
              401: gagal('email atau password salah', 'UNAUTHORIZED'),
              429: gagal('terlalu banyak percobaan, coba lagi nanti', 'TOO_MANY_REQUESTS'),
            },
          },
        },
        '/profile': {
          get: {
            tags: ['Profil'],
            summary: 'Lihat profil sendiri',
            security: butuhToken,
            responses: { 200: sukses('Data profil', user), 401: tokenSalah },
          },
          put: {
            tags: ['Profil'],
            summary: 'Ubah nama dan email',
            security: butuhToken,
            requestBody: jsonBody({ nama, email }),
            responses: {
              200: sukses('Profil diubah', { message: 'profil berhasil diperbarui' }),
              400: gagal('nama dan email wajib diisi', 'BAD_REQUEST'),
              401: tokenSalah,
              409: gagal('email sudah terdaftar', 'CONFLICT'),
            },
          },
        },
        '/profile/password': {
          put: {
            tags: ['Profil'],
            summary: 'Ubah password',
            security: butuhToken,
            requestBody: jsonBody({
              password_lama: password,
              password_baru: { ...password, example: 'rahasiabaru456' },
            }),
            responses: {
              200: sukses('Password diubah', { message: 'password berhasil diperbarui' }),
              400: gagal('password lama salah atau password baru terlalu pendek', 'BAD_REQUEST'),
              401: tokenSalah,
            },
          },
        },
      },
    };

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

src/app.js

    const express = require('express');
    const cors = require('cors');
    const swaggerUi = require('swagger-ui-express');

    const swaggerSpec = require('./docs/swagger');
    const { requireAuth } = require('./middleware/auth');
    const { loginLimiter } = require('./middleware/rateLimit');
    const { errorHandler } = require('./middleware/errorHandler');

    const authHandler = require('./handlers/authHandler');

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

server.js

    const app = require('./src/app');
    const config = require('./src/config');
    const prisma = require('./src/db');

    async function main() {
      // Tes koneksi database lebih dulu, gagal cepat kalau DATABASE_URL salah
      // daripada membiarkan server menyala tapi semua endpoint error 500.
      try {
        await prisma.$queryRaw`SELECT 1`;
        console.log('berhasil terhubung ke PostgreSQL');
      } catch (err) {
        console.error('gagal konek ke database:', err.message);
        process.exit(1);
      }

      const server = app.listen(config.port, () => {
        console.log(`server berjalan di port ${config.port}`);
        console.log(`swagger: http://localhost:${config.port}/swagger/`);
      });

      // graceful shutdown
      const shutdown = () => {
        console.log('server dimatikan dengan aman');
        server.close(async () => {
          await prisma.$disconnect();
          process.exit(0);
        });
      };
      process.on('SIGINT', shutdown);
      process.on('SIGTERM', shutdown);
    }

    main();

## 07 Jalankan & Uji

Pakai database baru

Buat database **baru yang kosong** di Neon untuk project-mu. Jangan memakai database latihan UMKM: Prisma akan menemukan tabel lain dan meminta *reset* yang menghapus data.

terminal

    cp .env.example .env      # isi DATABASE_URL dan JWT_SECRET
    npx prisma migrate dev --name init
    npm run dev

Buka `http://localhost:8080/swagger/`, lalu uji register, login, *Authorize*, dan profil seperti di [Pertemuan 9a Bagian 16](../../pertemuan-09a.html#s16).

Ingin membuat Swagger-nya sendiri selangkah demi selangkah? Ikuti [Setup Swagger dari Awal](swagger.md). Mau dibuat otomatis dari route? Ikuti [Generate Swagger Otomatis](swagger-generate.md).

Checkpoint

Lanjut ke tutorial project-mu hanya kalau `GET /profile` sudah membalas `200`. Kembali ke [daftar project](index.md).

Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
