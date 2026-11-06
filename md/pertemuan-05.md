<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Materi Pemula · Praktik Widget Flutter

# Praktik Widget & Layout Flutter — dari Kode ke Tampilan Android

Setiap widget pada materi ini disertai visual berupa mockup layar Android, sehingga terlihat jelas bagaimana kode Dart yang ditulis benar-benar menghasilkan tampilan tersebut. Materi mencakup posisi elemen (atas, tengah, kiri, kanan), teks, gambar, tombol, form, hingga menyusun satu halaman lengkap.

Layout→
Widget Dasar→
Form→
Halaman Utuh

## 01Filosofi Tata Letak: Row, Column, Stack

Seluruh posisi elemen pada Flutter — atas, bawah, kiri, kanan, tengah, atau bertumpuk — dibangun dari tiga widget dasar berikut. Memahami ketiganya dengan baik membuat sisa materi ini jauh lebih mudah diikuti.

| Widget | Fungsi |
|----|----|
| `Column` | Menyusun widget secara **vertikal** (atas ke bawah). |
| `Row` | Menyusun widget secara **horizontal** (kiri ke kanan). |
| `Stack` | Menumpuk widget satu di atas yang lain (untuk overlay, badge, label di atas gambar, dsb). |

9:41••• 100%

Column

Tersusun ke bawah

9:41••• 100%

Row

Tersusun ke samping

9:41••• 100%

FOTO LATAR

Label di Atas

Stack

Bertumpuk (overlay)

Column — vertikal

    Column(
      children: [
        Text('Baris pertama'),
        Text('Baris kedua'),
        Text('Baris ketiga'),
      ],
    )

Row — horizontal

    Row(
      children: [
        Icon(Icons.star),
        Icon(Icons.star),
        Icon(Icons.star),
      ],
    )

Stack — bertumpuk

    Stack(
      children: [
        Image.network('https://.../foto.jpg', fit: BoxFit.cover),
        Positioned(
          bottom: 10,
          left: 10,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.black54,
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Text('Label di Atas', style: TextStyle(color: Colors.white)),
          ),
        ),
      ],
    )

Positioned hanya berlaku di dalam Stack

Widget `Positioned` (mengatur jarak dari `top`/`bottom`/`left`/`right`) hanya bisa dipakai sebagai anak langsung dari `Stack`. Di luar `Stack`, gunakan `Align` atau `Padding`.

## 02Mengatur Posisi Elemen (Gambar Atas, Tengah, Kiri, Kanan)

Bagian ini menjawab pertanyaan paling umum pemula: *"bagaimana caranya taruh gambar/teks di posisi tertentu?"*. Empat pola paling sering dipakai ditunjukkan berikut, lengkap dengan visualnya.

#### Gambar di Atas

9:41100%

IMG

Nama Aplikasi

di atas

    Column(
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        Image.asset('assets/logo.png', width: 64),
        const SizedBox(height: 10),
        const Text('Nama Aplikasi'),
      ],
    )

#### Gambar di Tengah

9:41100%

IMG

di tengah

    Center(
      child: Image.asset('assets/logo.png', width: 64),
    )

#### Gambar di Kiri

9:41100%

IMG

di kiri

    Align(
      alignment: Alignment.centerLeft,
      child: Image.asset('assets/logo.png', width: 56),
    )

#### Gambar di Kanan

9:41100%

IMG

di kanan

    Align(
      alignment: Alignment.centerRight,
      child: Image.asset('assets/logo.png', width: 56),
    )

### 2.1 Gambar Kiri dan Kanan Sekaligus (Row + spaceBetween)

Untuk menaruh dua elemen di ujung kiri dan ujung kanan dalam satu baris yang sama, gunakan `Row` dengan `MainAxisAlignment.spaceBetween`.

9:41100%

KIRI

KANAN

Row + spaceBetween

    Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Image.asset('assets/kiri.png', width: 44),
        Image.asset('assets/kanan.png', width: 44),
      ],
    )

### 2.2 Tabel Referensi Alignment

