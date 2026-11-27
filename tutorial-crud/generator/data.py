"""Daftar project mahasiswa dan rancangan 1 tabel untuk masing-masing.

Sengaja TIDAK memuat nama maupun NPM, karena repo ini terhubung ke GitHub.
Ubah di sini lalu jalankan ulang: python3 generate.py

Bentuk kolom: (nama, tipe, wajib, contoh, opsi_tambahan)
Tipe: teks (butuh max, kecuali teks panjang) | bulat (min) | uang | angka (min, max, presisi)
      | boolean | tanggal | pilihan (opsi)
"""


def teks(nama, contoh, max=100, wajib=True):
    return (nama, "teks", wajib, contoh, {"max": max})


def panjang(nama, contoh, wajib=False):
    return (nama, "teks", wajib, contoh, {})


def bulat(nama, contoh, min=0, wajib=True):
    return (nama, "bulat", wajib, contoh, {"min": min})


def uang(nama, contoh, wajib=True):
    return (nama, "angka", wajib, contoh, {"min": 0, "max": 9999999999.99, "presisi": (12, 2)})


def boolean(nama, contoh):
    return (nama, "boolean", False, contoh, {})


def tanggal(nama, contoh, wajib=True):
    return (nama, "tanggal", wajib, contoh, {})


def pilihan(nama, opsi):
    return (nama, "pilihan", True, opsi[0], {"opsi": opsi, "max": 30})


def P(no, slug, judul, model, path, kolom, cari, tantangan, catatan=None):
    return dict(no=no, slug=slug, judul=judul, model=model, path=path, kolom=kolom,
                cari=cari, tantangan=tantangan, catatan=catatan)


