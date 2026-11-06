<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Materi Pemula · Flutter

# Komponen Flutter dan Navigasi Antar-Halaman

Materi ini membahas konsep dasar widget pada Flutter, cara berpindah antar-halaman, serta praktik pembuatan tiga halaman yang saling terhubung.

Splash Screen→
Login→
Register

## 01Konsep Dasar: Segala Sesuatu di Flutter Adalah Widget

Dalam Flutter, setiap elemen yang tampil di layar disebut **Widget**. Teks adalah widget, tombol adalah widget, bahkan jarak kosong pun merupakan widget. Memahami konsep ini adalah langkah awal yang penting sebelum mempelajari hal lain.

Terdapat dua jenis widget yang perlu dipahami sejak awal:

- **StatelessWidget** — digunakan untuk tampilan yang isinya tidak berubah. Contohnya adalah splash screen yang hanya menampilkan logo.
- **StatefulWidget** — digunakan untuk tampilan yang datanya dapat berubah ketika pengguna berinteraksi. Contohnya adalah formulir login yang nilainya berubah saat pengguna mengetik.

contoh sederhana

    class HalamanSaya extends StatelessWidget {
      const HalamanSaya({super.key});

      @override
      Widget build(BuildContext context) {
        return const Text('Halo dunia');
      }
    }

Apabila diperlukan pembaruan tampilan melalui `setState()`, maka widget yang digunakan harus berupa `StatefulWidget`:

stateful_widget.dart

    class CounterPage extends StatefulWidget {
      const CounterPage({super.key});
      @override
      State<CounterPage> createState() => _CounterPageState();
    }

    class _CounterPageState extends State<CounterPage> {
      int angka = 0;

      void tambah() {
        setState(() { angka++; });
      }

      @override
      Widget build(BuildContext context) => Text('Angka: $angka');
    }

Perlu diperhatikan bahwa setiap kali `setState()` dipanggil, method `build()` akan dijalankan kembali. Mekanisme inilah yang digunakan Flutter untuk menggambar ulang tampilan.

## 02Komponen yang Perlu Dikenal Terlebih Dahulu

Berikut adalah widget-widget dasar yang paling sering digunakan dan wajib dikuasai sebelum melanjutkan ke materi berikutnya.

| Widget | Fungsi |
|----|----|
| `MaterialApp` | Pembungkus paling luar dari aplikasi. Mengatur tema, judul, dan routing. |
| `Scaffold` | Kerangka dasar satu halaman: AppBar, body, tombol, dan sebagainya. |
| `AppBar` | Bilah judul yang tampil di bagian atas layar. |
| `Text` | Menampilkan teks. |
| `Container` | Kotak serbaguna yang dapat diatur warna, ukuran, padding, dan margin-nya. |
| `Column / Row` | Menyusun widget secara vertikal atau horizontal. |
| `TextField / TextFormField` | Kolom input teks untuk formulir. |
| `ElevatedButton` | Tombol yang dapat ditekan. |
| `SizedBox` | Memberikan jarak kosong atau mengatur ukuran. |
| `Form + GlobalKey<FormState>` | Membungkus beberapa TextFormField agar dapat divalidasi sekaligus. |

pola yang akan sering digunakan

    Scaffold(
      appBar: AppBar(title: const Text('Contoh')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text('Nama Lengkap'),
            const SizedBox(height: 8),
            TextField(decoration: const InputDecoration(border: OutlineInputBorder())),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: () {}, child: const Text('Simpan')),
          ],
        ),
      ),
    )

## 03Navigasi Antar-Halaman

Bagian ini merupakan inti dari materi hari ini. Perpindahan halaman pada Flutter dilakukan melalui objek yang disebut **Navigator**. Terdapat tiga cara utama yang perlu dipahami.

### 3.1 Navigator.push — membuka halaman baru

Cara ini digunakan untuk membuka halaman baru, sementara halaman sebelumnya tetap berada di tumpukan sehingga dapat diakses kembali melalui tombol kembali (back).

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const HalamanRegister()),
    );

Untuk kembali ke halaman sebelumnya, gunakan: `Navigator.pop(context);`

### 3.2 Navigator.pushReplacement — halaman sebelumnya tidak dapat diakses kembali

Contoh penerapannya adalah pada perpindahan dari Splash Screen menuju Login. Setelah pengguna berhasil login, tombol kembali seharusnya tidak mengarahkan kembali ke splash screen. Oleh karena itu, digunakan `pushReplacement`.

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const LoginPage()),
    );

### 3.3 Named Routes — untuk proyek berskala lebih besar

