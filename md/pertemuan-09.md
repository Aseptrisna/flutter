<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 9 · Tinjauan & Studi Kasus

# Tahapan Membangun Aplikasi & Bedah Proyek UMKM

Pertemuan ini tidak memperkenalkan fitur baru — tujuannya adalah **menengok ke belakang**: memahami tahapan umum membangun aplikasi Android dari nol, lalu memetakan tahapan itu ke proyek nyata yang sudah dibangun bersama sejak Pertemuan 4 dan 7 — **UMKM API** (Golang) dan **umkm-app** (Flutter) — dibedah *per fungsi* dan *per halaman*, lengkap dengan alasan setiap keputusan desainnya.

## 01Tentang Pertemuan Ini

Sampai Pertemuan 8, kalian sudah menulis banyak kode: backend Go dengan JWT dan upload foto, lalu aplikasi Flutter penuh yang terhubung ke backend itu. Masalahnya, saat menulis kode sambil mengikuti tutorial langkah demi langkah, mudah sekali kehilangan **gambaran besar** — kenapa kode dipecah jadi handler/service/repository, kenapa ada middleware, kenapa satu fungsi dipakai untuk create *dan* update sekaligus.

Pertemuan 9 menjawab itu dalam dua bagian:

- **Bagian pertama** — tahapan umum membangun aplikasi Android dari masalah sampai rilis, berlaku untuk proyek apa pun (termasuk proyek UAS kalian nanti).
- **Bagian kedua** — bedah detail `umkm-api` dan `umkm-app` sebagai contoh konkret dari tahapan tersebut, per fungsi dan per halaman.

## 02Tahapan Membangun Aplikasi Android dari Nol

Tidak ada aplikasi yang baik lahir langsung dari `flutter create`. Ada lima tahap yang selalu dilalui, baik disadari maupun tidak — mengabaikan salah satunya biasanya terasa belakangan dalam bentuk bug, fitur yang salah sasaran, atau kode yang sulit diubah.

1.  **Identifikasi masalah & kebutuhan** — apa masalah nyata yang ingin diselesaikan, siapa penggunanya.
2.  **Desain** — UX/alur layar, arsitektur sistem, skema database.
3.  **Development** — menulis backend dan frontend berdasarkan desain, bukan sambil menebak-nebak.
4.  **Testing** — memverifikasi bahwa yang dibangun benar-benar bekerja, termasuk kasus gagal.
5.  **Deployment & maintenance** — merilis dan menjaga aplikasi tetap hidup setelah rilis.

Kenapa UMKM API & umkm-app jadi contoh di pertemuan ini?

Karena kalian sudah membangunnya sendiri sejak Pertemuan 4-7, sehingga tiap tahap di bawah bisa langsung ditunjuk ke kode yang sudah pernah kalian tulis — bukan contoh abstrak dari proyek orang lain.

## 03Tahap 1: Identifikasi Masalah & Kebutuhan

Sebelum baris kode pertama ditulis, pertanyaan yang harus dijawab: **masalah apa** yang diselesaikan, dan **untuk siapa**. Untuk proyek UMKM, masalahnya sederhana: pelaku UMKM kecil tidak punya etalase digital yang mudah dibuat sendiri, dan calon pembeli kesulitan menemukan UMKM di sekitar mereka beserta produknya.

Dari masalah itu, diturunkan kebutuhan fungsional minimal — inilah yang nantinya menentukan tabel database dan endpoint API:

- Pengguna bisa mendaftar & login (butuh identitas, jadi butuh tabel `users`).
- Satu pengguna bisa mendaftarkan **satu** UMKM miliknya (keputusan bisnis: 1 user = 1 UMKM, bukan banyak).
- Satu UMKM punya banyak produk (relasi satu-ke-banyak: `umkm` → `produk`).
- Orang lain (tanpa login) harus bisa menjelajah daftar UMKM & produk — artinya sebagian endpoint harus publik, sebagian lagi butuh autentikasi.

### Cara mengumpulkan & merumuskan kebutuhan

Dalam konteks tugas kuliah, tahap ini tidak harus formal, tapi tetap perlu ditulis, bukan cuma dipikirkan di kepala:

| Teknik | Tools | Kapan dipakai |
|----|----|----|
| Wawancara/observasi singkat | Catatan manual, atau Google Forms kalau respondennya banyak | Saat masalahnya menyangkut orang lain (mis. survei ke pelaku UMKM sungguhan) — bukan cuma asumsi sendiri. |
| Analisis kompetitor | Cari 2-3 aplikasi sejenis di Play Store, catat fitur yang ada/tidak ada | Untuk tahu fitur apa yang sudah jadi standar di kategori aplikasi tersebut, dan celah apa yang bisa jadi pembeda. |
| User persona | Template 1 halaman (bisa di Figma/Canva/dokumen biasa): nama fiktif, peran, tujuan, frustrasi | Supaya "siapa penggunanya" tidak abstrak — setiap keputusan desain bisa dicek balik: "apakah ini membantu persona ini?" |
| Daftar kebutuhan fungsional & non-fungsional | Daftar centang sederhana (Notion, Google Docs, atau `.md` di repo) | Hasil akhir tahap ini — daftar singkat "aplikasi harus bisa X, Y, Z" yang dipakai sebagai acuan desain & scope, supaya tidak menambah fitur di tengah jalan tanpa sadar (*scope creep*). |

Kebutuhan **non-fungsional** juga perlu ditulis walau sering dilupakan pemula — contohnya untuk UMKM API: foto produk harus bisa diakses publik tanpa login (karena itu endpoint `/uploads/` disajikan statis, tidak dibungkus auth), dan percobaan login harus dibatasi (karena itu ada rate limiting khusus di endpoint login).

Ini menentukan segalanya di tahap berikutnya

Baris terakhir di atas — "sebagian publik, sebagian butuh login" — adalah alasan langsung kenapa `main.go` di UMKM API membungkus sebagian route dengan middleware `RequireAuth` dan sebagian tidak (dibahas di Bagian 09). Kebutuhan fungsional yang ditulis di tahap ini langsung menjelma jadi struktur kode di tahap development.

## 04Tahap 2: Desain

Desain punya tiga lapis yang saling bergantung — mengerjakannya berurutan (bukan langsung loncat ke kode) membuat tahap development jauh lebih cepat karena tidak ada keputusan besar yang harus diubah di tengah jalan.

### a. Desain alur & UX

Gambarkan dulu layar apa saja yang dibutuhkan dan bagaimana pengguna berpindah di antaranya, sebelum memikirkan widget Flutter apa yang dipakai. Ada tiga level kedalaman, dipilih sesuai waktu yang tersedia — untuk tugas kuliah, level 1-2 biasanya sudah cukup:

| Level | Tools | Output |
|----|----|----|
| **1. User flow** (alur berpindah layar) | Pensil & kertas, atau <a href="https://excalidraw.com" target="_blank" rel="noopener">Excalidraw</a> / <a href="https://draw.io" target="_blank" rel="noopener">draw.io</a> (gratis, langsung di browser) | Diagram kotak-panah: Splash → Login/Register → Home → Detail → Form, dst. Ini yang nantinya jadi peta `routes`/`Navigator`. |
| **2. Wireframe** (sketsa kasar tiap layar) | <a href="https://www.figma.com" target="_blank" rel="noopener">Figma</a> (gratis untuk pelajar, kolaboratif) atau <a href="https://balsamiq.com" target="_blank" rel="noopener">Balsamiq</a> | Kotak abu-abu berlabel per layar — posisi tombol, form, list — tanpa warna/font final, fokus ke tata letak dan kelengkapan elemen. |
| **3. Mockup/prototype** (tampilan hampir final + interaksi) | Figma (frame + Auto Layout + prototyping mode untuk klik-navigasi antar frame) | Tampilan mendekati hasil akhir, bisa diklik untuk simulasi alur sebelum satu baris kode Flutter pun ditulis — memudahkan deteksi alur yang membingungkan sejak dini. |

Untuk UMKM App, hasil tahap ini adalah: Splash → Login/Register → Home (tab Semua UMKM / UMKM Saya / Profil) → Detail UMKM → Form tambah/edit. Alur inilah yang akhirnya menentukan struktur `lib/screens/` yang kalian pakai sejak Pertemuan 6-7 — nama folder/file screen sengaja dibuat mengikuti nama layar di alur ini, bukan nama teknis yang sewenang-wenang.

### b. Desain arsitektur sistem

Memutuskan: aplikasi mobile-only atau butuh backend terpisah? Kalau butuh backend, dipecah jadi layer apa saja? Tools untuk tahap ini biasanya sama seperti user flow di atas (draw.io/Excalidraw/Figma) — dibuat diagram kotak yang merepresentasikan layer kode (bukan layar UI). UMKM API memilih arsitektur **handler → service → repository → domain** (lihat Bagian 08) — keputusan ini diambil di tahap desain, bukan ditemukan sambil menulis kode.

### c. Desain database

Dari kebutuhan fungsional di Tahap 1, diturunkan skema tabel memakai diagram **ERD (Entity Relationship Diagram)** — dibuat dengan tool seperti <a href="https://dbdiagram.io" target="_blank" rel="noopener">dbdiagram.io</a> (gratis, cukup ketik definisi tabel dalam teks dan diagramnya digambar otomatis) atau draw.io. Untuk UMKM App hasilnya: `users`, `umkm` (punya `user_id` sebagai foreign key, menegakkan aturan "1 user = 1 UMKM" di level database lewat `UNIQUE`), dan `produk` (punya `umkm_id` sebagai foreign key dengan `ON DELETE CASCADE` — supaya produk ikut terhapus otomatis saat UMKM induknya dihapus).

#### Tool untuk menggambar relasi antar tabel

Tujuan ERD bukan sekadar daftar kolom per tabel — intinya justru **garis relasi** yang menghubungkan satu tabel ke tabel lain (1-ke-1, 1-ke-banyak, banyak-ke-banyak). Tool di bawah ini dipilih karena bisa menggambar garis itu otomatis dari foreign key yang kamu tulis, tanpa perlu menarik-narik garis manual satu per satu:

| Tool | Cara kerja | Kenapa cocok untuk pemula |
|----|----|----|
| <a href="https://dbdiagram.io" target="_blank" rel="noopener"><strong>dbdiagram.io</strong></a> (rekomendasi) | Ketik definisi tabel pakai bahasa **DBML** (mirip SQL yang disederhanakan) di panel kiri, diagram ERD lengkap dengan garis relasi muncul otomatis di panel kanan. | Gratis tanpa akun, tidak perlu menggambar manual — cukup tulis `ref:` sekali dan garis beserta notasi "satu-ke-banyak" langsung tergambar sendiri. Bisa export jadi gambar PNG atau SQL langsung. |
| <a href="https://drawsql.app" target="_blank" rel="noopener">DrawSQL</a> | Mirip dbdiagram.io tapi lewat UI drag-and-drop (klik kolom, tarik ke tabel lain untuk bikin relasi) alih-alih mengetik kode. | Cocok yang lebih nyaman visual murni dibanding menulis sintaks DBML. |
| <a href="https://draw.io" target="_blank" rel="noopener">draw.io</a> / Excalidraw | Kanvas bebas — kotak dan garis digambar manual sepenuhnya, termasuk notasi relasinya. | Paling fleksibel (bisa gabung dengan diagram arsitektur lain di kanvas yang sama), tapi garis relasi harus ditarik & dilabeli sendiri satu per satu — lebih makan waktu untuk skema dengan banyak tabel. |

Berikut skema UMKM App yang sama persis dengan migration asli (lihat di bawah), ditulis ulang dalam sintaks **DBML** milik dbdiagram.io — tempel langsung ke editor di <a href="https://dbdiagram.io" target="_blank" rel="noopener">dbdiagram.io</a> untuk melihat garis relasinya digambar otomatis:

dbdiagram.io — skema UMKM App (DBML)

    Table users {
      id integer [primary key]
      nama varchar
      email varchar [unique]
      password varchar
      created_at timestamp
    }

    Table umkm {
      id integer [primary key]
      user_id integer [unique]
      nama varchar
      deskripsi text
      alamat varchar
      foto varchar
      created_at timestamp
    }

    Table produk {
      id integer [primary key]
      umkm_id integer
      nama varchar
      harga decimal
      deskripsi text
      foto varchar
      created_at timestamp
    }

    Ref: umkm.user_id > users.id // satu user, satu umkm (unique di sisi umkm)
    Ref: produk.umkm_id > umkm.id // satu umkm, banyak produk

Coba Sendiri

Buka <a href="https://dbdiagram.io" target="_blank" rel="noopener">dbdiagram.io</a> → klik **"Go to App"** / "Create new diagram" (tidak wajib bikin akun untuk coba-coba) → hapus contoh bawaan di editor kiri → tempel kode DBML di atas.

