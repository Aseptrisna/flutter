<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Materi Pemula · Integrasi Flutter + Golang

# Integrasi Penuh Flutter ke API UMKM: Auth, Token, dan Upload Foto

Menyambungkan seluruh layar aplikasi — register, login, profil, kelola UMKM milik sendiri beserta produknya — ke API Golang yang dibangun pada Pertemuan 4, mengikuti struktur project referensi `umkm_app`.

Login + Token→
ApiService Lengkap→
CRUD UMKM/Produk→
Upload Foto

## 01Dari Latihan ke Integrasi Penuh

Pertemuan 6 sudah membangun fondasi: `Umkm`/`Produk` model, `PaginatedResult<T>`, `ApiService` dengan tiga method baca-saja (`getUmkmList`, `getUmkmDetail`, `getProdukByUmkm`), dan pola `FutureBuilder`/`setState` untuk tiga kondisi wajib (loading/error/data). Pertemuan ini melengkapi sisi yang belum disentuh — semuanya endpoint yang **butuh login** (lihat kontrak lengkap di Pertemuan 4 Bagian 9.1):

| Yang ditambahkan | Endpoint API yang dipakai |
|----|----|
| Registrasi & login sungguhan (bukan dummy) | `POST /auth/register`, `POST /auth/login` |
| Menyimpan token JWT agar sesi tetap login setelah app ditutup | — (disimpan lokal di device) |
| Melihat & mengubah profil, ubah password | `GET/PUT /profile`, `PUT /profile/password` |
| Melihat, membuat, mengubah, menghapus UMKM milik sendiri | `GET /umkm/saya`, `POST/PUT/DELETE /umkm` |
| Mengelola produk pada UMKM sendiri, termasuk upload foto | `POST /umkm/{id}/produk`, `PUT/DELETE /produk/{id}` |

Ada satu konsep benar-benar baru dibanding Pertemuan 6: **mengirim data** ke server (bukan cuma membaca), yang berarti mengirim header `Authorization: Bearer <token>` di setiap request yang butuh login, dan mengirim *file* (foto) lewat `multipart/form-data` — bukan `jsonEncode` biasa.

## 02Menambahkan Dependency & Izin Baru

Dua package baru di luar `http` yang sudah dipasang Pertemuan 6: satu untuk menyimpan token secara aman, satu untuk memilih foto dari galeri/kamera.

terminal

    flutter pub add flutter_secure_storage
    flutter pub add image_picker

| Platform | Yang perlu ditambahkan |
|----|----|
| Android — testing ke backend lokal (`http://`, bukan `https://`) | Tambahkan `android:usesCleartextTraffic="true"` pada tag `<application>` di `android/app/src/main/AndroidManifest.xml`. Sejak Android 9, trafik HTTP polos diblokir secara default — tanpa ini, `http.post` ke `10.0.2.2:8080` akan gagal diam-diam dengan `SocketException`. |
| iOS — izin galeri foto | Tambahkan key `NSPhotoLibraryUsageDescription` di `ios/Runner/Info.plist` dengan deskripsi singkat (mis. "Dipakai untuk memilih foto UMKM/produk"), wajib ada atau app crash saat `image_picker` dipanggil. |

image_picker tidak butuh permission_handler manual

Plugin `image_picker` sudah menangani sendiri permintaan izin runtime untuk galeri/kamera di Android maupun iOS. Cukup pastikan deklarasi di atas ada; jangan tambahkan `permission_handler` kecuali benar-benar butuh mengecek status izin secara manual di luar alur pilih-foto.

## 03Menyimpan Token Login

Setelah login berhasil, server mengembalikan JWT token (lihat Pertemuan 4 Bagian 10.9 & 10.5). Token ini harus disimpan secara **lokal di device** agar pengguna tidak perlu login ulang setiap membuka aplikasi, dan harus disimpan dengan aman — bukan di `SharedPreferences` biasa yang tidak terenkripsi.

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

Kenapa flutter_secure_storage, bukan shared_preferences?

