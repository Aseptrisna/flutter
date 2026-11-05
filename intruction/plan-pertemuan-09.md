# Plan — Pertemuan 9

Sumber permintaan: `intruction/pertemuan-09.md`

## Pemahaman

Materi baru "Pertemuan 9", dua bagian besar:
1. Tahapan membuat aplikasi Android dari masalah → desain → selesai.
2. Bedah detail proyek yang sudah ada di course ini sebagai studi kasus:
   - Golang UMKM API (pertemuan-04) — dijelaskan per fungsi, kenapa ada.
   - Flutter UMKM App (pertemuan-07) — dijelaskan per halaman, UI, dan cara konek ke API.

Posisinya "menengok ke belakang" — merangkum kenapa arsitektur pertemuan 4 & 7 dibuat seperti itu, dibungkus dalam kerangka tahapan pengembangan software, bukan materi fitur baru.

## Konvensi yang diikuti

File dibuat sebagai `pertemuan-09.html`, mengikuti format HTML lecture page yang sama persis dengan file lain (dicek dari `pertemuan-08.html`): sidebar nav sticky, tema gelap dengan CSS vars yang sama, font Space Grotesk/Inter/JetBrains Mono, komponen `.codecard`, `.note`, `.warn`, `.verify`, `.steps`. Didaftarkan di `index.html`.

## Langkah

1. Baca ulang kode sumber `umkm-api/` dan `umkm-app/lib/` (bukan cuma prosa HTML pertemuan-04/07) untuk ambil daftar fungsi Go & daftar halaman Flutter yang akurat.
2. Susun struktur section `pertemuan-09.html`:
   - Bagian 1: Tahapan pengembangan aplikasi Android, tiap tahap dikaitkan ke contoh nyata dari proyek UMKM. Tahap "Desain" dipecah jadi 4 sub-bagian dengan tools konkret:
     - **Desain alur & UX** — 3 level kedalaman: (1) user flow pakai pensil/kertas atau Excalidraw/draw.io, (2) wireframe pakai Figma/Balsamiq, (3) mockup/prototype klik-navigasi pakai Figma (frame + prototyping mode).
     - **Desain arsitektur sistem** — diagram layer kode (handler→service→repository→domain) pakai draw.io/Excalidraw/Figma.
     - **Desain database** — ERD pakai dbdiagram.io atau draw.io, diturunkan dari kebutuhan fungsional Tahap 1.
     - **Desain kontrak API** — bentuk request/response tiap endpoint disepakati pakai Swagger/OpenAPI sebelum Flutter & Go ditulis bersamaan.
   - Bagian 2: Bedah Golang UMKM API per fungsi (handler, middleware, service, repository, upload, migration) — apa & kenapa.
   - Bagian 3: Bedah Flutter UMKM App per halaman (splash, login/register, home, umkm list/detail/form, profile, ApiService/TokenStorage) — UI & cara konek ke API.
3. Tulis file HTML-nya mengikuti styling `pertemuan-08.html` persis.
4. Update `index.html`: isi salah satu slot kosong jadi "Pertemuan 9" dengan title/desc/href yang sesuai.
5. Update memory `course_roadmap.md` untuk mencatat pertemuan-09 sebagai final ditambahkan.

## Status

- [x] Langkah 1 — riset kode `umkm-api`/`umkm-app` (lewat sub-agent).
- [x] Langkah 2 & 3 — `pertemuan-09.html` ditulis (20 section).
- [x] Langkah 4 — `index.html` diupdate, entri Pertemuan 9 aktif.
- [x] Langkah 5 — memory `course_roadmap.md` diupdate.
- [x] Langkah 6 — pendalaman detail di semua section atas permintaan user ("semuanya sedetail mungkin"):
  - **Tahap 1 (Identifikasi Masalah):** tabel teknik pengumpulan kebutuhan (wawancara/survei, analisis kompetitor, user persona, daftar kebutuhan fungsional & non-fungsional) + tools (Google Forms, Figma/Canva, Notion/Docs).
  - **Tahap 2 (Desain):** 4 sub-bagian dengan tools konkret — alur/UX (3 level: user flow di Excalidraw/draw.io, wireframe di Figma/Balsamiq, mockup/prototype di Figma), arsitektur sistem, database (ERD via dbdiagram.io), kontrak API (Swagger/OpenAPI).
  - **Tahap 3 (Development):** tabel tools (VS Code + ekstensi, Git/GitHub, go.mod/pubspec.yaml, Swagger/Postman, psql/TablePlus, emulator/device).
  - **Tahap 4 (Testing):** tabel tools per jenis testing (manual API via Postman, `go test`, `flutter test`, static analysis, manual QA checklist).
  - **Tahap 5 (Deployment):** tabel opsi layanan (Neon, Railway/Render/Fly.io, object storage, Play Console, GitHub Actions CI/CD, UptimeRobot).
  - **Golang (Bagian 08):** tabel peta lengkap 18 endpoint (method+path, handler function, auth, keterangan) dan tabel pemetaan sentinel error → status HTTP (400/401/403/404/409).
  - **Flutter (Bagian 13):** tabel dependency `pubspec.yaml` sungguhan (`http`, `flutter_secure_storage`, `image_picker`, `cupertino_icons`) dan fungsinya masing-masing.
