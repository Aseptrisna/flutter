<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Pertemuan 1b · Fundamental Bahasa

# Dasar Pemrograman Dart & Golang

Mata kuliah ini memakai **Dart** untuk membangun aplikasi mobile (Flutter) dan **Golang** untuk membangun backend (REST API). Materi ini membahas dasar sintaks kedua bahasa secara berdampingan — bukan supaya dihafal terpisah, tapi supaya pola pikirnya kelihatan: di mana keduanya mirip, dan di mana keduanya sengaja berbeda filosofi.

## 01Kenapa Dart & Kenapa Go

**Dart** dipilih Google sebagai bahasa Flutter karena mendukung *hot reload* (kompilasi JIT saat development) sekaligus kompilasi native (AOT) saat rilis — kombinasi yang jarang ada di bahasa lain, dan cocok untuk UI yang sering berubah-ubah saat development tapi harus cepat saat dipakai pengguna.

**Go (Golang)** dipilih untuk backend karena sederhana (sengaja sedikit fitur, mudah dibaca tim besar), punya concurrency bawaan (goroutine) yang ringan, dan dikompilasi jadi satu binary native tanpa dependensi runtime — cocok untuk server yang harus menangani banyak koneksi sekaligus dengan resource minim.

Keduanya "statically typed"

Baik Dart maupun Go memaksa tipe data diketahui saat kompilasi (bukan saat program jalan seperti Python/JavaScript). Ini sebabnya banyak kesalahan ketahuan lewat IDE/compiler sebelum sempat dijalankan — kebiasaan yang akan terus dipakai sepanjang mata kuliah ini.

## 02Variabel & Tipe Data

Dart punya tipe dasar: `int`, `double`, `String`, `bool`, `List`, `Map`. Go punya himpunan yang mirip: `int`, `float64`, `string`, `bool`, `[]T` (slice), `map[K]V`.

Dart

    void main() {
      int umur = 20;
      double harga = 15000.5;
      String nama = 'Budi';
      bool aktif = true;

      // Inferensi tipe otomatis
      var kota = 'Bandar Lampung';

      // Konstanta — nilai tidak bisa diubah
      const pajak = 0.11;

      print('$nama, $umur tahun, dari $kota');
    }

Go

    package main

    import "fmt"

    func main() {
        var umur int = 20
        var harga float64 = 15000.5
        var nama string = "Budi"
        var aktif bool = true

        // Inferensi tipe otomatis (:=)
        kota := "Bandar Lampung"

        // Konstanta — nilai tidak bisa diubah
        const pajak = 0.11

        fmt.Printf("%s, %d tahun, dari %s\n", nama, umur, kota)
    }

var di Dart vs := di Go

Keduanya sama-sama "biarkan compiler menebak tipe dari nilai di kanan", tapi sintaksnya beda: Dart tetap menulis `var`, Go memakai operator `:=` (short variable declaration) yang hanya bisa dipakai di dalam fungsi, bukan di level package. Keduanya tetap **statically typed** — begitu dideklarasikan, tipe variabel itu tidak bisa berubah.

Kegunaan nyata: buat apa sebenarnya?

Variabel & tipe data mencegah data tertukar jenis — nama itu teks, harga itu angka, status login itu benar/salah. Di `Umkm` model (`umkm_model.dart`), field `nama` (String), `id` (int), `punyaFoto` (bool) harus persis sesuai jenisnya; kalau `harga` produk salah dideklarasikan sebagai `String`, perhitungan total belanja di aplikasi akan error atau salah hasil.

## 03Operator & Percabangan

Dart

    int nilai = 75;

    if (nilai >= 85) {
      print('A');
    } else if (nilai >= 70) {
      print('B');
    } else {
      print('C');
    }

    // switch dengan pattern (Dart 3)
    String kategori = switch (nilai) {
      >= 85 => 'A',
      >= 70 => 'B',
      _ => 'C',
    };

Go

    nilai := 75

    if nilai >= 85 {
        fmt.Println("A")
    } else if nilai >= 70 {
        fmt.Println("B")
    } else {
        fmt.Println("C")
    }

    // switch tanpa kondisi (idiomatis di Go)
    var kategori string
    switch {
    case nilai >= 85:
        kategori = "A"
    case nilai >= 70:
        kategori = "B"
    default:
        kategori = "C"
    }

Go tidak pakai tanda kurung pada kondisi if

`if nilai >= 85 {` — bukan `if (nilai >= 85) {`. Ini bukan opsional, melainkan aturan sintaks Go: tanda kurung di sekitar kondisi malah jadi error compile. Kurung kurawal `{ }` juga wajib walau badan if cuma satu baris (beda dari Dart yang mengizinkan `if (x) print(x);` tanpa kurung kurawal).