Perhatikan dua baris `Ref:` paling bawah: begitu ditempel, dbdiagram.io langsung menggambar garis dari tabel `umkm` ke `users`, dan dari `produk` ke `umkm`, lengkap dengan notasi "satu-ke-banyak" (simbol kaki-ayam/crow's foot) tepat di ujung garisnya. Coba ganti `umkm.user_id > users.id` jadi `umkm.user_id - users.id` (tanda `-` bukan `>`) dan lihat bedanya — itu notasi relasi "satu-ke-satu" vs "satu-ke-banyak". Diagram inilah yang seharusnya digambar **sebelum** baris `CREATE TABLE` di bawah ini ditulis, bukan sesudahnya.

ERD itu cuma gambar — hasil akhirnya tetap harus diterjemahkan jadi perintah SQL sungguhan yang dijalankan ke Postgres. Sebelum masuk ke kode Go yang membungkusnya (Bagian 11), mundur dulu ke dasarnya: apa itu tabel, primary key, foreign key, dan lima perintah SQL (`CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`) — memakai **skema & query asli** yang dipakai UMKM API, satu per satu, supaya terbayang konkret konsep dasar database di balik ERD di atas.

#### Skema tabel asli — `migrations/000001_init.up.sql`

Ini definisi SQL asli dari ketiga tabel hasil ERD di atas, dijalankan sekali lewat `cmd/migrate` (lihat Bagian 12) saat database masih kosong:

migrations/000001_init.up.sql

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

- **`SERIAL PRIMARY KEY`** — `id` adalah kunci utama tiap baris: unik, tidak boleh kosong, dan nilainya otomatis naik sendiri (1, 2, 3, …) setiap kali ada baris baru. Ini yang dipakai tiap kali kode menulis `WHERE id = $1`.
- **`REFERENCES users(id)`** — ini *foreign key*: kolom `user_id` di tabel `umkm` wajib berisi nilai yang benar-benar ada sebagai `id` di tabel `users`. Postgres sendiri yang menolak kalau kamu coba menyisipkan `user_id` yang tidak pernah terdaftar — bukan validasi di Go.
- **`UNIQUE` di `umkm.user_id`** — inilah yang sebenarnya menegakkan aturan "1 akun cuma boleh punya 1 UMKM" di level database, bukan cuma di `UmkmService.CreateOwn` (Bagian 10). Kalaupun ada bug di Go yang lolos mengirim `INSERT` kedua untuk `user_id` yang sama, Postgres sendiri yang akan menolaknya dengan error *unique violation*.
- **`ON DELETE CASCADE`** — kalau satu baris `users` dihapus, semua baris `umkm` yang menunjuk ke situ ikut terhapus otomatis oleh Postgres; begitu juga `umkm` → `produk`. Rantai inilah yang membuat kode Go tidak pernah perlu menulis "hapus dulu semua produknya, baru hapus UMKM-nya" secara manual.
- **Kenapa `produk` tidak punya kolom `user_id` sendiri?** Karena kepemilikan produk cukup ditelusuri lewat `umkm_id` → `umkm.user_id` (dua `SELECT` berantai, persis yang dilakukan `authorizeOwner` di Bagian 10) — menyimpan `user_id` di kedua tabel akan jadi data yang bisa saling bertentangan kalau salah satunya lupa diperbarui.

#### Query di balik tiap aksi nyata di aplikasi, satu per satu

Supaya tidak abstrak, berikut ditelusuri **urutan aksi yang sebenarnya dilakukan pengguna** di UMKM App — **Register → Login → Buat UMKM → Lihat Daftar UMKM → Lihat Detail UMKM → Edit UMKM → Hapus UMKM** — satu per satu, masing-masing cukup **satu query sederhana** (bukan gabungan rumit), supaya kebayang persis apa yang terjadi di database setiap kali satu tombol di Flutter ditekan.

**1. Register — bikin akun baru**

Saat kamu mengisi form Register lalu menekan tombol "Daftar", Flutter mengirim `nama`/`email`/`password` ke Go, Go meng-hash password-nya pakai bcrypt, baru `userRepository.Create` menjalankan ini:

userRepository.Create

    INSERT INTO users (nama, email, password)
    VALUES ('Budi', 'budi@mail.com', '$2a$10$hasilHashBcrypt...')
    RETURNING id;

Satu baris baru masuk ke tabel `users`, dan Postgres langsung membalas `id` yang baru dibuatnya lewat `RETURNING` — Go tidak perlu `SELECT` terpisah untuk tahu ID akun yang baru saja dibuat.

Coba Sendiri

Tempel & jalankan di Neon SQL Editor — ganti nama/email dengan milikmu sendiri (password cukup teks bebas, karena ini cuma simulasi, bukan hash bcrypt asli):

    INSERT INTO users (nama, email, password)
    VALUES ('Nama Kamu Sendiri', 'emailkamu@mail.com', 'password_simulasi')
    RETURNING id;

**Catat angka `id` yang muncul di hasilnya** — ini dipakai lagi di langkah 3 (Buat UMKM), persis seperti saat registrasi sungguhan: akun yang baru dibuat langsung "dikenali" lewat ID-nya.

**2. Login — masuk pakai akun yang tadi dibuat**

Saat kamu mengisi email & password lalu menekan "Masuk", Go **tidak** langsung mencocokkan password di SQL — SQL cuma bertugas mengambil barisnya dulu lewat `userRepository.FindByEmail`, baru Go yang membandingkan password-nya pakai `bcrypt.CompareHashAndPassword` (Bagian 09):

userRepository.FindByEmail

    SELECT id, nama, email, password FROM users
    WHERE email = 'budi@mail.com';

Perhatikan: query ini **tidak punya syarat password sama sekali** di `WHERE`-nya — ia hanya mengambil baris berdasarkan email, lalu kolom `password` (yang isinya hash bcrypt) dibawa ke Go untuk dibandingkan di sana. Mencocokkan password lewat `WHERE password = '...'` di SQL justru tidak mungkin dilakukan, karena password yang tersimpan sudah di-hash, bukan teks asli.

Coba Sendiri

    SELECT id, nama, email FROM users WHERE email = 'emailkamu@mail.com';

Harus keluar satu baris — persis akun yang dibuat di langkah 1. Ini membuktikan proses "Login" di level database sebenarnya cuma satu `SELECT` sederhana; bagian "mengecek apakah password benar" terjadi di kode Go, bukan di SQL ini.

**3. Buat UMKM — submit form "Tambah UMKM"**

Setelah login, token JWT-mu menyimpan `user_id`-mu (Bagian 09). Saat kamu submit form "Tambah UMKM" di Flutter, Go membaca `user_id` dari token itu (bukan dari isian form) lalu `umkmRepository.Create` menjalankan:

umkmRepository.Create

    INSERT INTO umkm (user_id, nama, deskripsi, alamat)
    VALUES (3, 'Warung Kopi Budi', 'Jual kopi & gorengan', 'Jl. Melati No. 2')
    RETURNING id;

Angka `3` di situ bukan diketik pengguna — itu `id` akun yang sedang login, disisipkan otomatis oleh Go. Inilah yang membuat satu akun hanya bisa membuat UMKM atas namanya sendiri, tidak bisa membuatkan UMKM untuk akun orang lain.

Coba Sendiri

Ganti angka `1` di bawah dengan `id` yang kamu catat dari langkah 1:

    INSERT INTO umkm (user_id, nama, deskripsi, alamat)
    VALUES (1, 'Warung Hasil Latihan SQL', 'Dibuat manual lewat SQL Editor, bukan lewat Flutter', 'Jl. Percobaan No. 1')
    RETURNING id;

Kalau angka `user_id` yang kamu pakai memang hasil `RETURNING` langkah 1, baris ini akan berhasil tersimpan. Coba sekali lagi dengan `user_id` yang **tidak pernah ada** (misalnya `99999`) — harus muncul error *foreign key violation*, membuktikan `REFERENCES users(id)` di skema tabel benar-benar ditegakkan oleh Postgres, bukan cuma validasi di Go. Catat juga `id` UMKM yang baru dibuat ini untuk langkah berikutnya.

**4. Lihat Daftar UMKM — buka tab "Semua UMKM"**

Tab ini memanggil endpoint publik (tidak perlu login) yang menjalankan `umkmRepository.FindAll` dan `umkmRepository.Count` berpasangan:

umkmRepository.FindAll + Count

    SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm
    WHERE nama ILIKE '%warung%'
    ORDER BY id DESC LIMIT 10 OFFSET 0;

    SELECT COUNT(*) FROM umkm WHERE nama ILIKE '%warung%';

`ILIKE '%warung%'` = pencarian teks tanpa peduli huruf besar/kecil, cocok dengan kotak pencarian di layar. `ORDER BY id DESC` = UMKM terbaru tampil paling atas. `LIMIT 10 OFFSET 0` = ambil 10 baris pertama saja (halaman 1) — `Count` dijalankan terpisah supaya Flutter tahu total keseluruhan data untuk menghitung jumlah halaman, tanpa harus mengunduh semuanya sekaligus.

Coba Sendiri

    SELECT id, nama, alamat FROM umkm
    WHERE nama ILIKE '%Hasil Latihan SQL%'
    ORDER BY id DESC LIMIT 10 OFFSET 0;

Harus keluar UMKM yang dibuat di langkah 3. Kalau kamu buka tab **"Semua UMKM"** di aplikasi Flutter-mu sendiri, UMKM ini juga akan muncul di situ — karena dibuat langsung di tabel yang sama persis yang dibaca endpoint tersebut, walau dibuat lewat SQL manual bukan lewat form Flutter.

**5. Lihat Detail UMKM — buka satu UMKM untuk lihat produknya**

Tombol detail memanggil `umkmRepository.FindByID` (satu `SELECT`, cuma tabel `umkm`), lalu *terpisah* `produkRepository.FindByUmkmID` untuk daftar produknya — dua `SELECT` berurutan, bukan satu `JOIN` (lihat juga `authorizeOwner` di Bagian 10 yang memakai pola serupa). Tapi sebagai pembelajaran, berikut cara menyatukan keduanya jadi satu query lewat `JOIN` — cara SQL **sebenarnya** membuktikan relasi yang digambar di dbdiagram.io sebelumnya:

Relasi umkm ↔ produk (versi JOIN)

    SELECT um.nama AS nama_umkm, um.alamat, p.nama AS nama_produk, p.harga
    FROM umkm um
    JOIN produk p ON p.umkm_id = um.id
    WHERE um.nama = 'Warung Hasil Latihan SQL';

`JOIN ... ON p.umkm_id = um.id` menyatukan setiap baris `produk` dengan baris `umkm` induknya berdasarkan kecocokan foreign key — hasilnya satu tabel gabungan, padahal datanya tersimpan di dua tabel terpisah.

Coba Sendiri

Dulu kamu belum punya produk untuk UMKM latihan ini — buat satu dulu (ganti `1` dengan `id` UMKM dari langkah 3), baru jalankan `JOIN`-nya:

    INSERT INTO produk (umkm_id, nama, harga, deskripsi)
    VALUES (1, 'Kopi Susu', 12000, 'Produk latihan');

    SELECT um.nama AS nama_umkm, p.nama AS nama_produk, p.harga
    FROM umkm um
    JOIN produk p ON p.umkm_id = um.id
    WHERE um.nama = 'Warung Hasil Latihan SQL';

Harus keluar satu baris berisi nama UMKM-mu bergandengan dengan "Kopi Susu" — bukti paling konkret bahwa relasi yang cuma berupa garis di ERD benar-benar bisa "disatukan" lewat SQL.

**6. Edit UMKM — submit form edit**

Menekan "Simpan" di form edit memanggil `umkmRepository.Update`, menulis ulang semua kolom sekaligus (bukan per-kolom yang berubah saja):

umkmRepository.Update

    UPDATE umkm SET nama = 'Warung Kopi Budi (Cabang Baru)',
        deskripsi = 'Jual kopi & gorengan', alamat = 'Jl. Melati No. 2',
        foto = 'umkm/123.jpg' WHERE id = 7;

Nilai kolom yang *tidak* diubah pengguna (mis. `alamat`) tetap dikirim ulang dengan nilai lamanya oleh service layer, bukan dikosongkan — supaya satu `UPDATE` ini selalu lengkap mengisi semua kolom sekaligus.

Coba Sendiri

    UPDATE umkm SET nama = 'Warung Hasil Latihan SQL (sudah diedit)'
    WHERE nama = 'Warung Hasil Latihan SQL';

    SELECT id, nama, alamat FROM umkm WHERE nama ILIKE '%Hasil Latihan SQL%';

Baris kedua membuktikan baris pertama bekerja: nama UMKM latihan sekarang berakhiran "(sudah diedit)". Refresh tab "Semua UMKM" di Flutter-mu — nama yang berubah ikut muncul di situ.

**7. Hapus UMKM — tombol hapus di "UMKM Saya"**

Ini satu-satunya aksi yang efeknya **lebih luas dari satu tabel**: `umkmRepository.Delete` cuma menghapus dari tabel `umkm`, tapi berkat `ON DELETE CASCADE` di skema tabel `produk` (lihat skema tabel asli di atas), semua produk UMKM itu ikut terhapus otomatis oleh Postgres:

umkmRepository.Delete

    DELETE FROM umkm WHERE id = 7;

Coba Sendiri

    -- hitung dulu produknya sebelum dihapus
    SELECT COUNT(*) FROM produk WHERE umkm_id = (
      SELECT id FROM umkm WHERE nama ILIKE '%Hasil Latihan SQL%'
    );

    -- hapus UMKM-nya (bukan produknya)
    DELETE FROM umkm WHERE nama ILIKE '%Hasil Latihan SQL%';

    -- hitung ulang -- harus jadi 0, padahal baris ini TIDAK PERNAH menyentuh tabel produk
    SELECT COUNT(*) FROM produk WHERE umkm_id = (
      SELECT id FROM umkm WHERE nama ILIKE '%Hasil Latihan SQL%'
    );

    -- beres-beres: hapus juga akun latihannya (tidak wajib, tapi rapi)
    DELETE FROM users WHERE nama = 'Nama Kamu Sendiri';

Hitungan pertama harus `1` (dari "Kopi Susu" di langkah 5), hitungan kedua (setelah UMKM dihapus) harus `0` — padahal query penghapusnya cuma menyebut tabel `umkm`, tidak pernah menyentuh tabel `produk` sama sekali. `ON DELETE CASCADE`-lah yang bekerja di belakang layar. Baris terakhir cuma beres-beres supaya database latihanmu tidak menumpuk data sampah permanen.

### d. Desain kontrak API

Khusus proyek yang punya backend terpisah (seperti UMKM API + UMKM App), ada satu desain tambahan yang sering terlewat: **bentuk request/response tiap endpoint** disepakati di atas kertas dulu sebelum Flutter dan Go ditulis bersamaan. UMKM API memakai **Swagger/OpenAPI** (bisa dicoba langsung di `/swagger/`) untuk ini — mendefinisikan endpoint, field request, dan bentuk response JSON secara eksplisit, supaya tim backend dan frontend (atau diri sendiri di waktu berbeda) tidak saling menebak bentuk data yang dipertukarkan.

Kesalahan paling umum pemula

Langsung menulis kode Flutter sebelum tahu endpoint API apa saja yang dibutuhkan, lalu membangun backend belakangan sambil menebak-nebak bentuk responsnya. Hasilnya: bolak-balik mengubah kedua sisi. Desain dulu bentuk API (endpoint, request, response) di atas kertas/Swagger sebelum menulis Flutter yang memanggilnya.

## 05Tahap 3: Development

Urutan yang terbukti efisien: **backend dulu, baru frontend** — karena Flutter butuh sesuatu yang nyata untuk dipanggil. Di dalam backend sendiri, urutan membangunnya mengikuti lapisan arsitektur dari dalam ke luar:

1.  **Domain** — definisikan struct data dan jenis error bisnis dulu (`User`, `Umkm`, `Produk`, `ErrNotFound`, dst).
2.  **Repository** — implementasikan akses database mentah untuk tiap domain.
3.  **Service** — tambahkan aturan bisnis & otorisasi di atas repository (misal: cek kepemilikan sebelum izinkan update).
4.  **Handler** — bungkus service jadi endpoint HTTP, baru di tahap ini bentuk request/response JSON diputuskan secara konkret.
5.  **Flutter** — setelah API berjalan dan bisa dites lewat Swagger, baru model (`fromJson`), `ApiService`, lalu layar-layar UI ditulis mengonsumsi API tersebut.

Ini persis urutan yang kalian jalani dari Pertemuan 4 (backend) menuju Pertemuan 6-7 (Flutter mengonsumsinya) — bukan kebetulan, tapi memang urutan yang masuk akal secara rekayasa perangkat lunak.

### Tools yang dipakai selama development

| Kebutuhan | Tools yang dipakai di proyek ini |
|----|----|
| Editor kode | VS Code, dengan ekstensi Go (`golang.go`) dan Flutter/Dart resmi — autocomplete, format-on-save (`gofmt`/`dart format`), dan debugging terintegrasi. |
| Version control | Git + GitHub — setiap pertemuan jadi commit/branch terpisah, memudahkan membandingkan versi kode sebelum/sesudah fitur ditambahkan. |
| Manajemen dependency | `go.mod`/`go.sum` (Go modules) di `umkm-api`, `pubspec.yaml` + `flutter pub get` di `umkm-app`. |
| Uji coba API manual selama coding | Swagger UI bawaan (`/swagger/`) untuk coba endpoint satu-satu tanpa perlu Flutter sudah siap, atau Postman/Insomnia kalau butuh menyimpan koleksi request. |
| Database client | psql (CLI bawaan Postgres) atau GUI seperti TablePlus/DBeaver untuk inspeksi isi tabel langsung ke Neon Postgres saat debugging. |
| Emulator/device testing | Android Emulator (lewat Android Studio) untuk iterasi cepat, real device lewat USB debugging untuk uji performa & kamera/upload foto yang sesungguhnya. |

Development berjalan paralel dengan testing manual

Pada praktiknya, setiap fungsi yang baru ditulis langsung dicoba manual (lewat Swagger untuk Go, lewat `flutter run` + hot reload untuk UI) sebelum lanjut ke fungsi berikutnya — bukan menulis semua kode dulu baru dites di akhir. Ini mempersempit area pencarian bug: kalau baru satu fungsi ditambahkan lalu error muncul, penyebabnya hampir pasti ada di fungsi itu.

## 06Tahap 4: Testing

Testing bukan cuma "coba jalankan, kalau tidak merah berarti aman". Untuk proyek seukuran UMKM API/App, minimal ada tiga lapis pengecekan yang relevan:

| Jenis | Contoh di proyek UMKM |
|----|----|
| Uji endpoint API langsung | Coba tiap endpoint lewat Swagger UI (`/swagger/`) atau Postman — termasuk kasus gagal: login salah password, create UMKM kedua (harus kena `409 Conflict`), akses endpoint auth tanpa token (harus `401`). |
| Uji alur UI end-to-end | Jalankan Flutter sungguhan dari Splash sampai edit produk — pastikan token tersimpan dan terpakai, foto ter-upload dan tampil kembali, logout benar-benar menghapus sesi. |
| Uji kasus tepi (edge case) | Upload file selain JPG/PNG (harus ditolak baik di Flutter maupun di server — lihat Bagian 12), koneksi internet mati di tengah submit, data kosong (list UMKM kosong tidak boleh membuat UI crash). |

### Tools untuk tiap jenis testing

| Jenis | Tools | Contoh konkret |
|----|----|----|
| Manual API testing | Swagger UI (`/swagger/`), Postman/Insomnia | Simpan satu koleksi request di Postman: register → login (simpan token) → create UMKM pakai token itu → create UMKM kedua (harus gagal 409). |
| Automated unit test (Go) | `go test ./...` (built-in testing package) | Uji fungsi murni seperti `normalizePagination` — beri input aneh (limit negatif, page 0) pastikan hasilnya tetap dalam batas wajar, tanpa perlu database sungguhan. |
| Automated widget test (Flutter) | `flutter test` + package `flutter_test` bawaan SDK | Uji `LoginScreen` menampilkan pesan error validasi saat password diisi kurang dari 6 karakter, tanpa perlu menjalankan API sungguhan. |
| Static analysis | `flutter analyze`, `go vet` | Dijalankan sebelum commit — menangkap kesalahan sintaks/tipe yang lolos dari mata sebelum sempat dijalankan. |
| Manual QA checklist | Daftar centang tertulis (bisa di Notion/Google Docs/\`.md\`) | Daftar langkah tetap yang dijalankan ulang tiap kali ada perubahan besar — mis. "coba login dengan password salah 6x berturut-turut, pastikan percobaan ke-6 ditolak rate limiter". |

Prinsip: jangan percaya "kelihatannya jalan"

Kode yang terlihat berfungsi saat jalur normal dicoba belum tentu aman — baru ketahuan bermasalah saat kasus gagal benar-benar terjadi di tangan pengguna. Selalu uji jalur gagal, bukan cuma jalur sukses.

## 07Tahap 5: Deployment & Maintenance

Aplikasi yang hanya bisa jalan di laptop pembuatnya belum selesai. Untuk proyek seperti UMKM API/App, tahap ini berarti:

- **Backend** — database dipindah ke layanan terkelola (proyek ini memakai Neon Postgres, bukan Postgres lokal), server Go dijalankan di suatu tempat yang bisa diakses dari internet/jaringan lokal (bukan cuma `localhost` — ingat kenapa `baseUrl` di Flutter memakai IP LAN, bukan `localhost`, di Bagian 19), dan konfigurasi sensitif (kredensial database, `JWT_SECRET`) disimpan di `.env`, tidak ditulis langsung di kode.
- **Mobile app** — build rilis (`flutter build apk`/`appbundle`), lalu didistribusikan (internal testing, Play Store, atau dibagikan langsung sebagai APK untuk keperluan tugas kuliah).
- **Maintenance** — skema database yang berubah di kemudian hari dikelola lewat *migration* yang tercatat dan bisa dijalankan ulang di server mana pun (lihat Bagian 12), bukan mengubah tabel manual lewat `psql` setiap kali.

### Pilihan tools/layanan untuk tiap bagian

| Bagian | Opsi yang umum dipakai untuk skala tugas kuliah/proyek kecil |
|----|----|
| Database | <a href="https://neon.tech" target="_blank" rel="noopener">Neon</a> (dipakai proyek ini — Postgres gratis, serverless), alternatif: Supabase, Railway Postgres. |
| Hosting server Go | Railway, Render, atau Fly.io (semua punya tier gratis/murah, deploy langsung dari GitHub repo) — alternatif: VPS murah (mis. Lightsail/DigitalOcean) kalau butuh kendali penuh. |
| Penyimpanan file upload | Disk lokal server (dipakai proyek ini — cukup untuk skala kecil) — untuk skala produksi sungguhan biasanya dipindah ke object storage seperti Cloudflare R2/AWS S3 supaya tidak hilang saat server di-redeploy. |
| Distribusi Android | APK dibagikan langsung (cukup untuk tugas kuliah), atau Google Play Console → Internal Testing track untuk simulasi distribusi yang lebih resmi. |
| CI/CD (opsional) | GitHub Actions — otomatis menjalankan `go vet`/`flutter analyze` setiap push, supaya kesalahan ketahuan sebelum di-deploy manual. |
| Pemantauan setelah rilis | Endpoint `GET /healthz` dicek berkala (manual atau lewat layanan uptime gratis seperti UptimeRobot) untuk tahu kalau server down. |

Deployment bukan akhir

Setelah rilis, aplikasi tetap butuh pemantauan (karena itu ada `GET /healthz` di UMKM API) dan perbaikan bug berkelanjutan — siklus lima tahap ini sebenarnya berputar lagi setiap kali ada fitur baru atau masalah baru ditemukan dari pengguna nyata.

## 08Golang: Peta Arsitektur UMKM API

Sebelum masuk ke fungsi satu-per-satu, ini peta besar bagaimana `umkm-api` disusun — hasil dari Tahap 2 (desain arsitektur) di atas:

alur satu request masuk

    HTTP Request
       ↓
    handler/*.go        → decode JSON/multipart, panggil service, map error → status HTTP
       ↓
    service/*.go        → aturan bisnis: validasi, cek kepemilikan, hash password, dsb
       ↓
    repository/*.go     → SQL parameterized ke Postgres, pgx.ErrNoRows → domain.ErrNotFound
       ↓
    domain/*.go         → struct murni + sentinel error (ErrNotFound, ErrConflict, ErrForbidden, ErrInvalidInput)

Dua hal penting dari peta ini:

- **Error mengalir ke atas, bukan status HTTP.** `domain` dan `service` tidak pernah tahu apa itu "404" atau "409" — mereka hanya mengembalikan error Go biasa (`ErrNotFound`, dst). Hanya `handler` yang tahu cara menerjemahkan error itu jadi status HTTP, lewat `errors.Is(...)`. Ini membuat `service` dan `repository` bisa dipakai ulang di konteks lain (misal CLI) tanpa membawa konsep HTTP sama sekali.
- **Native `net/http`, bukan Gin/Echo/Fiber.** Routing di `cmd/api/main.go` memakai `http.NewServeMux()` dengan pattern Go 1.22+ (`"POST /umkm"`, `r.PathValue("id")`). Ini sengaja menunjukkan bahwa REST API lengkap — routing, middleware, JSON — bisa dibangun dari standard library saja, tanpa framework pihak ketiga.

### Peta lengkap endpoint

| Method & Path | Handler | Auth | Keterangan |
|----|----|----|----|
| `POST /api/auth/register` | `AuthHandler.Register` | Publik | Dibatasi validasi (nama/email/password≥6) di service, bukan di handler. |
| `POST /api/auth/login` | `AuthHandler.Login` | Publik + rate limit 5/menit/IP | Mengembalikan JWT + data user. |
| `GET /api/profile` | `AuthHandler.Profile` | Wajib login | Ambil data akun dari token yang aktif. |
| `PUT /api/profile` | `AuthHandler.UpdateProfile` | Wajib login | Ubah nama/email. |
| `PUT /api/profile/password` | `AuthHandler.UpdatePassword` | Wajib login | Wajib sertakan password lama. |
| `GET /api/umkm` | `UmkmHandler.List` | Publik | Pagination (`page`, `limit`) + pencarian (`q`). |
| `GET /api/umkm/{id}` | `UmkmHandler.Detail` | Publik | Detail satu UMKM. |
| `GET /api/umkm/saya` | `UmkmHandler.MyUmkm` | Wajib login | UMKM milik user yang sedang login; `404` kalau belum punya. |
| `POST /api/umkm` | `UmkmHandler.Create` | Wajib login | Multipart (field + foto); gagal `409` kalau user sudah punya UMKM. |
| `PUT /api/umkm/{id}` | `UmkmHandler.Update` | Wajib login + pemilik | Multipart; foto opsional (tidak wajib upload ulang). |
| `DELETE /api/umkm/{id}` | `UmkmHandler.Delete` | Wajib login + pemilik | Produk terkait ikut terhapus (FK `ON DELETE CASCADE`); file foto dihapus setelah DB sukses. |
| `GET /api/umkm/{id}/produk` | `ProdukHandler.ListByUmkm` | Publik | Daftar produk milik satu UMKM. |
| `GET /api/produk/{id}` | `ProdukHandler.Detail` | Publik | Detail satu produk. |
| `POST /api/umkm/{umkmId}/produk` | `ProdukHandler.Create` | Wajib login + pemilik UMKM | Multipart; kepemilikan dicek lewat `authorizeOwner`. |
| `PUT /api/produk/{id}` | `ProdukHandler.Update` | Wajib login + pemilik | Sama pola dengan update UMKM. |
| `DELETE /api/produk/{id}` | `ProdukHandler.Delete` | Wajib login + pemilik | File foto produk ikut dihapus. |
| `GET /uploads/*` | `http.FileServer` | Publik | Statis — foto UMKM/produk disajikan langsung sebagai file, bukan lewat handler custom. |
| `GET /healthz` | inline di `main.go` | Publik | Untuk pemantauan uptime (lihat Bagian 07). |
| `GET /swagger/*` | swagger-ui handler | Publik | Dokumentasi API interaktif, bisa langsung dicoba dari browser. |

### Pemetaan error bisnis → status HTTP

Semua handler memakai pola `switch`/`errors.Is` yang sama untuk menerjemahkan error dari `service` menjadi response HTTP yang konsisten:

| Sentinel error (domain) | Status HTTP | Kode error di response | Contoh pemicu |
|----|----|----|----|
| `ErrInvalidInput` | `400` | `BAD_REQUEST` | Email kosong saat register, password kurang dari 6 karakter. |
| (gagal autentikasi di middleware) | `401` | `UNAUTHORIZED` | Token tidak ada/tidak valid/kedaluwarsa. |
| `ErrForbidden` | `403` | `FORBIDDEN` | User mencoba update/hapus UMKM atau produk yang bukan miliknya. |
| `ErrNotFound` | `404` | `NOT_FOUND` | Akses `GET /umkm/{id}` dengan id yang tidak ada di database. |
| `ErrConflict` | `409` | `CONFLICT` | Register dengan email yang sudah terdaftar, atau create UMKM kedua. |

## 09Golang: Autentikasi & Keamanan

`internal/middleware/auth.go` — fungsi `RequireAuth(jwtSecret)` membungkus handler mana pun yang butuh login. Dipasang selektif di `main.go`: `/profile`, `POST/PUT/DELETE /umkm`, `GET /umkm/saya`, dan semua endpoint produk yang mengubah data — tapi **tidak** dipasang di `GET /umkm` (list publik) atau `GET /umkm/{id}` (detail publik), sesuai kebutuhan dari Tahap 1: UMKM harus bisa dijelajahi tanpa akun.

- **Hanya menerima algoritma HS256** (`jwt.WithValidMethods([]string{"HS256"})`) — mencegah *algorithm confusion attack*, yaitu token palsu yang mengaku memakai `alg: none` atau algoritma lain supaya lolos verifikasi.
- Header `Authorization` ditoleransi walau prefiks `"Bearer "` tidak ditulis — sengaja dilonggarkan supaya mahasiswa yang lupa mengetik "Bearer" di Swagger UI tidak langsung gagal.
- User ID hasil parse token disimpan di `context` request, diambil lagi di handler lewat `middleware.GetUserID(r)` — jadi handler tidak perlu parse token sendiri-sendiri.

internal/middleware/auth.go — RequireAuth

    func RequireAuth(jwtSecret string) func(http.Handler) http.Handler {
        return func(next http.Handler) http.Handler {
            return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
                header := r.Header.Get("Authorization")
                if header == "" {
                    http.Error(w, `{"error":{"message":"token tidak ditemukan","code":"UNAUTHORIZED"}}`, http.StatusUnauthorized)
                    return
                }

                // Terima baik "Bearer <token>" maupun token mentah tanpa prefix.
                tokenStr := header
                if len(header) > 7 && strings.EqualFold(header[:7], "Bearer ") {
                    tokenStr = header[7:]
                }
                // WithValidMethods memaksa algoritma HS256 saja — mencegah algorithm confusion attack.
                token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (interface{}, error) {
                    return []byte(jwtSecret), nil
                }, jwt.WithValidMethods([]string{jwt.SigningMethodHS256.Alg()}))
                if err != nil || !token.Valid {
                    http.Error(w, `{"error":{"message":"token tidak valid","code":"UNAUTHORIZED"}}`, http.StatusUnauthorized)
                    return
                }

                claims, _ := token.Claims.(jwt.MapClaims)
                sub, _ := claims["sub"].(float64)
                userID := int64(sub)

                ctx := context.WithValue(r.Context(), UserIDKey, userID)
                next.ServeHTTP(w, r.WithContext(ctx))
            })
        }
    }

Pola yang dipakai di sini disebut **higher-order function**: `RequireAuth` tidak memproses request sendiri, ia *mengembalikan* sebuah fungsi pembungkus (`func(http.Handler) http.Handler`) yang menerima handler asli (`next`) dan mengembalikan handler baru. Handler baru ini menjalankan pengecekan token dulu — kalau gagal, langsung `return` tanpa pernah memanggil `next.ServeHTTP` (handler asli tidak pernah dijalankan). Kalau token valid, `userID` ditempel ke `context` request lalu diteruskan ke `next`. Ini sebabnya dipasang di `main.go` dengan cara membungkus: `auth(http.HandlerFunc(umkmHandler.Create))` — `auth` adalah hasil pemanggilan `RequireAuth(cfg.JWTSecret)`.

Coba Sendiri

Jalankan server (`go run ./cmd/api`), lalu dari terminal lain jalankan tiga perintah ini satu-satu dan bandingkan hasilnya:

    # 1. Tanpa token sama sekali -> harus 401
    curl -i http://localhost:8080/api/profile

    # 2. Token asal-asalan -> harus 401 juga (bukan error server/panik)
    curl -i http://localhost:8080/api/profile -H "Authorization: Bearer token-ngasal-123"

    # 3. Tanpa prefix "Bearer " -> tetap diterima (lihat baris 24-31 kode di atas)
    curl -i http://localhost:8080/api/profile -H "Authorization: <token_hasil_login>"

Dapatkan `<token_hasil_login>` dari respons `POST /api/auth/login` (lihat kotak "Coba Sendiri" di bagian Register/Login tepat di bawah ini). **Yang harus kalian amati:** perintah 1 dan 2 sama-sama balas `401 Unauthorized` dengan body `{"error":{"message":"token tidak ditemukan atau tidak valid",...}}`, sedangkan perintah 3 balas `200 OK` walau tanpa kata "Bearer" di depan token. Kalau hasilnya beda, cek lagi apakah server benar-benar jalan di port 8080 dan `JWT_SECRET` di `.env` konsisten.

`internal/middleware/ratelimit.go` — `ipRateLimiter` hanya dipasang di `POST /auth/login` (5 request/menit per IP). Ini membatasi percobaan *brute-force* password tanpa mengganggu pengguna lain yang kebetulan berbagi endpoint yang sama.

`internal/service/auth_service.go` — `Register` meng-hash password dengan `bcrypt.DefaultCost` (password asli tidak pernah disimpan), `Login` membandingkannya lewat `bcrypt.CompareHashAndPassword`, dan `generateToken` menandatangani JWT berisi klaim `sub` (user ID) dengan masa berlaku 24 jam. `UpdatePassword` mewajibkan password lama diverifikasi dulu sebelum password baru diterima — mencegah orang lain mengganti password hanya karena sesi login sedang aktif di perangkat yang tertinggal.

internal/service/auth_service.go — Register, Login, generateToken

    func (s *AuthService) Register(ctx context.Context, nama, email, password string) (*domain.User, error) {
        if nama == "" || email == "" || len(password) < 6 {
            return nil, domain.ErrInvalidInput
        }
        _, err := s.userRepo.FindByEmail(ctx, email)
        if err == nil {
            return nil, domain.ErrConflict // email sudah dipakai
        }
        if !errors.Is(err, domain.ErrNotFound) {
            return nil, err
        }
        hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
        if err != nil {
            return nil, err
        }
        user := &domain.User{Nama: nama, Email: email, Password: string(hashed)}
        if err := s.userRepo.Create(ctx, user); err != nil {
            return nil, err
        }
        return user, nil
    }

    func (s *AuthService) Login(ctx context.Context, email, password string) (string, *domain.User, error) {
        user, err := s.userRepo.FindByEmail(ctx, email)
        if err != nil {
            return "", nil, domain.ErrNotFound
        }
        if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(password)); err != nil {
            return "", nil, domain.ErrInvalidInput // password salah
        }
        token, err := s.generateToken(user.ID)
        if err != nil {
            return "", nil, err
        }
        return token, user, nil
    }

    func (s *AuthService) generateToken(userID int64) (string, error) {
        claims := jwt.MapClaims{
            "sub": userID,
            "exp": time.Now().Add(24 * time.Hour).Unix(),
        }
        token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
        return token.SignedString([]byte(s.jwtSecret))
    }

Perhatikan `Register` memanggil `FindByEmail` lebih dulu dan membaca hasil errornya dengan cermat: kalau `err == nil` berarti email **sudah ketemu** → `ErrConflict`. Kalau error-nya *bukan* `ErrNotFound` (artinya ada error lain, mis. koneksi database putus) → error itu diteruskan apa adanya, bukan ditelan diam-diam. Hanya ketika error memang `ErrNotFound` (email belum terdaftar) proses lanjut ke hashing password. Tiga cabang ini — konflik, error tak terduga, dan jalur normal — ditangani eksplisit satu-satu, bukan asumsi "kalau tidak ada data berarti aman lanjut".

Coba Sendiri

    # 1. Register akun baru
    curl -i -X POST http://localhost:8080/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"nama":"Budi Tes","email":"budi.tes@mail.com","password":"rahasia123"}'

    # 2. Register LAGI dengan email yang sama -> harus 409 Conflict
    curl -i -X POST http://localhost:8080/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"nama":"Budi Lain","email":"budi.tes@mail.com","password":"lainlagi"}'

    # 3. Login dengan akun yang baru dibuat, simpan token-nya
    curl -i -X POST http://localhost:8080/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"budi.tes@mail.com","password":"rahasia123"}'

    # 4. Login dengan password SALAH -> harus 400, pesan "password salah"
    curl -i -X POST http://localhost:8080/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"budi.tes@mail.com","password":"ngasal"}'

**Eksperimen tambahan:** buka tabel `users` lewat psql/TablePlus setelah perintah 1 dijalankan — lihat kolom `password`, isinya string hash bcrypt yang diawali `$2a$...`, **bukan** `"rahasia123"`. Ini bukti nyata bahwa `bcrypt.GenerateFromPassword` benar-benar jalan, bukan cuma klaim di teks penjelasan. Token dari perintah 3 bisa langsung dipakai untuk kotak "Coba Sendiri" di bagian `RequireAuth` di atas.

## 10Golang: Service Layer — Aturan Bisnis & Otorisasi

`umkm_service.go` dan `produk_service.go` adalah tempat aturan bisnis dari Tahap 1 benar-benar ditegakkan di kode:

- **"1 user = 1 UMKM"** ditegakkan di `CreateOwn`: cek dulu lewat `FindByUserID`, kalau sudah ada → `ErrConflict` (jadi `409` di handler).
- **Kepemilikan UMKM** diverifikasi manual: `umkm.UserID != userID` → `ErrForbidden` (`403`) sebelum izinkan update/hapus.
- **Kepemilikan produk tidak langsung** — tabel `produk` tidak punya kolom `user_id` sendiri, jadi `ProdukService` punya fungsi privat `authorizeOwner` yang menembus dua tabel: ambil produk → ambil UMKM induknya → baru bandingkan `UserID`-nya. Ini contoh nyata kenapa otorisasi sebaiknya ditaruh di service, bukan di middleware generik — aturannya spesifik per domain data.
- **Pola `(entity, fotoLama, err)` pada Update** — foto lama hanya dikembalikan ke handler kalau memang digantikan foto baru. Kalau pengguna tidak upload foto baru saat edit, `fotoLama` dikosongkan sehingga `deleteFile` di handler otomatis tidak melakukan apa-apa. Ini mencegah foto lama terhapus tanpa sengaja saat pengguna hanya mengubah nama/deskripsi.

internal/service/produk_service.go — authorizeOwner & UpdateOwn

    // authorizeOwner memastikan userID adalah pemilik UMKM tempat produk berada.
    func (s *ProdukService) authorizeOwner(ctx context.Context, userID, produkID int64) (*domain.Produk, error) {
        produk, err := s.produkRepo.FindByID(ctx, produkID)
        if err != nil {
            return nil, err
        }
        umkm, err := s.umkmRepo.FindByID(ctx, produk.UmkmID)
        if err != nil {
            return nil, err
        }
        if umkm.UserID != userID {
            return nil, domain.ErrForbidden
        }
        return produk, nil
    }

    func (s *ProdukService) UpdateOwn(ctx context.Context, userID, produkID int64, nama string, harga float64, deskripsi, fotoBaru string) (produk *domain.Produk, fotoLama string, err error) {
        if nama == "" || harga < 0 {
            return nil, "", domain.ErrInvalidInput
        }
        produk, err = s.authorizeOwner(ctx, userID, produkID)
        if err != nil {
            return nil, "", err
        }

        fotoLama = produk.Foto
        produk.Nama = nama
        produk.Harga = harga
        produk.Deskripsi = deskripsi
        if fotoBaru != "" {
            produk.Foto = fotoBaru
        } else {
            fotoLama = "" // tidak ada foto baru -> jangan hapus foto lama
        }

        if err := s.produkRepo.Update(ctx, produk); err != nil {
            return nil, "", err
        }
        return produk, fotoLama, nil
    }

Baca baris demi baris `authorizeOwner`: dua kali `FindByID` dipanggil berturut-turut — pertama ambil produknya (untuk tahu `UmkmID`-nya), lalu ambil UMKM-nya (untuk tahu `UserID` pemiliknya) — baru dibandingkan dengan `userID` yang login. Dua query berantai ini adalah harga yang dibayar karena tabel `produk` sengaja tidak menyimpan `user_id` sendiri (lihat ERD di Bagian 04): kepemilikan produk selalu ditelusuri lewat UMKM induknya, tidak disimpan redundan.

Di `UpdateOwn`, perhatikan baris `if fotoBaru != "" { produk.Foto = fotoBaru } else { fotoLama = "" }` — ini jantung dari pola "jangan hapus foto kalau tidak diganti" yang dijelaskan di atas. `fotoLama` awalnya diisi dari foto yang sedang tersimpan; kalau pengguna *tidak* mengirim foto baru (`fotoBaru == ""`), variabel itu sengaja dikosongkan lagi sebelum dikembalikan, supaya pemanggil (handler) tahu "tidak ada apa-apa yang perlu dihapus".

Coba Sendiri

Untuk benar-benar melihat `ErrForbidden` terpicu, butuh **dua akun berbeda**:

    # 1. Daftar & login akun A, akun B (ulangi langkah register/login di atas
    #    dengan email berbeda), simpan dua token: $TOKEN_A dan $TOKEN_B

    # 2. Akun A membuat UMKM + 1 produk (pakai $TOKEN_A di Authorization)
    curl -s -X POST http://localhost:8080/api/umkm -H "Authorization: Bearer $TOKEN_A" \
      -F "nama=Warung A" | tee /tmp/umkm_a.json

    curl -s -X POST http://localhost:8080/api/umkm/ID_UMKM_A/produk \
      -H "Authorization: Bearer $TOKEN_A" -F "nama=Kopi" -F "harga=15000" | tee /tmp/produk_a.json

    # 3. Akun B mencoba EDIT produk milik akun A -> harus 403 Forbidden
    curl -i -X PUT http://localhost:8080/api/produk/ID_PRODUK_DARI_LANGKAH_2 \
      -H "Authorization: Bearer $TOKEN_B" -F "nama=Kopi Dicuri" -F "harga=1"

Kalau hasilnya memang `403` dengan pesan `"Anda bukan pemilik UMKM ini"`, berarti rantai `authorizeOwner` → bandingkan `umkm.UserID != userID` benar-benar bekerja. Coba juga kebalikannya — akun A mengedit produknya sendiri — harus berhasil `200 OK`, supaya yakin middleware tidak asal menolak semua orang.

`pagination.go` — fungsi `normalizePagination` adalah satu-satunya tempat default `limit=10`, `maxLimit=100`, dan minimal `page=1` ditentukan, dipakai bersama oleh `UmkmService.List` maupun `ProdukService.ListByUmkm` — menghindari dua aturan pagination yang beda sendiri-sendiri di dua tempat.

## 11Golang: Repository & Pola Anti SQL Injection

Ketiga repository (`user`, `umkm`, `produk`) mengikuti pola identik di atas `pgxpool.Pool`:

- **Selalu parameterized query** (`$1, $2, ...`), tidak pernah menyambung string SQL dengan input pengguna — ini yang mencegah SQL injection, bukan validasi input semata.
- **`pgx.ErrNoRows` dikonversi jadi `domain.ErrNotFound` tepat di repository** — supaya layer di atasnya (service, handler) tidak perlu tahu apa-apa soal pgx atau SQL sama sekali. Kalau suatu saat database diganti, hanya repository yang perlu disentuh.
- **`list := []domain.Umkm{}`, bukan `var list []domain.Umkm`** — detail kecil tapi penting: `var` menghasilkan `nil` slice yang di-serialize JSON jadi `null`, sedangkan inisialisasi eksplisit menghasilkan `[]`. Flutter yang menerima `null` untuk field yang diharapkan berupa list harus menangani kasus itu terus-menerus — jauh lebih sederhana kalau API konsisten mengembalikan array kosong.

internal/repository/umkm_repository.go — FindAll & FindByID

    func (r *umkmRepository) FindAll(ctx context.Context, q string, limit, offset int) ([]domain.Umkm, error) {
        query := `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm
                  WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')
                  ORDER BY id DESC LIMIT $2 OFFSET $3`
        rows, err := r.db.Query(ctx, query, q, limit, offset)
        if err != nil {
            return nil, err
        }
        defer rows.Close()

        list := []domain.Umkm{} // slice kosong, bukan nil, agar JSON-nya "[]" bukan "null"
        for rows.Next() {
            var u domain.Umkm
            if err := rows.Scan(&u.ID, &u.UserID, &u.Nama, &u.Deskripsi, &u.Alamat, &u.Foto); err != nil {
                return nil, err
            }
            list = append(list, u)
        }
        return list, rows.Err()
    }

    func (r *umkmRepository) FindByID(ctx context.Context, id int64) (*domain.Umkm, error) {
        var u domain.Umkm
        query := `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE id = $1`
        err := r.db.QueryRow(ctx, query, id).Scan(&u.ID, &u.UserID, &u.Nama, &u.Deskripsi, &u.Alamat, &u.Foto)
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, domain.ErrNotFound
        }
        if err != nil {
            return nil, err
        }
        return &u, nil
    }

Perhatikan parameter `$1` dipakai dua kali di query `FindAll` — sekali untuk cek apakah pencarian kosong (`$1 = ''`), sekali lagi untuk pola `ILIKE` (`ILIKE` = perbandingan teks tanpa peduli huruf besar/kecil di Postgres). Nilai `q` yang dikirim pengguna tidak pernah disisipkan langsung ke string SQL — ia selalu lewat sebagai *parameter terpisah* yang dikirim ke database oleh driver `pgx`, bukan digabung dengan `fmt.Sprintf` atau operator `+`. Walaupun pengguna mengetik sesuatu seperti `'; DROP TABLE umkm;--` di kotak pencarian, string itu tetap diperlakukan database sebagai *nilai* yang dicari, bukan sebagai *perintah SQL* yang dijalankan.

Di `FindByID`, satu baris `if errors.Is(err, pgx.ErrNoRows) { return nil, domain.ErrNotFound }` adalah titik tunggal tempat "bahasa" pgx (`pgx.ErrNoRows`) diterjemahkan jadi "bahasa" domain aplikasi (`domain.ErrNotFound`). Semua kode di atas repository — `service`, `handler` — hanya pernah melihat `domain.ErrNotFound`, tidak pernah tahu bahwa di baliknya ada pgx atau Postgres sama sekali.

Coba Sendiri

    # 1. ID yang tidak ada -> harus 404, bukan 500 crash
    curl -i http://localhost:8080/api/umkm/999999

    # 2. Pencarian normal
    curl -s "http://localhost:8080/api/umkm?q=warung" | head -c 300

    # 3. Coba "serang" kotak pencarian dengan sintaks SQL -> HARUS tetap
    #    aman, hasilnya kosong/wajar, server TIDAK boleh error 500 atau
    #    membocorkan data tabel lain
    curl -s "http://localhost:8080/api/umkm?q=';DROP TABLE umkm;--" | head -c 300

Kalau perintah 3 membalas `200 OK` dengan `{"data":[],...}` (list kosong karena memang tidak ada UMKM bernama persis string aneh itu) — **dan** tabel `umkm` masih ada & isinya utuh saat dicek ulang lewat perintah 2 — berarti parameterized query di Bagian 11 benar-benar mencegah SQL injection. Kalau sampai ada error 500 atau tabel hilang, itu baru jadi bug serius yang harus dilaporkan.

## 12Golang: Upload Foto & Migration Database

### Upload foto — `internal/handler/upload.go`

- `saveUploadedFile` memvalidasi ekstensi file dengan *whitelist* (hanya `.jpg`/`.jpeg`/`.png`) — menolak tipe lain lewat `errInvalidFileType`, bukan percaya begitu saja apa yang dikirim klien.
- Nama file baru dibuat dari `time.Now().UnixNano()` untuk menghindari dua file bertabrakan nama, dan path yang disimpan ke database adalah path **relatif** (mis. `"umkm/169...jpg"`) — bukan path absolut di server — supaya mudah digabung jadi URL publik (`/uploads/<path>`) dari sisi mana pun API itu diakses.
- `deleteFile` dipanggil setelah update/delete sukses di database, supaya tidak ada file foto "yatim" yang menumpuk di disk setiap kali foto diganti atau datanya dihapus.

internal/handler/upload.go

    var allowedImageExt = map[string]bool{".jpg": true, ".jpeg": true, ".png": true}

    func saveUploadedFile(r *http.Request, fieldName, uploadDir, subDir string) (string, error) {
        file, header, err := r.FormFile(fieldName)
        if err == http.ErrMissingFile {
            return "", nil // foto bersifat opsional
        }
        if err != nil {
            return "", err
        }
        defer file.Close()

        ext := strings.ToLower(filepath.Ext(header.Filename))
        if !allowedImageExt[ext] {
            return "", errInvalidFileType
        }

        targetDir := filepath.Join(uploadDir, subDir)
        os.MkdirAll(targetDir, 0755)

        filename := fmt.Sprintf("%d%s", time.Now().UnixNano(), ext)
        dst, err := os.Create(filepath.Join(targetDir, filename))
        if err != nil {
            return "", err
        }
        defer dst.Close()
        io.Copy(dst, file)

        return subDir + "/" + filename, nil // path RELATIF
    }

    func deleteFile(uploadDir, relPath string) {
        if relPath == "" {
            return
        }
        _ = os.Remove(filepath.Join(uploadDir, relPath))
    }

Urutan pengecekan di `saveUploadedFile` penting: ekstensi dicek (`allowedImageExt[ext]`) **sebelum** file ditulis ke disk. Kalau urutan dibalik — tulis dulu baru cek — file berbahaya sudah sempat tersimpan sebelum ditolak. `header.Filename` adalah nama asli dari perangkat pengirim (tidak bisa dipercaya), karena itu nama file yang benar-benar disimpan ke disk dibuat ulang dari `time.Now().UnixNano()` — bukan memakai `header.Filename` mentah, yang berisiko mengandung karakter aneh atau sengaja dibuat untuk menimpa file lain (path traversal).

Coba Sendiri

    # Siapkan dulu satu foto asli (foto.jpg) dan satu file apa saja
    # yang diubah namanya jadi berekstensi gambar tapi isinya bukan gambar
    echo "ini bukan foto" > palsu.jpg
    echo "ini dokumen" > dokumen.pdf

    # 1. Upload foto.jpg sungguhan -> harus 201, field foto di response terisi
    curl -s -X POST http://localhost:8080/api/umkm -H "Authorization: Bearer $TOKEN_A" \
      -F "nama=Toko Uji Foto" -F "foto=@foto.jpg" | head -c 300

    # 2. Upload dokumen.pdf sebagai foto -> HARUS 400, pesan ekstensi tidak didukung
    curl -i -X PUT http://localhost:8080/api/umkm/ID_UMKM_DARI_LANGKAH_1 \
      -H "Authorization: Bearer $TOKEN_A" -F "nama=Toko Uji Foto" -F "foto=@dokumen.pdf"

Perintah 2 memverifikasi whitelist ekstensi di `allowedImageExt` benar-benar jalan — bandingkan juga dengan `produk_form_screen.dart`/`umkm_form_screen.dart` di Flutter yang menolak file non-JPG/PNG **sebelum** sempat dikirim ke server (coba pilih file `.pdf` lewat `image_picker` di app — galeri foto memang biasanya hanya menampilkan gambar, jadi validasi sisi klien ini lebih kerasa saat menguji lewat curl seperti di atas).

### Migration — `cmd/migrate/main.go`

Alat migrasi di proyek ini bukan CLI eksternal yang diinstal terpisah, melainkan program Go kecil yang memanggil library `golang-migrate/migrate/v4` secara langsung (dijalankan dengan `go run ./cmd/migrate up`, dst, membaca `.env` lewat `godotenv`). Tujuannya: perintah migrasi tetap identik di Windows/macOS/Linux tanpa mahasiswa perlu menginstal binary tambahan atau mengatur `DATABASE_URL` manual di setiap OS.

Kenapa migration, bukan ubah tabel manual lewat psql?

Migration membuat setiap perubahan skema database (buat tabel, tambah kolom, dst) tercatat sebagai file bernomor urut yang bisa dijalankan ulang di server mana pun dengan hasil yang sama persis — sejalan dengan Tahap 5 (Maintenance): skema database ikut "berversi" seperti kode, bukan diubah diam-diam di satu server saja.

## 13Fundamental Flutter: Membangun Layout & Konek ke API

Sebelum membedah tiap halaman `umkm-app` satu per satu (Bagian 14 dst), mundur dulu ke dasarnya — sama seperti Bagian 04 mundur ke SQL mentah sebelum membedah kode Go. Di sini dibedah dua hal paling fundamental di Flutter: **bagaimana widget disusun jadi tampilan**, dan **bagaimana tampilan itu "terisi" data asli dari server** — keduanya dijelaskan pakai potongan kode **asli** dari `umkm-app`, bukan contoh karangan.

### a. Widget dasar tata letak (layout)

Di Flutter, **semuanya adalah widget** — teks, tombol, bahkan jarak kosong sekalipun. Menyusun tampilan berarti menyusun widget jadi sebuah *pohon* (tree): widget besar membungkus widget-widget kecil di dalamnya. Empat widget tata letak ini dipakai di hampir setiap layar `umkm-app`:

| Widget | Fungsi | Dipakai di mana di umkm-app |
|----|----|----|
| `Column` | Menyusun widget anak **vertikal** (dari atas ke bawah), satu di bawah yang lain. | Tampilan error di `UmkmListScreen` (teks error, jarak, lalu tombol "Coba Lagi" bertumpuk ke bawah). |
| `Row` | Menyusun widget anak **horizontal** (kiri ke kanan), kebalikan dari `Column`. | Baris ikon + label di form, atau dua tombol bersebelahan. |
| `Padding` / `SizedBox` | `Padding` memberi jarak *di sekeliling* satu widget; `SizedBox` membuat kotak kosong berukuran tetap, sering dipakai sebagai "jarak antar widget". | `SizedBox(height: 12)` di antara teks error dan tombol "Coba Lagi". |
| `Expanded` / `Flexible` | Memaksa satu widget anak di dalam `Row`/`Column` mengisi **sisa ruang** yang tersedia, bukan cuma sebesar isinya. | Judul UMKM di `ListTile` agar tidak terpotong meski layar sempit. |

Potongan nyata dari `umkm_list_screen.dart` — ini yang tampil kalau `getUmkmList()` gagal (lihat alurnya lengkap di bagian "b" di bawah):

umkm_list_screen.dart — tampilan error

    Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Gagal memuat data: ${snapshot.error}'),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: _muatUlang, child: const Text('Coba Lagi')),
        ],
      ),
    )

Baca dari luar ke dalam, persis cara Flutter merendernya: `Center` (taruh di tengah layar) → membungkus `Column` (susun vertikal) → berisi tiga anak berurutan dari atas ke bawah: teks error, jarak kosong 12 piksel (`SizedBox`), lalu tombol. `mainAxisSize: MainAxisSize.min` artinya `Column` ini **tidak** memaksa dirinya setinggi layar penuh — tingginya menyesuaikan isi anak-anaknya saja, supaya `Center` di luarnya bisa benar-benar menengahkan kotak sekecil itu, bukan kotak setinggi layar.

### b. Menampilkan daftar data — ListView.builder

Hampir semua "daftar" di `umkm-app` (daftar UMKM, daftar produk) memakai `ListView.builder`, bukan `ListView` biasa atau `Column` berisi banyak item manual. Bedanya krusial untuk performa: `ListView.builder` hanya benar-benar *membangun* widget untuk item yang sedang terlihat di layar — kalau datanya 1000 baris tapi yang muat di layar cuma 8, hanya 8 (plus sedikit buffer) yang dibuat, sisanya dibangun on-demand saat pengguna scroll. `Column` dengan 1000 anak akan membangun ke-1000-nya sekaligus di awal, walau 992 di antaranya tidak terlihat.

umkm_list_screen.dart — ListView.builder

    ListView.builder(
      itemCount: hasil.data.length,
      itemBuilder: (context, i) {
        final umkm = hasil.data[i];
        return ListTile(
          leading: CircleAvatar(
            backgroundImage: umkm.punyaFoto
                ? NetworkImage(ApiService.fotoUrl(umkm.foto))
                : null,
            child: umkm.punyaFoto ? null : Text(umkm.nama[0]),
          ),
          title: Text(umkm.nama),
          subtitle: Text(umkm.alamat),
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => UmkmDetailScreen(umkmId: umkm.id)),
          ),
        );
      },
    )

`itemCount` memberi tahu Flutter berapa total item yang ADA (dari panjang `hasil.data`, hasil parsing JSON dari API). `itemBuilder` adalah fungsi yang dipanggil Flutter **berulang-ulang**, sekali per index `i` yang sedang perlu ditampilkan, mengembalikan satu widget `ListTile` per baris. `onTap` berisi `Navigator.push` — ini yang berpindah ke halaman detail saat salah satu baris disentuh, membawa `umkm.id` sebagai parameter supaya halaman tujuan tahu UMKM mana yang harus dimuat.

### c. Struktur dasar satu halaman — Scaffold & StatefulWidget

Hampir semua layar di `umkm-app` berbentuk `StatefulWidget` (bukan `StatelessWidget`) karena perlu menyimpan *state* yang berubah seiring waktu — misalnya data hasil panggilan API yang awalnya kosong, lalu terisi setelah respons datang. Kerangka minimalnya:

kerangka umum tiap layar di umkm-app

    class UmkmListScreen extends StatefulWidget {
      const UmkmListScreen({super.key});

      @override
      State<UmkmListScreen> createState() => _UmkmListScreenState();
    }

    class _UmkmListScreenState extends State<UmkmListScreen> {
      // 1. deklarasi state di sini (variabel yang bisa berubah)

      @override
      void initState() {
        super.initState();
        // 2. kode yang jalan SEKALI saat layar pertama kali dibuka
      }

      @override
      Widget build(BuildContext context) {
        // 3. kode yang membangun tampilan, dipanggil ulang tiap setState()
        return Scaffold(
          appBar: AppBar(title: const Text('Semua UMKM')),
          body: /* ... isi layar ... */,
        );
      }
    }