`shared_preferences` menyimpan data sebagai file XML/plist biasa yang bisa dibaca siapa pun dengan akses ke penyimpanan device (device yang di-root/jailbreak, atau lewat backup file). `flutter_secure_storage` memakai Keystore (Android) / Keychain (iOS) — penyimpanan terenkripsi di level sistem operasi, tempat yang semestinya untuk data sensitif seperti token autentikasi.

## 04Model User & Memperluas ApiService untuk Auth

Tambahkan satu model baru untuk merepresentasikan data akun, mengikuti kontrak `GET /profile` dan field `user` pada respons login (Pertemuan 4 Bagian 9.1 & 10.8).

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

Lalu tambahkan method-method berikut ke dalam class `ApiService` yang sudah dibuat di Pertemuan 6 (di bawah `getProdukByUmkm`, sebelum kurung kurawal penutup class):

lib/services/api_service.dart — tambahan import

    import '../models/user_model.dart';
    import 'token_storage.dart';

lib/services/api_service.dart — tambahan method

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

login() tidak mengembalikan token ke pemanggil

Perhatikan `login()` bertipe `Future<void>`, bukan `Future<String>` — token langsung disimpan ke `TokenStorage` di dalam method itu sendiri. Layar `LoginScreen` (Bagian 08) tidak perlu tahu atau menyimpan token secara manual; ia cukup tahu "login berhasil atau gagal" (lewat *throw*/tidaknya `ApiException`), lalu pindah halaman. Menyimpan token di satu tempat (di dalam `ApiService`) mencegah lupa menyimpannya di salah satu alur.

## 05ApiService: Mengirim Foto Lewat Multipart

Endpoint `POST/PUT /umkm` dan `POST /umkm/{id}/produk`, `PUT /produk/{id}` menerima `multipart/form-data` (Pertemuan 4 Bagian 10.8), bukan JSON — karena ada file foto yang ikut dikirim. Di Dart, ini memakai `http.MultipartRequest`, bukan `http.post` biasa.

lib/services/api_service.dart — tambahan method UMKM & Produk

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

Satu fungsi simpanUmkm untuk create DAN update — kenapa?

Perbedaan `POST /umkm` (buat baru) dan `PUT /umkm/{id}` (ubah) di sisi Golang cuma soal method HTTP dan ada/tidaknya `{id}` di path (Pertemuan 4 Bagian 10.8) — field yang dikirim persis sama. Menyatukannya jadi satu method dengan parameter opsional `id` menghindari duplikasi kode di `ApiService`, dan di sisi UI nanti satu `UmkmFormScreen` (Bagian 13) juga dipakai untuk kedua mode (buat/edit) dengan pola yang sama.

fotoPath null berarti "tidak ganti foto", bukan "hapus foto"

Sama seperti di backend (Pertemuan 4 Bagian 10.5: `fotoBaru != "" { umkm.Foto = fotoBaru }`) — kalau `fotoPath` tidak dikirim sama sekali, field `foto` yang sudah tersimpan di database tidak diubah. Ini dipakai saat mode edit dan pengguna tidak mengganti foto: cukup tidak memanggil `request.files.add(...)`.

### ApiService Lengkap — Setelah Bagian 04 & 05

Supaya tidak perlu menyusun sendiri potongan-potongan di atas, berikut `lib/services/api_service.dart` secara **utuh** — gabungan base dari Pertemuan 6 (Bagian 06) ditambah semua method auth (Bagian 04) dan method UMKM/Produk multipart (Bagian 05). Timpa seluruh isi berkas `api_service.dart` milikmu dengan ini:

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

✓ Diverifikasi

Berkas ini sudah dicoba `flutter analyze` dalam project nyata bersama seluruh model (`umkm_model.dart`, `produk_model.dart`, `paginated_result.dart`, `user_model.dart`) dan `token_storage.dart` dari tutorial ini — hasilnya `No issues found!`, tidak ada error maupun warning.

## 06Memperbaiki Routing di main.dart

Sebelum menyambungkan layar ke API sungguhan, ada satu bug di `main.dart` starter project yang perlu diperbaiki lebih dulu: route `/login` dan `/register` tertukar arahnya ke class yang salah.