Kegunaan nyata: buat apa sebenarnya?

Operator & percabangan membuat program mengambil keputusan berbeda tergantung kondisi — inti dari hampir semua logika aplikasi. Di `MyUmkmScreen`: `if (umkm == null)` menentukan tampilkan tombol "Buat UMKM" atau detail UMKM. Di backend Go: `if response.statusCode != 200 { throw error }` dipakai di **setiap** method `ApiService` untuk membedakan request sukses atau gagal.

## 04Perulangan

Dart

    // for klasik
    for (int i = 0; i < 5; i++) {
      print(i);
    }

    // for-in untuk koleksi
    final buah = ['apel', 'jeruk', 'mangga'];
    for (final nama in buah) {
      print(nama);
    }

    // while
    int sisa = 3;
    while (sisa > 0) {
      sisa--;
    }

Go

    // for klasik — satu-satunya bentuk loop di Go
    for i := 0; i < 5; i++ {
        fmt.Println(i)
    }

    // for-range untuk koleksi (index, value)
    buah := []string{"apel", "jeruk", "mangga"}
    for _, nama := range buah {
        fmt.Println(nama)
    }

    // "while" di Go cukup pakai for tanpa init/post
    sisa := 3
    for sisa > 0 {
        sisa--
    }

Go cuma punya satu kata kunci loop: for

Tidak ada `while` atau `do-while` terpisah seperti di Dart — semuanya ditulis dengan `for` dalam bentuk berbeda. Ini konsisten dengan filosofi Go: lebih sedikit cara melakukan hal yang sama, supaya kode tim besar tetap seragam gayanya.

Kegunaan nyata: buat apa sebenarnya?

Perulangan mengerjakan hal yang sama berulang kali tanpa menulis kode berkali-kali — biasanya untuk memproses daftar data. `produkList.map((p) => ListTile(...)).toList()` di `MyUmkmScreen` menampilkan setiap produk jadi satu baris list, berapapun jumlah produknya. Tanpa loop, kamu harus menulis kode tampilan untuk tiap produk satu per satu secara manual.

## 05Fungsi

Dart

    int tambah(int a, int b) {
      return a + b;
    }

    // parameter bernama (named) & opsional
    String sapa(String nama, {String salam = 'Halo'}) {
      return '$salam, $nama!';
    }

    // mengembalikan lebih dari satu nilai lewat Record (Dart 3)
    (int, int) bagiSisa(int a, int b) {
      return (a ~/ b, a % b);
    }

    void main() {
      print(tambah(2, 3));
      print(sapa('Budi'));
      final (hasil, sisa) = bagiSisa(17, 5);
      print('$hasil sisa $sisa');
    }

Go

    package main

    import "fmt"

    func tambah(a int, b int) int {
        return a + b
    }

    func sapa(nama string) string {
        return fmt.Sprintf("Halo, %s!", nama)
    }

    // mengembalikan lebih dari satu nilai — pola sangat umum di Go
    func bagiSisa(a int, b int) (int, int) {
        return a / b, a % b
    }

    func main() {
        fmt.Println(tambah(2, 3))
        fmt.Println(sapa("Budi"))
        hasil, sisa := bagiSisa(17, 5)
        fmt.Printf("%d sisa %d\n", hasil, sisa)
    }

Multiple return value: fitur bawaan Go, fitur baru di Dart

Go sudah punya multiple return value sejak awal — dan ini dipakai di **mana-mana**, terutama untuk pola `(hasil, error)` yang akan dibahas di Bagian 09. Dart baru mendapat fitur setara (*Records*) di Dart 3 (2023) — sebelumnya pemrogram Dart harus membungkus beberapa nilai dalam class atau `List`/`Map` buatan sendiri.

Kegunaan nyata: buat apa sebenarnya?

Fungsi membungkus sekumpulan langkah jadi satu nama yang bisa dipanggil ulang — menghindari copy-paste kode yang sama di banyak tempat. `ApiService.getUmkmSaya()` membungkus seluruh langkah (buat request, decode JSON, cek status, lempar error) jadi satu pemanggilan sederhana yang dipakai di `MyUmkmScreen` tanpa perlu menulis ulang detail HTTP-nya setiap kali butuh data UMKM.

## 06Koleksi Data

Dart

    // List — array dinamis
    List<String> kota = ['Bandar Lampung', 'Metro'];
    kota.add('Kotabumi');
    print(kota.length);

    // Map — key-value
    Map<String, int> stok = {'apel': 10, 'jeruk': 5};
    stok['mangga'] = 8;
    print(stok['apel']);

    // Operasi fungsional
    final genap = [1, 2, 3, 4, 5].where((n) => n % 2 == 0).toList();

