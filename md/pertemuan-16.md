<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 16 · UAS

# UAS: Proyek Akhir

Ini bukan materi baru — ini **muara** dari seluruh perjalanan sejak Pertemuan 8: ide aplikasi pribadi yang didesain (Pertemuan 10), dibangun backend & Flutter-nya sendiri (Pertemuan 11-13), diuji & ditelusuri alurnya (Pertemuan 14), lalu dirilis (Pertemuan 15). Pertemuan ini merangkum apa yang dinilai, apa yang dikumpulkan, dan bagaimana presentasinya.

## 01Tentang UAS Ini

Proyek UAS **bukan proyek baru** — ia adalah kelanjutan langsung dari proyek individu yang dimulai sejak Pertemuan 8 (UTS), lalu dikembangkan penuh lewat rangkaian praktikum Pertemuan 10-14. Tidak ada kejutan topik baru di sini; UAS menilai seberapa lengkap dan konsisten kamu menerapkan kerangka lima tahap (identifikasi masalah → desain → development → testing → deployment) yang sudah dilatih di pertemuan-pertemuan itu.

Kalau belum mengikuti rangkaian Pertemuan 10-14

Mulai dari [Pertemuan 10](pertemuan-10.html) sekarang. Setiap pertemuan di rangkaian itu punya kotak "Tugas Kamu" yang hasilnya langsung menjadi bagian dari proyek UAS ini — bukan latihan terpisah yang harus diulang.

## 02Ruang Lingkup Proyek

Proyek UAS minimal mencakup, sesuai yang sudah dibangun sepanjang Pertemuan 10-14:

- Satu ide aplikasi Android (Flutter) dengan masalah & pengguna yang jelas (dokumen dari Pertemuan 10 Bagian 03).
- Backend sendiri (Go **atau** Node.js — bebas pilih, lihat Pertemuan 9/9a) dengan minimal: register/login (JWT+bcrypt), 1 entitas utama dengan CRUD lengkap, otorisasi kepemilikan, dan database PostgreSQL (Neon).
- Aplikasi Flutter yang mengonsumsi backend sendiri itu: Splash/Login/Register, daftar+detail (publik), CRUD milik sendiri (butuh login), profil+ubah password.
- Minimal 5 halaman fungsional (sesuai minimum dari Pertemuan 8), boleh lebih banyak sesuai kompleksitas ide aplikasimu.
- Upload foto minimal untuk satu jenis data, kalau relevan dengan ide aplikasimu.

Tugas Kamu

Bandingkan daftar di atas dengan aplikasimu sekarang. Kalau ada yang belum terpenuhi, kerjakan dulu sebelum lanjut ke bagian penilaian & pengumpulan — jangan menunggu sampai hari pengumpulan untuk menyadari ada bagian yang terlewat.

## 03Kriteria Penilaian

Penilaian mengikuti bobot kira-kira berikut (detail persis dikonfirmasi dosen pengampu, tabel ini acuan umum):

| Aspek | Yang dinilai | Bobot indikatif |
|----|----|----|
| Desain | Kejelasan masalah & kebutuhan, ERD masuk akal, kontrak API konsisten dengan implementasi (Pertemuan 10). | 15% |
| Implementasi backend | Arsitektur berlapis, auth aman (bcrypt+JWT), otorisasi kepemilikan benar, query aman dari SQL injection (Pertemuan 11). | 25% |
| Implementasi Flutter | Alur auth jalan, CRUD lengkap, state/refresh ditangani benar, kode rapi mengikuti pola yang diajarkan (Pertemuan 12-13). | 25% |
| Testing & pemahaman alur | QA checklist dijalankan, dua dokumen trace request lengkap & akurat (Pertemuan 14). | 15% |
| Rilis | Aplikasi berhasil diunggah minimal ke Internal testing Play Console (Pertemuan 15). | 10% |
| Presentasi/demo | Bisa menjelaskan alur kode sendiri secara langsung, menjawab pertanyaan "kenapa" (bukan cuma "apa"), lihat Bagian 05. | 10% |

Yang paling sering jadi pembeda nilai bukan "fitur sebanyak apa"

Aplikasi dengan fitur sedikit tapi dipahami & dijelaskan dengan baik (bisa jawab "kenapa ditulis begini" untuk kode sendiri) biasanya dinilai lebih baik daripada aplikasi dengan banyak fitur tapi mahasiswanya tidak bisa menjelaskan alurnya sendiri saat ditanya. Dokumen trace request di Pertemuan 14 Bagian 04 bukan formalitas — itu bukti pemahaman yang akan sangat membantu saat presentasi.

## 04Yang Dikumpulkan

