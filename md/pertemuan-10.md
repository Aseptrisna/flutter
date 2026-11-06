<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 10 · Praktikum 1/5 · Proyek Sendiri

# Identifikasi Masalah & Desain Proyek Sendiri

Ini pertemuan praktikum pertama dari rangkaian 5 pertemuan (10-14) yang menerjemahkan studi kasus **UMKM API + umkm-app** (Pertemuan 9) jadi langkah kerja nyata. Bedanya: setiap konsep di sini langsung kamu terapkan ke **proyek UAS kamu sendiri** yang sudah dimulai sejak Pertemuan 8 — bukan UMKM lagi, tapi ide aplikasi kamu sendiri. Tiap bagian ditutup kotak ungu **"Tugas Kamu"** — kerjakan itu sebelum lanjut ke bagian berikutnya.

← [Pertemuan 9: Studi Kasus Lengkap](pertemuan-09.html)
[Pertemuan 11: Backend Sendiri](pertemuan-11.html) →

## 01Tentang Pertemuan Ini

Pertemuan 9 membedah **UMKM API** (Golang/Node.js) dan **umkm-app** (Flutter) sebagai studi kasus lengkap, dibungkus dalam kerangka 5 tahap pengembangan software. Lima pertemuan berikutnya (10-14) memakai kerangka yang sama, tapi setiap langkahnya kamu kerjakan untuk **aplikasi UAS kamu sendiri** — ide, nama entitas, dan kebutuhannya boleh beda total dari UMKM, tapi *caranya* dipandu persis sama, supaya hasil akhirnya tetap terarah walau proyeknya beragam.

| Pertemuan | Fokus | Hasil yang kamu bawa pulang |
|----|----|----|
| **10 (ini)** | Identifikasi masalah + desain (UX, arsitektur, database, kontrak API) | Dokumen desain lengkap untuk app sendiri |
| 11 | Membangun backend sendiri (arsitektur, auth, repository/SQL, upload) | Backend API sendiri yang jalan |
| 12 | Fundamental layout Flutter + konek API + halaman awal (splash/login/register) | Alur auth jalan nyata di app sendiri |
| 13 | Halaman CRUD lengkap & ApiService | CRUD penuh untuk entitas utama app sendiri |
| 14 | Trace request, testing, deployment & rangkuman | Dokumen trace + checklist kesiapan UAS |

Kenapa dipecah, bukan satu pertemuan besar seperti Pertemuan 9?

Karena Pertemuan 9 sifatnya *membaca & memahami* proyek yang sudah jadi (UMKM), sedangkan rangkaian ini sifatnya *mengerjakan dari nol* proyek yang belum jadi (punyamu). Mengerjakan butuh waktu dan tahapan yang tidak bisa dipadatkan jadi satu sesi — makanya dipecah, satu pertemuan satu fase kerja yang jelas selesainya.

## 02Tahapan Membangun Aplikasi Android dari Nol

Tidak ada aplikasi yang baik lahir langsung dari `flutter create`. Ada lima tahap yang selalu dilalui, baik disadari maupun tidak — mengabaikan salah satunya biasanya terasa belakangan dalam bentuk bug, fitur yang salah sasaran, atau kode yang sulit diubah.

1.  **Identifikasi masalah & kebutuhan** — apa masalah nyata yang ingin diselesaikan, siapa penggunanya. *(Bagian 03 di bawah)*
2.  **Desain** — UX/alur layar, arsitektur sistem, skema database, kontrak API. *(Bagian 04-07)*
3.  **Development** — menulis backend dan frontend berdasarkan desain. *(Pertemuan 11-13)*
4.  **Testing** — memverifikasi bahwa yang dibangun benar-benar bekerja. *(Pertemuan 14)*
5.  **Deployment & maintenance** — merilis dan menjaga aplikasi tetap hidup. *(Pertemuan 14)*

Pertemuan 10 ini mencakup tahap 1 dan 2 secara penuh — tahap 3-5 dikerjakan di pertemuan-pertemuan berikutnya setelah desainmu benar-benar matang.

