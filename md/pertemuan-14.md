<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 14 · Praktikum 5/5 · Proyek Sendiri

# Trace Request, Testing, Deployment & Rangkuman

Bagian penutup rangkaian. Backend dan Flutter aplikasimu sudah jalan penuh sejak Pertemuan 11-13 — pertemuan ini menelusuri salah satu alurnya dari ujung ke ujung (seperti bedah `umkm-app`), menambahkan lapisan testing & rencana deployment, lalu menutup dengan checklist kesiapan sebelum UAS.

← [Pertemuan 13: CRUD Lengkap](pertemuan-13.html)
[Pertemuan 9: Studi Kasus Lengkap](pertemuan-09.html) →

## 01Tentang Pertemuan Ini

Ingat lima tahap dari Pertemuan 10 Bagian 02: identifikasi masalah, desain, **development, testing, deployment**. Tahap *development* sudah kamu jalani penuh di Pertemuan 11-13 (backend dulu, baru Flutter — persis urutan yang disarankan). Pertemuan ini menutup dua tahap terakhir, plus satu latihan penting: **trace request** — menelusuri satu aksi pengguna dari tombol sampai database di aplikasimu sendiri, seperti yang dicontohkan untuk UMKM App di [Pertemuan 9 Bagian 20-21](pertemuan-09.html#s20).

## 02Tahap 4: Testing

Testing bukan cuma "coba jalankan, kalau tidak merah berarti aman". Minimal ada tiga lapis pengecekan yang relevan untuk proyek seukuran UAS-mu:

| Jenis | Contoh |
|----|----|
| Uji endpoint API langsung | Coba tiap endpoint lewat curl/Postman — termasuk kasus gagal: login salah password, create data kedua kalau harusnya dibatasi, akses endpoint butuh-login tanpa token. |
| Uji alur UI end-to-end | Jalankan Flutter sungguhan dari Splash sampai edit data — pastikan token tersimpan & terpakai, foto ter-upload & tampil kembali, logout benar-benar menghapus sesi. |
| Uji kasus tepi (edge case) | Upload file selain JPG/PNG (harus ditolak), koneksi internet mati di tengah submit, data kosong (list kosong tidak boleh membuat UI crash). |

| Tools | Kapan dipakai |
|----|----|
| Postman/Insomnia | Simpan satu koleksi request: register → login (simpan token) → create data pakai token itu → dst. Bisa dipakai ulang tiap kali ada perubahan. |
| `go test ./...` / `flutter test` | Uji fungsi murni (mis. fungsi pagination) atau widget tanpa perlu API/database sungguhan menyala. |
| `go vet` / `flutter analyze` | Dijalankan sebelum commit — menangkap kesalahan sintaks/tipe sebelum sempat dijalankan. |
| Manual QA checklist | Daftar centang tertulis, dijalankan ulang tiap kali ada perubahan besar. |

Prinsip: jangan percaya "kelihatannya jalan"

Kode yang terlihat berfungsi saat jalur normal dicoba belum tentu aman — baru ketahuan bermasalah saat kasus gagal benar-benar terjadi. Selalu uji jalur gagal, bukan cuma jalur sukses.

Tugas Kamu

Buat **manual QA checklist** tertulis untuk aplikasimu (boleh di dokumen yang sama dari Pertemuan 10), minimal 10 baris, mencakup ketiga jenis testing di atas. Jalankan checklist itu sekarang terhadap aplikasimu, catat kalau ada yang gagal lalu perbaiki sebelum lanjut.

## 03Tahap 5: Deployment & Maintenance

Aplikasi yang hanya bisa jalan di laptop pembuatnya belum selesai:

| Bagian | Opsi untuk skala tugas kuliah/UAS |
|----|----|
| Database | <a href="https://neon.tech" target="_blank" rel="noopener">Neon</a> (sudah kamu pakai sejak Pertemuan 10-11) — gratis, serverless. |
| Hosting backend | Railway, Render, atau Fly.io — tier gratis/murah, deploy langsung dari GitHub repo. |
| Penyimpanan file upload | Disk lokal server cukup untuk skala kecil; object storage (Cloudflare R2/S3) kalau butuh persisten walau server di-redeploy. |
| Distribusi Android | APK dibagikan langsung (`flutter build apk`) — cukup untuk keperluan UAS. |
| Pemantauan | Endpoint `/healthz` dicek berkala (manual atau UptimeRobot gratis). |

Deployment bukan akhir

Setelah rilis, aplikasi tetap butuh pemantauan dan perbaikan bug berkelanjutan — siklus lima tahap ini berputar lagi setiap kali ada fitur baru atau masalah baru ditemukan dari pengguna nyata.

Tugas Kamu (opsional, bonus)

Deploy backend-mu ke Railway/Render/Fly.io (gratis), update `baseUrl` di Flutter menunjuk ke URL publik itu, lalu build APK rilis (`flutter build apk --release`). Tidak wajib untuk tugas ini, tapi sangat membantu demo UAS nanti — aplikasi yang bisa diinstal & dicoba langsung dari APK lebih meyakinkan daripada hanya dijalankan dari editor.

## 04Trace Request: Telusuri Alur Sendiri

Ini latihan inti pertemuan ini. Di [Pertemuan 9 Bagian 20-21](pertemuan-09.html#s20), dua alur UMKM App ditelusuri utuh dari tombol Flutter sampai baris masuk Postgres dan balik lagi: **"Membuat UMKM + Foto"** (pola "kirim data + file lalu simpan ke database") dan **"Login"** (pola "verifikasi kredensial lalu keluarkan token"). Hampir semua fitur lain mengikuti salah satu dari dua pola ini.

Contoh potongan trace "Membuat UMKM + Foto" (ringkas, lengkapnya di Pertemuan 9):

1.  Flutter — form tervalidasi lokal, memanggil `ApiService.simpan(...)` dengan `id: null` (mode tambah).
2.  Flutter — `ApiService` membangun `MultipartRequest` (karena ada file foto), menempel token lewat `_authHeaders()`.
3.  Backend — middleware auth memverifikasi token, menempelkan `userId` ke request.
4.  Backend — handler mem-parsing form, menyimpan foto ke disk, memanggil service.
5.  Backend — service mengecek aturan bisnis (mis. kuota/duplikasi), baru memanggil repository.
6.  Backend — repository menjalankan `INSERT ... RETURNING id`.
7.  Balik ke Flutter — response diterima, di-`fromJson`, `Navigator.pop(context, true)` memicu reload di layar pemanggil.

Tugas Kamu — wajib, ini inti pertemuan

Pilih **satu aksi** di aplikasimu yang melibatkan kirim data + file (atau kirim data biasa kalau tidak ada upload foto), lalu tulis trace lengkapnya sendiri, mengikuti format di atas: satu langkah per layer (Flutter form → ApiService → middleware auth backend → handler → service → repository → balik ke Flutter). Sertakan potongan kode ASLI dari proyekmu sendiri di tiap langkah (bukan pseudocode) — persis gaya Pertemuan 9 Bagian 20.

Lakukan hal yang sama untuk alur **login** di aplikasimu (biasanya lebih singkat karena sudah dibangun identik dengan UMKM API/App).

Dokumen trace ini yang akan jadi bahan utama kalau dosen/asisten bertanya "coba jelaskan alur kode login/CRUD kamu dari awal sampai akhir" saat sesi bimbingan atau sidang UAS.

## 05Pola yang Berulang

Enam pola ini muncul berulang di UMKM API/App — cek satu per satu apakah pola yang sama juga muncul di kodemu sendiri:

- **Error mengalir ke atas lewat tipe**, bukan lewat angka status — layer domain/service tidak tahu soal HTTP.
- **Create dan Update digabung satu fungsi** lewat parameter id/entity opsional, konsisten di backend maupun Flutter.
- **Validasi ganda client + server** untuk tipe file foto — server tidak pernah boleh percaya input dari klien begitu saja.
- **Fetch sekali di `initState`**, refresh lewat re-assign `Future` di `setState`.
- **Otorisasi kepemilikan dicek di service layer**, bukan middleware generik.
- **Satu titik tunggal untuk aturan lintas-fitur** (mis. pagination, header auth) — bukan ditulis ulang di banyak tempat.

Tugas Kamu

Centang mana dari 6 pola di atas yang sudah konsisten diterapkan di kodemu. Untuk yang belum, perbaiki sekarang — ini jauh lebih mudah dibenahi sebelum fitur bertambah banyak di UAS, daripada dibiarkan tidak konsisten sampai akhir.

## 06Checklist Kesiapan UAS

Gabungan dari seluruh rangkaian Pertemuan 10-14 — pastikan semua ini sudah ada/terjadi sebelum menganggap fondasi proyek UAS-mu selesai:

- Dokumen desain lengkap: kebutuhan, user flow, ERD+`schema.sql`, kontrak API (Pertemuan 10).
- Backend sendiri jalan: auth (JWT+bcrypt+rate limit), service layer dengan ownership check, repository aman dari SQL injection, upload foto (kalau perlu) (Pertemuan 11).
- Flutter: alur Splash/Login/Register jalan tersambung ke backend sendiri (Pertemuan 12).
- Flutter: CRUD penuh untuk entitas utama, termasuk trik `ValueKey` kalau ada relasi anak, form dual-mode, profil & logout (Pertemuan 13).
- Manual QA checklist tertulis sudah dijalankan, semua poin lolos (Bagian 02).
- Dua dokumen trace request (kirim-data+file, dan login) sudah ditulis dengan kode asli sendiri (Bagian 04).
- Enam pola berulang sudah dicek, yang belum konsisten sudah diperbaiki (Bagian 05).
- *(Opsional/bonus)* Backend sudah di-deploy, APK rilis sudah di-build (Bagian 03).

Selamat — fondasi proyek UAS-mu selesai

Kalau checklist di atas semua tercentang, kamu sudah melalui proses yang sama persis dengan membangun UMKM API + umkm-app dari Pertemuan 4-9, hanya saja untuk ide aplikasimu sendiri. Fitur-fitur tambahan di UAS nanti tinggal mengikuti pola yang sama (Bagian 05) — bukan mulai dari nol lagi.

## 07Rangkuman Rangkaian

Lima pertemuan ini (10-14) menerjemahkan studi kasus [Pertemuan 9](pertemuan-09.html) jadi pengalaman mengerjakan langsung, satu fase kerja per pertemuan:

| Pertemuan | Yang dikerjakan |
|----|----|
| 10 | Identifikasi masalah & desain (UX, database, kontrak API) untuk proyek sendiri. |
| 11 | Backend sendiri: arsitektur, auth, service, repository, upload. |
| 12 | Fundamental Flutter + halaman awal (Splash/Login/Register) tersambung ke backend sendiri. |
| 13 | CRUD lengkap, ApiService, profil — fitur inti aplikasi selesai. |
| 14 (ini) | Trace request, testing, deployment — verifikasi semuanya benar-benar nyambung & siap dipakai. |

Lima tahap pengembangan (identifikasi masalah, desain, development, testing, deployment) bukan birokrasi yang bisa dilewati, melainkan urutan yang membuat keputusan besar diambil **sebelum** menulis kode, bukan ditambal sambil jalan. Pakai kerangka ini lagi untuk setiap fitur baru yang ditambahkan ke proyek UAS — mulai dari menuliskan kebutuhannya dengan jelas, sebelum membuka editor.

← [Pertemuan 13: CRUD Lengkap](pertemuan-13.html)
[Pertemuan 9: Studi Kasus Lengkap](pertemuan-09.html) →

Bagian 5 dari 5 rangkaian praktikum proyek UAS — kembali kapan saja ke [Pertemuan 9](pertemuan-09.html) untuk membaca ulang studi kasus lengkapnya. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