PROJECTS = [
    P(1, "laundrycare", "LaundryCare", "Pesanan", "pesanan", [
        teks("nama_pelanggan", "Rina"),
        pilihan("layanan", ["cuci_kering", "cuci_setrika", "setrika"]),
        ("berat_kg", "angka", True, 3.5, {"min": 0.1, "max": 9999.99, "presisi": (6, 2)}),
        uang("total", 28000),
        pilihan("status", ["diterima", "diproses", "selesai", "diambil"]),
    ], "nama_pelanggan", "Hitung <code>total</code> di service dari <code>berat_kg</code> dan tarif per layanan, supaya klien tidak bisa mengarang harga."),
    P(2, "topup-ml", "Topup ML", "PaketDiamond", "paket-diamond", [
        teks("nama", "Paket Hemat 86"),
        bulat("jumlah_diamond", 86, min=1),
        uang("harga", 22000),
        boolean("aktif", True),
    ], "nama", "Tambahkan query <code>?aktif=true</code> untuk menampilkan paket yang masih dijual saja."),
    P(3, "toko-sepatu", "Toko Sepatu", "Sepatu", "sepatu", [
        teks("nama", "Runner X"), teks("merek", "Kanky"), bulat("ukuran", 42, min=20),
        uang("harga", 350000), bulat("stok", 10),
    ], "nama", "Tambahkan filter <code>?ukuran=42</code> pada daftar sepatu."),
    P(4, "mood-tracker", "Mood Tracker", "CatatanMood", "catatan-mood", [
        tanggal("tanggal", "2026-11-27"),
        pilihan("mood", ["senang", "biasa", "sedih", "marah", "cemas"]),
        panjang("catatan", "Presentasi berjalan lancar"),
    ], "catatan", "Tolak dua catatan pada tanggal yang sama untuk satu pengguna (balas <code>409</code>)."),
    P(5, "klinik-kecantikan", "Klinik Kecantikan", "Treatment", "treatment", [
        teks("nama", "Facial Brightening"), panjang("deskripsi", "Perawatan wajah 5 tahap"),
        bulat("durasi_menit", 60, min=1), uang("harga", 150000),
    ], "nama", "Tambahkan pilihan urutan <code>?urut=harga</code> pada daftar treatment."),
    P(6, "klinik-hewan", "Klinik Hewan", "PasienHewan", "pasien-hewan", [
        teks("nama_hewan", "Milo"), teks("jenis", "Kucing", max=50), bulat("umur_bulan", 14),
        teks("nama_pemilik", "Andi"), panjang("keluhan", "Tidak mau makan sejak kemarin"),
    ], "nama_hewan", "Izinkan pencarian <code>?q=</code> mencocokkan nama hewan <strong>atau</strong> nama pemilik."),
    P(7, "apotek", "Apotek", "Obat", "obat", [
        teks("nama", "Paracetamol 500 mg"), pilihan("kategori", ["bebas", "bebas_terbatas", "keras"]),
        uang("harga", 8000), bulat("stok", 100), panjang("deskripsi", "Pereda demam dan nyeri"),
    ], "nama", "Buat endpoint <code>GET /api/obat/menipis</code> berisi obat dengan stok di bawah 10."),
    P(8, "perpustakaan", "Perpustakaan", "Buku", "buku", [
        teks("judul", "Pemrograman Flutter", max=150), teks("penulis", "Dewi Lestari"),
        bulat("tahun_terbit", 2024, min=1000), bulat("stok", 4),
    ], "judul", "Tolak tahun terbit yang lebih besar dari tahun sekarang."),
    P(9, "kasir-cafe", "Kasir Cafe", "Menu", "menu", [
        teks("nama", "Es Kopi Susu"), pilihan("kategori", ["minuman", "makanan", "camilan"]),
        uang("harga", 18000), boolean("tersedia", True),
    ], "nama", "Tambahkan filter <code>?kategori=minuman</code>."),
    P(10, "toko-hp", "Toko HP", "Handphone", "handphone", [
        teks("merek", "Samsung", max=50), teks("tipe", "Galaxy A16"), bulat("ram_gb", 8, min=1),
        uang("harga", 2999000), bulat("stok", 7),
    ], "tipe", "Tambahkan filter rentang harga <code>?min=</code> dan <code>?max=</code>."),
    P(11, "toko-parfum", "Toko Parfum", "Parfum", "parfum", [
        teks("nama", "Vanilla Breeze"), teks("merek", "HMNS", max=50), bulat("ukuran_ml", 100, min=1),
        uang("harga", 365000), bulat("stok", 12),
    ], "nama", "Tambahkan filter <code>?merek=</code>."),
    P(12, "catatan-pribadi", "Catatan Pribadi", "Catatan", "catatan", [
        teks("judul", "Rencana minggu ini", max=150), panjang("isi", "Selesaikan tugas pemrograman", wajib=True),
        boolean("disematkan", False),
    ], "judul", "Tampilkan catatan yang disematkan paling atas."),
    P(13, "warteg", "Warteg", "Lauk", "lauk", [
        teks("nama", "Orek Tempe"), uang("harga", 4000), bulat("porsi_tersedia", 25),
        panjang("keterangan", "Pedas sedang"),
    ], "nama", "Buat endpoint <code>PUT /api/lauk/{id}/jual</code> yang mengurangi 1 porsi dan menolak bila habis."),
    P(14, "toko-tas", "Toko Tas", "Tas", "tas", [
        teks("nama", "Tote Bag Kanvas"), teks("bahan", "Kanvas", max=50), teks("warna", "Krem", max=30),
        uang("harga", 85000), bulat("stok", 20),
    ], "nama", "Tambahkan filter <code>?warna=</code>."),
    P(15, "toko-laptop", "Toko Laptop", "Laptop", "laptop", [
        teks("merek", "Lenovo", max=50), teks("tipe", "IdeaPad Slim 3"), teks("prosesor", "Ryzen 5 7520U"),
        bulat("ram_gb", 16, min=1), uang("harga", 8499000), bulat("stok", 3),
    ], "tipe", "Tambahkan filter <code>?ram_min=16</code>."),
    P(16, "toko-bunga", "Toko Bunga", "Bunga", "bunga", [
        teks("nama", "Buket Mawar"), teks("warna", "Merah", max=30), uang("harga", 175000),
        bulat("stok", 8), panjang("deskripsi", "10 tangkai mawar segar"),
    ], "nama", "Buat endpoint <code>GET /api/bunga/habis</code> berisi bunga dengan stok 0."),
    P(17, "tugas-harian", "Daftar Tugas Harian", "Tugas", "tugas", [
        teks("judul", "Kerjakan laporan praktikum", max=150), panjang("deskripsi", "Bab 1 sampai 3"),
        tanggal("tenggat", "2026-12-04"), boolean("selesai", False),
    ], "judul", "Tambahkan filter <code>?selesai=false</code> dan urutkan berdasarkan tenggat terdekat."),
    P(18, "dompetku", "DompetKu (Manajemen Keuangan)", "Transaksi", "transaksi", [
        pilihan("jenis", ["pemasukan", "pengeluaran"]), teks("kategori", "Uang saku", max=50),
        uang("jumlah", 500000), tanggal("tanggal", "2026-11-27"), panjang("keterangan", "Kiriman bulanan"),
    ], "kategori", "Buat endpoint <code>GET /api/transaksi/saldo</code> berisi total pemasukan dikurangi pengeluaran."),
    P(19, "manajemen-obat", "Manajemen Obat", "BatchObat", "batch-obat", [
        teks("nama_obat", "Amoxicillin 500 mg"), teks("nomor_batch", "AMX-2611", max=50),
        bulat("jumlah", 200), tanggal("kedaluwarsa", "2028-03-31"),
    ], "nama_obat", "Buat endpoint yang menampilkan batch yang kedaluwarsa dalam 90 hari."),
    P(20, "plantcare", "PlantCare", "Tanaman", "tanaman", [
        teks("nama", "Monstera Ruang Tamu"), teks("jenis", "Monstera deliciosa"),
        bulat("interval_siram_hari", 3, min=1), tanggal("terakhir_disiram", "2026-11-25", wajib=False),
    ], "nama", "Tambahkan field hitungan <code>jadwal_berikutnya</code> pada respons."),
    P(21, "mobil-muatan", "Sistem Mobil Muatan", "Armada", "armada", [
        teks("plat_nomor", "BE 1234 AB", max=15), teks("jenis_kendaraan", "Pickup", max=50),
        bulat("kapasitas_kg", 1000, min=1), pilihan("status", ["tersedia", "dipakai", "perawatan"]),
    ], "plat_nomor", "Tolak plat nomor yang sama dua kali (balas <code>409</code>)."),
    P(22, "toko-elektronik", "Toko Elektronik", "Barang", "barang", [
        teks("nama", "Kipas Angin 16 inci"), teks("kategori", "Rumah tangga", max=50),
        bulat("garansi_bulan", 12), uang("harga", 245000), bulat("stok", 15),
    ], "nama", "Tambahkan filter <code>?kategori=</code>."),
    P(23, "keuangan-bengkel", "Sistem Keuangan Bengkel", "Servis", "servis", [
        teks("nama_pelanggan", "Budi"), teks("jenis_servis", "Ganti oli"), uang("biaya", 75000),
        tanggal("tanggal", "2026-11-27"), boolean("lunas", False),
    ], "nama_pelanggan", "Buat endpoint rekap total biaya yang sudah lunas dan yang belum."),
    P(24, "hackpath", "HackPath", "MateriBelajar", "materi", [
        teks("judul", "Dasar Jaringan Komputer", max=150), pilihan("tingkat", ["pemula", "menengah", "lanjut"]),
        bulat("urutan", 1, min=1), teks("tautan", "https://example.com/materi", max=255, wajib=False),
        boolean("selesai", False),
    ], "judul", "Urutkan daftar berdasarkan <code>urutan</code>.",
      catatan="Tabel ini disusun dengan <strong>asumsi</strong> bahwa HackPath adalah aplikasi jalur materi belajar. Konfirmasikan ke dosen kalau idemu berbeda."),
    P(25, "kantin-bem", "Kantin BEM FIK UBL", "Jajanan", "jajanan", [
        teks("nama", "Risoles Mayo"), teks("penjual", "Stand A"), uang("harga", 5000), bulat("stok", 30),
    ], "nama", "Tambahkan filter <code>?penjual=</code>."),
    P(26, "toko-kucing", "Toko Kucing", "Kucing", "kucing", [
        teks("nama", "Oyen"), teks("ras", "Persia", max=50), bulat("umur_bulan", 4),
        pilihan("jenis_kelamin", ["jantan", "betina"]), uang("harga", 1200000),
    ], "nama", "Tambahkan filter <code>?ras=</code>."),
    P(27, "pet-finder", "Pet Finder", "LaporanHilang", "laporan-hilang", [
        teks("nama_hewan", "Bruno"), teks("jenis", "Anjing", max=50),
        teks("lokasi_terakhir", "Kedaton, Bandar Lampung", max=200), tanggal("tanggal_hilang", "2026-11-20"),
        pilihan("status", ["hilang", "ditemukan"]),
    ], "nama_hewan", "Buat endpoint publik (tanpa login) berisi laporan berstatus hilang."),
    P(28, "smart-camera", "Smart Camera", "Kamera", "kamera", [
        teks("nama", "Kamera Gerbang"), teks("lokasi", "Pintu depan"),
        teks("url_stream", "rtsp://192.168.1.10:554/stream", max=255), boolean("aktif", True),
    ], "nama", "Tolak <code>url_stream</code> yang tidak diawali <code>rtsp://</code> atau <code>http</code>."),
]
