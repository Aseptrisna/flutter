<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Materi Pemula · HTTP & State Asinkron

# HTTP Client, Model Data & State Asinkron di Flutter

Materi ini adalah jembatan antara latihan widget (Pertemuan 5) dan integrasi penuh ke API UMKM (Pertemuan 7): cara memanggil REST API sungguhan, mengubah JSON menjadi objek Dart, dan menampilkannya dengan menangani tiga kondisi wajib — loading, error, dan data.

http.get→
Model.fromJson→
FutureBuilder→
Tampil di Layar

## 01Kenapa Perlu HTTP Client & Model Data

Sejauh ini, data yang ditampilkan pada latihan-latihan sebelumnya berasal dari nilai yang ditulis langsung di kode (dummy). Pada aplikasi nyata, data berasal dari server — pada kasus mata kuliah ini, dari **API UMKM berbasis Golang** yang dibangun pada Pertemuan 4.

Ada tiga hal baru yang perlu dikuasai dibanding sebelumnya:

- **Memanggil API** — mengirim HTTP request dan menunggu responsnya, yang sifatnya *asinkron* (tidak langsung selesai).
- **Mengubah JSON menjadi objek Dart** — respons API berbentuk teks JSON, perlu diubah menjadi *model* agar mudah dipakai di widget.
- **Menangani waktu tunggu** — selama data belum datang (atau gagal datang), UI tetap harus menampilkan sesuatu yang masuk akal, bukan layar kosong atau error mentah.

## 02Menambahkan Package http & Izin Internet

Flutter tidak memiliki HTTP client bawaan yang ringkas untuk dipakai langsung; package resmi `http` dari tim Dart adalah pilihan paling sederhana untuk memulai.

terminal

    flutter pub add http

| Platform | Yang perlu diperiksa |
|----|----|
| Android | Izin internet biasanya sudah otomatis ada di `android/app/src/main/AndroidManifest.xml` lewat template Flutter. Jika tidak, tambahkan `<uses-permission android:name="android.permission.INTERNET" />`. |
| iOS | Untuk memanggil URL `http://` (bukan `https://`) saat development, tambahkan pengecualian App Transport Security di `Info.plist`. Untuk produksi, gunakan `https://`. |

## 03Mengingat Kembali Kontrak API

Model dan service pada materi ini dibuat mengikuti persis bentuk respons API UMKM dari Pertemuan 4 — bukan format buatan sendiri. Tiga aturan yang wajib diingat:

respons sukses (single)

    { "data": { "id": 1, "nama": "Warung Bu Sari", "foto": "umkm/169....png" } }

respons sukses (list + pagination)

    { "data": [ { "id": 1, "nama": "Warung Bu Sari", "foto": "" } ], "meta": { "page": 1, "limit": 10, "total": 1 } }

respons gagal

    { "error": { "message": "UMKM tidak ditemukan", "code": "NOT_FOUND" } }

foto berisi path relatif, bukan URL penuh

Seperti dibahas di Pertemuan 4, field `foto` hanya berisi path relatif (mis. `"umkm/169....png"`) atau string kosong jika belum ada foto. Aplikasi Flutter yang menggabungkannya menjadi URL lengkap — dibahas di Bagian 10.

## 04Membuat Model Data (fromJson)

Model adalah class Dart biasa yang merepresentasikan satu baris data dari API, dengan constructor `fromJson` untuk mengubah `Map<String, dynamic>` (hasil decode JSON) menjadi objek. Materi ini memakai model manual (tanpa `freezed`/code generation) agar setiap barisnya mudah ditelusuri.

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

PostgreSQL `NUMERIC` dapat dikirim sebagai angka bulat oleh `encoding/json` Go (misal `17000` tanpa desimal). Meng-cast ke `num` dahulu (bukan langsung `double`) membuat kode tetap aman baik ketika nilainya `17000` maupun `17000.50`.

