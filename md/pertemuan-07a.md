<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 7a · Proyek Lengkap

# Membangun umkm-app dari Nol: Panduan Lengkap

Materi ini merangkum Pertemuan 5, 6, dan 7 menjadi satu alur runtut: membuat proyek Flutter `umkm-app` dari `flutter create` yang kosong sampai menjadi aplikasi penuh — login, lihat semua UMKM, kelola UMKM & produk milik sendiri lengkap dengan foto, dan profil — tersambung ke backend Go `umkm-api` (Pertemuan 4). Setiap berkas disertai kode lengkap dan penjelasan *mengapa* ditulis seperti itu, bukan sekadar salin-tempel.

Daftar isi cepat

1.  [01. Tujuan & Prasyarat](#s1)
2.  [02. Membuat Proyek dari Nol](#s2)
3.  [03. Struktur Folder Final](#s3)
4.  [04. Dependency di pubspec.yaml](#s4)
5.  [05. Konfigurasi Native](#s5)
6.  [06. Model: Umkm, Produk, Paginasi](#s6)
7.  [07. Model: User](#s7)
8.  [08. TokenStorage](#s8)
9.  [09. ApiService Lengkap](#s9)
10. [10. main.dart & Routing](#s10)
11. [11. SplashScreen](#s11)
12. [12. Login & Register](#s12)
13. [13. HomeScreen](#s13)
14. [14. Profile & UpdateProfile](#s14)
15. [15. UmkmList & UmkmDetail](#s15)
16. [16. MyUmkmScreen](#s16)
17. [17. Form UMKM & Produk](#s17)
18. [18. Menjalankan Aplikasi](#s18)
19. [19. Troubleshooting Cepat](#s19)
20. [20. Latihan](#s20)

## 01Tujuan & Prasyarat

Di akhir materi ini, akan ada satu proyek Flutter utuh bernama `umkm-app` yang bisa: mendaftar & login, melihat daftar seluruh UMKM beserta detailnya (publik, tanpa login), membuat/mengubah/menghapus UMKM dan produk milik sendiri lengkap dengan upload foto (butuh login), serta melihat dan mengubah profil akun. Semua data sungguhan, datang dari API Golang + PostgreSQL yang dibangun di Pertemuan 4.

Sebelum mulai, pastikan:

- Flutter SDK sudah terpasang dan `flutter doctor` bersih (Pertemuan 1).
- Backend `umkm-api` (Pertemuan 4) sudah bisa dijalankan dengan `go run ./cmd/api` dan diuji lewat Swagger (`http://localhost:8080/swagger/index.html`).
- Paham dasar widget, `State`/`setState`, dan navigasi (Pertemuan 3), serta pola `FutureBuilder`/async (Pertemuan 6).
- Paham konsep `applicationId`/package name (Pertemuan 1a) — dipakai saat `flutter create` di bawah.

Materi ini vs Pertemuan 5–7

Isinya sama persis dengan Pertemuan 5, 6, dan 7 — tidak ada fitur baru. Bedanya, di sini semua langkah disusun **berurutan dari proyek kosong** sampai selesai dalam satu alur baca, cocok dipakai sebagai referensi saat membangun ulang proyek dari nol (misalnya proyek UAS/tugas akhir) tanpa perlu bolak-balik tiga pertemuan berbeda.

## 02Membuat Proyek dari Nol

Jalankan perintah berikut di terminal, di folder tempat proyek ingin disimpan:

terminal

    flutter create --org com.aseptrisna --project-name umkm_app umkm-app
    cd umkm-app

Beberapa catatan soal perintah ini (lihat Pertemuan 1a untuk penjelasan konsepnya):

- `--org com.aseptrisna` menentukan `applicationId`/Bundle Identifier menjadi `com.aseptrisna.umkm_app`. Ganti `aseptrisna` dengan identitasmu sendiri.
- `--project-name umkm_app` adalah nama internal paket Dart (dipakai di `pubspec.yaml` dan import `package:umkm_app/...`) — **harus** `snake_case`, tidak boleh pakai tanda hubung.
- Nama folder `umkm-app` (pakai tanda hubung) boleh berbeda dari nama proyek Dart `umkm_app` — folder cuma lokasi di disk, tidak memengaruhi kode.

✓ Verifikasi

Jalankan `flutter run` sekali di sini (sebelum kode apa pun ditambahkan) untuk memastikan proyek kosong bisa jalan ke device/emulator pilihanmu (Pertemuan 2) — counter demo bawaan Flutter akan muncul. Kalau ini berhasil, lanjut ke langkah berikutnya.

## 03Struktur Folder Final

Berikut struktur `lib/` yang akan dibangun sampai akhir materi ini — flat per area, konsisten dengan pola `lib/screens/<area>/<nama>_screen.dart` (bukan `lib/features/...` berlapis):

struktur folder

    lib/
    ├── main.dart
    ├── models/
    │   ├── user_model.dart
    │   ├── umkm_model.dart
    │   ├── produk_model.dart
    │   └── paginated_result.dart
    ├── services/
    │   ├── api_service.dart
    │   └── token_storage.dart
    └── screens/
        ├── splash_screen.dart
        ├── auth/
        │   ├── login_screen.dart
        │   └── register_screen.dart
        └── home/
            ├── home_screen.dart
            ├── profile/
            │   ├── profile_screen.dart
            │   └── update_profile_screen.dart
            └── umkm/
                ├── umkm_list_screen.dart
                ├── umkm_detail_screen.dart
                ├── myumkm_screen.dart
                ├── umkm_form_screen.dart
                └── produk_form_screen.dart

Buat seluruh folder kosongnya sekarang supaya tinggal mengisi berkas di langkah-langkah berikutnya:

terminal (dari dalam folder umkm-app)

    mkdir -p lib/models lib/services lib/screens/auth lib/screens/home/profile lib/screens/home/umkm

## 04Dependency di pubspec.yaml

Empat package tambahan dibutuhkan di luar bawaan Flutter: `http` (Pertemuan 6, panggil REST API), `flutter_secure_storage` (Pertemuan 7, simpan token terenkripsi), dan `image_picker` (Pertemuan 7, pilih foto dari galeri).

terminal

    flutter pub add http
    flutter pub add flutter_secure_storage
    flutter pub add image_picker

Perintah ini otomatis menulis versi terbaru ke `pubspec.yaml` dan menjalankan `flutter pub get`. Tidak perlu mengetik versi secara manual.

Kenapa flutter_secure_storage, bukan shared_preferences?

`shared_preferences` menyimpan data sebagai file XML/plist biasa yang bisa dibaca siapa pun dengan akses ke penyimpanan device. `flutter_secure_storage` memakai Keystore (Android)/Keychain (iOS) — penyimpanan terenkripsi level sistem operasi, tempat yang semestinya untuk token autentikasi.

image_picker tidak butuh permission_handler manual

Plugin ini sudah menangani sendiri permintaan izin runtime untuk galeri/kamera di Android maupun iOS. Cukup tambahkan deklarasi di Bagian 05; jangan tambahkan `permission_handler` kecuali benar-benar perlu mengecek status izin secara manual di luar alur pilih-foto.

## 05Konfigurasi Native (Android & iOS)

Dua pengaturan wajib di luar kode Dart, atau aplikasi akan gagal diam-diam saat mengakses backend lokal atau galeri foto:

| Platform | Yang ditambahkan | Kenapa |
|----|----|----|
| Android | `android:usesCleartextTraffic="true"` pada tag `<application>` | Sejak Android 9, trafik HTTP polos (bukan HTTPS) diblokir secara default. Backend lokal (`http://10.0.2.2:8080`) memakai HTTP biasa, jadi tanpa ini `http.get`/`http.post` gagal dengan `SocketException` tanpa pesan jelas. |
| iOS | `NSPhotoLibraryUsageDescription` di `Info.plist` | Wajib ada deskripsi alasan akses galeri, atau aplikasi **crash** begitu `image_picker` dipanggil. |

android/app/src/main/AndroidManifest.xml

    <application
        android:label="umkm_app"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true">
        ...
    </application>

ios/Runner/Info.plist — tambahkan di dalam \<dict\> utama

    <key>NSPhotoLibraryUsageDescription</key>
    <string>Dipakai untuk memilih foto UMKM/produk</string>

usesCleartextTraffic hanya untuk development

Pengaturan ini sengaja melonggarkan keamanan supaya HTTP polos ke backend lokal diizinkan. Untuk aplikasi produksi yang server-nya sudah pakai HTTPS, baris ini sebaiknya dihapus kembali — bukan kebiasaan yang dibawa ke aplikasi nyata.

## 06Model: Umkm, Produk, dan Paginasi

Model di Flutter adalah representasi Dart dari bentuk JSON yang dikirim `umkm-api` (Pertemuan 4 Bagian 9). Setiap model punya `factory ...fromJson()` untuk mengubah `Map<String, dynamic>` hasil `jsonDecode` menjadi object Dart yang type-safe — sehingga kesalahan tipe data ketahuan saat kompilasi, bukan saat aplikasi sudah berjalan.

lib/models/umkm_model.dart

    class Umkm {
      final int id;
      final int userId;
      final String nama;
      final String deskripsi;
      final String alamat;
      final String foto;

      Umkm({
        required this.id,
        required this.userId,
        required this.nama,
        required this.deskripsi,
        required this.alamat,
        required this.foto,
      });

      factory Umkm.fromJson(Map<String, dynamic> json) {
        return Umkm(
          id: json['id'] as int,
          userId: json['user_id'] as int,
          nama: json['nama'] as String,
          deskripsi: json['deskripsi'] as String? ?? '',
          alamat: json['alamat'] as String? ?? '',
          foto: json['foto'] as String? ?? '',
        );
      }

      bool get punyaFoto => foto.isNotEmpty;
    }

lib/models/produk_model.dart

    class Produk {
      final int id;
      final int umkmId;
      final String nama;
      final double harga;
      final String deskripsi;
      final String foto;

      Produk({
        required this.id,
        required this.umkmId,
        required this.nama,
        required this.harga,
        required this.deskripsi,
        required this.foto,
      });

      factory Produk.fromJson(Map<String, dynamic> json) {
        return Produk(
          id: json['id'] as int,
          umkmId: json['umkm_id'] as int,
          nama: json['nama'] as String,
          harga: (json['harga'] as num).toDouble(),
          deskripsi: json['deskripsi'] as String? ?? '',
          foto: json['foto'] as String? ?? '',
        );
      }
    }

Kenapa (json\['harga'\] as num).toDouble()?

PostgreSQL `NUMERIC` bisa dikirim sebagai angka bulat oleh `encoding/json` Go (mis. `17000` tanpa desimal). Meng-cast ke `num` dulu — bukan langsung `double` — membuat parsing tetap aman baik nilainya `17000` maupun `17000.50`.

Kenapa pakai ?? '' di setiap field String?

Field seperti `deskripsi`, `alamat`, atau `foto` boleh kosong di API (string kosong, bukan `null`) — namun berjaga dengan `as String? ?? ''` membuat parsing tidak pernah crash walau suatu saat backend mengirim `null` untuk field itu.

Karena banyak endpoint mengembalikan `data` beserta `meta` (page/limit/total), dibuat satu class generic `PaginatedResult<T>` yang dipakai ulang untuk daftar UMKM maupun daftar produk:

lib/models/paginated_result.dart

    class PaginatedResult<T> {
      final List<T> data;
      final int page;
      final int limit;
      final int total;

      PaginatedResult({
        required this.data,
        required this.page,
        required this.limit,
        required this.total,
      });

      factory PaginatedResult.fromJson(
        Map<String, dynamic> json,
        T Function(Map<String, dynamic>) fromJsonItem,
      ) {
        final items = (json['data'] as List<dynamic>? ?? [])
            .map((e) => fromJsonItem(e as Map<String, dynamic>))
            .toList();
        final meta = json['meta'] as Map<String, dynamic>? ?? {};
        return PaginatedResult(
          data: items,
          page: meta['page'] as int? ?? 1,
          limit: meta['limit'] as int? ?? items.length,
          total: meta['total'] as int? ?? items.length,
        );
      }

      bool get masihAdaHalamanBerikutnya => page * limit < total;
    }

Generic `<T>` berarti class ini tidak terikat satu jenis model — dipanggil dengan `PaginatedResult.fromJson(json, Umkm.fromJson)` untuk daftar UMKM, atau `PaginatedResult.fromJson(json, Produk.fromJson)` untuk daftar produk, tanpa menulis ulang logika paginasinya.

## 07Model: User

Model terakhir merepresentasikan data akun, mengikuti kontrak `GET /profile` dan field `user` pada respons login.

lib/models/user_model.dart

    class User {
      final int id;
      final String nama;
      final String email;

      User({required this.id, required this.nama, required this.email});

      factory User.fromJson(Map<String, dynamic> json) {
        return User(
          id: json['id'] as int,
          nama: json['nama'] as String,
          email: json['email'] as String,
        );
      }
    }

## 08TokenStorage: Menyimpan Token Login

Setelah login berhasil, server mengembalikan JWT token. Token ini harus disimpan secara lokal di device agar pengguna tidak perlu login ulang setiap membuka aplikasi, dan disimpan dengan aman.

lib/services/token_storage.dart

    import 'package:flutter_secure_storage/flutter_secure_storage.dart';

    /// Membungkus flutter_secure_storage agar seluruh aplikasi mengakses token
    /// lewat satu pintu — bukan memanggil FlutterSecureStorage() di banyak tempat.
    class TokenStorage {
      static const _storage = FlutterSecureStorage();
      static const _key = 'auth_token';

      static Future<void> simpan(String token) => _storage.write(key: _key, value: token);
      static Future<String?> ambil() => _storage.read(key: _key);
      static Future<void> hapus() => _storage.delete(key: _key);
    }

## 09ApiService Lengkap

Seluruh logika pemanggilan API dikumpulkan dalam satu class `ApiService`, terpisah dari widget/screen. Screen hanya perlu tahu *apa* yang dipanggil (mis. `getUmkmSaya()`), bukan *bagaimana* detail HTTP/header/parsing-nya. Berikut versi **lengkap** — timpa seluruh isi `api_service.dart` dengan ini:

lib/services/api_service.dart — LENGKAP

    import 'dart:convert';
    import 'package:http/http.dart' as http;

    import '../models/umkm_model.dart';
    import '../models/produk_model.dart';
    import '../models/paginated_result.dart';
    import '../models/user_model.dart';
    import 'token_storage.dart';

    class ApiException implements Exception {
      final String message;
      ApiException(this.message);

      @override
      String toString() => message;
    }

    class ApiService {
      static const String baseUrl = 'http://10.0.2.2:8080/api';

      // ---------- Publik: daftar & detail UMKM, tanpa login ----------

      Future<PaginatedResult<Umkm>> getUmkmList({String q = '', int page = 1}) async {
        final uri = Uri.parse('$baseUrl/umkm').replace(queryParameters: {
          if (q.isNotEmpty) 'q': q,
          'page': '$page',
          'limit': '10',
        });

        final response = await http.get(uri);
        final body = jsonDecode(response.body) as Map<String, dynamic>;

        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal memuat data UMKM');
        }
        return PaginatedResult.fromJson(body, Umkm.fromJson);
      }

      Future<Umkm> getUmkmDetail(int id) async {
        final response = await http.get(Uri.parse('$baseUrl/umkm/$id'));
        final body = jsonDecode(response.body) as Map<String, dynamic>;

        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'UMKM tidak ditemukan');
        }
        return Umkm.fromJson(body['data'] as Map<String, dynamic>);
      }

      Future<PaginatedResult<Produk>> getProdukByUmkm(int umkmId, {int page = 1}) async {
        final uri = Uri.parse('$baseUrl/umkm/$umkmId/produk').replace(queryParameters: {
          'page': '$page',
          'limit': '10',
        });

        final response = await http.get(uri);
        final body = jsonDecode(response.body) as Map<String, dynamic>;

        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal memuat produk');
        }
        return PaginatedResult.fromJson(body, Produk.fromJson);
      }

      // ---------- Auth & profil, butuh token ----------

      /// Header Authorization yang disisipkan ke setiap request yang butuh login.
      Future<Map<String, String>> _authHeaders() async {
        final token = await TokenStorage.ambil();
        return {'Authorization': 'Bearer $token'};
      }

      Future<User> register(String nama, String email, String password) async {
        final response = await http.post(
          Uri.parse('$baseUrl/auth/register'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'nama': nama, 'email': email, 'password': password}),
        );
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 201) {
          throw ApiException(body['error']?['message'] ?? 'Gagal mendaftar');
        }
        return User.fromJson(body['data'] as Map<String, dynamic>);
      }

      Future<void> login(String email, String password) async {
        final response = await http.post(
          Uri.parse('$baseUrl/auth/login'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'email': email, 'password': password}),
        );
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Email atau password salah');
        }
        final token = body['data']['token'] as String;
        await TokenStorage.simpan(token);
      }

      Future<void> logout() => TokenStorage.hapus();

      Future<User> getProfile() async {
        final response = await http.get(Uri.parse('$baseUrl/profile'), headers: await _authHeaders());
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal memuat profil');
        }
        return User.fromJson(body['data'] as Map<String, dynamic>);
      }

      Future<void> updateProfile(String nama, String email) async {
        final response = await http.put(
          Uri.parse('$baseUrl/profile'),
          headers: {...await _authHeaders(), 'Content-Type': 'application/json'},
          body: jsonEncode({'nama': nama, 'email': email}),
        );
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal memperbarui profil');
        }
      }

      Future<void> updatePassword(String lama, String baru) async {
        final response = await http.put(
          Uri.parse('$baseUrl/profile/password'),
          headers: {...await _authHeaders(), 'Content-Type': 'application/json'},
          body: jsonEncode({'password_lama': lama, 'password_baru': baru}),
        );
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal memperbarui password');
        }
      }

      // ---------- UMKM & produk milik sendiri, butuh token + multipart ----------

      Future<Umkm?> getUmkmSaya() async {
        final response = await http.get(Uri.parse('$baseUrl/umkm/saya'), headers: await _authHeaders());
        if (response.statusCode == 404) return null;
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal memuat UMKM saya');
        }
        return Umkm.fromJson(body['data'] as Map<String, dynamic>);
      }

      /// id == null -> membuat UMKM baru (POST /umkm).
      /// id terisi -> mengubah UMKM yang sudah ada (PUT /umkm/{id}).
      Future<Umkm> simpanUmkm({
        int? id,
        required String nama,
        String deskripsi = '',
        String alamat = '',
        String? fotoPath,
      }) async {
        final uri = id == null ? Uri.parse('$baseUrl/umkm') : Uri.parse('$baseUrl/umkm/$id');
        final request = http.MultipartRequest(id == null ? 'POST' : 'PUT', uri)
          ..headers.addAll(await _authHeaders())
          ..fields['nama'] = nama
          ..fields['deskripsi'] = deskripsi
          ..fields['alamat'] = alamat;
        if (fotoPath != null) {
          request.files.add(await http.MultipartFile.fromPath('foto', fotoPath));
        }

        final streamed = await request.send();
        final response = await http.Response.fromStream(streamed);
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200 && response.statusCode != 201) {
          throw ApiException(body['error']?['message'] ?? 'Gagal menyimpan UMKM');
        }
        return Umkm.fromJson(body['data'] as Map<String, dynamic>);
      }

      Future<void> hapusUmkm(int id) async {
        final response = await http.delete(Uri.parse('$baseUrl/umkm/$id'), headers: await _authHeaders());
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal menghapus UMKM');
        }
      }

      /// id == null -> tambah produk baru pada UMKM `umkmId` (POST /umkm/{umkmId}/produk).
      /// id terisi -> ubah produk yang sudah ada (PUT /produk/{id}), `umkmId` diabaikan.
      Future<Produk> simpanProduk({
        int? id,
        int? umkmId,
        required String nama,
        required double harga,
        String deskripsi = '',
        String? fotoPath,
      }) async {
        final uri = id == null
            ? Uri.parse('$baseUrl/umkm/$umkmId/produk')
            : Uri.parse('$baseUrl/produk/$id');
        final request = http.MultipartRequest(id == null ? 'POST' : 'PUT', uri)
          ..headers.addAll(await _authHeaders())
          ..fields['nama'] = nama
          ..fields['harga'] = '$harga'
          ..fields['deskripsi'] = deskripsi;
        if (fotoPath != null) {
          request.files.add(await http.MultipartFile.fromPath('foto', fotoPath));
        }

        final streamed = await request.send();
        final response = await http.Response.fromStream(streamed);
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200 && response.statusCode != 201) {
          throw ApiException(body['error']?['message'] ?? 'Gagal menyimpan produk');
        }
        return Produk.fromJson(body['data'] as Map<String, dynamic>);
      }

      Future<void> hapusProduk(int id) async {
        final response = await http.delete(Uri.parse('$baseUrl/produk/$id'), headers: await _authHeaders());
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        if (response.statusCode != 200) {
          throw ApiException(body['error']?['message'] ?? 'Gagal menghapus produk');
        }
      }

      static String fotoUrl(String relativePath) {
        final origin = baseUrl.replaceFirst('/api', '');
        return '$origin/uploads/$relativePath';
      }
    }

Beberapa keputusan desain penting dalam berkas ini:

- **login() bertipe `Future<void>`, bukan `Future<String>`** — token langsung disimpan ke `TokenStorage` di dalam method itu sendiri. Layar pemanggil cukup tahu "berhasil atau gagal" (lewat *throw*/tidaknya `ApiException`), tidak perlu tahu atau menyimpan token secara manual.
- **Satu `simpanUmkm`/`simpanProduk` untuk create *dan* update** — perbedaan `POST` (buat baru) dan `PUT /…/{id}` (ubah) di backend cuma soal method HTTP dan ada/tidaknya `{id}` di path; field yang dikirim persis sama. Parameter opsional `id` menghindari duplikasi kode di sini maupun di form nanti.
- **Request multipart, bukan `http.post` biasa** — endpoint yang menerima foto memakai `multipart/form-data` (Pertemuan 4 Bagian 10.8), sehingga di Dart memakai `http.MultipartRequest`. Header ditambahkan lewat `.headers.addAll(...)`, **bukan** parameter `headers:` biasa seperti di `http.get`/`http.post`.
- **`fotoPath` bernilai `null` berarti "tidak ganti foto", bukan "hapus foto"** — sama seperti di backend: kalau parameter foto tidak dikirim sama sekali, field `foto` yang sudah tersimpan di database tidak diubah.
- **`getUmkmSaya()` mengembalikan `Umkm?` (nullable)**, bukan melempar error saat belum punya UMKM — status `404` ditangani secara eksplisit sebagai "belum ada", bukan sebagai kegagalan. Layar `MyUmkmScreen` memanfaatkan ini untuk menampilkan tombol "Buat UMKM" alih-alih pesan error.

✓ Diverifikasi

Seluruh berkas ini — model, service, `token_storage.dart` — sudah dicoba `flutter analyze` dalam proyek nyata (`umkm-app`). Hasilnya `No issues found!`, tidak ada error maupun warning.

## 10main.dart & Routing

`main.dart` mendefinisikan titik masuk aplikasi dan peta *named route* yang dipakai seluruh layar untuk berpindah halaman.

lib/main.dart

    import 'package:flutter/material.dart';
    import 'package:umkm_app/screens/auth/login_screen.dart';
    import 'package:umkm_app/screens/auth/register_screen.dart';
    import 'package:umkm_app/screens/home/home_screen.dart';
    import 'package:umkm_app/screens/splash_screen.dart';

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
            '/login': (context) => const LoginScreen(),
            '/register': (context) => const RegisterPage(),
            '/home': (context) => const HomeScreen(),
          },
        );
      }
    }

Ganti package:umkm_app sesuai nama proyekmu

Import `package:umkm_app/...` di atas mengikuti nama yang diisi di `--project-name umkm_app` pada Bagian 02. Kalau proyekmu dibuat dengan nama berbeda, ganti `umkm_app` di baris import ini (dan hanya di baris ini — berkas lain dalam tutorial ini memakai import relatif `../` yang tidak terpengaruh nama proyek).

## 11SplashScreen: Memeriksa Token Tersimpan

Tugas `SplashScreen`: memeriksa apakah pengguna sudah pernah login sebelumnya (ada token tersimpan) — kalau ada, langsung masuk ke `HomeScreen` tanpa perlu login ulang; kalau tidak, arahkan ke `LoginScreen`.

lib/screens/splash_screen.dart

    import 'package:flutter/material.dart';
    import '../services/token_storage.dart';

    class SplashScreen extends StatefulWidget {
      const SplashScreen({super.key});
      @override
      State<SplashScreen> createState() => _SplashScreenState();
    }

    class _SplashScreenState extends State<SplashScreen> {
      @override
      void initState() {
        super.initState();
        _cekTokenTersimpan();
      }

      Future<void> _cekTokenTersimpan() async {
        final token = await TokenStorage.ambil();
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, token == null ? '/login' : '/home');
      }

      @override
      Widget build(BuildContext context) {
        return const Scaffold(
          backgroundColor: Colors.indigo,
          body: Center(child: CircularProgressIndicator(color: Colors.white)),
        );
      }
    }