lib/main.dart — SEBELUM (keliru)

    routes: {
      '/': (context) => const SplashScreen(),
      '/register': (context) => const LoginScreen(),   // <- tertukar
      '/login': (context) => const RegisterPage(),      // <- tertukar
    },

lib/main.dart — SESUDAH

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

Kenapa bug ini baru terasa sekarang?

Selama `LoginScreen`/`RegisterPage` masih dummy (Bagian 08 sebelum diperbaiki), tertukarnya nama route tidak kelihatan janggal karena isinya sama-sama cuma `SnackBar`. Begitu alur login sungguhan menentukan ke mana pengguna diarahkan setelah sukses (`/home`), route yang salah arah akan langsung terasa sebagai bug nyata — inilah pentingnya menamai route sesuai isinya sejak awal, bukan menebak dari konteks pemakaian.

## 07SplashScreen: Memeriksa Token Tersimpan

Tugas `SplashScreen` berubah: bukan sekadar jeda 3 detik lalu ke halaman login, tapi memeriksa **apakah pengguna sudah pernah login sebelumnya** (ada token tersimpan) — kalau ada, langsung masuk ke `HomeScreen` tanpa perlu login ulang.

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

Antara `await TokenStorage.ambil()` dimulai dan selesai, pengguna bisa saja sudah menutup aplikasi atau widget ini sudah dilepas dari tree. Memanggil `Navigator.pushReplacementNamed` pada `BuildContext` yang sudah tidak `mounted` akan melempar error. Aturan ini berlaku di **setiap** pemakaian `context` setelah sebuah `await` — akan terus berulang di Bagian 08, 12, dan 13.

## 08LoginScreen & RegisterScreen Tersambung ke API

Dua perubahan di kedua layar: fungsi `_proses...()` memanggil `ApiService` sungguhan (bukan sekadar validasi form lalu `SnackBar`), dan ditambahkan variabel `_loading` supaya tombol submit menampilkan indikator progres serta tidak bisa ditekan dua kali selama request berjalan.

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

## 09HomeScreen: Navigasi Bawah Tiga Tab

Setelah login, pengguna mendarat di `HomeScreen` yang membagi aplikasi jadi tiga tab lewat `NavigationBar` (Material 3) — "Semua UMKM" (dari Pertemuan 6, publik), "UMKM Saya" (baru, butuh login), dan "Profil" (baru, butuh login).

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

`IndexedStack` membangun ketiga halaman sekaligus di memori dan hanya menampilkan satu, alih-alih membongkar-pasang widget setiap pindah tab. Efeknya: state tiap tab (misalnya posisi scroll, atau `Future` yang sedang berjalan di `MyUmkmScreen`) tidak hilang ketika berpindah ke tab lain lalu kembali lagi — pengalaman yang diharapkan dari navigasi bawah gaya aplikasi mobile pada umumnya.

## 10ProfileScreen & UpdateProfileScreen

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

Form profil dan form ganti password sengaja memakai `GlobalKey<FormState>` dan fungsi simpan yang terpisah (`_formProfilKey`/`_simpanProfil` vs `_formPasswordKey`/`_simpanPassword`). Kalau disatukan jadi satu `Form`, menekan "Simpan Profil" akan ikut memvalidasi field password lama/baru yang mungkin sengaja dikosongkan pengguna (karena tidak sedang ingin ganti password) — padahal keduanya memang dua aksi independen di API (`PUT /profile` vs `PUT /profile/password`, Pertemuan 4 Bagian 9.1).

## 11Melihat Detail UMKM Milik Orang Lain

Di Pertemuan 6, `onTap` pada `UmkmListScreen` masih berupa komentar kosong. Sekarang hubungkan ke layar detail sungguhan — ini layar **publik**, tidak butuh token, memakai `getUmkmDetail` dan `getProdukByUmkm` yang sudah ada sejak Pertemuan 6.

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

`umkm_list_screen.dart` yang dibuat di Pertemuan 6 perlu diubah: komentar kosong pada `onTap` diganti navigasi sungguhan ke `UmkmDetailScreen`, dan ditambah satu import baru. Berikut berkasnya secara **utuh** setelah perubahan — timpa seluruh isi `umkm_list_screen.dart` milikmu dengan ini (baris import baru dan `onTap` yang berubah ditandai lewat teks di bawah kode):