`Scaffold` adalah "bingkai" dasar satu layar bergaya Material Design — otomatis menyediakan tempat untuk `appBar` (judul + tombol di atas), `body` (isi utama), dan opsional `floatingActionButton`/`bottomNavigationBar`, tanpa perlu menyusun manual dari nol. `initState()` adalah titik yang tepat untuk memulai pengambilan data dari API — dijelaskan lebih lanjut di bagian "d" di bawah — karena ia dijamin hanya berjalan **satu kali** saat widget pertama kali dibuat, tidak berulang setiap kali layar digambar ulang.

### d. Fundamental konek ke API: http, async/await, dan FutureBuilder

Ini jantung dari "bagaimana Flutter bisa terhubung ke internet". Tiga konsep Dart yang wajib dipahami dulu sebelum membaca `ApiService` secara utuh di Bagian 19:

- **`Future<T>`** — representasi "nilai bertipe `T` yang *akan* ada, tapi belum tentu sekarang" (karena menunggu jaringan). Memanggil API selalu mengembalikan `Future`, tidak pernah data langsung, karena request ke server butuh waktu (tidak instan seperti membaca variabel biasa).
- **`async` / `await`** — `async` menandai sebuah fungsi akan berisi operasi yang perlu "ditunggu"; `await` menjeda eksekusi baris itu sampai `Future`-nya selesai, lalu lanjut ke baris berikutnya dengan nilai yang sudah "terbuka" dari dalam `Future`-nya. Tanpa `await`, kode akan lanjut ke baris berikutnya sebelum data dari server datang.
- **`jsonDecode`/`jsonEncode`** — API membalas data sebagai teks JSON mentah; `jsonDecode` mengubah teks itu jadi `Map<String, dynamic>` yang bisa dibaca Dart (`body['data']`, dst), `jsonEncode` melakukan kebalikannya saat Flutter *mengirim* data ke server.