if (!mounted) return; sebelum Navigator

Antara `await TokenStorage.ambil()` dimulai dan selesai, pengguna bisa saja sudah menutup aplikasi atau widget ini sudah dilepas dari tree. Memanggil `Navigator` pada `BuildContext` yang sudah tidak `mounted` akan melempar error. Pola ini berulang di **setiap** pemakaian `context` setelah sebuah `await` di seluruh materi ini.

## 12LoginScreen & RegisterScreen

Kedua layar memanggil `ApiService` sungguhan, dengan variabel `_loading` supaya tombol submit menampilkan indikator progres dan tidak bisa ditekan dua kali selama request berjalan.

lib/screens/auth/login_screen.dart

    import 'package:flutter/material.dart';
    import '../../services/api_service.dart';

    class LoginScreen extends StatefulWidget {
      const LoginScreen({super.key});
      @override
      State<LoginScreen> createState() => _LoginScreenState();
    }

    class _LoginScreenState extends State<LoginScreen> {
      final _formKey = GlobalKey<FormState>();
      final _emailController = TextEditingController();
      final _passwordController = TextEditingController();
      final _apiService = ApiService();
      bool _loading = false;

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
                    child: ElevatedButton(
                      onPressed: _loading ? null : _prosesLogin,
                      child: _loading
                          ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Text('Masuk'),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () => Navigator.pushNamed(context, '/register'),
                    child: const Text('Belum memiliki akun? Daftar di sini'),
                  ),
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

lib/screens/auth/register_screen.dart

    import 'package:flutter/material.dart';
    import '../../services/api_service.dart';

    class RegisterPage extends StatefulWidget {
      const RegisterPage({super.key});
      @override
      State<RegisterPage> createState() => _RegisterPageState();
    }

    class _RegisterPageState extends State<RegisterPage> {
      final _formKey = GlobalKey<FormState>();
      final _namaController = TextEditingController();
      final _emailController = TextEditingController();
      final _passwordController = TextEditingController();
      final _apiService = ApiService();
      bool _loading = false;

      Future<void> _prosesRegister() async {
        if (!_formKey.currentState!.validate()) return;
        setState(() => _loading = true);
        try {
          await _apiService.register(_namaController.text, _emailController.text, _passwordController.text);
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Akun berhasil dibuat, silakan login')),
          );
          Navigator.pop(context);
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        } finally {
          if (mounted) setState(() => _loading = false);
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
                    validator: (v) =>
                        (v == null || v.length < 6) ? 'Password minimal 6 karakter' : null,
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _prosesRegister,
                      child: _loading
                          ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Text('Daftar'),
                    ),
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

## 13HomeScreen: Navigasi Bawah Tiga Tab

Setelah login, pengguna mendarat di `HomeScreen` yang membagi aplikasi jadi tiga tab lewat `NavigationBar` (Material 3) — "Semua UMKM" (publik), "UMKM Saya" (butuh login), dan "Profil" (butuh login).

lib/screens/home/home_screen.dart

    import 'package:flutter/material.dart';
    import 'umkm/umkm_list_screen.dart';
    import 'umkm/myumkm_screen.dart';
    import 'profile/profile_screen.dart';

    class HomeScreen extends StatefulWidget {
      const HomeScreen({super.key});
      @override
      State<HomeScreen> createState() => _HomeScreenState();
    }

    class _HomeScreenState extends State<HomeScreen> {
      int _index = 0;

      static const _halaman = [
        UmkmListScreen(),
        MyUmkmScreen(),
        ProfileScreen(),
      ];

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          body: IndexedStack(index: _index, children: _halaman),
          bottomNavigationBar: NavigationBar(
            selectedIndex: _index,
            onDestinationSelected: (i) => setState(() => _index = i),
            destinations: const [
              NavigationDestination(icon: Icon(Icons.storefront_outlined), selectedIcon: Icon(Icons.storefront), label: 'Semua UMKM'),
              NavigationDestination(icon: Icon(Icons.store_outlined), selectedIcon: Icon(Icons.store), label: 'UMKM Saya'),
              NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profil'),
            ],
          ),
        );
      }
    }

