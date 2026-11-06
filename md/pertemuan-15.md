<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 15 · Rilis Aplikasi

# Upload Aplikasi ke Google Play Store

Aplikasi yang hanya bisa dijalankan lewat `flutter run` dari laptop pembuatnya belum benar-benar "rilis" — Tahap 5 (Deployment) dari kerangka yang dipakai sejak Pertemuan 10 baru selesai kalau orang lain bisa menginstal dan memakainya sendiri. Pertemuan ini menuntaskan itu: dari keystore, build `.aab`, sampai aplikasi tayang di track testing Google Play Console, memakai aplikasi UAS kamu sendiri dari rangkaian Pertemuan 10-14.

## 01Tentang Pertemuan Ini

Materi ini murni tentang **distribusi** — tidak ada kode fitur baru yang ditulis. Prasyarat: aplikasi Flutter-mu (dari Pertemuan 8 & dikembangkan penuh di Pertemuan 10-14) sudah bisa dijalankan tanpa error dalam mode *debug*, dan backend-nya (kalau ada) sudah berjalan di tempat yang bisa diakses dari internet — bukan lagi `localhost` (lihat Pertemuan 14 Bagian 03 soal opsi hosting gratis).

Akun Google Play Developer berbayar sekali

Mendaftar sebagai developer di Google Play Console mewajibkan biaya pendaftaran **satu kali seumur hidup** (bukan langganan), dibayar lewat kartu yang mendukung pembayaran internasional. Kalau kelas/kampus punya akun developer bersama, tanyakan ke dosen/asisten dulu sebelum mendaftar akun baru sendiri-sendiri — banyak kampus menyediakan ini supaya mahasiswa tidak perlu bayar pribadi.

## 02Persiapan Sebelum Upload

Siapkan dulu aset & keputusan berikut — mengerjakannya belakangan di tengah proses upload biasanya bikin bolak-balik:

| Yang disiapkan | Keterangan |
|----|----|
| Nama aplikasi | Tampil di Play Store & home screen perangkat — beda dari nama proyek Flutter. |
| Package name (`applicationId`) | Format `com.<namamu><npm>.<nama_aplikasi>` sudah ditentukan sejak Pertemuan 8 — **tidak bisa diubah lagi** setelah pertama kali diupload ke Play Store, jadi pastikan sudah benar sebelum lanjut. |
| Ikon aplikasi | Minimal 512×512px, format PNG, dipakai sebagai ikon di listing Play Store (beda file dari ikon yang tampil di home screen, walau biasa dari sumber yang sama). |
| Screenshot | Minimal 2 screenshot per jenis perangkat yang didukung (ponsel wajib) — ambil langsung dari emulator/device sungguhan, bukan mockup palsu. |
| Deskripsi singkat & lengkap | Deskripsi singkat maks. 80 karakter, deskripsi lengkap maks. 4000 karakter — jelaskan apa yang dilakukan aplikasi, bukan daftar fitur teknis. |
| Privacy policy (URL) | **Wajib** kalau aplikasi meminta data pengguna (login, lokasi, kamera, dst) — bisa pakai generator gratis atau halaman statis sederhana yang kamu hosting sendiri (GitHub Pages cukup). |

Tugas Kamu

Siapkan keenam item di tabel di atas untuk aplikasi UAS-mu. Simpan di satu folder — semuanya akan diminta berurutan saat mengisi Play Console nanti.

## 03App Signing & Keystore

Setiap aplikasi Android yang dirilis harus ditandatangani secara digital dengan sebuah *keystore* — ini yang membuktikan ke Google Play bahwa update aplikasi di masa depan benar-benar datang dari pengembang yang sama, bukan orang lain yang mengaku-aku.

terminal — membuat keystore

    keytool -genkey -v -keystore ~/upload-keystore.jks \
      -keyalg RSA -keysize 2048 -validity 10000 \
      -alias upload

Perintah ini meminta beberapa pertanyaan (password, nama, organisasi) — **catat password-nya di tempat aman**, karena kalau keystore ini hilang, kamu tidak akan bisa merilis update untuk aplikasi yang sama lagi selamanya (harus rilis sebagai aplikasi baru dengan package name berbeda).

android/key.properties — buat berkas baru

    storePassword=<password keystore>
    keyPassword=<password key>
    keyAlias=upload
    storeFile=/lokasi/lengkap/ke/upload-keystore.jks

android/app/build.gradle — tambahkan signingConfig

    def keystoreProperties = new Properties()
    def keystorePropertiesFile = rootProject.file('key.properties')
    if (keystorePropertiesFile.exists()) {
        keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
    }

    android {
        // ...
        signingConfigs {
            release {
                keyAlias keystoreProperties['keyAlias']
                keyPassword keystoreProperties['keyPassword']
                storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
                storePassword keystoreProperties['storePassword']
            }
        }
        buildTypes {
            release {
                signingConfig signingConfigs.release
            }
        }
    }

