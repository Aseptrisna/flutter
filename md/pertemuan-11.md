<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 11 · Praktikum 2/5 · Proyek Sendiri

# Membangun Backend Sendiri

Bagian 2 dari rangkaian praktikum. Dokumen desain dari Pertemuan 10 (ERD, `schema.sql`, kontrak API) sekarang diimplementasikan jadi backend sungguhan untuk aplikasi UAS-mu — pola arsitektur, autentikasi, dan keamanannya mengikuti persis **UMKM API** (Pertemuan 9), tapi entitasnya milikmu sendiri. Pilih stack yang kamu kuasai: [Golang](pertemuan-09.html) atau [Node.js + Express](pertemuan-09a.html) — keduanya dipakai sebagai rujukan kode di pertemuan ini.

← [Pertemuan 10: Desain Proyek Sendiri](pertemuan-10.html)
[Pertemuan 12: Fundamental Flutter](pertemuan-12.html) →

## 01Tentang Pertemuan Ini

Semua keputusan desain sudah diambil di Pertemuan 10 — pertemuan ini murni **implementasi**, tidak ada desain ulang. Bawa dokumenmu: `schema.sql`, tabel kontrak API, dan keputusan stack (Go/Node.js).

Tugas Kamu — sebelum mulai

Siapkan folder proyek backend baru untuk aplikasi UAS-mu, ikuti langkah setup dari rujukan stack pilihanmu:

- **Go**: struktur folder `cmd/api`, `internal/{handler,service,repository,domain,middleware}` — lihat [Pertemuan 9 Bagian 08](pertemuan-09.html#s8) untuk peta lengkapnya.
- **Node.js**: struktur folder `src/{handlers,services,repositories,middleware,utils}` — lihat [Pertemuan 9a Bagian 03](pertemuan-09a.html#s3) untuk struktur folder lengkap + cara `npm init`.

Jalankan `schema.sql` dari Pertemuan 10 ke database Neon proyek ini (boleh project Neon baru, terpisah dari UMKM).

## 02Peta Arsitektur Backend

Backend UMKM API (apa pun stack-nya) disusun dalam satu alur yang sama — ini pola yang akan kamu terapkan juga:

alur satu request masuk

    HTTP Request
       ↓
    handler/controller   → baca input (JSON/multipart), panggil service, map error → status HTTP
       ↓
    service              → aturan bisnis: validasi, cek kepemilikan, hash password, dsb
       ↓
    repository           → SQL parameterized ke Postgres, "tidak ketemu" → error khusus
       ↓
    domain/model         → struct/kelas data murni + error bisnis (NotFound, Conflict, Forbidden, InvalidInput)

**Error mengalir ke atas, bukan status HTTP.** `service` dan `repository` tidak pernah tahu apa itu "404" atau "409" — mereka cuma mengembalikan/melempar error domain. Hanya `handler` yang menerjemahkan error itu jadi status HTTP. Penjelasan detail pola ini ada di [Pertemuan 9 Bagian 08](pertemuan-09.html#s8) (Go) dan [Pertemuan 9a Bagian 07](pertemuan-09a.html#s7) (Node.js, pakai kelas `AppError`).

| Sentinel/kelas error | Status HTTP | Kode | Contoh pemicu |
|----|----|----|----|
| InvalidInput | `400` | `BAD_REQUEST` | Field wajib kosong, format salah. |
| (auth gagal di middleware) | `401` | `UNAUTHORIZED` | Token tidak ada/tidak valid. |
| Forbidden | `403` | `FORBIDDEN` | Mengubah/menghapus data milik orang lain. |
| NotFound | `404` | `NOT_FOUND` | ID tidak ada di database. |
| Conflict | `409` | `CONFLICT` | Data unik yang sudah ada (mis. email terdaftar). |

Tugas Kamu

Buat berkas error/domain untuk proyekmu (padanan `domain` di Go atau `errors.js` di Node) berisi minimal 4 jenis error: InvalidInput, NotFound, Conflict, Forbidden — dengan status & kode seperti tabel di atas. Ini dipakai di semua bagian berikutnya.

## 03Autentikasi & Keamanan

Setiap backend butuh register & login, apa pun entitas utamanya. Tiga aturan keamanan yang **wajib** ditiru persis dari UMKM API:

- **Password di-hash dengan bcrypt**, tidak pernah disimpan sebagai teks asli. `Register` meng-hash, `Login` membandingkan lewat fungsi compare bcrypt (bukan dengan `WHERE password = '...'` di SQL — password yang tersimpan sudah ter-hash, tidak bisa dicocokkan langsung lewat query).
- **JWT hanya menerima algoritma HS256**, dan klaim `sub` (user ID) ditempel saat login, dibaca lagi di setiap request yang butuh login.
- **Rate limit di endpoint login** (mis. 5 percobaan/menit/IP) untuk membatasi brute-force password.

pola Register & Login (bahasa-agnostik, intinya sama di Go maupun Node)

    function register(nama, email, password):
        if nama kosong OR email kosong OR panjang(password) < 6:
            throw InvalidInput

        if cariUserByEmail(email) ditemukan:
            throw Conflict   // email sudah dipakai

        hashed = bcryptHash(password)
        simpanUser(nama, email, hashed)

    function login(email, password):
        user = cariUserByEmail(email)
        if user tidak ditemukan:
            throw NotFound   // dibalas sebagai pesan generik "email atau password salah"

        if bukan bcryptCompare(password, user.password):
            throw InvalidInput   // juga dibalas generik, jangan bedakan dgn di atas

        token = jwtSign({ sub: user.id }, exp: 24 jam)
        return token

Kode asli lengkapnya (langsung bisa disalin-sesuaikan): [Pertemuan 9 Bagian 09](pertemuan-09.html#s9) untuk Go (`AuthService.Register/Login`, `RequireAuth` middleware), atau [Pertemuan 9a Bagian 11](pertemuan-09a.html#s11) untuk Node.js (`authService.js` lengkap dengan `bcrypt`/`jsonwebtoken`).

Kenapa pesan error login digeneralisasi?

Baik email tidak ditemukan maupun password salah, keduanya dibalas pesan **yang sama** ("email atau password salah") dengan status 401 — supaya penyerang tidak bisa menebak email mana saja yang terdaftar di sistemmu cuma dari beda-tidaknya pesan error.

Tugas Kamu

1.  Implementasikan `register` & `login` untuk proyekmu, memakai tabel `users` dari `schema.sql` Pertemuan 10.
2.  Pasang middleware auth (JWT) dan rate limiter di endpoint login — sama polanya seperti rujukan.
3.  **Uji dengan curl**: register akun baru, register email sama (harus 409), login benar (harus dapat token), login salah password (harus 401 pesan generik).

## 04Service Layer: Aturan Bisnis & Otorisasi

Di sinilah aturan dari dokumen kebutuhan Pertemuan 10 ditegakkan jadi kode — bukan di handler, bukan di database, tapi di **service**:

- Aturan kuantitas (contoh UMKM: "1 user = 1 UMKM") dicek dengan query `FindByUserID` dulu sebelum `Create` — kalau sudah ada, lempar `Conflict`.
- Kepemilikan dicek manual: `data.userId !== userId yang login` → `Forbidden`, sebelum izinkan update/hapus.
- **Kepemilikan tidak langsung** (seperti produk milik UMKM) ditelusuri berantai: ambil data anak → ambil data induknya → baru bandingkan pemiliknya. Pola ini disebut `authorizeOwner` di UMKM API.

pola authorizeOwner (ownership tidak langsung, 2 level)

    function authorizeOwner(userId, childId):
        child = cariChildById(childId)            // misal: produk
        if child tidak ditemukan: throw NotFound

        parent = cariParentById(child.parentId)    // misal: umkm induknya
        if parent tidak ditemukan: throw NotFound

        if parent.userId != userId:
            throw Forbidden

        return child

Kode asli lengkap (`authorizeOwner`, `CreateOwn`, `UpdateOwn` dengan pola "jangan hapus foto kalau tidak diganti"): [Pertemuan 9 Bagian 10](pertemuan-09.html#s10) (Go) atau [Pertemuan 9a Bagian 12](pertemuan-09a.html#s12) (Node.js, `umkmService.js`/`produkService.js`).

Tugas Kamu

1.  Tulis service untuk entitas utama aplikasimu: `create`, `update`, `delete`, masing-masing memverifikasi kepemilikan sebelum mengizinkan aksi.
2.  Kalau aplikasimu punya relasi berjenjang (entitas anak di bawah entitas induk, seperti produk-di-bawah-UMKM), implementasikan `authorizeOwner` 2 level seperti contoh.
3.  **Uji dengan curl pakai 2 akun berbeda**: akun A buat data, akun B coba edit/hapus data akun A → harus `403 Forbidden`. Lalu akun A edit datanya sendiri → harus berhasil.

## 05Repository & Anti SQL Injection

Repository adalah satu-satunya layer yang boleh menyentuh SQL langsung. Tiga aturan wajib:

- **Selalu parameterized query** (`$1, $2, ...` di Postgres) — **tidak pernah** menyambung string SQL dengan input pengguna lewat `+` atau `sprintf`/template string. Ini (bukan validasi input) yang benar-benar mencegah SQL injection.
- "Baris tidak ketemu" dikonversi jadi error domain (`NotFound`) **di repository** — layer di atasnya tidak perlu tahu detail driver database yang dipakai.
- List kosong selalu dikembalikan sebagai `[]`, bukan `null`/`nil` — supaya Flutter yang menerimanya tidak perlu menangani kasus `null` di setiap tempat.

pola query aman (sintaks Postgres, berlaku untuk pgx maupun node-postgres)

    -- AMAN: nilai pengguna lewat sebagai parameter terpisah
    SELECT id, nama FROM umkm
    WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')
    ORDER BY id DESC LIMIT $2 OFFSET $3;

    -- BERBAHAYA, JANGAN PERNAH DITULIS (menyambung string manual):
    -- "SELECT * FROM umkm WHERE nama ILIKE '%" + q + "%'"

Query lengkap tiap fungsi repository (`FindAll`, `FindByID`, `Create`, `Update`, `Delete`) dengan penjelasan baris-per-baris sudah dibahas tuntas di [Pertemuan 9 Bagian 11](pertemuan-09.html#s11) (Go, pakai `pgx`) dan [Pertemuan 9a Bagian 10](pertemuan-09a.html#s10) (Node.js, pakai `pg` — perhatikan juga catatan penting soal `COUNT(*)` yang balik sebagai string di node-postgres, wajib `Number()`). Kalau butuh mengingat kembali fundamental `SELECT`/`INSERT`/`UPDATE`/`DELETE`/`JOIN` satu per satu, itu ada di [Pertemuan 9 Bagian 04](pertemuan-09.html#s4) dan sudah kamu praktikkan sendiri di Pertemuan 10 Bagian 06.

Tugas Kamu

1.  Tulis repository untuk tiap tabel di `schema.sql`-mu: minimal `create`, `findAll` (dengan pencarian+pagination), `findById`, `update`, `delete`.
2.  Pastikan **semua** query memakai parameter (`$1, $2, ...`), tidak ada satu pun string SQL yang disambung manual dari input pengguna.
3.  **Uji keamanannya**: coba kirim `q=';DROP TABLE <nama_tabelmu>;--` ke endpoint pencarianmu — harus tetap `200 OK` dengan hasil kosong/wajar, dan tabelmu harus tetap utuh setelahnya.

## 06Upload Foto & Migration

Kalau aplikasimu punya fitur unggah foto (produk, profil, dsb), tiga aturan yang sama dipakai di UMKM API:

- **Whitelist ekstensi** (hanya `.jpg`/`.jpeg`/`.png`), dicek **sebelum** file ditulis ke disk — bukan sesudah.
- Nama file disimpan dibuat ulang dari timestamp/angka acak, **tidak** memakai nama asli dari pengguna (mencegah karakter aneh/path traversal).
- Path yang disimpan ke database adalah path **relatif** (mis. `"produk/169....jpg"`), supaya mudah digabung jadi URL publik `/uploads/<path>`.
- File lama dihapus dari disk setelah update/delete sukses di database — mencegah file "yatim" menumpuk.

Kode lengkap `saveUploadedFile`/`deleteFile`: [Pertemuan 9 Bagian 12](pertemuan-09.html#s12) (Go, manual lewat `io.Copy`) atau [Pertemuan 9a Bagian 09](pertemuan-09a.html#s9) (Node.js, pakai `multer` — jauh lebih ringkas karena sebagian besar proses ditangani otomatis oleh library).

### Migration database

Skema yang kamu jalankan manual di Neon SQL Editor (Pertemuan 10) di proyek sungguhan sebaiknya dicatat sebagai *migration file* bernomor urut, bukan diubah diam-diam lewat SQL Editor setiap kali ada perubahan — supaya skema bisa dijalankan ulang identik di server mana pun. Untuk tugas kuliah skala kecil, cukup simpan `schema.sql`-mu di root proyek sebagai dokumentasi; kalau mau meniru persis pola migration bernomor seperti UMKM API, lihat [Pertemuan 9 Bagian 12](pertemuan-09.html#s12) ("Migration — `cmd/migrate/main.go`").

Tugas Kamu

Kalau aplikasimu butuh upload foto: implementasikan validasi ekstensi + penyimpanan file dengan nama unik, lalu **uji** upload file `.jpg` asli (harus berhasil) dan file yang diubah ekstensinya jadi `.jpg` padahal isinya teks biasa (harus tetap tervalidasi sesuai yang dicek backend-mu — kalau validasi hanya dari ekstensi nama file, catat ini sebagai keterbatasan untuk didiskusikan, bukan dianggap bug).

## 07Menjalankan & Menguji Backend Sendiri

Sebelum lanjut ke Flutter (Pertemuan 12), backend-mu harus benar-benar jalan dan teruji dari luar (lewat curl/Postman), bukan cuma "kelihatannya benar" dari membaca kode.

1.  Jalankan server lokal (`go run ./cmd/api` atau `npm run dev`), pastikan tersambung ke database tanpa error.
2.  Tes `register` → `login` → simpan token.
3.  Tes `create` entitas utama pakai token tadi → catat `id`-nya.
4.  Tes `list` (publik, tanpa token) → data yang baru dibuat harus muncul.
5.  Tes `update`/`delete` dengan akun yang BUKAN pemilik → harus `403`.
6.  Tes endpoint pencarian dengan payload SQL injection → harus tetap aman.

Checkpoint

Kalau keenam langkah di atas semua berhasil sesuai yang diharapkan, backend-mu siap dipakai Flutter. Simpan urutan perintah curl yang kamu pakai — ini akan dipakai ulang sebagai bahan trace request di Pertemuan 14.

## 08Rangkuman & Checklist

- Berkas error/domain (InvalidInput/NotFound/Conflict/Forbidden) sudah ada dan dipakai konsisten.
- Register & login jalan, password ter-hash (cek langsung di database, bukan percaya dari luar), JWT+rate limit terpasang.
- Service layer menegakkan aturan bisnis & ownership (termasuk ownership berjenjang kalau ada).
- Semua query di repository memakai parameter, teruji aman dari SQL injection.
- Upload foto (kalau ada) tervalidasi & tersimpan dengan nama unik.
- Seluruh alur di atas sudah diuji lewat curl/Postman dari luar, bukan cuma dibaca kodenya.

← [Pertemuan 10: Desain Proyek Sendiri](pertemuan-10.html)
[Pertemuan 12: Fundamental Flutter](pertemuan-12.html) →

Bagian 2 dari 5 rangkaian praktikum proyek UAS — lanjut ke [Pertemuan 12: Fundamental Flutter, Konek API & Halaman Awal](pertemuan-12.html). — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