IndexedStack, bukan sekadar menukar widget biasa

`IndexedStack` membangun ketiga halaman sekaligus di memori dan hanya menampilkan satu, alih-alih membongkar-pasang widget setiap pindah tab. Efeknya: state tiap tab (posisi scroll, `Future` yang sedang berjalan) tidak hilang ketika berpindah ke tab lain lalu kembali lagi.

## 14ProfileScreen & UpdateProfileScreen

lib/screens/home/profile/profile_screen.dart

    import 'package:flutter/material.dart';
    import '../../../models/user_model.dart';
    import '../../../services/api_service.dart';
    import 'update_profile_screen.dart';

    class ProfileScreen extends StatefulWidget {
      const ProfileScreen({super.key});
      @override
      State<ProfileScreen> createState() => _ProfileScreenState();
    }

    class _ProfileScreenState extends State<ProfileScreen> {
      final _apiService = ApiService();
      late Future<User> _futureProfile;

      @override
      void initState() {
        super.initState();
        _futureProfile = _apiService.getProfile();
      }

      Future<void> _logout() async {
        await _apiService.logout();
        if (!mounted) return;
        Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Profil Saya')),
          body: FutureBuilder<User>(
            future: _futureProfile,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Center(child: Text('Gagal memuat profil: ${snapshot.error}'));
              }
              final user = snapshot.data!;
              return ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  CircleAvatar(radius: 36, child: Text(user.nama[0].toUpperCase(), style: const TextStyle(fontSize: 28))),
                  const SizedBox(height: 16),
                  Text(user.nama, style: Theme.of(context).textTheme.titleLarge),
                  Text(user.email, style: TextStyle(color: Colors.grey[600])),
                  const SizedBox(height: 24),
                  ListTile(
                    leading: const Icon(Icons.edit),
                    title: const Text('Ubah Profil & Password'),
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => UpdateProfileScreen(user: user)),
                    ),
                  ),
                  ListTile(
                    leading: const Icon(Icons.logout, color: Colors.red),
                    title: const Text('Keluar', style: TextStyle(color: Colors.red)),
                    onTap: _logout,
                  ),
                ],
              );
            },
          ),
        );
      }
    }

