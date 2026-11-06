<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 2 · Run to Device

# Menjalankan Aplikasi ke Perangkat Nyata (Real Device)

Materi ini membahas persiapan perangkat Android dan iOS agar dapat digunakan untuk menjalankan dan menguji aplikasi Flutter secara langsung, tanpa emulator.

## 01Mengapa Perlu Diuji pada Perangkat Nyata

Emulator dan simulator memang praktis untuk pengembangan sehari-hari, namun performa, sensor (kamera, GPS, akselerometer), dan pengalaman sentuh pada perangkat sungguhan seringkali berbeda. Sebelum aplikasi dikumpulkan sebagai tugas, sebaiknya diuji langsung pada perangkat fisik minimal satu kali.

## 02Menyiapkan Perangkat Android

1.  Buka **Pengaturan → Tentang Ponsel**, lalu ketuk **Nomor Build** sebanyak 7 kali hingga muncul notifikasi "Anda sekarang menjadi pengembang".
2.  Masuk ke **Pengaturan → Opsi Pengembang**, lalu aktifkan **USB Debugging**.
3.  Hubungkan perangkat ke komputer menggunakan kabel USB.
4.  Pada layar ponsel akan muncul dialog "Izinkan debugging USB?" — pilih **Izinkan**.
5.  Periksa apakah perangkat sudah terdeteksi oleh Flutter:

terminal

    flutter devices

Apabila perangkat muncul dalam daftar, jalankan aplikasi langsung ke perangkat tersebut:

terminal

    flutter run

Lebih dari satu perangkat terdeteksi?

Gunakan `flutter run -d <device_id>`, di mana `device_id` diambil dari kolom paling kiri hasil `flutter devices`.

## 03Menyiapkan Perangkat iOS (Khusus Pengguna macOS)

1.  Hubungkan iPhone ke Mac menggunakan kabel, kemudian pilih **Trust** pada dialog yang muncul di kedua perangkat.
2.  Buka proyek Flutter melalui Xcode dengan perintah `open ios/Runner.xcworkspace`, lalu pada bagian **Signing & Capabilities**, pilih **Team** menggunakan Apple ID pribadi (akun gratis sudah cukup untuk keperluan pengujian).
3.  Jalankan aplikasi pertama kali melalui tombol Run pada Xcode agar proses code signing selesai dengan sempurna.
4.  Pada iPhone, buka **Pengaturan → Umum → VPN & Manajemen Perangkat**, lalu percayai (trust) profil developer yang muncul.
5.  Setelah langkah tersebut berhasil, aplikasi selanjutnya dapat dijalankan langsung dari terminal:

terminal

    flutter run

Khusus pengguna Windows/Linux

Pengembangan dan pengujian untuk perangkat iOS memerlukan macOS dan Xcode, sehingga langkah ini tidak dapat dilakukan pada sistem operasi lain.

## 04Perintah-Perintah yang Sering Digunakan

| Perintah | Fungsi |
|----|----|
| `flutter devices` | Menampilkan daftar perangkat/emulator yang terdeteksi. |
| `flutter run` | Membangun dan menjalankan aplikasi pada perangkat yang terhubung. |
| `flutter run -d <id>` | Menjalankan aplikasi pada perangkat tertentu apabila lebih dari satu terdeteksi. |
| Tombol `r` saat flutter run berjalan | Hot reload — memuat ulang perubahan kode tanpa mengulang seluruh state aplikasi. |
| Tombol `R` saat flutter run berjalan | Hot restart — memulai ulang aplikasi dari awal beserta seluruh state-nya. |
| Tombol `q` saat flutter run berjalan | Menghentikan proses dan keluar dari sesi flutter run. |

## 05Masalah yang Sering Terjadi

- **Perangkat berstatus "unauthorized"** pada Android — lepas kabel, cabut sambungkan kembali, lalu periksa apakah dialog izin USB debugging muncul dan pilih Izinkan.
- **Perangkat tidak muncul sama sekali** — pastikan mode koneksi USB pada ponsel diatur ke *Transfer Berkas (MTP)*, bukan *Hanya Mengisi Daya*.
- **Untrusted Developer pada iOS** — ulangi langkah trust profil developer melalui menu VPN & Manajemen Perangkat, karena langkah ini kadang perlu dilakukan ulang setelah build baru.
- **Proses build pertama terasa lama** — hal ini wajar, karena Gradle (Android) atau Xcode (iOS) sedang mengunduh dan menyiapkan dependensi untuk pertama kalinya.

Setelah aplikasi berhasil berjalan pada perangkat nyata, proses pengembangan selanjutnya dapat dilakukan dengan hot reload agar lebih cepat. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
