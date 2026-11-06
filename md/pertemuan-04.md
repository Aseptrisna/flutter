<a href="index.html" class="back">← Kembali ke daftar pertemuan</a>

Materi Pemula · Backend Go

# Membangun REST API UMKM dengan Golang dan PostgreSQL

Tutorial langkah demi langkah membangun REST API untuk aplikasi pendataan UMKM, lengkap dengan dokumentasi Swagger: pengguna dapat register, login, membuat UMKM miliknya sendiri, mengelola produk, mengunggah foto, serta melihat UMKM dan produk milik pengguna lain.

Golang→
PostgreSQL (Neon)→
REST API + Swagger

## 01Apa itu Golang

**Golang (Go)** adalah bahasa pemrograman yang dikembangkan oleh Google, dirancang untuk membangun aplikasi backend/server yang cepat, sederhana, dan mudah di-deploy. Go bersifat *compiled* (dikompilasi menjadi satu file binary) sehingga tidak memerlukan runtime tambahan saat dijalankan di server.

Alasan Go banyak dipilih untuk membangun REST API:

- **Performa tinggi** — sekelas bahasa C/C++ untuk urusan kecepatan, namun jauh lebih mudah ditulis.
- **Concurrency bawaan** — melalui *goroutine*, Go dapat menangani ribuan koneksi sekaligus tanpa framework tambahan.
- **Sintaks sederhana** — sengaja dibuat minim fitur agar kode mudah dibaca oleh siapa pun, termasuk tim yang besar.
- **Standard library lengkap** — untuk membuat HTTP server dan JSON, Go tidak selalu membutuhkan framework eksternal.
- **Satu binary, tanpa dependency runtime** — hasil `go build` tinggal dijalankan di server, cocok untuk Docker image yang ringan.

Kenapa Go cocok untuk API UMKM ini?

API yang akan dibangun perlu menangani autentikasi, upload file, dan banyak request dari aplikasi Flutter secara bersamaan. Go menangani ketiganya dengan baik menggunakan tools bawaan tanpa konfigurasi yang rumit.

## 02Instalasi Golang

Unduh dan pasang Go sesuai sistem operasi yang digunakan, lalu pastikan perintah `go` dapat dipanggil dari terminal. Materi ini diverifikasi dengan Go 1.22 ke atas (mendukung method & path parameter pada `net/http`).

| OS | Langkah instalasi |
|----|----|
| Windows | Unduh installer `.msi` dari `go.dev/dl`, jalankan, ikuti wizard hingga selesai. Installer otomatis menambahkan Go ke `PATH`. |
| Linux | Unduh arsip `.tar.gz`, ekstrak ke `/usr/local`, lalu tambahkan `/usr/local/go/bin` ke `PATH` pada `~/.bashrc` atau `~/.zshrc`. |
| macOS | Paling mudah menggunakan Homebrew: `brew install go`. Alternatif lain: unduh installer `.pkg` dari `go.dev/dl`. |

Linux — instalasi manual

    wget https://go.dev/dl/go1.22.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf go1.22.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    source ~/.bashrc

verifikasi instalasi (semua OS)

    go version
    # contoh keluaran: go version go1.22.3 darwin/arm64

## 03Dasar-Dasar Golang

Sebelum membangun API, berikut adalah bagian inti sintaks Go yang akan terus dipakai sepanjang tutorial ini.

### 3.1 Package, Import, dan Fungsi main

Setiap berkas Go wajib berada dalam sebuah *package*. Program yang dapat dijalankan langsung wajib memiliki package bernama `main` beserta fungsi `main()`.

main.go

    package main

    import "fmt"

    func main() {
        fmt.Println("Halo, UMKM API")
    }

### 3.2 Variabel dan Tipe Data

    var nama string = "Warung Bu Sari"
    kategori := "Kuliner"      // deklarasi singkat, tipe otomatis dikenali
    var stok int = 25
    var harga float64 = 15000.0
    var aktif bool = true

### 3.3 Struct — Merepresentasikan Data

`struct` pada Go dipakai untuk merepresentasikan sebuah entitas, misalnya data *user* atau *UMKM*. Tag `json:"..."` menentukan nama field saat data diubah menjadi JSON.

    type User struct {
        ID       int64  `json:"id"`
        Nama     string `json:"nama"`
        Email    string `json:"email"`
        Password string `json:"-"` // tanda "-" berarti tidak pernah dikirim ke klien
    }

### 3.4 Function, Multiple Return Value, dan Error

Pola paling khas di Go: sebuah fungsi hampir selalu mengembalikan **nilai hasil** beserta **error** sekaligus. Pengecekan error dilakukan segera setelah pemanggilan fungsi.

    func bagi(a, b int) (int, error) {
        if b == 0 {
            return 0, errors.New("tidak boleh membagi dengan nol")
        }
        return a / b, nil
    }

    func main() {
        hasil, err := bagi(10, 2)
        if err != nil {
            fmt.Println("terjadi error:", err)
            return
        }
        fmt.Println("hasil:", hasil)
    }

### 3.5 Slice, Map, dan Pointer

    umkmList := []string{"Warung Bu Sari", "Toko Pak Budi"} // slice (array dinamis)
    umkmList = append(umkmList, "Kedai Kopi Senja")

    filter := map[string]string{"kategori": "kuliner"} // map (key-value)

    func naikkanStok(stok *int) { // pointer: mengubah nilai asli, bukan salinan
        *stok = *stok + 1
    }

Cukup untuk melanjutkan

Lima konsep di atas — package, struct, function multi-return, error, dan slice/map — sudah cukup untuk memahami seluruh kode API pada materi ini. Konsep lanjutan seperti interface dan goroutine akan dijelaskan langsung pada bagian implementasi.

## 04Apa itu PostgreSQL

**PostgreSQL** adalah sistem basis data relasional (RDBMS) open-source yang dipakai untuk menyimpan data secara terstruktur dalam bentuk tabel-tabel yang saling berelasi. Pada aplikasi UMKM ini, PostgreSQL dipakai menyimpan tiga entitas utama yang saling berhubungan: **users**, **umkm**, dan **produk**.

PostgreSQL dipilih dibanding basis data lain karena:

- Mendukung relasi antar-tabel (foreign key) dengan baik — cocok untuk data "1 user punya 1 UMKM, 1 UMKM punya banyak produk".
- Gratis, open-source, dan sangat stabil untuk skala kecil maupun besar.
- Didukung penuh oleh driver Go modern seperti `pgx`.
- Tersedia versi cloud gratis untuk development, salah satunya **Neon**, sehingga tidak wajib instalasi lokal.

## 05Instalasi PostgreSQL (Opsional untuk Lokal)

Instalasi lokal berguna untuk latihan dasar SQL di komputer sendiri. Untuk pengembangan API pada tutorial ini, disarankan langsung memakai Neon (lihat bagian 07) agar tidak perlu mengelola server database sendiri.

| OS | Langkah instalasi |
|----|----|
| Windows | Unduh installer dari `postgresql.org/download/windows`, jalankan wizard, catat password superuser `postgres` yang dibuat saat instalasi. |
| Linux (Debian/Ubuntu) | `sudo apt update && sudo apt install postgresql postgresql-contrib`, lalu service otomatis berjalan. |
| macOS | `brew install postgresql@16`, kemudian `brew services start postgresql@16`. |

verifikasi instalasi

    psql --version
    psql -U postgres -h localhost   # masuk ke prompt psql

## 06Dasar-Dasar PostgreSQL

### 6.1 Membuat Tabel

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );

### 6.2 Relasi dengan Foreign Key

Foreign key memastikan setiap baris pada tabel `umkm` selalu terhubung ke satu baris pada tabel `users` yang benar-benar ada. Tambahan `ON DELETE CASCADE` membuat baris terkait ikut terhapus otomatis — dipakai nanti agar produk ikut terhapus saat UMKM induknya dihapus.

    CREATE TABLE umkm (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        foto VARCHAR(255)
    );

### 6.3 Query Dasar

    -- menambah data
    INSERT INTO users (nama, email, password) VALUES ('Asep', 'asep@mail.com', '******');

    -- mengambil data dengan join antar-tabel
    SELECT umkm.nama, users.nama AS pemilik
    FROM umkm
    JOIN users ON umkm.user_id = users.id
    WHERE umkm.id = 1;

    -- mengubah dan menghapus data
    UPDATE users SET nama = 'Asep Trisna' WHERE id = 1;
    DELETE FROM umkm WHERE id = 3;

Cukup untuk melanjutkan

Tiga hal di atas — membuat tabel, foreign key, dan query CRUD dasar — adalah fondasi seluruh query yang dipakai pada Bagian 10.

## 07Memakai PostgreSQL Neon untuk Development

**Neon** (neon.tech) adalah layanan PostgreSQL cloud dengan paket gratis yang sangat praktis untuk development, karena tidak perlu instalasi ataupun menjaga server basis data tetap menyala di komputer sendiri.

1.  Buat akun di `neon.tech`, lalu buat **Project** baru (pilih region yang terdekat, misalnya Singapore).
2.  Neon otomatis membuat sebuah database dan menyediakan **Connection String** pada dashboard project.
3.  Salin connection string tersebut, formatnya menyerupai:

contoh connection string

    postgresql://neondb_owner:password@ep-xxxx-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

4.  Simpan connection string tersebut pada berkas `.env` di project Go (dijelaskan pada bagian berikutnya). **Jangan pernah** mengunggah berkas `.env` ke repository Git.

Kenapa Neon dipilih untuk latihan ini?

Mahasiswa tidak perlu menginstal PostgreSQL di laptop masing-masing, tidak perlu mengatur user/permission database secara manual, dan connection string yang sama dapat langsung dipakai baik saat development maupun ketika API di-deploy nanti.

## 08Setup Project API UMKM di Visual Studio Code

Buat folder project baru, lalu inisialisasi module Go dan pasang seluruh dependency yang dibutuhkan.

terminal VS Code

    mkdir umkm-api && cd umkm-api
    go mod init umkm-api

    go get github.com/jackc/pgx/v5/pgxpool
    go get github.com/golang-jwt/jwt/v5
    go get golang.org/x/crypto/bcrypt
    go get github.com/joho/godotenv
    go get golang.org/x/time/rate

    # untuk dokumentasi Swagger (dipakai di Bagian 11)
    go get github.com/swaggo/http-swagger/v2
    go get github.com/swaggo/swag
    go install github.com/swaggo/swag/cmd/swag@latest

Struktur folder yang dipakai sepanjang tutorial ini — berlapis agar mudah dikembangkan, namun tetap sederhana untuk skala belajar:

struktur folder

    umkm-api/
    ├── cmd/
    │   └── api/
    │       └── main.go
    ├── internal/
    │   ├── config/
    │   │   └── config.go
    │   ├── domain/
    │   │   ├── user.go
    │   │   ├── umkm.go
    │   │   └── produk.go
    │   ├── repository/
    │   │   ├── user_repository.go
    │   │   ├── umkm_repository.go
    │   │   └── produk_repository.go
    │   ├── service/
    │   │   ├── auth_service.go
    │   │   ├── umkm_service.go
    │   │   ├── produk_service.go
    │   │   └── pagination.go
    │   ├── handler/
    │   │   ├── response.go
    │   │   ├── upload.go
    │   │   ├── swagger_types.go
    │   │   ├── auth_handler.go
    │   │   ├── umkm_handler.go
    │   │   └── produk_handler.go
    │   └── middleware/
    │       ├── auth.go
    │       └── ratelimit.go
    ├── docs/                  # hasil generate "swag init" (Bagian 11)
    ├── migrations/
    │   ├── 000001_init.up.sql
    │   └── 000001_init.down.sql
    ├── uploads/
    │   ├── umkm/
    │   └── produk/
    ├── .env.example
    ├── go.mod
    └── go.sum

### 8.1 Fungsi Setiap Folder

Sebelum masuk ke implementasi, pahami dulu **tugas masing-masing folder** dan arah ketergantungannya: `domain` tidak bergantung ke folder mana pun, `repository` hanya bergantung ke `domain`, `service` bergantung ke `repository` (lewat interface) dan `domain`, sedangkan `handler` bergantung ke `service`. Panahnya selalu mengarah ke dalam — **tidak pernah sebaliknya** (misalnya `domain` memanggil `service`). Aturan arah ini yang membuat kode mudah diuji dan mudah ditiru untuk entitas baru.

| Folder / Berkas | Tugasnya apa |
|----|----|
| `cmd/api/main.go` | Satu-satunya *pintu masuk* program. Membuat koneksi database, merakit (meng-*inject*) semua repository → service → handler, mendaftarkan route, lalu menyalakan server. Tidak ada logika bisnis di sini. |
| `internal/config` | Membaca environment variable (`.env`) menjadi satu struct `Config`. Satu-satunya tempat kode lain boleh "bertanya" nilai konfigurasi — tidak ada `os.Getenv` tersebar di file lain. |
| `internal/domain` | Definisi *entitas* (`User`, `Umkm`, `Produk`) dan *sentinel error* bersama (`ErrNotFound`, dst). Hanya berisi struct dan konstanta — tidak ada query SQL, tidak ada `net/http`. Kalau nanti butuh entitas baru (misalnya `Kategori`), mulai dari sini. |
| `internal/repository` | Satu-satunya lapisan yang *boleh* menulis SQL. Tugasnya murni menerjemahkan struct Go ⇄ baris tabel database. Tidak tahu dan tidak peduli soal aturan bisnis (misalnya "1 user cuma boleh 1 UMKM") — itu tugas `service`. |
| `internal/service` | Tempat *aturan bisnis* hidup: validasi input, pengecekan kepemilikan (otorisasi), aturan "1 user 1 UMKM", normalisasi pagination. Service memanggil repository lewat *interface*, bukan struct konkret, supaya saat unit test bisa diganti dengan repository palsu (fake). |
| `internal/handler` | Jembatan antara dunia HTTP dan dunia Go biasa: membaca `r.Body`/`r.FormValue`/`r.PathValue`, memanggil satu fungsi service, lalu mengubah hasil atau error-nya menjadi response JSON dengan kode status yang tepat. Juga tempat menaruh komentar anotasi Swagger (Bagian 11). |
| `internal/middleware` | Fungsi "pembungkus" yang berjalan *sebelum* handler asli dipanggil — dipakai lintas banyak endpoint sekaligus, seperti memeriksa token JWT atau membatasi laju request. Tidak ditempel ke satu entitas tertentu. |
| `docs/` | Hasil otomatis perintah `swag init` (Bagian 11) — berisi `swagger.json`, dsb. Jangan diedit manual; akan tertimpa setiap kali `swag init` dijalankan ulang. |
| `migrations/` | Skrip SQL yang mendefinisikan skema tabel, dikelola dengan CLI `golang-migrate` (pasangan berkas `*.up.sql`/`*.down.sql` bernomor urut). Dijalankan terhadap database (Neon atau lokal) sebelum API pertama kali dipakai, dan lagi setiap kali ada perubahan skema. |
| `uploads/` | Folder fisik tempat berkas foto yang diunggah pengguna benar-benar disimpan di disk server, dipisah per jenis entitas (`umkm/`, `produk/`). |
| `.env` / `.env.example` | `.env.example` adalah contoh/dokumentasi variabel yang dibutuhkan (boleh di-commit). `.env` adalah isian asli dengan nilai rahasia milik masing-masing developer (wajib masuk `.gitignore`, jangan pernah di-commit). |

Kenapa penting dipahami sebelum menulis kode?