Kenapa pakai ?? '' di setiap field String?

Field seperti `deskripsi`, `alamat`, atau `foto` boleh kosong di API (dikirim sebagai string kosong, bukan `null`) — namun berjaga dengan `as String? ?? ''` membuat parsing tidak pernah crash walau suatu saat backend mengirim `null`.

## 05Membungkus Pagination

Karena banyak endpoint (Pertemuan 4) mengembalikan `data` beserta `meta` (page/limit/total), dibuat satu class generic `PaginatedResult<T>` yang bisa dipakai ulang untuk daftar UMKM maupun daftar apa pun di masa depan.

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

Generic `<T>` berarti class ini tidak terikat pada satu jenis model — dipanggil dengan `PaginatedResult.fromJson(json, Umkm.fromJson)` untuk daftar UMKM, atau `PaginatedResult.fromJson(json, Produk.fromJson)` untuk daftar produk, tanpa perlu menulis ulang logika paginasinya.

## 06ApiService: Memanggil Endpoint dengan http.get

Seluruh logika pemanggilan API dikumpulkan dalam satu class `ApiService`, terpisah dari widget/screen. Dengan begitu, screen hanya perlu tahu *apa* yang dipanggil, bukan *bagaimana* detail HTTP-nya.

lib/services/api_service.dart

    import 'dart:convert';
    import 'package:http/http.dart' as http;

    import '../models/umkm_model.dart';
    import '../models/produk_model.dart';
    import '../models/paginated_result.dart';

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

      static String fotoUrl(String relativePath) {
        final origin = baseUrl.replaceFirst('/api', '');
        return '$origin/uploads/$relativePath';
      }
    }

Kenapa error dibaca dari body, bukan cuma statusCode?

API Pertemuan 4 selalu mengembalikan body JSON meskipun gagal (`{"error":{"message":...}}`). Membaca `body['error']['message']` memungkinkan pesan error yang ramah ("UMKM tidak ditemukan") ditampilkan ke pengguna, bukan sekadar kode angka seperti `404`.

## 07Base URL: Emulator vs Device Fisik

Kesalahan paling umum saat pertama kali menyambungkan Flutter ke backend lokal adalah alamat `baseUrl` yang salah untuk jenis perangkat yang dipakai.

| Menjalankan dari | Alamat backend lokal (port 8080) |
|----|----|
| Android Emulator | `http://10.0.2.2:8080` — alamat khusus yang diarahkan emulator ke `localhost` komputer |
| iOS Simulator | `http://localhost:8080` — simulator berbagi jaringan langsung dengan komputer |
| Device fisik (Android/iOS) | `http://<IP-LAN-komputer>:8080`, misal `http://192.168.1.10:8080` — device dan komputer wajib berada di WiFi yang sama |
| Backend sudah di-deploy (produksi) | Domain sungguhan dengan `https://` |

Cek IP LAN komputer

Jalankan `ipconfig` (Windows) atau `ifconfig`/`ip addr` (macOS/Linux) untuk melihat alamat IP lokal komputer sebelum menguji dari device fisik.

## 08Menampilkan Data Asinkron dengan FutureBuilder

`FutureBuilder` adalah widget yang secara otomatis membangun ulang tampilan berdasarkan status sebuah `Future`: sedang menunggu, gagal, atau berhasil dengan data. Tiga kondisi ini **wajib** ditangani secara eksplisit.

9:41100%

ConnectionState.waiting

9:41100%

!

Gagal memuat data

Coba Lagi

snapshot.hasError

9:41100%

WS

Warung Bu Sari

Jl. Melati 10

TB

Toko Pak Budi

Jl. Kenanga 5

snapshot.hasData