Go

    // Slice — array dinamis (mirip List)
    kota := []string{"Bandar Lampung", "Metro"}
    kota = append(kota, "Kotabumi")
    fmt.Println(len(kota))

    // Map — key-value
    stok := map[string]int{"apel": 10, "jeruk": 5}
    stok["mangga"] = 8
    fmt.Println(stok["apel"])

    // Go tidak punya .where()/.map() bawaan — ditulis manual dengan for
    var genap []int
    for _, n := range []int{1, 2, 3, 4, 5} {
        if n%2 == 0 {
            genap = append(genap, n)
        }
    }

append() mengembalikan slice baru, bukan mengubah di tempat

`kota = append(kota, "Kotabumi")` — hasil `append` harus ditampung ulang ke variabelnya. Beda dari Dart `List.add()` yang langsung mengubah list aslinya. Ini karena slice Go bisa saja perlu dialokasikan ulang ke memori baru kalau kapasitasnya penuh, jadi Go memaksa penulisnya sadar akan hal ini lewat return value.

Kegunaan nyata: buat apa sebenarnya?

Koleksi data menyimpan banyak data sejenis sekaligus — daftar UMKM, daftar produk, hasil query database. `PaginatedResult<Umkm>.data` adalah `List<Umkm>` — seluruh daftar UMKM dari API ditampung di satu variabel ini, lalu ditampilkan lewat `ListView.builder`. Di backend Go, hasil query SQL ditampung sebagai slice `[]Umkm` sebelum dikirim jadi JSON ke Flutter.

## 07OOP: Class (Dart) vs Struct + Method (Go)

Dart adalah bahasa *object-oriented* penuh dengan `class`, pewarisan (`extends`), dan interface. Go **tidak punya class sama sekali** — Go memakai `struct` untuk mengelompokkan data, lalu menempelkan *method* ke struct itu secara terpisah.

Dart

    class Produk {
      final String nama;
      final double harga;

      Produk({required this.nama, required this.harga});

      String info() {
        return '$nama - Rp$harga';
      }
    }

    void main() {
      final p = Produk(nama: 'Kopi', harga: 15000);
      print(p.info());
    }

Go

    package main

    import "fmt"

    type Produk struct {
        Nama  string
        Harga float64
    }

    // method ditempel ke struct lewat "receiver" (p Produk)
    func (p Produk) Info() string {
        return fmt.Sprintf("%s - Rp%.0f", p.Nama, p.Harga)
    }

    func main() {
        p := Produk{Nama: "Kopi", Harga: 15000}
        fmt.Println(p.Info())
    }

Tidak ada pewarisan (inheritance) di Go

Dart punya `class Anak extends Induk`. Go sengaja tidak menyediakan ini — sebagai gantinya, Go memakai **composition** (menaruh satu struct di dalam struct lain) dan **interface** (kontrak method, tanpa implementasi) untuk berbagi perilaku antar tipe. Ini keputusan filosofis Go: pewarisan sering membuat hierarki class rumit di bahasa lain, jadi Go menghindarinya sejak awal.

Huruf besar di awal nama = exported (public) di Go

`Produk`, `Nama`, `Info` diawali huruf besar sehingga bisa diakses dari package lain (setara `public` di bahasa lain). Kalau ditulis huruf kecil (`produk`, `nama`), otomatis *private* — hanya bisa diakses dalam package yang sama. Dart memakai kata kunci eksplisit seperti garis bawah di depan nama (`_variabelPrivat`) untuk hal yang sama.

Kegunaan nyata: buat apa sebenarnya?

OOP mengelompokkan data yang berkaitan jadi satu "bentuk" yang jelas, plus perilakunya — daripada data UMKM berceceran di banyak variabel lepas. `class Umkm { id, nama, alamat, foto }` membuat satu objek `Umkm` mewakili satu baris data UMKM secara utuh, dioper ke mana-mana (ke `UmkmDetailScreen`, `UmkmFormScreen`) sebagai satu kesatuan, bukan parameter terpisah-pisah yang gampang salah urutan.

## 08Null Safety (Dart) vs Zero Value (Go)

Keduanya mencegah bug klasik "null reference", tapi dengan pendekatan yang berlawanan.