lib/screens/home/profile/update_profile_screen.dart

    import 'package:flutter/material.dart';
    import '../../../models/user_model.dart';
    import '../../../services/api_service.dart';

    class UpdateProfileScreen extends StatefulWidget {
      final User user;
      const UpdateProfileScreen({super.key, required this.user});
      @override
      State<UpdateProfileScreen> createState() => _UpdateProfileScreenState();
    }

    class _UpdateProfileScreenState extends State<UpdateProfileScreen> {
      final _apiService = ApiService();
      final _formProfilKey = GlobalKey<FormState>();
      final _formPasswordKey = GlobalKey<FormState>();
      late final _namaController = TextEditingController(text: widget.user.nama);
      late final _emailController = TextEditingController(text: widget.user.email);
      final _passwordLamaController = TextEditingController();
      final _passwordBaruController = TextEditingController();
      bool _savingProfil = false;
      bool _savingPassword = false;

      Future<void> _simpanProfil() async {
        if (!_formProfilKey.currentState!.validate()) return;
        setState(() => _savingProfil = true);
        try {
          await _apiService.updateProfile(_namaController.text, _emailController.text);
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profil berhasil diperbarui')));
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        } finally {
          if (mounted) setState(() => _savingProfil = false);
        }
      }

      Future<void> _simpanPassword() async {
        if (!_formPasswordKey.currentState!.validate()) return;
        setState(() => _savingPassword = true);
        try {
          await _apiService.updatePassword(_passwordLamaController.text, _passwordBaruController.text);
          if (!mounted) return;
          _passwordLamaController.clear();
          _passwordBaruController.clear();
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Password berhasil diperbarui')));
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        } finally {
          if (mounted) setState(() => _savingPassword = false);
        }
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Ubah Profil')),
          body: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Form(
                key: _formProfilKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _namaController,
                      decoration: const InputDecoration(labelText: 'Nama', border: OutlineInputBorder()),
                      validator: (v) => (v == null || v.isEmpty) ? 'Nama wajib diisi' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
                      validator: (v) => (v == null || v.isEmpty) ? 'Email wajib diisi' : null,
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _savingProfil ? null : _simpanProfil,
                        child: Text(_savingProfil ? 'Menyimpan...' : 'Simpan Profil'),
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 48),
              Form(
                key: _formPasswordKey,
                child: Column(
                  children: [
                    TextFormField(
                      controller: _passwordLamaController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Password Lama', border: OutlineInputBorder()),
                      validator: (v) => (v == null || v.isEmpty) ? 'Password lama wajib diisi' : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordBaruController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Password Baru', border: OutlineInputBorder()),
                      validator: (v) => (v == null || v.length < 6) ? 'Minimal 6 karakter' : null,
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton(
                        onPressed: _savingPassword ? null : _simpanPassword,
                        child: Text(_savingPassword ? 'Menyimpan...' : 'Ubah Password'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      }

      @override
      void dispose() {
        _namaController.dispose();
        _emailController.dispose();
        _passwordLamaController.dispose();
        _passwordBaruController.dispose();
        super.dispose();
      }
    }

Dua Form terpisah dalam satu layar

Form profil dan form ganti password sengaja memakai `GlobalKey<FormState>` dan fungsi simpan yang terpisah. Kalau disatukan jadi satu `Form`, menekan "Simpan Profil" akan ikut memvalidasi field password lama/baru yang mungkin sengaja dikosongkan pengguna — padahal keduanya memang dua aksi independen di API (`PUT /profile` vs `PUT /profile/password`).

## 15UmkmListScreen & UmkmDetailScreen

`UmkmListScreen` adalah layar publik yang menampilkan seluruh UMKM terdaftar; `onTap` pada tiap item membuka `UmkmDetailScreen` — juga publik, menampilkan info UMKM beserta daftar produknya.

lib/screens/home/umkm/umkm_list_screen.dart

    import 'package:flutter/material.dart';

    import '../../../models/paginated_result.dart';
    import '../../../models/umkm_model.dart';
    import '../../../services/api_service.dart';
    import 'umkm_detail_screen.dart';

    class UmkmListScreen extends StatefulWidget {
      const UmkmListScreen({super.key});

      @override
      State<UmkmListScreen> createState() => _UmkmListScreenState();
    }

    class _UmkmListScreenState extends State<UmkmListScreen> {
      final _apiService = ApiService();
      late Future<PaginatedResult<Umkm>> _futureUmkm;

      @override
      void initState() {
        super.initState();
        _futureUmkm = _apiService.getUmkmList();
      }

      Future<void> _muatUlang() async {
        setState(() {
          _futureUmkm = _apiService.getUmkmList();
        });
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Semua UMKM')),
          body: FutureBuilder<PaginatedResult<Umkm>>(
            future: _futureUmkm,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('Gagal memuat data: ${snapshot.error}'),
                      const SizedBox(height: 12),
                      ElevatedButton(onPressed: _muatUlang, child: const Text('Coba Lagi')),
                    ],
                  ),
                );
              }

              final hasil = snapshot.data!;
              if (hasil.data.isEmpty) {
                return const Center(child: Text('Belum ada UMKM yang terdaftar'));
              }

              return RefreshIndicator(
                onRefresh: _muatUlang,
                child: ListView.builder(
                  itemCount: hasil.data.length,
                  itemBuilder: (context, i) {
                    final umkm = hasil.data[i];
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundImage: umkm.punyaFoto
                            ? NetworkImage(ApiService.fotoUrl(umkm.foto))
                            : null,
                        child: umkm.punyaFoto ? null : Text(umkm.nama[0]),
                      ),
                      title: Text(umkm.nama),
                      subtitle: Text(umkm.alamat),
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => UmkmDetailScreen(umkmId: umkm.id)),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        );
      }
    }

lib/screens/home/umkm/umkm_detail_screen.dart

    import 'package:flutter/material.dart';
    import '../../../models/umkm_model.dart';
    import '../../../models/produk_model.dart';
    import '../../../models/paginated_result.dart';
    import '../../../services/api_service.dart';

    class UmkmDetailScreen extends StatefulWidget {
      final int umkmId;
      const UmkmDetailScreen({super.key, required this.umkmId});
      @override
      State<UmkmDetailScreen> createState() => _UmkmDetailScreenState();
    }

    class _UmkmDetailScreenState extends State<UmkmDetailScreen> {
      final _apiService = ApiService();
      late Future<Umkm> _futureUmkm;
      late Future<PaginatedResult<Produk>> _futureProduk;

      @override
      void initState() {
        super.initState();
        _futureUmkm = _apiService.getUmkmDetail(widget.umkmId);
        _futureProduk = _apiService.getProdukByUmkm(widget.umkmId);
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Detail UMKM')),
          body: FutureBuilder<Umkm>(
            future: _futureUmkm,
            builder: (context, snapshotUmkm) {
              if (snapshotUmkm.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshotUmkm.hasError) {
                return Center(child: Text('Gagal memuat UMKM: ${snapshotUmkm.error}'));
              }
              final umkm = snapshotUmkm.data!;
              return ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (umkm.punyaFoto)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.network(ApiService.fotoUrl(umkm.foto), height: 180, width: double.infinity, fit: BoxFit.cover),
                    ),
                  const SizedBox(height: 12),
                  Text(umkm.nama, style: Theme.of(context).textTheme.titleLarge),
                  Text(umkm.alamat, style: TextStyle(color: Colors.grey[600])),
                  const SizedBox(height: 8),
                  Text(umkm.deskripsi),
                  const Divider(height: 32),
                  Text('Produk', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  FutureBuilder<PaginatedResult<Produk>>(
                    future: _futureProduk,
                    builder: (context, snapshotProduk) {
                      if (snapshotProduk.connectionState == ConnectionState.waiting) {
                        return const Padding(
                          padding: EdgeInsets.symmetric(vertical: 24),
                          child: Center(child: CircularProgressIndicator()),
                        );
                      }
                      if (snapshotProduk.hasError) {
                        return Text('Gagal memuat produk: ${snapshotProduk.error}');
                      }
                      final produkList = snapshotProduk.data!.data;
                      if (produkList.isEmpty) {
                        return const Text('Belum ada produk');
                      }
                      return Column(
                        children: produkList.map((p) => ListTile(
                          leading: p.foto.isNotEmpty
                              ? CircleAvatar(backgroundImage: NetworkImage(ApiService.fotoUrl(p.foto)))
                              : const CircleAvatar(child: Icon(Icons.inventory_2_outlined)),
                          title: Text(p.nama),
                          subtitle: Text('Rp${p.harga.toStringAsFixed(0)}'),
                        )).toList(),
                      );
                    },
                  ),
                ],
              );
            },
          ),
        );
      }
    }