## 03Tahap 1: Identifikasi Masalah & Kebutuhan

Sebelum baris kode pertama ditulis, pertanyaan yang harus dijawab: **masalah apa** yang diselesaikan, dan **untuk siapa**. Untuk proyek UMKM (Pertemuan 9), masalahnya sederhana: pelaku UMKM kecil tidak punya etalase digital yang mudah dibuat sendiri. Dari masalah itu, diturunkan kebutuhan fungsional minimal — inilah yang nantinya menentukan tabel database dan endpoint API:

- Pengguna bisa mendaftar & login (butuh identitas, jadi butuh tabel `users`).
- Satu pengguna bisa mendaftarkan **satu** UMKM miliknya (keputusan bisnis: 1 user = 1 UMKM).
- Satu UMKM punya banyak produk (relasi satu-ke-banyak: `umkm` → `produk`).
- Orang lain (tanpa login) harus bisa menjelajah daftar UMKM & produk — sebagian endpoint publik, sebagian butuh autentikasi.

### Cara mengumpulkan & merumuskan kebutuhan

| Teknik | Tools | Kapan dipakai |
|----|----|----|
| Wawancara/observasi singkat | Catatan manual, atau Google Forms kalau respondennya banyak | Saat masalahnya menyangkut orang lain — bukan cuma asumsi sendiri. |
| Analisis kompetitor | Cari 2-3 aplikasi sejenis di Play Store, catat fitur yang ada/tidak ada | Untuk tahu fitur standar di kategori aplikasimu, dan celah yang bisa jadi pembeda. |
| User persona | Template 1 halaman: nama fiktif, peran, tujuan, frustrasi | Supaya "siapa penggunanya" tidak abstrak. |
| Daftar kebutuhan fungsional & non-fungsional | Daftar centang sederhana (Notion, Google Docs, atau `.md`) | Hasil akhir tahap ini — acuan desain & scope, mencegah *scope creep*. |

Tugas Kamu

Tulis untuk aplikasi UAS kamu sendiri (format bebas, 1 dokumen — Google Docs/Notion/markdown):

1.  **Masalah**: satu-dua kalimat, masalah nyata apa yang diselesaikan aplikasimu, untuk siapa.
2.  **Minimal 5 kebutuhan fungsional**, ditulis dalam format "Pengguna bisa \_\_\_" (contoh gaya di atas) — termasuk tentukan entitas utama aplikasimu (padanan "UMKM" dan "produk" di app kamu) dan relasinya (1-ke-1? 1-ke-banyak?).
3.  **Minimal 2 kebutuhan non-fungsional** (contoh: "foto harus bisa diakses publik tanpa login", "percobaan login dibatasi").
4.  Tandai mana endpoint yang nanti **publik** dan mana yang **butuh login** — ini menentukan middleware apa yang dipakai di tahap development nanti.

## 04Tahap 2: Desain — UX & Arsitektur Sistem

Desain punya beberapa lapis yang saling bergantung — mengerjakannya berurutan membuat tahap development jauh lebih cepat karena tidak ada keputusan besar yang harus diubah di tengah jalan.

### a. Desain alur & UX

Gambarkan dulu layar apa saja yang dibutuhkan dan bagaimana pengguna berpindah di antaranya, sebelum memikirkan widget Flutter apa yang dipakai. Ada tiga level kedalaman, dipilih sesuai waktu yang tersedia — untuk tugas kuliah, level 1-2 biasanya sudah cukup:

| Level | Tools | Output |
|----|----|----|
| **1. User flow** | Pensil & kertas, atau <a href="https://excalidraw.com" target="_blank" rel="noopener">Excalidraw</a> / <a href="https://draw.io" target="_blank" rel="noopener">draw.io</a> | Diagram kotak-panah: Splash → Login/Register → Home → Detail → Form, dst. |
| **2. Wireframe** | <a href="https://www.figma.com" target="_blank" rel="noopener">Figma</a> (gratis untuk pelajar) atau <a href="https://balsamiq.com" target="_blank" rel="noopener">Balsamiq</a> | Kotak abu-abu berlabel per layar — posisi tombol, form, list. |
| **3. Mockup/prototype** | Figma (frame + prototyping mode) | Tampilan mendekati final, bisa diklik untuk simulasi alur. |

