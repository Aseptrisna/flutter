# Plan — Pertemuan 10-14 (Pecahan Praktikum dari Pertemuan 9)

Sumber permintaan: percakapan lanjutan setelah `pertemuan-09.html` & `pertemuan-09a.html` selesai — user minta materi itu dipecah jadi beberapa pertemuan praktikum, supaya setiap mahasiswa mengikuti langkah yang sama tapi diterapkan ke **proyek UAS mereka sendiri** (dari Pertemuan 8), bukan cuma membaca studi kasus UMKM secara pasif.

## Pemahaman yang disepakati

- `pertemuan-09.html` (23 section, studi kasus UMKM API+App lengkap) **dipertahankan apa adanya** sebagai referensi/bedah kode utuh — tidak dibongkar.
- Dibuat 5 pertemuan baru (10-14) yang "menerjemahkan" isi `pertemuan-09.html` jadi langkah praktikum bertahap, tiap bagian ditutup kotak **"Tugas Kamu"**: instruksi konkret menerapkan konsep yang sama ke app masing-masing mahasiswa.
- Materi database dipecah **Opsi A** (dikonfirmasi user): desain (ERD + fundamental SQL) di Pertemuan 10, implementasi (repository/query sungguhan) di Pertemuan 11 — bukan satu pertemuan database berdiri sendiri.
- Stack backend boleh pilih Go (`pertemuan-09.html`) atau Node.js (`pertemuan-09a.html`) sebagai referensi — mahasiswa pakai yang mereka kuasai dari pertemuan sebelumnya.

## Pemetaan isi per pertemuan

| Pertemuan | Judul | Sumber section dari pertemuan-09.html | Deliverable mahasiswa |
|---|---|---|---|
| 10 | Identifikasi Masalah & Desain Proyek Sendiri | s2, s3, s4 (UX, arsitektur, **database+SQL fundamental**, kontrak API) | Dokumen desain: daftar kebutuhan, user flow, ERD+skema SQL, draft endpoint API — untuk app sendiri |
| 11 | Membangun Backend Sendiri (Arsitektur, Auth, **Repository/SQL**, Upload) | s8, s9, s10, s11 (**repository & SQL implementasi**), s12 | Backend API sendiri jalan: register/login + minimal 1 CRUD + upload foto |
| 12 | Fundamental Flutter: Layout, Konek API & Halaman Awal | s13, s15 | Alur auth (splash→login/register→home) jalan nyata, nyambung ke backend sendiri |
| 13 | Halaman CRUD Lengkap & ApiService | s14, s16, s17, s18, s19 | CRUD penuh (list/detail/tambah/edit/hapus) untuk entitas utama app sendiri |
| 14 | Trace Request, Testing, Deployment & Rangkuman | s5, s6, s7, s20, s21, s22, s23 | 1 trace request tertulis (app sendiri) + checklist kesiapan UAS |

## Konvensi

- File: `pertemuan-10.html` s/d `pertemuan-14.html`, mengikuti format HTML lecture page yang sama (dicek dari `pertemuan-09.html`): sidebar nav, `.codecard`/`.note`/`.warn`/`.verify`/`.try` component classes.
- Tambahan komponen baru: kotak `.task` ("Tugas Kamu") — biru/aksen berbeda dari `.try`, berisi instruksi menerapkan konsep ke proyek sendiri (bukan sekadar mencoba kode contoh).
- Tiap pertemuan tetap memuat contoh kode UMKM asli (dari `pertemuan-09.html`/`umkm-api`/`umkm-app`) sebagai rujukan, karena mahasiswa butuh contoh konkret sebelum menerapkan ke proyek sendiri yang bentuknya beda-beda.
- Didaftarkan di `index.html` begitu tiap file selesai dibuat.

## Status