Potongan nyata paling sederhana di `ApiService` — memuat daftar UMKM:

api_service.dart — getUmkmList

    Future<PaginatedResult<Umkm>> getUmkmList({
      String q = '',
      int page = 1,
    }) async {
      final uri = Uri.parse('$baseUrl/umkm').replace(
        queryParameters: {
          if (q.isNotEmpty) 'q': q,
          'page': '$page',
          'limit': '10',
        },
      );

      final response = await http.get(uri);
      final body = jsonDecode(response.body) as Map<String, dynamic>;

      if (response.statusCode != 200) {
        throw ApiException(body['error']?['message'] ?? 'Gagal memuat data UMKM');
      }
      return PaginatedResult.fromJson(body, Umkm.fromJson);
    }

Baca urut dari atas: (1) `Uri.parse(...).replace(queryParameters: ...)` menyusun URL lengkap dengan parameter pencarian/halaman — persis seperti parameter `?q=...&page=...` yang dibaca `parsePagination` di Go (Bagian 08); (2) `await http.get(uri)` mengirim request GET sungguhan ke server dan **menunggu** balasannya — inilah titik kode "berhenti sejenak" sampai jaringan selesai bekerja; (3) `jsonDecode` mengubah teks JSON balasan jadi `Map` yang bisa dibaca; (4) kalau `statusCode` bukan 200, `throw` error supaya pemanggil tahu something's wrong, membaca pesan error dari struktur `{"error":{"message":...}}` yang sama persis dibahas di Bagian 09 (baik versi Go maupun Node).