lib/screens/home/umkm/umkm_list_screen.dart — LENGKAP (update dari Pertemuan 6)

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

Dua perubahan dari versi Pertemuan 6: (1) tambahan `import 'umkm_detail_screen.dart';` di baris import, dan (2) isi `onTap` yang tadinya komentar kosong sekarang memanggil `Navigator.push` menuju `UmkmDetailScreen(umkmId: umkm.id)`.

## 12MyUmkmScreen: Lihat, Buat, Edit, Hapus UMKM Sendiri

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

Pertemuan 6 mengajarkan "`Future` dibuat sekali di `initState`, bukan di `build()`" — supaya tidak memicu request berulang setiap rebuild. Di sini ada masalah baru: produk perlu di-*refresh* setelah ditambah/diubah/dihapus, padahal `MyUmkmScreen` sendiri juga rebuild karena alasan lain (mis. `setState` dari UMKM). Solusinya **bukan** memanggil ulang `getProdukByUmkm` langsung di `build()` (melanggar aturan di atas), melainkan membungkus daftar produk dalam widget `StatefulWidget` terpisah (`_DaftarProduk`) yang fetch sekali di `initState`-nya sendiri, lalu memberinya `key: ValueKey(_produkKey)`. Mengganti nilai `key` memberi tahu Flutter untuk **membuang widget lama dan membuat yang baru dari nol** — termasuk memanggil `initState` lagi — persis saat dibutuhkan (setelah produk berubah), tidak lebih sering dari itu.

## 13Form UMKM & Form Produk (Buat/Ubah + Upload Foto)

Kedua form berikut dipakai untuk **dua mode sekaligus**: `umkm`/`produk` bernilai `null` berarti mode "buat baru", terisi berarti mode "edit" (form terisi otomatis dari data yang ada). Memilih foto memakai `image_picker`, lalu path file lokalnya dikirim ke `ApiService.simpanUmkm`/`simpanProduk` (Bagian 05).

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

Kedua form memanggil `Navigator.pop(context, true)` setelah berhasil simpan, bukan `Navigator.pop(context)` polos. Nilai `true` ini diterima layar pemanggil lewat `await Navigator.push<bool>(...)` di `MyUmkmScreen` (Bagian 12) — dipakai sebagai sinyal "data berubah, silakan muat ulang" tanpa perlu `Provider`/state management tambahan. Kalau pengguna menekan tombol back tanpa menyimpan, `pop` otomatis membawa `null` sehingga `MyUmkmScreen` tahu tidak perlu memuat ulang apa-apa.

## 14Logout

Logout sudah terpasang di `ProfileScreen` (Bagian 10): memanggil `ApiService().logout()` (yang menghapus token dari `TokenStorage`, Bagian 04), lalu `Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false)`.

pushNamedAndRemoveUntil, bukan pushReplacementNamed

`pushReplacementNamed` hanya mengganti satu halaman teratas, sehingga riwayat navigasi (`HomeScreen`, tab-tab sebelumnya) masih ada di *back stack* — menekan tombol back dari `LoginScreen` setelah logout bisa saja balik ke `HomeScreen` dengan state lama. `pushNamedAndRemoveUntil(..., (route) => false)` membuang **seluruh** riwayat navigasi sebelumnya, memastikan tombol back dari layar login tidak mengarah ke halaman yang seharusnya sudah tidak bisa diakses tanpa login.

## 15Troubleshooting — Error 401 Unauthorized

Backend Pertemuan 4 sudah diuji ulang end-to-end (register → login → panggil endpoint ber-token, termasuk `POST /api/umkm` yang pakai `multipart/form-data`) dan token dari `/api/auth/login` **berfungsi normal** di semua endpoint yang butuh login. Jadi kalau aplikasi Flutter-mu dapat `401`, penyebabnya hampir selalu ada di kode klien, bukan di server. Masalahnya, pesan error dari server sengaja dibuat generik (`"token tidak valid"` untuk hampir semua kasus — token rusak, salah secret, maupun kedaluwarsa, semuanya dibalas pesan yang sama) supaya penyerang tidak bisa menebak alasan penolakan, sehingga **pesan errornya sendiri tidak cukup untuk mendiagnosis**. Ikuti urutan pengecekan di bawah.