### b. Desain arsitektur sistem

Memutuskan: aplikasi mobile-only atau butuh backend terpisah? Kalau butuh backend, dipecah jadi layer apa saja? UMKM API memilih arsitektur **handler → service → repository → domain** (lihat Pertemuan 9 Bagian 08) — keputusan ini diambil di tahap desain, bukan ditemukan sambil menulis kode. Kamu akan memakai pola arsitektur yang **sama persis** di Pertemuan 11, jadi tidak perlu dipikirkan ulang dari nol — tinggal diterapkan ke entitas aplikasimu.

Tugas Kamu

Untuk aplikasi UAS kamu:

1.  Buat **user flow** (minimal level 1) — Splash → Login/Register → Home → … sesuai alur aplikasimu sendiri. Simpan sebagai gambar/screenshot.
2.  Tentukan: aplikasimu butuh backend terpisah atau cukup mobile-only? Kalau butuh backend, tuliskan kamu akan pakai **Go** (seperti Pertemuan 9) atau **Node.js** (seperti Pertemuan 9a) — ini menentukan materi mana yang kamu ikuti di Pertemuan 11.

## 05Desain Database: ERD & Tool Relasi

Dari kebutuhan fungsional di Bagian 03, diturunkan skema tabel memakai diagram **ERD (Entity Relationship Diagram)**.

#### Tool untuk menggambar relasi antar tabel

| Tool | Cara kerja | Kenapa cocok untuk pemula |
|----|----|----|
| <a href="https://dbdiagram.io" target="_blank" rel="noopener"><strong>dbdiagram.io</strong></a> (rekomendasi) | Ketik definisi tabel pakai bahasa **DBML**, diagram ERD lengkap dengan garis relasi muncul otomatis. | Gratis tanpa akun, cukup tulis `ref:` sekali dan garis "satu-ke-banyak" langsung tergambar. |
| <a href="https://drawsql.app" target="_blank" rel="noopener">DrawSQL</a> | Mirip dbdiagram.io tapi lewat UI drag-and-drop. | Cocok yang lebih nyaman visual murni dibanding menulis sintaks DBML. |
| <a href="https://draw.io" target="_blank" rel="noopener">draw.io</a> / Excalidraw | Kanvas bebas, digambar manual sepenuhnya. | Paling fleksibel, tapi garis relasi harus ditarik & dilabeli sendiri. |

Contoh skema UMKM App dalam sintaks DBML (dari Pertemuan 9) — tempel ke <a href="https://dbdiagram.io" target="_blank" rel="noopener">dbdiagram.io</a> untuk melihat polanya:

dbdiagram.io — skema UMKM App (DBML), contoh acuan

    Table users {
      id integer [primary key]
      nama varchar
      email varchar [unique]
      password varchar
    }

    Table umkm {
      id integer [primary key]
      user_id integer [unique]
      nama varchar
      deskripsi text
      alamat varchar
      foto varchar
    }

    Table produk {
      id integer [primary key]
      umkm_id integer
      nama varchar
      harga decimal
      deskripsi text
      foto varchar
    }

    Ref: umkm.user_id > users.id // satu user, satu umkm (unique di sisi umkm)
    Ref: produk.umkm_id > umkm.id // satu umkm, banyak produk

Skema asli ini diterjemahkan jadi SQL sungguhan begini (lihat juga Pertemuan 9 Bagian 04):

schema.sql — contoh acuan dari UMKM API

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