- Validasi akhir: 20 nav anchor = 20 heading, semua tag HTML (div/table/tr/ul/ol) seimbang.
- [x] Langkah 7 — user bilang "masih belum puas", diklarifikasi lewat AskUserQuestion: kode kurang lengkap, penjelasan kurang dalam, tahapan kurang nyambung ke kode, format/tampilan kurang ("terlalu AI slop"). Perbaikan:
  - Menambah 2 section baru **Trace Request end-to-end** (sekarang s19 "Membuat UMKM + Foto" dan s20 "Login") — mengikuti satu permintaan pengguna sungguhan dari tombol di Flutter sampai baris masuk ke Postgres dan balik lagi, memakai kode ASLI (bukan simplifikasi) dari `umkm_handler.go Create`, `UmkmService.CreateOwn`, `umkmRepository.Create`, `AuthService.Login`, dst — ini yang menjembatani kesenjangan antara "tahapan abstrak" dan "bedah kode per file" yang sebelumnya terasa terpisah.
  - Section lama s19/s20 (Pola Berulang, Rangkuman) di-renumber jadi s21/s22.
  - 7 blok `.codecard` kode asli ditambahkan sebelumnya (RequireAuth, AuthService Register/Login/generateToken, ProdukService authorizeOwner/UpdateOwn, umkm_repository FindAll/FindByID, upload.go, login_screen _prosesLogin, myumkm_screen ValueKey trick, api_service simpanUmkm/_authHeaders, token_storage.dart) — total jadi 13 codecard kode nyata di seluruh halaman.
  - Bug ditemukan & diperbaiki 2x: (1) generic Dart (`Future<void>`, `State<X>`, dst) ditulis mentah tanpa escape HTML — browser akan mengira itu tag HTML dan merusak tampilan kode; semua diganti `&lt;&gt;`. (2) Go bitshift (`5<<20`) juga sama, perlu `&lt;&lt;`. (3) snippet `umkm_handler.go Create` yang tadinya "disederhanakan" ternyata meleset dari kode asli (nama field `h.svc` bukan `h.service`, urutan parameter `writeError`) — diganti kode asli persis (komentar Swagger saja yang dipangkas).
  - Validasi akhir: 22 nav anchor = 22 heading, semua tag seimbang (div 38, table 10, tr 73, ul 11, ol 7, pre 13), 13 codecard.