- [x] Plan ini dibuat & disepakati (Opsi A dikonfirmasi user).
- [x] Pertemuan 10 — Identifikasi Masalah & Desain Proyek Sendiri.
  - 8 section: Tentang Pertemuan Ini (+ tabel ringkasan 5 pertemuan), Tahapan Umum, Tahap 1 Identifikasi (+ Tugas Kamu), Tahap 2 Desain UX & Arsitektur (+ Tugas Kamu), Desain Database ERD & Relasi (+ Tugas Kamu), Fundamental SQL 7 Aksi Nyata diringkas jadi 1 tabel + rujuk ke Pertemuan 9 Bagian 04 untuk versi detail (+ Tugas Kamu), Desain Kontrak API (+ Tugas Kamu), Rangkuman & Checklist 4-item sebelum lanjut Pertemuan 11.
  - Komponen baru `.task` (kotak ungu "Tugas Kamu") ditambahkan ke CSS, dipakai 5x.
  - Komponen baru `.seriesnav` (link navigasi "Pertemuan sebelumnya/berikutnya" di atas & bawah halaman) untuk menghubungkan antar pertemuan di rangkaian ini.
  - Bug ditemukan & diperbaiki: satu `<li>` di Tugas Kamu Bagian 03 tidak tertutup `</li>` — ketahuan dari validasi count `li` terbuka vs tertutup, sudah diperbaiki.
  - Didaftarkan di `index.html` mengisi slot kosong pertama.
  - Validasi akhir: 8 nav = 8 heading, semua tag seimbang (div 17, table 6, tr 33, ul 3, ol 6, li 37, pre 2, h3 3, h4 1), 2 codecard, 5 task-box.
- [x] Pertemuan 11 — Membangun Backend Sendiri.
  - 8 section: Tentang Pertemuan Ini (+ Tugas Kamu setup folder, pilih Go/Node), Peta Arsitektur Backend (+ Tugas Kamu bikin berkas error/domain), Autentikasi & Keamanan (pseudocode register/login bahasa-agnostik + Tugas Kamu), Service Layer Bisnis & Otorisasi (pseudocode authorizeOwner 2-level + Tugas Kamu), Repository & Anti SQL Injection (pola query aman vs berbahaya + Tugas Kamu uji SQL injection), Upload Foto & Migration (+ Tugas Kamu), Menjalankan & Menguji Backend (6 langkah verifikasi end-to-end), Rangkuman & Checklist.
  - Beda dengan Pertemuan 10: karena ini tahap implementasi dan kode aslinya sudah lengkap di Pertemuan 9 (Go) & 9a (Node.js), isi di sini memakai **pseudocode bahasa-agnostik** untuk pola inti (register/login, authorizeOwner, query aman) + link langsung ke section spesifik Pertemuan 9/9a untuk kode asli lengkap tiap stack — menghindari duplikasi besar sambil tetap memberi mahasiswa rujukan konkret.
  - Mahasiswa diarahkan pilih stack sendiri (Go atau Node.js) dari Pertemuan 9/9a sesuai yang mereka kuasai.
  - Validasi akhir: 8 nav = 8 heading, semua tag seimbang (div 20, table 1, tr 6, ul 6, ol 5, li 44, pre 4, h3 1), 4 codecard (3 pseudocode + 1 peta arsitektur), 6 task-box.
- [x] Pertemuan 12 — Fundamental Flutter: Layout, Konek API & Halaman Awal.
  - 7 section: Tentang Pertemuan Ini (+ Tugas Kamu setup), Peta Halaman & Dependency (struktur screens generik dgn placeholder `<entitas>` + Tugas Kamu), Fundamental Layout Widget Dasar (Column/Row/ListView.builder/Scaffold+StatefulWidget, diringkas dari Pertemuan 9 Bagian 13 + Tugas Kamu DartPad), Fundamental Konek ke API (Future/async-await/jsonDecode + pola fungsi API generik + FutureBuilder generik + Tugas Kamu bikin `api_service.dart` sendiri), Membangun Splash/Login/Register (kode `_prosesLogin` asli dari umkm-app sbg acuan + Tugas Kamu bangun versi sendiri), Menjalankan & Menguji Alur Auth (5 skenario uji), Rangkuman & Checklist.
  - Beda dengan Pertemuan 10/11: kode contoh di sini sengaja digenerikkan (nama fungsi `getDaftarItem`, `Item`, placeholder `<entitas>`) ketimbang selalu UMKM, supaya terasa jadi template yang langsung bisa diisi nama entitas masing-masing mahasiswa — sambil tetap menyertakan 1 kode ASLI dari `login_screen.dart` (`_prosesLogin`) sebagai acuan konkret yang sudah terbukti jalan.
  - Validasi akhir: 7 nav = 7 heading, semua tag seimbang (div 26, table 2, tr 9, ul 3, ol 3, li 25, pre 7), 7 codecard, 5 task-box, 1 try-box.
