<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 8 · UTS

# UTS: Proyek Flutter Perorangan

Ujian Tengah Semester ini sekaligus menjadi **titik awal proyek UAS** — ide aplikasi yang ditentukan sekarang akan terus dikembangkan sampai akhir semester. Dikerjakan **perorangan**, bukan kelompok, dan dinilai dari seberapa rapi fondasi navigasi dasarnya terpasang.

## 01Tentang UTS Ini

UTS mata kuliah ini tidak berbentuk soal ujian tertulis, melainkan **membangun fondasi proyek Flutter** yang nantinya dikembangkan terus sampai menjadi proyek UAS. Karena itu, keputusan yang diambil sekarang (terutama ide aplikasi dan nama proyek) akan dipakai sampai akhir semester — pilih dengan sungguh-sungguh, bukan asal jadi.

- **Sifat pengerjaan:** perorangan. Tidak ada kerja kelompok untuk UTS maupun UAS.
- **Keaslian ide:** ide aplikasi tidak boleh sama dengan mahasiswa lain di kelas — dicatat di spreadsheet kelas supaya ketahuan kalau ada yang bentrok.
- **Waktu pengerjaan:** aplikasi harus sudah berjalan (minimal lima menu wajib + navigasi) pada tanggal UTS dilaksanakan sesuai jadwal kampus.

Ide ini dipakai sampai UAS

Jangan asal pilih ide aplikasi cuma supaya cepat selesai UTS. Fitur-fitur tambahan di UAS nanti (CRUD, API, database, dsb — menyusul di pertemuan berikutnya) akan dibangun di atas ide yang sama. Pilih ide yang masuk akal untuk dikembangkan minimal 2-3 bulan ke depan.

## 02Langkah 1: Tentukan & Daftarkan Ide Aplikasi

1.  Pikirkan satu ide aplikasi mobile yang ingin dibangun untuk proyek UAS. Boleh terinspirasi dari masalah sehari-hari di sekitarmu (contoh: aplikasi pencatat keuangan pribadi, aplikasi booking lapangan futsal, aplikasi manajemen tugas kuliah, dll) — tapi harus bisa dijelaskan dalam satu-dua kalimat apa masalah yang diselesaikan.
2.  Buka spreadsheet kelas di tautan berikut, lalu **tuliskan nama ide aplikasimu** di baris sesuai namamu:\
    <a href="https://docs.google.com/spreadsheets/d/1fIGSAVGdEZajpY7B-amSITQifzv9QKFJqGKz619jKzo/edit?usp=sharing" target="_blank" rel="noopener">docs.google.com/spreadsheets/.../1fIGSAVGdEZajpY7B-amSITQifzv9QKFJqGKz619jKzo</a>
3.  Sebelum menuliskannya, **scroll daftar yang sudah ada** — pastikan idemu belum dipakai mahasiswa lain. Kalau mirip, ganti sudut pandang atau fiturnya supaya jelas berbeda.

"Tidak boleh sama" artinya apa, persisnya?

Dua mahasiswa boleh sama-sama membuat "aplikasi UMKM", tapi tidak boleh identik sampai ke detail fitur dan target penggunanya. Perbedaan yang jelas — target pengguna, alur utama, atau jenis data yang dikelola — sudah cukup membuat dua ide dianggap berbeda.

## 03Langkah 2: Buat Proyek Flutter Baru

Buat folder kerja baru bernama **"Project UTS dan UAS"** — terpisah dari folder latihan pertemuan 1-7, karena ini proyek yang akan terus dikembangkan sampai akhir semester, bukan sekadar latihan.

terminal

    mkdir "Project UTS dan UAS"
    cd "Project UTS dan UAS"
    flutter create --org com.<namamu> --project-name <nama_aplikasimu> <nama_aplikasimu>
    cd <nama_aplikasimu>

Ganti `<namamu>` dan `<nama_aplikasimu>` sesuai identitas dan ide yang sudah didaftarkan di Langkah 1. Lihat Bagian 04 untuk aturan lengkap format nama paketnya.

## 04Langkah 3: Format Package Name

Package name/`applicationId` proyek UTS **wajib** mengikuti format berikut (lihat Pertemuan 1a untuk penjelasan konsep `applicationId` secara umum):

