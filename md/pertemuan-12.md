<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 12 · Praktikum 3/5 · Proyek Sendiri

# Fundamental Flutter, Konek API & Halaman Awal

Backend sendiri sudah jalan dari Pertemuan 11. Sekarang giliran sisi Flutter: mundur dulu ke dasar widget & cara Flutter bicara ke API (sama seperti UMKM App), lalu langsung dipakai membangun alur awal aplikasimu sendiri — **Splash → Login → Register → Home** — tersambung ke backend yang kamu bangun sendiri, bukan lagi server UMKM.

← [Pertemuan 11: Backend Sendiri](pertemuan-11.html)
[Pertemuan 13: CRUD Lengkap](pertemuan-13.html) →

## 01Tentang Pertemuan Ini

Pertemuan ini menyatukan dua hal: **fundamental Flutter** (widget layout + cara konek API — diringkas dari [Pertemuan 9 Bagian 13](pertemuan-09.html#s13)) dan **praktik langsung** membangun tiga halaman pertama proyekmu (diringkas dari [Pertemuan 9 Bagian 15](pertemuan-09.html#s15)). Kalau kamu sudah lancar dengan widget dasar dari Pertemuan 5-7, Bagian 03 boleh dibaca cepat sebagai pengingat — fokus utama ada di Bagian 05.

Tugas Kamu — sebelum mulai

Pastikan proyek Flutter UAS-mu (dari Pertemuan 8) sudah punya: struktur `lib/screens/`, dan backend sendiri dari Pertemuan 11 sudah berjalan (`flutter run` di satu terminal, server backend di terminal lain, keduanya di jaringan yang sama — ingat aturan `baseUrl` harus pakai IP LAN, bukan `localhost`, kalau diuji di device/emulator fisik).

## 02Peta Halaman & Dependency

Struktur `lib/screens/` di `umkm-app` mengikuti persis alur UX yang dirancang di Pertemuan 10:

lib/screens/ — contoh acuan umkm-app

    screens/
    ├── splash_screen.dart              → cek token, arahkan ke /home atau /login
    ├── auth/
    │   ├── login_screen.dart
    │   └── register_screen.dart
    └── home/
        ├── home_screen.dart            → shell tab (IndexedStack + NavigationBar)
        ├── <entitas>/
        │   ├── <entitas>_list_screen.dart   → daftar (publik)
        │   ├── <entitas>_detail_screen.dart → detail (publik)
        │   ├── my_<entitas>_screen.dart     → milik sendiri (perlu login, CRUD)
        │   └── <entitas>_form_screen.dart    → form tambah/edit
        └── profile/
            ├── profile_screen.dart
            └── update_profile_screen.dart

Tidak perlu state management library (Provider/Riverpod/Bloc) — cukup `StatefulWidget` bawaan, `FutureBuilder`, dan `setState`, persis seperti `umkm-app`.

| Package | Fungsi |
|----|----|
| `http` | Semua request ke API — dibungkus di satu `ApiService`, tidak dipanggil langsung dari screen. |
| `flutter_secure_storage` | Menyimpan token JWT terenkripsi, bukan `SharedPreferences` biasa. |
| `image_picker` | Memilih foto dari galeri (kalau aplikasimu punya fitur upload foto). |

Tugas Kamu

Buat struktur folder `lib/screens/` untuk aplikasimu mengikuti pola di atas — ganti `<entitas>` dengan nama entitas utama aplikasimu (hasil Pertemuan 10). Tambahkan dependency `http` dan `flutter_secure_storage` ke `pubspec.yaml` kalau belum ada, lalu `flutter pub get`.

## 03Fundamental Layout: Widget Dasar

Di Flutter, **semuanya adalah widget** — menyusun tampilan berarti menyusun widget jadi sebuah *pohon*. Empat widget tata letak ini dipakai di hampir setiap layar:

| Widget | Fungsi |
|----|----|
| `Column` | Menyusun widget anak **vertikal**, satu di bawah yang lain. |
| `Row` | Menyusun widget anak **horizontal**, kebalikan dari `Column`. |
| `Padding` / `SizedBox` | `Padding` memberi jarak di sekeliling satu widget; `SizedBox` kotak kosong berukuran tetap, sering jadi "jarak antar widget". |
| `Expanded` / `Flexible` | Memaksa satu widget anak di dalam `Row`/`Column` mengisi sisa ruang yang tersedia. |

umkm_list_screen.dart — tampilan error, contoh acuan

    Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Gagal memuat data: ${snapshot.error}'),
          const SizedBox(height: 12),
          ElevatedButton(onPressed: _muatUlang, child: const Text('Coba Lagi')),
        ],
      ),
    )