- [x] Pertemuan 13 — Halaman CRUD Lengkap & ApiService.
  - 8 section: Tentang Pertemuan Ini, ApiService & TokenStorage (kode asli `simpanUmkm`/`_authHeaders`/`token_storage.dart` penuh dari umkm-app + Tugas Kamu lengkapi ApiService sendiri), Halaman Daftar & Detail (IndexedStack/FutureBuilder/RefreshIndicator + Tugas Kamu), CRUD Lengkap & Trik ValueKey (kode asli `myumkm_screen.dart` potongan kunci + penjelasan alur remount + Tugas Kamu wajib buktikan sendiri pakai debugPrint), Form Tambah/Edit dual-mode (+ Tugas Kamu), Profil & Ubah Password (+ Tugas Kamu), Menjalankan & Menguji CRUD Lengkap (7 langkah), Rangkuman & Checklist.
  - Ini pertemuan paling padat Tugas Kamu (5 kotak) karena cakupannya paling luas (sumber dari 4 section penuh Pertemuan 9: s16-s19) — tapi tanpa tabel sama sekali (semua penjelasan naratif + codecard), beda dari P10/P11/P12 yang masih pakai tabel untuk ringkasan.
  - Validasi akhir: 8 nav = 8 heading, semua tag seimbang (div 16, ul 3, ol 5, li 39, pre 3), 3 codecard, 5 task-box, 0 try-box (verifikasi dipindah jadi bagian dari Tugas Kamu langsung, bukan kotak try terpisah).
- [x] Pertemuan 14 — Trace Request, Testing, Deployment & Rangkuman.
  - 7 section: Tentang Pertemuan Ini, Tahap 4 Testing (+ Tugas Kamu bikin & jalankan QA checklist sendiri), Tahap 5 Deployment & Maintenance (+ Tugas Kamu opsional deploy ke Railway/Render/Fly.io), Trace Request: Telusuri Alur Sendiri (ringkasan pola trace dari Pertemuan 9 Bagian 20-21 + **Tugas Kamu wajib**: tulis 2 trace lengkap pakai kode asli sendiri — kirim-data+file dan login), Pola yang Berulang (6 pola jadi checklist + Tugas Kamu audit kode sendiri), Checklist Kesiapan UAS (gabungan semua deliverable Pertemuan 10-14 jadi satu checklist akhir), Rangkuman Rangkaian (tabel ringkas 5 pertemuan + penutup).
  - Ini penutup rangkaian 5 pertemuan (10-14) — seriesnav di bagian ini mengarah balik ke Pertemuan 9 (bukan ke pertemuan 15, karena rangkaian ini memang berhenti di 14), dan footer menyebutkan "Bagian 5 dari 5".
  - Validasi akhir: 7 nav = 7 heading, semua tag seimbang (div 11, table 4, tr 21, ul 2, ol 2, li 28), 0 codecard, 4 task-box, 0 try-box.

## Rangkaian selesai (2026-11-05)

Seluruh rangkaian Pertemuan 10-14 selesai dibuat dalam satu sesi lanjutan, masing-masing didaftarkan di `index.html` (3 slot kosong tersisa untuk pertemuan berikutnya). Total: 5 file HTML baru, komponen CSS baru `.task` dan `.seriesnav` dipakai konsisten di semua 5 file. Pola umum tiap pertemuan: ringkasan/rujukan ke section spesifik Pertemuan 9 (dan 9a untuk Node.js) + kotak "Tugas Kamu" yang menyuruh penerapan langsung ke proyek UAS masing-masing mahasiswa, bukan sekadar membaca ulang studi kasus UMKM.