Struktur ini bukan sekadar rapi-rapi folder — ia memaksa pemisahan tanggung jawab. Begitu paham polanya, menambah fitur baru (misalnya CRUD "ulasan" atau "kategori") tinggal mengulang lima langkah yang sama: tambah struct di `domain`, tambah query di `repository`, tambah aturan bisnis di `service`, tambah endpoint di `handler`, lalu daftarkan route-nya di `main.go`.

.env.example

    DATABASE_URL=postgresql://neondb_owner:password@ep-xxxx.aws.neon.tech/neondb?sslmode=require
    JWT_SECRET=ganti-dengan-string-acak-yang-panjang
    PORT=8080
    UPLOAD_DIR=./uploads

Salin berkas tersebut menjadi `.env` lalu isi dengan connection string Neon milik masing-masing. Tambahkan juga `.env` ke dalam `.gitignore`.

## 09Desain Database dan Kontrak API

Sebelum menulis kode, tentukan dahulu relasi data dan kontrak setiap endpoint agar implementasi terarah.

relasi data

    users (1) ────── (1) umkm ────── (banyak) produk
      │                    │
      id                 user_id  →  merujuk ke users.id
                            id
                              └───  umkm_id  →  merujuk ke umkm.id (pada produk)

Satu akun (`users`) hanya boleh memiliki satu UMKM, dan satu UMKM dapat memiliki banyak produk. Aturan ini akan dijaga pada lapisan *service*, bukan hanya di database.

### 9.1 Kontrak Endpoint

| Method | Path | Akses | Deskripsi |
|----|----|----|----|
| `POST` | `/api/auth/register` | Publik | Mendaftarkan akun baru |
| `POST` | `/api/auth/login` | Publik (rate limited) | Login, mengembalikan JWT token. Dibatasi 5 percobaan/menit per IP |
| `GET` | `/api/profile` | Login | Melihat profil akun sendiri |
| `PUT` | `/api/profile` | Login | Mengubah nama/email profil |
| `PUT` | `/api/profile/password` | Login | Mengubah password (wajib password lama) |
| `GET` | `/api/umkm?q=&page=&limit=` | Publik | Melihat seluruh UMKM, mendukung pencarian nama (`q`) dan pagination |
| `GET` | `/api/umkm/saya` | Login | Melihat UMKM milik akun sendiri |
| `GET` | `/api/umkm/{id}` | Publik | Melihat detail satu UMKM |
| `POST` | `/api/umkm` | Login | Membuat UMKM milik sendiri (foto opsional, `multipart/form-data`) |
| `PUT` | `/api/umkm/{id}` | Login (pemilik) | Mengubah data UMKM sendiri, foto opsional diganti |
| `DELETE` | `/api/umkm/{id}` | Login (pemilik) | Menghapus UMKM sendiri beserta seluruh produknya |
| `GET` | `/api/umkm/{id}/produk?page=&limit=` | Publik | Melihat seluruh produk pada satu UMKM, mendukung pagination |
| `POST` | `/api/umkm/{id}/produk` | Login (pemilik) | Menambahkan produk pada UMKM sendiri (foto `multipart/form-data`) |
| `GET` | `/api/produk/{id}` | Publik | Melihat detail satu produk |
| `PUT` | `/api/produk/{id}` | Login (pemilik) | Mengubah data produk, foto opsional diganti |
| `DELETE` | `/api/produk/{id}` | Login (pemilik) | Menghapus produk beserta foto di folder lokal |

Kenapa path produk terpisah dari umkm/{id}/produk?

Membuat produk butuh konteks UMKM induknya (`POST /api/umkm/{id}/produk`), sedangkan operasi pada satu produk spesifik — detail, update, delete — cukup mengacu ke ID produk itu sendiri (`/api/produk/{id}`). Kepemilikan tetap divalidasi di service dengan menelusuri `produk → umkm → user_id`, jadi tidak ada celah pengguna lain mengubah produk yang bukan miliknya.

### 9.2 Format Respons

respons sukses

    { "data": { "id": 1, "nama": "Warung Bu Sari" } }

respons error

    { "error": { "message": "email sudah terdaftar", "code": "CONFLICT" } }

respons list dengan pagination

    {
      "data": [ { "id": 1, "nama": "Warung Bu Sari" } ],
      "meta": { "page": 1, "limit": 10, "total": 1 }
    }

Field foto berisi path relatif, bukan URL penuh

Agar aman dipindah-pindah server (localhost, staging, produksi), field `foto` pada respons hanya berisi path relatif seperti `"umkm/1699999999.jpg"`. Klien (aplikasi Flutter) tinggal menggabungkannya sendiri: `base_url + "/uploads/" + foto`.

## 10Implementasi API UMKM

Kode disusun berlapis: `domain` (struktur data) → `repository` (akses database) → `service` (aturan bisnis) → `handler` (menerima HTTP request) → `middleware` + `main.go` (menyatukan semuanya).

### 10.1 Migration — Membuat Tabel

Migration dikelola dengan <a href="https://github.com/golang-migrate/migrate" target="_blank" rel="noopener">golang-migrate</a>, tapi dipakai sebagai **library Go biasa** lewat satu tool kecil (`cmd/migrate`) yang kita tulis sendiri — **bukan** CLI eksternal yang harus diinstal terpisah. Keuntungannya: perintahnya persis sama di Windows, macOS, maupun Linux (`go run ./cmd/migrate ...`), tidak perlu mengatur `PATH` tambahan, dan tidak perlu `export` environment variable manual — sama seperti menjalankan `go run ./cmd/api` yang sudah terbiasa dipakai. Setiap migration terdiri dari **dua berkas berpasangan**: `*.up.sql` (menerapkan perubahan) dan `*.down.sql` (membatalkannya), diberi nomor urut di depan nama supaya urutan eksekusinya jelas dan bisa di-rollback.

#### Tambahkan dependency golang-migrate

terminal VS Code, dari root project umkm-api

    go get github.com/golang-migrate/migrate/v4
    go get github.com/golang-migrate/migrate/v4/database/postgres

#### Buat folder dan berkas migration

Buat folder `migrations/` di root project, lalu buat dua berkas kosong di dalamnya dengan nama persis seperti ini (lewat VS Code biasa, klik kanan folder → New File):

    migrations/000001_init.up.sql
    migrations/000001_init.down.sql

Penomoran `000001_` di depan nama penting — itu yang dipakai `golang-migrate` untuk menentukan urutan eksekusi. Migration berikutnya (misalnya nanti menambah kolom) dibuat dengan nomor urut lanjutannya, misal `000002_tambah_kolom.up.sql`. Isi kedua berkas `000001` seperti berikut.