#### Langkah 1 — Pastikan token memang tersimpan setelah login

Tambahkan `print('token tersimpan: $token')` sesaat setelah `TokenStorage.simpan(token)` dipanggil di `ApiService.login()` (Bagian 04), lalu login ulang dan cek konsol. Token harus berupa string panjang berformat `xxxxx.yyyyy.zzzzz` (tiga bagian dipisah titik). Kalau kosong/null, masalahnya ada di alur login/penyimpanan — bukan di endpoint yang 401.

#### Langkah 2 — Pastikan header Authorization benar-benar terkirim

Penyebab paling sering: method `ApiService` yang baru ditambahkan (misalnya endpoint custom di luar yang sudah ada di tutorial) **lupa menyertakan `await _authHeaders()`** pada \`headers:\`. Contoh kode yang salah vs benar:

salah — tanpa header Authorization

    final response = await http.get(Uri.parse('$baseUrl/umkm/saya'));
    // server menolak dengan 401 "token tidak ditemukan", karena tidak ada header sama sekali

benar — ikut sertakan \_authHeaders()

    final response = await http.get(Uri.parse('$baseUrl/umkm/saya'), headers: await _authHeaders());

Untuk request `multipart/form-data` (buat/ubah UMKM dan produk), polanya beda — header ditambahkan lewat `.headers.addAll(...)`, **bukan** lewat parameter `headers:` biasa (karena `http.MultipartRequest` tidak punya parameter itu):

pola yang benar untuk multipart (Bagian 05)

    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/umkm'))
      ..headers.addAll(await _authHeaders())
      ..fields['nama'] = nama;

Kalau butuh memastikan header memang terkirim tanpa menebak-nebak, tambahkan `print(request.headers)` (untuk multipart) atau `print(await _authHeaders())` sebelum request dikirim, lalu cek apakah formatnya persis `Bearer <token>` — bukan `bearer` huruf kecil, dan bukan tanpa spasi setelah `Bearer`. Server membaca header ini *case-sensitive*, jadi `"bearer eyJ..."` akan dianggap sama dengan "tidak ada token sama sekali".

#### Langkah 3 — Jangan timpa header Content-Type pada multipart

Kalau endpoint yang 401 justru endpoint upload foto (`POST /api/umkm` atau `POST /api/umkm/{id}/produk`), cek apakah ada baris yang menambahkan `'Content-Type': 'multipart/form-data'` secara manual ke `request.headers`. **Jangan pernah lakukan ini** — `http.MultipartRequest` sudah otomatis membuat header `Content-Type` lengkap dengan `boundary` acak yang dipakai server untuk memisahkan tiap field/file. Menimpanya secara manual membuat boundary hilang, sehingga server gagal mem-parse body (biasanya muncul sebagai `400 "form tidak valid"`, tapi pada beberapa kasus request bisa gagal lebih awal dan terlihat seperti token tidak terkirim). Solusi: cukup gunakan `..headers.addAll(await _authHeaders())` saja, biarkan `Content-Type` diatur otomatis oleh package `http`.

#### Langkah 4 — Token kedaluwarsa atau server di-restart dengan JWT_SECRET baru

Token berlaku **24 jam** sejak login (lihat `generateToken` di `AuthService`, Pertemuan 4 Bagian 10.6) — token lama otomatis ditolak setelah itu. Selain itu, kalau backend direstart dengan `JWT_SECRET` yang berbeda dari saat token diterbitkan (misalnya `.env` diedit atau API dijalankan dari komputer lain dengan `.env` yang beda), semua token lama otomatis tidak valid walau belum 24 jam. Perbaikannya: logout lalu login ulang untuk mendapat token baru. Kalau ini sering terjadi padahal baru saja login, cek apakah ada lebih dari satu proses `go run ./cmd/api` yang nyala bersamaan dengan `.env` berbeda (salah satunya sisa proses lama yang lupa dimatikan).

#### Langkah 5 — Uji backend-nya langsung dulu, lepas dari Flutter

Supaya cepat tahu masalahnya di Flutter atau di server, uji dulu lewat Swagger UI (`http://localhost:8080/swagger/index.html`, Pertemuan 4 Bagian 11) atau `curl`: login untuk dapat token, lalu panggil endpoint yang 401 pakai token yang sama persis. Kalau lewat Swagger/curl berhasil (bukan 401) tapi dari Flutter tetap 401 dengan token yang sama — dipastikan masalahnya ada di kode Flutter (langkah 1-3 di atas), bukan di backend.