## 16MyUmkmScreen: Lihat, Buat, Edit, Hapus UMKM Sendiri

Layar ini punya tiga kondisi yang lebih kaya dari sekadar loading/error/data: **belum punya UMKM** (tampilkan tombol "Buat UMKM"), **sudah punya** (tampilkan detail + tombol edit/hapus + daftar produknya).

lib/screens/home/umkm/myumkm_screen.dart

    import 'package:flutter/material.dart';
    import '../../../models/umkm_model.dart';
    import '../../../models/produk_model.dart';
    import '../../../models/paginated_result.dart';
    import '../../../services/api_service.dart';
    import 'umkm_form_screen.dart';
    import 'produk_form_screen.dart';

    class MyUmkmScreen extends StatefulWidget {
      const MyUmkmScreen({super.key});
      @override
      State<MyUmkmScreen> createState() => _MyUmkmScreenState();
    }

    class _MyUmkmScreenState extends State<MyUmkmScreen> {
      final _apiService = ApiService();
      late Future<Umkm?> _futureUmkm;
      int _produkKey = 0;

      @override
      void initState() {
        super.initState();
        _muatUmkm();
      }

      void _muatUmkm() {
        setState(() {
          _futureUmkm = _apiService.getUmkmSaya();
        });
      }

      void _muatUlangProduk() => setState(() => _produkKey++);

      Future<void> _bukaFormUmkm([Umkm? umkm]) async {
        final tersimpan = await Navigator.push<bool>(
          context,
          MaterialPageRoute(builder: (_) => UmkmFormScreen(umkm: umkm)),
        );
        if (tersimpan == true) _muatUmkm();
      }

      Future<void> _hapusUmkm(int id) async {
        try {
          await _apiService.hapusUmkm(id);
          _muatUmkm();
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        }
      }

      Future<void> _bukaFormProduk(int umkmId, [Produk? produk]) async {
        final tersimpan = await Navigator.push<bool>(
          context,
          MaterialPageRoute(builder: (_) => ProdukFormScreen(umkmId: umkmId, produk: produk)),
        );
        if (tersimpan == true) _muatUlangProduk();
      }

      Future<void> _hapusProduk(int id) async {
        try {
          await _apiService.hapusProduk(id);
          _muatUlangProduk();
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        }
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('UMKM Saya')),
          body: FutureBuilder<Umkm?>(
            future: _futureUmkm,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                return Center(child: Text('Gagal memuat: ${snapshot.error}'));
              }
              final umkm = snapshot.data;
              if (umkm == null) {
                return Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text('Anda belum memiliki UMKM'),
                      const SizedBox(height: 12),
                      ElevatedButton(onPressed: () => _bukaFormUmkm(), child: const Text('Buat UMKM')),
                    ],
                  ),
                );
              }
              return ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (umkm.punyaFoto)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.network(ApiService.fotoUrl(umkm.foto), height: 160, width: double.infinity, fit: BoxFit.cover),
                    ),
                  const SizedBox(height: 12),
                  Text(umkm.nama, style: Theme.of(context).textTheme.titleLarge),
                  Text(umkm.alamat, style: TextStyle(color: Colors.grey[600])),
                  Text(umkm.deskripsi),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: OutlinedButton(onPressed: () => _bukaFormUmkm(umkm), child: const Text('Edit UMKM'))),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton(
                          style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                          onPressed: () => _hapusUmkm(umkm.id),
                          child: const Text('Hapus UMKM'),
                        ),
                      ),
                    ],
                  ),
                  const Divider(height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Produk', style: Theme.of(context).textTheme.titleMedium),
                      TextButton.icon(
                        onPressed: () => _bukaFormProduk(umkm.id),
                        icon: const Icon(Icons.add),
                        label: const Text('Tambah'),
                      ),
                    ],
                  ),
                  _DaftarProduk(
                    key: ValueKey(_produkKey),
                    umkmId: umkm.id,
                    apiService: _apiService,
                    onEdit: (p) => _bukaFormProduk(umkm.id, p),
                    onHapus: _hapusProduk,
                  ),
                ],
              );
            },
          ),
        );
      }
    }

    /// Widget terpisah dengan state sendiri untuk daftar produk, supaya punya
    /// siklus fetch-sekali-di-initState yang independen dari FutureBuilder UMKM
    /// di atasnya (lihat catatan di bawah).
    class _DaftarProduk extends StatefulWidget {
      final int umkmId;
      final ApiService apiService;
      final void Function(Produk) onEdit;
      final void Function(int id) onHapus;

      const _DaftarProduk({
        super.key,
        required this.umkmId,
        required this.apiService,
        required this.onEdit,
        required this.onHapus,
      });

      @override
      State<_DaftarProduk> createState() => _DaftarProdukState();
    }

    class _DaftarProdukState extends State<_DaftarProduk> {
      late Future<PaginatedResult<Produk>> _futureProduk;

      @override
      void initState() {
        super.initState();
        _futureProduk = widget.apiService.getProdukByUmkm(widget.umkmId);
      }

      @override
      Widget build(BuildContext context) {
        return FutureBuilder<PaginatedResult<Produk>>(
          future: _futureProduk,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            if (snapshot.hasError) {
              return Text('Gagal memuat produk: ${snapshot.error}');
            }
            final produkList = snapshot.data!.data;
            if (produkList.isEmpty) {
              return const Padding(padding: EdgeInsets.symmetric(vertical: 12), child: Text('Belum ada produk'));
            }
            return Column(
              children: produkList.map((p) => ListTile(
                leading: p.foto.isNotEmpty
                    ? CircleAvatar(backgroundImage: NetworkImage(ApiService.fotoUrl(p.foto)))
                    : const CircleAvatar(child: Icon(Icons.inventory_2_outlined)),
                title: Text(p.nama),
                subtitle: Text('Rp${p.harga.toStringAsFixed(0)}'),
                trailing: PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'edit') widget.onEdit(p);
                    if (value == 'hapus') widget.onHapus(p.id);
                  },
                  itemBuilder: (_) => const [
                    PopupMenuItem(value: 'edit', child: Text('Edit')),
                    PopupMenuItem(value: 'hapus', child: Text('Hapus')),
                  ],
                ),
              )).toList(),
            );
          },
        );
      }
    }