migrations/000001_init.up.sql

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE umkm (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        deskripsi TEXT,
        alamat VARCHAR(255),
        foto VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE produk (
        id SERIAL PRIMARY KEY,
        umkm_id INTEGER NOT NULL REFERENCES umkm(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        harga NUMERIC(12,2) NOT NULL DEFAULT 0,
        deskripsi TEXT,
        foto VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

`user_id UNIQUE` pada tabel `umkm` memaksa di level database bahwa satu user hanya boleh punya satu baris UMKM — lapisan pertahanan tambahan selain pengecekan di service.

migrations/000001_init.down.sql

    DROP TABLE IF EXISTS produk;
    DROP TABLE IF EXISTS umkm;
    DROP TABLE IF EXISTS users;

Urutan `DROP TABLE` di berkas down sengaja dibalik (anak dulu baru induk) karena foreign key `umkm → users` dan `produk → umkm` akan menolak tabel induknya dihapus duluan selama masih ada tabel anak yang mereferensikannya.

#### Tool migration sendiri — cmd/migrate/main.go

Daripada menginstal CLI `migrate` terpisah (yang caranya beda-beda per OS dan sering gagal karena isu `PATH`/tag driver), buat satu program Go kecil yang membungkus *library* `golang-migrate` dan membaca `.env` otomatis lewat `godotenv` — persis seperti yang sudah dilakukan `cmd/api/main.go`:

cmd/migrate/main.go

    package main

    import (
        "errors"
        "fmt"
        "log"
        "os"
        "strconv"

        "github.com/golang-migrate/migrate/v4"
        _ "github.com/golang-migrate/migrate/v4/database/postgres"
        _ "github.com/golang-migrate/migrate/v4/source/file"
        "github.com/joho/godotenv"
    )

    func main() {
        _ = godotenv.Load()

        dbURL := os.Getenv("DATABASE_URL")
        if dbURL == "" {
            log.Fatal("DATABASE_URL belum diatur di berkas .env")
        }

        if len(os.Args) < 2 {
            log.Fatal("penggunaan: go run ./cmd/migrate  [angka versi]")
        }

        m, err := migrate.New("file://migrations", dbURL)
        if err != nil {
            log.Fatalf("gagal membuka migrations: %v", err)
        }

        switch os.Args[1] {
        case "up":
            err = m.Up()
        case "down":
            err = m.Steps(-1)
        case "version":
            version, dirty, verErr := m.Version()
            if verErr != nil {
                log.Fatalf("gagal membaca versi: %v", verErr)
            }
            fmt.Printf("versi migration saat ini: %d (dirty: %v)\n", version, dirty)
            return
        case "force":
            if len(os.Args) < 3 {
                log.Fatal("penggunaan: go run ./cmd/migrate force ")
            }
            version, convErr := strconv.Atoi(os.Args[2])
            if convErr != nil {
                log.Fatalf("angka versi tidak valid: %v", convErr)
            }
            err = m.Force(version)
        default:
            log.Fatalf("perintah tidak dikenal: %q (pakai up/down/version/force)", os.Args[1])
        }

        if err != nil && !errors.Is(err, migrate.ErrNoChange) {
            log.Fatalf("migration gagal: %v", err)
        }
        fmt.Println("selesai")
    }

Dua baris `_ "github.com/golang-migrate/migrate/v4/database/postgres"` dan `_ "github.com/golang-migrate/migrate/v4/source/file"` adalah *blank import* — hanya menjalankan efek sampingnya (mendaftarkan driver Postgres dan pembaca berkas `.sql` dari folder lokal ke dalam `golang-migrate`) tanpa memanggil fungsi apa pun darinya secara langsung, makanya namanya diganti `_`.

#### Menjalankan migration

Begini cara makainya — **sama persis** di Windows (CMD maupun PowerShell), macOS, dan Linux, dari root project `umkm-api`:

menerapkan migration (up)

    go run ./cmd/migrate up

membatalkan 1 migration terakhir (down)

    go run ./cmd/migrate down

cek versi migration yang sedang aktif

    go run ./cmd/migrate version

memperbaiki status "dirty" (lihat Bagian 10.2)

    go run ./cmd/migrate force 1

✓ Diverifikasi

Seluruh perintah di atas sudah dicoba langsung terhadap Postgres lokal sungguhan dari kondisi database kosong: `go run ./cmd/migrate up` berhasil membuat 4 tabel (`users`, `umkm`, `produk`, `schema_migrations`) tanpa perlu `export` apa pun lebih dulu, `go run ./cmd/migrate version` menampilkan `versi migration saat ini: 1 (dirty: false)`, dan `go run ./cmd/migrate down` berhasil mengembalikan ke kondisi semula.

Kenapa pakai golang-migrate, bukan psql manual?

Dengan `psql -f file.sql`, kamu harus ingat sendiri file mana yang sudah/belum dijalankan dan tidak ada cara mudah untuk *rollback*. `golang-migrate` mencatat nomor versi migration terakhir di tabel `schema_migrations` pada database itu sendiri, jadi perintah `up` hanya menjalankan migration yang belum diterapkan, dan `down` bisa membatalkan perubahan secara terurut. Setiap kali ada perubahan skema baru (misalnya tambah kolom), cukup buat sepasang berkas baru dengan nomor urut lanjutannya (lihat "Buat folder dan berkas migration" di atas) — jangan edit ulang file migration yang sudah pernah dijalankan ke database manapun.

### 10.2 Mengatasi Error Migration

Bagian ini bagian "P3K" migration — kumpulkan di sini supaya kalau `go run ./cmd/migrate up` gagal, kamu tidak perlu scroll ke atas mencari-cari, cukup cocokkan pesan errornya dengan tabel di bawah.

Ingat: tutorial ini memakai Neon (cloud), bukan Postgres lokal

Sesuai Bagian 07, `DATABASE_URL` di `.env` kamu seharusnya menunjuk ke **Neon** (`...aws.neon.tech/...?sslmode=require`), bukan `localhost` — karena itu, kamu **tidak wajib** punya `psql` ter-install di komputer (itu justru alasan Neon dipilih). Semua langkah di bawah menyediakan cara verifikasi lewat **SQL Editor di dashboard Neon** (buka project-mu di <a href="https://console.neon.tech" target="_blank" rel="noopener">console.neon.tech</a> → menu **SQL Editor** di sidebar) sebagai cara utama, bukan lewat terminal.

#### Langkah 0 — Sudah dicoba berkali-kali dan masih error? Reset total dari nol

Kalau migration sudah dijalankan berulang kali dengan berbagai cara sebelumnya (termasuk sebelum tutorial ini diperbarui, waktu masih pakai CLI `migrate` terpisah), kemungkinan besar databasenya sekarang dalam kondisi "nanggung" — sebagian tabel sudah ada, sebagian belum, atau tabel pencatat `schema_migrations` menyimpan versi yang tidak cocok dengan tabel yang benar-benar ada. Daripada menebak-nebak kondisinya sekarang, **paling cepat reset total dari nol** (aman dilakukan karena ini masih database latihan, belum ada data penting):

1.  Buka <a href="https://console.neon.tech" target="_blank" rel="noopener">console.neon.tech</a>, masuk ke project-mu, klik menu **SQL Editor** di sidebar kiri.
2.  Jalankan query ini untuk menghapus **semua** tabel termasuk tabel pencatat migration, benar-benar kembali ke database kosong:

    SQL Editor Neon

        DROP TABLE IF EXISTS produk, umkm, users, schema_migrations CASCADE;

3.  Jalankan `SELECT * FROM information_schema.tables WHERE table_schema = 'public';` di SQL Editor yang sama — hasilnya harus **kosong (0 rows)**. Kalau masih ada baris tersisa, ulangi langkah 2 untuk tabel yang tersisa.
4.  Kembali ke terminal VS Code, pastikan `.env` berisi `DATABASE_URL` Neon yang benar (lihat catatan di atas), lalu jalankan dari root project `umkm-api`:

    

        go run ./cmd/migrate up

5.  Verifikasi lagi lewat SQL Editor dengan query yang sama di langkah 3 — sekarang harus muncul **4 baris**: `users`, `umkm`, `produk`, `schema_migrations`.

Kalau reset total ini *masih* gagal (bukan cuma "sudah dicoba, capek, ingin cara cepat" tapi beneran error lagi dari kondisi benar-benar kosong), baru lanjut ke Langkah 1-4 di bawah untuk mendiagnosis penyebabnya satu per satu.

#### Langkah 1 — Pastikan isi berkas migration persis seperti ini

Penyebab error yang paling sering luput dicek: isi `migrations/000001_init.up.sql` atau `.down.sql` ada yang salah ketik (titik koma hilang, nama kolom beda, urutan tabel tertukar). Buka kedua berkas itu dan **samakan persis** dengan isi berikut sebelum lanjut ke langkah berikutnya:

migrations/000001_init.up.sql

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE umkm (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        deskripsi TEXT,
        alamat VARCHAR(255),
        foto VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

    CREATE TABLE produk (
        id SERIAL PRIMARY KEY,
        umkm_id INTEGER NOT NULL REFERENCES umkm(id) ON DELETE CASCADE,
        nama VARCHAR(150) NOT NULL,
        harga NUMERIC(12,2) NOT NULL DEFAULT 0,
        deskripsi TEXT,
        foto VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

migrations/000001_init.down.sql

    DROP TABLE IF EXISTS produk;
    DROP TABLE IF EXISTS umkm;
    DROP TABLE IF EXISTS users;

Tiga hal yang wajib persis: (1) urutan `CREATE TABLE` di `up.sql` harus `users` → `umkm` → `produk`, karena `umkm` mereferensikan `users` dan `produk` mereferensikan `umkm` lewat `REFERENCES` — kalau urutannya dibalik, Postgres akan menolak dengan error *relation "users" does not exist*; (2) urutan `DROP TABLE` di `down.sql` harus kebalikannya (`produk` dulu baru `umkm`, baru `users`); (3) setiap pernyataan SQL diakhiri titik koma `;` — satu titik koma hilang bisa membuat `golang-migrate` gagal mem-parsing berkas dengan pesan error yang kadang tidak jelas menunjuk ke baris mana.

#### Langkah 2 — Pastikan dependency-nya ter-pasang dan tool-nya bisa di-build

cek build tanpa menjalankan

    go build ./cmd/migrate

Kalau muncul error `missing go.sum entry`, berarti ada dependency yang belum lengkap ter-download — jalankan `go mod tidy` lalu ulangi. Kalau muncul `package github.com/golang-migrate/migrate/v4 is not in std` atau sejenisnya, berarti langkah `go get` di Bagian 10.1 belum dijalankan atau gagal — ulangi lagi sambil pastikan koneksi internet lancar.

#### Langkah 3 — Pastikan `.env` berisi `DATABASE_URL` yang benar

Karena tool `cmd/migrate` membaca `.env` otomatis lewat `godotenv` (sama seperti `cmd/api`), **tidak perlu `export` manual sama sekali** di langkah ini — beda dengan CLI `migrate` eksternal yang mengharuskan environment variable di-set di shell. Cukup buka `.env` dan pastikan baris `DATABASE_URL=...` ada isinya dan sesuai (Neon pakai `?sslmode=require`, Postgres lokal pakai `?sslmode=disable`). Kalau `.env` tidak ada sama sekali atau baris itu kosong, tool akan berhenti dengan pesan jelas: `DATABASE_URL belum diatur di berkas .env`.

#### Langkah 4 — Jalankan migration, lalu verifikasi tabelnya benar-benar terbentuk

terapkan migration

    go run ./cmd/migrate up

Kalau berhasil, akan muncul tulisan `selesai` tanpa pesan error di atasnya. Jangan berhenti di sini — **verifikasi langsung ke database** supaya yakin tabelnya benar-benar ada, bukan cuma percaya output program. Karena databasenya di Neon, cara paling praktis adalah lewat **SQL Editor di dashboard Neon** (tidak perlu `psql` ter-install):

SQL Editor Neon (console.neon.tech)

    SELECT * FROM information_schema.tables WHERE table_schema = 'public';

Kalau kebetulan sudah punya `psql` ter-install, boleh juga langsung dari terminal:

alternatif — psql dari terminal (opsional)

    psql "$DATABASE_URL" -c "\dt"

Hasilnya harus menampilkan empat tabel: `users`, `umkm`, `produk`, dan `schema_migrations` (tabel internal milik `golang-migrate` untuk mencatat versi). Kalau sampai langkah ini masih ada error, baru cocokkan pesan errornya persis dengan tabel di bawah.

#### Tabel error yang sering muncul

| Pesan error | Penyebab | Perbaikan |
|----|----|----|
| `DATABASE_URL belum diatur di berkas .env` | Berkas `.env` tidak ada di root project, atau ada tapi baris `DATABASE_URL=...` kosong/salah ketik nama variabelnya. | Pastikan ada berkas bernama persis `.env` (bukan `.env.txt` atau `env`) di folder yang sama dengan `go.mod`, isinya ada baris `DATABASE_URL=postgresql://...` tanpa spasi di sekitar tanda `=`. |
| `missing go.sum entry for module providing package github.com/lib/pq` | Dependency driver Postgres untuk `golang-migrate` belum lengkap ter-download ke `go.sum`. | Jalankan `go get github.com/golang-migrate/migrate/v4/database/postgres` lagi (lihat Bagian 10.1), atau jalankan `go mod tidy`. |
| `dial tcp 127.0.0.1:5432: connect: connection refused` | `DATABASE_URL` menunjuk ke Postgres lokal (`localhost:5432`) padahal tutorial ini memakai Neon — biasanya kecopy dari `.env.example` bawaan tanpa diganti ke connection string Neon milik sendiri. | Buka `.env`, pastikan `DATABASE_URL` adalah connection string dari dashboard Neon (Bagian 07), bukan `localhost`. |
| `unrecognized configuration parameter "channel_binding"` / koneksi gagal padahal connection string dari Neon di-copy persis | Dashboard Neon kadang menyertakan `&channel_binding=require` di akhir connection string saat tombol "Copy" ditekan. Driver Postgres yang dipakai `golang-migrate` (`lib/pq`) tidak mengenali parameter ini dan meneruskannya mentah-mentah ke server, yang lalu menolaknya. | Hapus bagian `&channel_binding=require` dari `DATABASE_URL` di `.env` — cukup sisakan sampai `?sslmode=require`. Koneksi tetap aman karena `sslmode=require` saja sudah cukup untuk enkripsi TLS ke Neon. |
| Error koneksi/timeout hanya di percobaan **pertama** setelah lama tidak dipakai, lalu normal kalau dicoba lagi | Neon tier gratis otomatis "menidurkan" database (*scale to zero*) setelah beberapa menit tidak ada aktivitas, untuk menghemat resource. Koneksi pertama setelah idle perlu beberapa detik untuk membangunkannya kembali, dan kadang keburu dianggap timeout. | Coba jalankan ulang perintah yang sama sekali lagi — kalau berhasil di percobaan kedua tanpa ada yang diubah, ini penyebabnya, bukan ada yang salah di kode/konfigurasi. |
| `Dirty database version 1. Fix and force version.` | Migration sempat gagal di tengah jalan (misalnya koneksi putus atau ada typo SQL), jadi `golang-migrate` berhenti dan menandai versi itu "kotor" supaya tidak dijalankan ulang begitu saja. | Perbaiki dulu penyebab SQL-nya kalau ada, lalu paksa versi tracking kembali bersih dengan `go run ./cmd/migrate force 1` (angka sesuai nomor migration terakhir), baru jalankan `up` lagi. Kalau bingung atau sudah dicoba berkali-kali, lebih cepat langsung reset total (Langkah 0 di atas). |
| `relation "users" already exists` | Tabelnya sudah pernah terbentuk dari percobaan migration sebelumnya, tapi `golang-migrate` belum tahu soal itu karena tabel `schema_migrations` belum ada/masih versi 0 — biasanya terjadi kalau sebelumnya sempat pakai cara lain (CLI terpisah, psql manual, dsb) sebelum beralih ke `cmd/migrate`. | Paling cepat: ikuti reset total di Langkah 0 di atas. Kalau datanya mau dipertahankan (jarang terjadi di tahap latihan ini): tandai migration 1 sebagai "sudah diterapkan" tanpa dijalankan ulang dengan `go run ./cmd/migrate force 1`. |
| Koneksi ke Neon gagal / `x509` / `SSL is not enabled` | `sslmode` di `DATABASE_URL` tidak sesuai — Neon mewajibkan `sslmode=require`, tidak bisa `disable` seperti pada Postgres lokal. | Cek ulang query string di akhir `DATABASE_URL` — harus diakhiri `?sslmode=require` kalau memakai Neon. |
| `open migrations: no such file or directory` | Perintah `go run ./cmd/migrate` dijalankan dari direktori yang salah — tool ini mencari folder `migrations/` relatif terhadap direktori tempat perintah dijalankan, bukan relatif terhadap lokasi `main.go`. | Pastikan kamu berada di root proyek `umkm-api` (folder yang berisi `go.mod` dan folder `migrations/`) saat menjalankan `go run ./cmd/migrate ...`. |

Masih gagal setelah dicoba semua di atas?

Siapkan tiga info ini sebelum bertanya ke dosen/asisten supaya cepat dibantu: (1) **pesan error lengkap** dari terminal (jangan diringkas), (2) output `go run ./cmd/migrate version`, dan (3) `DATABASE_URL` milikmu dengan **password disensor** (ganti jadi `***`) supaya strukturnya tetap kelihatan tanpa membocorkan kredensial.

### 10.3 Konfigurasi dan Koneksi Database

internal/config/config.go

    package config

    import (
        "os"

        "github.com/joho/godotenv"
    )

    type Config struct {
        DatabaseURL string
        JWTSecret   string
        Port        string
        UploadDir   string
    }

    func Load() Config {
        _ = godotenv.Load() // abaikan error, misal saat deploy tanpa berkas .env

        return Config{
            DatabaseURL: os.Getenv("DATABASE_URL"),
            JWTSecret:   os.Getenv("JWT_SECRET"),
            Port:        getOrDefault("PORT", "8080"),
            UploadDir:   getOrDefault("UPLOAD_DIR", "./uploads"),
        }
    }

    func getOrDefault(key, def string) string {
        if v := os.Getenv(key); v != "" {
            return v
        }
        return def
    }

### 10.4 Domain — Struktur Data

Berkas pertama yang ditulis di `errors.go` (di sini digabung dalam `user.go`) adalah empat ***sentinel error*** — nilai error bersama yang dipakai di seluruh aplikasi. Kenapa bukan langsung menulis pesan error di `repository` atau `service`? Karena `handler` perlu **membedakan jenis error** secara terprogram (lewat `errors.Is`) untuk memilih kode status HTTP yang tepat — "data tidak ditemukan" harus jadi 404, "data sudah ada" harus jadi 409, dan seterusnya. Sentinel error ini yang jadi "jembatan" penerjemah tersebut, dipakai konsisten oleh `repository` (Bagian 10.5), `service` (Bagian 10.6), dan dibaca kembali oleh `handler` (Bagian 10.9).

internal/domain/user.go

    package domain

    import "errors"

    var (
        ErrNotFound     = errors.New("data tidak ditemukan")
        ErrConflict     = errors.New("data sudah ada")
        ErrForbidden    = errors.New("tidak memiliki akses")
        ErrInvalidInput = errors.New("input tidak valid")
    )

    type User struct {
        ID       int64  `json:"id"`
        Nama     string `json:"nama"`
        Email    string `json:"email"`
        Password string `json:"-"`
    }

internal/domain/umkm.go

    package domain

    type Umkm struct {
        ID        int64  `json:"id"`
        UserID    int64  `json:"user_id"`
        Nama      string `json:"nama"`
        Deskripsi string `json:"deskripsi"`
        Alamat    string `json:"alamat"`
        Foto      string `json:"foto"`
    }

internal/domain/produk.go

    package domain

    type Produk struct {
        ID        int64   `json:"id"`
        UmkmID    int64   `json:"umkm_id"`
        Nama      string  `json:"nama"`
        Harga     float64 `json:"harga"`
        Deskripsi string  `json:"deskripsi"`
        Foto      string  `json:"foto"`
    }

Dua hal yang perlu diperhatikan pada setiap struct domain

Pertama, tag `json:"..."` menentukan nama field pada response API — tulis dalam `snake_case` (misalnya `user_id`) karena itu konvensi JSON yang dipakai konsisten di seluruh kontrak endpoint (Bagian 9.1), supaya nanti aplikasi Flutter tidak bingung mencocokkan nama field. Kedua, tag `json:"-"` pada `Password` berarti field itu **tidak pernah ikut ter-serialize** ke JSON — aturan ini yang mencegah hash password bocor ke response meski struct `User` yang sama dipakai di banyak tempat. **Pola untuk entitas baru:** kalau membuat entitas lain, misal `Kategori`, cukup buat struct serupa dengan field dan tag JSON yang sesuai kontrak endpointnya — tidak perlu import apa pun dari `repository` atau `service`.

### 10.5 Repository — Akses Database

Interface repository didefinisikan sesempit mungkin, hanya berisi method yang benar-benar dipakai oleh service — bukan method generik seperti `Save`/`Delete` gaya ORM. Ini supaya saat membaca `UserRepository`, langsung jelas apa saja yang benar-benar dilakukan sistem terhadap tabel `users`, dan supaya versi palsunya (*fake*, dipakai saat unit test service) mudah dibuat karena cuma perlu mengimplementasikan sedikit method.

internal/repository/user_repository.go

    package repository

    import (
        "context"
        "errors"

        "github.com/jackc/pgx/v5"
        "github.com/jackc/pgx/v5/pgxpool"
        "umkm-api/internal/domain"
    )

    type UserRepository interface {
        Create(ctx context.Context, u *domain.User) error
        FindByEmail(ctx context.Context, email string) (*domain.User, error)
        FindByID(ctx context.Context, id int64) (*domain.User, error)
        UpdateProfile(ctx context.Context, id int64, nama, email string) error
        UpdatePassword(ctx context.Context, id int64, hashed string) error
    }

    type userRepository struct {
        db *pgxpool.Pool
    }

    func NewUserRepository(db *pgxpool.Pool) UserRepository {
        return &userRepository{db: db}
    }

    func (r *userRepository) Create(ctx context.Context, u *domain.User) error {
        query := `INSERT INTO users (nama, email, password) VALUES ($1, $2, $3) RETURNING id`
        return r.db.QueryRow(ctx, query, u.Nama, u.Email, u.Password).Scan(&u.ID)
    }

    func (r *userRepository) FindByEmail(ctx context.Context, email string) (*domain.User, error) {
        var u domain.User
        query := `SELECT id, nama, email, password FROM users WHERE email = $1`
        err := r.db.QueryRow(ctx, query, email).Scan(&u.ID, &u.Nama, &u.Email, &u.Password)
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, domain.ErrNotFound
        }
        if err != nil {
            return nil, err
        }
        return &u, nil
    }

    func (r *userRepository) FindByID(ctx context.Context, id int64) (*domain.User, error) {
        var u domain.User
        query := `SELECT id, nama, email, password FROM users WHERE id = $1`
        err := r.db.QueryRow(ctx, query, id).Scan(&u.ID, &u.Nama, &u.Email, &u.Password)
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, domain.ErrNotFound
        }
        if err != nil {
            return nil, err
        }
        return &u, nil
    }

    func (r *userRepository) UpdateProfile(ctx context.Context, id int64, nama, email string) error {
        query := `UPDATE users SET nama = $1, email = $2 WHERE id = $3`
        _, err := r.db.Exec(ctx, query, nama, email, id)
        return err
    }

    func (r *userRepository) UpdatePassword(ctx context.Context, id int64, hashed string) error {
        query := `UPDATE users SET password = $1 WHERE id = $2`
        _, err := r.db.Exec(ctx, query, hashed, id)
        return err
    }

internal/repository/umkm_repository.go

    package repository

    import (
        "context"
        "errors"

        "github.com/jackc/pgx/v5"
        "github.com/jackc/pgx/v5/pgxpool"
        "umkm-api/internal/domain"
    )

    type UmkmRepository interface {
        Create(ctx context.Context, u *domain.Umkm) error
        FindAll(ctx context.Context, q string, limit, offset int) ([]domain.Umkm, error)
        Count(ctx context.Context, q string) (int, error)
        FindByID(ctx context.Context, id int64) (*domain.Umkm, error)
        FindByUserID(ctx context.Context, userID int64) (*domain.Umkm, error)
        Update(ctx context.Context, u *domain.Umkm) error
        Delete(ctx context.Context, id int64) error
    }

    type umkmRepository struct {
        db *pgxpool.Pool
    }

    func NewUmkmRepository(db *pgxpool.Pool) UmkmRepository {
        return &umkmRepository{db: db}
    }

    func (r *umkmRepository) Create(ctx context.Context, u *domain.Umkm) error {
        query := `INSERT INTO umkm (user_id, nama, deskripsi, alamat, foto)
                  VALUES ($1, $2, $3, $4, $5) RETURNING id`
        return r.db.QueryRow(ctx, query, u.UserID, u.Nama, u.Deskripsi, u.Alamat, u.Foto).Scan(&u.ID)
    }

    // FindAll mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
    // q kosong berarti tidak difilter sama sekali.
    func (r *umkmRepository) FindAll(ctx context.Context, q string, limit, offset int) ([]domain.Umkm, error) {
        query := `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm
                  WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')
                  ORDER BY id DESC LIMIT $2 OFFSET $3`
        rows, err := r.db.Query(ctx, query, q, limit, offset)
        if err != nil {
            return nil, err
        }
        defer rows.Close()

        list := []domain.Umkm{} // inisialisasi slice kosong, bukan nil, agar JSON-nya "[]" bukan "null"
        for rows.Next() {
            var u domain.Umkm
            if err := rows.Scan(&u.ID, &u.UserID, &u.Nama, &u.Deskripsi, &u.Alamat, &u.Foto); err != nil {
                return nil, err
            }
            list = append(list, u)
        }
        return list, rows.Err()
    }

    func (r *umkmRepository) Count(ctx context.Context, q string) (int, error) {
        var total int
        query := `SELECT COUNT(*) FROM umkm WHERE ($1 = '' OR nama ILIKE '%' || $1 || '%')`
        err := r.db.QueryRow(ctx, query, q).Scan(&total)
        return total, err
    }

    func (r *umkmRepository) FindByID(ctx context.Context, id int64) (*domain.Umkm, error) {
        var u domain.Umkm
        query := `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE id = $1`
        err := r.db.QueryRow(ctx, query, id).Scan(&u.ID, &u.UserID, &u.Nama, &u.Deskripsi, &u.Alamat, &u.Foto)
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, domain.ErrNotFound
        }
        if err != nil {
            return nil, err
        }
        return &u, nil
    }

    func (r *umkmRepository) FindByUserID(ctx context.Context, userID int64) (*domain.Umkm, error) {
        var u domain.Umkm
        query := `SELECT id, user_id, nama, deskripsi, alamat, foto FROM umkm WHERE user_id = $1`
        err := r.db.QueryRow(ctx, query, userID).Scan(&u.ID, &u.UserID, &u.Nama, &u.Deskripsi, &u.Alamat, &u.Foto)
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, domain.ErrNotFound
        }
        if err != nil {
            return nil, err
        }
        return &u, nil
    }

    func (r *umkmRepository) Update(ctx context.Context, u *domain.Umkm) error {
        query := `UPDATE umkm SET nama = $1, deskripsi = $2, alamat = $3, foto = $4 WHERE id = $5`
        _, err := r.db.Exec(ctx, query, u.Nama, u.Deskripsi, u.Alamat, u.Foto, u.ID)
        return err
    }

    func (r *umkmRepository) Delete(ctx context.Context, id int64) error {
        _, err := r.db.Exec(ctx, `DELETE FROM umkm WHERE id = $1`, id)
        return err
    }

internal/repository/produk_repository.go

    package repository

    import (
        "context"
        "errors"

        "github.com/jackc/pgx/v5"
        "github.com/jackc/pgx/v5/pgxpool"
        "umkm-api/internal/domain"
    )

    type ProdukRepository interface {
        Create(ctx context.Context, p *domain.Produk) error
        FindByID(ctx context.Context, id int64) (*domain.Produk, error)
        FindByUmkmID(ctx context.Context, umkmID int64, limit, offset int) ([]domain.Produk, error)
        CountByUmkmID(ctx context.Context, umkmID int64) (int, error)
        Update(ctx context.Context, p *domain.Produk) error
        Delete(ctx context.Context, id int64) error
    }

    type produkRepository struct {
        db *pgxpool.Pool
    }

    func NewProdukRepository(db *pgxpool.Pool) ProdukRepository {
        return &produkRepository{db: db}
    }

    func (r *produkRepository) Create(ctx context.Context, p *domain.Produk) error {
        query := `INSERT INTO produk (umkm_id, nama, harga, deskripsi, foto)
                  VALUES ($1, $2, $3, $4, $5) RETURNING id`
        return r.db.QueryRow(ctx, query, p.UmkmID, p.Nama, p.Harga, p.Deskripsi, p.Foto).Scan(&p.ID)
    }

    func (r *produkRepository) FindByID(ctx context.Context, id int64) (*domain.Produk, error) {
        var p domain.Produk
        query := `SELECT id, umkm_id, nama, harga, deskripsi, foto FROM produk WHERE id = $1`
        err := r.db.QueryRow(ctx, query, id).Scan(&p.ID, &p.UmkmID, &p.Nama, &p.Harga, &p.Deskripsi, &p.Foto)
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, domain.ErrNotFound
        }
        if err != nil {
            return nil, err
        }
        return &p, nil
    }

    func (r *produkRepository) FindByUmkmID(ctx context.Context, umkmID int64, limit, offset int) ([]domain.Produk, error) {
        rows, err := r.db.Query(ctx,
            `SELECT id, umkm_id, nama, harga, deskripsi, foto FROM produk
             WHERE umkm_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3`,
            umkmID, limit, offset)
        if err != nil {
            return nil, err
        }
        defer rows.Close()

        list := []domain.Produk{}
        for rows.Next() {
            var p domain.Produk
            if err := rows.Scan(&p.ID, &p.UmkmID, &p.Nama, &p.Harga, &p.Deskripsi, &p.Foto); err != nil {
                return nil, err
            }
            list = append(list, p)
        }
        return list, rows.Err()
    }

    func (r *produkRepository) CountByUmkmID(ctx context.Context, umkmID int64) (int, error) {
        var total int
        err := r.db.QueryRow(ctx, `SELECT COUNT(*) FROM produk WHERE umkm_id = $1`, umkmID).Scan(&total)
        return total, err
    }

    func (r *produkRepository) Update(ctx context.Context, p *domain.Produk) error {
        query := `UPDATE produk SET nama = $1, harga = $2, deskripsi = $3, foto = $4 WHERE id = $5`
        _, err := r.db.Exec(ctx, query, p.Nama, p.Harga, p.Deskripsi, p.Foto, p.ID)
        return err
    }

    func (r *produkRepository) Delete(ctx context.Context, id int64) error {
        _, err := r.db.Exec(ctx, `DELETE FROM produk WHERE id = $1`, id)
        return err
    }