| Properti | Nilai umum | Efek |
|----|----|----|
| `mainAxisAlignment` | `start`, `end`, `center`, `spaceBetween`, `spaceAround`, `spaceEvenly` | Posisi di sepanjang arah utama (vertikal untuk `Column`, horizontal untuk `Row`) |
| `crossAxisAlignment` | `start`, `end`, `center`, `stretch` | Posisi tegak lurus arah utama |
| `Alignment` (dipakai `Align`/`Container`) | `topLeft`, `topCenter`, `topRight`, `centerLeft`, `center`, `centerRight`, `bottomLeft`, `bottomCenter`, `bottomRight` | Menaruh satu widget di titik tertentu dalam ruang yang tersedia |

Align vs Center

`Center` sebenarnya adalah `Align` dengan nilai `alignment: Alignment.center` yang sudah dipersingkat. Gunakan `Center` untuk kasus di tengah, dan `Align` untuk delapan posisi lainnya.

## 03Container, Padding, Margin & Dekorasi

`Container` adalah widget serbaguna: bisa mengatur ukuran, jarak dalam (`padding`), jarak luar (`margin`), warna, sudut membulat, bayangan, hingga border — semua dalam satu widget.

9:41100%

Kartu Info

Dibungkus Container dengan bayangan & sudut membulat

Container + BoxDecoration

    Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 2)),
        ],
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Kartu Info', style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 4),
          Text('Dibungkus Container dengan bayangan & sudut membulat'),
        ],
      ),
    )

| Properti | Kegunaan |
|----|----|
| `padding` | Jarak antara tepi `Container` dengan isi di dalamnya |
| `margin` | Jarak antara `Container` dengan widget di sekelilingnya |
| `decoration` | Warna, `borderRadius`, `border`, `boxShadow` — tidak bisa dipakai bersamaan dengan `color` langsung, pakai `decoration: BoxDecoration(color: ...)` |
| `width` / `height` | Ukuran tetap; kosongkan agar mengikuti ukuran isi |

SizedBox untuk jarak kosong

Untuk sekadar memberi jarak antar-widget (tanpa warna/dekorasi), `SizedBox(height: 12)` atau `SizedBox(width: 12)` lebih ringan dan lebih jelas maksudnya dibanding `Container` kosong.

## 04Teks & Gaya Tulisan

Semua teks pada Flutter ditampilkan lewat widget `Text`, dengan tampilan diatur melalui parameter `style: TextStyle(...)`.

9:41100%

Judul Besar & Tebal

Subjudul berwarna

Paragraf biasa dengan warna abu-abu dan ukuran lebih kecil untuk teks pendukung.

Teks bergaris bawah

Variasi TextStyle

    Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Judul Besar & Tebal',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
        ),
        Text(
          'Subjudul berwarna',
          style: TextStyle(fontSize: 14, color: Colors.indigo, fontWeight: FontWeight.w600),
        ),
        Text(
          'Paragraf biasa dengan warna abu-abu dan ukuran lebih kecil untuk teks pendukung.',
          style: TextStyle(fontSize: 13, color: Colors.grey, height: 1.4),
        ),
        Text(
          'Teks bergaris bawah',
          style: TextStyle(decoration: TextDecoration.underline),
        ),
      ],
    )

| Parameter | Kegunaan |
|----|----|
| `fontSize` | Ukuran huruf (satuan logical pixel) |
| `fontWeight` | `FontWeight.normal`, `w600`, `bold`, dst. |
| `color` | Warna teks |
| `height` | Jarak antar-baris (line-height), relatif terhadap `fontSize` |
| `overflow` + `maxLines` | Memotong teks panjang, misal `overflow: TextOverflow.ellipsis, maxLines: 1` |

## 05Gambar (Image)

Dua sumber gambar paling umum: berkas lokal di folder `assets/` (`Image.asset`) dan gambar dari internet (`Image.network`).

9:41100%

BoxFit.cover

Image.asset

9:41100%

FOTO

Image.network (avatar bulat)

dari assets

    Image.asset(
      'assets/produk.png',
      width: 160,
      height: 100,
      fit: BoxFit.cover,
    )

