<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 1 · Instalasi

# Instalasi Flutter di Windows, macOS, dan Linux

Materi ini membahas langkah-langkah pemasangan Flutter SDK pada tiga sistem operasi yang umum digunakan, serta cara memverifikasi bahwa instalasi telah berhasil.

## 01Apa Itu Flutter SDK

Flutter SDK adalah kumpulan alat (tools) dan pustaka (library) yang digunakan untuk membangun aplikasi menggunakan bahasa pemrograman Dart. Sebelum menulis satu baris kode pun, SDK ini perlu terpasang terlebih dahulu di komputer, beserta beberapa perangkat pendukung seperti Android Studio dan Git.

Proses instalasi berbeda pada setiap sistem operasi, namun tujuan akhirnya sama: memastikan perintah `flutter` dapat dijalankan dari terminal dan seluruh pemeriksaan pada `flutter doctor` berstatus baik.

## 02Kebutuhan Sebelum Memulai

- Koneksi internet yang stabil, karena proses unduh SDK dan dependensinya berukuran cukup besar.
- Ruang penyimpanan kosong minimal 2,5 GB (di luar ruang untuk Android Studio dan emulator).
- **Git** sudah terpasang, karena Flutter menggunakannya untuk memperbarui SDK.
- **Android Studio**, digunakan untuk menyediakan Android SDK, emulator, serta sebagai editor (opsional, dapat diganti VS Code).

## 03Instalasi di Windows

1.  Unduh Flutter SDK dalam format `.zip` melalui laman resmi <a href="https://docs.flutter.dev/get-started/install/windows" target="_blank" rel="noopener">docs.flutter.dev</a>.
2.  Ekstrak berkas tersebut ke lokasi tetap, misalnya `C:\src\flutter`. Hindari folder yang memerlukan hak akses administrator seperti `C:\Program Files`.
3.  Tambahkan `C:\src\flutter\bin` ke environment variable **Path** melalui menu Edit Environment Variables.
4.  Pasang Android Studio, kemudian buka menu *SDK Manager* untuk memastikan Android SDK dan Android SDK Command-line Tools sudah terpasang.
5.  Buka Command Prompt baru, lalu jalankan `flutter doctor` untuk memeriksa hasil instalasi.

cmd

    flutter doctor

## 04Instalasi di macOS

1.  Unduh Flutter SDK melalui <a href="https://docs.flutter.dev/get-started/install/macos" target="_blank" rel="noopener">docs.flutter.dev</a>, lalu ekstrak ke folder tetap, misalnya `~/development`.
2.  Tambahkan Flutter ke PATH dengan menambahkan baris berikut pada `~/.zshrc`:

~/.zshrc

    export PATH="$PATH:$HOME/development/flutter/bin"

3.  Jalankan `source ~/.zshrc` agar perubahan langsung berlaku pada terminal yang sedang aktif.
4.  Pasang **Xcode** melalui App Store apabila berencana membangun aplikasi untuk iOS, kemudian jalankan `sudo xcodebuild -runFirstLaunch`.
5.  Pasang Android Studio untuk kebutuhan pengembangan Android.
6.  Jalankan `flutter doctor` untuk memverifikasi instalasi.

terminal

    flutter doctor

## 05Instalasi di Linux

1.  Unduh berkas `.tar.xz` melalui <a href="https://docs.flutter.dev/get-started/install/linux" target="_blank" rel="noopener">docs.flutter.dev</a>, lalu ekstrak ke folder tetap seperti `~/development`.
2.  Tambahkan Flutter ke PATH dengan menambahkan baris berikut pada `~/.bashrc`:

~/.bashrc

    export PATH="$PATH:$HOME/development/flutter/bin"

3.  Jalankan `source ~/.bashrc`.
4.  Pasang dependensi tambahan yang dibutuhkan untuk pengembangan aplikasi Linux/Android:

terminal (Ubuntu/Debian)

    sudo apt-get update
    sudo apt-get install -y curl git unzip xz-utils zip libglu1-mesa \
      clang cmake ninja-build pkg-config libgtk-3-dev

5.  Pasang Android Studio (diunduh dari situs resminya, bukan dari package manager bawaan distro), lalu buka SDK Manager untuk memasang Android SDK.
6.  Jalankan `flutter doctor` untuk memverifikasi instalasi.

terminal

    flutter doctor

## 06Membaca Hasil flutter doctor

Perintah `flutter doctor` memeriksa seluruh komponen yang dibutuhkan Flutter dan menampilkan status masing-masing dengan tanda berikut:

- **\[✓\]** — komponen sudah terpasang dan berfungsi dengan baik.
- **\[!\]** — komponen terpasang namun ada catatan yang sebaiknya ditindaklanjuti (tidak wajib segera diperbaiki).
- **\[✗\]** — komponen belum terpasang atau bermasalah, dan wajib diperbaiki sebelum melanjutkan.

Tidak perlu semua baris hijau

Untuk kebutuhan pengembangan Android saja, tanda seru pada baris terkait iOS/Xcode (khusus Windows dan Linux) dapat diabaikan. Fokuskan perhatian pada baris Flutter, Android toolchain, dan editor yang digunakan.

## 07Masalah yang Sering Terjadi

- **Perintah flutter tidak dikenali** — biasanya karena PATH belum ditambahkan dengan benar, atau terminal belum dibuka ulang setelah perubahan PATH dilakukan.
- **Android licenses belum diterima** — jalankan `flutter doctor --android-licenses` lalu ketik `y` pada setiap pertanyaan yang muncul.
- **cmdline-tools component is missing** — buka Android Studio, masuk ke SDK Manager, lalu pasang komponen *Android SDK Command-line Tools* secara manual.

Setelah `flutter doctor` menunjukkan status baik pada bagian Flutter dan Android toolchain, instalasi sudah dapat dilanjutkan ke pertemuan berikutnya. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