Jangan pakai setState(() =\> ...) berbentuk assignment untuk Future

`_muatUmkm()` sengaja ditulis dengan **blok** `setState(() { _futureUmkm = ...; });`, bukan bentuk singkat `setState(() => _futureUmkm = _apiService.getUmkmSaya());`. Alasannya teknis tapi penting: di Dart, nilai dari ekspresi assignment (`a = b`) adalah nilai `b` itu sendiri. Kalau closure ditulis dengan tanda panah `=>`, closure tersebut otomatis **mengembalikan** hasil assignment-nya — dalam kasus ini sebuah `Future<Umkm?>`, karena `getUmkmSaya()` adalah fungsi `async`. Flutter sengaja melempar error `"setState() callback argument returned a Future"` begitu mendeteksi ini, karena khawatir pemanggilnya bermaksud menunggu proses asinkron di dalam `setState` (yang tidak didukung). Memakai blok `{ }` membuat closure mengembalikan `void`, menghilangkan masalah ini sepenuhnya. Pola `setState(() => _variabel = nilai)` tetap aman dipakai selama nilai di kanan **bukan** hasil pemanggilan fungsi `async` (lihat `_muatUlangProduk()` di bawah, yang aman karena `_produkKey++` bertipe `int`).

Kenapa daftar produk jadi widget terpisah, bukan FutureBuilder langsung di dalam build()?