- [x] Langkah 8 — user masih belum puas: "mahasiswa tidak bisa mencoba setiap potongan code nya". Diklarifikasi via AskUserQuestion → dipilih opsi "Instruksi coba nyata per fungsi". Ditambahkan 9 kotak `.try` ("Coba Sendiri", style baru warna biru) menempel di codecard-codecard kunci:
  - `RequireAuth` — 3 curl (tanpa token/token asal/tanpa prefix Bearer) + cara baca hasilnya.
  - `AuthService Register/Login` — 4 curl (register, register duplikat→409, login, login salah password→400) + cara verifikasi password ter-hash bcrypt lewat psql.
  - `ProdukService authorizeOwner` — skenario 2 akun berbeda untuk memicu 403 Forbidden sungguhan.
  - `umkm_repository FindAll/FindByID` — curl 404 + percobaan SQL injection di parameter `q` untuk membuktikan parameterized query aman.
  - `upload.go` — upload file `.jpg` asli vs file disamarkan jadi `.pdf` untuk memicu 400 validasi tipe file.
  - `login_screen._prosesLogin` — 3 skenario manual di app (password invalid, login sukses, password salah) + saran `debugPrint` untuk lihat `_loading` berubah di Debug Console.
  - `myumkm_screen` ValueKey trick — eksperimen `debugPrint` di `initState` untuk MEMBUKTIKAN remount terjadi, termasuk langkah "sengaja merusak" (hapus `key:`) untuk membuktikan triknya perlu, lalu dikembalikan.
  - `api_service.simpanUmkm` — `debugPrint` untuk melihat pemilihan POST/PUT otomatis + saran pakai Proxyman/DevTools Network tab untuk lihat request asli.
  - `token_storage.dart` — skenario tutup-buka app setelah login vs setelah logout untuk membuktikan splash screen benar-benar membaca token.
  - Semua placeholder di contoh curl diganti jadi `ALL_CAPS_TANPA_KURUNG` (bukan `<...>`) setelah ketemu kasus beberapa placeholder awal tidak di-escape dan berisiko dikira tag HTML oleh browser — sudah diperbaiki semua.
  - Validasi akhir: 22 nav anchor = 22 heading, semua tag seimbang (div 47, table 10, tr 73, ul 11, ol 7, pre 22), 13 codecard, 9 try-box, tidak ada placeholder `<kata>` mentah yang lolos dari escaping.
- [x] Langkah 9 — permintaan baru user: tambahkan materi fundamental query database (SQL) agar mahasiswa belajar ulang konsep dasar query yang bisa dijalankan di Neon, memakai **semua query asli yang dipakai umkm-api**, supaya mereka terbayang konsep dasarnya.
  - Percobaan pertama: dibuat sebagai section standalone baru **s11** sebelum section Repository (semua section setelahnya di-renumber +1).
  - User koreksi: "baiknya di masukan ke c. Desain database dong bro" — konten dipindah jadi **bagian dari sub-section `s4` → `h3 c. Desain database`** (bukan section/nav sendiri), karena memang secara konsep itu kelanjutan dari ERD yang sudah dibahas di situ. Section standalone s11 dihapus, semua section setelahnya di-renumber turun lagi ke nomor semula (11-22, utuh seperti sebelum Langkah 9), dan semua referensi silang "Bagian N" yang sempat ikut bergeser dikembalikan ke nomor asalnya.
  - Isi akhir di `c. Desain database` (urutan: paragraf ERD asli → paragraf transisi "ERD itu cuma gambar, hasilnya tetap harus diterjemahkan jadi SQL" → `h4 Skema tabel asli` → `h4 Lima perintah dasar`), dibaca langsung dari source asli: `migrations/000001_init.up.sql` (3 `CREATE TABLE`: users/umkm/produk, dengan `SERIAL PRIMARY KEY`, `REFERENCES ... ON DELETE CASCADE`, `UNIQUE`) dan semua query di `user_repository.go`, `umkm_repository.go`, `produk_repository.go` (`INSERT...RETURNING`, `SELECT...WHERE`, `SELECT...ILIKE` + `ORDER BY/LIMIT/OFFSET` pagination, `SELECT COUNT(*)`, `UPDATE...SET`, `DELETE FROM`).
  - Tabel "Lima perintah dasar" menampilkan tiap query asli dalam bentuk nilai literal (bukan placeholder `$1`) supaya bisa langsung ditempel ke Neon SQL Editor.
  - Kotak **Coba Sendiri** baru (jadi try-box ke-10, menempel di akhir `c. Desain database`): instruksi `\dt`/`\d umkm`, `SELECT`/`UPDATE` manual langsung di Neon SQL Editor atau `psql` memakai database Pertemuan 4 mereka sendiri, lalu buka ulang aplikasi Flutter untuk melihat perubahan data via SQL langsung muncul di UI — bukti konkret API = jembatan HTTP ke query yang sama.
  - Validasi akhir: 22 nav anchor = 22 heading (utuh seperti semula, tidak ada section baru di nav), semua tag seimbang (div 50, table 11, tr 80, ul 12, ol 7, pre 24, h3 13, h4 2), 14 codecard, 10 try-box.