#### Memakai hasilnya di layar: FutureBuilder

Setelah `ApiService` mengembalikan `Future`, layar butuh cara menampilkan tiga kondisi berbeda: *sedang memuat*, *gagal*, atau *berhasil dengan data*. `FutureBuilder` adalah widget yang menangani ketiganya otomatis:

umkm_list_screen.dart — initState & FutureBuilder

    late Future<PaginatedResult<Umkm>> _futureUmkm;

    @override
    void initState() {
      super.initState();
      _futureUmkm = _apiService.getUmkmList();   // panggil API SEKALI saat layar dibuka
    }

    // ...di dalam build():
    FutureBuilder<PaginatedResult<Umkm>>(
      future: _futureUmkm,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());  // kondisi 1: sedang memuat
        }
        if (snapshot.hasError) {
          return Center(child: Text('Gagal memuat data: ${snapshot.error}'));  // kondisi 2: gagal
        }
        final hasil = snapshot.data!;
        return ListView.builder(/* ...kondisi 3: berhasil, tampilkan hasil.data... */);
      },
    )

`initState()` memanggil `getUmkmList()` **satu kali** dan menyimpan `Future`-nya (belum selesai) ke variabel `_futureUmkm` — bukan menunggu hasilnya di situ juga. `FutureBuilder` lah yang kemudian "mengawasi" `_futureUmkm`: selama belum selesai, `snapshot.connectionState` bernilai `waiting` dan layar menampilkan *spinner*; begitu selesai (sukses atau gagal), `builder` dipanggil ulang otomatis dengan `snapshot` baru berisi `snapshot.data` (kalau sukses) atau `snapshot.error` (kalau `throw ApiException` di Bagian d di atas benar-benar terpicu).