Dart — null safety

    String nama = 'Budi';       // tidak boleh null
    String? alamat;              // boleh null, wajib tanda ?

    // Compiler MEMAKSA cek null sebelum dipakai
    print(alamat?.toUpperCase()); // aman, hasil null kalau alamat null
    print(alamat ?? 'Tidak ada'); // nilai default kalau null

    // "Saya yakin ini tidak null" (hati-hati, bisa crash)
    print(alamat!.length);

Go — zero value

    var nama string   // otomatis ""  (bukan null/nil)
    var umur int      // otomatis 0
    var aktif bool    // otomatis false
    var daftar []int  // otomatis nil (slice kosong)

    // nil HANYA ada untuk tipe tertentu: pointer, slice,
    // map, interface, channel, function
    var alamat *string // boleh nil, karena pointer

    if alamat != nil {
        fmt.Println(*alamat)
    }

Filosofi yang berbeda

Dart (sejak versi 2.12/null safety) memaksa programmer menyatakan eksplisit "variabel ini boleh kosong" lewat tanda `?`, lalu compiler menolak kompilasi kalau nilai nullable dipakai tanpa dicek. Go tidak punya konsep "nullable type" — setiap tipe data punya **zero value** baku (string kosong, angka nol, dst) sehingga variabel tidak pernah benar-benar "tidak terdefinisi". `nil` di Go cuma berlaku untuk segelintir tipe (pointer, slice, map, interface, channel, function), dan mengakses pointer `nil` tetap bisa bikin program crash (*nil pointer dereference*) — mirip efeknya dengan null safety yang dilanggar paksa pakai `!` di Dart.

Kegunaan nyata: buat apa sebenarnya?

Null safety & zero value mencegah aplikasi crash gara-gara mengakses data yang sebenarnya belum ada/kosong. `getUmkmSaya()` mengembalikan `Umkm?` (boleh null) karena pengguna baru **mungkin belum punya UMKM** — `if (umkm == null)` di `MyUmkmScreen` menangani kasus itu secara eksplisit, bukan asal akses `umkm.nama` yang akan crash kalau null.

## 09Error Handling

Dart — try/catch

    double bagi(int a, int b) {
      if (b == 0) {
        throw Exception('Tidak bisa dibagi nol');
      }
      return a / b;
    }

    void main() {
      try {
        print(bagi(10, 0));
      } catch (e) {
        print('Error: $e');
      } finally {
        print('Selesai diproses');
      }
    }

Go — return error

    package main

    import (
        "errors"
        "fmt"
    )

    func bagi(a, b int) (float64, error) {
        if b == 0 {
            return 0, errors.New("tidak bisa dibagi nol")
        }
        return float64(a) / float64(b), nil
    }

    func main() {
        hasil, err := bagi(10, 0)
        if err != nil {
            fmt.Println("Error:", err)
            return
        }
        fmt.Println(hasil)
    }

Go tidak punya exception — error adalah nilai biasa

Dart (seperti kebanyakan bahasa lain) melempar *exception* yang "melompat" ke blok `catch` terdekat. Go sama sekali tidak punya mekanisme ini untuk alur normal — fungsi yang bisa gagal cukup mengembalikan nilai kedua bertipe `error` (lihat Bagian 05: multiple return value), dan pemanggil **wajib** mengecek `if err != nil` secara eksplisit setiap kali. Ini terasa lebih verbose, tapi membuat jalur error terlihat jelas di setiap baris, tidak tersembunyi seperti exception yang bisa dilempar dari fungsi manapun tanpa terlihat di signature-nya. Pola `if err != nil { return ...err }` ini akan sangat sering muncul di backend `umkm-api` (Pertemuan 4).

Kegunaan nyata: buat apa sebenarnya?

Error handling menangani kegagalan (koneksi putus, data tidak valid, server down) dengan rapi, bukan bikin aplikasi langsung tertutup paksa. `try { await _apiService.hapusUmkm(id); } on ApiException catch (e) { tampilkan SnackBar }` — kalau hapus gagal (misal koneksi internet putus), pengguna melihat pesan error yang jelas, aplikasi tidak crash.

## 10Asynchronous: Future/async-await vs Goroutine/Channel

Dart berjalan di satu *thread* (event loop) dan memakai `Future`/`async`/`await` untuk kerja yang butuh menunggu (network, file). Go punya **concurrency bawaan** lewat *goroutine* — ribuan "thread ringan" bisa jalan bersamaan, dikoordinasikan lewat *channel*.

Dart — Future & async/await

    Future<String> ambilData() async {
      await Future.delayed(const Duration(seconds: 1));
      return 'Data dari server';
    }

    void main() async {
      print('Mulai mengambil data...');
      final data = await ambilData();
      print(data);
    }