Pola yang berulang di ketiga repository — hafalkan, bukan dihafal per baris kode

1\. **Parameter selalu `$1, $2, ...`, tidak pernah digabung string manual (`+` atau `fmt.Sprintf`)** pada nilai dari pengguna. `pgx` mengirim nilai itu terpisah dari teks query ke database, sehingga nilai seperti `"'; DROP TABLE users;--"` yang diketik di form tetap diperlakukan sebagai teks biasa, bukan perintah SQL — inilah yang mencegah *SQL injection*.

2\. **Setiap `Find...` yang mengembalikan satu baris menerjemahkan `pgx.ErrNoRows` menjadi `domain.ErrNotFound`** (lihat `FindByEmail`, `FindByID`, dst). Tanpa penerjemahan ini, `service` dan `handler` di lapisan atas harus tahu detail library `pgx` — padahal mereka seharusnya cukup kenal error domain yang sudah didefinisikan di Bagian 10.4.

3\. **Query yang mengembalikan daftar (`FindAll`, `FindByUmkmID`) selalu diinisialisasi `list := []domain.X{}`, bukan `var list []domain.X`**. Slice nil di Go di-encode jadi `null` pada JSON, sedangkan slice kosong di-encode jadi `[]` — klien Flutter mengharapkan `[]` saat datanya kosong, bukan `null`.

4\. **Constructor (`NewUserRepository`, dst.) mengembalikan tipe *interface*, bukan tipe struct `*userRepository`** — ini yang memungkinkan `service` (Bagian 10.6) bergantung ke interface tanpa pernah tahu implementasinya memakai `pgx`.

**Cara meniru untuk entitas baru:** salin pola `umkmRepository` (paling lengkap: create, list+count untuk pagination, find by id, update, delete), ganti nama tabel dan kolom sesuai struct domain yang baru dibuat.

### 10.6 Service — Aturan Bisnis

Lapisan ini menjawab pertanyaan "*boleh* atau tidak", bukan "*bagaimana caranya* menyimpan ke database" (itu sudah selesai di `repository`) dan bukan "*bagaimana caranya* membaca request HTTP" (itu tugas `handler` di Bagian 10.8–10.9). Tiga jenis aturan bisnis yang akan berulang di `service` manapun yang Anda buat sendiri nanti:

- **Validasi input** — contoh: `len(password) < 6` pada `Register`, `nama == ""` pada `CreateOwn`. Dilakukan di sini (bukan di `handler`) karena aturan ini murni soal bisnis, bukan soal format HTTP.
- **Otorisasi kepemilikan** — contoh: `if umkm.UserID != userID { return nil, domain.ErrForbidden }` pada `UpdateOwn`/`DeleteOwn`. Polanya selalu sama: ambil data dulu dari repository, bandingkan pemiliknya dengan `userID` yang login (didapat dari JWT lewat middleware di Bagian 10.7), baru lanjutkan atau tolak.
- **Aturan unik bisnis** — contoh: "1 user hanya boleh 1 UMKM" dicek di `CreateOwn` dengan memanggil `FindByUserID` terlebih dulu sebelum `Create`.

internal/service/auth_service.go

    package service

    import (
        "context"
        "errors"
        "time"

        "github.com/golang-jwt/jwt/v5"
        "golang.org/x/crypto/bcrypt"
        "umkm-api/internal/domain"
        "umkm-api/internal/repository"
    )

    type AuthService struct {
        userRepo  repository.UserRepository
        jwtSecret string
    }

    func NewAuthService(userRepo repository.UserRepository, jwtSecret string) *AuthService {
        return &AuthService{userRepo: userRepo, jwtSecret: jwtSecret}
    }

    func (s *AuthService) Register(ctx context.Context, nama, email, password string) (*domain.User, error) {
        if nama == "" || email == "" || len(password) < 6 {
            return nil, domain.ErrInvalidInput
        }

        _, err := s.userRepo.FindByEmail(ctx, email)
        if err == nil {
            return nil, domain.ErrConflict // email sudah dipakai
        }
        if !errors.Is(err, domain.ErrNotFound) {
            return nil, err
        }

        hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
        if err != nil {
            return nil, err
        }

        user := &domain.User{Nama: nama, Email: email, Password: string(hashed)}
        if err := s.userRepo.Create(ctx, user); err != nil {
            return nil, err
        }
        return user, nil
    }

    func (s *AuthService) Login(ctx context.Context, email, password string) (string, *domain.User, error) {
        user, err := s.userRepo.FindByEmail(ctx, email)
        if err != nil {
            return "", nil, domain.ErrNotFound
        }

        if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(password)); err != nil {
            return "", nil, domain.ErrInvalidInput // password salah
        }

        token, err := s.generateToken(user.ID)
        if err != nil {
            return "", nil, err
        }
        return token, user, nil
    }

    func (s *AuthService) Profile(ctx context.Context, userID int64) (*domain.User, error) {
        return s.userRepo.FindByID(ctx, userID)
    }

    func (s *AuthService) UpdateProfile(ctx context.Context, userID int64, nama, email string) error {
        if nama == "" || email == "" {
            return domain.ErrInvalidInput
        }
        return s.userRepo.UpdateProfile(ctx, userID, nama, email)
    }

    func (s *AuthService) UpdatePassword(ctx context.Context, userID int64, lama, baru string) error {
        user, err := s.userRepo.FindByID(ctx, userID)
        if err != nil {
            return err
        }
        if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(lama)); err != nil {
            return domain.ErrInvalidInput // password lama tidak cocok
        }
        if len(baru) < 6 {
            return domain.ErrInvalidInput
        }
        hashed, err := bcrypt.GenerateFromPassword([]byte(baru), bcrypt.DefaultCost)
        if err != nil {
            return err
        }
        return s.userRepo.UpdatePassword(ctx, userID, string(hashed))
    }

    func (s *AuthService) generateToken(userID int64) (string, error) {
        claims := jwt.MapClaims{
            "sub": userID,
            "exp": time.Now().Add(24 * time.Hour).Unix(),
        }
        token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
        return token.SignedString([]byte(s.jwtSecret))
    }

Helper kecil berikut dipakai bersama oleh `UmkmService` dan `ProdukService` agar pengguna tidak bisa meminta `limit=0` (bikin loop tak berguna di sisi UI) atau `limit` yang sangat besar (membebani database).

internal/service/pagination.go

    package service

    const (
        defaultLimit = 10
        maxLimit     = 100
    )

    // normalizePagination memastikan page minimal 1 dan limit berada pada rentang wajar.
    func normalizePagination(page, limit int) (int, int) {
        if page < 1 {
            page = 1
        }
        if limit <= 0 {
            limit = defaultLimit
        }
        if limit > maxLimit {
            limit = maxLimit
        }
        return page, limit
    }