- [x] Langkah 10 — permintaan user: tambahkan tool khusus untuk desain database yang kelihatan garis relasinya (bukan cuma daftar kolom per tabel). Ditambahkan di awal `c. Desain database`, sebelum penjelasan skema/query:
  - Tabel baru **"Tool untuk menggambar relasi antar tabel"** membandingkan dbdiagram.io (rekomendasi — tulis DBML, garis relasi tergambar otomatis dari `ref:`), DrawSQL (drag-and-drop visual), dan draw.io/Excalidraw (kanvas bebas, garis ditarik manual).
  - Codecard baru berisi skema UMKM App asli ditulis ulang dalam sintaks **DBML** (`Table users/umkm/produk { ... }` + `Ref: umkm.user_id > users.id` + `Ref: produk.umkm_id > umkm.id`) — siap tempel langsung ke editor dbdiagram.io.
  - Kotak **Coba Sendiri** baru (try-box ke-11): buka dbdiagram.io, tempel DBML di atas, lihat garis relasi + notasi crow's foot tergambar otomatis dari baris `Ref:`, dan eksperimen ganti `>` jadi `-` untuk melihat beda notasi "satu-ke-banyak" vs "satu-ke-satu".
  - Validasi akhir: 22 nav anchor = 22 heading, semua tag seimbang (div 53, table 12, tr 84, ul 12, ol 7, pre 25, h3 13, h4 3), 15 codecard, 11 try-box.
- [x] Langkah 11 — permintaan user: query yang bisa dicoba copy-paste langsung oleh tiap mahasiswa di Neon masing-masing (sebelumnya try-box SQL mengasumsikan sudah ada data dengan `id = 1` dari percobaan curl, tidak aman buat mahasiswa yang datanya beda/belum ada). Try-box SQL di `c. Desain database` ditulis ulang total jadi mandiri:
  - Langkah 2: satu query `INSERT` berantai user→umkm→produk pakai CTE (`WITH ... AS`, `RETURNING`) dengan email acak (`'latihan' || floor(random()*1000000) || '@mail.com'`) — aman dijalankan berkali-kali tanpa bentrok unique constraint, tidak butuh id siapa pun.
  - Langkah 3: query `JOIN` tiga tabel sekaligus (baru, belum ada contoh JOIN eksplisit di section ini sebelumnya) untuk membuktikan relasi ERD/DBML dari section tool di atas benar-benar bisa disatukan jadi satu baris hasil.
  - Langkah 4-6: `UPDATE`/`DELETE` dicari lewat `nama` (bukan `id` hardcoded) supaya tetap jalan untuk siapa pun, plus pembuktian `ON DELETE CASCADE` lewat hitung produk sebelum/sesudah UMKM dihapus.
  - Langkah 7: beres-beres hapus user latihan supaya tidak menyisakan data sampah permanen di database masing-masing.
  - Validasi akhir tidak berubah dari langkah sebelumnya (isi try-box diganti, jumlah div/table/tr/pre tetap sama persis): 22 nav = 22 heading, semua tag seimbang, 15 codecard, 11 try-box.
- [x] Langkah 12 — user minta materi dipecah **per query disertai penjelasan**, bukan dipadatkan jadi satu tabel + satu try-box raksasa. "Lima perintah dasar" dirombak total jadi 7 blok berurutan, tiap blok formatnya konsisten: heading kecil → codecard (query literal asli dari repository Go) → paragraf penjelasan → kotak Coba Sendiri sendiri (query copy-paste + hasil yang diharapkan):
  1. `INSERT...RETURNING` — sekaligus jadi try-box pembuat data latihan berantai (CTE `WITH...AS`, user→umkm→produk, dipakai ulang di semua langkah berikutnya).
  2. `SELECT...WHERE` — cari user latihan lewat nama.
  3. `SELECT...ILIKE` + `ORDER BY/LIMIT/OFFSET` — cari & urutkan umkm latihan, penjelasan pagination `LIMIT/OFFSET`.
  4. `SELECT COUNT(*)` — hitung produk, sekalian kenalkan konsep *subquery*.
  5. `SELECT...JOIN` — bagian baru: menyatukan 3 tabel jadi 1 baris hasil, bukti relasi paling konkret (dicatat "belum ada di repository Go manapun secara langsung, tapi inilah cara SQL sebenarnya membuktikan relasi").
  6. `UPDATE...SET` — edit umkm, verifikasi via SELECT ulang + saran cek di tab Flutter.
  7. `DELETE FROM` + pembuktian `ON DELETE CASCADE` — hitung produk sebelum/sesudah, ditutup query beres-beres hapus user latihan.
  - Validasi akhir: 22 nav anchor = 22 heading, semua tag seimbang (div 73, table 11, tr 77, ul 12, ol 7, pre 38, h3 13, h4 3), 22 codecard, 17 try-box.