**Menampilkan daftar data** selalu pakai `ListView.builder`, bukan `ListView` biasa atau `Column` berisi banyak item manual — `ListView.builder` hanya membangun widget untuk item yang *sedang terlihat* di layar, jauh lebih hemat untuk data banyak:

ListView.builder — pola umum

    ListView.builder(
      itemCount: hasil.data.length,
      itemBuilder: (context, i) {
        final item = hasil.data[i];
        return ListTile(
          title: Text(item.nama),
          onTap: () => Navigator.push(context,
            MaterialPageRoute(builder: (_) => DetailScreen(id: item.id))),
        );
      },
    )

**Struktur dasar satu halaman** hampir selalu `StatefulWidget` + `Scaffold`:

kerangka umum tiap layar

    class ContohScreen extends StatefulWidget {
      const ContohScreen({super.key});
      @override
      State<ContohScreen> createState() => _ContohScreenState();
    }

    class _ContohScreenState extends State<ContohScreen> {
      @override
      void initState() {
        super.initState();
        // kode yang jalan SEKALI saat layar pertama kali dibuka
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Judul Layar')),
          body: /* ...isi layar... */,
        );
      }
    }

Penjelasan lengkap baris-per-baris (kenapa `mainAxisSize: MainAxisSize.min`, kenapa `Scaffold`, dst) ada di [Pertemuan 9 Bagian 13](pertemuan-09.html#s13) — bagian ini cuma ringkasan cepat.

Tugas Kamu

Buka <a href="https://dartpad.dev" target="_blank" rel="noopener">dartpad.dev</a>, tempel kerangka `StatefulWidget` di atas, lalu isi `build()`-nya dengan satu `Column` berisi minimal 3 widget (teks + jarak + tombol) — ini latihan layout dasar sebelum dipakai di halaman sungguhan.

## 04Fundamental Konek ke API

Tiga konsep Dart yang wajib dipahami sebelum menulis `ApiService`:

- **`Future<T>`** — representasi "nilai yang *akan* ada", karena menunggu jaringan. Memanggil API selalu mengembalikan `Future`, tidak pernah data langsung.
- **`async` / `await`** — `await` menjeda eksekusi sampai `Future`-nya selesai, baru lanjut ke baris berikutnya dengan nilai yang sudah "terbuka".
- **`jsonDecode`/`jsonEncode`** — API membalas teks JSON mentah; `jsonDecode` mengubahnya jadi `Map<String, dynamic>` yang bisa dibaca Dart.

pola dasar satu fungsi API, contoh acuan dari api_service.dart

    Future<List<Item>> getDaftarItem() async {
      final response = await http.get(Uri.parse('$baseUrl/items'));
      final body = jsonDecode(response.body) as Map<String, dynamic>;

      if (response.statusCode != 200) {
        throw ApiException(body['error']?['message'] ?? 'Gagal memuat data');
      }
      final list = body['data'] as List;
      return list.map((e) => Item.fromJson(e)).toList();
    }

Lalu dipakai di layar lewat `FutureBuilder`, yang otomatis menangani tiga kondisi (memuat/gagal/berhasil):

FutureBuilder — pola umum

    late Future<List<Item>> _futureItem;

    @override
    void initState() {
      super.initState();
      _futureItem = _apiService.getDaftarItem();   // panggil API SEKALI
    }

    // ...di dalam build():
    FutureBuilder<List<Item>>(
      future: _futureItem,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Text('Gagal memuat data: ${snapshot.error}'));
        }
        return ListView.builder(/* ...tampilkan snapshot.data!... */);
      },
    )

Kenapa panggil API di initState, bukan build()?

`build()` bisa dipanggil ulang berkali-kali, sedangkan `initState()` dijamin cuma sekali seumur hidup widget. Kalau pemanggilan API ditaruh di `build()`, setiap rebuild akan mengirim request baru tanpa henti.

Tugas Kamu

Buat berkas `lib/services/api_service.dart` di proyekmu. Tulis `baseUrl` menunjuk ke backend sendiri (Pertemuan 11) — pakai IP LAN kalau diuji di device/emulator fisik, bukan `localhost`. Tulis satu fungsi `getDaftarItem()` (atau nama sesuai entitasmu) mengikuti pola di atas.

## 05Membangun Splash, Login, Register