dari internet, dibuat bulat

    ClipOval(
      child: Image.network(
        'https://contoh.com/foto-profil.jpg',
        width: 100,
        height: 100,
        fit: BoxFit.cover,
        loadingBuilder: (context, child, progress) {
          if (progress == null) return child;
          return const Center(child: CircularProgressIndicator());
        },
        errorBuilder: (context, error, stack) =>
            const Icon(Icons.broken_image, size: 40),
      ),
    )

| Nilai `BoxFit` | Efek |
|----|----|
| `cover` | Mengisi penuh, sebagian gambar bisa terpotong (paling umum untuk foto produk/profil) |
| `contain` | Seluruh gambar terlihat, bisa ada ruang kosong di sisi |
| `fill` | Meregang mengisi penuh, rasio gambar bisa berubah |
| `fitWidth` / `fitHeight` | Menyesuaikan salah satu sisi saja |

Mendaftarkan folder assets

Sebelum `Image.asset` bisa dipakai, folder harus didaftarkan di `pubspec.yaml`:

`flutter:`\
`  assets:`\
`    - assets/`

## 06Tombol (Button)

Flutter menyediakan beberapa jenis tombol dengan gaya visual dan tujuan pemakaian yang berbeda.

9:41100%

Simpan

Batal

Lewati

Elevated · Outlined · Text

9:41100%

♡

\+

IconButton · FloatingActionButton

tiga tombol utama

    ElevatedButton(
      onPressed: () {},
      child: const Text('Simpan'),
    )

    OutlinedButton(
      onPressed: () {},
      child: const Text('Batal'),
    )

    TextButton(
      onPressed: () {},
      child: const Text('Lewati'),
    )

icon & floating action button

    IconButton(
      onPressed: () {},
      icon: const Icon(Icons.favorite_border),
    )

    // dipasang di properti floatingActionButton milik Scaffold
    FloatingActionButton(
      onPressed: () {},
      child: const Icon(Icons.add),
    )

| Tombol | Kapan dipakai |
|----|----|
| `ElevatedButton` | Aksi utama pada halaman (submit, simpan, lanjut) |
| `OutlinedButton` | Aksi sekunder, sejajar dengan tombol utama (batal, kembali) |
| `TextButton` | Aksi ringan/opsional (lewati, lihat lainnya) |
| `IconButton` | Aksi yang cukup diwakili ikon (suka, bagikan, hapus) |
| `FloatingActionButton` | Aksi paling penting di halaman, melayang di sudut layar |

## 07Form Input Teks

`TextFormField` adalah pilihan default untuk input teks karena mendukung validasi bawaan ketika dibungkus `Form`. Untuk kasus sederhana tanpa validasi, `TextField` saja sudah cukup.

←Masuk

EMAILasep@mail.com

PASSWORD••••••••

Masuk

TextFormField di dalam Form

form login sederhana

    final _formKey = GlobalKey<FormState>();
    final _emailController = TextEditingController();
    final _passwordController = TextEditingController();

    Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: 'Email',
              border: OutlineInputBorder(),
            ),
            validator: (v) => (v == null || v.isEmpty) ? 'Email wajib diisi' : null,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _passwordController,
            obscureText: true,
            decoration: const InputDecoration(
              labelText: 'Password',
              border: OutlineInputBorder(),
            ),
            validator: (v) =>
                (v == null || v.length < 6) ? 'Password minimal 6 karakter' : null,
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {
              if (_formKey.currentState!.validate()) {
                // proses login
              }
            },
            child: const Text('Masuk'),
          ),
        ],
      ),
    )

| Properti | Kegunaan |
|----|----|
| `controller` | Membaca/mengatur nilai yang diketik pengguna |
| `decoration` | Label, hint, border, ikon di dalam field |
| `obscureText` | Menyembunyikan karakter (untuk password) |
| `keyboardType` | Jenis keyboard: `emailAddress`, `number`, `phone`, dst. |
| `validator` | Fungsi pengecekan, dijalankan bersamaan saat `_formKey.currentState!.validate()` dipanggil |

Jangan lupa dispose()