Setiap halaman diberi nama pada `MaterialApp`, kemudian dipanggil menggunakan nama tersebut. Pendekatan inilah yang digunakan pada praktik selanjutnya.

    MaterialApp(
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginPage(),
        '/register': (context) => const RegisterPage(),
      },
    )

    Navigator.pushNamed(context, '/login');
    Navigator.pushReplacementNamed(context, '/login');

## 04Praktik: Splash Screen, Login, dan Register

struktur berkas

    lib/
     ├─ main.dart
     ├─ splash_screen.dart
     ├─ login_page.dart
     └─ register_page.dart

### 4.1 Splash Screen

Halaman ini tampil sesaat ketika aplikasi dibuka, kemudian secara otomatis berpindah ke halaman Login. Mekanismenya menggunakan `initState()` yang dikombinasikan dengan `Future.delayed`.

splash_screen.dart

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
        Future.delayed(const Duration(seconds: 3), () {
          if (mounted) {
            Navigator.pushReplacementNamed(context, '/login');
          }
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
                Icon(Icons.school, color: Colors.white, size: 80),
                SizedBox(height: 16),
                Text('SI FIK UBL',
                  style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        );
      }
    }

Mengapa perlu if (mounted)?

Pengecekan ini diperlukan untuk mengantisipasi kondisi widget yang sudah tidak aktif lagi (misalnya aplikasi ditutup oleh pengguna) sebelum durasi 3 detik selesai. Tanpa pengecekan ini, aplikasi berpotensi mengalami error.

### 4.2 Login Page — versi terstruktur dengan pemisahan method

login_page.dart

    class _LoginPageState extends State<LoginPage> {
      final _formKey = GlobalKey<FormState>();
      final _emailController = TextEditingController();
      final _passwordController = TextEditingController();

      void _prosesLogin() {
        if (_formKey.currentState!.validate()) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Login berhasil (dummy)')),
          );
        }
      }

      Widget _buildEmailField() {
        return TextFormField(
          controller: _emailController,
          decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
          validator: (v) => (v == null || v.isEmpty) ? 'Email wajib diisi' : null,
        );
      }

      Widget _buildPasswordField() {
        return TextFormField(
          controller: _passwordController,
          obscureText: true,
          decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
          validator: (v) => (v == null || v.length < 6) ? 'Password minimal 6 karakter' : null,
        );
      }

      Widget _buildLoginButton() {
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton(onPressed: _prosesLogin, child: const Text('Masuk')),
        );
      }

      Widget _buildRegisterLink() {
        return TextButton(
          onPressed: () => Navigator.pushNamed(context, '/register'),
          child: const Text('Belum memiliki akun? Daftar di sini'),
        );
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Login')),
          body: Padding(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildEmailField(),
                  const SizedBox(height: 16),
                  _buildPasswordField(),
                  const SizedBox(height: 24),
                  _buildLoginButton(),
                  const SizedBox(height: 12),
                  _buildRegisterLink(),
                ],
              ),
            ),
          ),
        );
      }

      @override
      void dispose() {
        _emailController.dispose();
        _passwordController.dispose();
        super.dispose();
      }
    }

Terdapat dua hal penting yang perlu diperhatikan: perpindahan ke halaman Register menggunakan `pushNamed`, bukan `pushReplacement`, karena pengguna masih dapat kembali ke halaman Login. Selain itu, `_formKey.currentState!.validate()` akan menjalankan seluruh `validator` pada setiap kolom secara bersamaan.

### 4.3 Register Page

register_page.dart

    class _RegisterPageState extends State<RegisterPage> {
      final _formKey = GlobalKey<FormState>();
      final _namaController = TextEditingController();
      final _emailController = TextEditingController();
      final _passwordController = TextEditingController();

      void _prosesRegister() {
        if (_formKey.currentState!.validate()) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Akun berhasil dibuat, silakan login')),
          );
          Navigator.pop(context);
        }
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Daftar Akun')),
          body: Padding(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _namaController,
                    decoration: const InputDecoration(labelText: 'Nama Lengkap', border: OutlineInputBorder()),
                    validator: (v) => (v == null || v.isEmpty) ? 'Nama wajib diisi' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _emailController,
                    decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                    validator: (v) => (v == null || v.isEmpty) ? 'Email wajib diisi' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                    validator: (v) => (v == null || v.length < 6) ? 'Password minimal 6 karakter' : null,
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(onPressed: _prosesRegister, child: const Text('Daftar')),
                  ),
                ],
              ),
            ),
          ),
        );
      }

      @override
      void dispose() {
        _namaController.dispose();
        _emailController.dispose();
        _passwordController.dispose();
        super.dispose();
      }
    }