internal/service/umkm_service.go

    package service

    import (
        "context"
        "errors"

        "umkm-api/internal/domain"
        "umkm-api/internal/repository"
    )

    type UmkmService struct {
        umkmRepo repository.UmkmRepository
    }

    func NewUmkmService(umkmRepo repository.UmkmRepository) *UmkmService {
        return &UmkmService{umkmRepo: umkmRepo}
    }

    // List mengambil daftar UMKM dengan pagination, opsional difilter nama (q).
    // Mengembalikan list, total data, serta page/limit yang benar-benar dipakai
    // (setelah dinormalisasi) agar handler bisa menuliskan meta pagination yang akurat.
    func (s *UmkmService) List(ctx context.Context, q string, page, limit int) (list []domain.Umkm, total, usedPage, usedLimit int, err error) {
        usedPage, usedLimit = normalizePagination(page, limit)
        offset := (usedPage - 1) * usedLimit

        list, err = s.umkmRepo.FindAll(ctx, q, usedLimit, offset)
        if err != nil {
            return nil, 0, usedPage, usedLimit, err
        }
        total, err = s.umkmRepo.Count(ctx, q)
        if err != nil {
            return nil, 0, usedPage, usedLimit, err
        }
        return list, total, usedPage, usedLimit, nil
    }

    func (s *UmkmService) Detail(ctx context.Context, id int64) (*domain.Umkm, error) {
        return s.umkmRepo.FindByID(ctx, id)
    }

    func (s *UmkmService) MyUmkm(ctx context.Context, userID int64) (*domain.Umkm, error) {
        return s.umkmRepo.FindByUserID(ctx, userID)
    }

    func (s *UmkmService) CreateOwn(ctx context.Context, userID int64, nama, deskripsi, alamat, foto string) (*domain.Umkm, error) {
        if nama == "" {
            return nil, domain.ErrInvalidInput
        }

        _, err := s.umkmRepo.FindByUserID(ctx, userID)
        if err == nil {
            return nil, domain.ErrConflict // setiap user hanya boleh punya 1 UMKM
        }
        if !errors.Is(err, domain.ErrNotFound) {
            return nil, err
        }

        umkm := &domain.Umkm{UserID: userID, Nama: nama, Deskripsi: deskripsi, Alamat: alamat, Foto: foto}
        if err := s.umkmRepo.Create(ctx, umkm); err != nil {
            return nil, err
        }
        return umkm, nil
    }

    // UpdateOwn mengembalikan UMKM hasil update beserta path foto lama (bisa kosong).
    // Handler bertanggung jawab menghapus berkas foto lama dari disk setelah update berhasil.
    func (s *UmkmService) UpdateOwn(ctx context.Context, userID, umkmID int64, nama, deskripsi, alamat, fotoBaru string) (umkm *domain.Umkm, fotoLama string, err error) {
        if nama == "" {
            return nil, "", domain.ErrInvalidInput
        }

        umkm, err = s.umkmRepo.FindByID(ctx, umkmID)
        if err != nil {
            return nil, "", err
        }
        if umkm.UserID != userID {
            return nil, "", domain.ErrForbidden
        }

        fotoLama = umkm.Foto
        umkm.Nama = nama
        umkm.Deskripsi = deskripsi
        umkm.Alamat = alamat
        if fotoBaru != "" {
            umkm.Foto = fotoBaru
        } else {
            fotoLama = "" // foto tidak diganti, tidak ada yang perlu dihapus
        }

        if err := s.umkmRepo.Update(ctx, umkm); err != nil {
            return nil, "", err
        }
        return umkm, fotoLama, nil
    }

    func (s *UmkmService) DeleteOwn(ctx context.Context, userID, umkmID int64) (*domain.Umkm, error) {
        umkm, err := s.umkmRepo.FindByID(ctx, umkmID)
        if err != nil {
            return nil, err
        }
        if umkm.UserID != userID {
            return nil, domain.ErrForbidden
        }
        if err := s.umkmRepo.Delete(ctx, umkmID); err != nil {
            return nil, err
        }
        return umkm, nil
    }

internal/service/produk_service.go

    package service

    import (
        "context"

        "umkm-api/internal/domain"
        "umkm-api/internal/repository"
    )

    type ProdukService struct {
        produkRepo repository.ProdukRepository
        umkmRepo   repository.UmkmRepository
    }

    func NewProdukService(produkRepo repository.ProdukRepository, umkmRepo repository.UmkmRepository) *ProdukService {
        return &ProdukService{produkRepo: produkRepo, umkmRepo: umkmRepo}
    }

    // ListByUmkm mengambil daftar produk milik satu UMKM dengan pagination.
    // Mengembalikan list, total data, serta page/limit yang benar-benar dipakai.
    func (s *ProdukService) ListByUmkm(ctx context.Context, umkmID int64, page, limit int) (list []domain.Produk, total, usedPage, usedLimit int, err error) {
        usedPage, usedLimit = normalizePagination(page, limit)
        offset := (usedPage - 1) * usedLimit

        list, err = s.produkRepo.FindByUmkmID(ctx, umkmID, usedLimit, offset)
        if err != nil {
            return nil, 0, usedPage, usedLimit, err
        }
        total, err = s.produkRepo.CountByUmkmID(ctx, umkmID)
        if err != nil {
            return nil, 0, usedPage, usedLimit, err
        }
        return list, total, usedPage, usedLimit, nil
    }

    func (s *ProdukService) Detail(ctx context.Context, id int64) (*domain.Produk, error) {
        return s.produkRepo.FindByID(ctx, id)
    }

    func (s *ProdukService) CreateForOwnUmkm(ctx context.Context, userID, umkmID int64, nama string, harga float64, deskripsi, foto string) (*domain.Produk, error) {
        if nama == "" || harga < 0 {
            return nil, domain.ErrInvalidInput
        }

        umkm, err := s.umkmRepo.FindByID(ctx, umkmID)
        if err != nil {
            return nil, err
        }
        if umkm.UserID != userID {
            return nil, domain.ErrForbidden // hanya pemilik UMKM yang boleh menambah produk
        }

        produk := &domain.Produk{UmkmID: umkmID, Nama: nama, Harga: harga, Deskripsi: deskripsi, Foto: foto}
        if err := s.produkRepo.Create(ctx, produk); err != nil {
            return nil, err
        }
        return produk, nil
    }

    // authorizeOwner memastikan userID adalah pemilik UMKM tempat produk berada.
    func (s *ProdukService) authorizeOwner(ctx context.Context, userID, produkID int64) (*domain.Produk, error) {
        produk, err := s.produkRepo.FindByID(ctx, produkID)
        if err != nil {
            return nil, err
        }
        umkm, err := s.umkmRepo.FindByID(ctx, produk.UmkmID)
        if err != nil {
            return nil, err
        }
        if umkm.UserID != userID {
            return nil, domain.ErrForbidden
        }
        return produk, nil
    }

    func (s *ProdukService) UpdateOwn(ctx context.Context, userID, produkID int64, nama string, harga float64, deskripsi, fotoBaru string) (produk *domain.Produk, fotoLama string, err error) {
        if nama == "" || harga < 0 {
            return nil, "", domain.ErrInvalidInput
        }

        produk, err = s.authorizeOwner(ctx, userID, produkID)
        if err != nil {
            return nil, "", err
        }

        fotoLama = produk.Foto
        produk.Nama = nama
        produk.Harga = harga
        produk.Deskripsi = deskripsi
        if fotoBaru != "" {
            produk.Foto = fotoBaru
        } else {
            fotoLama = ""
        }

        if err := s.produkRepo.Update(ctx, produk); err != nil {
            return nil, "", err
        }
        return produk, fotoLama, nil
    }

    func (s *ProdukService) DeleteOwn(ctx context.Context, userID, produkID int64) (*domain.Produk, error) {
        produk, err := s.authorizeOwner(ctx, userID, produkID)
        if err != nil {
            return nil, err
        }
        if err := s.produkRepo.Delete(ctx, produkID); err != nil {
            return nil, err
        }
        return produk, nil
    }

Dua pola penting di lapisan service untuk ditiru

**Pagination mengembalikan 5 nilai sekaligus** — lihat tanda tangan `List(...) (list []domain.Umkm, total, usedPage, usedLimit int, err error)`. Kenapa `usedPage`/`usedLimit` ikut dikembalikan, padahal sudah dikirim sebagai parameter `page`/`limit`? Karena service menormalisasi nilainya lebih dulu lewat `normalizePagination` (misalnya `limit=0` diubah jadi `10`) — dan `handler` butuh tahu nilai *setelah* dinormalisasi itu, supaya `meta.page`/`meta.limit` pada response JSON mencerminkan apa yang benar-benar dipakai untuk query, bukan apa yang diketik pengguna di URL.

**Update yang mengganti foto mengembalikan path foto lama** — lihat tanda tangan `UpdateOwn(...) (umkm *domain.Umkm, fotoLama string, err error)`. Service sengaja tidak menghapus file lama sendiri (menghapus file adalah urusan I/O, bukan aturan bisnis) — ia hanya memutuskan foto mana yang sudah "usang" lalu melaporkannya ke `handler`, yang baru menghapus file fisiknya *setelah* database berhasil di-update (lihat Bagian 10.9). Urutan ini penting: kalau file dihapus duluan lalu update database gagal, foto hilang tanpa alasan.

**Cara meniru:** service baru untuk entitas lain cukup ikuti tiga daftar aturan di atas paragraf ini (validasi, otorisasi, aturan unik), dan pakai `normalizePagination` dari `pagination.go` kalau endpoint-nya berupa daftar.

### 10.7 Middleware — Autentikasi JWT

Middleware ini memeriksa header `Authorization: Bearer <token>`, lalu menyisipkan `userID` ke dalam `context` agar dapat dibaca oleh handler berikutnya. Secara tipe, middleware di Go cukup berupa fungsi dengan tanda tangan `func(http.Handler) http.Handler` — ia menerima handler "asli", lalu mengembalikan handler baru yang menjalankan kode tambahan (cek token) *sebelum* memanggil handler asli lewat `next.ServeHTTP(...)`. Pola "bungkus-memanggil" inilah yang disebut *middleware chaining*.

Kenapa prefix "Bearer " dibuat opsional, bukan wajib?

Swagger (OpenAPI 2.0, dipakai `swag`) hanya punya skema keamanan `apiKey` untuk kasus seperti ini — **tidak ada** skema `http bearer` yang membuat Swagger UI otomatis menambahkan kata "Bearer " di kotak Authorize seperti pada beberapa tools lain. Akibatnya mahasiswa yang hanya paste token mentah (tanpa mengetik "Bearer " sendiri) akan selalu dapat `401 "token tidak ditemukan"` walau tokennya valid — ini sumber kebingungan yang sangat umum. Middleware di atas sengaja dibuat menerima **kedua bentuk**: `Bearer <token>` (format standar, tetap dianjurkan dan dipakai semua contoh di tutorial ini) maupun token mentah tanpa prefix — tanpa mengurangi keamanan, karena yang diverifikasi tetap tanda tangan HS256 token itu sendiri, bukan format headernya.

Project kamu sudah lebih dulu dibuat (sebelum update ini)? Cukup ganti satu file ini

Kalau pas coba token di Swagger masih dapat `401 "token tidak ditemukan"` padahal tokennya valid, berarti `internal/middleware/auth.go` di project kamu masih versi lama. **Tidak perlu menulis ulang semua, cukup ganti isi satu file ini** — buka `internal/middleware/auth.go` di VS Code, hapus semua isinya, lalu salin-tempel (copy-paste) persis kode lengkap di bawah ini menggantikannya. Setelah disimpan, matikan server (Ctrl+C di terminal) dan jalankan ulang `go run ./cmd/api` — Go tidak hot-reload otomatis, jadi perubahan baru berlaku setelah server dinyalakan ulang.

internal/middleware/auth.go — ganti seluruh isi file ini

    package middleware

    import (
        "context"
        "net/http"
        "strings"

        "github.com/golang-jwt/jwt/v5"
    )

    type contextKey string

    const UserIDKey contextKey = "userID"

    func RequireAuth(jwtSecret string) func(http.Handler) http.Handler {
        return func(next http.Handler) http.Handler {
            return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
                header := r.Header.Get("Authorization")
                if header == "" {
                    http.Error(w, `{"error":{"message":"token tidak ditemukan","code":"UNAUTHORIZED"}}`, http.StatusUnauthorized)
                    return
                }

                // Terima baik "Bearer <token>" maupun token mentah tanpa prefix,
                // supaya kotak Authorize di Swagger (skema apikey, tidak auto-tambah "Bearer ")
                // tidak selalu gagal kalau mahasiswa lupa mengetik kata "Bearer".
                tokenStr := header
                if len(header) > 7 && strings.EqualFold(header[:7], "Bearer ") {
                    tokenStr = header[7:]
                }
                // jwt.WithValidMethods memaksa algoritma HS256 saja, agar token dengan
                // header "alg" lain (termasuk "none") selalu ditolak (algorithm confusion attack).
                token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (interface{}, error) {
                    return []byte(jwtSecret), nil
                }, jwt.WithValidMethods([]string{jwt.SigningMethodHS256.Alg()}))
                if err != nil || !token.Valid {
                    http.Error(w, `{"error":{"message":"token tidak valid","code":"UNAUTHORIZED"}}`, http.StatusUnauthorized)
                    return
                }

                claims, ok := token.Claims.(jwt.MapClaims)
                if !ok {
                    http.Error(w, `{"error":{"message":"token tidak valid","code":"UNAUTHORIZED"}}`, http.StatusUnauthorized)
                    return
                }
                sub, ok := claims["sub"].(float64)
                if !ok {
                    http.Error(w, `{"error":{"message":"token tidak valid","code":"UNAUTHORIZED"}}`, http.StatusUnauthorized)
                    return
                }
                userID := int64(sub)

                ctx := context.WithValue(r.Context(), UserIDKey, userID)
                next.ServeHTTP(w, r.WithContext(ctx))
            })
        }
    }

    func GetUserID(r *http.Request) int64 {
        id, _ := r.Context().Value(UserIDKey).(int64)
        return id
    }

Dua pengecekan tambahan `claims, ok := ...` dan `sub, ok := ...` di atas (dibanding sekadar `token.Claims.(jwt.MapClaims)` langsung) mencegah server *panic* kalau ada token yang lolos tanda tangan tapi strukturnya aneh — misalnya claims kosong atau `sub` bukan angka. Tanpa pengecekan ini, satu request dengan token "nyeleneh" bisa menjatuhkan seluruh server.

Middleware kedua membatasi laju request per alamat IP, dipasang khusus pada endpoint login agar percobaan brute-force password tidak bisa dilakukan tanpa batas.

internal/middleware/ratelimit.go

    package middleware

    import (
        "net"
        "net/http"
        "sync"

        "golang.org/x/time/rate"
    )

    // ipRateLimiter menyimpan satu rate.Limiter per alamat IP, supaya percobaan
    // login yang bertubi-tubi dari satu IP (brute-force) dibatasi tanpa mengganggu
    // pengguna lain yang mengakses endpoint yang sama secara wajar.
    type ipRateLimiter struct {
        mu       sync.Mutex
        limiters map[string]*rate.Limiter
        r        rate.Limit
        b        int
    }

    func newIPRateLimiter(r rate.Limit, b int) *ipRateLimiter {
        return &ipRateLimiter{
            limiters: make(map[string]*rate.Limiter),
            r:        r,
            b:        b,
        }
    }

    func (i *ipRateLimiter) getLimiter(ip string) *rate.Limiter {
        i.mu.Lock()
        defer i.mu.Unlock()

        limiter, exists := i.limiters[ip]
        if !exists {
            limiter = rate.NewLimiter(i.r, i.b)
            i.limiters[ip] = limiter
        }
        return limiter
    }

    func clientIP(r *http.Request) string {
        host, _, err := net.SplitHostPort(r.RemoteAddr)
        if err != nil {
            return r.RemoteAddr
        }
        return host
    }

    // RateLimit membatasi jumlah request per alamat IP. r adalah laju pengisian ulang
    // token (request/detik) dan b adalah ukuran burst (jumlah request beruntun yang
    // masih diizinkan sebelum limiter mulai menahan).
    func RateLimit(r rate.Limit, b int) func(http.Handler) http.Handler {
        limiter := newIPRateLimiter(r, b)
        return func(next http.Handler) http.Handler {
            return http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
                if !limiter.getLimiter(clientIP(req)).Allow() {
                    http.Error(w, `{"error":{"message":"terlalu banyak percobaan, coba lagi nanti","code":"TOO_MANY_REQUESTS"}}`, http.StatusTooManyRequests)
                    return
                }
                next.ServeHTTP(w, req)
            })
        }
    }

Kenapa per-IP, bukan global?

Limiter global akan membatasi *semua* pengguna sekaligus begitu satu orang menembak berkali-kali. Dengan satu `rate.Limiter` per alamat IP (disimpan dalam `map`), pengguna lain yang login secara wajar dari IP berbeda tidak ikut terkena batas.

### 10.8 Handler — Response Helper dan Upload File