Setiap `TextEditingController` yang dibuat wajib dipanggil `.dispose()` di method `dispose()` milik `State`, agar tidak terjadi kebocoran memori.

## 08Input Lainnya: Checkbox, Radio, Switch, Dropdown, Slider

←Pengaturan

✓

Ingat saya

Laki-laki

Perempuan

Notifikasi

Kota Bandar Lampung▾

Volume

Checkbox · Radio · Switch · Dropdown · Slider

Checkbox

    bool _ingatSaya = false;

    CheckboxListTile(
      value: _ingatSaya,
      title: const Text('Ingat saya'),
      onChanged: (v) => setState(() => _ingatSaya = v!),
    )

Radio

    enum JenisKelamin { pria, wanita }
    JenisKelamin? _pilihan = JenisKelamin.pria;

    RadioListTile<JenisKelamin>(
      title: const Text('Laki-laki'),
      value: JenisKelamin.pria,
      groupValue: _pilihan,
      onChanged: (v) => setState(() => _pilihan = v),
    )

Switch

    bool _notifAktif = true;

    SwitchListTile(
      title: const Text('Notifikasi'),
      value: _notifAktif,
      onChanged: (v) => setState(() => _notifAktif = v),
    )

Dropdown & Slider

    String? _kota = 'Bandar Lampung';
    double _volume = 0.4;

    DropdownButtonFormField<String>(
      value: _kota,
      items: const [
        DropdownMenuItem(value: 'Bandar Lampung', child: Text('Kota Bandar Lampung')),
        DropdownMenuItem(value: 'Jakarta', child: Text('Jakarta')),
      ],
      onChanged: (v) => setState(() => _kota = v),
    )

    Slider(
      value: _volume,
      onChanged: (v) => setState(() => _volume = v),
    )

Semua widget ini butuh StatefulWidget

Checkbox, Radio, Switch, Dropdown, dan Slider tidak mengubah tampilannya sendiri — kode di atas wajib berada di dalam `StatefulWidget`, dan setiap `onChanged` memanggil `setState()` agar tampilan diperbarui.

## 09List & Grid: ListView dan GridView

☰Daftar UMKM

WS

Warung Bu Sari

Kuliner · Jl. Melati 10

TB

Toko Pak Budi

Sembako · Jl. Kenanga 5

KC

Kedai Bu Citra

Kopi · Jl. Anggrek 2

ListView.builder + ListTile

☰Produk

Produk A

Produk B

Produk C

Produk D

GridView.builder

ListView.builder

    ListView.builder(
      itemCount: daftarUmkm.length,
      itemBuilder: (context, i) {
        final umkm = daftarUmkm[i];
        return ListTile(
          leading: CircleAvatar(child: Text(umkm.nama[0])),
          title: Text(umkm.nama),
          subtitle: Text('${umkm.kategori} · ${umkm.alamat}'),
          onTap: () {},
        );
      },
    )

GridView.builder

    GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
      ),
      itemCount: daftarProduk.length,
      itemBuilder: (context, i) => Container(
        decoration: BoxDecoration(
          color: Colors.indigo.shade50,
          borderRadius: BorderRadius.circular(8),
        ),
        alignment: Alignment.center,
        child: Text(daftarProduk[i].nama),
      ),
    )

Selalu pakai .builder untuk daftar panjang

`ListView.builder`/`GridView.builder` hanya membuat widget untuk item yang terlihat di layar (lazy loading), jauh lebih hemat memori dibanding `ListView(children: [...])` yang membuat semua item sekaligus.

## 10Card & Kombinasi Layout

`Card` adalah `Container` yang sudah dipercantik (sudut membulat + bayangan tipis bawaan Material Design), sangat umum dipakai membungkus satu item ringkasan.

9:41100%

IMG

Nasi Uduk Spesial

Rp 15.000 · Warung Bu Sari

Card + Row (foto, judul, harga)

    Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network('https://.../produk.jpg', width: 56, height: 56, fit: BoxFit.cover),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text('Nasi Uduk Spesial', style: TextStyle(fontWeight: FontWeight.bold)),
                Text('Rp 15.000 · Warung Bu Sari'),
              ],
            ),
          ],
        ),
      ),
    )