- **`SERIAL PRIMARY KEY`** — kunci utama tiap baris, unik & otomatis naik sendiri.
- **`REFERENCES ... ON DELETE CASCADE`** — foreign key; Postgres menolak nilai yang tidak pernah terdaftar di tabel induk, dan menghapus baris induk otomatis menghapus semua baris anak yang menunjuk ke situ.
- **`UNIQUE`** — menegakkan aturan "1-ke-1" di level database, bukan cuma di kode aplikasi.

Tugas Kamu

Untuk aplikasi UAS kamu:

1.  Tentukan minimal **2-3 tabel** berdasarkan kebutuhan fungsional dari Bagian 03 (selalu ada tabel `users` untuk login, plus minimal 1-2 tabel untuk entitas utama aplikasimu).
2.  Gambar ERD-nya di <a href="https://dbdiagram.io" target="_blank" rel="noopener">dbdiagram.io</a> memakai DBML seperti contoh — pastikan ada minimal satu relasi (`Ref:`) antar tabel.
3.  Tulis ulang jadi `CREATE TABLE` SQL asli, mengikuti pola `SERIAL PRIMARY KEY`/`REFERENCES`/`UNIQUE` seperti contoh — simpan sebagai `schema.sql`, ini akan langsung dipakai di Pertemuan 11.

## 06Fundamental SQL: 7 Aksi Nyata

Supaya tidak abstrak, berikut ditelusuri urutan aksi yang sebenarnya dilakukan pengguna — **Register → Login → Buat Data → Lihat Daftar → Lihat Detail (relasi/JOIN) → Edit → Hapus** — satu per satu, satu query sederhana per aksi. Ini ringkasan dari Pertemuan 9 Bagian 04 (bagian "Lima perintah dasar") — kalau kamu sudah pernah mengerjakan try-box di sana, bagian ini tinggal jadi pengingat cepat.

| Aksi | Perintah SQL | Inti yang perlu diingat |
|----|----|----|
| Register | `INSERT INTO users (...) VALUES (...) RETURNING id;` | Postgres langsung membalas `id` baris baru lewat `RETURNING`. |
| Login | `SELECT ... FROM users WHERE email = ...;` | SQL cuma mengambil barisnya — mencocokkan password terjadi di kode backend (bcrypt), bukan di `WHERE`. |
| Buat data | `INSERT INTO umkm (user_id, ...) VALUES (...);` | `user_id` diambil dari akun yang sedang login, bukan diketik manual pengguna. |
| Lihat daftar | `SELECT ... WHERE nama ILIKE '%...%' ORDER BY id DESC LIMIT ... OFFSET ...;` | `ILIKE` = pencarian tanpa peduli huruf besar/kecil; `LIMIT/OFFSET` = pagination. |
| Lihat detail (relasi) | `SELECT ... FROM a JOIN b ON b.a_id = a.id WHERE ...;` | `JOIN` menyatukan data dari tabel berbeda jadi satu baris hasil, berdasarkan foreign key. |
| Edit | `UPDATE umkm SET ... WHERE id = ...;` | Semua kolom ditulis ulang sekaligus, bukan per-kolom. |
| Hapus | `DELETE FROM umkm WHERE id = ...;` | Berkat `ON DELETE CASCADE`, baris anak ikut terhapus otomatis. |

Mau yang lebih detail?