`writePaginated` membungkus data list beserta info halaman (`page`, `limit`, `total`), dipakai oleh endpoint `GET /api/umkm` dan `GET /api/umkm/{id}/produk`. `parsePagination` membaca query param `page`/`limit` apa adanya — validasi/normalisasi rentangnya tetap tanggung jawab service (Bagian 10.6), bukan handler.

internal/handler/response.go

    package handler

    import (
        "encoding/json"
        "net/http"
        "strconv"
    )

    func writeJSON(w http.ResponseWriter, status int, data any) {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(status)
        json.NewEncoder(w).Encode(map[string]any{"data": data})
    }

    // paginationMeta adalah bentuk info halaman yang disisipkan pada respons list.
    type paginationMeta struct {
        Page  int `json:"page"`
        Limit int `json:"limit"`
        Total int `json:"total"`
    }

    func writePaginated(w http.ResponseWriter, status int, data any, page, limit, total int) {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(status)
        json.NewEncoder(w).Encode(map[string]any{
            "data": data,
            "meta": paginationMeta{Page: page, Limit: limit, Total: total},
        })
    }

    func writeError(w http.ResponseWriter, status int, message, code string) {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(status)
        json.NewEncoder(w).Encode(map[string]any{
            "error": map[string]string{"message": message, "code": code},
        })
    }

    // parsePagination membaca query param "page" dan "limit". Nilai yang tidak ada
    // atau tidak valid dibiarkan 0 agar dinormalisasi oleh lapisan service.
    func parsePagination(r *http.Request) (page, limit int) {
        page, _ = strconv.Atoi(r.URL.Query().Get("page"))
        limit, _ = strconv.Atoi(r.URL.Query().Get("limit"))
        return page, limit
    }

Tiga helper ini dipakai di hampir setiap handler — pahami sekali, pakai di mana-mana

`writeJSON` untuk response sukses satu objek, `writePaginated` khusus untuk daftar (menambahkan blok `meta`), dan `writeError` untuk semua jalur gagal. Karena ketiganya selalu men-set `Content-Type` dan `WriteHeader` dengan cara yang sama, handler manapun yang Anda tulis nanti — termasuk untuk entitas baru — tinggal memanggil salah satu dari ketiganya, tidak perlu menulis ulang `json.NewEncoder(w).Encode(...)` setiap kali. Inilah sebabnya format response di seluruh API konsisten walau ditulis oleh fungsi yang berbeda-beda (bandingkan dengan kontrak format response di Bagian 9.2).

Upload foto ditangani dengan `multipart/form-data`. Berkas disimpan ke folder lokal, dan yang disimpan ke database hanyalah **path relatif** (`umkm/xxx.jpg`) — bukan path disk absolut — agar bisa langsung digabung menjadi URL oleh klien maupun dipakai untuk menghapus berkas lama saat update/delete. Hanya berkas berekstensi `.jpg`/`.jpeg`/`.png` yang diterima.

internal/handler/upload.go

    package handler

    import (
        "errors"
        "fmt"
        "io"
        "net/http"
        "os"
        "path/filepath"
        "strings"
        "time"
    )

    // errInvalidFileType dikembalikan saat ekstensi berkas yang diunggah bukan
    // salah satu dari allowedImageExt.
    var errInvalidFileType = errors.New("tipe berkas tidak didukung, hanya jpg/jpeg/png")

    var allowedImageExt = map[string]bool{
        ".jpg":  true,
        ".jpeg": true,
        ".png":  true,
    }

    // saveUploadedFile menyimpan berkas dari form-field fieldName ke <uploadDir>/<subDir>/.
    // Mengembalikan path RELATIF (contoh: "umkm/169...jpg"), bukan path disk absolut,
    // agar nilai yang sama bisa langsung dipakai klien sebagai "<base_url>/uploads/<foto>".
    // Mengembalikan string kosong (bukan error) apabila pengguna tidak mengunggah foto,
    // karena foto bersifat opsional. Hanya menerima berkas berekstensi .jpg/.jpeg/.png.
    func saveUploadedFile(r *http.Request, fieldName, uploadDir, subDir string) (string, error) {
        file, header, err := r.FormFile(fieldName)
        if err == http.ErrMissingFile {
            return "", nil
        }
        if err != nil {
            return "", err
        }
        defer file.Close()

        ext := strings.ToLower(filepath.Ext(header.Filename))
        if !allowedImageExt[ext] {
            return "", errInvalidFileType
        }

        targetDir := filepath.Join(uploadDir, subDir)
        if err := os.MkdirAll(targetDir, 0755); err != nil {
            return "", err
        }

        filename := fmt.Sprintf("%d%s", time.Now().UnixNano(), ext)

        dst, err := os.Create(filepath.Join(targetDir, filename))
        if err != nil {
            return "", err
        }
        defer dst.Close()

        if _, err := io.Copy(dst, file); err != nil {
            return "", err
        }

        return subDir + "/" + filename, nil
    }

    // deleteFile menghapus berkas lama di <uploadDir>/<relPath>. Dipanggil setelah
    // update/delete berhasil di database, agar tidak ada berkas foto yang menumpuk.
    func deleteFile(uploadDir, relPath string) {
        if relPath == "" {
            return
        }
        _ = os.Remove(filepath.Join(uploadDir, relPath))
    }

Alur lengkap satu file upload, dari form sampai database

1\) Handler memanggil `saveUploadedFile(r, "foto", uploadDir, "umkm")` → file disimpan ke disk di `uploads/umkm/<timestamp>.jpg`, mengembalikan path relatif `"umkm/<timestamp>.jpg"`. 2) Path relatif itu (bukan file-nya) yang diteruskan ke `service` lalu disimpan sebagai kolom `foto` di database. 3) Saat ditampilkan kembali lewat API, path relatif ini yang dikirim ke klien (lihat catatan "Field foto" di Bagian 9.2) — klien yang menggabungkannya dengan `base_url`. **Kenapa nama file pakai `time.Now().UnixNano()`?** Supaya setiap upload punya nama unik walau dua pengguna mengunggah file dengan nama asli yang sama persis (misalnya sama-sama `foto.jpg`), tanpa perlu mengecek tabrakan nama ke database.

### 10.9 Handler — Auth, Profile, UMKM, Produk (dengan Anotasi Swagger)

Komentar berformat `@Summary`, `@Param`, `@Success`, dsb. di atas setiap fungsi bukan komentar biasa — ini adalah **anotasi Swagger** yang akan dibaca oleh tool `swag` pada Bagian 11 untuk menghasilkan dokumentasi otomatis. Untuk anotasi tersebut merujuk ke tipe respons, tambahkan dahulu berkas berikut:

internal/handler/swagger_types.go

    package handler

    import "umkm-api/internal/domain"

    type DataUserResponse struct {
        Data domain.User `json:"data"`
    }

    type DataLoginResponse struct {
        Data struct {
            Token string      `json:"token"`
            User  domain.User `json:"user"`
        } `json:"data"`
    }

    type DataUmkmResponse struct {
        Data domain.Umkm `json:"data"`
    }

    type DataUmkmListResponse struct {
        Data []domain.Umkm `json:"data"`
    }

    type DataProdukResponse struct {
        Data domain.Produk `json:"data"`
    }

    type DataProdukListResponse struct {
        Data []domain.Produk `json:"data"`
    }

    type MessageResponse struct {
        Data struct {
            Message string `json:"message"`
        } `json:"data"`
    }

    type ErrorResponse struct {
        Error struct {
            Message string `json:"message"`
            Code    string `json:"code"`
        } `json:"error"`
    }

Pola yang sama berulang di setiap fungsi handler di bawah ini

Perhatikan setiap fungsi seperti `Register`, `Login`, `Create`, dst. — semuanya mengikuti tiga langkah yang sama: **(1) baca input** dari `r.Body` (JSON) atau `r.FormValue`/`r.PathValue` (form/path), **(2) panggil satu fungsi service**, lalu **(3) terjemahkan hasilnya** lewat blok `switch { case errors.Is(err, domain.ErrXxx): ... }` menjadi kode status HTTP yang sesuai. Urutan `case` dalam `switch` ini tidak sembarangan — error domain paling spesifik dicek lebih dulu (`ErrInvalidInput`, `ErrConflict`, `ErrForbidden`, `ErrNotFound`), baru `case err != nil` sebagai jaring pengaman terakhir untuk error tak terduga (dipetakan ke `500 Internal Server Error` — pesannya sengaja digeneralisasi "kesalahan server" agar detail internal, misalnya pesan error asli dari database, tidak bocor ke klien). **Kalau membuat handler untuk entitas baru, tiru persis struktur tiga langkah ini.**

internal/handler/auth_handler.go

    package handler

    import (
        "encoding/json"
        "errors"
        "net/http"

        "umkm-api/internal/domain"
        "umkm-api/internal/middleware"
        "umkm-api/internal/service"
    )

    type AuthHandler struct {
        svc *service.AuthService
    }

    func NewAuthHandler(svc *service.AuthService) *AuthHandler {
        return &AuthHandler{svc: svc}
    }

    type registerRequest struct {
        Nama     string `json:"nama"`
        Email    string `json:"email"`
        Password string `json:"password"`
    }

    // Register godoc
    // @Summary      Register akun baru
    // @Description  Mendaftarkan pengguna baru dengan nama, email, dan password
    // @Tags         auth
    // @Accept       json
    // @Produce      json
    // @Param        body body registerRequest true "Data registrasi"
    // @Success      201 {object} handler.DataUserResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Failure      409 {object} handler.ErrorResponse
    // @Router       /auth/register [post]
    func (h *AuthHandler) Register(w http.ResponseWriter, r *http.Request) {
        var req registerRequest
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            writeError(w, http.StatusBadRequest, "body tidak valid", "BAD_REQUEST")
            return
        }

        user, err := h.svc.Register(r.Context(), req.Nama, req.Email, req.Password)
        switch {
        case errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusBadRequest, "nama, email, dan password (min 6 karakter) wajib diisi", "BAD_REQUEST")
        case errors.Is(err, domain.ErrConflict):
            writeError(w, http.StatusConflict, "email sudah terdaftar", "CONFLICT")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusCreated, user)
        }
    }

    type loginRequest struct {
        Email    string `json:"email"`
        Password string `json:"password"`
    }

    // Login godoc
    // @Summary      Login
    // @Description  Login dengan email dan password, mengembalikan JWT token
    // @Tags         auth
    // @Accept       json
    // @Produce      json
    // @Param        body body loginRequest true "Kredensial login"
    // @Success      200 {object} handler.DataLoginResponse
    // @Failure      401 {object} handler.ErrorResponse
    // @Router       /auth/login [post]
    func (h *AuthHandler) Login(w http.ResponseWriter, r *http.Request) {
        var req loginRequest
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            writeError(w, http.StatusBadRequest, "body tidak valid", "BAD_REQUEST")
            return
        }

        token, user, err := h.svc.Login(r.Context(), req.Email, req.Password)
        switch {
        case errors.Is(err, domain.ErrNotFound), errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusUnauthorized, "email atau password salah", "UNAUTHORIZED")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusOK, map[string]any{"token": token, "user": user})
        }
    }

    // Profile godoc
    // @Summary      Lihat profil sendiri
    // @Description  Mengambil data profil pengguna yang sedang login
    // @Tags         profile
    // @Produce      json
    // @Security     BearerAuth
    // @Success      200 {object} handler.DataUserResponse
    // @Failure      401 {object} handler.ErrorResponse
    // @Router       /profile [get]
    func (h *AuthHandler) Profile(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        user, err := h.svc.Profile(r.Context(), userID)
        if err != nil {
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
            return
        }
        writeJSON(w, http.StatusOK, user)
    }

    type updateProfileRequest struct {
        Nama  string `json:"nama"`
        Email string `json:"email"`
    }

    // UpdateProfile godoc
    // @Summary      Update profil
    // @Description  Mengubah nama dan email akun yang sedang login
    // @Tags         profile
    // @Accept       json
    // @Produce      json
    // @Security     BearerAuth
    // @Param        body body updateProfileRequest true "Data profil baru"
    // @Success      200 {object} handler.MessageResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Router       /profile [put]
    func (h *AuthHandler) UpdateProfile(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        var req updateProfileRequest
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            writeError(w, http.StatusBadRequest, "body tidak valid", "BAD_REQUEST")
            return
        }

        if err := h.svc.UpdateProfile(r.Context(), userID, req.Nama, req.Email); err != nil {
            writeError(w, http.StatusBadRequest, "gagal memperbarui profil", "BAD_REQUEST")
            return
        }
        writeJSON(w, http.StatusOK, map[string]string{"message": "profil berhasil diperbarui"})
    }

    type updatePasswordRequest struct {
        PasswordLama string `json:"password_lama"`
        PasswordBaru string `json:"password_baru"`
    }

    // UpdatePassword godoc
    // @Summary      Update password
    // @Description  Mengubah password akun yang sedang login, wajib menyertakan password lama
    // @Tags         profile
    // @Accept       json
    // @Produce      json
    // @Security     BearerAuth
    // @Param        body body updatePasswordRequest true "Password lama dan baru"
    // @Success      200 {object} handler.MessageResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Router       /profile/password [put]
    func (h *AuthHandler) UpdatePassword(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        var req updatePasswordRequest
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            writeError(w, http.StatusBadRequest, "body tidak valid", "BAD_REQUEST")
            return
        }

        err := h.svc.UpdatePassword(r.Context(), userID, req.PasswordLama, req.PasswordBaru)
        switch {
        case errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusBadRequest, "password lama salah atau password baru terlalu pendek", "BAD_REQUEST")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusOK, map[string]string{"message": "password berhasil diperbarui"})
        }
    }