format wajib

    com.<nama><npm>.<nama_aplikasi>

| Bagian | Isi | Aturan |
|----|----|----|
| `nama` | Nama depan kamu | Huruf kecil semua, tanpa spasi |
| `npm` | NPM/NIM kamu | Hanya angka, ditempel langsung setelah nama (segmen tidak boleh *diawali* angka, jadi digabung dengan nama) |
| `nama_aplikasi` | Nama proyek yang didaftarkan di Langkah 1 | Huruf kecil, `underscore` sebagai pemisah kata, bukan tanda hubung |

Contoh: mahasiswa bernama **Budi** dengan NPM **2224510089** membuat aplikasi "Catatan Keuangan":

contoh applicationId

    com.budi2224510089.catatan_keuangan

contoh perintah flutter create

    flutter create --org com.budi2224510089 --project-name catatan_keuangan catatan_keuangan

Kenapa NPM digabung ke nama, bukan jadi segmen sendiri?

Package name Android tidak mengizinkan segmen yang diawali angka (`com.2224510089.budi` akan **ditolak** saat build). NPM digabung langsung setelah nama (`budi2224510089`) supaya segmennya tetap diawali huruf dan proyekmu bisa di-build tanpa error.

## 05Langkah 4: Lima Menu Wajib

Proyek UTS minimal harus punya lima layar berikut, saling terhubung lewat navigasi:

| Menu | Isi minimal |
|----|----|
| **Splash Screen** | Logo + nama aplikasi (desain bebas, tapi **tidak boleh sama** dengan splash screen mahasiswa lain), tampil sebentar lalu pindah ke Login. |
| **Login** | Form email/username + password, tombol masuk, link ke halaman Register. |
| **Register** | Form pendaftaran akun baru, tombol daftar, kembali ke halaman Login setelah berhasil. |
| **Home** | Halaman utama setelah login — isinya menyesuaikan ide aplikasimu (boleh masih berupa tampilan dummy/statis untuk UTS, fungsionalitas penuh menyusul di UAS). |
| **Profile** | Menampilkan info akun pengguna, minimal ada tombol untuk kembali/logout. |

Belum wajib tersambung ke API

Untuk UTS, fokusnya adalah **struktur & navigasi** — form boleh memakai data dummy/lokal (belum tersambung ke backend sungguhan). Koneksi ke API/database adalah materi lanjutan yang akan dikerjakan menuju UAS, mengikuti pola yang sudah dipelajari di Pertemuan 4-7 pada proyek `umkm-app`.

## 06Contoh Navigasi Antar Menu

Pola routing paling sederhana untuk lima menu ini sama seperti yang sudah dipelajari di Pertemuan 3 dan 7 — satu `MaterialApp` dengan peta `routes`, lalu setiap tombol berpindah pakai `Navigator`.

lib/main.dart — kerangka awal

    import 'package:flutter/material.dart';
    import 'screens/splash_screen.dart';
    import 'screens/auth/login_screen.dart';
    import 'screens/auth/register_screen.dart';
    import 'screens/home/home_screen.dart';
    import 'screens/home/profile_screen.dart';

    void main() {
      runApp(const MyApp());
    }

    class MyApp extends StatelessWidget {
      const MyApp({super.key});
      @override
      Widget build(BuildContext context) {
        return MaterialApp(
          title: 'Nama Aplikasimu',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(primarySwatch: Colors.indigo),
          initialRoute: '/',
          routes: {
            '/': (context) => const SplashScreen(),
            '/login': (context) => const LoginScreen(),
            '/register': (context) => const RegisterScreen(),
            '/home': (context) => const HomeScreen(),
            '/profile': (context) => const ProfileScreen(),
          },
        );
      }
    }