contoh verifikasi cepat lewat curl

    curl http://localhost:8080/api/umkm/saya -H "Authorization: Bearer <token-dari-login>"

Verifikasi lewat Swagger UI tetap aman walau lupa ketik "Bearer "

Kotak **Authorize** di Swagger UI *tidak* otomatis menambahkan kata `Bearer` ke token yang kamu paste (lihat Pertemuan 4 Bagian 10.7 & 11.4) — ini dulu sumber kebingungan paling umum saat pertama kali coba Swagger, karena token valid tapi tetap dibalas `401 "token tidak ditemukan"`. Middleware backend sekarang sudah menerima token dengan **atau tanpa** prefix `Bearer`, jadi verifikasi lewat Swagger tidak akan gagal gara-gara ini lagi. Tapi di kode Flutter sendiri, tetap selalu kirim header dengan format standar `Bearer <token>` (lewat `_authHeaders()`, Bagian 04) — itu konvensi yang benar dan dipakai semua API lain di dunia nyata.

## 16Struktur Folder Project (Final)

Struktur akhir setelah pertemuan ini — tetap mengikuti `lib/screens/<area>/<nama>_screen.dart` yang flat, konsisten dengan repo referensi project (bukan `lib/features/...` berlapis):

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

✓ Jalankan bersama API Pertemuan 4

Nyalakan backend Go lebih dulu (`go run ./cmd/api`, lihat Pertemuan 4 Bagian 12), pastikan `baseUrl` di `ApiService` sesuai jenis perangkat yang dipakai (Pertemuan 6 Bagian 07), baru jalankan `flutter run`. Urutan uji coba yang disarankan: register akun baru → login → buat UMKM (dengan/tanpa foto) → tambah beberapa produk → buka tab "Semua UMKM" dari akun lain untuk memastikan data publik ikut tampil → logout → pastikan kembali ke layar login dan tidak bisa menekan back ke Home.

## 17Latihan

1.  Tambahkan `RefreshIndicator` (tarik-untuk-refresh) pada `MyUmkmScreen`, memanggil ulang `_muatUmkm()`.
2.  Wire fitur pencarian yang diminta sebagai latihan di Pertemuan 6: tambahkan `TextField` pencarian pada `UmkmListScreen` yang memanggil ulang `getUmkmList(q: ...)`.
3.  Tambahkan konfirmasi (`showDialog` dengan tombol "Batal"/"Hapus") sebelum benar-benar memanggil `_hapusUmkm`/`_hapusProduk`, supaya tidak terhapus karena salah sentuh.
4.  **Tantangan:** buat satu fungsi pembantu di `ApiService` yang membungkus semua pemanggilan `http`, menangkap kasus token kedaluwarsa/tidak valid (status `401`) secara seragam — hapus token dari `TokenStorage` lalu lempar `ApiException` khusus yang ditangkap di level atas (mis. `MaterialApp` atau sebuah listener global) untuk otomatis mengarahkan ke `/login`, tanpa perlu menduplikasi pengecekan status 401 di setiap layar.

Dengan pertemuan ini, seluruh siklus penuh — dari Golang + PostgreSQL (Pertemuan 4) sampai aplikasi Flutter yang benar-benar login, menyimpan sesi, dan mengelola data milik sendiri termasuk foto (Pertemuan 5-7) — sudah tersambung end-to-end. Pola yang dipakai berulang di sini (model manual, ApiService terpusat, FutureBuilder/setState, ValueKey untuk refresh sebagian layar) adalah fondasi yang akan terus relevan di proyek Flutter skala berapa pun. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
