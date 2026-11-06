<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 1a · Fundamental

# Dasar Fundamental Pemrograman Mobile Android & Identitas Aplikasi

Materi tambahan sebelum masuk ke praktik Flutter: konsep dasar platform Android yang tetap berlaku meski kita membangun aplikasi lewat Flutter, serta pengenalan identitas aplikasi (package name, application ID, dan sejenisnya) yang akan terus dipakai sepanjang semester.

## 01Fundamental Platform Android

Flutter membungkus banyak hal, tetapi aplikasi yang dihasilkan tetap berjalan di atas sistem operasi Android dengan aturan mainnya sendiri. Konsep berikut tetap wajib dipahami:

- **Application lifecycle** — urutan `onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy` pada sisi native. Di Flutter, lifecycle ini dipetakan ke `AppLifecycleState` (`resumed`, `inactive`, `paused`, `detached`) dan menentukan kapan data harus disimpan sebelum aplikasi dipindah ke background.
- **Activity, Fragment, dan View** — unit tampilan di dunia native Android. Flutter membungkus semuanya menjadi satu `FlutterActivity`, namun konsep ini tetap muncul saat berurusan dengan permission atau platform channel.
- **Manifest & permission model** — berkas `AndroidManifest.xml` mendeklarasikan komponen dan izin aplikasi. Sejak Android 6 (API 23), permission sensitif (kamera, lokasi, storage) harus diminta ulang saat runtime, tidak cukup hanya dideklarasikan di manifest.
- **Intent** — mekanisme komunikasi antar-komponen atau antar-aplikasi, misalnya membuka kamera bawaan, fitur share, atau deep link dari notifikasi.
- **Threading model** — Android hanya punya satu *main/UI thread*; pekerjaan berat (network, baca-tulis file) tidak boleh memblokirnya. Di Flutter, ini tercermin lewat `async/await` dan `Isolate`.
- **APK & AAB** — format berkas hasil build. `minSdkVersion`/`targetSdkVersion` menentukan rentang versi Android yang didukung, dan keystore dipakai untuk menandatangani build sebelum dirilis.

## 02Fundamental Flutter & Dart

Di atas fondasi Android tadi, Flutter menambahkan lapisan konsepnya sendiri yang akan dipakai di hampir setiap pertemuan:

- **Widget tree & reactive UI** — seluruh tampilan adalah widget; UI dianggap sebagai fungsi dari state, sehingga `build(context)` dipanggil ulang setiap kali state berubah.
- **StatelessWidget vs StatefulWidget** — menentukan apakah sebuah widget butuh menyimpan dan mengubah datanya sendiri lewat `setState`.
- **const constructor** — menandai widget yang tidak berubah agar tidak dibangun ulang tanpa perlu, berdampak langsung ke performa.
- **Pemrograman asinkron** — `Future`, `async/await`, dan `Stream`, karena hampir seluruh operasi I/O (panggilan API, baca database lokal) bersifat asinkron.
- **State management, navigasi, dan networking** — akan dibahas mendalam pada pertemuan-pertemuan berikutnya (Riverpod, go_router, Dio).

## 03Jebakan Umum Pemula

- **Memakai `BuildContext` setelah jeda `await`** — widget bisa saja sudah di-*dispose* ketika proses asinkron selesai, sehingga wajib memeriksa `context.mounted` sebelum memakainya kembali.
- **State hilang saat rotasi layar atau aplikasi di-kill sistem** — terjadi bila data penting hanya disimpan di memori, tanpa mekanisme persist.
- **Layout kaku (tidak responsif)** — perangkat Android sangat beragam ukurannya; hindari nilai ukuran yang di-hardcode.
- **Lupa meminta permission saat runtime** — deklarasi di manifest saja tidak cukup untuk permission sensitif pada Android modern.

## 04Package Name vs Application ID

Dua istilah ini sering tertukar padahal fungsinya berbeda:

- **Package name** — nama namespace kode Java/Kotlin, tercermin di struktur folder dan `AndroidManifest.xml` (contoh: `com.aseptrisna.umkmapp`).
- **Application ID** — identitas unik aplikasi di level build system (Gradle), didefinisikan lewat `applicationId` di `android/app/build.gradle`. Inilah yang benar-benar membedakan aplikasi di Play Store, dan sengaja dipisahkan dari package name agar satu basis kode bisa punya beberapa varian build (debug, staging, production) dengan ID berbeda.

android/app/build.gradle

    android {
        defaultConfig {
            applicationId "com.aseptrisna.umkmapp"
            minSdkVersion 21
            targetSdkVersion 34
            versionCode 1
            versionName "1.0.0"
        }
    }

Aturan penamaan

Gunakan notasi domain terbalik: `com.<organisasi>.<namaaplikasi>`, hanya huruf kecil, angka, titik, dan underscore. Harus unik secara global di Play Store dan **tidak boleh diubah lagi setelah aplikasi dipublikasikan**, karena menjadi identitas permanen untuk proses update.

## 05Lokasi Identitas di Proyek Flutter

Satu identitas aplikasi sebenarnya tersebar di beberapa berkas berbeda dalam proyek Flutter:

| File | Fungsi |
|----|----|
| `android/app/build.gradle` | `applicationId` — ID unik untuk Play Store dan instalasi di perangkat |
| `android/app/src/main/AndroidManifest.xml` | Deklarasi permission, activity, dan atribut package (versi lama) |
| `android/.../MainActivity.kt` | Lokasi folder harus sesuai dengan package name lama |
| `ios/Runner.xcodeproj` → Bundle Identifier | Setara `applicationId` tetapi untuk iOS, format sama |
| `pubspec.yaml` → `name:` | Nama internal proyek Dart, tidak terkait identitas Play Store |

Mengganti applicationId

Tidak cukup edit satu berkas saja. Jika salah satu lokasi (build.gradle, manifest, path MainActivity) tidak konsisten, build bisa gagal atau aplikasi gagal dipasang sebagai update dari versi sebelumnya. Gunakan tool bantu seperti package `change_app_package_name` agar seluruh berkas diperbarui sekaligus.

## 06Identitas Lain yang Sepaket

- **App name** — `android:label` di manifest (Android) atau `CFBundleDisplayName` di `Info.plist` (iOS); nama yang tampil di launcher, berbeda dari application ID.
- **Version code & version name** — di `pubspec.yaml` ditulis sebagai `1.0.0+1`. Bagian `1.0.0` (versionName) yang dilihat pengguna, bagian `1` (versionCode) adalah angka internal yang wajib naik setiap kali mengunggah update ke Play Store.
- **Signing key / keystore** — bukti kriptografis bahwa sebuah update benar-benar berasal dari pengembang yang sama. Play Store menolak update jika signing key berbeda dari rilis pertama.
- **minSdkVersion / targetSdkVersion** — menentukan versi Android minimum yang didukung dan versi API yang ditarget; Play Store mewajibkan target SDK tertentu yang naik setiap tahun.

## 07Latihan Pemahaman

1.  Jelaskan perbedaan antara `package name` dan `applicationId` dengan kata-kata sendiri, beserta contoh kasus mengapa keduanya sengaja dipisahkan.
2.  Buka proyek Flutter yang sudah pernah dibuat (atau proyek UMKM dari pertemuan sebelumnya), temukan nilai `applicationId` di `android/app/build.gradle`, lalu cocokkan dengan struktur folder paket Kotlin/Java di dalamnya.
3.  Sebutkan tiga permission Android yang membutuhkan permintaan izin saat runtime, dan jelaskan mengapa cukup mendeklarasikannya di manifest saja tidak memadai.

Setelah memahami fundamental ini, lanjutkan ke Pertemuan 1 untuk praktik instalasi Flutter SDK dan verifikasi lingkungan pengembangan. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