pola FutureBuilder lengkap

    FutureBuilder<PaginatedResult<Umkm>>(
      future: _futureUmkm,
      builder: (context, snapshot) {
        // 1. Loading
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        // 2. Error
        if (snapshot.hasError) {
          return Center(child: Text('Gagal memuat data: ${snapshot.error}'));
        }
        final hasil = snapshot.data!;
        // 3. Kosong
        if (hasil.data.isEmpty) {
          return const Center(child: Text('Belum ada UMKM yang terdaftar'));
        }
        // 4. Data tersedia
        return ListView.builder(
          itemCount: hasil.data.length,
          itemBuilder: (context, i) => ListTile(title: Text(hasil.data[i].nama)),
        );
      },
    )

Future dibuat sekali di initState, bukan di build()

Jika pemanggilan `ApiService().getUmkmList()` diletakkan langsung di dalam `build()`, setiap kali widget rebuild (misalnya karena animasi kecil) akan memicu request baru ke server berulang-ulang. Simpan hasilnya ke variabel `Future` di `initState()` agar hanya dipanggil sekali.

## 09Alternatif: initState + setState Manual

`FutureBuilder` sangat cocok untuk pemanggilan sekali saat halaman dibuka. Namun ketika dibutuhkan kontrol lebih (misalnya tombol "muat ulang", atau menggabungkan loading dari beberapa sumber data), pola manual dengan variabel state lebih fleksibel.

pola manual dengan setState

    bool _loading = true;
    String? _error;
    List<Produk> _produk = [];

    @override
    void initState() {
      super.initState();
      _muatProduk();
    }

    Future<void> _muatProduk() async {
      setState(() {
        _loading = true;
        _error = null;
      });
      try {
        final hasil = await _apiService.getProdukByUmkm(widget.umkmId);
        setState(() => _produk = hasil.data); // ambil .data, meta (page/limit/total) diabaikan di sini
      } on ApiException catch (e) {
        setState(() => _error = e.message);
      } finally {
        setState(() => _loading = false);
      }
    }

Kenapa cuma ambil .data, bukan seluruh PaginatedResult\<Produk\>?

Sejak Bagian 06, `getProdukByUmkm` sudah mengembalikan `PaginatedResult<Produk>` (bukan `List<Produk>`) — persis seperti `getUmkmList` — karena endpoint `/api/umkm/{id}/produk` di API Golang memang mengirim `meta` (page/limit/total) juga. Halaman ini sengaja cuma menyimpan `.data`-nya ke `List<Produk>` karena belum butuh tombol "muat halaman berikutnya" untuk produk. Kalau nanti butuh paginasi produk juga, ganti tipe variabel state-nya jadi `PaginatedResult<Produk>`, sama persis seperti pola `_futureUmkm` di Bagian 08 dan 12.

| Pola | Kapan dipakai |
|----|----|
| `FutureBuilder` | Pemanggilan sederhana, sekali per halaman, tidak butuh tombol muat ulang manual |
| `initState` + `setState` | Butuh tombol "coba lagi"/refresh eksplisit, atau menggabungkan beberapa variabel status (loading, error, data) secara terpisah |

## 10Menampilkan Foto dari API

Karena field `foto` dari API hanya berisi path relatif (Bagian 03), method `ApiService.fotoUrl()` menggabungkannya menjadi URL lengkap sebelum dipakai `Image.network`/`NetworkImage`. Jika UMKM belum punya foto, tampilkan inisial nama sebagai gantinya.

    CircleAvatar(
      backgroundImage: umkm.punyaFoto
          ? NetworkImage(ApiService.fotoUrl(umkm.foto))
          : null,
      child: umkm.punyaFoto ? null : Text(umkm.nama[0]),
    )

Diuji dengan unit test

`ApiService.fotoUrl('umkm/169999.png')` diverifikasi menghasilkan persis `http://10.0.2.2:8080/uploads/umkm/169999.png` — menggabungkan origin server (tanpa `/api`) dengan `/uploads/` dan path relatifnya.

## 11Struktur Folder Project