Penggunaan `Navigator.pop(context)` bertujuan agar setelah proses pendaftaran selesai, pengguna secara otomatis kembali ke halaman Login tanpa menambah tumpukan halaman baru.

### 4.4 Menghubungkan Seluruh Halaman pada main.dart

main.dart

    import 'package:flutter/material.dart';
    import 'splash_screen.dart';
    import 'login_page.dart';
    import 'register_page.dart';

    void main() {
      runApp(const MyApp());
    }

    class MyApp extends StatelessWidget {
      const MyApp({super.key});
      @override
      Widget build(BuildContext context) {
        return MaterialApp(
          title: 'Aplikasi SI FIK UBL',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(primarySwatch: Colors.indigo),
          initialRoute: '/',
          routes: {
            '/': (context) => const SplashScreen(),
            '/login': (context) => const LoginPage(),
            '/register': (context) => const RegisterPage(),
          },
        );
      }
    }

Alur akhir aplikasi

Splash Screen (3 detik) → pushReplacement → Login. Login → pushNamed → Register. Register → pop → kembali ke Login.

## 05Kesalahan yang Umum Terjadi pada Pemula

- **Lupa menambahkan const** — bukan merupakan error fatal, namun dapat memperlambat performa aplikasi. Apabila isi widget tidak berubah, tambahkan `const` di depannya.
- **Tertukar antara push dan pushReplacement** — apabila halaman sebelumnya masih perlu diakses melalui tombol kembali, gunakan `push`. Apabila tidak, gunakan `pushReplacement`.
- **Lupa memanggil dispose() pada controller** — setiap `TextEditingController` yang dibuat wajib di-`dispose()`. Kelalaian ini dapat menyebabkan kebocoran memori (memory leak).
- **Memanggil Navigator sebelum widget siap** — oleh karena itu pada Splash Screen dilakukan pengecekan `if (mounted)` terlebih dahulu.

## 06Latihan

1.  Tambahkan `Image.asset()` pada Splash Screen untuk menampilkan logo kampus, menggantikan ikon `Icons.school`.
2.  Tambahkan validasi format email pada halaman Login menggunakan `RegExp`, tidak hanya memeriksa apakah kolom kosong atau tidak.
3.  Buat halaman baru bernama `HomePage` yang tampil setelah proses login berhasil, menggunakan `pushReplacementNamed`.
4.  Ubah durasi splash screen dan amati perbedaannya.
5.  **Tantangan:** simpan status login pengguna menggunakan package `shared_preferences`, sehingga pengguna tidak perlu login ulang setiap kali membuka aplikasi.

## 07Menyusun Kode agar Lebih Terstruktur

Daripada menuliskan seluruh widget secara berurutan di dalam satu method `build()`, sebaiknya kode dipecah menjadi beberapa method kecil agar lebih mudah dibaca.

- **Tempatkan berkas pada folder yang sesuai** — buat folder `lib/pages/`, jangan menumpuk seluruh berkas `.dart` langsung di dalam `lib/`.
- **Pisahkan setiap bagian antarmuka menjadi method tersendiri** — misalnya `_buildEmailField()`, `_buildLoginButton()`, dan sejenisnya.
- **Pisahkan logika dari tampilan** — fungsi seperti `_prosesLogin()` ditempatkan terpisah dari bagian yang menampilkan widget.
- **Kelompokkan seluruh variabel di bagian atas kelas** — controller dan `_formKey` dideklarasikan sebelum method lainnya.

## 08Kelas Tidak Terbentuk Secara Otomatis — Berikut Cara Membuatnya dengan Cepat

Berkas baru yang dibuat masih dalam keadaan kosong. Struktur dasar (boilerplate) `StatefulWidget` tidak muncul secara otomatis, namun terdapat fitur snippet pada editor yang dapat menghasilkannya secara instan.

Snippet pada VS Code / Android Studio

Ketikkan `stful` kemudian tekan Enter atau Tab, maka struktur dasar `StatefulWidget` akan muncul secara lengkap. Apabila membutuhkan widget tanpa state, ketikkan `stless` kemudian tekan Enter.

Apabila mengalami error, sebagian besar penyebabnya berasal dari tiga hal: lupa menuliskan `import`, kesalahan penggunaan `context`, atau lupa memanggil `setState()`. Periksa ketiga hal tersebut terlebih dahulu sebelum melakukan penelusuran lebih lanjut. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