Kenapa panggil API di initState, bukan langsung di build()?

`build()` bisa dipanggil ulang berkali-kali oleh Flutter (misalnya tiap kali ada perubahan kecil di layar), sedangkan `initState()` dijamin cuma sekali seumur hidup widget. Kalau `getUmkmList()` dipanggil langsung di dalam `build()`, setiap rebuild akan mengirim request baru ke server tanpa henti — aturan "fetch sekali di initState" ini konsisten dipakai di semua layar `umkm-app`, termasuk trik `ValueKey` di `MyUmkmScreen` (Bagian 17) yang sengaja memakai *remount* untuk tetap mematuhi aturan ini walau perlu refresh data.

Coba Sendiri

**Untuk layout murni** (tanpa perlu backend menyala): buka <a href="https://dartpad.dev" target="_blank" rel="noopener">dartpad.dev</a> di browser, pilih template "Flutter", lalu tempel potongan `Column` dari bagian "a" di atas ke dalam `build()` sebuah widget contoh. Ubah `mainAxisSize: MainAxisSize.min` jadi `MainAxisSize.max` dan perhatikan bedanya — kotak `Column`-nya jadi memenuhi seluruh tinggi layar meski isinya tetap cuma 3 baris pendek.

**Untuk konek API sungguhan** (pakai server UMKM API yang sudah berjalan dari Pertemuan 4-9): buka `umkm_list_screen.dart` di proyekmu, tambahkan satu baris `debugPrint(response.body);` tepat setelah baris `final response = await http.get(uri);` di `api_service.dart`, lalu `flutter run` dan buka tab "Semua UMKM". Lihat Debug Console — di situ akan muncul teks JSON mentah persis seperti yang dibalas server, sebelum sempat diubah `jsonDecode` jadi objek Dart. Hapus baris `debugPrint` itu lagi setelah selesai mengamati.

Eksperimen DartPad membuktikan efek properti layout tanpa risiko merusak aplikasi sungguhan. Eksperimen `debugPrint` membuktikan bahwa "data di layar" bukan sihir — ia persis string JSON yang sama yang bisa kamu lihat sendiri lewat `curl` ke endpoint yang sama di Bagian 16 (materi Node.js) atau Swagger (versi Go), cuma sudah "diterjemahkan" jadi widget oleh `ListView.builder`.

## 14Flutter: Peta Halaman UMKM App

Di sisi Flutter, struktur `lib/screens/` mengikuti persis alur UX yang dirancang di Tahap 2:

lib/screens/

    screens/
    ├── splash_screen.dart              → cek token, arahkan ke /home atau /login
    ├── auth/
    │   ├── login_screen.dart
    │   └── register_screen.dart
    └── home/
        ├── home_screen.dart            → shell 3 tab (IndexedStack + NavigationBar)
        ├── umkm/
        │   ├── umkm_list_screen.dart   → tab "Semua UMKM" (publik)
        │   ├── umkm_detail_screen.dart → detail UMKM + daftar produknya (publik)
        │   ├── myumkm_screen.dart      → tab "UMKM Saya" (perlu login, CRUD)
        │   ├── umkm_form_screen.dart   → form tambah/edit UMKM
        │   └── produk_form_screen.dart → form tambah/edit produk
        └── profile/
            ├── profile_screen.dart         → tab "Profil"
            └── update_profile_screen.dart  → ubah nama/email & password

Tidak ada state management library (Provider/Riverpod/Bloc) dipakai di proyek ini — semua state cukup ditangani dengan `StatefulWidget` bawaan, `FutureBuilder`, dan `setState`. Ini pilihan sengaja supaya fokus pertemuan 5-7 tetap di konsep HTTP client dan navigasi, bukan state management — library itu bisa menyusul di proyek UAS kalau dibutuhkan.

### Dependency di `pubspec.yaml`

Hanya empat package eksternal yang dipakai — sengaja diminimalkan supaya fokus belajar tetap di konsep inti, bukan menghafal API banyak library:

| Package | Fungsi di proyek ini |
|----|----|
| `http` | Semua request ke UMKM API — dibungkus seluruhnya di `ApiService` (Bagian 19), tidak dipanggil langsung dari screen. |
| `flutter_secure_storage` | Menyimpan token JWT terenkripsi lewat `TokenStorage` — bukan `SharedPreferences`, karena token adalah kredensial sensitif. |
| `image_picker` | Memilih foto dari galeri saat membuat/mengubah UMKM atau produk (`ImageSource.gallery`). |
| `cupertino_icons` | Bawaan dari `flutter create`, dipakai untuk beberapa ikon bergaya iOS. |

## 15Flutter: Splash, Login, Register

- **`splash_screen.dart`** — di `initState`, cek `TokenStorage.ambil()`: kalau ada token tersimpan, langsung `pushReplacementNamed('/home')`; kalau tidak, ke `'/login'`. Ini yang membuat pengguna yang sudah login tidak perlu login ulang setiap buka aplikasi.
- **`login_screen.dart`** — `Form` + `GlobalKey<FormState>`, validasi lokal dulu (password minimal 6 karakter) sebelum memanggil `ApiService.login()`. Ada state `_loading` yang menonaktifkan tombol & menampilkan spinner selama request berlangsung — mencegah pengguna menekan tombol berkali-kali. `ApiException` dari server ditangkap dan ditampilkan lewat `SnackBar`.
- **`register_screen.dart`** — pola identik dengan login (3 field: nama/email/password). Setelah sukses, **tidak** auto-login — pengguna dikembalikan (`Navigator.pop`) ke halaman Login untuk masuk manual. Ini keputusan UX yang wajar: mengonfirmasi akun benar-benar bisa dipakai untuk login sebelum masuk ke aplikasi.

screens/auth/login_screen.dart — \_prosesLogin

    Future<void> _prosesLogin() async {
      if (!_formKey.currentState!.validate()) return;
      setState(() => _loading = true);
      try {
        await _apiService.login(_emailController.text, _passwordController.text);
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, '/home');
      } on ApiException catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
      } finally {
        if (mounted) setState(() => _loading = false);
      }
    }

Lima hal yang terjadi berurutan di fungsi ini, masing-masing menjaga aplikasi dari bug yang umum terjadi pada pemula:

1.  `_formKey.currentState!.validate()` dipanggil dulu — kalau ada field yang gagal validasi (misal password kurang dari 6 karakter), fungsi langsung `return` sebelum request ke API sama sekali dikirim. Validasi lokal selalu lebih murah daripada menunggu respons gagal dari server.
2.  `setState(() => _loading = true)` — baru di titik ini UI menampilkan spinner dan tombol menjadi tidak bisa ditekan (`onPressed: _loading ? null : _prosesLogin` di bagian `build`).
3.  `await _apiService.login(...)` dibungkus `try` — kalau sukses, baris `if (!mounted) return;` mengecek apakah widget ini **masih ada di layar** sebelum memanggil `Navigator`. Ini penting karena proses `await` butuh waktu; kalau pengguna sudah berpindah layar (atau widget sudah dibuang) sebelum respons API datang, memanggil `Navigator`/`setState` pada widget yang sudah tidak ada akan melempar error.
4.  `on ApiException catch (e)` — hanya menangkap exception bertipe `ApiException` (dilempar sendiri oleh `ApiService`), bukan `catch (e)` generik yang bisa diam-diam menelan bug lain yang sebenarnya perlu diperbaiki, bukan ditampilkan ke pengguna sebagai pesan error biasa.
5.  `finally { if (mounted) setState(() => _loading = false); }` — dijalankan baik request berhasil maupun gagal, memastikan spinner tidak "menggantung" selamanya kalau terjadi error yang tidak terduga.

Coba Sendiri

Jalankan `umkm-app` (`flutter run`) sambil server Go aktif, lalu uji tiga skenario ini satu-satu di layar Login:

    1. Password diisi 3 karakter -> tekan "Masuk" tanpa pernah mengirim request
       (perhatikan: TIDAK ada jeda loading sama sekali, karena validate()
       langsung gagal sebelum _apiService.login() dipanggil)

    2. Email & password benar (akun hasil "Coba Sendiri" di bagian auth_service)
       -> tombol berubah jadi spinner sebentar, lalu pindah ke /home

    3. Email benar, password salah -> tombol sempat jadi spinner, lalu
       kembali normal + muncul SnackBar merah "password salah"