Mulai pertemuan ini, folder `lib/` ditambah dua folder baru — `models/` dan `services/`. Berikut struktur **yang benar-benar sudah ada** di project-mu setelah mengikuti pertemuan ini sampai Bagian 12 — kalau kamu cek folder `lib/` sendiri, isinya harus persis seperti ini, tidak lebih:

struktur folder — setelah Pertemuan 6

    lib/
    ├── main.dart
    ├── models/
    │   ├── umkm_model.dart
    │   ├── produk_model.dart
    │   └── paginated_result.dart
    ├── services/
    │   └── api_service.dart
    └── screens/
        └── home/
            └── umkm/
                └── umkm_list_screen.dart

Kenapa cuma satu screen (umkm_list_screen.dart)?

Pertemuan ini fokus ke konsep HTTP client, model data, dan `ApiService` — baru dipraktikkan ke **satu** layar contoh (Bagian 12) untuk membuktikan semuanya tersambung ke API sungguhan. Layar lain seperti login, register, splash, profil, dan detail UMKM **belum dibuat di pertemuan ini** — itu semua baru ditambahkan satu per satu di Pertemuan 7 (integrasi penuh), yang juga akan menata ulang `screens/` jadi per-area (`auth/`, `home/profile/`, dst) mengikuti struktur `lib/screens/<area>/<nama>_screen.dart` yang flat (bukan `lib/features/...` berlapis).

## 12Praktik: Halaman "Semua UMKM" Tersambung ke API Sungguhan

Menggabungkan seluruh bagian di atas menjadi satu halaman utuh yang memanggil API, menampilkan avatar dari foto (atau inisial), serta mendukung tarik-untuk-refresh.

☰Semua UMKM

WS

Warung Bu Sari

Jl. Melati 10

TB

Toko Pak Budi

Jl. Kenanga 5

KC

Kedai Bu Citra

Jl. Anggrek 2

UmkmListScreen — data dari API sungguhan

lib/screens/home/umkm/umkm_list_screen.dart

    import 'package:flutter/material.dart';

    import '../../../models/paginated_result.dart';
    import '../../../models/umkm_model.dart';
    import '../../../services/api_service.dart';

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
                      onTap: () {
                        // navigasi ke UmkmDetailScreen, dibahas Pertemuan 7
                      },
                    );
                  },
                ),
              );
            },
          ),
        );
      }
    }

Menjalankan bersama API Pertemuan 4

Jalankan backend Go (`go run ./cmd/api`) sebelum menjalankan aplikasi Flutter ini. Isi minimal satu data UMKM lewat `POST /api/umkm` (lihat Pertemuan 4 Bagian 12) agar daftar tidak kosong saat pertama kali dicoba.

## 13Latihan

1.  Tambahkan parameter pencarian pada `UmkmListScreen`: sebuah `TextField` di atas daftar yang memanggil ulang `getUmkmList(q: ...)` ketika pengguna mengetik.
2.  Buat `UmkmDetailScreen` menampilkan detail satu UMKM (`getUmkmDetail`) beserta daftar produknya (`getProdukByUmkm`) dalam satu halaman, dan hubungkan dari `onTap` pada Bagian 12.
3.  Tambahkan penanganan *timeout*: bungkus pemanggilan `http.get` dengan `.timeout(const Duration(seconds: 10))` dan tampilkan pesan khusus jika waktu habis.
4.  **Tantangan:** pindahkan `baseUrl` pada `ApiService` agar bisa diatur lewat `--dart-define=API_BASE_URL=...` saat `flutter run`, sehingga tidak perlu mengubah kode setiap berpindah antara emulator dan device fisik.

Pola pada materi ini — model + service + FutureBuilder — adalah fondasi yang akan dipakai berulang kali pada Pertemuan 7 untuk seluruh fitur: login, register, profil, dan CRUD UMKM/produk. Semakin terbiasa dengan tiga kondisi wajib (loading/error/data) di sini, semakin mudah mengikuti integrasi penuh nanti. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
