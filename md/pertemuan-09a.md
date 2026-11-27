<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 9a · Proyek Lengkap

# Membangun umkm-api dengan Node.js, Express, Prisma & PostgreSQL

Proyek `umkm-api` dari Pertemuan 4 dibangun aslinya pakai Golang. Materi ini membangun ULANG API yang **persis sama** — endpoint sama, aturan bisnis sama, bentuk respons JSON sama — tapi memakai **Node.js + Express + Prisma ORM + PostgreSQL**, supaya terlihat jelas bahwa arsitektur (handler → service → repository) dan konsepnya (JWT, bcrypt, ownership, pagination, upload foto) itu universal, tidak terikat satu bahasa. Seluruh kode di materi ini sudah diuji ulang dari folder kosong memakai versi paket yang dipatok, jadi ikuti persis, termasuk nomor versinya.

Daftar isi cepat

1.  [01. Tujuan & Prasyarat](#s1)
2.  [02. Membuat Proyek dari Nol](#s2)
3.  [03. Struktur Folder Final](#s3)
4.  [04. Dependency di package.json](#s4)
5.  [05. Skema Database (Prisma Schema)](#s5)
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

- **Node.js 18.18 ke atas** terpasang — cek dengan `node -v` di terminal.
- Akun **Neon** (PostgreSQL) sudah ada dari Pertemuan 4, dengan `DATABASE_URL`-nya dicatat (atau buat proyek Neon baru khusus untuk versi Node ini).
- Editor kode (VS Code direkomendasikan) dan **Postman** atau `curl` untuk menguji endpoint.
- Paham dasar JavaScript: `async/await`, `require`/`module.exports`, dan konsep *middleware* (kalau belum, lihat Pertemuan 1b untuk perbandingan Dart vs sintaks mirip di JS).

Kenapa dibuat ulang, bukan sekadar dijelaskan?

Membaca kode Go lalu kode Node yang melakukan hal sama, baris per baris, adalah cara tercepat membuktikan bahwa yang dipelajari di Pertemuan 4/9 bukan "cara Go", tapi "cara REST API dibangun" — `handler → service → repository`, JWT, bcrypt, dan query parameterized adalah konsep yang sama persis di balik bahasa apa pun.

## 02Membuat Proyek dari Nol

Buat folder proyek baru, lalu inisialisasi `package.json` dan install semua dependency yang dipakai sepanjang materi ini:

terminal

    mkdir umkm-api-node && cd umkm-api-node
    npm init -y

    npm install --save-exact express@4.22.3 @prisma/client@6.19.3 bcrypt@6.0.0 jsonwebtoken@9.0.3 multer@2.5.0 cors@2.8.6 dotenv@16.6.1 express-rate-limit@7.5.1
    npm install --save-exact --save-dev nodemon@3.1.11 prisma@6.19.3

- `express` — framework HTTP, setara `net/http` + `http.ServeMux` di Go.
- `@prisma/client` — **Prisma Client**, pustaka query bertipe aman yang dihasilkan dari skema kita; kita memanggil method JavaScript, Prisma yang menyusun SQL-nya. Setara peran `pgx` + `sqlc` di Go.
- `prisma` (dev saja) — **Prisma CLI**: perintah `migrate` (membuat/mengubah tabel), `generate` (membuat Prisma Client), dan `studio` (GUI untuk melihat isi tabel). Setara `golang-migrate` di Go.
- `bcrypt` — hashing password satu arah, setara `golang.org/x/crypto/bcrypt`.
- `jsonwebtoken` — membuat & memverifikasi JWT, setara `golang-jwt/jwt`.
- `multer` — middleware upload `multipart/form-data`, setara `r.ParseMultipartForm` manual di Go.
- `cors` — mengizinkan Flutter Web (kalau dipakai) memanggil API dari origin berbeda.
- `dotenv` — membaca berkas `.env`, setara `godotenv`.
- `express-rate-limit` — pembatas percobaan login, setara `golang.org/x/time/rate` yang dipakai manual di Go.
- `nodemon` (dev saja) — restart otomatis server tiap kali berkas disimpan, setara `air`/`fresh` di dunia Go.

Pakai nomor versi persis seperti di atas

Tanpa nomor versi, `npm install` mengambil rilis terbaru (misalnya Express 5), yang tidak diuji di materi ini. `nama@versi` memilih versi tertentu, dan `--save-exact` menuliskannya di `package.json` tanpa tanda `^` supaya tidak naik sendiri. Jangan turunkan ke `multer` 1.x (sudah ditandai usang karena celah keamanan) atau `bcrypt` 5.x (dependensi instalasinya punya celah keamanan).

Prisma dipatok ke versi 6.x

Materi ini ditulis & diuji dengan Prisma **6.19.3** (`provider = "prisma-client-js"`, `new PrismaClient()` polos). Prisma 7 ke atas mengubah cara konfigurasi (ada `prisma.config.ts` dan driver adapter wajib), sehingga kode di materi ini tidak bisa dipakai apa adanya. Versi `@prisma/client` dan `prisma` harus selalu sama.

Peringatan yang mungkin muncul saat install

npm versi baru bisa menampilkan `npm warn allow-scripts` untuk Prisma. Itu peringatan, bukan error. Kalau nanti Prisma Client tidak ditemukan, jalankan `npx prisma generate`. `npm audit` juga masih melaporkan temuan *high* pada dependensi Prisma CLI (`deepmerge-ts`, `effect`); perbaikannya mengharuskan pindah versi mayor Prisma, jadi **jangan** jalankan `npm audit fix --force`.

## 03Struktur Folder Final

Strukturnya sengaja dibuat semirip mungkin dengan `internal/` di proyek Go, supaya siapa pun yang sudah paham arsitektur `umkm-api` versi Go bisa langsung menebak isi tiap folder di versi Node ini:

struktur folder

    umkm-api-node/
    ├── package.json
    ├── package-lock.json     dibuat otomatis oleh npm
    ├── node_modules/         paket hasil npm install
    ├── .env                  (dibuat sendiri, JANGAN di-commit ke Git)
    ├── .env.example
    ├── .gitignore
    ├── prisma/
    │   ├── schema.prisma     skema database
    │   └── migrations/       riwayat migrasi SQL, dibuat otomatis oleh Prisma
    │       ├── migration_lock.toml
    │       └── <timestamp>_init/migration.sql
    ├── server.js             entry point
    ├── uploads/              foto UMKM & produk tersimpan di sini
    └── src/
        ├── app.js            daftar semua route Express
        ├── config.js         baca .env
        ├── db.js             instance PrismaClient (koneksi database)
        ├── errors.js         kelas error kustom (AppError & turunannya)
        ├── middleware/
        │   ├── auth.js        requireAuth (verifikasi JWT)
        │   ├── rateLimit.js    pembatas percobaan login
        │   └── errorHandler.js  penerjemah error -> response JSON
        ├── utils/
        │   ├── response.js    ok() & paginated()
        │   ├── pagination.js  normalizePagination()
        │   └── upload.js      konfigurasi multer & helper file
        ├── repositories/       akses database (Prisma)
        │   ├── userRepository.js
        │   ├── umkmRepository.js
        │   └── produkRepository.js
        ├── services/           aturan bisnis & otorisasi
        │   ├── authService.js
        │   ├── umkmService.js
        │   └── produkService.js
        └── handlers/           terima request, balas JSON
            ├── authHandler.js
            ├── umkmHandler.js
            └── produkHandler.js

Buat semua folder kosongnya dulu, biar tidak bolak-balik `mkdir` di tengah jalan:

terminal

    mkdir -p src/middleware src/utils src/repositories src/services src/handlers uploads
    touch uploads/.gitkeep

### Fungsi setiap folder

| Folder | Untuk apa | Aturan |
|----|----|----|
| `prisma/` | Definisi database: skema dan riwayat perubahannya. | Di-commit ke Git, termasuk seluruh isi `migrations/`. |
| `src/` | Semua kode aplikasi. | `server.js` sengaja di luar sebagai pintu masuk. |
| `src/middleware/` | Kode yang dijalankan di tengah perjalanan request: cek token, batasi login, ubah error jadi JSON. | Tidak berisi aturan bisnis. |
| `src/utils/` | Fungsi bantu yang dipakai banyak tempat: respons, pagination, upload. | Tidak mengakses database. |
| `src/repositories/` | Satu-satunya lapisan yang berbicara dengan database lewat Prisma Client. | Tanpa validasi dan tanpa keputusan bisnis. |
| `src/services/` | Otak aplikasi: validasi, aturan bisnis, otorisasi. | Tidak mengenal `req` maupun `res`. |
| `src/handlers/` | Penerjemah HTTP: ambil input dari `req`, panggil service, balas lewat `res`. | Tidak memanggil Prisma langsung. |
| `uploads/` | Tempat file foto disimpan (`umkm/` dan `produk/` dibuat otomatis). | Isinya tidak di-commit; hanya `.gitkeep` supaya folder tetap ada. |
| `node_modules/` | Kode paket pihak ketiga. | Tidak di-commit, bisa dibuat ulang dengan `npm install`. |

### Fungsi setiap file

| File | Fungsi | Dipakai oleh |
|----|----|----|
| `package.json` | Identitas proyek, daftar paket beserta versinya, dan perintah `npm run`. | npm |
| `package-lock.json` | Mengunci versi persis seluruh paket, termasuk paket turunannya. | npm (`npm ci`) |
| `.env` | Nilai rahasia: alamat database, kunci JWT, port, folder upload. | `config.js`, Prisma |
| `.env.example` | Contoh isi `.env` tanpa rahasia asli. | Anggota tim |
| `.gitignore` | Daftar file yang tidak boleh masuk Git. | Git |
| `prisma/schema.prisma` | Bentuk tabel dan relasinya. | Prisma Migrate dan Generate |
| `prisma/migrations/*/migration.sql` | SQL untuk setiap perubahan skema, berurutan menurut waktu. | Prisma Migrate |
| `prisma/migrations/migration_lock.toml` | Mencatat jenis database (`postgresql`). Jangan diedit manual. | Prisma Migrate |
| `server.js` | Cek koneksi database, nyalakan server, matikan dengan rapi. | `npm run dev` / `npm start` |
| `src/app.js` | Membuat aplikasi Express, memasang middleware dan semua route. | `server.js` |
| `src/config.js` | Membaca `.env` dan memberi nilai default. | auth, upload, service, server |
| `src/db.js` | Membuat satu `PrismaClient` untuk seluruh aplikasi. | Semua repository, `server.js` |
| `src/errors.js` | Kelas error yang membawa status HTTP dan kode error. | Service dan handler |
| `src/middleware/auth.js` | `requireAuth`: memeriksa token JWT. | `app.js` |
| `src/middleware/rateLimit.js` | `loginLimiter`: maksimal 5 percobaan login per menit. | `app.js` |
| `src/middleware/errorHandler.js` | Mengubah semua error menjadi respons JSON. | `app.js` |
| `src/utils/response.js` | `ok()` dan `paginated()`: bentuk respons sukses. | Handler |
| `src/utils/pagination.js` | `normalizePagination()`: merapikan `page` dan `limit`. | `umkmService`, `produkService` |
| `src/utils/upload.js` | Konfigurasi multer, menyusun path foto, menghapus foto. | `app.js`, handler, `errorHandler` |
| `src/repositories/userRepository.js` | Query tabel `users`. | `authService` |
| `src/repositories/umkmRepository.js` | Query tabel `umkm`. | `umkmService`, `produkService` |
| `src/repositories/produkRepository.js` | Query tabel `produk`. | `produkService` |
| `src/services/authService.js` | Register, login, profil, ubah password, pembuatan token. | `authHandler` |
| `src/services/umkmService.js` | Aturan UMKM: satu user satu UMKM, cek pemilik. | `umkmHandler` |
| `src/services/produkService.js` | Aturan produk: validasi harga, cek pemilik lewat UMKM. | `produkHandler` |
| `src/handlers/authHandler.js` | Endpoint auth dan profil. | `app.js` |
| `src/handlers/umkmHandler.js` | Endpoint UMKM. | `app.js` |
| `src/handlers/produkHandler.js` | Endpoint produk. | `app.js` |

### Alur satu request melewati file-file itu

alur request

    Flutter / curl
       |  HTTP request
       v
    app.js            cocokkan method + path
       v
    middleware        cors -> express.json -> (loginLimiter / requireAuth / uploadSingle)
       v
    handler           ambil input dari req
       v
    service           validasi + aturan bisnis
       v
    repository        panggil Prisma Client
       v
    PostgreSQL

    Sukses : repository -> service -> handler -> ok() / paginated() -> JSON
    Gagal  : throw / next(err) -> errorHandler -> JSON error

Setiap lapisan hanya memanggil lapisan tepat di bawahnya. Dengan begitu, kalau database diganti, yang berubah cukup repository; kalau aturan bisnis berubah, yang diubah cukup service.

## 04Dependency di package.json

Buka `package.json` yang dibuat `npm init -y` tadi, tambahkan bagian `scripts` (bagian `dependencies` dan `devDependencies` sudah otomatis terisi dari `npm install` di Bagian 02, tidak perlu ditulis ulang manual):

package.json

    {
      "name": "umkm-api-node",
      "version": "1.0.0",
      "description": "REST API UMKM — Node.js + Express + Prisma + PostgreSQL",
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
        "multer": "2.5.0"
      },
      "devDependencies": {
        "nodemon": "3.1.11",
        "prisma": "6.19.3"
      }
    }

- `npm run dev` — dipakai sehari-hari selama development (auto-restart tiap simpan berkas); `npm start` dipakai saat deploy ke server sungguhan (tidak butuh auto-restart).
- `npm run migrate:dev` — membuat & menerapkan migrasi baru setiap `schema.prisma` berubah (hanya untuk development).
- `npm run migrate` — menerapkan migrasi yang sudah ada tanpa membuat yang baru (aman untuk server produksi/deploy).
- `npm run studio` — membuka Prisma Studio, GUI di browser untuk melihat & mengedit isi tabel.
- `postinstall` — otomatis menjalankan `prisma generate` setiap kali `npm install`, supaya Prisma Client selalu ada setelah `git clone` baru atau deploy.

Kenapa tanpa tanda ^

`"express": "^4.22.3"` berarti boleh naik ke 4.x yang lebih baru, sedangkan `"express": "4.22.3"` berarti hanya versi itu. `package-lock.json` ikut di-commit; di komputer lain atau server, `npm ci` memasang persis isi file tersebut. Kalau `npm init -y` menambahkan baris lain (misalnya `license` atau `type`), biarkan saja.

## 05Skema Database (Prisma Schema)

### Prisma itu apa dan untuk apa

**Prisma** adalah *ORM* (Object-Relational Mapper): jembatan antara tabel di database dan objek di JavaScript. Tanpa Prisma, kita menulis sendiri `CREATE TABLE`, string SQL untuk setiap query, dan mengingat urutan parameter `$1, $2`. Dengan Prisma, bentuk data ditulis sekali di satu file, lalu SQL-nya dibuatkan.

| Pekerjaan | SQL manual | Dengan Prisma |
|----|----|----|
| Membuat tabel | Menulis `CREATE TABLE` | Menulis `model`, lalu `migrate` |
| Mengubah tabel | Menulis `ALTER TABLE` dan mengingat urutannya | `migrate` membuat file SQL bernomor |
| Mengambil data | `SELECT * FROM users WHERE email = $1` | `prisma.user.findUnique({ where: { email } })` |
| Salah ketik nama kolom | Baru ketahuan saat query dijalankan | Ditolak Prisma Client, dan editor memberi saran nama kolom |
| SQL injection | Harus disiplin memakai parameter | Query Prisma Client otomatis memakai parameter |

Prisma terdiri dari empat bagian:

| Bagian | Fungsinya | Perintah |
|----|----|----|
| **Prisma Schema** | File `schema.prisma`, sumber kebenaran bentuk data. | `npx prisma validate` |
| **Prisma Migrate** | Membandingkan skema dengan riwayat migrasi, lalu membuat dan menjalankan SQL. | `npx prisma migrate dev` |
| **Prisma Client** | Kode JavaScript hasil *generate* yang dipakai repository. | `npx prisma generate` |
| **Prisma Studio** | Tampilan di browser untuk melihat dan mengedit isi tabel. | `npx prisma studio` |

hubungan antar bagian

                        prisma/schema.prisma
                         /                \
            migrate dev /                  \ generate
                       v                    v
       prisma/migrations/*.sql        Prisma Client (di node_modules)
                       |                    |
                       v                    v
                  PostgreSQL  <-------  repository

Harga yang dibayar: ada langkah *generate* yang harus diingat, dan query yang sangat rumit kadang lebih mudah ditulis sebagai SQL (Prisma menyediakan `$queryRaw` untuk itu).

### Isi schema.prisma

Tabel dan relasinya sama dengan versi Go (lihat Pertemuan 9 Bagian 04 "Desain Database"). Bedanya, di sini kita **tidak menulis `CREATE TABLE` manual**: skema dideklarasikan sekali di `prisma/schema.prisma`, lalu Prisma memakainya untuk membuat tabel (**migrate**) dan membuat Prisma Client yang tahu bentuk setiap tabel (**generate**).

Buat folder `prisma/` lalu berkas `prisma/schema.prisma` (boleh juga lewat `npx prisma init --datasource-provider postgresql`, lalu ganti isinya dengan yang di bawah):

prisma/schema.prisma

    // Skema database UMKM API — menggantikan schema.sql.
    // Satu-satunya sumber kebenaran: dari file ini Prisma membuat tabel (migrate)
    // sekaligus Prisma Client yang bertipe aman (generate).

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

      umkm Umkm?

      @@map("users")
    }

    model Umkm {
      id         Int      @id @default(autoincrement())
      user_id    Int      @unique
      nama       String   @db.VarChar(150)
      deskripsi  String?
      alamat     String?  @db.VarChar(255)
      foto       String?  @db.VarChar(255)
      created_at DateTime @default(now()) @db.Timestamp(6)

      user   User     @relation(fields: [user_id], references: [id], onDelete: Cascade)
      produk Produk[]

      @@map("umkm")
    }

    model Produk {
      id         Int      @id @default(autoincrement())
      umkm_id    Int
      nama       String   @db.VarChar(150)
      harga      Decimal  @default(0) @db.Decimal(12, 2)
      deskripsi  String?
      foto       String?  @db.VarChar(255)
      created_at DateTime @default(now()) @db.Timestamp(6)

      umkm Umkm @relation(fields: [umkm_id], references: [id], onDelete: Cascade)

      @@index([umkm_id])
      @@map("produk")
    }

Cara membacanya:

- `model User` ↔ tabel `users`: nama model memakai huruf kapital tunggal (konvensi Prisma), sedangkan `@@map("users")` menjaga nama tabel aslinya tetap `users`, `umkm`, dan `produk` seperti di versi Go.
- `@id @default(autoincrement())` ↔ `SERIAL PRIMARY KEY`. `@unique` ↔ `UNIQUE` — pada `Umkm.user_id` inilah yang membuat aturan **1 user = 1 UMKM**.
- `String?` (tanda tanya) berarti kolom boleh `NULL` (`deskripsi`, `alamat`, `foto`); tanpa tanda tanya berarti `NOT NULL`.
- `@relation(..., onDelete: Cascade)` ↔ `REFERENCES ... ON DELETE CASCADE`. Baris `umkm Umkm?` dan `produk Produk[]` adalah sisi sebaliknya dari relasi (hanya ada di Prisma Client, **tidak** jadi kolom di database).
- Nama field `user_id` dan `umkm_id` sengaja ditulis snake_case (bukan `userId`) supaya bentuk JSON respons API **identik** dengan versi Go — Flutter tidak perlu diubah sama sekali.
- `Decimal @db.Decimal(12, 2)` ↔ `NUMERIC(12,2)` untuk harga. Hati-hati: Prisma membalasnya sebagai objek `Decimal`, bukan angka biasa (dibahas di Bagian 10).

### Fungsi setiap bagian schema

| Blok | Fungsi |
|----|----|
| `generator client` | Memberi tahu Prisma apa yang dibuat saat *generate*; `prisma-client-js` berarti Prisma Client untuk JavaScript. |
| `datasource db` | Jenis database (`provider`) dan alamatnya (`url`). `env("DATABASE_URL")` mengambil nilai dari `.env`, jadi password tidak tertulis di kode. |
| `model Nama` | Satu model sama dengan satu tabel. Satu baris di dalamnya sama dengan satu kolom atau satu relasi. |

| Tipe / tanda | Di PostgreSQL | Di JavaScript |
|----|----|----|
| `Int` | `INTEGER` | number |
| `String` | `TEXT` (atau `VARCHAR(n)` bila diberi `@db.VarChar(n)`) | string |
| `Decimal` | `DECIMAL(12,2)` | objek `Decimal` |
| `DateTime` | `TIMESTAMP` | `Date` |
| `?` (mis. `String?`) | boleh `NULL` | bisa `null` |
| `[]` (mis. `Produk[]`) | bukan kolom | daftar data relasi |

| Atribut | Fungsi |
|----|----|
| `@id` | Primary key. |
| `@default(autoincrement())` | Nomor naik otomatis (`SERIAL`). |
| `@default(now())` | Diisi waktu saat baris dibuat. |
| `@default(0)` | Nilai awal bila tidak dikirim. |
| `@unique` | Nilai tidak boleh kembar. Hanya field unik (atau `@id`) yang bisa dipakai di `findUnique`. |
| `@db.VarChar(150)` | Menentukan tipe persis di database, di sini teks maksimal 150 karakter. |
| `@db.Decimal(12, 2)` | 12 digit total, 2 di belakang koma. |
| `@db.Timestamp(6)` | Waktu dengan ketelitian mikrodetik. |
| `@relation(fields, references)` | `fields` = kolom foreign key di tabel ini; `references` = kolom yang dirujuk di tabel induk. |
| `onDelete: Cascade` | Induk dihapus, anaknya ikut terhapus. |
| `@@map("users")` | Nama tabel asli di database. |
| `@@index([umkm_id])` | Indeks supaya pencarian produk per UMKM cepat. |

### Apa itu migrasi

**Migrasi** adalah catatan perubahan struktur database dalam bentuk file SQL berurutan, mirip riwayat commit untuk tabel. Prisma menandai migrasi yang sudah dijalankan di tabel `_prisma_migrations`, sehingga setiap database (laptopmu, laptop teman, server) bisa disamakan dengan menjalankan migrasi yang belum ada.

### Membuat migrasi pertama

1.  Isi `.env` (Bagian 06), minimal `DATABASE_URL`.
2.  Periksa penulisan skema: `npx prisma validate`. Salah ketik atribut langsung dilaporkan beserta nomor barisnya.
3.  Buat dan jalankan migrasi (perintah di bawah).
4.  Pastikan hasilnya: `npx prisma migrate status` harus menjawab `Database schema is up to date!`

Isi `.env` dulu (Bagian 06 di bawah) supaya `DATABASE_URL` tersedia, lalu jalankan migrasi pertama:

terminal

    npx prisma migrate dev --name init

Perintah ini melakukan tiga hal sekaligus: (1) membuat berkas SQL di `prisma/migrations/<timestamp>_init/migration.sql`, (2) menjalankan SQL itu ke database-mu, (3) menjalankan `prisma generate` untuk membuat Prisma Client. SQL yang dihasilkan kurang lebih seperti ini — isinya setara dengan `000001_init.up.sql` versi Go, hanya ditulis otomatis:

prisma/migrations/<timestamp>_init/migration.sql

    -- CreateTable
    CREATE TABLE "users" (
        "id" SERIAL NOT NULL,
        "nama" VARCHAR(100) NOT NULL,
        "email" VARCHAR(150) NOT NULL,
        "password" VARCHAR(255) NOT NULL,
        "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT "users_pkey" PRIMARY KEY ("id")
    );

    -- CreateTable
    CREATE TABLE "umkm" (
        "id" SERIAL NOT NULL,
        "user_id" INTEGER NOT NULL,
        "nama" VARCHAR(150) NOT NULL,
        "deskripsi" TEXT,
        "alamat" VARCHAR(255),
        "foto" VARCHAR(255),
        "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT "umkm_pkey" PRIMARY KEY ("id")
    );

    -- CreateTable
    CREATE TABLE "produk" (
        "id" SERIAL NOT NULL,
        "umkm_id" INTEGER NOT NULL,
        "nama" VARCHAR(150) NOT NULL,
        "harga" DECIMAL(12,2) NOT NULL DEFAULT 0,
        "deskripsi" TEXT,
        "foto" VARCHAR(255),
        "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

        CONSTRAINT "produk_pkey" PRIMARY KEY ("id")
    );

    -- CreateIndex
    CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

    -- CreateIndex
    CREATE UNIQUE INDEX "umkm_user_id_key" ON "umkm"("user_id");

    -- CreateIndex
    CREATE INDEX "produk_umkm_id_idx" ON "produk"("umkm_id");

    -- AddForeignKey
    ALTER TABLE "umkm" ADD CONSTRAINT "umkm_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

    -- AddForeignKey
    ALTER TABLE "produk" ADD CONSTRAINT "produk_umkm_id_fkey" FOREIGN KEY ("umkm_id") REFERENCES "umkm"("id") ON DELETE CASCADE ON UPDATE CASCADE;

Mau melihat isi tabel tanpa menulis query? Jalankan `npx prisma studio` — terbuka halaman di browser berisi tabel `users`, `umkm`, dan `produk` yang bisa dilihat dan diedit langsung.

### Mengubah tabel: latihan migrasi dari awal sampai akhir

Polanya selalu sama: **ubah `schema.prisma`, lalu jalankan `migrate dev` dengan nama yang menjelaskan perubahannya**. Latihan berikut menambah, mengganti nama, lalu menghapus satu kolom.

#### 1. Menambah kolom

prisma/schema.prisma — tambahkan satu baris di model Umkm

      alamat     String?  @db.VarChar(255)
      no_telepon String?  @db.VarChar(20)

terminal

    npx prisma migrate dev --name tambah_no_telepon

prisma/migrations/<timestamp>_tambah_no_telepon/migration.sql (dibuat otomatis)

    -- AlterTable
    ALTER TABLE "umkm" ADD COLUMN     "no_telepon" VARCHAR(20);

Kolom baru sengaja dibuat boleh kosong (`?`) karena baris lama belum punya nilainya. Kolom ini juga **belum muncul di respons API**: kalau mau dipakai sungguhan, tambahkan ke `umkmSelect`, `create`, dan `update` di repository, lalu ke service dan handler.

#### 2. Mengganti nama kolom tanpa kehilangan data

Ubah nama field `no_telepon` menjadi `telepon` di skema, lalu buat migrasinya **tanpa langsung dijalankan**:

terminal

    npx prisma migrate dev --name rename_telepon --create-only

migration.sql bawaan Prisma — BERBAHAYA

    /*
      Warnings:

      - You are about to drop the column `no_telepon` on the `umkm` table. All the data in the column will be lost.

    */
    -- AlterTable
    ALTER TABLE "umkm" DROP COLUMN "no_telepon",
    ADD COLUMN     "telepon" VARCHAR(20);

Kalau kolomnya sudah berisi data, Prisma lebih dulu bertanya `Are you sure you want to create this migration?`. Jawab `y`; pada tahap ini belum ada SQL yang dijalankan. Prisma tidak bisa menebak bahwa kamu hanya mengganti nama, jadi SQL-nya menghapus kolom lama beserta datanya. Ganti seluruh isi file itu dengan:

migration.sql setelah diedit

    ALTER TABLE "umkm" RENAME COLUMN "no_telepon" TO "telepon";

terminal — jalankan migrasi yang sudah diedit

    npx prisma migrate dev

#### 3. Menghapus kolom (kembalikan seperti semula)

Hapus baris `telepon` dari skema, lalu:

terminal

    npx prisma migrate dev --name hapus_telepon

Kalau kolomnya masih berisi data, Prisma menampilkan peringatan lalu bertanya `Are you sure you want to create and apply this migration?` — jawab `y` hanya kalau datanya memang boleh hilang, atau `n` untuk membatalkan. Setelah latihan ini skema kembali sama dengan di awal, sedangkan ketiga file migrasi tetap tersimpan sebagai riwayat.

### Daftar perintah Prisma

| Perintah | Fungsi | Kapan dipakai |
|----|----|----|
| `npx prisma validate` | Memeriksa penulisan skema. | Setelah mengedit skema |
| `npx prisma format` | Merapikan skema. | Sebelum commit |
| `npx prisma generate` | Membuat ulang Prisma Client. Tidak menyentuh database. | Setelah `git clone` / `git pull` |
| `npx prisma migrate dev --name ...` | Membuat migrasi baru, menjalankannya, lalu generate. | Development |
| `npx prisma migrate dev --create-only` | Membuat file migrasi untuk diperiksa dulu. | Rename atau perubahan berisiko |
| `npx prisma migrate deploy` | Hanya menjalankan migrasi yang belum jalan. | Server / produksi |
| `npx prisma migrate status` | Melihat apakah database sudah sinkron. | Saat ragu |
| `npx prisma migrate resolve --applied ...` | Menandai migrasi sebagai sudah dijalankan. | Baseline database lama |
| `npx prisma migrate reset` | **Menghapus seluruh data**, lalu menjalankan ulang semua migrasi. | Hanya database latihan |
| `npx prisma db push` | Menyamakan database dengan skema tanpa membuat file migrasi. | Coba-coba cepat saja |
| `npx prisma db pull` | Kebalikannya: menulis skema berdasarkan tabel yang sudah ada. | Proyek dengan database lama |
| `npx prisma studio` | Melihat dan mengedit data di browser. | Kapan saja saat development |

Tiga aturan migrasi

Commit seluruh folder `prisma/migrations/` ke Git. Jangan mengedit file migrasi yang **sudah dijalankan**; buat migrasi baru. Jangan pernah menjalankan `migrate dev` atau `migrate reset` ke database produksi.

### Database yang sudah berisi tabel (baseline)

Kalau `DATABASE_URL` menunjuk ke database yang tabelnya sudah dibuat versi Go (Pertemuan 4), `migrate deploy` menolak dengan error `P3005` karena database tidak kosong. Cara paling aman untuk belajar adalah memakai **database baru yang kosong**. Kalau datanya harus dipertahankan, tandai migrasi awal sebagai sudah diterapkan, pada proyek yang belum punya folder `prisma/migrations/`:

terminal

    mkdir -p prisma/migrations/0_init
    npx prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script > prisma/migrations/0_init/migration.sql
    npx prisma migrate resolve --applied 0_init
    npx prisma migrate deploy      # harus: No pending migrations to apply.

Database yang dipakai bersama versi Go

Jangan jalankan `migrate dev` di database tersebut: Prisma menemukan perbedaan (tabel `schema_migrations` milik Go, aturan foreign key, indeks) dan bisa meminta *reset* yang menghapus data. Perhatikan juga bahwa data yang dibuat versi Node tanpa `deskripsi` atau `alamat` tersimpan `NULL`, yang tidak bisa dibaca kode Go di Pertemuan 4. Selalu kirim semua field, atau pisahkan database kedua versi.

Neon: pakai connection string direct untuk migrate

Prisma Migrate memakai *advisory lock* dan shadow database yang sering bermasalah lewat connection pooler. Kalau `migrate dev` menggantung atau gagal di Neon, salin connection string **Direct** (tanpa `-pooler` di nama host) dari Neon Console → Connection Details untuk menjalankan migrasi.

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

| Variabel | Fungsi | Kalau kosong |
|----|----|----|
| `DATABASE_URL` | Alamat dan kredensial PostgreSQL. | Server gagal konek dan berhenti. |
| `JWT_SECRET` | Kunci untuk menandatangani dan memeriksa token. Siapa pun yang tahu nilainya bisa membuat token palsu. | Login gagal karena token tidak bisa dibuat. |
| `PORT` | Port server. | Dipakai `8080`. |
| `UPLOAD_DIR` | Folder penyimpanan foto. | Dipakai `./uploads`. |

Salin `.env.example` jadi `.env`, lalu isi `DATABASE_URL` dengan connection string Neon-mu yang sungguhan (dari Neon Console → Connection Details → pastikan bentuknya menyertakan `?sslmode=require` di akhir) dan `JWT_SECRET` dengan string acak panjang (boleh pakai `openssl rand -hex 32` di terminal untuk membuatnya).

### config.js — membaca .env

src/config.js

    require('dotenv').config();

    function getOrDefault(key, def) {
      const v = process.env[key];
      return v && v !== '' ? v : def;
    }

    module.exports = {
      jwtSecret: process.env.JWT_SECRET,
      port: getOrDefault('PORT', '8080'),
      uploadDir: getOrDefault('UPLOAD_DIR', './uploads'),
    };

`require('dotenv').config()` memindahkan isi `.env` ke `process.env`. `getOrDefault` memakai nilai default kalau variabelnya tidak ada atau kosong. File lain cukup `require('./config')`, tidak membaca `process.env` sendiri-sendiri.

### db.js — instance PrismaClient

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

Perhatikan `config.js` tidak memuat `databaseUrl`: Prisma membaca `DATABASE_URL` sendiri lewat `env("DATABASE_URL")` di `schema.prisma` (dan otomatis memuat berkas `.env` di root proyek). `PrismaClient` setara `pgxpool.Pool` di Go: ia mengelola kumpulan koneksi sendiri, dipakai bergantian oleh tiap query.

Satu PrismaClient untuk seluruh aplikasi

Selalu `require('../db')` dari repository — **jangan** menulis `new PrismaClient()` di tiap file. Setiap instance membuka connection pool sendiri; membuat banyak instance cepat menghabiskan jatah koneksi database (Neon gratis terbatas), dan gejalanya baru muncul belakangan sebagai error `Too many connections`.

SSL ke Neon tidak perlu diatur manual

Prisma otomatis mengaktifkan SSL kalau `DATABASE_URL` memuat `?sslmode=require` (bentuk standar dari Neon Console). Jadi tidak perlu kode SSL di `db.js`.

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

`AppError` adalah induknya: selain `message`, ia menyimpan `code` (teks untuk aplikasi) dan `status` (angka HTTP). Empat turunannya tinggal mengisi dua nilai itu:

| Kelas               | Status | Kode          | Contoh pemakaian                |
|---------------------|--------|---------------|---------------------------------|
| `InvalidInputError` | 400    | `BAD_REQUEST` | Password kurang dari 6 karakter |
| `ForbiddenError`    | 403    | `FORBIDDEN`   | Mengubah UMKM milik orang lain  |
| `NotFoundError`     | 404    | `NOT_FOUND`   | UMKM tidak ada                  |
| `ConflictError`     | 409    | `CONFLICT`    | Email sudah terdaftar           |

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

`ok(res, status, data)` membungkus hasil dalam `data`. `paginated(...)` menambahkan `meta` supaya aplikasi tahu halaman ke berapa dan berapa total datanya.

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

Isi `requireAuth` baris demi baris:

1.  Ambil header `Authorization`. Kalau kosong, langsung balas `401` "token tidak ditemukan".
2.  Buang awalan `Bearer ` (huruf besar/kecil diabaikan). Tanpa awalan, seluruh isi header dianggap token.
3.  `jwt.verify` memeriksa tanda tangan dengan `JWT_SECRET`, masa berlaku, dan memastikan algoritmanya `HS256`.
4.  Kalau sah, id pengguna dari klaim `sub` ditempel ke `req.userId`, lalu `next()` meneruskan ke langkah berikutnya.
5.  Kalau tidak sah (diubah, kedaluwarsa, kunci beda), balas `401` "token tidak valid". Handler tidak pernah dijalankan.

Token JWT terdiri dari tiga bagian dipisah titik: `header.payload.signature`. Payload-nya hanya di-encode, bukan dienkripsi, sehingga bisa dibaca siapa saja. Jangan menaruh data rahasia di sana. Yang mencegah pemalsuan adalah *signature*.

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

| Opsi | Arti |
|----|----|
| `windowMs: 60 * 1000` | Jendela hitungan 1 menit. |
| `limit: 5` | Maksimal 5 request per IP dalam jendela itu, baik berhasil maupun gagal. |
| `standardHeaders: true` | Mengirim header `RateLimit-*` berisi sisa kuota. |
| `legacyHeaders: false` | Tidak mengirim header lama `X-RateLimit-*`. |
| `handler` | Balasan saat kuota habis: `429` dengan bentuk error yang seragam. |

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

Urutan pemeriksaannya: (1) tipe file salah → `400`; (2) file lebih dari 5 MB → `400`; (3) error yang punya `status` (semua `AppError`) → status dan pesannya sendiri; (4) selain itu → dicetak ke terminal dan dibalas `500`. Pengguna tidak melihat detail error server, tetapi kamu bisa membacanya di terminal.

Dua hal yang perlu diketahui saat debugging

Body JSON yang rusak ditolak oleh `express.json()` dengan status `400` tetapi tanpa field `code`. Error dari Prisma (misalnya `P2002`, data unik kembar) tidak punya `status`, jadi menjadi `500`.

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

| Bagian | Fungsi |
|----|----|
| `ALLOWED_EXT` | Ekstensi yang diterima: `.jpg`, `.jpeg`, `.png`. |
| `InvalidFileTypeError` | Penanda error tipe file, dikenali `errorHandler`. |
| `storageFor(subDir)` | Menentukan folder tujuan (dibuat bila belum ada) dan nama file unik: waktu + angka acak. |
| `fileFilter` | Menolak file sebelum disimpan bila ekstensinya tidak diizinkan. |
| `uploadSingle(subDir, fieldName)` | Merakit middleware multer untuk satu field file, maksimal 5 MB. |
| `relativePath(subDir, file)` | Path yang disimpan ke database; string kosong kalau tidak ada foto. |
| `deleteFile(uploadDir, relPath)` | Menghapus foto lama; kegagalan diabaikan. |

Pemeriksaannya berdasarkan ekstensi nama file, bukan isi file. Untuk aplikasi produksi, periksa juga isi filenya.

Bedanya dengan Go: Go menyimpan file manual lewat `io.Copy` satu per satu di dalam handler. Multer melakukan seluruh proses (baca stream multipart, simpan ke disk, kasih nama unik) secara otomatis lewat konfigurasi `diskStorage` — handler tinggal membaca hasilnya dari `req.file`.

## 10Repository Layer

**Repository** adalah satu-satunya lapisan yang menyentuh database. Tugasnya menerima nilai biasa, menjalankan satu query lewat Prisma Client, lalu mengembalikan hasilnya. Ia tidak memeriksa apakah input valid atau siapa yang berhak; itu tugas service. Tidak ada string SQL di sini, dan tabel berikut membandingkan SQL dengan padanannya di Prisma:

| Operasi | SQL | Prisma Client |
|----|----|----|
| Ambil satu baris | `SELECT ... WHERE id = $1` lalu `rows[0] \|\| null` | `prisma.umkm.findUnique({ where: { id } })` → langsung `null` kalau tidak ada |
| Ambil banyak + pagination | `ORDER BY id DESC LIMIT $2 OFFSET $3` | `findMany({ orderBy, take, skip })` |
| Pencarian nama | `nama ILIKE '%' \|\| $1 \|\| '%'` | `where: { nama: { contains: q, mode: 'insensitive' } }` |
| Hitung baris | `SELECT COUNT(*)` | `prisma.umkm.count({ where })` → sudah berupa `Number` |
| Tambah | `INSERT ... RETURNING id` | `create({ data })` → mengembalikan baris yang baru dibuat |
| Ubah / hapus | `UPDATE ... WHERE` / `DELETE ... WHERE` | `update({ where, data })` / `delete({ where })` |

Pola setiap pemanggilan: `prisma.<model>.<method>({ where, data, select, orderBy, take, skip })`. `where` = syarat, `data` = nilai yang ditulis, `select` = kolom yang diambil. Semuanya `async`, jadi dipanggil dengan `await`. Untuk melihat SQL asli yang dijalankan, ubah sementara `log` di `db.js` menjadi `['query', 'warn', 'error']`.

### userRepository.js

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

`userSelect` sengaja menyertakan `password` (berisi hash) karena service butuh membandingkannya saat login. Hash itu dibuang oleh `toSafeUser` sebelum dikirim ke pengguna. SQL di bawah disederhanakan dari yang dihasilkan Prisma:

| Fungsi | SQL yang dijalankan | Hasil | Dipanggil oleh |
|----|----|----|----|
| `create(user)` | `INSERT INTO users (...) VALUES (...) RETURNING id, nama, email, password` | Baris yang baru dibuat | `register` |
| `findByEmail(email)` | `SELECT ... FROM users WHERE email = $1 LIMIT 1` | Objek user, atau `null` | `register`, `login` |
| `findById(id)` | `SELECT ... FROM users WHERE id = $1 LIMIT 1` | Objek user, atau `null` | `profile`, `updatePassword` |
| `updateProfile(id, nama, email)` | `UPDATE users SET nama = $1, email = $2 WHERE id = $3` | Tidak mengembalikan apa-apa | `updateProfile` |
| `updatePassword(id, hashedPassword)` | `UPDATE users SET password = $1 WHERE id = $2` | Tidak mengembalikan apa-apa | `updatePassword` |

Di mana "tidak ketemu" ditangani?

Di Go, baris yang tidak ketemu membuat `pgx` mengembalikan `pgx.ErrNoRows` yang lalu dikonversi jadi `domain.ErrNotFound`. Prisma `findUnique` tidak melempar error untuk kasus ini — ia mengembalikan `null`. Repository meneruskan `null` apa adanya, dan **service**-lah (Bagian 11-12) yang memutuskan melempar `NotFoundError` — persis seperti Go, cuma titik konversinya satu layer lebih ke atas. Perhatikan juga `select: userSelect`: kita memilih kolom secara eksplisit (sama seperti daftar kolom di `SELECT` lama) supaya `created_at` tidak ikut terbawa.

### umkmRepository.js

src/repositories/umkmRepository.js

    const prisma = require('../db');

    // select eksplisit: created_at sengaja tidak ikut dikirim ke klien,
    // sama seperti daftar kolom pada SELECT versi SQL mentah sebelumnya.
    const umkmSelect = { id: true, user_id: true, nama: true, deskripsi: true, alamat: true, foto: true };

    // where dipakai bersama oleh findAll & count supaya filter pencarian selalu
    // konsisten. q kosong -> undefined -> Prisma mengabaikan filter sama sekali.
    function buildWhere(q) {
      return q ? { nama: { contains: q, mode: 'insensitive' } } : undefined;
    }

    async function create(umkm) {
      return prisma.umkm.create({
        data: {
          user_id: umkm.user_id,
          nama: umkm.nama,
          deskripsi: umkm.deskripsi,
          alamat: umkm.alamat,
          foto: umkm.foto,
        },
        select: umkmSelect,
      });
    }

    // findAll mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
    async function findAll(q, limit, offset) {
      return prisma.umkm.findMany({
        where: buildWhere(q),
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: umkmSelect,
      });
    }

    // prisma.count() langsung mengembalikan Number -- tidak perlu lagi
    // Number(rows[0].count) seperti saat memakai node-postgres.
    async function count(q) {
      return prisma.umkm.count({ where: buildWhere(q) });
    }

    async function findById(id) {
      return prisma.umkm.findUnique({ where: { id }, select: umkmSelect });
    }

    async function findByUserId(userId) {
      return prisma.umkm.findUnique({ where: { user_id: userId }, select: umkmSelect });
    }

    async function update(umkm) {
      await prisma.umkm.update({
        where: { id: umkm.id },
        data: { nama: umkm.nama, deskripsi: umkm.deskripsi, alamat: umkm.alamat, foto: umkm.foto },
      });
    }

    async function remove(id) {
      await prisma.umkm.delete({ where: { id } });
    }

    module.exports = { create, findAll, count, findById, findByUserId, update, remove };

| Fungsi | SQL yang dijalankan | Catatan |
|----|----|----|
| `create(umkm)` | `INSERT INTO umkm (...) VALUES (...) RETURNING ...` | `user_id` kedua untuk user yang sama ditolak database (`@unique`). |
| `findAll(q, limit, offset)` | `SELECT ... WHERE nama ILIKE '%q%' ORDER BY id DESC LIMIT $2 OFFSET $3` | `take` = LIMIT, `skip` = OFFSET. Terbaru di atas. |
| `count(q)` | `SELECT COUNT(*) ... WHERE nama ILIKE '%q%'` | Total untuk `meta.total`. |
| `findById(id)` | `SELECT ... WHERE id = $1` | `null` bila tidak ada. |
| `findByUserId(userId)` | `SELECT ... WHERE user_id = $1` | Bisa memakai `findUnique` karena `user_id` unik. |
| `update(umkm)` | `UPDATE umkm SET nama, deskripsi, alamat, foto WHERE id = $5` | Field bernilai `undefined` dilewati Prisma (nilai lama tetap). |
| `remove(id)` | `DELETE FROM umkm WHERE id = $1` | Produk ikut terhapus oleh database (cascade). |

Filter pencarian opsional

`buildWhere(q)` mengembalikan `undefined` kalau `q` kosong, dan Prisma mengabaikan `where: undefined` — jadi tidak perlu lagi trik SQL `($1 = '' OR ...)`. Fungsi yang sama dipakai oleh `findAll` dan `count` supaya filter keduanya selalu konsisten (kalau tidak, `meta.total` bisa tidak cocok dengan isi `data`).

### produkRepository.js

src/repositories/produkRepository.js

    const prisma = require('../db');

    const produkSelect = { id: true, umkm_id: true, nama: true, harga: true, deskripsi: true, foto: true };

    // mapRow mengubah kolom "harga" (tipe Decimal di Prisma) menjadi Number biasa.
    // Prisma membalas NUMERIC/Decimal sebagai objek Decimal (di JSON jadi STRING
    // "15000") supaya tidak kehilangan presisi -- kita konversi balik ke Number,
    // setara float64 Harga di struct domain.Produk versi Go.
    function mapRow(row) {
      if (!row) return row;
      return { ...row, harga: Number(row.harga) };
    }

    async function create(produk) {
      const row = await prisma.produk.create({
        data: {
          umkm_id: produk.umkm_id,
          nama: produk.nama,
          harga: produk.harga,
          deskripsi: produk.deskripsi,
          foto: produk.foto,
        },
        select: produkSelect,
      });
      return mapRow(row);
    }

    async function findById(id) {
      return mapRow(await prisma.produk.findUnique({ where: { id }, select: produkSelect }));
    }

    async function findByUmkmId(umkmId, limit, offset) {
      const rows = await prisma.produk.findMany({
        where: { umkm_id: umkmId },
        orderBy: { id: 'desc' },
        take: limit,
        skip: offset,
        select: produkSelect,
      });
      return rows.map(mapRow);
    }

    async function countByUmkmId(umkmId) {
      return prisma.produk.count({ where: { umkm_id: umkmId } });
    }

    async function update(produk) {
      await prisma.produk.update({
        where: { id: produk.id },
        data: { nama: produk.nama, harga: produk.harga, deskripsi: produk.deskripsi, foto: produk.foto },
      });
    }

    async function remove(id) {
      await prisma.produk.delete({ where: { id } });
    }

    module.exports = { create, findById, findByUmkmId, countByUmkmId, update, remove };

| Fungsi | SQL yang dijalankan | Catatan |
|----|----|----|
| `mapRow(row)` | tidak ada | Mengubah `harga` dari `Decimal` ke `Number`; `null` diteruskan. |
| `create(produk)` | `INSERT INTO produk (...) VALUES (...) RETURNING ...` | Hasil dilewatkan `mapRow`. |
| `findById(id)` | `SELECT ... WHERE id = $1` | Dipakai detail dan cek pemilik. |
| `findByUmkmId(umkmId, limit, offset)` | `SELECT ... WHERE umkm_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3` | Memanfaatkan indeks `umkm_id`. |
| `countByUmkmId(umkmId)` | `SELECT COUNT(*) ... WHERE umkm_id = $1` | Sudah berupa `Number`. |
| `update(produk)` | `UPDATE produk SET nama, harga, deskripsi, foto WHERE id = $5` | `umkm_id` tidak ikut diubah. |
| `remove(id)` | `DELETE FROM produk WHERE id = $1` | Foto dihapus terpisah oleh handler. |

Jebakan klasik: Decimal bukan angka biasa

Kolom `harga` bertipe `Decimal`, dan Prisma membalasnya sebagai objek `Decimal` (hasil `JSON.stringify`-nya berupa **string** `"15000.5"`, bukan angka `15000.5`) supaya presisi uang tidak hilang. Kalau `mapRow` dihapus, Flutter akan menerima `"harga": "15000.5"` dan gagal mem-parse-nya sebagai `double`. Fungsi `mapRow()` di atas mengubahnya kembali ke `Number` — jangan dihapus. `count()` di Prisma sudah berupa `Number`, jadi tidak perlu dikonversi.

Semua query Prisma Client otomatis **parameterized**: nilai yang dikirim pengguna (`q`, `email`, dll) dikirim ke database sebagai parameter terpisah, tidak pernah disambung ke string SQL — sehingga aman dari SQL injection dengan cara yang sama seperti `pgx` di Go. Satu-satunya pengecualian adalah `prisma.$queryRawUnsafe(...)` (nama "Unsafe"-nya sengaja): jangan dipakai dengan input pengguna.

Kalau hapus/ubah target yang tidak ada

`prisma.umkm.delete({ where: { id } })` melempar error `P2025` (record not found) kalau barisnya tidak ada, sedangkan `DELETE FROM umkm WHERE id = $1` diam saja. Di proyek ini aman karena service selalu memanggil `findById` dulu dan melempar `NotFoundError` sebelum `remove()`/`update()` dipanggil.

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

### Penjelasan tiap fungsi auth

#### toSafeUser(user)

Membuat objek baru yang hanya berisi `id`, `nama`, dan `email`. Setiap data user yang keluar dari service melewati fungsi ini, supaya hash password tidak pernah terkirim.

#### register(nama, email, password)

1.  Semua field wajib ada dan password minimal 6 karakter; kalau tidak, `InvalidInputError` (400).
2.  `findByEmail`: kalau email sudah dipakai, `ConflictError` (409).
3.  `bcrypt.hash(password, 10)`: password diubah jadi hash satu arah. Angka 10 adalah *cost*; makin besar makin lambat ditebak.
4.  `userRepository.create` menyimpan **hash**-nya.
5.  Kembalikan `toSafeUser(user)`.

#### login(email, password)

1.  Cari user lewat email; tidak ada → `NotFoundError`.
2.  `bcrypt.compare(password, user.password)` mencocokkan password ketikan dengan hash; tidak cocok → `InvalidInputError`.
3.  Cocok → `generateToken(user.id)`, lalu kembalikan `{ token, user }`.

Kedua kegagalan memakai pesan yang sama, dan handler mengubahnya menjadi `401`.

#### profile(userId)

`userId` berasal dari token, bukan dari isian pengguna, sehingga orang hanya bisa melihat profilnya sendiri.

#### updateProfile(userId, nama, email)

Menolak field kosong, lalu menyimpan. Keunikan email dijaga database: memakai email milik akun lain menghasilkan error Prisma `P2002` yang saat ini dibalas `500` (lihat Latihan).

#### updatePassword(userId, passwordLama, passwordBaru)

Urutannya: ambil user → cocokkan password lama → periksa panjang password baru → hash → simpan. Token lama tetap berlaku sampai kedaluwarsa. Kalau field `password_lama` tidak dikirim sama sekali, `bcrypt` melempar error dan hasilnya `500`.

#### generateToken(userId)

`jwt.sign({ sub: userId }, JWT_SECRET, ...)` membuat token berisi `sub` (id user), `iat` (waktu dibuat), dan `exp` (24 jam kemudian). Server tidak menyimpan token; keabsahannya cukup diperiksa lewat tanda tangan.

Tiga hal yang persis sama dengan Go: (1) `bcrypt.hash`/`bcrypt.compare` satu arah, password asli tidak pernah tersimpan maupun dibandingkan sebagai teks biasa; (2) `login()` sengaja melempar pesan error **yang sama** ("email atau password salah") baik emailnya tidak ada maupun passwordnya salah, supaya penyerang tidak bisa menebak email mana yang terdaftar; (3) klaim JWT `sub` diisi id user, kedaluwarsa 24 jam — identik dengan `generateToken` di Go.

## 12Service Layer: UMKM & Produk

### pagination.js — dipakai bersama service

Kedua service di bawah memanggil file ini, jadi buat **lebih dulu**. Tanpanya server gagal menyala dengan `Cannot find module '../utils/pagination'`.

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

Query string selalu berupa teks dan bisa diisi apa saja. `normalizePagination` mengubahnya menjadi angka yang aman; service lalu menghitung `offset = (page - 1) * limit`.

| Permintaan           | page | limit | offset |
|----------------------|------|-------|--------|
| `(kosong)`           | 1    | 10    | 0      |
| `?page=3`            | 3    | 10    | 20     |
| `?page=2&limit=5`    | 2    | 5     | 5      |
| `?page=-4&limit=abc` | 1    | 10    | 0      |
| `?limit=1000`        | 1    | 100   | 0      |

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

| Fungsi | Urutan pemeriksaan | Hasil |
|----|----|----|
| `list(q, rawPage, rawLimit)` | Rapikan pagination | `{ data, total, page, limit }` |
| `detail(id)` | Ada? kalau tidak 404 | UMKM |
| `myUmkm(userId)` | Punya UMKM? kalau tidak 404 | UMKM milik sendiri |
| `createOwn(...)` | Nama wajib (400) → belum punya UMKM (409) | UMKM baru |
| `updateOwn(...)` | Nama wajib (400) → ada (404) → pemilik (403) | `{ umkm, fotoLama }`; `fotoLama` kosong bila foto tidak diganti |
| `deleteOwn(userId, umkmId)` | Ada (404) → pemilik (403) | UMKM yang dihapus, supaya fotonya bisa dibersihkan |

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

| Fungsi | Urutan pemeriksaan | Hasil |
|----|----|----|
| `listByUmkm(...)` | Rapikan pagination | Daftar produk (kosong bila UMKM tidak ada) |
| `detail(id)` | Ada? (404) | Produk |
| `createForOwnUmkm(...)` | Nama dan harga valid (400) → UMKM ada (404) → pemilik (403) | Produk baru |
| `authorizeOwner(userId, produkId)` | Produk ada (404) → UMKM induk ada (404) → pemilik (403) | Produk |
| `updateOwn(...)` | Input valid (400) → `authorizeOwner` | `{ produk, fotoLama }` |
| `deleteOwn(...)` | `authorizeOwner` | Produk yang dihapus |

Syarat `!(harga >= 0)` menolak angka negatif sekaligus `NaN`.

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

| Fungsi | Input | Memanggil | Balasan sukses |
|----|----|----|----|
| `register` | `req.body`: nama, email, password | `authService.register` | 201 data user |
| `login` | `req.body`: email, password | `authService.login` | 200 token dan user |
| `profile` | `req.userId` | `authService.profile` | 200 data user |
| `updateProfile` | `req.userId`, nama, email | `authService.updateProfile` | 200 pesan |
| `updatePassword` | `req.userId`, password_lama, password_baru | `authService.updatePassword` | 200 pesan |

Blok catch di login berbeda

Handler lain meneruskan error apa adanya, sedangkan `login` menimpa **semua** error menjadi `401`, termasuk saat database bermasalah. Kalau login selalu `401` padahal password benar, tambahkan sementara `console.error(err)` di awal blok `catch` untuk melihat penyebab aslinya.

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

`parseId(req)` mengubah `:id` dari URL menjadi angka dan menolak yang bukan bilangan bulat. `list` membaca `q`, `page`, `limit` dari query string. `create` dan `update` berjalan setelah multer, jadi teks ada di `req.body` dan file di `req.file`. Foto lama dihapus **setelah** database berhasil diubah. Kalau service menolak request, file yang telanjur diunggah tetap tersisa di `uploads/`.

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

Polanya sama dengan UMKM. Tambahannya, `harga` dikirim sebagai teks di form-data sehingga diubah dengan `Number.parseFloat`; kalau bukan angka, langsung `400` sebelum service dipanggil.

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

### Daftar endpoint

| Method dan path             | Login?           | Handler                      |
|-----------------------------|------------------|------------------------------|
| `POST /api/auth/register`   | tidak            | `authHandler.register`       |
| `POST /api/auth/login`      | tidak (dibatasi) | `authHandler.login`          |
| `GET /api/profile`          | ya               | `authHandler.profile`        |
| `PUT /api/profile`          | ya               | `authHandler.updateProfile`  |
| `PUT /api/profile/password` | ya               | `authHandler.updatePassword` |
| `GET /api/umkm`             | tidak            | `umkmHandler.list`           |
| `GET /api/umkm/saya`        | ya               | `umkmHandler.myUmkm`         |
| `GET /api/umkm/:id`         | tidak            | `umkmHandler.detail`         |
| `POST /api/umkm`            | ya               | `umkmHandler.create`         |
| `PUT /api/umkm/:id`         | ya               | `umkmHandler.update`         |
| `DELETE /api/umkm/:id`      | ya               | `umkmHandler.remove`         |
| `GET /api/umkm/:id/produk`  | tidak            | `produkHandler.listByUmkm`   |
| `POST /api/umkm/:id/produk` | ya               | `produkHandler.create`       |
| `GET /api/produk/:id`       | tidak            | `produkHandler.detail`       |
| `PUT /api/produk/:id`       | ya               | `produkHandler.update`       |
| `DELETE /api/produk/:id`    | ya               | `produkHandler.remove`       |

### Menelusuri alur auth dari awal sampai akhir

register

    POST /api/auth/register  {nama, email, password}
     app.js          cors -> express.json
     authHandler     register()        ambil req.body
     authService     register()        validasi input
     userRepository  findByEmail()     email sudah ada? -> 409
     authService     bcrypt.hash()     password jadi hash
     userRepository  create()          INSERT ke tabel users
     authService     toSafeUser()      buang hash
     authHandler     ok(res, 201)      {"data": {id, nama, email}}

login

    POST /api/auth/login  {email, password}
     rateLimit       loginLimiter      lebih dari 5x per menit? -> 429
     authHandler     login()
     authService     login()
     userRepository  findByEmail()     tidak ada -> 401
     authService     bcrypt.compare()  salah -> 401
     authService     generateToken()   JWT berlaku 24 jam
     authHandler     ok(res, 200)      {"data": {token, user}}

mengakses halaman yang butuh login

    GET /api/profile   Header: Authorization: Bearer TOKEN
     auth.js         requireAuth()     verifikasi token, isi req.userId -> kalau gagal 401
     authHandler     profile()
     authService     profile()
     userRepository  findById()
     authHandler     ok(res, 200)      {"data": {id, nama, email}}

Aplikasi Flutter menyimpan token hasil login dan mengirimkannya di setiap request berikutnya. Logout cukup dengan menghapus token di aplikasi.

## 15server.js & Menjalankan Project

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

Persis seperti `main.go`: tes koneksi database dulu sebelum membuka port (`db.Ping(ctx)` di Go, `prisma.$queryRaw` dengan `SELECT 1` di sini), dan menangani sinyal `SIGINT`/`SIGTERM` untuk mematikan server dengan rapi (menyelesaikan request yang sedang berjalan dulu, lalu `prisma.$disconnect()` menutup koneksi database) alih-alih langsung dibunuh paksa.

### Langkah menjalankan dari nol

1.  Pastikan `.env` sudah diisi lengkap (Bagian 06).
2.  Install dependency: `npm install` (otomatis menjalankan `prisma generate` lewat skrip `postinstall`; di komputer lain atau server boleh `npm ci`).
3.  Terapkan migrasi ke database: `npx prisma migrate deploy` (atau `npx prisma migrate dev` kalau kamu sedang mengembangkan skema — Bagian 05).
4.  Jalankan mode development (auto-restart): `npm run dev`.
5.  Harus muncul di terminal: `berhasil terhubung ke PostgreSQL` lalu `server berjalan di port 8080`.
6.  Tes cepat: buka `http://localhost:8080/healthz` di browser, atau `curl http://localhost:8080/healthz` — harus balas kosong dengan status `200`.

Checkpoint

Kalau langkah 5 berhasil (200 OK), seluruh fondasi (koneksi database, Prisma, Express, middleware) sudah benar. Lanjut ke Bagian 16 untuk menguji seluruh alur CRUD lengkap.

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
    # {"data":{"id":1,"user_id":1,"nama":"Warung Budi","deskripsi":"Jual kopi","alamat":"Jl. Melati 1","foto":""}}

    # bikin UMKM KEDUA untuk akun yang sama -> harus 409 (1 user = 1 UMKM)
    curl -s -w "\nHTTP:%{http_code}\n" -X POST http://localhost:8080/api/umkm \
      -H "Authorization: Bearer $TOKEN" -F "nama=Warung Dua"
    # {"error":{"message":"Anda sudah memiliki UMKM","code":"CONFLICT"}}  HTTP:409

    # tambah produk LENGKAP DENGAN FOTO sungguhan ke UMKM id=1
    curl -s -X POST http://localhost:8080/api/umkm/1/produk -H "Authorization: Bearer $TOKEN" \
      -F "nama=Kopi Susu" -F "harga=15000" -F "deskripsi=Kopi susu gula aren" \
      -F "foto=@/path/ke/foto.jpg"
    # {"data":{"id":1,"umkm_id":1,"nama":"Kopi Susu","harga":15000, ..., "foto":"produk/179...jpg"}}

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
    curl -s -X POST http://localhost:8080/api/auth/login -H "Content-Type: application/json" \
      -d '{"email":"siti@test.com","password":"rahasia123"}'
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

### 6. SQL injection tetap aman (Prisma otomatis parameterized)

terminal

    # pakai -G --data-urlencode supaya karakter aneh di query string tidak
    # merusak sintaks URL curl itu sendiri (ini soal shell/curl, bukan soal API)
    curl -s -G http://localhost:8080/api/umkm --data-urlencode "q=';DROP TABLE umkm;--"
    # {"data":[], "meta":{"page":1,"limit":10,"total":0}}  -- aman, tabel tidak hilang

    curl -s http://localhost:8080/api/umkm
    # {"data":[], ...}  -- tetap 200: tabel masih ada (kosong karena dihapus di langkah 5)

### 7. Rate limit login

terminal

    for i in 1 2 3 4 5 6; do
      curl -s -o /dev/null -w "percobaan $i: %{http_code}\n" \
        -X POST http://localhost:8080/api/auth/login \
        -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"salah"}'
    done
    # di server yang baru dinyalakan: percobaan 1-5 -> 401, percobaan ke-6 -> 429
    # login di langkah 1, 2, dan 4 ikut dihitung: kalau dijalankan berurutan dalam
    # 1 menit, 429 muncul lebih cepat. Tunggu 1 menit atau restart server.

Semua hasil di atas adalah hasil nyata

Ketujuh skenario ini dijalankan terhadap server Node.js + PostgreSQL 17 sungguhan (bukan database tiruan) sebelum materi ini ditulis. Kalau kamu mengikuti kode dari Bagian 02-15 persis seperti yang tertulis, hasil yang kamu dapatkan di komputermu sendiri akan identik.

## 17Troubleshooting Cepat

| Error yang muncul | Penyebab paling umum | Solusi |
|----|----|----|
| `P1001: Can't reach database server` | `DATABASE_URL` salah, atau Neon project sedang "sleep" (auto-suspend saat idle lama). | Cek ulang connection string di Neon Console, buka dashboard Neon sekali untuk membangunkan project-nya, lalu coba lagi. |
| `Environment variable not found: DATABASE_URL` | Berkas `.env` belum dibuat, salah nama, atau tidak berada di root proyek (sejajar `package.json`). | Salin `.env.example` jadi `.env` di root proyek dan isi `DATABASE_URL`-nya; jalankan Prisma CLI dari folder root itu. |
| `P3005: The database schema is not empty` | Database sudah berisi tabel (mis. dibuat versi Go) sehingga `migrate` tidak mau menimpa. | Pakai database kosong, atau lakukan baseline (lihat Bagian 05). |
| `EADDRINUSE: address already in use :::8080` | Server lama (dari `nodemon` atau terminal lain) masih berjalan di port yang sama. | Hentikan proses lama (`Ctrl+C` di terminal itu), atau ganti `PORT` di `.env`. |
| Field form (`nama`, dll) selalu `undefined` di endpoint upload | Lupa memasang `uploadSingle(...)` di route, atau mengirim request sebagai JSON padahal field-nya ditulis sebagai `multipart/form-data`. | Endpoint yang menerima foto (buat/update UMKM & produk) wajib dikirim sebagai *form-data* (pakai `-F` di curl, bukan `-d` dengan JSON), dan route-nya wajib melalui `uploadSingle(...)`. |
| `Cannot find module '../utils/pagination'` | File `src/utils/pagination.js` belum dibuat. | Buat file itu (Bagian 12). |
| Respons `500` dan terminal menulis `MulterError: Unexpected file field` | Nama field file di form-data tidak sama dengan nama field di `uploadSingle(subDir, fieldName)`. | Pastikan nama field upload selalu `foto` (huruf kecil semua), sama seperti didaftarkan di `app.js`. |
| `JsonWebTokenError: jwt malformed` | Header `Authorization` terkirim kosong, atau menempelkan teks lain (bukan token asli) setelah "Bearer ". | Login ulang, salin token hasil `data.token` persis, cek tidak ada spasi/baris baru tambahan yang ikut tersalin. |
| CORS error di console browser (saat dites dari Flutter Web) | Middleware `cors()` belum terpasang atau terpasang setelah route. | Pastikan `app.use(cors())` ada di baris paling atas `app.js`, sebelum route apa pun didaftarkan. |
| Response menggantung tanpa balasan sama sekali (tidak error, tidak sukses) | Lupa `try/catch` di salah satu fungsi handler `async`, sehingga exception tidak pernah sampai ke `next(err)`. | Cek ulang semua handler punya pola `try { ... } catch (err) { next(err); }` seperti dijelaskan di Bagian 13. |
| `harga` di JSON berupa `"15000"` (string, bertanda kutip) | Lupa mengonversi kolom `Decimal` dengan `Number(...)` di `produkRepository` (fungsi `mapRow`). | Lihat kembali `mapRow()` di Bagian 10 — pastikan dipakai di `create`, `findById`, dan `findByUmkmId`. |
| `@prisma/client did not initialize yet` / `Cannot find module '.prisma/client'` | Prisma Client belum di-generate (mis. habis `git clone`, atau `postinstall` terlewat). | Jalankan `npx prisma generate`, lalu jalankan ulang server. |

## 18Perbandingan Go vs Node.js

Satu proyek, dua bahasa — tabel ini meringkas padanan tiap konsep, supaya kalau suatu saat perlu membaca atau menulis salah satu versi, versi yang satunya terasa seperti sudah pernah dilihat sebelumnya:

| Konsep | Golang (umkm-api) | Node.js (umkm-api-node) |
|----|----|----|
| Web framework | `net/http` + `http.ServeMux` (bawaan Go 1.22+) | Express |
| ORM / driver database | `pgx` + `pgxpool.Pool` (SQL ditulis manual) | Prisma Client (query lewat method, SQL dibuat otomatis) di atas koneksi `PrismaClient` |
| Error "tidak ketemu" dari DB | `pgx.ErrNoRows` → dikonversi manual jadi `domain.ErrNotFound` | `findUnique` mengembalikan `null` → service yang melempar `NotFoundError` |
| Penanganan error di handler | `switch { case errors.Is(err, ...) }` diulang di tiap handler | `throw` kelas error kustom, ditangkap satu `errorHandler` terpusat |
| Middleware auth | `func(http.Handler) http.Handler`, userID disisipkan ke `context.Context` | fungsi `(req, res, next)` biasa, userID ditempel langsung ke `req.userId` |
| Rate limiting | `golang.org/x/time/rate`, `map[string]*rate.Limiter` ditulis manual per IP | `express-rate-limit`, penghitung per IP sudah dibungkus library |
| Hashing password | `golang.org/x/crypto/bcrypt` | `bcrypt` (binding native ke algoritma yang sama) |
| JWT | `golang-jwt/jwt/v5`, klaim lewat `jwt.MapClaims` | `jsonwebtoken`, klaim lewat object literal biasa |
| Upload file | `r.ParseMultipartForm` + `io.Copy` manual | `multer` (`diskStorage` + `fileFilter`) |
| Tipe data numerik dari DB | di-`Scan` otomatis ke tipe Go asli (`int`, `float64`) | `count()` sudah `Number`, tapi kolom `Decimal` (harga) berupa objek/string → wajib `Number()` manual |
| Concurrency model | goroutine, tiap request punya *thread* ringan sendiri | single-threaded + event loop, `async/await` untuk I/O non-blocking |
| Dokumentasi API | Swagger via komentar `// @Summary` dkk (swaggo) | bisa ditambah `swagger-jsdoc` + `swagger-ui-express` dengan pola komentar serupa (di luar cakupan materi ini) |
| Skema & migrasi | `golang-migrate` — berkas `.sql` bernomor ditulis tangan | Prisma Migrate — tulis `schema.prisma`, SQL migrasi dibuat otomatis |

Satu pelajaran terpenting dari perbandingan ini

Baris kode berbeda, library berbeda, bahkan model concurrency-nya berbeda total (goroutine vs event loop) — tapi **arsitektur** (handler → service → repository), **aturan bisnis** (1 user 1 UMKM, ownership check, validasi), dan **skema database**-nya persis sama. Itulah yang dimaksud "belajar konsep, bukan sekadar sintaks" — begitu paham UMKM API di satu bahasa, mempelajari versi bahasa lain jauh lebih cepat karena tinggal mencari padanannya, bukan belajar dari nol.

Perbedaan perilaku yang masih ada

Endpoint dan alur utamanya sama, tetapi di kasus tepi ada beda: field `deskripsi`/`alamat` yang tidak dikirim tersimpan `NULL` di Node (Go: teks kosong) dan saat update nilai lamanya dipertahankan (Go: dikosongkan); email kembar saat ubah profil dibalas `500` (Go: `400`). Aplikasi `umkm-app` selalu mengirim semua field, jadi dua hal pertama tidak muncul dari aplikasi.

## 19Latihan

1.  Perbaiki `updateProfile` di `authService`: tangkap error Prisma `P2002` dan lempar `ConflictError` supaya email kembar dibalas `409`, bukan `500`.
2.  Tambahkan endpoint `GET /api/umkm/:id/produk/:produkId` yang memvalidasi produk tersebut benar-benar milik UMKM dengan `:id` itu (bukan cuma dicari lewat `produkId` saja) — balas `404` kalau tidak cocok.
3.  Tambahkan validasi panjang maksimal `nama` (mis. 150 karakter) di `umkmService.createOwn`, balas `InvalidInputError` kalau melebihi — cek juga `@db.VarChar(150)` di `schema.prisma` supaya konsisten.
4.  Ganti `express-rate-limit` default (disimpan di memori) menjadi versi yang disimpan di Redis, supaya rate limit tetap konsisten walau server di-restart atau dijalankan lebih dari satu instance.
5.  **Tantangan:** tambahkan `swagger-jsdoc` + `swagger-ui-express`, tulis dokumentasi untuk seluruh endpoint di atas memakai komentar JSDoc, supaya ada halaman `/docs` yang setara `/swagger/` di versi Go.
6.  **Tantangan integrasi:** jalankan server Node ini di port berbeda dari versi Go (mis. 8081), lalu ubah `baseUrl` di `ApiService` Flutter (Pertemuan 7) untuk sementara menunjuk ke situ — buktikan aplikasi `umkm-app` yang sama persis bisa jalan tanpa perubahan kode Flutter sedikit pun, baik menunjuk ke backend Go maupun Node.
7.  Tambahkan model `Kategori` (id, nama) di `schema.prisma` dengan relasi satu-ke-banyak ke `Produk`, lalu jalankan `npx prisma migrate dev --name tambah_kategori`. Buka berkas SQL baru di `prisma/migrations/` dan jelaskan apa yang berubah dibanding migrasi `init`.
8.  Ubah endpoint detail UMKM supaya sekalian menyertakan daftar produknya dalam **satu** query memakai `include` (`prisma.umkm.findUnique({ where: { id }, include: { produk: true } })`). Bandingkan dengan pendekatan dua query terpisah (`findById` + `findByUmkmId`) — apa untung-ruginya?

Dengan panduan ini, proyek `umkm-api` yang sama bisa dibangun ulang dari nol dengan stack Node.js + Express + Prisma + PostgreSQL kapan pun dibutuhkan — seluruh endpoint, aturan bisnis, dan skema database identik dengan versi Golang di Pertemuan 4/9, dan setiap baris kodenya sudah diuji berjalan nyata sebelum materi ini ditulis. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