## 11Praktik: Menyusun Halaman Profil Lengkap

Sebagai penutup, seluruh widget pada materi ini digabungkan menjadi satu halaman profil yang realistis: foto di tengah-atas, nama di bawahnya, form untuk mengubah data, sebuah switch, dan tombol simpan di bagian bawah.

←Edit Profil

FOTO

NAMA LENGKAPAsep Trisna Setiawan

EMAILasep@mail.com

Tampilkan email ke publik

Simpan Perubahan

Kombinasi: Center, Form, Switch, Button

edit_profile_page.dart

    class EditProfilePage extends StatefulWidget {
      const EditProfilePage({super.key});
      @override
      State<EditProfilePage> createState() => _EditProfilePageState();
    }

    class _EditProfilePageState extends State<EditProfilePage> {
      final _formKey = GlobalKey<FormState>();
      final _namaController = TextEditingController(text: 'Asep Trisna Setiawan');
      final _emailController = TextEditingController(text: 'asep@mail.com');
      bool _emailPublik = false;

      void _simpan() {
        if (_formKey.currentState!.validate()) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Profil berhasil disimpan')),
          );
        }
      }

      @override
      Widget build(BuildContext context) {
        return Scaffold(
          appBar: AppBar(title: const Text('Edit Profil')),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 1. Foto di tengah-atas -> Center
                  const Center(
                    child: CircleAvatar(
                      radius: 40,
                      backgroundImage: NetworkImage('https://.../foto-profil.jpg'),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // 2. Form input -> TextFormField
                  TextFormField(
                    controller: _namaController,
                    decoration: const InputDecoration(
                      labelText: 'Nama Lengkap',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) => (v == null || v.isEmpty) ? 'Nama wajib diisi' : null,
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Email',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) => (v == null || v.isEmpty) ? 'Email wajib diisi' : null,
                  ),
                  const SizedBox(height: 10),

                  // 3. Switch -> Row + spaceBetween
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Tampilkan email ke publik'),
                    value: _emailPublik,
                    onChanged: (v) => setState(() => _emailPublik = v),
                  ),
                  const SizedBox(height: 10),

                  // 4. Tombol simpan -> ElevatedButton selebar layar
                  ElevatedButton(
                    onPressed: _simpan,
                    style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
                    child: const Text('Simpan Perubahan'),
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
        super.dispose();
      }
    }

Kenapa dibungkus SingleChildScrollView?

Ketika keyboard muncul (saat mengetik di `TextFormField`), tinggi layar yang tersedia berkurang. Tanpa `SingleChildScrollView`, konten yang tidak muat akan memicu error *"RenderFlex overflowed"*. Membungkus `Column` dengan `SingleChildScrollView` membuat halaman bisa digulir sehingga aman dari overflow.

## 12Latihan

1.  Ubah halaman pada Bagian 11 agar foto profil berada di **kiri atas** (bukan tengah), sejajar dengan nama di sampingnya menggunakan `Row`.
2.  Tambahkan `DropdownButtonFormField` untuk memilih kota domisili pada halaman yang sama.
3.  Buat kartu produk (seperti Bagian 10) di dalam `GridView.builder` 2 kolom, menampilkan minimal 6 produk dummy.
4.  Tambahkan `Stack` berisi gambar sampul UMKM dengan label kategori (misal "Kuliner") menumpuk di pojok kiri atas gambar, memakai `Positioned`.
5.  **Tantangan:** gabungkan seluruh latihan di atas menjadi satu halaman "Detail UMKM" yang utuh: gambar sampul dengan label di atasnya, nama & kategori UMKM, tombol "Hubungi" dan "Lihat Produk" berdampingan, lalu daftar produk dalam `GridView` di bawahnya.

Ingat: hampir seluruh tampilan Flutter yang rumit sekalipun hanyalah kombinasi berulang dari `Row`, `Column`, `Stack`, `Container`, dan beberapa widget input. Jika sebuah tampilan terasa sulit dibuat, coba pecah dulu di atas kertas menjadi kotak-kotak sederhana sebelum menerjemahkannya ke kode. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