Aturan "`Future` dibuat sekali di `initState`, bukan di `build()`" mencegah request berulang setiap rebuild. Di sini ada masalah baru: produk perlu di-*refresh* setelah ditambah/diubah/dihapus, padahal `MyUmkmScreen` sendiri juga rebuild karena alasan lain (mis. `setState` dari UMKM). Solusinya **bukan** memanggil ulang `getProdukByUmkm` langsung di `build()` (melanggar aturan di atas), melainkan membungkus daftar produk dalam widget `StatefulWidget` terpisah (`_DaftarProduk`) yang fetch sekali di `initState`-nya sendiri, lalu memberinya `key: ValueKey(_produkKey)`. Mengganti nilai `key` memberi tahu Flutter untuk **membuang widget lama dan membuat yang baru dari nol** — termasuk memanggil `initState` lagi — persis saat dibutuhkan, tidak lebih sering dari itu.

## 17Form UMKM & Form Produk (Buat/Ubah + Upload Foto)

Kedua form berikut dipakai untuk **dua mode sekaligus**: `umkm`/`produk` bernilai `null` berarti mode "buat baru", terisi berarti mode "edit" (form terisi otomatis dari data yang ada). Memilih foto memakai `image_picker`, lalu path file lokalnya dikirim ke `ApiService.simpanUmkm`/`simpanProduk`.

Foto wajib berformat JPG/JPEG/PNG

`image_picker` membuka galeri bawaan device, yang bisa saja berisi foto HEIC (default iPhone), WebP, atau format lain di luar yang didukung — plugin ini sendiri tidak punya opsi untuk membatasi jenis file yang boleh dipilih dari galeri. Karena itu, validasi dilakukan manual setelah foto dipilih: cek ekstensi `file.path`, dan tolak dengan `SnackBar` kalau bukan `.jpg`/`.jpeg`/`.png` — foto tidak ikut disimpan ke `_fotoBaru` kalau gagal validasi, sehingga tombol "Simpan" tetap memakai foto lama (mode edit) atau tanpa foto (mode buat baru).

lib/screens/home/umkm/umkm_form_screen.dart

    import 'dart:io';
    import 'package:flutter/material.dart';
    import 'package:image_picker/image_picker.dart';
    import '../../../models/umkm_model.dart';
    import '../../../services/api_service.dart';

    class UmkmFormScreen extends StatefulWidget {
      final Umkm? umkm; // null = membuat baru, terisi = mode edit
      const UmkmFormScreen({super.key, this.umkm});
      @override
      State<UmkmFormScreen> createState() => _UmkmFormScreenState();
    }

    class _UmkmFormScreenState extends State<UmkmFormScreen> {
      final _formKey = GlobalKey<FormState>();
      final _apiService = ApiService();
      late final _namaController = TextEditingController(text: widget.umkm?.nama ?? '');
      late final _deskripsiController = TextEditingController(text: widget.umkm?.deskripsi ?? '');
      late final _alamatController = TextEditingController(text: widget.umkm?.alamat ?? '');
      XFile? _fotoBaru;
      bool _saving = false;

      Future<void> _pilihFoto() async {
        final file = await ImagePicker().pickImage(source: ImageSource.gallery, imageQuality: 80);
        if (file == null) return;
        final ext = file.path.toLowerCase();
        if (!ext.endsWith('.jpg') && !ext.endsWith('.jpeg') && !ext.endsWith('.png')) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Foto harus berformat JPG/JPEG/PNG')),
          );
          return;
        }
        setState(() => _fotoBaru = file);
      }

      Future<void> _simpan() async {
        if (!_formKey.currentState!.validate()) return;
        setState(() => _saving = true);
        try {
          await _apiService.simpanUmkm(
            id: widget.umkm?.id,
            nama: _namaController.text,
            deskripsi: _deskripsiController.text,
            alamat: _alamatController.text,
            fotoPath: _fotoBaru?.path,
          );
          if (!mounted) return;
          Navigator.pop(context, true);
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        } finally {
          if (mounted) setState(() => _saving = false);
        }
      }

      @override
      Widget build(BuildContext context) {
        final sedangEdit = widget.umkm != null;
        return Scaffold(
          appBar: AppBar(title: Text(sedangEdit ? 'Edit UMKM' : 'Buat UMKM')),
          body: Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                GestureDetector(
                  onTap: _pilihFoto,
                  child: _fotoBaru != null
                      ? ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.file(File(_fotoBaru!.path), height: 160, fit: BoxFit.cover))
                      : (sedangEdit && widget.umkm!.punyaFoto
                          ? ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.network(ApiService.fotoUrl(widget.umkm!.foto), height: 160, fit: BoxFit.cover))
                          : Container(
                              height: 160,
                              decoration: BoxDecoration(color: Colors.grey[200], borderRadius: BorderRadius.circular(12)),
                              child: const Center(child: Icon(Icons.add_a_photo_outlined, size: 32)),
                            )),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _namaController,
                  decoration: const InputDecoration(labelText: 'Nama UMKM', border: OutlineInputBorder()),
                  validator: (v) => (v == null || v.isEmpty) ? 'Nama wajib diisi' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _deskripsiController,
                  maxLines: 3,
                  decoration: const InputDecoration(labelText: 'Deskripsi', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _alamatController,
                  decoration: const InputDecoration(labelText: 'Alamat', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _saving ? null : _simpan,
                    child: Text(_saving ? 'Menyimpan...' : 'Simpan'),
                  ),
                ),
              ],
            ),
          ),
        );
      }

      @override
      void dispose() {
        _namaController.dispose();
        _deskripsiController.dispose();
        _alamatController.dispose();
        super.dispose();
      }
    }