key.properties dan .jks TIDAK PERNAH masuk Git

Tambahkan `key.properties` dan `*.jks` ke `.gitignore` sebelum commit apa pun — berkas ini berisi kredensial yang kalau bocor ke repo publik (atau bahkan privat yang dibagikan), siapa pun yang memilikinya bisa merilis update palsu atas nama aplikasimu.

Tugas Kamu

Buat keystore untuk aplikasi UAS-mu, simpan passwordnya di password manager (bukan di catatan biasa yang gampang hilang), lalu konfigurasikan `key.properties` dan `build.gradle` seperti di atas. Pastikan `.gitignore` sudah menolak kedua berkas sensitif ini.

## 04Build App Bundle (.aab)

Google Play mewajibkan format **Android App Bundle (`.aab`)**, bukan `.apk` biasa, untuk aplikasi baru — Google Play yang nanti meracik APK optimal per jenis perangkat dari satu `.aab` ini, sehingga pengguna mengunduh ukuran yang lebih kecil daripada APK universal.

terminal

    flutter build appbundle --release

Hasilnya ada di `build/app/outputs/bundle/release/app-release.aab` — berkas inilah yang diunggah ke Play Console, bukan APK. Kalau cuma butuh APK untuk dibagikan langsung (misalnya untuk demo manual tanpa lewat Play Store), tetap bisa pakai `flutter build apk --release` seperti yang sudah dipakai sejak Pertemuan 14.

Selalu uji build release, bukan cuma debug

Build *release* mengaktifkan optimisasi (minifikasi kode, dsb) yang tidak aktif di mode *debug* — kadang ada bug yang cuma muncul di build release. Install hasil `flutter build apk --release` ke device sungguhan dan coba alur penuh (login, CRUD, upload foto) sebelum mengunggah `.aab` ke Play Console.

Tugas Kamu

Jalankan `flutter build appbundle --release` untuk aplikasimu. Kalau gagal karena signing, kembali ke Bagian 03 dan cek lagi konfigurasinya. Install dulu versi `--release` APK ke device sungguhan dan uji alur penuh sebelum lanjut ke Bagian 05.

## 05Setup Google Play Console

1.  Buka <a href="https://play.google.com/console" target="_blank" rel="noopener">play.google.com/console</a>, daftar sebagai developer (biaya satu kali, lihat peringatan Bagian 01).
2.  Klik "Create app" — isi nama aplikasi, bahasa default, pilih "App" (bukan "Game"), tentukan gratis/berbayar.
3.  Google Play akan menampilkan daftar langkah yang harus diselesaikan sebelum bisa rilis — biasanya mencakup: App content (rating, data safety, target audience), Store listing, dan Main store listing.

Review pertama kali bisa lebih lama

Aplikasi yang pertama kali diunggah oleh akun developer baru sering butuh waktu review lebih lama (bisa beberapa hari) dibanding developer yang sudah established. Jangan menunggu sampai hari terakhir deadline untuk mulai proses ini.

## 06Store Listing

Ini halaman yang dilihat calon pengguna di Play Store sebelum menginstal — isi dengan aset yang sudah disiapkan di Bagian 02:

| Bagian | Ketentuan umum |
|----|----|
| Ikon aplikasi | 512×512px, PNG, tanpa transparansi di tepi yang dianggap penting. |
| Feature graphic | 1024×500px — banner yang tampil di bagian atas listing. |
| Screenshot ponsel | Minimal 2, rasio sesuai perangkat yang discreenshot — ambil dari alur penting aplikasimu (home, detail, form), bukan layar kosong. |
| Deskripsi singkat | Maks. 80 karakter — satu kalimat inti tentang apa aplikasimu. |
| Deskripsi lengkap | Maks. 4000 karakter — jelaskan masalah yang diselesaikan (ingat Pertemuan 10 Bagian 03) dan fitur utamanya. |
| Kategori | Pilih kategori yang paling relevan dengan fungsi aplikasimu (mis. "Business", "Shopping", "Productivity"). |

Tugas Kamu

Isi seluruh Store Listing di Play Console memakai aset dari Bagian 02. Tulis deskripsi singkat & lengkap berdasarkan dokumen kebutuhan yang sudah kamu tulis di Pertemuan 10 Bagian 03 — masalah dan kebutuhan fungsional yang kamu rumuskan di sana adalah bahan baku terbaik untuk deskripsi ini.

## 07Content Rating & Data Safety

Dua formulir wajib diisi sebelum aplikasi bisa dipublikasikan, keduanya berupa kuesioner di Play Console:

- **Content rating** — kuesioner tentang konten aplikasi (kekerasan, konten dewasa, perjudian, dst). Untuk aplikasi UAS kebanyakan kategori "Everyone" sudah cukup, asal dijawab jujur sesuai isi aplikasi sungguhan.
- **Data safety** — deklarasi data apa saja yang dikumpulkan aplikasimu (email, nama, lokasi, dst) dan untuk apa. Ini harus **konsisten** dengan privacy policy yang kamu siapkan di Bagian 02 — isian yang tidak sesuai (mis. bilang tidak mengumpulkan data padahal ada fitur login) bisa membuat aplikasi ditolak.

Jangan asal klik "tidak mengumpulkan data apa pun"

Aplikasi dengan fitur login/register sudah pasti mengumpulkan data (minimal email). Mendeklarasikan secara tidak akurat bisa melanggar kebijakan Google Play, bahkan untuk aplikasi tugas kuliah yang tidak dipublikasikan secara luas.

## 08Rilis ke Internal Testing

Untuk tugas kuliah, **tidak perlu langsung rilis ke Production** (publik luas) — cukup track **Internal testing**, yang bisa diakses oleh daftar email tester yang kamu tentukan sendiri (termasuk dosen/asisten), dan proses reviewnya jauh lebih cepat daripada Production.

1.  Di Play Console, buka menu **Testing → Internal testing**, klik "Create new release".
2.  Upload berkas `.aab` hasil Bagian 04.
3.  Isi release notes singkat (boleh "Rilis awal untuk UAS Pemrograman IV").
4.  Tambahkan email tester (dosen/asisten/diri sendiri) di tab "Testers".
5.  Simpan & review, lalu "Start rollout to Internal testing".
6.  Bagikan link opt-in testing ke daftar tester — mereka harus membuka link itu dan "Become a tester" sebelum bisa menginstal lewat Play Store.

Checkpoint

Internal testing biasanya aktif dalam hitungan menit (jauh lebih cepat dari Production). Kalau tester bisa menginstal & membuka aplikasimu lewat link Play Store (bukan APK manual), berarti seluruh rantai signing & upload sudah benar.

Tugas Kamu

Rilis aplikasimu ke Internal testing track, tambahkan dosen/asisten sebagai tester, lalu uji instalasi lewat link Play Store (bukan APK manual) di device yang berbeda dari device development-mu.

## 09Troubleshooting Umum

| Masalah | Penyebab umum | Solusi |
|----|----|----|
| Upload `.aab` ditolak: "You uploaded an APK/App Bundle with a debuggable Application" | Build masih pakai signing config debug, bukan release. | Cek lagi `signingConfigs.release` di `build.gradle` sudah benar dan `buildTypes.release` memakainya. |
| "Your app bundle must support 64-bit" | Dependency native lama yang belum mendukung arsitektur 64-bit. | Update semua dependency ke versi terbaru, pastikan `flutter build appbundle` (bukan konfigurasi custom) yang dipakai. |
| Versi tidak bisa diupload: "Version code X has already been used" | `versionCode` di `pubspec.yaml` (bagian `version: x.y.z+N`, angka setelah `+`) sama dengan rilis sebelumnya. | Naikkan angka setelah `+` di `pubspec.yaml` setiap kali build ulang untuk diupload. |
| Keystore password lupa/hilang | Tidak disimpan di tempat aman saat dibuat. | Tidak ada cara memulihkan keystore yang hilang — kalau ini aplikasi yang belum pernah dirilis, buat keystore baru. Kalau sudah pernah dirilis dengan keystore lama, harus rilis sebagai aplikasi baru (package name baru). |
| Data safety form dianggap tidak lengkap | Jawaban kuesioner tidak konsisten dengan fitur aplikasi sungguhan. | Tinjau ulang semua fitur yang mengumpulkan data (login, upload foto, lokasi) dan cocokkan dengan deklarasi di form. |

## 10Checklist & Rangkuman

- Keystore dibuat, password tersimpan aman, `key.properties` & `.jks` masuk `.gitignore`.
- Build `--release` sudah diuji penuh di device sungguhan sebelum diupload.
- `.aab` berhasil dibuat dan diupload ke Play Console tanpa error signing.
- Store listing lengkap: ikon, screenshot, deskripsi, kategori.
- Content rating & Data safety terisi jujur dan konsisten dengan privacy policy.
- Rilis ke Internal testing berhasil, minimal 1 tester (dosen/asisten) bisa menginstal lewat Play Store.

Dengan ini, aplikasi UAS-mu sudah melewati seluruh siklus pengembangan penuh: identifikasi masalah & desain (Pertemuan 10), backend (Pertemuan 11), Flutter dari fundamental sampai CRUD lengkap (Pertemuan 12-13), testing & trace request (Pertemuan 14), dan sekarang distribusi nyata (pertemuan ini) — persis siklus lima tahap yang diperkenalkan sejak Pertemuan 9/10, dari awal sampai benar-benar di tangan pengguna.

Materi ini melengkapi Tahap 5 (Deployment) dari kerangka lima tahap pengembangan aplikasi — distribusi nyata ke Google Play, bukan lagi sekadar `flutter run` di laptop sendiri. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