Tambahkan `debugPrint('loading: $_loading');` di awal `build()` kalau mau benar-benar melihat state `_loading` berubah true/false di **Debug Console** VS Code — cara paling langsung membuktikan baris `setState` di langkah 2 dan 5 memang terpanggil, bukan cuma teori di atas kertas.

## 16Flutter: Home, Daftar & Detail UMKM

**`home_screen.dart`** memakai `IndexedStack` dengan `NavigationBar` 3 tab. `IndexedStack` dipilih (bukan mengganti `body` biasa) supaya setiap kali pindah tab, `State` tab sebelumnya — termasuk `Future` yang sudah ter-fetch di `initState`-nya — tidak dibuang dan di-fetch ulang setiap kali tab dibuka kembali.

**`umkm_list_screen.dart`** — `FutureBuilder<PaginatedResult<Umkm>>`, data diambil sekali di `initState` (bukan di `build`, supaya tidak fetch berulang setiap rebuild). `RefreshIndicator` (tarik-untuk-refresh) memanggil `_muatUlang()` yang meng-assign ulang variabel `_futureUmkm` di dalam `setState` — pola standar "refresh" untuk `FutureBuilder`, karena `FutureBuilder` sendiri tidak pernah otomatis memanggil ulang `Future`-nya. Tap item → `push` ke `UmkmDetailScreen`.

**`umkm_detail_screen.dart`** — halaman publik (tidak perlu login), mengambil dua `Future` independen secara paralel di `initState` (data UMKM dan daftar produknya), ditampilkan lewat dua `FutureBuilder` bersarang.

## 17Flutter: UMKM Saya (CRUD & Trik ValueKey)

`myumkm_screen.dart` adalah layar paling kompleks di aplikasi ini karena menggabungkan baca, buat, ubah, dan hapus dalam satu tempat.

- `FutureBuilder<Umkm?>` — hasil `null` berarti pengguna belum punya UMKM sama sekali, ditampilkan tombol "Buat UMKM"; kalau ada data, ditampilkan detail + tombol Edit/Hapus + daftar produk + tombol tambah produk.
- Form UMKM/produk dibuka lewat `Navigator.push<bool>`; hasil `true` (dikirim balik dari `Navigator.pop(context, true)` di halaman form setelah sukses simpan) dipakai memicu reload data di halaman ini.

**Trik `ValueKey` untuk memaksa remount:** daftar produk dipisah jadi widget tersendiri (`_DaftarProduk`, sebuah `StatefulWidget` yang fetch data sendiri di `initState`-nya). Supaya daftar ini bisa "di-refresh" dari luar tanpa mengubah widget itu jadi menerima `Future` dari parent, widget tersebut diberi `key: ValueKey(_produkKey)`, lalu `_muatUlangProduk()` cukup meng-increment `_produkKey`. Flutter melihat `key` berubah sebagai sinyal "ini widget yang berbeda", sehingga instance lama dibuang dan instance baru dibuat dari nol — `initState`-nya jalan lagi, fetch data lagi.

screens/home/umkm/myumkm_screen.dart — potongan kunci

    class _MyUmkmScreenState extends State<MyUmkmScreen> {
      late Future<Umkm?> _futureUmkm;
      int _produkKey = 0;

      void _muatUlangProduk() => setState(() => _produkKey++);

      // ...di dalam build(), setelah data UMKM didapat:
      _DaftarProduk(
        key: ValueKey(_produkKey),   // berubah setiap _muatUlangProduk() dipanggil
        umkmId: umkm.id,
        apiService: _apiService,
        onEdit: (p) => _bukaFormProduk(umkm.id, p),
        onHapus: _hapusProduk,
      ),
    }

    class _DaftarProdukState extends State<_DaftarProduk> {
      late Future<PaginatedResult<Produk>> _futureProduk;

      @override
      void initState() {
        super.initState();
        _futureProduk = widget.apiService.getProdukByUmkm(widget.umkmId); // fetch sekali
      }
    }

Alur lengkapnya saat pengguna menghapus satu produk: `_hapusProduk(id)` di `_MyUmkmScreenState` memanggil API lalu `_muatUlangProduk()` → `_produkKey` bertambah dari, katakanlah, `0` jadi `1` → `setState` men-trigger `build()` ulang di `_MyUmkmScreenState` → widget `_DaftarProduk` dibuat lagi dengan `key: ValueKey(1)`, berbeda dari key sebelumnya (`ValueKey(0)`) → Flutter membandingkan key lama vs baru, melihatnya beda, lalu **membuang instance `_DaftarProdukState` yang lama** dan membuat yang baru dari nol → `initState` widget baru ini jalan lagi, otomatis fetch ulang `getProdukByUmkm`. Tanpa `key` yang berubah, Flutter akan menganggap ini widget yang "sama" (tipe dan posisinya identik) dan tidak pernah membuat instance baru — `initState` tidak akan terpanggil lagi, daftar produk tidak pernah ter-refresh walau datanya di server sudah berubah.

Coba Sendiri

Buktikan triknya dengan mata kepala sendiri, bukan cuma percaya penjelasan di atas:

    1. Tambahkan 1 baris di _DaftarProdukState.initState():
         debugPrint('Fetch produk dijalankan! key=${widget.key}');

    2. flutter run, buka tab "UMKM Saya", lihat Debug Console -> baris
       itu muncul SATU KALI saat layar pertama dibuka.

    3. Tambah satu produk baru lewat tombol "Tambah" -> simpan.
       Lihat Debug Console lagi -> baris itu HARUS muncul LAGI dengan
       key yang berbeda angkanya -> bukti _DaftarProdukState lama dibuang,
       dibuat ulang, initState jalan lagi.

    4. Sekarang coba hapus baris "key: ValueKey(_produkKey)" di kode
       _DaftarProduk (ganti jadi tanpa key sama sekali), hot restart,
       ulangi langkah 3 -> baris debugPrint TIDAK muncul lagi setelah
       tambah produk, padahal datanya sudah berubah di server. Daftar
       produk di layar jadi "basi" sampai layar dibuka ulang dari awal.

Langkah 4 sengaja merusak kode untuk membuktikan triknya *perlu* — setelah selesai bereksperimen, kembalikan baris `key: ValueKey(_produkKey)` seperti semula sebelum lanjut mengerjakan bagian lain.

Kenapa tidak lebih sederhana angkat state produk ke parent saja?

Bisa saja, tapi trik `ValueKey` dipakai di sini karena `_DaftarProduk` memang sengaja dibuat independen (punya siklus fetch sendiri) — pola ini berguna dikenal karena sering ditemui di kode nyata saat me-refactor widget besar jadi beberapa widget kecil yang masing-masing tetap mengatur fetch datanya sendiri.

`umkm_form_screen.dart` dan `produk_form_screen.dart` sama-sama dual-mode create/edit lewat parameter nullable di constructor (`umkm`/`produk` bernilai `null` → mode tambah). Validasi ekstensi foto (JPG/JPEG/PNG) dicek ulang di sisi Flutter sebelum submit — identik dengan whitelist di `saveUploadedFile` Go (Bagian 12) — supaya pengguna dapat feedback instan tanpa harus menunggu response gagal dari server.

## 18Flutter: Profil & Ubah Password

`profile_screen.dart` — `FutureBuilder<User>` fetch sekali, menampilkan avatar inisial, nama, email, dan tombol Logout. Logout memanggil `ApiService.logout()` (hanya menghapus token lokal, tidak memanggil API) lalu `pushNamedAndRemoveUntil` ke `/login` — menghapus **seluruh** riwayat navigasi, supaya tombol back tidak bisa membawa pengguna kembali ke halaman yang butuh login.

`update_profile_screen.dart` menggabungkan dua `Form` independen dalam satu layar: ubah profil (nama/email) dan ubah password (lama/baru), masing-masing dengan state loading terpisah (`_savingProfil`, `_savingPassword`) — supaya mengirim salah satu form tidak ikut mengunci tombol submit form lainnya.

## 19Flutter: ApiService & TokenStorage — Jembatan Tunggal ke API

Semua layar di atas tidak pernah memanggil `http.get`/`http.post` secara langsung — semuanya lewat satu class `ApiService` yang membungkus 13 endpoint:

| Method | Endpoint | Perlu login? |
|----|----|----|
| `getUmkmList` | `GET /umkm` (q, page, limit) | Tidak |
| `getUmkmDetail` | `GET /umkm/{id}` | Tidak |
| `getProdukByUmkm` | `GET /umkm/{id}/produk` | Tidak |
| `register` / `login` | `POST /auth/register` / `/auth/login` | Tidak |
| `getProfile` / `updateProfile` / `updatePassword` | `/profile`, `/profile/password` | Ya |
| `getUmkmSaya` | `GET /umkm/saya` (404 → `null`, bukan exception) | Ya |
| `simpanUmkm` / `simpanProduk` | `POST` atau `PUT` tergantung ada/tidaknya `id` | Ya |
| `hapusUmkm` / `hapusProduk` | `DELETE /umkm/{id}` / `/produk/{id}` | Ya |

- **`simpanUmkm`/`simpanProduk` menyatukan create dan update** lewat satu parameter `id` opsional (`null` → `POST`, terisi → `PUT`) — menghindari dua method multipart yang nyaris identik.
- **`_authHeaders()` privat** membaca token dari `TokenStorage` dan dipanggil di semua method yang butuh login — satu tempat untuk logika "tempel header Authorization", bukan diulang di tiap method.
- **`ApiService.fotoUrl()`** mengonversi path relatif yang dikembalikan API (mis. `"umkm/xxx.jpg"`, hasil keputusan desain di Bagian 12) menjadi URL penuh `http://<host>:8080/uploads/umkm/xxx.jpg` yang bisa langsung dipakai `Image.network`.
- **`baseUrl` memakai IP LAN**, bukan `localhost` — karena perangkat fisik/emulator berjalan sebagai "komputer" terpisah dari mesin development, dan perlu mengakses server lewat alamat jaringan lokal yang sama-sama terjangkau.

services/api_service.dart — simpanUmkm & \_authHeaders

    /// id == null -> membuat UMKM baru (POST /umkm).
    /// id terisi -> mengubah UMKM yang sudah ada (PUT /umkm/{id}).
    Future<Umkm> simpanUmkm({
      int? id,
      required String nama,
      String deskripsi = '',
      String alamat = '',
      String? fotoPath,
    }) async {
      final uri = id == null
          ? Uri.parse('$baseUrl/umkm')
          : Uri.parse('$baseUrl/umkm/$id');
      final request = http.MultipartRequest(id == null ? 'POST' : 'PUT', uri)
        ..headers.addAll(await _authHeaders())
        ..fields['nama'] = nama
        ..fields['deskripsi'] = deskripsi
        ..fields['alamat'] = alamat;
      if (fotoPath != null) {
        request.files.add(await http.MultipartFile.fromPath('foto', fotoPath));
      }

      final streamed = await request.send();
      final response = await http.Response.fromStream(streamed);
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode != 200 && response.statusCode != 201) {
        throw ApiException(body['error']?['message'] ?? 'Gagal menyimpan UMKM');
      }
      return Umkm.fromJson(body['data'] as Map<String, dynamic>);
    }

    Future<Map<String, String>> _authHeaders() async {
      final token = await TokenStorage.ambil();
      return {'Authorization': 'Bearer $token'};
    }

Baris `id == null ? Uri.parse('$baseUrl/umkm') : Uri.parse('$baseUrl/umkm/$id')` dan `http.MultipartRequest(id == null ? 'POST' : 'PUT', uri)` adalah implementasi langsung dari pola "satu fungsi untuk create dan update" — nilai `id` menentukan URL dan HTTP method mana yang dipakai, tapi semua logika setelahnya (membangun multipart request, menyisipkan field, mengirim foto, mem-parsing response) ditulis sekali saja. `foto` hanya ditambahkan ke `request.files` kalau `fotoPath != null` — karena saat *update*, pengguna boleh tidak mengganti foto sama sekali (server akan mempertahankan foto lama, lihat `UpdateOwn` di Bagian 10).

`status 200 dan 201 dua-duanya dianggap sukses` karena Go API mengembalikan `201 Created` untuk `POST` (baru dibuat) dan `200 OK` untuk `PUT` (berhasil diubah) — Flutter sengaja menerima keduanya di satu pengecekan yang sama, konsisten dengan satu fungsi yang menangani dua operasi.

Coba Sendiri

Lihat `simpanUmkm` benar-benar memilih `POST` vs `PUT` secara otomatis, tanpa membaca kode dua kali:

    1. Tambahkan log sementara di awal simpanUmkm():
         debugPrint('simpanUmkm dipanggil, id=$id, method akan jadi '
           '${id == null ? "POST" : "PUT"}');

    2. Di MyUmkmScreen, tombol "Buat UMKM" (mode tambah, id null) ->
       Debug Console harus menampilkan "method akan jadi POST".

    3. Tombol "Edit UMKM" pada UMKM yang sudah ada (id terisi) ->
       Debug Console harus menampilkan "method akan jadi PUT".

    4. Opsional, kalau punya Proxyman/Charles Proxy/Flutter DevTools
       Network tab: amati request yang benar-benar dikirim, cek header
       "Authorization: Bearer ..." sungguhan ada, dan Content-Type
       request adalah "multipart/form-data; boundary=..." bukan
       "application/json" -- bukti nyata kenapa MultipartRequest dipakai.

Langkah 4 tidak wajib, tapi kalau sempat dicoba, ini cara paling meyakinkan untuk melihat *persis* apa yang dikirim Flutter ke server — bukan menduga-duga dari baca kode saja.

services/token_storage.dart — seluruh isi file

    import 'package:flutter_secure_storage/flutter_secure_storage.dart';

    class TokenStorage {
      static const _storage = FlutterSecureStorage();
      static const _key = 'auth_token';

      static Future<void> simpan(String token) => _storage.write(key: _key, value: token);
      static Future<String?> ambil() => _storage.read(key: _key);
      static Future<void> hapus() => _storage.delete(key: _key);
    }