internal/handler/umkm_handler.go

    package handler

    import (
        "errors"
        "net/http"
        "strconv"

        "umkm-api/internal/domain"
        "umkm-api/internal/middleware"
        "umkm-api/internal/service"
    )

    type UmkmHandler struct {
        svc       *service.UmkmService
        uploadDir string
    }

    func NewUmkmHandler(svc *service.UmkmService, uploadDir string) *UmkmHandler {
        return &UmkmHandler{svc: svc, uploadDir: uploadDir}
    }

    // List godoc
    // @Summary      Lihat semua UMKM
    // @Description  Mendukung pagination dan pencarian nama
    // @Tags         umkm
    // @Produce      json
    // @Param        q query string false "Kata kunci pencarian nama UMKM"
    // @Param        page query int false "Halaman (default 1)"
    // @Param        limit query int false "Jumlah data per halaman (default 10, maksimal 100)"
    // @Success      200 {object} handler.DataUmkmListResponse
    // @Router       /umkm [get]
    func (h *UmkmHandler) List(w http.ResponseWriter, r *http.Request) {
        q := r.URL.Query().Get("q")
        page, limit := parsePagination(r)

        list, total, usedPage, usedLimit, err := h.svc.List(r.Context(), q, page, limit)
        if err != nil {
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
            return
        }
        writePaginated(w, http.StatusOK, list, usedPage, usedLimit, total)
    }

    // Detail godoc
    // @Summary      Detail UMKM
    // @Tags         umkm
    // @Produce      json
    // @Param        id path int true "ID UMKM"
    // @Success      200 {object} handler.DataUmkmResponse
    // @Failure      404 {object} handler.ErrorResponse
    // @Router       /umkm/{id} [get]
    func (h *UmkmHandler) Detail(w http.ResponseWriter, r *http.Request) {
        id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        umkm, err := h.svc.Detail(r.Context(), id)
        switch {
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "UMKM tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusOK, umkm)
        }
    }

    // MyUmkm godoc
    // @Summary      Lihat UMKM saya
    // @Tags         umkm
    // @Produce      json
    // @Security     BearerAuth
    // @Success      200 {object} handler.DataUmkmResponse
    // @Failure      404 {object} handler.ErrorResponse
    // @Router       /umkm/saya [get]
    func (h *UmkmHandler) MyUmkm(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        umkm, err := h.svc.MyUmkm(r.Context(), userID)
        switch {
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "Anda belum memiliki UMKM", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusOK, umkm)
        }
    }

    // Create godoc
    // @Summary      Buat UMKM sendiri
    // @Description  1 user hanya boleh punya 1 UMKM. Foto opsional.
    // @Tags         umkm
    // @Accept       multipart/form-data
    // @Produce      json
    // @Security     BearerAuth
    // @Param        nama formData string true "Nama UMKM"
    // @Param        deskripsi formData string false "Deskripsi UMKM"
    // @Param        alamat formData string false "Alamat UMKM"
    // @Param        foto formData file false "Foto UMKM"
    // @Success      201 {object} handler.DataUmkmResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Failure      409 {object} handler.ErrorResponse
    // @Router       /umkm [post]
    func (h *UmkmHandler) Create(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)

        r.Body = http.MaxBytesReader(w, r.Body, 5<<20)
        if err := r.ParseMultipartForm(5 << 20); err != nil {
            writeError(w, http.StatusBadRequest, "form tidak valid atau file terlalu besar", "BAD_REQUEST")
            return
        }

        nama := r.FormValue("nama")
        deskripsi := r.FormValue("deskripsi")
        alamat := r.FormValue("alamat")

        fotoPath, err := saveUploadedFile(r, "foto", h.uploadDir, "umkm")
        if errors.Is(err, errInvalidFileType) {
            writeError(w, http.StatusBadRequest, "foto harus berformat jpg/jpeg/png", "BAD_REQUEST")
            return
        }
        if err != nil {
            writeError(w, http.StatusBadRequest, "gagal menyimpan foto", "BAD_REQUEST")
            return
        }

        umkm, err := h.svc.CreateOwn(r.Context(), userID, nama, deskripsi, alamat, fotoPath)
        switch {
        case errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusBadRequest, "nama UMKM wajib diisi", "BAD_REQUEST")
        case errors.Is(err, domain.ErrConflict):
            writeError(w, http.StatusConflict, "Anda sudah memiliki UMKM", "CONFLICT")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusCreated, umkm)
        }
    }

    // Update godoc
    // @Summary      Update UMKM sendiri
    // @Tags         umkm
    // @Accept       multipart/form-data
    // @Produce      json
    // @Security     BearerAuth
    // @Param        id path int true "ID UMKM"
    // @Param        nama formData string true "Nama UMKM"
    // @Param        deskripsi formData string false "Deskripsi UMKM"
    // @Param        alamat formData string false "Alamat UMKM"
    // @Param        foto formData file false "Foto UMKM baru"
    // @Success      200 {object} handler.DataUmkmResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Failure      403 {object} handler.ErrorResponse
    // @Router       /umkm/{id} [put]
    func (h *UmkmHandler) Update(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        r.Body = http.MaxBytesReader(w, r.Body, 5<<20)
        if err := r.ParseMultipartForm(5 << 20); err != nil {
            writeError(w, http.StatusBadRequest, "form tidak valid atau file terlalu besar", "BAD_REQUEST")
            return
        }

        nama := r.FormValue("nama")
        deskripsi := r.FormValue("deskripsi")
        alamat := r.FormValue("alamat")

        fotoBaru, err := saveUploadedFile(r, "foto", h.uploadDir, "umkm")
        if errors.Is(err, errInvalidFileType) {
            writeError(w, http.StatusBadRequest, "foto harus berformat jpg/jpeg/png", "BAD_REQUEST")
            return
        }
        if err != nil {
            writeError(w, http.StatusBadRequest, "gagal menyimpan foto", "BAD_REQUEST")
            return
        }

        umkm, fotoLama, err := h.svc.UpdateOwn(r.Context(), userID, id, nama, deskripsi, alamat, fotoBaru)
        switch {
        case errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusBadRequest, "nama UMKM wajib diisi", "BAD_REQUEST")
        case errors.Is(err, domain.ErrForbidden):
            writeError(w, http.StatusForbidden, "Anda bukan pemilik UMKM ini", "FORBIDDEN")
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "UMKM tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            deleteFile(h.uploadDir, fotoLama)
            writeJSON(w, http.StatusOK, umkm)
        }
    }

    // Delete godoc
    // @Summary      Hapus UMKM sendiri
    // @Description  Produk pada UMKM ini ikut terhapus otomatis (ON DELETE CASCADE)
    // @Tags         umkm
    // @Produce      json
    // @Security     BearerAuth
    // @Param        id path int true "ID UMKM"
    // @Success      200 {object} handler.MessageResponse
    // @Failure      403 {object} handler.ErrorResponse
    // @Failure      404 {object} handler.ErrorResponse
    // @Router       /umkm/{id} [delete]
    func (h *UmkmHandler) Delete(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        umkm, err := h.svc.DeleteOwn(r.Context(), userID, id)
        switch {
        case errors.Is(err, domain.ErrForbidden):
            writeError(w, http.StatusForbidden, "Anda bukan pemilik UMKM ini", "FORBIDDEN")
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "UMKM tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            deleteFile(h.uploadDir, umkm.Foto)
            writeJSON(w, http.StatusOK, map[string]string{"message": "UMKM berhasil dihapus"})
        }
    }

internal/handler/produk_handler.go

    package handler

    import (
        "errors"
        "net/http"
        "strconv"

        "umkm-api/internal/domain"
        "umkm-api/internal/middleware"
        "umkm-api/internal/service"
    )

    type ProdukHandler struct {
        svc       *service.ProdukService
        uploadDir string
    }

    func NewProdukHandler(svc *service.ProdukService, uploadDir string) *ProdukHandler {
        return &ProdukHandler{svc: svc, uploadDir: uploadDir}
    }

    // Detail godoc
    // @Summary      Detail produk
    // @Tags         produk
    // @Produce      json
    // @Param        id path int true "ID Produk"
    // @Success      200 {object} handler.DataProdukResponse
    // @Failure      404 {object} handler.ErrorResponse
    // @Router       /produk/{id} [get]
    func (h *ProdukHandler) Detail(w http.ResponseWriter, r *http.Request) {
        id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        produk, err := h.svc.Detail(r.Context(), id)
        switch {
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "produk tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusOK, produk)
        }
    }

    // ListByUmkm godoc
    // @Summary      Lihat produk pada satu UMKM
    // @Description  Mendukung pagination
    // @Tags         produk
    // @Produce      json
    // @Param        id path int true "ID UMKM"
    // @Param        page query int false "Halaman (default 1)"
    // @Param        limit query int false "Jumlah data per halaman (default 10, maksimal 100)"
    // @Success      200 {object} handler.DataProdukListResponse
    // @Router       /umkm/{id}/produk [get]
    func (h *ProdukHandler) ListByUmkm(w http.ResponseWriter, r *http.Request) {
        umkmID, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }
        page, limit := parsePagination(r)

        list, total, usedPage, usedLimit, err := h.svc.ListByUmkm(r.Context(), umkmID, page, limit)
        if err != nil {
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
            return
        }
        writePaginated(w, http.StatusOK, list, usedPage, usedLimit, total)
    }

    // Create godoc
    // @Summary      Tambah produk pada UMKM sendiri
    // @Tags         produk
    // @Accept       multipart/form-data
    // @Produce      json
    // @Security     BearerAuth
    // @Param        id path int true "ID UMKM"
    // @Param        nama formData string true "Nama produk"
    // @Param        harga formData number true "Harga produk"
    // @Param        deskripsi formData string false "Deskripsi produk"
    // @Param        foto formData file false "Foto produk"
    // @Success      201 {object} handler.DataProdukResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Failure      403 {object} handler.ErrorResponse
    // @Router       /umkm/{id}/produk [post]
    func (h *ProdukHandler) Create(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        umkmID, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        r.Body = http.MaxBytesReader(w, r.Body, 5<<20)
        if err := r.ParseMultipartForm(5 << 20); err != nil {
            writeError(w, http.StatusBadRequest, "form tidak valid atau file terlalu besar", "BAD_REQUEST")
            return
        }

        nama := r.FormValue("nama")
        deskripsi := r.FormValue("deskripsi")
        harga, _ := strconv.ParseFloat(r.FormValue("harga"), 64)

        fotoPath, err := saveUploadedFile(r, "foto", h.uploadDir, "produk")
        if errors.Is(err, errInvalidFileType) {
            writeError(w, http.StatusBadRequest, "foto harus berformat jpg/jpeg/png", "BAD_REQUEST")
            return
        }
        if err != nil {
            writeError(w, http.StatusBadRequest, "gagal menyimpan foto", "BAD_REQUEST")
            return
        }

        produk, err := h.svc.CreateForOwnUmkm(r.Context(), userID, umkmID, nama, harga, deskripsi, fotoPath)
        switch {
        case errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusBadRequest, "nama dan harga produk wajib valid", "BAD_REQUEST")
        case errors.Is(err, domain.ErrForbidden):
            writeError(w, http.StatusForbidden, "Anda bukan pemilik UMKM ini", "FORBIDDEN")
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "UMKM tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            writeJSON(w, http.StatusCreated, produk)
        }
    }

    // Update godoc
    // @Summary      Update produk sendiri
    // @Tags         produk
    // @Accept       multipart/form-data
    // @Produce      json
    // @Security     BearerAuth
    // @Param        id path int true "ID Produk"
    // @Param        nama formData string true "Nama produk"
    // @Param        harga formData number true "Harga produk"
    // @Param        deskripsi formData string false "Deskripsi produk"
    // @Param        foto formData file false "Foto produk baru"
    // @Success      200 {object} handler.DataProdukResponse
    // @Failure      400 {object} handler.ErrorResponse
    // @Failure      403 {object} handler.ErrorResponse
    // @Router       /produk/{id} [put]
    func (h *ProdukHandler) Update(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        r.Body = http.MaxBytesReader(w, r.Body, 5<<20)
        if err := r.ParseMultipartForm(5 << 20); err != nil {
            writeError(w, http.StatusBadRequest, "form tidak valid atau file terlalu besar", "BAD_REQUEST")
            return
        }

        nama := r.FormValue("nama")
        deskripsi := r.FormValue("deskripsi")
        harga, _ := strconv.ParseFloat(r.FormValue("harga"), 64)

        fotoBaru, err := saveUploadedFile(r, "foto", h.uploadDir, "produk")
        if errors.Is(err, errInvalidFileType) {
            writeError(w, http.StatusBadRequest, "foto harus berformat jpg/jpeg/png", "BAD_REQUEST")
            return
        }
        if err != nil {
            writeError(w, http.StatusBadRequest, "gagal menyimpan foto", "BAD_REQUEST")
            return
        }

        produk, fotoLama, err := h.svc.UpdateOwn(r.Context(), userID, id, nama, harga, deskripsi, fotoBaru)
        switch {
        case errors.Is(err, domain.ErrInvalidInput):
            writeError(w, http.StatusBadRequest, "nama dan harga produk wajib valid", "BAD_REQUEST")
        case errors.Is(err, domain.ErrForbidden):
            writeError(w, http.StatusForbidden, "Anda bukan pemilik produk ini", "FORBIDDEN")
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "produk tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            deleteFile(h.uploadDir, fotoLama)
            writeJSON(w, http.StatusOK, produk)
        }
    }

    // Delete godoc
    // @Summary      Hapus produk sendiri
    // @Tags         produk
    // @Produce      json
    // @Security     BearerAuth
    // @Param        id path int true "ID Produk"
    // @Success      200 {object} handler.MessageResponse
    // @Failure      403 {object} handler.ErrorResponse
    // @Failure      404 {object} handler.ErrorResponse
    // @Router       /produk/{id} [delete]
    func (h *ProdukHandler) Delete(w http.ResponseWriter, r *http.Request) {
        userID := middleware.GetUserID(r)
        id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
        if err != nil {
            writeError(w, http.StatusBadRequest, "id tidak valid", "BAD_REQUEST")
            return
        }

        produk, err := h.svc.DeleteOwn(r.Context(), userID, id)
        switch {
        case errors.Is(err, domain.ErrForbidden):
            writeError(w, http.StatusForbidden, "Anda bukan pemilik produk ini", "FORBIDDEN")
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "produk tidak ditemukan", "NOT_FOUND")
        case err != nil:
            writeError(w, http.StatusInternalServerError, "kesalahan server", "INTERNAL")
        default:
            deleteFile(h.uploadDir, produk.Foto)
            writeJSON(w, http.StatusOK, map[string]string{"message": "produk berhasil dihapus"})
        }
    }

### 10.10 Menyatukan Semua Lapisan pada main.go

Router memakai `http.ServeMux` bawaan Go 1.22 yang sudah mendukung method dan path parameter (`{id}`) tanpa perlu framework tambahan. Komentar di paling atas berkas (`@title`, `@BasePath`, `@securityDefinitions...`) adalah anotasi Swagger tingkat aplikasi, dijelaskan di Bagian 11.