- [x] Langkah 13 — user kasih screenshot try-box CTE langkah 1 dan bilang "satu satu dong bro, register, login, buat umkm, lihat umkm, itu query nya bagaimana" — koreksi: dasarnya bukan "query per perintah SQL" (INSERT/SELECT/UPDATE/DELETE sebagai kategori abstrak), tapi **query per aksi nyata yang dilakukan pengguna di aplikasi**. CTE gabungan 3-INSERT-sekaligus di langkah sebelumnya dianggap membingungkan karena tidak dipetakan ke aksi yang mereka kenal. Seluruh 7 blok dirombak ulang jadi urutan aksi aplikasi sungguhan, tiap aksi query-nya SATU saja (tidak ada CTE):
  1. **Register** — `INSERT INTO users ... RETURNING id`, try-box: catat `id` hasilnya untuk langkah 3.
  2. **Login** — `SELECT ... WHERE email = ...` (ditegaskan: SQL tidak mencocokkan password, itu kerja Go/bcrypt di belakangnya).
  3. **Buat UMKM** — `INSERT INTO umkm (user_id, ...)` memakai `id` dari langkah 1, try-box bonus: coba `user_id` yang tidak ada → harus error foreign key violation, bukti `REFERENCES` ditegakkan Postgres.
  4. **Lihat Daftar UMKM** — `FindAll` + `Count` berpasangan (gabungan dari versi lama langkah 3 & 4).
  5. **Lihat Detail UMKM** — dijelaskan Go aslinya 2 `SELECT` terpisah (umkm lalu produk), lalu diberi versi `JOIN` sebagai pembelajaran cara SQL menyatukan relasi, try-box: insert 1 produk dulu baru JOIN.
  6. **Edit UMKM** — `UPDATE ... SET` semua kolom.
  7. **Hapus UMKM** — `DELETE` + pembuktian `ON DELETE CASCADE` (sama seperti sebelumnya, konsisten dengan data latihan nomor 1 & 3).
  - Validasi akhir tidak berubah dari langkah 12 (isi try-box/codecard diganti, jumlah tag tetap sama persis): 22 nav = 22 heading, semua tag seimbang (div 73, table 11, tr 77, ul 12, ol 7, pre 38), 22 codecard, 17 try-box.

## Catatan: materi terpisah Pertemuan 9a (2026-11-05)

Permintaan baru user: "buatkan Materi 09-a membangun umkm-api dengan node js express dan postgree sql, tutorial lengkap detail dan project bisa diimplementasikan tanpa error". Ini halaman BARU terpisah (`pertemuan-09a.html`), bukan edit lanjutan ke `pertemuan-09.html` di atas — dicatat di sini sekadar sebagai lampiran karena topiknya berhubungan langsung (membangun ulang `umkm-api` yang sama di Pertemuan 9 dengan stack berbeda).