Tiga halaman pertama yang menyatukan semua fundamental di atas — pola di `umkm-app` (lihat [Pertemuan 9 Bagian 15](pertemuan-09.html#s15)):

- **Splash** — di `initState`, cek apakah ada token tersimpan: kalau ada, langsung `pushReplacementNamed('/home')`; kalau tidak, ke `'/login'`.
- **Login** — `Form` + `GlobalKey<FormState>`, validasi lokal dulu sebelum memanggil API. State `_loading` menonaktifkan tombol & menampilkan spinner selama request berlangsung.
- **Register** — pola identik dengan login. Setelah sukses, **tidak** auto-login — kembalikan ke halaman Login untuk masuk manual (mengonfirmasi akun benar-benar bisa dipakai).

login_screen.dart — \_prosesLogin, contoh acuan

    Future<void> _prosesLogin() async {
      if (!_formKey.currentState!.validate()) return;
      setState(() => _loading = true);
      try {
        await _apiService.login(_emailController.text, _passwordController.text);
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, '/home');
      } on ApiException catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
      } finally {
        if (mounted) setState(() => _loading = false);
      }
    }

Lima hal yang menjaga fungsi ini dari bug umum pemula: (1) validasi lokal dicek **sebelum** request dikirim; (2) `setState` menampilkan spinner; (3) `if (!mounted) return;` setelah `await` — mencegah error memanggil `Navigator`/`setState` pada widget yang sudah tidak ada di layar; (4) `on ApiException catch` — hanya menangkap exception yang memang sengaja dilempar `ApiService`, bukan `catch` generik yang menelan bug lain; (5) `finally` memastikan spinner tidak menggantung selamanya kalau terjadi error tak terduga. Penjelasan baris-per-baris lengkap: [Pertemuan 9 Bagian 15](pertemuan-09.html#s15).

Tugas Kamu

1.  Tulis `login(email, password)` dan `register(nama, email, password)` di `api_service.dart`-mu, memanggil endpoint backend sendiri dari Pertemuan 11.
2.  Bangun `splash_screen.dart`, `login_screen.dart`, `register_screen.dart` mengikuti pola di atas — termasuk state `_loading`, pengecekan `mounted`, dan penanganan `ApiException` lewat `SnackBar`.
3.  Daftarkan ketiganya di `routes` (`main.dart`) dengan nama `/` (atau `/splash`), `/login`, `/register`.

## 06Menjalankan & Menguji Alur Auth

Jalankan `flutter run` sambil backend-mu aktif, lalu uji skenario yang sama seperti `umkm-app`:

1.  Password diisi kurang dari minimum → tekan "Masuk"/"Daftar" → **tidak boleh ada jeda loading sama sekali** (validasi lokal gagal sebelum request dikirim).
2.  Register akun baru → harus kembali ke layar Login (bukan auto-login).
3.  Login dengan akun yang baru dibuat → spinner sebentar, lalu pindah ke Home.
4.  Login dengan password salah → spinner sebentar, lalu kembali normal + `SnackBar` pesan error.
5.  Tutup & buka ulang aplikasi setelah login → harus langsung ke Home (bukan ke Login lagi) — bukti Splash membaca token tersimpan.

Coba Sendiri

Tambahkan `debugPrint('loading: $_loading');` di awal `build()` salah satu layar untuk benar-benar melihat state `_loading` berubah `true`/`false` di Debug Console — bukti konkret `setState` di fungsi `_prosesLogin` benar-benar terpanggil, bukan cuma teori.

Kalau kelima skenario di atas berhasil, fondasi auth-mu sudah sama kuat dengan `umkm-app` — siap dilanjutkan ke CRUD lengkap di Pertemuan 13.

## 07Rangkuman & Checklist

- Struktur `lib/screens/` sudah dibuat sesuai pola, dependency `http` & `flutter_secure_storage` terpasang.
- `api_service.dart` punya fungsi `login`/`register`/minimal 1 fungsi `GET` daftar data, menunjuk ke backend sendiri.
- Splash, Login, Register jalan dan terhubung ke backend sendiri (bukan server UMKM).
- Kelima skenario uji di Bagian 06 semua berhasil sesuai yang diharapkan.

Checkpoint sebelum Pertemuan 13

Alur auth yang jalan penuh ini jadi fondasi: Pertemuan 13 akan menambahkan CRUD lengkap untuk entitas utama aplikasimu di atas fondasi yang sama persis (token yang sama, `ApiService` yang sama, pola `FutureBuilder` yang sama).

← [Pertemuan 11: Backend Sendiri](pertemuan-11.html)
[Pertemuan 13: CRUD Lengkap](pertemuan-13.html) →

Bagian 3 dari 5 rangkaian praktikum proyek UAS — lanjut ke [Pertemuan 13: Halaman CRUD Lengkap & ApiService](pertemuan-13.html). — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
