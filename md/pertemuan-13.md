<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 13 · Praktikum 4/5 · Proyek Sendiri

# Halaman CRUD Lengkap & ApiService

Alur auth sudah jalan dari Pertemuan 12. Sekarang dibangun bagian terbesar aplikasimu: `ApiService` lengkap sebagai satu-satunya jembatan ke API, lalu halaman daftar, detail, dan CRUD penuh (tambah/ubah/hapus, termasuk foto) untuk entitas utama aplikasimu — mengikuti pola `umkm-app` persis, termasuk trik `ValueKey` yang sering jadi titik bingung pemula.

← [Pertemuan 12: Fundamental Flutter](pertemuan-12.html)
[Pertemuan 14: Trace & Rangkuman](pertemuan-14.html) →

## 01Tentang Pertemuan Ini

Ini pertemuan praktikum paling padat di rangkaian ini — tujuannya satu: entitas utama aplikasimu bisa **dibaca, dibuat, diubah, dan dihapus** sepenuhnya dari Flutter, tersambung ke backend sendiri (Pertemuan 11). Semua kode acuan di sini diambil dari `umkm-app` ([Pertemuan 9 Bagian 16-19](pertemuan-09.html#s16)) — dibaca dulu polanya, baru diterapkan ke entitasmu.

## 02ApiService & TokenStorage — Jembatan Tunggal ke API

Aturan paling penting: **tidak ada layar yang memanggil `http.get`/`http.post` langsung** — semua request lewat satu class `ApiService`. Tiga pola kunci dari `umkm-app`:

- **Satu fungsi untuk create dan update** lewat parameter `id` opsional (`null` → `POST`, terisi → `PUT`) — menghindari dua fungsi multipart yang nyaris identik.
- **`_authHeaders()` privat** membaca token dari `TokenStorage`, dipanggil di semua fungsi yang butuh login — satu tempat untuk logika "tempel header Authorization".
- **`baseUrl` memakai IP LAN**, bukan `localhost` — perangkat fisik/emulator adalah "komputer" terpisah dari mesin development.

api_service.dart — simpanUmkm & \_authHeaders, contoh acuan

    /// id == null -> membuat baru (POST). id terisi -> ubah yang ada (PUT).
    Future<Umkm> simpanUmkm({
      int? id,
      required String nama,
      String deskripsi = '',
      String alamat = '',
      String? fotoPath,
    }) async {
      final uri = id == null
          ? Uri.parse('$baseUrl/umkm')
          : Uri.parse('$baseUrl/umkm/$id');
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

    Future<Map<String, String>> _authHeaders() async {
      final token = await TokenStorage.ambil();
      return {'Authorization': 'Bearer $token'};
    }

`foto` hanya ditambahkan ke `request.files` kalau `fotoPath != null` — saat *update*, pengguna boleh tidak mengganti foto sama sekali (backend mempertahankan foto lama, lihat Pertemuan 11 Bagian 04). Status `200` dan `201` dua-duanya dianggap sukses, karena backend membalas `201` untuk `POST` dan `200` untuk `PUT` — satu fungsi menangani dua kemungkinan status.

token_storage.dart — seluruh isi file, contoh acuan

    import 'package:flutter_secure_storage/flutter_secure_storage.dart';

    class TokenStorage {
      static const _storage = FlutterSecureStorage();
      static const _key = 'auth_token';

      static Future<void> simpan(String token) => _storage.write(key: _key, value: token);
      static Future<String?> ambil() => _storage.read(key: _key);
      static Future<void> hapus() => _storage.delete(key: _key);
    }

Dipakai di terlalu banyak tempat: `login()` memanggil `simpan()`, `_authHeaders()` memanggil `ambil()`, `logout()` memanggil `hapus()`. Kalau mekanisme penyimpanan token perlu diganti di kemudian hari, hanya file ini yang perlu disentuh.

Tugas Kamu

Lengkapi `api_service.dart`-mu (yang sudah mulai dibuat di Pertemuan 12) dengan fungsi-fungsi berikut, untuk entitas utama aplikasimu:

1.  `getDaftar(...)` — publik, dengan pencarian + pagination (sudah ada dari Pertemuan 12, pastikan lengkap).
2.  `getDetail(id)` — publik, satu data.
3.  `simpan({id, ...field, fotoPath})` — satu fungsi untuk create & update, pola persis seperti `simpanUmkm` di atas.
4.  `hapus(id)` — butuh login.
5.  Buat `token_storage.dart` milikmu sendiri — boleh disalin persis dari contoh di atas, isinya memang sengaja setipis itu.

## 03Halaman Daftar & Detail

Pola layar publik (tidak perlu login) di `umkm-app`:

- **Layar Home** — kalau punya beberapa tab, pakai `IndexedStack` dengan `NavigationBar`, bukan mengganti `body` biasa. `IndexedStack` membuat `State` tiap tab (termasuk `Future` yang sudah ter-fetch) tidak dibuang & di-fetch ulang setiap kali pindah tab.
- **Layar Daftar** — `FutureBuilder`, data diambil sekali di `initState`. `RefreshIndicator` (tarik-untuk-refresh) memanggil fungsi yang meng-assign ulang variabel `Future` di dalam `setState` — ini pola standar "refresh" untuk `FutureBuilder`, karena `FutureBuilder` sendiri tidak pernah otomatis memanggil ulang `Future`-nya.
- **Layar Detail** — publik, mengambil beberapa `Future` independen secara paralel di `initState` kalau perlu menampilkan data relasi (misal data utama + daftar anaknya), ditampilkan lewat `FutureBuilder` bersarang.

Tugas Kamu

Bangun `<entitas>_list_screen.dart` (daftar, dengan `RefreshIndicator`) dan `<entitas>_detail_screen.dart` (detail) untuk entitas utamamu, tersambung ke `getDaftar`/`getDetail` dari Bagian 02. Keduanya harus bisa diakses **tanpa login** (uji dengan logout dulu, lalu buka layar ini).

## 04CRUD Lengkap & Trik ValueKey

Layar "milik saya" (butuh login) biasanya paling kompleks karena menggabungkan baca, buat, ubah, dan hapus dalam satu tempat.

**Trik `ValueKey` untuk memaksa remount** — kalau halaman utamamu punya daftar anak (misal daftar produk di bawah satu UMKM) yang dipisah jadi widget tersendiri dengan `initState`-nya sendiri, widget anak itu **tidak akan pernah fetch ulang otomatis** hanya karena parent-nya `setState` — kecuali diberi `key` yang sengaja diubah:

myumkm_screen.dart — potongan kunci, contoh acuan

    class _MyUmkmScreenState extends State<MyUmkmScreen> {
      int _produkKey = 0;

      void _muatUlangProduk() => setState(() => _produkKey++);

      // ...di dalam build(), setelah data utama didapat:
      _DaftarProduk(
        key: ValueKey(_produkKey),   // berubah setiap _muatUlangProduk() dipanggil
        umkmId: umkm.id,
        apiService: _apiService,
      ),
    }

    class _DaftarProdukState extends State<_DaftarProduk> {
      @override
      void initState() {
        super.initState();
        _futureProduk = widget.apiService.getProdukByUmkm(widget.umkmId); // fetch sekali
      }
    }

Alurnya: hapus satu produk → `_muatUlangProduk()` → `_produkKey` bertambah → `setState` men-trigger `build()` ulang → widget `_DaftarProduk` dibuat lagi dengan `key` yang berbeda dari sebelumnya → Flutter melihat `key` berubah sebagai sinyal "ini widget yang berbeda" → instance lama **dibuang**, instance baru dibuat dari nol → `initState`-nya jalan lagi, fetch ulang. Tanpa `key` yang berubah, Flutter menganggap ini widget yang "sama" dan tidak pernah membuat instance baru — daftar tidak pernah ter-refresh walau datanya di server sudah berubah.

Tugas Kamu

1.  Bangun layar "`<Entitas>` Saya" — tampilkan data milik pengguna yang sedang login (`null` berarti belum punya, tampilkan tombol "Buat"), lengkap tombol Edit & Hapus.
2.  Kalau entitasmu punya relasi anak (seperti produk di bawah UMKM), pisahkan daftar anak itu jadi widget tersendiri dan terapkan trik `ValueKey` seperti contoh di atas.
3.  **Buktikan triknya**: tambahkan `debugPrint` di `initState` widget anak, lalu coba tambah satu data anak baru — `debugPrint` harus muncul lagi dengan key berbeda. Coba lepas `key: ValueKey(...)`-nya sebentar untuk melihat daftar jadi "basi" (tidak ter-refresh), lalu kembalikan lagi.

## 05Form Tambah/Edit

Satu layar form dipakai untuk **dua mode** (tambah dan edit) lewat parameter nullable di constructor — kalau data yang dikirim `null`, berarti mode tambah; kalau terisi, mode edit dengan field sudah terisi data lama. Validasi ekstensi foto (JPG/JPEG/PNG) dicek ulang di sisi Flutter sebelum submit — identik dengan whitelist di backend (Pertemuan 11 Bagian 06) — supaya pengguna dapat feedback instan tanpa menunggu respons gagal dari server.

Tugas Kamu

1.  Bangun `<entitas>_form_screen.dart` dual-mode (constructor menerima parameter data nullable).
2.  Pakai `image_picker` untuk memilih foto (kalau entitasmu punya foto), validasi ekstensi di sisi Flutter sebelum submit.
3.  Setelah sukses simpan, `Navigator.pop(context, true)` — lalu di layar pemanggil, hasil `true` dipakai memicu reload data (lihat Bagian 04).

## 06Profil & Ubah Password

Pola layar profil di `umkm-app`: `FutureBuilder<User>` fetch sekali, menampilkan data akun + tombol Logout. **Logout** memanggil `ApiService.logout()` (hanya menghapus token lokal, **tidak** memanggil API) lalu `Navigator.pushNamedAndRemoveUntil` ke `/login` — menghapus **seluruh** riwayat navigasi, supaya tombol back tidak bisa membawa pengguna kembali ke halaman yang butuh login.

Layar ubah profil biasanya menggabungkan dua `Form` independen (ubah profil, ubah password) dengan state loading **terpisah** untuk masing-masing — supaya mengirim salah satu form tidak ikut mengunci tombol submit form lainnya.

Tugas Kamu

Bangun layar Profil (tampilkan data akun + tombol Logout yang membersihkan navigation stack) dan layar Ubah Profil/Password (dua form independen, state loading terpisah).

## 07Menjalankan & Menguji CRUD Lengkap

Jalankan `flutter run` sambil backend-mu aktif, lalu uji urutan lengkap ini:

1.  Logout (atau install ulang) → buka layar Daftar & Detail tanpa login → harus bisa diakses (publik).
2.  Login → buka layar "Milik Saya" → kalau belum punya data, harus tampil tombol "Buat".
3.  Buat data baru lewat form (dengan foto kalau ada) → harus langsung muncul di layar "Milik Saya" setelah `Navigator.pop(context, true)`.
4.  Edit data yang baru dibuat (ubah 1 field, tidak upload foto baru) → foto lama harus tetap ada, bukan hilang.
5.  Kalau ada relasi anak: tambah 1 data anak → buktikan daftar anak ter-refresh otomatis (trik `ValueKey`).
6.  Hapus data → harus hilang dari semua layar yang menampilkannya setelah refresh.
7.  Ubah profil & password → logout & login lagi dengan password baru.

Checkpoint sebelum Pertemuan 14

Kalau ketujuh langkah di atas berhasil, aplikasimu sudah punya alur CRUD penuh yang setara `umkm-app`. Pertemuan 14 akan menelusuri salah satu alur ini (trace request) dari tombol sampai database, memakai urutan yang sama seperti yang baru saja kamu uji.

## 08Rangkuman & Checklist

- `ApiService` lengkap: daftar, detail, simpan (create+update), hapus — semua lewat satu class, tidak ada `http.get`/`http.post` langsung di screen.
- `TokenStorage` terpasang, dipakai konsisten di login/logout/`_authHeaders`.
- Layar Daftar & Detail bisa diakses tanpa login.
- Layar "Milik Saya" CRUD penuh, termasuk trik `ValueKey` kalau ada relasi anak.
- Form dual-mode (tambah/edit) dengan validasi foto di sisi Flutter.
- Profil, ubah password, dan logout (menghapus seluruh riwayat navigasi) jalan dengan benar.
- Ketujuh skenario uji di Bagian 07 semua berhasil.

← [Pertemuan 12: Fundamental Flutter](pertemuan-12.html)
[Pertemuan 14: Trace & Rangkuman](pertemuan-14.html) →

Bagian 4 dari 5 rangkaian praktikum proyek UAS — lanjut ke [Pertemuan 14: Trace Request, Testing, Deployment & Rangkuman](pertemuan-14.html). — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