Class ini sengaja dibuat setipis mungkin — tiga method statis yang langsung meneruskan ke `FlutterSecureStorage`, tanpa logika tambahan. Dipakai sebagai satu-satunya pintu masuk/keluar token di seluruh aplikasi: `ApiService.login()` memanggil `simpan()`, `_authHeaders()` memanggil `ambil()`, dan `ApiService.logout()` memanggil `hapus()`. Kalau suatu saat mekanisme penyimpanan token perlu diganti (misal pindah ke library lain), hanya file ini yang perlu disentuh — seluruh layar yang memanggil `ApiService` tidak perlu tahu apa-apa soal perubahan itu.

Coba Sendiri

    1. Login di aplikasi sampai masuk ke /home.
    2. Tutup aplikasi SEPENUHNYA (bukan cuma minimize -- swipe dari
       recent apps), buka lagi dari ikon. Harusnya langsung masuk ke
       /home tanpa diminta login ulang (token masih tersimpan).
    3. Tekan tombol Logout di ProfileScreen, lalu tutup & buka lagi
       aplikasi. Kali ini harus kembali ke layar Login (token sudah
       dihapus TokenStorage.hapus()).
    4. (Opsional, butuh akses ke device/emulator secara langsung)
       Cari lokasi penyimpanan secure storage di Android -- isinya
       tidak bisa dibaca sebagai teks biasa seperti SharedPreferences,
       karena memang dienkripsi oleh Android Keystore.

Langkah 2 dan 3 membuktikan `splash_screen.dart` (Bagian 15) dan `TokenStorage` benar-benar bekerja sama: splash *selalu* mengecek token lebih dulu sebelum memutuskan ke layar mana pengguna diarahkan.

`token_storage.dart` membungkus `flutter_secure_storage` (bukan `SharedPreferences`) karena token JWT adalah kredensial sensitif — `flutter_secure_storage` menyimpannya terenkripsi di keystore (Android) / keychain (iOS), sedangkan `SharedPreferences` menyimpan data sebagai teks biasa yang jauh lebih mudah diakses.

## 20Trace Request: Membuat UMKM Baru Lengkap dengan Foto

Semua bagian sebelumnya membahas file satu-satu. Sekarang diikuti **satu permintaan pengguna** secara utuh — dari tombol ditekan di Flutter sampai baris baru masuk ke Postgres dan responsnya kembali ke layar — supaya terlihat jelas bagaimana potongan-potongan kode yang sudah dibahas itu benar-benar saling memanggil, bukan cuma berdiri sendiri-sendiri.

**Skenario:** pengguna yang sudah login membuka `MyUmkmScreen`, menekan "Buat UMKM", mengisi nama "Warung Bu Siti", memilih foto dari galeri, lalu menekan tombol simpan di `UmkmFormScreen`.

1.  **Flutter — `UmkmFormScreen` submit.** Form tervalidasi lokal dulu (nama tidak boleh kosong), lalu memanggil:

    umkm_form_screen.dart — potongan submit

        final umkmBaru = await _apiService.simpanUmkm(
          id: widget.umkm?.id,         // null karena ini mode "tambah"
          nama: _namaController.text,
          deskripsi: _deskripsiController.text,
          alamat: _alamatController.text,
          fotoPath: _fotoBaru?.path,   // path file lokal hasil image_picker
        );
        if (!mounted) return;
        Navigator.pop(context, true); // beri tahu MyUmkmScreen untuk reload

    Karena `widget.umkm` adalah `null` (mode tambah), `id` yang dikirim ke `simpanUmkm` juga `null`.

2.  **Flutter — `ApiService.simpanUmkm` membangun request.** Karena `id == null`, method HTTP yang dipakai adalah `POST` ke `$baseUrl/umkm` (lihat kode lengkapnya di Bagian 19). Token diselipkan via `_authHeaders()`, field teks (nama/deskripsi/alamat) ditempel ke `request.fields`, dan file foto ditempel ke `request.files` sebagai `MultipartFile` — inilah kenapa request ini memakai `http.MultipartRequest`, bukan `http.post` biasa: body-nya bukan JSON murni, tapi campuran teks + berkas biner dalam satu request (format `multipart/form-data`).

3.  **Go — `main.go` routing & middleware.** Request `POST /api/umkm` cocok dengan pattern yang didaftarkan sebagai `auth(http.HandlerFunc(umkmHandler.Create))`. `auth` (hasil `RequireAuth`, Bagian 09) jalan lebih dulu: membaca header `Authorization: Bearer <token>` yang tadi ditempel di langkah 2, memverifikasinya, lalu menempelkan `userID` ke `context` sebelum meneruskan ke `umkmHandler.Create` yang sesungguhnya.

4.  **Go — `UmkmHandler.Create`.** Mem-parsing multipart form, memanggil `saveUploadedFile(r, "foto", cfg.UploadDir, "umkm")` (Bagian 12) untuk menyimpan file foto ke disk dan mendapat path relatif seperti `"umkm/1730700000000000000.jpg"`, lalu memanggil:

    umkm_handler.go — Create (kode asli, komentar Swagger dipangkas)

        func (h *UmkmHandler) Create(w http.ResponseWriter, r *http.Request) {
            userID := middleware.GetUserID(r)

            r.Body = http.MaxBytesReader(w, r.Body, 5<<20)
            if err := r.ParseMultipartForm(5 << 20); err != nil {
                writeError(w, http.StatusBadRequest, "form tidak valid atau file terlalu besar", "BAD_REQUEST")
                return
            }

            nama := r.FormValue("nama")
            deskripsi := r.FormValue("deskripsi")
            alamat := r.FormValue("alamat")

            fotoPath, err := saveUploadedFile(r, "foto", h.uploadDir, "umkm")
            if errors.Is(err, errInvalidFileType) {
                writeError(w, http.StatusBadRequest, "foto harus berformat jpg/jpeg/png", "BAD_REQUEST")
                return
            }
            if err != nil {
                writeError(w, http.StatusBadRequest, "gagal menyimpan foto", "BAD_REQUEST")
                return
            }

            umkm, err := h.svc.CreateOwn(r.Context(), userID, nama, deskripsi, alamat, fotoPath)
            switch {
            case errors.Is(err, domain.ErrInvalidInput):
                writeError(w, http.StatusBadRequest, "nama UMKM wajib diisi", "BAD_REQUEST")
            case errors.Is(err, domain.ErrConflict):
                writeError(w, http.StatusConflict, "Anda sudah memiliki UMKM", "CONFLICT")
            case err != nil:
                writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
            default:
                writeJSON(w, http.StatusCreated, umkm)
            }
        }

    Perhatikan `r.Body = http.MaxBytesReader(w, r.Body, 5<<20)` di baris paling atas — ini batas ukuran upload 5MB yang belum sempat dibahas di Bagian 12: kalau body request (termasuk file foto) lebih besar dari itu, `ParseMultipartForm` akan gagal lebih dulu sebelum sempat menulis apa pun ke disk, mencegah seseorang sengaja mengunggah file raksasa untuk membebani server.

5.  **Go — `UmkmService.CreateOwn`.** Mengecek dulu lewat `umkmRepo.FindByUserID(ctx, userID)` apakah user ini sudah punya UMKM (aturan "1 user = 1 UMKM" dari Tahap 1 & Bagian 10) — kalau sudah ada, langsung `return domain.ErrConflict` **sebelum** apa pun ditulis ke database. Baru kalau belum ada, `umkmRepo.Create` dipanggil.

6.  **Go — `umkmRepository.Create`.** Menjalankan `INSERT INTO umkm (...) VALUES ($1,$2,$3,$4,$5) RETURNING id` — nilai `$1..$5` diisi dari parameter Go (bukan disambung manual ke string SQL, lihat Bagian 11), dan `id` yang baru dibuat Postgres langsung di-`Scan` balik ke struct `u.ID` di memori Go.

7.  **Balik ke Flutter.** Response `201 Created` berisi JSON data UMKM yang baru dibuat (termasuk `id` dan path foto) diterima `simpanUmkm`, di-parse jadi objek `Umkm` lewat `Umkm.fromJson`, dikembalikan ke `UmkmFormScreen`, lalu `Navigator.pop(context, true)` mengirim sinyal "berhasil" ke `MyUmkmScreen` yang langsung memanggil `_muatUmkm()` untuk menampilkan data yang baru saja dibuat.

Satu baris gagal, seluruh rantai gagal

Kalau di langkah 4 validasi foto gagal (misal file berekstensi `.gif`), rantai berhenti di situ juga — `CreateOwn` tidak pernah dipanggil, tidak ada baris baru di database, dan Flutter menerima `400 Bad Request` yang ditangkap sebagai `ApiException` lalu ditampilkan lewat `SnackBar`. Tidak ada status "setengah tersimpan" — baik semuanya berhasil, atau semuanya gagal di titik pertama yang bermasalah.

## 21Trace Request: Login

Satu lagi alur lengkap, kali ini yang paling sering dijalankan — login — karena melibatkan tiga konsep keamanan sekaligus: bcrypt, JWT, dan penyimpanan token aman.

1.  **Flutter — `LoginScreen._prosesLogin`** (kode lengkap di Bagian 15) memanggil `_apiService.login(email, password)` dengan `email`/`password` polos (belum di-hash di sisi klien — hashing adalah tanggung jawab server, bukan klien).
2.  **Flutter — `ApiService.login`** mengirim `POST /api/auth/login` dengan body JSON `{"email": ..., "password": ...}`. Tidak ada token yang dikirim di langkah ini (memang belum punya).
3.  **Go — rate limiter dulu.** Sebelum sampai ke `AuthHandler.Login`, request melewati `loginLimiter` (Bagian 09) — kalau IP yang sama sudah mencoba login lebih dari 5 kali dalam satu menit, request ditolak di titik ini juga, `AuthService.Login` tidak pernah dipanggil.
4.  **Go — `AuthService.Login`** (kode lengkap di Bagian 09): `userRepo.FindByEmail` mengambil baris user dari database (termasuk `password` yang tersimpan sebagai *hash* bcrypt, bukan teks asli), lalu `bcrypt.CompareHashAndPassword(hash, passwordInput)` membandingkan tanpa pernah men-decode hash itu kembali jadi password asli — bcrypt memang didesain satu arah (tidak bisa dibalik).
5.  **Go — `generateToken`** dipanggil hanya jika password cocok, menghasilkan JWT yang ditandatangani dengan `JWT_SECRET` dari `.env` server, berisi klaim `sub` (ID user) dan `exp` (kedaluwarsa 24 jam dari sekarang).
6.  **Balik ke Flutter — simpan token.** `ApiService.login` menerima `{"data":{"token": "...", "user": {...}}}`, mengambil `body['data']['token']`, lalu memanggil `TokenStorage.simpan(token)` — token masuk ke `flutter_secure_storage`, terenkripsi di keystore/keychain perangkat, **sebelum** `LoginScreen` berpindah ke `/home`.
7.  **Request berikutnya otomatis terautentikasi.** Begitu pengguna membuka tab "UMKM Saya", `getUmkmSaya()` memanggil `_authHeaders()` yang membaca kembali token dari `TokenStorage.ambil()` dan menempelkannya sebagai header `Authorization` — pengguna tidak perlu login ulang untuk setiap request selama token masih berlaku 24 jam.

Kenapa dua trace ini penting dipahami, bukan dihafal

Hampir semua fitur lain di proyek UAS kalian nanti akan mengikuti salah satu dari dua pola alur ini: "kirim data + file lalu simpan ke database" (seperti trace pertama) atau "verifikasi kredensial lalu keluarkan token" (seperti trace kedua). Memahami urutan pemanggilan di sini — bukan menghafal nama fungsinya — adalah yang membuat kalian bisa menulis fitur serupa dari nol untuk ide aplikasi yang berbeda.

## 22Pola yang Berulang di Kedua Sisi

Enam pola berikut muncul berulang kali di kedua proyek — mengenalinya memudahkan kalian membaca (dan menulis) kode serupa di proyek UAS nanti:

1.  **Error mengalir ke atas lewat tipe, bukan lewat angka status** — `domain` dan `service` Go tidak tahu soal HTTP; hanya `handler` yang menerjemahkan `errors.Is(...)` jadi status code.
2.  **Create dan Update digabung satu fungsi** lewat parameter `id`/entity opsional — konsisten di Flutter (`simpanUmkm`/`simpanProduk`) maupun di struktur form (`umkm_form_screen`, `produk_form_screen` dual-mode lewat constructor nullable).
3.  **Validasi ganda client + server** untuk tipe file foto — Flutter mengecek dulu demi UX instan, Go tetap mengecek ulang karena **server tidak pernah boleh percaya input dari klien**.
4.  **Fetch sekali di `initState`, refresh lewat re-assign `Future` di `setState`** — pola standar di semua layar list/detail Flutter, dipilih di atas state management library demi kesederhanaan.
5.  **Otorisasi kepemilikan dicek di service layer**, bukan middleware generik — karena aturannya spesifik per jenis data (UMKM dicek langsung, produk dicek tidak langsung lewat UMKM induknya).
6.  **Satu titik tunggal untuk aturan lintas-fitur** — `normalizePagination` di Go dan `_authHeaders()`/`fotoUrl()` di Flutter: daripada aturan yang sama ditulis ulang di banyak tempat, ditaruh satu fungsi yang dipanggil dari mana-mana.

## 23Rangkuman

Lima tahap — identifikasi masalah, desain, development, testing, deployment — bukan birokrasi yang bisa dilewati, tapi urutan yang membuat keputusan besar (skema database, pembagian endpoint publik/privat, arsitektur layer) diambil **sebelum** menulis kode, bukan ditambal sambil jalan. Proyek UMKM API dan umkm-app yang kalian pakai sejak Pertemuan 4 adalah bukti bahwa tahapan ini bisa menghasilkan kode yang konsisten: pola yang sama (otorisasi di service, validasi ganda, create/update digabung) muncul berulang kali karena memang direncanakan sejak awal, bukan kebetulan.

Pakai kerangka lima tahap ini untuk proyek UAS kalian masing-masing — mulai dari menuliskan masalah yang diselesaikan dengan jelas, sebelum membuka `flutter create`.

Materi ini merangkum dan membedah kode yang sudah dibangun di Pertemuan 4 (UMKM API) dan Pertemuan 5-7 (umkm-app) — bukan materi baru, melainkan fondasi untuk memahami kenapa keputusan arsitektur itu diambil. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