- Dibuat `pertemuan-09a.html`, 19 section, mengikuti template visual `pertemuan-07a.html` (sidebar nav + toc ganda + codecard/note/warn/verify).
- Sebelum menulis satu baris pun prosa, seluruh source Go asli dibaca ulang (`main.go`, `response.go`, semua handler/service/repository, `upload.go`, `middleware/auth.go` & `ratelimit.go`, `config.go`) untuk memastikan port Node-nya 1:1 akurat (bentuk JSON error `{"error":{"message","code"}}`, aturan 1-user-1-UMKM, authorizeOwner 2-level untuk produk, dsb).
- **Seluruh kode ditulis ke disk dan benar-benar dijalankan**, bukan cuma ditulis dari ingatan: dibuat instance PostgreSQL 17 lokal sekali pakai di scratchpad (port custom, socket dir custom karena path scratchpad kepanjangan untuk Unix socket default), schema dijalankan, server Node dinyalakan sungguhan, lalu diuji end-to-end lewat curl: register/login/validasi 400/409/401, buat UMKM+produk dengan upload foto `.jpg` asli, tolak upload `.txt`, ownership 403 (dua akun), cascade delete (produk ikut hilang saat UMKM dihapus), SQL injection di parameter `q` (aman), rate limit login (429 di percobaan ke-6). Semua hasil asli (bukan karangan) dicantumkan di Bagian 16 materi.
- Proyek yang sudah teruji itu disalin ke repo ini di `umkm-api-node/` (tanpa `node_modules/`, `.env` asli, dan isi `uploads/`) sebagai referensi kerja, sejajar dengan `umkm-api/` (Go) dan `umkm-app/` (Flutter) yang sudah ada.
- Bug/gotcha nyata yang ditemukan selama pengujian dan sengaja didokumentasikan di materi: `COUNT(*)` dan kolom `NUMERIC` selalu dibalas node-postgres sebagai STRING, wajib `Number()` manual (beda dari Go yang otomatis scan ke tipe asli) — kalau lupa, `meta.total`/`harga` di JSON jadi string bertanda kutip, bukan error keras tapi silent behavior mismatch.
- `index.html` diperbarui: entri baru `num: "9a"` ditambahkan setelah entri Pertemuan 9, mengikuti pola penomoran `1a`/`1b`/`7a` yang sudah ada.
- Memory `course_roadmap.md` diperbarui mencatat `umkm-api-node/` sebagai checkout ketiga di repo ini.
- Validasi struktur HTML akhir: 19 `h2` = 19 section, nav sidebar + toc (38 link total, masing-masing 19) cocok semua, semua tag seimbang (div 84, table 2, tr 24, ul 2, ol 4, pre 34), 34 codecard, tidak ada placeholder/tag mentah yang lolos escaping.

## Catatan: section baru s13 "Fundamental Flutter" di pertemuan-09.html (2026-11-05)

Permintaan baru user: "pertemuan-09.html fundamental flutter supaya mahasiswa paham membuat layout tampilan, konek ke api nya bro, tambahkan materi ini". Ini EDIT ke `pertemuan-09.html` utama (bukan ke 09a), ditambahkan sebagai section baru **s13 "Fundamental Flutter: Membangun Layout & Konek ke API"**, disisipkan sebelum "Flutter: Peta Halaman UMKM App" (yang lama s13, sekarang bergeser ke s14) — simetris dengan cara section fundamental SQL ditambahkan di sisi Golang. Semua section s13-s22 lama di-renumber +1 jadi s14-s23 (script Python descending), referensi silang "Bagian N" yang ikut bergeser (18→19, 14→15 di beberapa tempat) sudah diperbaiki.

Isi section baru, dibaca langsung dari source `umkm-app/lib/` (bukan dikarang):
- **a. Widget dasar tata letak** — tabel `Column`/`Row`/`Padding`+`SizedBox`/`Expanded` dengan kolom "dipakai di mana" merujuk kode nyata, plus codecard tampilan error asli dari `umkm_list_screen.dart`.
- **b. Menampilkan daftar data** — `ListView.builder` asli dari `umkm_list_screen.dart`, dijelaskan kenapa bukan `ListView`/`Column` manual (lazy-build vs build-semua-sekaligus).
- **c. Struktur dasar satu halaman** — kerangka umum `StatefulWidget`+`Scaffold`+`initState` yang dipakai semua layar di app ini.
- **d. Fundamental konek ke API** — konsep `Future<T>`/`async`/`await`/`jsonDecode` dijelaskan dulu, lalu codecard nyata `ApiService.getUmkmList` baris-per-baris, ditutup `FutureBuilder` asli dari `umkm_list_screen.dart` (3 kondisi: waiting/error/data) + catatan kenapa fetch di `initState` bukan `build()`.
- Try-box (jadi try-box ke-18): dua jalur — DartPad untuk eksperimen layout murni tanpa backend, dan `debugPrint(response.body)` di `api_service.dart` untuk melihat JSON mentah sungguhan di Debug Console memakai server yang sudah berjalan dari Pertemuan 4-9.
- Validasi akhir: 23 nav anchor = 23 heading, semua tag seimbang (div 85, table 12, tr 82, ul 13, ol 7, pre 43, h3 17, h4 4), 27 codecard, 18 try-box, tidak ada generic Dart (`State<X>`, `Future<T>`, dll) yang lolos tanpa escape `&lt;&gt;`.