lib/screens/home/umkm/produk_form_screen.dart

    import 'dart:io';
    import 'package:flutter/material.dart';
    import 'package:image_picker/image_picker.dart';
    import '../../../models/produk_model.dart';
    import '../../../services/api_service.dart';

    class ProdukFormScreen extends StatefulWidget {
      final int umkmId;
      final Produk? produk; // null = tambah baru, terisi = mode edit
      const ProdukFormScreen({super.key, required this.umkmId, this.produk});
      @override
      State<ProdukFormScreen> createState() => _ProdukFormScreenState();
    }

    class _ProdukFormScreenState extends State<ProdukFormScreen> {
      final _formKey = GlobalKey<FormState>();
      final _apiService = ApiService();
      late final _namaController = TextEditingController(text: widget.produk?.nama ?? '');
      late final _hargaController = TextEditingController(text: widget.produk?.harga.toStringAsFixed(0) ?? '');
      late final _deskripsiController = TextEditingController(text: widget.produk?.deskripsi ?? '');
      XFile? _fotoBaru;
      bool _saving = false;

      Future<void> _pilihFoto() async {
        final file = await ImagePicker().pickImage(source: ImageSource.gallery, imageQuality: 80);
        if (file == null) return;
        final ext = file.path.toLowerCase();
        if (!ext.endsWith('.jpg') && !ext.endsWith('.jpeg') && !ext.endsWith('.png')) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Foto harus berformat JPG/JPEG/PNG')),
          );
          return;
        }
        setState(() => _fotoBaru = file);
      }

      Future<void> _simpan() async {
        if (!_formKey.currentState!.validate()) return;
        setState(() => _saving = true);
        try {
          await _apiService.simpanProduk(
            id: widget.produk?.id,
            umkmId: widget.umkmId,
            nama: _namaController.text,
            harga: double.parse(_hargaController.text),
            deskripsi: _deskripsiController.text,
            fotoPath: _fotoBaru?.path,
          );
          if (!mounted) return;
          Navigator.pop(context, true);
        } on ApiException catch (e) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
        } finally {
          if (mounted) setState(() => _saving = false);
        }
      }

      @override
      Widget build(BuildContext context) {
        final sedangEdit = widget.produk != null;
        return Scaffold(
          appBar: AppBar(title: Text(sedangEdit ? 'Edit Produk' : 'Tambah Produk')),
          body: Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                GestureDetector(
                  onTap: _pilihFoto,
                  child: _fotoBaru != null
                      ? ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.file(File(_fotoBaru!.path), height: 140, fit: BoxFit.cover))
                      : (sedangEdit && widget.produk!.foto.isNotEmpty
                          ? ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.network(ApiService.fotoUrl(widget.produk!.foto), height: 140, fit: BoxFit.cover))
                          : Container(
                              height: 140,
                              decoration: BoxDecoration(color: Colors.grey[200], borderRadius: BorderRadius.circular(12)),
                              child: const Center(child: Icon(Icons.add_a_photo_outlined, size: 32)),
                            )),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _namaController,
                  decoration: const InputDecoration(labelText: 'Nama Produk', border: OutlineInputBorder()),
                  validator: (v) => (v == null || v.isEmpty) ? 'Nama wajib diisi' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _hargaController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Harga', border: OutlineInputBorder()),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Harga wajib diisi';
                    if (double.tryParse(v) == null) return 'Harga harus berupa angka';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _deskripsiController,
                  maxLines: 3,
                  decoration: const InputDecoration(labelText: 'Deskripsi', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _saving ? null : _simpan,
                    child: Text(_saving ? 'Menyimpan...' : 'Simpan'),
                  ),
                ),
              ],
            ),
          ),
        );
      }

      @override
      void dispose() {
        _namaController.dispose();
        _hargaController.dispose();
        _deskripsiController.dispose();
        super.dispose();
      }
    }

Navigator.pop(context, true) — kenapa membawa nilai?

Kedua form memanggil `Navigator.pop(context, true)` setelah berhasil simpan, bukan `Navigator.pop(context)` polos. Nilai `true` ini diterima layar pemanggil lewat `await Navigator.push<bool>(...)` di `MyUmkmScreen` — dipakai sebagai sinyal "data berubah, silakan muat ulang" tanpa perlu `Provider`/state management tambahan. Kalau pengguna menekan tombol back tanpa menyimpan, `pop` otomatis membawa `null` sehingga `MyUmkmScreen` tahu tidak perlu memuat ulang apa-apa.

## 18Menjalankan Aplikasi

Urutan menyalakan proyek selalu sama: backend dulu, baru Flutter.

terminal 1 — backend

    cd umkm-api
    go run ./cmd/api

terminal 2 — aplikasi Flutter

    cd umkm-app
    flutter run

Pastikan `ApiService.baseUrl` sesuai jenis perangkat yang dipakai (Pertemuan 6 Bagian 07):

| Target | baseUrl |
|----|----|
| Android Emulator | `http://10.0.2.2:8080/api` (default di kode ini) |
| iOS Simulator | `http://localhost:8080/api` |
| HP fisik (Android/iOS) | `http://<IP-lokal-komputer>:8080/api`, mis. `http://192.168.1.5:8080/api` — HP dan komputer harus satu jaringan Wi-Fi |

✓ Urutan uji coba yang disarankan

Register akun baru → login → buat UMKM (dengan/tanpa foto) → tambah beberapa produk → buka tab "Semua UMKM" dari akun lain untuk memastikan data publik ikut tampil → edit salah satu produk → hapus salah satu produk → logout → pastikan kembali ke layar login dan tidak bisa menekan back ke Home.

## 19Troubleshooting Cepat

Kalau menemui `401 Unauthorized` di endpoint mana pun yang butuh login, atau error lain yang tidak jelas penyebabnya, langkah diagnosisnya sudah dibahas lengkap di Pertemuan 7 Bagian 15 — ringkasannya:

1.  Pastikan token benar-benar tersimpan setelah login (`print` di `ApiService.login()`).
2.  Pastikan setiap method baru yang kamu tambahkan sendiri ikut menyertakan `await _authHeaders()` / `.headers.addAll(await _authHeaders())`.
3.  Jangan pernah menimpa header `Content-Type` secara manual pada `http.MultipartRequest` — biarkan diatur otomatis.
4.  Token kedaluwarsa (24 jam) atau backend direstart dengan `JWT_SECRET` berbeda → logout lalu login ulang.
5.  Uji endpoint langsung lewat Swagger/`curl` dulu untuk memastikan masalahnya di Flutter, bukan di server.

Lihat [Pertemuan 7 Bagian 15](pertemuan-07.html#s15) untuk penjelasan lengkap beserta contoh kode salah/benar.

## 20Latihan

1.  Tambahkan `RefreshIndicator` (tarik-untuk-refresh) pada `MyUmkmScreen`, memanggil ulang `_muatUmkm()`.
2.  Tambahkan fitur pencarian: `TextField` di `UmkmListScreen` yang memanggil ulang `getUmkmList(q: ...)`.
3.  Tambahkan konfirmasi (`showDialog` dengan tombol "Batal"/"Hapus") sebelum benar-benar memanggil `_hapusUmkm`/`_hapusProduk`.
4.  **Tantangan:** buat satu fungsi pembantu di `ApiService` yang membungkus semua pemanggilan `http`, menangkap status `401` secara seragam — hapus token dari `TokenStorage` lalu lempar `ApiException` khusus yang ditangkap di level atas untuk otomatis mengarahkan ke `/login`, tanpa duplikasi pengecekan di setiap layar.

Dengan panduan ini, proyek `umkm-app` bisa dibangun ulang dari nol kapan pun dibutuhkan — satu alur lengkap dari `flutter create` kosong sampai aplikasi yang benar-benar login, menyimpan sesi, dan mengelola data milik sendiri termasuk foto, tersambung ke backend Golang + PostgreSQL. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