- Link repository kode (backend + Flutter), riwayat commit mencerminkan proses bertahap (bukan satu commit raksasa di akhir).
- Berkas `schema.sql` dan dokumen desain lengkap dari Pertemuan 10.
- Dua dokumen trace request dari Pertemuan 14 Bagian 04 (kirim-data+file, dan login) memakai kode asli proyekmu sendiri.
- Link aplikasi di Internal testing Google Play Console (atau APK rilis kalau karena suatu hal belum sempat diunggah — konfirmasi ke dosen kalau ini terjadi).
- Laporan singkat (boleh gabung dengan dokumen desain): ringkasan masalah, fitur yang diimplementasikan, kendala & solusi selama pengerjaan.

Tugas Kamu

Kumpulkan kelima item di atas dalam satu dokumen indeks (boleh Google Docs/Notion) berisi link ke masing-masing — ini yang memudahkan dosen/asisten menilai tanpa harus mencari-cari di banyak tempat terpisah.

## 05Format Presentasi & Demo

Demo dilakukan langsung dari aplikasi yang berjalan (device/emulator atau hasil install dari Play Store), bukan dari slide semata. Urutan yang disarankan:

1.  **Masalah & solusi** (1-2 menit) — jelaskan masalah nyata yang diselesaikan dan untuk siapa, merujuk dokumen Pertemuan 10 Bagian 03.
2.  **Demo alur utama** (3-5 menit) — register/login, lihat daftar publik, CRUD data milik sendiri termasuk upload foto, logout. Jalankan langsung, jangan direkam sebelumnya kalau memungkinkan (lebih meyakinkan).
3.  **Jelaskan satu alur kode** (3-5 menit) — pilih satu trace request dari Pertemuan 14 Bagian 04, tunjukkan kodenya langsung sambil menjelaskan urutan Flutter → backend → database → balik lagi.
4.  **Tanya-jawab** — siap ditanya "kenapa" untuk keputusan desain tertentu (kenapa pakai arsitektur ini, kenapa otorisasi di layer ini, dst) — bukan cuma "bagaimana cara pakai aplikasinya".

Latihan dulu sebelum hari-H

Coba jalankan seluruh demo dari awal sampai akhir minimal sekali sehari sebelumnya, di jaringan dan perangkat yang sama persis dengan yang akan dipakai saat presentasi — banyak demo gagal bukan karena kodenya salah, tapi karena backend lupa dinyalakan, Neon project "tertidur" karena idle lama, atau `baseUrl` masih menunjuk ke IP lama.

## 06Kesalahan yang Sering Menurunkan Nilai

| Kesalahan | Kenapa bermasalah |
|----|----|
| Password disimpan/dibandingkan sebagai teks biasa | Melanggar prinsip keamanan paling dasar yang sudah diajarkan sejak Pertemuan 11 — biasanya langsung jadi catatan besar saat penilaian. |
| Semua orang bisa edit/hapus data orang lain | Berarti otorisasi kepemilikan (Pertemuan 11 Bagian 04) tidak diimplementasikan — fitur CRUD dianggap tidak lengkap meski secara teknis "berfungsi". |
| Tidak bisa menjelaskan kode sendiri saat demo | Indikasi kuat kode disalin tanpa dipahami — lihat peringatan di Bagian 03. |
| `baseUrl` masih `localhost` saat demo di device lain | Menunjukkan belum paham konsep jaringan dasar yang sudah dibahas sejak Pertemuan 9 Bagian 19 — demo gagal total karena ini sering terjadi. |
| Commit history cuma 1-2 commit raksasa | Tidak menunjukkan proses bertahap sesuai kerangka lima tahap yang diajarkan — sulit dinilai prosesnya, hanya hasil akhirnya. |

## 07Checklist Akhir

- Semua item di Bagian 02 (ruang lingkup) terpenuhi.
- Semua item di Bagian 04 (yang dikumpulkan) sudah disiapkan dan di-link dalam satu dokumen indeks.
- Demo sudah dilatih minimal sekali penuh dari awal sampai akhir, di perangkat & jaringan yang sama dengan hari-H.
- Backend ter-deploy atau setidaknya bisa diakses dari device demo (bukan cuma `localhost` laptop sendiri).
- Siap menjelaskan minimal satu trace request secara langsung dari kode sungguhan, tanpa membaca catatan.

## 08Penutup Mata Kuliah

Dari instalasi Flutter pertama kali (Pertemuan 1) sampai aplikasi yang punya backend sendiri, database sendiri, dan rilis sungguhan di Google Play (Pertemuan 15) — satu mata kuliah ini menempuh siklus penuh pengembangan aplikasi, bukan cuma kumpulan topik lepas. Kerangka lima tahap (identifikasi masalah, desain, development, testing, deployment) yang dipakai berulang-ulang sejak Pertemuan 9 bukan sekadar materi untuk mata kuliah ini — itu kerangka yang sama yang dipakai di proyek perangkat lunak sungguhan, skala apa pun.

Apa pun hasil proyek UAS-mu, kemampuan paling berharga yang dibawa pulang bukan aplikasi UMKM atau aplikasi UAS itu sendiri — melainkan kemampuan mengulang seluruh proses ini dari nol, untuk ide aplikasi apa pun yang muncul di masa depan.

Selamat menyelesaikan proyek UAS. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