Penjelasan lengkap tiap query (dengan contoh literal, penjelasan baris-per-baris, dan kotak "Coba Sendiri" yang bisa langsung ditempel di Neon SQL Editor) ada di [Pertemuan 9 Bagian 04](pertemuan-09.html#s4). Tabel di atas cukup sebagai pengingat urutannya.

Tugas Kamu

Buka Neon Console (boleh bikin project baru khusus aplikasi UAS-mu, terpisah dari project UMKM). Jalankan `schema.sql` hasil Bagian 05 di SQL Editor-nya. Lalu, memakai pola 7 aksi di atas tapi dengan **nama tabel & data milikmu sendiri**:

1.  Jalankan `INSERT` manual untuk membuat 1 baris data latihan (akun + 1 baris entitas utama), catat `id`-nya.
2.  Jalankan `SELECT ... WHERE`, `SELECT ... ILIKE ... LIMIT/OFFSET`, dan (kalau tabelmu lebih dari 1 dan berelasi) `JOIN` memakai data latihan itu.
3.  Jalankan `UPDATE` lalu `SELECT` ulang untuk membuktikan perubahannya.
4.  Kalau ada relasi dengan `ON DELETE CASCADE`, buktikan dengan `DELETE` baris induk dan cek baris anak ikut hilang.

Skema & data latihan yang sudah tervalidasi di sini langsung dipakai lagi di Pertemuan 11 saat menulis kode *repository*.

## 07Desain Kontrak API

Khusus proyek yang punya backend terpisah, ada satu desain tambahan yang sering terlewat: **bentuk request/response tiap endpoint** disepakati di atas kertas dulu sebelum Flutter dan backend ditulis bersamaan. UMKM API memakai Swagger/OpenAPI untuk ini. Untuk tugas kuliah, cukup tabel sederhana berisi: method, path, siapa yang boleh akses, dan bentuk data yang dikirim/dibalas.

| Method & Path | Akses | Keterangan |
|----|----|----|
| `POST /api/auth/register` | Publik | Body: `nama`, `email`, `password` |
| `POST /api/auth/login` | Publik | Balas: `token` + data user |
| `GET /api/<entitas>` | Publik | Daftar, mendukung `?q=` & pagination |
| `POST /api/<entitas>` | Butuh login | Multipart kalau ada upload foto |
| `PUT` / `DELETE /api/<entitas>/:id` | Butuh login + pemilik | Tolak kalau bukan pemilik data (403) |

Kesalahan paling umum pemula

Langsung menulis kode Flutter sebelum tahu endpoint API apa saja yang dibutuhkan, lalu membangun backend belakangan sambil menebak-nebak bentuk responsnya. Hasilnya: bolak-balik mengubah kedua sisi. Desain dulu bentuk API di atas kertas sebelum menulis Flutter yang memanggilnya.

Tugas Kamu

Buat tabel kontrak API seperti contoh di atas, untuk **semua endpoint** yang dibutuhkan aplikasi UAS-mu (minimal: register, login, dan CRUD lengkap untuk entitas utamamu). Tandai jelas mana yang publik, mana yang butuh login, dan mana yang butuh validasi kepemilikan (403 kalau bukan pemilik). Dokumen ini jadi acuan langsung saat menulis route di Pertemuan 11.

## 08Rangkuman & Checklist

Sebelum lanjut ke Pertemuan 11, pastikan kamu sudah punya 4 dokumen/berkas ini untuk aplikasi UAS-mu sendiri:

- Dokumen kebutuhan: masalah, minimal 5 kebutuhan fungsional, minimal 2 non-fungsional, daftar endpoint publik vs butuh login.
- User flow (gambar/screenshot) minimal level 1, dan keputusan stack backend (Go atau Node.js).
- ERD (dbdiagram.io) + berkas `schema.sql` yang sudah divalidasi langsung di Neon (berhasil di-`INSERT`/`SELECT`/`UPDATE`/`DELETE` dengan data latihan).
- Tabel kontrak API lengkap untuk semua endpoint yang dibutuhkan.

Checkpoint sebelum Pertemuan 11

Kalau keempat dokumen di atas sudah ada, kamu sudah siap masuk tahap development. Pertemuan 11 akan langsung memakai `schema.sql` dan tabel kontrak API ini sebagai bahan baku — tidak ada desain ulang dari nol di situ, murni implementasi dari apa yang sudah kamu rancang di pertemuan ini.

← [Pertemuan 9: Studi Kasus Lengkap](pertemuan-09.html)
[Pertemuan 11: Backend Sendiri](pertemuan-11.html) →

Bagian 1 dari 5 rangkaian praktikum proyek UAS — lanjut ke [Pertemuan 11: Membangun Backend Sendiri](pertemuan-11.html). — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