lib/screens/splash_screen.dart — contoh perpindahan otomatis

    import 'package:flutter/material.dart';

    class SplashScreen extends StatefulWidget {
      const SplashScreen({super.key});
      @override
      State<SplashScreen> createState() => _SplashScreenState();
    }

    class _SplashScreenState extends State<SplashScreen> {
      @override
      void initState() {
        super.initState();
        Future.delayed(const Duration(seconds: 2), () {
          if (!mounted) return;
          Navigator.pushReplacementNamed(context, '/login');
        });
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          backgroundColor: Colors.indigo,
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: const [
                Icon(Icons.apps, size: 72, color: Colors.white),
                SizedBox(height: 16),
                Text('Nama Aplikasimu', style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        );
      }
    }

contoh perpindahan dari tombol

    // Dari LoginScreen menuju Home setelah "login" (dummy, belum ke API)
    ElevatedButton(
      onPressed: () => Navigator.pushReplacementNamed(context, '/home'),
      child: const Text('Masuk'),
    ),

    // Dari LoginScreen menuju Register
    TextButton(
      onPressed: () => Navigator.pushNamed(context, '/register'),
      child: const Text('Belum punya akun? Daftar di sini'),
    ),

    // Dari HomeScreen menuju Profile (lewat BottomNavigationBar/tombol/ikon)
    IconButton(
      icon: const Icon(Icons.person),
      onPressed: () => Navigator.pushNamed(context, '/profile'),
    ),

pushReplacementNamed vs pushNamed

Dipakai `pushReplacementNamed` dari Splash ke Login dan dari Login ke Home — **mengganti** halaman sebelumnya di riwayat navigasi, supaya pengguna tidak bisa menekan tombol back untuk kembali ke Splash atau ke Login setelah berhasil masuk. Sedangkan Login → Register memakai `pushNamed` biasa karena pengguna memang boleh menekan back untuk kembali ke Login (dibahas lengkap di Pertemuan 3).

## 07Checklist Sebelum Submit

- Ide aplikasi sudah dituliskan di spreadsheet kelas, dan sudah dicek tidak sama dengan mahasiswa lain.
- Proyek dibuat di folder baru "Project UTS dan UAS", bukan menimpa folder latihan pertemuan sebelumnya.
- Package name mengikuti format `com.<nama><npm>.<nama_aplikasi>`.
- Kelima menu wajib ada: Splash Screen, Login, Register, Home, Profile.
- Splash Screen punya logo + nama aplikasi yang berbeda dari milik mahasiswa lain.
- Navigasi antar kelima halaman berfungsi (bisa dicoba tekan semua tombol tanpa error merah).
- `flutter analyze` dijalankan dan tidak ada error (warning masih boleh ditoleransi).
- Proyek bisa dijalankan dengan `flutter run` tanpa crash saat dibuka pertama kali.

## 08Kesalahan yang Sering Terjadi

- **Lupa cek spreadsheet sebelum menuliskan ide** — berakhir dengan ide yang sama persis dengan mahasiswa lain, harus mengulang dari awal mendekati deadline.
- **Package name mengandung huruf besar atau spasi** — `Com.Budi.CatatanKeuangan` akan gagal di-build; harus huruf kecil semua.
- **NPM dijadikan segmen sendiri** (`com.budi.2224510089.catatan`) — gagal build karena segmen diawali angka. Gabungkan NPM langsung setelah nama.
- **Splash Screen tidak pernah berpindah halaman** — biasanya karena lupa memanggil `Navigator` di dalam `Future.delayed`, atau lupa `if (!mounted) return;` sehingga error saat widget sudah tidak ada di tree.
- **Menimpa folder latihan pertemuan 1-7** alih-alih membuat folder proyek baru — menyulitkan kalau sewaktu-waktu perlu membuka ulang materi latihan sebelumnya.

## 09Kriteria Penilaian

| Aspek | Yang dinilai |
|----|----|
| Keaslian ide | Ide tidak duplikat dengan mahasiswa lain, tercatat di spreadsheet kelas |
| Kesesuaian struktur | Package name mengikuti format wajib, struktur folder proyek rapi (mengikuti pola `lib/screens/...` seperti di `umkm-app`) |
| Kelengkapan menu | Kelima menu wajib ada dan masing-masing menampilkan konten yang relevan (bukan halaman kosong) |
| Navigasi | Perpindahan antar halaman berfungsi tanpa error, memakai pola `Navigator`/`routes` yang benar |
| Kebersihan kode | `flutter analyze` tanpa error, penamaan file/folder konsisten |

Proyek yang dibangun hari ini adalah fondasi UAS — semakin rapi struktur navigasi dan semakin matang ide yang dipilih sekarang, semakin mudah menambahkan fitur CRUD, koneksi API, dan database di pertemuan-pertemuan berikutnya. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