cmd/api/main.go

    // @title           UMKM API
    // @version         1.0
    // @description     REST API untuk pendataan UMKM: registrasi, login, kelola profil, kelola UMKM milik sendiri, dan kelola produk.
    // @BasePath        /api
    //
    // @securityDefinitions.apikey  BearerAuth
    // @in                          header
    // @name                        Authorization
    // @description                 Ketik "Bearer" diikuti spasi dan token JWT. Contoh: "Bearer eyJhbGciOi..."
    package main

    import (
        "context"
        "log/slog"
        "net/http"
        "os"
        "os/signal"
        "syscall"
        "time"

        "github.com/jackc/pgx/v5/pgxpool"
        httpSwagger "github.com/swaggo/http-swagger/v2"
        "golang.org/x/time/rate"

        _ "umkm-api/docs"
        "umkm-api/internal/config"
        "umkm-api/internal/handler"
        "umkm-api/internal/middleware"
        "umkm-api/internal/repository"
        "umkm-api/internal/service"
    )

    func main() {
        cfg := config.Load()

        ctx := context.Background()
        db, err := pgxpool.New(ctx, cfg.DatabaseURL)
        if err != nil {
            slog.Error("gagal konek ke database", "err", err)
            os.Exit(1)
        }
        defer db.Close()

        if err := db.Ping(ctx); err != nil {
            slog.Error("database tidak dapat dijangkau", "err", err)
            os.Exit(1)
        }
        slog.Info("berhasil terhubung ke PostgreSQL (Neon)")

        userRepo := repository.NewUserRepository(db)
        umkmRepo := repository.NewUmkmRepository(db)
        produkRepo := repository.NewProdukRepository(db)

        authSvc := service.NewAuthService(userRepo, cfg.JWTSecret)
        umkmSvc := service.NewUmkmService(umkmRepo)
        produkSvc := service.NewProdukService(produkRepo, umkmRepo)

        authHandler := handler.NewAuthHandler(authSvc)
        umkmHandler := handler.NewUmkmHandler(umkmSvc, cfg.UploadDir)
        produkHandler := handler.NewProdukHandler(produkSvc, cfg.UploadDir)

        auth := middleware.RequireAuth(cfg.JWTSecret)

        // maksimal 5 percobaan login per menit per alamat IP, agar brute-force password dibatasi
        loginLimiter := middleware.RateLimit(rate.Every(time.Minute/5), 5)

        mux := http.NewServeMux()

        // auth
        mux.HandleFunc("POST /api/auth/register", authHandler.Register)
        mux.Handle("POST /api/auth/login", loginLimiter(http.HandlerFunc(authHandler.Login)))

        // profile (butuh login)
        mux.Handle("GET /api/profile", auth(http.HandlerFunc(authHandler.Profile)))
        mux.Handle("PUT /api/profile", auth(http.HandlerFunc(authHandler.UpdateProfile)))
        mux.Handle("PUT /api/profile/password", auth(http.HandlerFunc(authHandler.UpdatePassword)))

        // umkm
        mux.HandleFunc("GET /api/umkm", umkmHandler.List)
        mux.Handle("GET /api/umkm/saya", auth(http.HandlerFunc(umkmHandler.MyUmkm)))
        mux.HandleFunc("GET /api/umkm/{id}", umkmHandler.Detail)
        mux.Handle("POST /api/umkm", auth(http.HandlerFunc(umkmHandler.Create)))
        mux.Handle("PUT /api/umkm/{id}", auth(http.HandlerFunc(umkmHandler.Update)))
        mux.Handle("DELETE /api/umkm/{id}", auth(http.HandlerFunc(umkmHandler.Delete)))

        // produk
        mux.HandleFunc("GET /api/umkm/{id}/produk", produkHandler.ListByUmkm)
        mux.Handle("POST /api/umkm/{id}/produk", auth(http.HandlerFunc(produkHandler.Create)))
        mux.HandleFunc("GET /api/produk/{id}", produkHandler.Detail)
        mux.Handle("PUT /api/produk/{id}", auth(http.HandlerFunc(produkHandler.Update)))
        mux.Handle("DELETE /api/produk/{id}", auth(http.HandlerFunc(produkHandler.Delete)))

        // static file untuk foto yang sudah diupload
        mux.Handle("GET /uploads/", http.StripPrefix("/uploads/", http.FileServer(http.Dir(cfg.UploadDir))))

        // dokumentasi Swagger
        mux.Handle("GET /swagger/", httpSwagger.WrapHandler)

        // health check
        mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
            w.WriteHeader(http.StatusOK)
        })

        srv := &http.Server{
            Addr:              ":" + cfg.Port,
            Handler:           mux,
            ReadHeaderTimeout: 5 * time.Second,
            ReadTimeout:       10 * time.Second,
            WriteTimeout:      10 * time.Second,
            IdleTimeout:       60 * time.Second,
        }

        go func() {
            slog.Info("server berjalan", "port", cfg.Port, "swagger", "/swagger/index.html")
            if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
                slog.Error("server berhenti", "err", err)
                os.Exit(1)
            }
        }()

        // graceful shutdown
        stop, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
        defer cancel()
        <-stop.Done()

        shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer shutdownCancel()
        _ = srv.Shutdown(shutdownCtx)
        slog.Info("server dimatikan dengan aman")
    }

Kenapa import docs pakai underscore ( \_ )?

`_ "umkm-api/docs"` berarti package `docs` (hasil generate `swag init` pada Bagian 11) diimpor hanya untuk efek sampingnya — package tersebut mendaftarkan spesifikasi Swagger ke memori saat program start, tanpa perlu memanggil fungsi apa pun darinya secara langsung.

main.go membaca dari bawah ke atas: urutan wiring ini bukan kebetulan

**1. Koneksi database dibuat lebih dulu** (`pgxpool.New` + `db.Ping`) sebelum apa pun lain — kalau database tidak bisa dijangkau, program langsung berhenti (`os.Exit(1)`) daripada menyalakan server yang pasti akan gagal di setiap request.

**2. Setiap repository dibuat dari `db`, setiap service dibuat dari repository-nya, setiap handler dibuat dari service-nya** — persis mengikuti arah ketergantungan yang sudah dijelaskan di Bagian 8.1 (`domain ← repository ← service ← handler`). `main.go` adalah satu-satunya tempat ketiga layer ini "bertemu" dan dirakit — dependency injection manual tanpa framework DI.

**3. Route didaftarkan dengan pola `"METHOD /path"`** (fitur `http.ServeMux` sejak Go 1.22) — `mux.HandleFunc(...)` untuk endpoint publik, dibungkus `auth(...)` untuk endpoint yang wajib login. Perhatikan path dengan parameter seperti `{id}` langsung dibaca di handler lewat `r.PathValue("id")` (lihat Bagian 10.9), tanpa router pihak ketiga.

**Cara menambah endpoint baru:** setelah entitas baru selesai dibuat di keempat layer (Bagian 8.1), baris terakhir yang ditambahkan selalu di sini — satu baris `mux.HandleFunc(...)` atau `mux.Handle(...)` per endpoint, mengikuti pola yang sudah ada.

## 11Dokumentasi API dengan Swagger

Swagger (OpenAPI) menghasilkan halaman dokumentasi interaktif dari kode itu sendiri — setiap kali handler diubah dan anotasinya diperbarui, dokumentasi tinggal di-generate ulang. Ini sangat membantu ketika API dipakai tim Flutter yang berbeda dari yang menulis backend.

### 11.1 Instal Swag CLI

`swag` adalah tool command-line yang membaca komentar anotasi (`@Summary`, `@Param`, dst.) pada kode Go dan mengubahnya menjadi berkas spesifikasi OpenAPI.

terminal

    go install github.com/swaggo/swag/cmd/swag@latest

    # pastikan $GOPATH/bin ada di PATH, lalu cek:
    swag --version

Kalau perintah swag tidak dikenali

Tambahkan `export PATH=$PATH:$(go env GOPATH)/bin` ke `~/.zshrc` / `~/.bashrc` (macOS/Linux), atau pada Windows tambahkan `%USERPROFILE%\go\bin` ke Environment Variables → Path.

### 11.2 Anotasi Sudah Ditulis di Handler

Perhatikan kembali kode pada Bagian 10.9 — setiap fungsi handler (`Register`, `Login`, `Create`, dst.) sudah memiliki komentar `// ... godoc` di atasnya. Anotasi tingkat aplikasi (judul, versi, skema keamanan) ditulis satu kali di atas package `main` pada `cmd/api/main.go` (Bagian 10.10). Tabel berikut merangkum arti setiap tag yang dipakai:

| Tag | Arti |
|----|----|
| `@Summary` | Judul singkat endpoint, tampil di daftar Swagger UI |
| `@Tags` | Mengelompokkan endpoint (auth, profile, umkm, produk) |
| `@Accept` / `@Produce` | Format request/response: `json` atau `multipart/form-data` |
| `@Param` | Parameter: `path` (di URL), `formData` (multipart), atau `body` (JSON) |
| `@Security BearerAuth` | Menandai endpoint butuh header `Authorization: Bearer` |
| `@Success` / `@Failure` | Kode status beserta struct respons yang dikembalikan |
| `@Router` | Path endpoint (relatif ke `@BasePath`) beserta method HTTP-nya |

### 11.3 Generate Dokumentasi

Jalankan `swag init` dari root project, menunjuk ke berkas yang memuat anotasi `@title` (yaitu `cmd/api/main.go`). Perintah ini membuat folder `docs/` berisi `docs.go`, `swagger.json`, dan `swagger.yaml`.

terminal, dari root project

    swag init -g cmd/api/main.go -o docs

Jalankan ulang setiap kali anotasi berubah

`swag init` tidak otomatis — setiap kali menambah endpoint baru atau mengubah anotasi `@Param`/`@Success`, perintah ini wajib dijalankan ulang agar `docs/` ikut diperbarui. Folder `docs/` boleh di-commit ke Git supaya rekan satu tim tidak perlu menjalankan `swag init` sendiri.

### 11.4 Membuka Swagger UI

Setelah `docs/` ter-generate dan `go run ./cmd/api` dijalankan, buka browser ke:

    http://localhost:8080/swagger/index.html

Halaman ini menampilkan seluruh endpoint terkelompok per `@Tags` (auth, profile, umkm, produk), lengkap dengan tombol **"Try it out"** untuk mengirim request langsung dari browser — termasuk endpoint upload file (`multipart/form-data`).

1.  Klik endpoint `POST /auth/login` → **Try it out** → isi email/password → **Execute** → salin `token` dari respons.
2.  Klik tombol **Authorize** di kanan atas halaman, masukkan `Bearer <token>`, lalu klik **Authorize**.
3.  Endpoint yang butuh login (bertanda gembok) kini otomatis menyertakan token tersebut setiap kali dicoba.

Tetap biasakan ketik "Bearer " di depan token, walau sekarang tidak wajib

Skema keamanan project ini didefinisikan sebagai `@securityDefinitions.apikey BearerAuth` (lihat `cmd/api/main.go`) — Swagger tidak punya tipe `http`/`bearer` bawaan OpenAPI 2.0 yang auto-menambahkan kata "Bearer ". Kotak **Authorize** mengirim **persis apa yang kamu ketik** sebagai header `Authorization`. Awalnya ini bikin banyak mahasiswa dapat `401 "token tidak ditemukan"` kalau cuma paste tokennya saja tanpa kata `Bearer` di depan — makanya middleware di Bagian 10.7 sekarang sengaja dibuat menerima **keduanya** (dengan atau tanpa prefix). Tapi tetap biasakan menulis format standar `Bearer <token>`, karena itu konvensi yang dipakai aplikasi Flutter (Pertemuan 7) dan hampir semua API lain di dunia nyata.

✓ Diverifikasi

Setelah `swag init` dijalankan pada project hasil Bagian 10, `http://localhost:8080/swagger/index.html` menampilkan 9 path (`/auth/register`, `/auth/login`, `/profile`, `/profile/password`, `/umkm`, `/umkm/saya`, `/umkm/{id}`, `/umkm/{id}/produk`, `/produk/{id}`) dengan skema `BearerAuth` aktif — persis sesuai kontrak endpoint pada Bagian 9.1.

## 12Menjalankan dan Menguji API

Sebelum menjalankan server, pastikan migration sudah diterapkan ke database (lihat [Bagian 10.1](#s10)):

migrate -path migrations -database "\$DATABASE_URL" up

    migrate -path migrations -database "$DATABASE_URL" up

menjalankan server

    go run ./cmd/api

Uji setiap endpoint menggunakan `curl`, Postman/Thunder Client, atau langsung dari Swagger UI pada Bagian 11.4. Urutan di bawah ini persis seperti yang dipakai saat memverifikasi materi ini.

register & login

    curl -X POST http://localhost:8080/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"nama":"Asep","email":"asep@mail.com","password":"rahasia123"}'

    curl -X POST http://localhost:8080/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"asep@mail.com","password":"rahasia123"}'
    # simpan token dari respons untuk request berikutnya

profile

    curl http://localhost:8080/api/profile -H "Authorization: Bearer <TOKEN>"

    curl -X PUT http://localhost:8080/api/profile \
      -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
      -d '{"nama":"Asep Trisna","email":"asep@mail.com"}'

    curl -X PUT http://localhost:8080/api/profile/password \
      -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
      -d '{"password_lama":"rahasia123","password_baru":"rahasiabaru123"}'

membuat, melihat, mengubah, dan menghapus UMKM

    curl -X POST http://localhost:8080/api/umkm \
      -H "Authorization: Bearer <TOKEN>" \
      -F "nama=Warung Bu Sari" -F "deskripsi=Menjual makanan rumahan" \
      -F "alamat=Jl. Melati No. 10" -F "foto=@/path/ke/foto.jpg"

    curl http://localhost:8080/api/umkm
    curl "http://localhost:8080/api/umkm?page=1&limit=2"
    curl "http://localhost:8080/api/umkm?q=warung"
    curl http://localhost:8080/api/umkm/1
    curl http://localhost:8080/api/umkm/saya -H "Authorization: Bearer <TOKEN>"

    curl -X PUT http://localhost:8080/api/umkm/1 \
      -H "Authorization: Bearer <TOKEN>" \
      -F "nama=Warung Bu Sari Baru" -F "deskripsi=Update" -F "alamat=Jl. Baru"

    curl -X DELETE http://localhost:8080/api/umkm/1 -H "Authorization: Bearer <TOKEN>"

CRUD produk pada satu UMKM

    curl -X POST http://localhost:8080/api/umkm/1/produk \
      -H "Authorization: Bearer <TOKEN>" \
      -F "nama=Nasi Uduk Spesial" -F "harga=15000" \
      -F "deskripsi=Nasi uduk dengan lauk lengkap" -F "foto=@/path/ke/produk.jpg"

    curl http://localhost:8080/api/umkm/1/produk
    curl "http://localhost:8080/api/umkm/1/produk?page=1&limit=5"
    curl http://localhost:8080/api/produk/1

    # upload dengan tipe berkas yang tidak didukung (harus 400)
    curl -X POST http://localhost:8080/api/umkm/1/produk \
      -H "Authorization: Bearer <TOKEN>" \
      -F "nama=Produk Salah" -F "harga=1000" -F "foto=@/path/ke/dokumen.pdf"

    curl -X PUT http://localhost:8080/api/produk/1 \
      -H "Authorization: Bearer <TOKEN>" \
      -F "nama=Nasi Uduk Spesial (Update)" -F "harga=17000" \
      -F "deskripsi=Porsi lebih besar" -F "foto=@/path/ke/foto-baru.jpg"

    curl -X DELETE http://localhost:8080/api/produk/1 -H "Authorization: Bearer <TOKEN>"

mengakses foto yang sudah diupload

    # field "foto" pada respons berisi path relatif, misal "umkm/1699999999.jpg"
    # gabungkan dengan base URL + "/uploads/" untuk mendapat URL yang bisa dibuka:
    curl http://localhost:8080/uploads/umkm/1699999999.jpg -o hasil.jpg

rate limit pada login (maksimal 5x/menit per IP)

    for i in 1 2 3 4 5 6; do
      curl -s -o /dev/null -w "percobaan $i: %{http_code}\n" \
        -X POST http://localhost:8080/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"asep@mail.com","password":"salah"}'
    done
    # percobaan 1-5 -> 401 (password salah), percobaan 6 -> 429 (terlalu banyak percobaan)

Daftar kode error yang perlu diuji juga

Selain jalur sukses, pastikan menguji: register dengan email yang sudah dipakai (409), login dengan password salah (401), akses `/api/profile` tanpa token (401), membuat UMKM kedua untuk user yang sama (409), menghapus/mengubah produk milik UMKM orang lain (403), upload dengan tipe berkas tidak didukung (400), dan login beruntun melebihi rate limit (429). Semua kasus ini sudah diverifikasi mengembalikan kode status yang benar pada materi ini.

Struktur berlapis pada tutorial ini (domain → repository → service → handler) memang terasa lebih banyak berkas dibanding menulis semuanya dalam satu file, namun tujuannya agar setiap bagian mudah diuji dan dikembangkan secara terpisah — hal ini akan sangat terasa manfaatnya ketika API mulai dihubungkan dengan aplikasi Flutter pada pertemuan berikutnya. Seluruh kode — termasuk pagination, pencarian, validasi tipe file, dan rate limiting — telah diverifikasi berjalan tanpa error terhadap PostgreSQL sungguhan sebelum materi ini diterbitkan. — Materi Sistem Informasi, Fakultas Ilmu Komputer, Universitas Bandar Lampung