Go — goroutine & channel

    package main

    import (
        "fmt"
        "time"
    )

    func ambilData(hasil chan string) {
        time.Sleep(1 * time.Second)
        hasil <- "Data dari server"
    }

    func main() {
        hasil := make(chan string)
        fmt.Println("Mulai mengambil data...")
        go ambilData(hasil) // jalankan sebagai goroutine terpisah
        data := <-hasil      // tunggu sampai ada nilai dikirim ke channel
        fmt.Println(data)
    }

Dart: satu tugas tertunda setiap saat. Go: banyak tugas berjalan betulan bersamaan

`await` di Dart menjeda eksekusi fungsi saat ini sampai `Future` selesai, tapi thread utama tetap satu — cocok untuk UI yang menunggu respons API tanpa membekukan layar. Kata kunci `go` di depan pemanggilan fungsi Go benar-benar menjalankan fungsi itu di goroutine terpisah yang berjalan konkuren (bisa paralel di banyak core CPU) — inilah yang membuat satu server Go sanggup melayani ribuan request HTTP sekaligus tanpa membuat thread sistem operasi baru untuk tiap request (yang mahal). `channel` adalah "pipa" aman untuk mengirim nilai antar goroutine tanpa data race.

Kegunaan nyata: buat apa sebenarnya?

Asynchronous menjalankan proses yang makan waktu (request ke server, baca database) tanpa membekukan tampilan aplikasi/server selagi menunggu. `await _apiService.login(...)` — selagi menunggu respons server, Flutter tetap bisa menampilkan `CircularProgressIndicator` berputar, tidak freeze. Di backend Go, goroutine membuat satu server sanggup melayani ratusan request UMKM sekaligus tanpa antre satu per satu.

## 11Package & Module System

|  | Dart / Flutter | Go |
|----|----|----|
| Berkas manifest dependensi | `pubspec.yaml` | `go.mod` |
| Perintah tambah dependensi | `flutter pub add <paket>` | `go get <modul>` |
| Registry resmi | <a href="https://pub.dev" target="_blank" rel="noopener">pub.dev</a> | <a href="https://pkg.go.dev" target="_blank" rel="noopener">pkg.go.dev</a> |
| Import dalam kode | `import 'package:http/http.dart';` | `import "net/http"` |
| File lock versi | `pubspec.lock` | `go.sum` |

Struktur ini sudah dipakai sejak Pertemuan 4 & 6

Penambahan `http`, `flutter_secure_storage`, `image_picker` lewat `flutter pub add` (Pertemuan 7 Bagian 02/04) di sisi Flutter, dan `go get` untuk `pgx`/`golang-jwt`/dsb di sisi backend (Pertemuan 4), keduanya mengikuti pola yang sama persis seperti tabel di atas — cuma nama perintah dan file manifest-nya yang beda.

Kegunaan nyata: buat apa sebenarnya?

Package & module system memakai kode yang sudah dibuat orang lain (komunitas) daripada menulis ulang dari nol — misalnya logika HTTP request yang rumit. `flutter pub add http` memberi akses ke package `http` yang dipakai di `ApiService` untuk semua pemanggilan API — tanpa package ini, kamu harus menulis sendiri seluruh protokol HTTP dari socket mentah, yang jauh lebih rumit dan rawan bug.

## 12Latihan

1.  Tulis fungsi Dart dan fungsi Go yang sama-sama menghitung apakah sebuah angka termasuk bilangan prima, lalu bandingkan gaya penulisannya.
2.  Buat satu `class Mahasiswa` di Dart (dengan field `nama` dan `nim`) dan satu `struct Mahasiswa` + method `Info()` yang setara di Go.
3.  Di Dart, buat fungsi yang mengembalikan `String?` (nullable) untuk mencari nama berdasarkan ID di sebuah `Map`; tangani kasus ID tidak ditemukan tanpa memakai tanda `!`.
4.  Di Go, buat fungsi yang mengembalikan `(string, error)` untuk kasus yang sama; kembalikan error ketika ID tidak ditemukan di `map`.
5.  **Tantangan:** jalankan tiga `Future` di Dart secara bersamaan dengan `Future.wait([...])`, lalu bandingkan dengan menjalankan tiga goroutine di Go yang mengirim hasilnya ke satu channel yang sama.

Dasar-dasar di sini akan terus dipakai di sepanjang mata kuliah: sintaks Dart untuk seluruh layar Flutter (Pertemuan 2–7), dan sintaks Go untuk seluruh backend `umkm-api` (Pertemuan 4). Kalau ada bagian yang masih terasa asing saat membaca kode di pertemuan lain, kembali ke materi ini sebagai rujukan. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
